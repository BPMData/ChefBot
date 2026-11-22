import { expect, test, type Page } from "@playwright/test";

type Node = { id: string; label: string; kind: string; children?: string[]; prompt_name?: string };
type Tree = { roots: string[]; nodes: Record<string, Node> };

const api = "http://localhost:8911";
const continentNames: Record<string, string> = { americas: "The Americas" };

async function cuisineTree(page: Page): Promise<Tree> {
  return (await page.request.get(api + "/api/cuisines")).json();
}

const label = (tree: Tree, id: string) => continentNames[id] ?? tree.nodes[id].label;

function foodName(node: Node) {
  const name = (node.prompt_name ?? node.label).replace(/\s*\([^)]*\)\s*$/, "");
  return /\bfood$/i.test(name) ? name : name + " food";
}

/** Opens the globe screen from the list-first home page, the way the old flow did. */
async function openGlobe(page: Page) {
  await page.addInitScript(() => localStorage.setItem("chefbot.cuisine-picker", "list"));
  await page.goto("./");
  await page.getByRole("button", { name: "Cuisine globe", exact: true }).click();
  await settled(page, "world");
}

async function settled(page: Page, level: string) {
  const map = page.getByLabel("Interactive cuisine map");
  await expect(map).toHaveAttribute("data-level", level);
  await expect(map).toHaveAttribute("data-settled", "true", { timeout: 15_000 });
}

/** Every callout sits inside the map, is big enough to tap, overlaps no other, and is on top where it is drawn. */
async function checkCallouts(page: Page, heading: string, expected: string[]) {
  const group = page.getByRole("group", { name: heading + " regions" });
  await expect(group.locator(".globe-callout")).toHaveCount(expected.length);
  await page.getByLabel("Interactive cuisine map").scrollIntoViewIfNeeded();
  const problems = await group.evaluate((element) => {
    const frame = element.getBoundingClientRect();
    const chips = [...element.querySelectorAll<HTMLElement>(".globe-callout")];
    const boxes = chips.map((chip) => ({ name: chip.textContent, box: chip.getBoundingClientRect() }));
    const found: string[] = [];
    for (const { name, box } of boxes) {
      if (box.left < frame.left || box.right > frame.right || box.top < frame.top || box.bottom > frame.bottom) {
        found.push(name + " is outside the map");
      }
      if (box.height < 28 || box.width < 44) found.push(name + " is too small to tap");
      const hit = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
      if (!hit?.closest(".globe-callout") || hit.closest(".globe-callout")!.textContent !== name) {
        found.push(name + " is covered");
      }
    }
    boxes.forEach((a, i) => boxes.slice(i + 1).forEach((b) => {
      if (a.box.left < b.box.right && b.box.left < a.box.right && a.box.top < b.box.bottom && b.box.top < a.box.bottom) {
        found.push(a.name + " overlaps " + b.name);
      }
    }));
    return found;
  });
  expect(problems).toEqual([]);
  expect((await group.locator(".globe-callout").allTextContents()).sort()).toEqual([...expected].sort());
}

async function checkInfobox(page: Page, tree: Tree, id: string, name: string) {
  const details = page.getByRole("dialog", { name, exact: true });
  await expect(details).toBeVisible();
  await expect(details.getByText("Start making " + foodName(tree.nodes[id]) + "?", { exact: true })).toBeVisible();
  await expect(details.getByRole("button", { name: "Go", exact: true })).toBeVisible();
  await details.getByRole("button", { name: "Close" }).click();
  await expect(details).toHaveCount(0);
}

const choices = (tree: Tree, id: string) => (tree.nodes[id].children ?? []).filter((child) => tree.nodes[child].kind !== "any");

