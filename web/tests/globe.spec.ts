import { expect, test } from "@playwright/test";

test.use({ reducedMotion: "no-preference" });

test("flies to the Italian-American counties and uses the picked cuisine", async ({ page }, info) => {
  const externalRequests: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.protocol.startsWith("http") && url.hostname !== "localhost") externalRequests.push(url.origin);
  });
  await page.goto("./");
  await page.getByRole("button", { name: "Cuisine globe", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Cuisine globe" })).toBeVisible();
  const map = page.getByLabel("Interactive cuisine map");
  await expect(map).toHaveAttribute("data-ready", "true", { timeout: 15_000 });
  await page.getByText("Regional close-ups", { exact: true }).click();
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

  const details = page.getByRole("dialog", { name: "Italian-American", exact: true });
  await expect(details.getByRole("img", { name: "Italian-American region highlighted" })).toBeVisible();
  await details.getByRole("button", { name: "Close" }).click();
  await expect(details).toHaveCount(0);

  const canvas = map.locator("canvas");
  if (info.project.name === "phone") await canvas.tap();
  else {
    await canvas.hover();
    await expect(page.locator(".globe-location")).toHaveText("New York");
    await canvas.click();
  }
  await expect(page.locator(".globe-location")).toHaveText("New York");
  await expect(details).toBeVisible();
  await details.getByRole("button", { name: "Use Italian-American" }).click();
  await expect(page.getByRole("button", { name: "Italian-American", exact: true })).toBeVisible();
  expect(externalRequests).toEqual([]);
});

test("drags the globe with one finger on a phone", async ({ page }, info) => {
  test.skip(info.project.name !== "phone", "Requires touchscreen emulation");
  await page.goto("./");
  await page.getByRole("button", { name: "Cuisine globe", exact: true }).click();
  const map = page.getByLabel("Interactive cuisine map");
  await expect(map).toHaveAttribute("data-ready", "true", { timeout: 15_000 });
  const canvas = map.locator("canvas");
  await canvas.scrollIntoViewIfNeeded();
  const bounds = await canvas.boundingBox();
  if (!bounds) throw new Error("Globe canvas is not visible");
  await page.evaluate(() => performance.clearMarks("chefbot-globe-frame"));

  const touch = await page.context().newCDPSession(page);
  const x = Math.round(bounds.x + bounds.width / 3);
  const y = Math.round(bounds.y + bounds.height / 2);
  await touch.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y }] });
  for (const distance of [20, 40, 60, 80]) {
    await touch.send("Input.dispatchTouchEvent", {
      type: "touchMove", touchPoints: [{ x: x + distance, y }],
    });
  }
  await touch.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await touch.detach();
  await expect.poll(() => page.evaluate(() => performance.getEntriesByName("chefbot-globe-frame").length))
    .toBeGreaterThan(0);
});

test("opens a continent from the globe and a regional cuisine from its map", async ({ page }, info) => {
  await page.goto("./");
  await page.getByRole("button", { name: "Cuisine globe", exact: true }).click();
  const map = page.getByLabel("Interactive cuisine map");
  await expect(map).toHaveAttribute("data-ready", "true", { timeout: 15_000 });
  const canvas = map.locator("canvas");
  const bounds = (await canvas.boundingBox())!;
  const point = { x: Math.round(bounds.width / 2 + bounds.height * 0.18), y: Math.round(bounds.height * 0.55) };
  await canvas.hover({ position: point });
  await expect(page.locator(".globe-location")).toHaveText("Africa");
  if (info.project.name === "phone") await canvas.tap({ position: point });
  else await canvas.click({ position: point });
  await expect(page.getByRole("group", { name: "Africa cuisine map" })).toBeVisible();
  await page.getByRole("button", { name: "Ghanaian", exact: true }).click();
  await expect(page.getByRole("dialog", { name: "Ghanaian" })).toBeVisible();
  await page.goBack();
  await expect(page.getByRole("group", { name: "Africa cuisine map" })).toBeVisible();
  await page.getByRole("button", { name: "Back to globe" }).click();
  await expect(map).toHaveAttribute("data-ready", "true", { timeout: 15_000 });
  await page.getByRole("button", { name: "Zoom in", exact: true }).click();
  await expect(map).toHaveAttribute("data-zoom", "1.55");
  await page.getByRole("button", { name: "The Americas", exact: true }).click();
  await page.getByRole("button", { name: "United States", exact: true }).click();
  await expect(page.getByRole("group", { name: "United States cuisine map" })).toBeVisible();
  const withinMap = await page.getByRole("group", { name: "United States cuisine map" }).evaluate((map) => {
    const bounds = map.getBoundingClientRect();
    return [...map.querySelectorAll(".map-label")].every((target) => {
      const label = target.getBoundingClientRect();
      return label.left >= bounds.left && label.right <= bounds.right;
    });
  });
  expect(withinMap).toBe(true);
  await page.screenshot({ path: info.outputPath("regional-map.png") });
  await page.getByRole("button", { name: "Cajun", exact: true }).click();
  await page.goBack();
  await expect(page.getByRole("group", { name: "United States cuisine map" })).toBeVisible();
  await page.goBack();
  await page.goBack();
  await expect(map).toHaveAttribute("data-zoom", "1.55");
  await page.getByRole("button", { name: "The Americas", exact: true }).click();
  await page.getByRole("button", { name: "United States", exact: true }).click();
  await page.getByRole("button", { name: "Cajun", exact: true }).click();
  await page.getByRole("button", { name: "Use Cajun" }).click();
  await expect(page.getByRole("button", { name: "Cajun", exact: true })).toBeVisible();
  await expect(page.getByLabel("Ingredients", { exact: true })).toBeVisible();
});
