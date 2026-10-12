import { expect, test } from "@playwright/test";

test("the branded loader fits narrow screens and respects reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 320, height: 700 });
  await page.goto("/fixtures/loading");
  const loader = page.getByRole("status", { name: "Loading Serene" });
  await expect(loader).toBeVisible();
  await expect(loader).toContainText("A moment to bring everything into view.");
  expect(await loader.locator("svg").evaluate((node) => getComputedStyle(node).animationName)).toBe("none");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
});

test("the brief prioritizes the next action and lets parents open recorded steps", async ({ page }) => {
  await page.goto("/fixtures/today");
  const investigation = page.locator("[data-investigation-id]").first();
  const history = investigation.locator("details").filter({ has: page.getByText("Steps Serene actually took", { exact: true }) });
  await expect(history).not.toHaveAttribute("open");
  const positions = await investigation.evaluate((node) => ({
    action: node.querySelector('[data-block="next-action"]')!.getBoundingClientRect().top,
    workflow: node.querySelector('[data-block="workflow"]')!.getBoundingClientRect().top,
  }));
  expect(positions.action).toBeLessThan(positions.workflow);
  await history.locator("summary").click();
  await expect(history.locator("[data-workflow-sequence]").first()).toBeVisible();
  await history.locator("summary").click();
  await expect(history).not.toHaveAttribute("open");
});

test("experiment jumps clear the header and back to top returns to content", async ({ page }) => {
  await page.goto("/fixtures/experiments");
  await page.getByRole("navigation", { name: "Experiment sections" }).getByRole("link", { name: /^Finished/ }).click();
  const section = page.getByRole("region", { name: /^Finished/ });
  await expect(section).toBeInViewport();
  await expect.poll(async () => section.evaluate((node) => Math.round(node.getBoundingClientRect().top))).toBeGreaterThanOrEqual(72);
  await page.getByRole("link", { name: "Back to top" }).click();
  await expect.poll(() => page.evaluate(() => scrollY)).toBe(0);
});