for (const continent of ["americas", "asia", "europe", "near_east", "africa", "oceania"]) {
  test(`reaches every ${continent.replace("_", " ")} cuisine from the globe`, async ({ page }, info) => {
    test.setTimeout(150_000);
    const tree = await cuisineTree(page);
    await openGlobe(page);
    await checkCallouts(page, "Cuisine globe", tree.roots.map((id) => label(tree, id)));
    const name = label(tree, continent);
    await page.getByRole("group", { name: "Cuisine globe regions" }).getByRole("button", { name, exact: true }).click();
    await settled(page, continent);
    await expect(page.getByRole("heading", { name, level: 1 })).toBeVisible();
    await checkCallouts(page, name, choices(tree, continent).map((id) => label(tree, id)));
    await page.screenshot({ path: info.outputPath(`${continent}.png`) });

    for (const id of choices(tree, continent)) {
      const node = tree.nodes[id];
      await page.getByRole("group", { name: name + " regions" }).getByRole("button", { name: node.label, exact: true }).click();
      if (!node.children?.length) {
        await checkInfobox(page, tree, id, node.label);
        continue;
      }
      await settled(page, id);
      await checkCallouts(page, node.label, choices(tree, id).map((child) => label(tree, child)));
      await page.screenshot({ path: info.outputPath(`${id}.png`) });
      for (const child of choices(tree, id)) {
        await page.getByRole("group", { name: node.label + " regions" })
          .getByRole("button", { name: tree.nodes[child].label, exact: true }).click();
        await checkInfobox(page, tree, child, tree.nodes[child].label);
      }
      const any = node.children.find((child) => tree.nodes[child].kind === "any")!;
      await page.getByRole("button", { name: /^Any region/ }).click();
      await checkInfobox(page, tree, any, tree.nodes[any].prompt_name!);
      await page.getByRole("button", { name: "Back to " + name, exact: true }).click();
      await settled(page, continent);
    }
    await page.getByRole("button", { name: "Back to globe", exact: true }).click();
    await settled(page, "world");
  });
}

