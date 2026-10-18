import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import { AgentChat } from "./AgentChat";

afterEach(() => vi.unstubAllGlobals());

it("sends a question through the existing agent endpoint and renders its saved reply", async () => {
  let history: object[] = [];
  const fetch = vi.fn(async (_url: string, options?: RequestInit) => {
    if (options?.method === "POST") {
      const sent = JSON.parse(String(options.body));
      history = [{ id: 1, request_id: sent.request_id, channel: "web", message: sent.message,
        at: "2026-10-13T06:00:00Z", reply: "A short warning helped at pickup.", state: "completed", latency_ms: 10, receipt: null }];
      return Response.json({ ok: true });
    }
    return Response.json({ memory: { files: [] }, history, report_count: history.length });
  });
  vi.stubGlobal("fetch", fetch);
  const user = userEvent.setup();
  render(<AgentChat />);
  await screen.findByText(/Memory connected/);
  await user.type(screen.getByRole("textbox", { name: "Message Serene" }), "What helped at pickup?");
  await user.click(screen.getByRole("button", { name: "Send message" }));
  expect(await screen.findByText("A short warning helped at pickup.")).toBeVisible();
  const posts = fetch.mock.calls.filter(([, options]) => options?.method === "POST");
  expect(posts).toHaveLength(1);
  expect(JSON.parse(String(posts[0][1]?.body))).toMatchObject({ message: "What helped at pickup?", request_id: expect.stringMatching(/^web:/) });
  expect(screen.getByRole("textbox")).toHaveValue("");
});

it("keeps sending disabled when the service is unavailable and offers reconnect", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => Response.json({ error: "Serene is not available." }, { status: 503 })));
  render(<AgentChat />);
  expect(await screen.findByRole("alert")).toHaveTextContent("Serene is not available.");
  expect(screen.getByRole("button", { name: "Reconnect" })).toBeEnabled();
  expect(screen.getByRole("button", { name: "Send message" })).toBeDisabled();
});
