import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function localRequest(request: NextRequest) {
  if (process.env.SERENE_DEMO_MODE !== "1") return false;
  const host = request.headers.get("host") ?? "";
  if (!/^(localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/.test(host)) return false;
  const origin = request.headers.get("origin");
  return !origin || origin === `http://${host}` || origin === `https://${host}`;
}

async function forward(request: NextRequest, method: "GET" | "POST") {
  if (!localRequest(request)) return NextResponse.json({ error: "Local demo access only" }, { status: 403 });
  try {
    let body: string | undefined;
    if (method === "POST") {
      if (!request.headers.get("content-type")?.startsWith("application/json")) {
        return NextResponse.json({ error: "JSON required" }, { status: 415 });
      }
      const raw = await request.text();
      if (raw.length > 24000) return NextResponse.json({ error: "Message too large" }, { status: 413 });
      let value: unknown;
      try { value = JSON.parse(raw); } catch { return NextResponse.json({ error: "Invalid JSON" }, { status: 400 }); }
      if (!value || typeof value !== "object") return NextResponse.json({ error: "Invalid request" }, { status: 400 });
      const payload = value as Record<string, unknown>;
      if (typeof payload.message !== "string" || !payload.message.trim() || payload.message.length > 4000 ||
          typeof payload.request_id !== "string" || !/^[A-Za-z0-9:_-]{1,120}$/.test(payload.request_id)) {
        return NextResponse.json({ error: "Enter a message of up to 4,000 characters" }, { status: 400 });
      }
      body = JSON.stringify({ message: payload.message, request_id: payload.request_id, channel: "web" });
    }
    const secret = (await readFile(join(process.env.SERENE_LOCAL_DATA_DIR ?? join(homedir(), ".serene-live"), "agent.secret"), "utf8")).trim();
    const response = await fetch("http://127.0.0.1:8788/agent", {
      method, body, cache: "no-store", signal: AbortSignal.timeout(65000),
      headers: { Authorization: `Bearer ${secret}`, "Content-Type": "application/json" },
    });
    return NextResponse.json(await response.json(), { status: response.status, headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ error: "Serene is not available. Please try again shortly." }, { status: 503 });
  }
}

export function GET(request: NextRequest) { return forward(request, "GET"); }
export function POST(request: NextRequest) { return forward(request, "POST"); }