test("goes from the home page globe to Shandong and back to the form with it picked", async ({ page }, info) => {
  await page.goto("./");
  await expect(page.getByRole("button", { name: "Cuisine globe", exact: true })).toHaveCount(0);
  const continents = page.getByRole("group", { name: "Continents" });
  await expect(continents.locator(".globe-callout")).toHaveCount(6, { timeout: 15_000 });
  await page.screenshot({ path: info.outputPath("home.png") });
  await page.getByLabel("Ingredients", { exact: true }).fill("leeks and eggs");
  await continents.getByRole("button", { name: "Asia", exact: true }).click();
  await settled(page, "asia");
  await expect(page.getByRole("heading", { name: "Asia", level: 1 })).toBeVisible();
  await page.getByRole("button", { name: "China", exact: true }).click();
  await settled(page, "china");
  await page.screenshot({ path: info.outputPath("china.png") });
  await page.getByRole("button", { name: "Shandong", exact: true }).click();
  const details = page.getByRole("dialog", { name: "Shandong" });
  await expect(details.getByRole("img", { name: "Shandong region highlighted" })).toBeVisible();
  await expect(details.getByText("Start making Shandong food?")).toBeVisible();
  await page.screenshot({ path: info.outputPath("shandong-infobox.png") });
  await details.getByRole("button", { name: "Go", exact: true }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Shandong", exact: true })).toBeVisible();
  await expect(page.getByLabel("Ingredients", { exact: true })).toHaveValue("leeks and eggs");
});

test("opens Greece straight away, since it has one cuisine", async ({ page }) => {
  await openGlobe(page);
  await page.getByRole("button", { name: "Europe", exact: true }).click();
  await settled(page, "europe");
  await page.getByRole("button", { name: "Greek", exact: true }).click();
  const details = page.getByRole("dialog", { name: "Greek" });
  await expect(details.getByText("Start making Greek food?")).toBeVisible();
  await details.getByRole("button", { name: "Go", exact: true }).click();
  await expect(page.getByRole("button", { name: "Greek", exact: true })).toBeVisible();
  await expect(page.getByLabel("Ingredients", { exact: true })).toBeVisible();
});

test("picks a region by tapping the map itself", async ({ page }, info) => {
  await openGlobe(page);
  await page.getByRole("button", { name: "Europe", exact: true }).click();
  await settled(page, "europe");
  // Find a spot inside Spain that no callout covers, then tap the map there.
  const point = await page.evaluate(() => {
    const globe = (window as unknown as { chefbotGlobe: { project: (p: [number, number]) => { x: number; y: number }; getCanvas: () => HTMLCanvasElement } }).chefbotGlobe;
    const frame = globe.getCanvas().getBoundingClientRect();
    for (const spot of [[-5, 37.6], [-2, 41.8], [-6.5, 39], [-1, 38.4], [-4.5, 42.4]] as [number, number][]) {
      const { x, y } = globe.project(spot);
      const target = document.elementFromPoint(frame.left + x, frame.top + y);
      if (target === globe.getCanvas()) return { x, y };
    }
    return null;
  });
  expect(point).not.toBeNull();
  const canvas = page.getByLabel("Interactive cuisine map").locator("canvas");
  if (info.project.name === "phone") await canvas.tap({ position: point! });
  else {
    await canvas.hover({ position: point! });
    await expect(page.locator(".globe-location")).toHaveText("Spanish");
    await canvas.click({ position: point! });
  }
  await expect(page.getByRole("dialog", { name: "Spanish" })).toBeVisible();
});

test("Back returns to the previous level and the view the person left", async ({ page }) => {
  await openGlobe(page);
  const map = page.getByLabel("Interactive cuisine map");
  await page.getByRole("button", { name: "Zoom in", exact: true }).click();
  await expect(map).toHaveAttribute("data-settled", "true");
  const zoom = await map.getAttribute("data-zoom");
  await page.getByRole("button", { name: "Europe", exact: true }).click();
  await settled(page, "europe");
  const europeZoom = await map.getAttribute("data-zoom");
  expect(Number(europeZoom)).toBeGreaterThan(Number(zoom));
  await page.getByRole("button", { name: "Italy", exact: true }).click();
  await settled(page, "italy");
  await expect(page.getByRole("heading", { name: "Italy", level: 1 })).toBeVisible();
  await page.getByRole("button", { name: "Back to Europe", exact: true }).click();
  await settled(page, "europe");
  await expect(map).toHaveAttribute("data-zoom", europeZoom!);
  await page.goBack();
  await settled(page, "world");
  await expect(map).toHaveAttribute("data-zoom", zoom!);
  await expect(page.getByRole("heading", { name: "Cuisine globe", level: 1 })).toBeVisible();
  // Forward again lands on the continent's fixed view, not a leftover one.
  await page.getByRole("button", { name: "Europe", exact: true }).click();
  await settled(page, "europe");
  await expect(map).toHaveAttribute("data-zoom", europeZoom!);
});

test.describe("with motion", () => {
  test.use({ reducedMotion: "no-preference" });

  test("the home page globe spins slowly until it is touched", async ({ page }, info) => {
    await page.goto("./");
    await expect(page.getByRole("group", { name: "Continents" }).locator(".globe-callout")).toHaveCount(6, { timeout: 15_000 });
    const center = () => page.evaluate(() => (window as unknown as { chefbotGlobe: { getCenter: () => { lng: number } } }).chefbotGlobe.getCenter().lng);
    const before = await center();
    await expect.poll(center, { timeout: 6_000 }).toBeGreaterThan(before + 2);
    await page.evaluate(() => performance.clearMarks("chefbot-globe-frame"));
    await page.waitForTimeout(2_000);
    const fps = await page.evaluate(() => performance.getEntriesByName("chefbot-globe-frame").length / 2);
    console.log(`Home globe spin at ${info.project.name} viewport: ${fps.toFixed(1)} rendered frames/s`);
    // A short drag (not a tap, which would open a continent) stops the spin for good.
    const box = (await page.locator(".globe-host canvas").boundingBox())!;
    const x = Math.round(box.x + 20);
    const y = Math.round(box.y + box.height / 2);
    if (info.project.name === "phone") {
      const touch = await page.context().newCDPSession(page);
      await touch.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y }] });
      await touch.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: x + 12, y }] });
      await touch.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
      await touch.detach();
    } else {
      await page.mouse.move(x, y);
      await page.mouse.down();
      await page.mouse.move(x + 12, y, { steps: 3 });
      await page.mouse.up();
    }
    await page.waitForTimeout(600);
    await expect(page.getByRole("heading", { name: "What’s in your kitchen?" })).toBeVisible();
    const stopped = await center();
    await page.waitForTimeout(1_200);
    expect(Math.abs((await center()) - stopped)).toBeLessThan(0.01);
  });

  test("flies between levels without leaving this site", async ({ page }, info) => {
    const externalRequests: string[] = [];
    page.on("request", (request) => {
      const url = new URL(request.url());
      if (url.protocol.startsWith("http") && url.hostname !== "localhost") externalRequests.push(url.origin);
    });
    await openGlobe(page);
    await page.evaluate(() => performance.clearMarks("chefbot-globe-frame"));
    await page.getByRole("button", { name: "The Americas", exact: true }).click();
    await settled(page, "americas");
    await page.getByRole("button", { name: "United States", exact: true }).click();
    await settled(page, "united_states");
    const fps = await page.evaluate(() => {
      const frames = performance.getEntriesByName("chefbot-globe-frame");
      return frames.length < 2 ? 0 : (frames.length - 1) * 1000 / (frames.at(-1)!.startTime - frames[0].startTime);
    });
    console.log(`MapLibre camera flights at ${info.project.name} viewport: ${fps.toFixed(1)} rendered frames/s`);
    await page.getByRole("button", { name: "Italian-American", exact: true }).click();
    await expect(page.getByRole("dialog", { name: "Italian-American" })).toBeVisible();
    await expect(page.getByText("Start making Italian-American food?")).toBeVisible();
    expect(externalRequests).toEqual([]);
  });

  test("drags the globe with one finger on a phone", async ({ page }, info) => {
    test.skip(info.project.name !== "phone", "Requires touchscreen emulation");
    await openGlobe(page);
    const canvas = page.getByLabel("Interactive cuisine map").locator("canvas");
    await canvas.scrollIntoViewIfNeeded();
    const bounds = await canvas.boundingBox();
    if (!bounds) throw new Error("Globe canvas is not visible");
    await page.evaluate(() => performance.clearMarks("chefbot-globe-frame"));
    const before = await page.evaluate(() => (window as unknown as { chefbotGlobe: { getCenter: () => { lng: number } } }).chefbotGlobe.getCenter().lng);

    const touch = await page.context().newCDPSession(page);
    const x = Math.round(bounds.x + bounds.width / 3);
    const y = Math.round(bounds.y + bounds.height / 2);
    await touch.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y }] });
    for (const distance of [20, 40, 60, 80]) {
      await touch.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: x + distance, y }] });
    }
    await touch.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await touch.detach();
    await expect.poll(() => page.evaluate(() => performance.getEntriesByName("chefbot-globe-frame").length))
      .toBeGreaterThan(0);
    await expect.poll(() => page.evaluate(() => (window as unknown as { chefbotGlobe: { getCenter: () => { lng: number } } }).chefbotGlobe.getCenter().lng))
      .toBeLessThan(before - 1);
  });
});

