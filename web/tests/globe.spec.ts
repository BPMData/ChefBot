import { expect, test } from "@playwright/test";

test.use({ reducedMotion: "no-preference" });

test("flies to the Italian-American counties and uses the picked cuisine", async ({ page }, info) => {
  const externalRequests: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.protocol.startsWith("http") && url.hostname !== "localhost") externalRequests.push(url.origin);
  });
  await page.goto("./");
  await page.getByRole("button", { name: "Preview cuisine globe" }).click();
  await expect(page.getByRole("heading", { name: "Cuisine globe" })).toBeVisible();
  const map = page.getByLabel("Interactive cuisine map");
  await expect(map).toHaveAttribute("data-ready", "true", { timeout: 15_000 });
  await expect(page.getByRole("button", { name: "Greek", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Central & West Indian", exact: true })).toBeVisible();
  await page.evaluate(() => performance.clearMarks("chefbot-globe-frame"));
  await page.getByRole("button", { name: "Italian-American", exact: true }).click();
  await expect(map).toHaveAttribute("data-zoom", "9.20", { timeout: 15_000 });

  const fps = await page.evaluate(() => {
    const frames = performance.getEntriesByName("chefbot-globe-frame");
    return frames.length < 2 ? 0 : (frames.length - 1) * 1000 / (frames.at(-1)!.startTime - frames[0].startTime);
  });
  console.log(`MapLibre camera flight at ${info.project.name} viewport: ${fps.toFixed(1)} rendered frames/s`);

  const canvas = map.locator("canvas");
  if (info.project.name === "phone") await canvas.tap();
  else {
    await canvas.hover();
    await expect(page.locator(".globe-location")).toHaveText("New York");
    await canvas.click();
  }
  await expect(page.locator(".globe-location")).toHaveText("New York");
  await page.getByRole("button", { name: "Use Italian-American" }).click();
  await expect(page.getByRole("button", { name: "Cuisine", exact: true })).toHaveText("Italian-American");
  expect(externalRequests).toEqual([]);
});
