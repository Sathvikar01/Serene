import { expect, test } from "@playwright/test";

test("the branded loader fits narrow screens and respects reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 320, height: 700 });
  await page.goto("/fixtures/loading");
  const loader = page.getByRole("status", { name: "Loading Serene" });
  await expect(loader).toBeVisible();
  const logo = loader.locator("[data-loading-logo]");
  expect(await logo.locator(":scope > div").evaluate((node) => getComputedStyle(node).animationName)).toBe("none");
  const box = await logo.boundingBox();
  expect(box!.x + box!.width / 2).toBeCloseTo(160, 0);
  expect(box!.y + box!.height / 2).toBeCloseTo(350, 0);
  expect(await loader.locator(":scope > div").first().evaluate((node) => getComputedStyle(node).backdropFilter)).toBe("blur(10px)");
  await page.getByRole("button", { name: "Finish loading preview" }).click();
  await expect(loader).toHaveCount(0);
  await expect(page.locator("[data-shell-bar] > a [data-brand-mark]")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
});

test("the rotating logo returns to the header and a new load can interrupt it", async ({ page }) => {
  await page.goto("/fixtures/loading");
  const overlay = page.locator("[data-page-loader]");
  const logo = page.locator("[data-loading-logo]");
  await expect(overlay).toHaveAttribute("data-state", "loading");
  expect(await logo.locator(":scope > div").evaluate((node) => getComputedStyle(node).animationName)).not.toBe("none");
  await logo.evaluate((node) => {
    const animate = node.animate.bind(node);
    node.animate = (frames, options) => {
      const flight = animate(frames, options);
      flight.pause();
      node.animate = animate;
      return flight;
    };
  });
  await page.getByRole("button", { name: "Finish loading preview" }).click();
  // Pause the actual Web Animation to inspect the flight's destination.
  await expect(overlay).toHaveAttribute("data-state", "returning");
  const destination = await logo.evaluate((node) => {
    const animation = node.getAnimations()[0];
    if (!animation) throw new Error("Logo return animation did not start");
    animation.pause();
    animation.currentTime = 419;
    const from = node.getBoundingClientRect();
    const to = document.querySelector("[data-shell-bar] > a [data-brand-mark]")!.getBoundingClientRect();
    return { dx: Math.abs(from.x - to.x), dy: Math.abs(from.y - to.y), dw: Math.abs(from.width - to.width) };
  });
  expect(destination.dx).toBeLessThan(1);
  expect(destination.dy).toBeLessThan(1);
  expect(destination.dw).toBeLessThan(1);
  await page.getByRole("button", { name: "Load preview again" }).click();
  await expect(overlay).toHaveAttribute("data-state", "loading");
  const centered = await logo.boundingBox();
  const viewport = page.viewportSize()!;
  expect(centered!.x + centered!.width / 2).toBeCloseTo(viewport.width / 2, 0);
  await page.getByRole("button", { name: "Finish loading preview" }).click();
  await expect(overlay).toHaveCount(0);
  await expect(page.locator("[data-shell-bar] > a [data-brand-mark]")).toBeVisible();
  expect(await page.locator("body").evaluate((node) => getComputedStyle(node).overflow)).not.toBe("hidden");
});

test("the original visual styling is retained without default heading gaps", async ({ page }) => {
  await page.goto("/fixtures/investigations");
  await expect(page.locator("[data-page-loader]")).toHaveCount(0);
  expect(await page.locator("h1").evaluate((node) => getComputedStyle(node).textTransform)).toBe("uppercase");
  expect(await page.locator("body").evaluate(() => getComputedStyle(document.documentElement).getPropertyValue("--ground").trim())).toBe("#e0dfd8");
  const margins = await page.locator("h4").evaluateAll((nodes) => nodes.map((node) => ({ top: getComputedStyle(node).marginTop, bottom: getComputedStyle(node).marginBottom })));
  expect(margins.length).toBeGreaterThan(0);
  expect(margins.every((margin) => margin.top === "0px" && margin.bottom === "0px")).toBe(true);
});

test("the brief prioritizes the next action and lets parents open recorded steps", async ({ page }) => {
  await page.goto("/fixtures/today");
  const investigation = page.locator("[data-investigation-id]").first();
  const history = investigation.locator("details[data-record-details]").filter({ has: page.locator('[data-block="workflow"]') });
  await expect(history).not.toHaveAttribute("open");
  const concise = await investigation.innerText();
  await history.locator(":scope > summary").click();
  await expect(history.locator("[data-workflow-sequence]").first()).toBeVisible();
  expect((await investigation.innerText()).length).toBeGreaterThan(concise.length * 1.5);
  await history.locator(":scope > summary").click();
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