test("the cuisine picker setting chooses between the globe and the list", async ({ page }) => {
  await page.goto("./");
  await expect(page.getByRole("group", { name: "Continents" })).toBeVisible({ timeout: 15_000 });
  await page.getByRole("button", { name: "Start with the cuisine list instead" }).click();
  await expect(page.getByRole("group", { name: "Continents" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Cuisine globe", exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("button", { name: "Cuisine globe", exact: true })).toBeVisible();
  await expect(page.locator(".globe-host")).toHaveCount(0);
  await page.getByRole("button", { name: "Settings" }).click();
  await expect(page.getByLabel("Pick cuisines with")).toHaveValue("list");
  await page.getByLabel("Pick cuisines with").selectOption("globe");
  await page.getByRole("button", { name: "Back to recipes" }).click();
  await expect(page.getByRole("group", { name: "Continents" })).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("button", { name: "Start with the cuisine list instead" })).toBeVisible();
});

test("Back from a continent opened on the home page climbs out to the globe, then home", async ({ page }) => {
  await page.goto("./");
  const continents = page.getByRole("group", { name: "Continents" });
  await continents.getByRole("button", { name: "Europe", exact: true }).click();
  await settled(page, "europe");
  await page.getByRole("button", { name: "Back to globe", exact: true }).click();
  await settled(page, "world");
  await expect(page.getByRole("heading", { name: "Cuisine globe", level: 1 })).toBeVisible();
  await page.getByRole("button", { name: "Back to recipes", exact: true }).click();
  await expect(continents).toBeVisible({ timeout: 15_000 });
});

test("the home page globe holds still when the browser asks for less motion", async ({ page }) => {
  await page.goto("./");
  await expect(page.getByRole("group", { name: "Continents" }).locator(".globe-callout")).toHaveCount(6, { timeout: 15_000 });
  const center = () => page.evaluate(() => (window as unknown as { chefbotGlobe: { getCenter: () => { lng: number } } }).chefbotGlobe.getCenter().lng);
  const before = await center();
  await page.waitForTimeout(1_500);
  expect(await center()).toBe(before);
});
