import { expect, test } from "@playwright/test";

test("Ask Serene sends once, shows the saved answer, and keeps the composer usable on a phone", async ({ page }) => {
  let history: object[] = [];
  const sent: { message: string; request_id: string }[] = [];
  await page.route("**/api/agent", async (route) => {
    if (route.request().method() === "POST") {
      const message = route.request().postDataJSON();
      sent.push(message);
      history = [{ id: 1, request_id: message.request_id, channel: "web", message: message.message,
        at: "2026-10-13T06:00:00Z", reply: "A short warning helped at pickup.", state: "completed", latency_ms: 10, receipt: null }];
      return route.fulfill({ json: { ok: true } });
    }
    return route.fulfill({ json: { history, memory: { files: [] }, report_count: history.length } });
  });
  await page.goto("/fixtures/agent");
  await expect(page.getByRole("heading", { level: 1, name: "Ask Serene" })).toBeVisible();
  await expect(page.getByText(/Memory connected/)).toBeVisible();
  await page.getByRole("textbox", { name: "Message Serene" }).fill("What helped at pickup?");
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(page.getByText("A short warning helped at pickup.")).toBeVisible();
  expect(sent).toHaveLength(1);
  expect(sent[0]).toMatchObject({ message: "What helped at pickup?", request_id: expect.stringMatching(/^web:/) });
  await page.setViewportSize({ width: 320, height: 700 });
  await expect(page.getByRole("textbox")).toBeInViewport();
  await expect(page.getByRole("button", { name: "Send message" })).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await expect(page.getByRole("main")).not.toContainText(/demo story|model|memory_head|report_sha256/);
});

test("Ask Serene offers reconnect when the service is unavailable", async ({ page }) => {
  await page.route("**/api/agent", (route) => route.fulfill({ status: 503, json: { error: "Serene is unavailable." } }));
  await page.goto("/fixtures/agent");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Serene is unavailable.");
  await expect(page.getByRole("button", { name: "Reconnect" })).toBeEnabled();
  await expect(page.getByRole("button", { name: "Send message" })).toBeDisabled();
});
