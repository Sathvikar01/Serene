import { NextRequest } from "next/server";
import { afterEach, expect, it, vi } from "vitest";
import { GET, POST } from "./route";

vi.mock("node:fs/promises", () => {
  const readFile = vi.fn(async () => "test-server-only-secret");
  return { readFile, default: { readFile } };
});
afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

const request = (host: string, body?: string, origin?: string) => new NextRequest(`http://${host}/api/agent`, {
  method: body === undefined ? "GET" : "POST", body,
  headers: { host, "content-type": "application/json", ...(origin ? { origin } : {}) },
});

it("refuses hosted, disabled and cross-origin access without forwarding", async () => {
  const fetch = vi.fn(); vi.stubGlobal("fetch", fetch);
  vi.stubEnv("SERENE_DEMO_MODE", "0");
  expect((await GET(request("127.0.0.1:3000"))).status).toBe(403);
  vi.stubEnv("SERENE_DEMO_MODE", "1");
  expect((await GET(request("example.com"))).status).toBe(403);
  expect((await POST(request("127.0.0.1:3000", "{}", "https://example.com"))).status).toBe(403);
  expect(fetch).not.toHaveBeenCalled();
});

it("rejects malformed messages and keeps the service credential server-side", async () => {
  vi.stubEnv("SERENE_DEMO_MODE", "1");
  const fetch = vi.fn(async () => Response.json({ history: [], memory: { files: [] } }));
  vi.stubGlobal("fetch", fetch);
  expect((await POST(request("127.0.0.1:3000", "invalid"))).status).toBe(400);
  expect((await POST(request("127.0.0.1:3000", JSON.stringify({ message: "", request_id: "web:1" })))).status).toBe(400);
  expect(fetch).not.toHaveBeenCalled();
  const response = await GET(request("127.0.0.1:3000"));
  expect(response.status).toBe(200);
  expect(fetch).toHaveBeenCalledWith("http://127.0.0.1:8788/agent", expect.objectContaining({
    headers: expect.objectContaining({ Authorization: "Bearer test-server-only-secret" }),
  }));
  expect(await response.text()).not.toContain("test-server-only-secret");
});
