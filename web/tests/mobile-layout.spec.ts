import { expect, test, type Page } from "@playwright/test";

// A long recipe with a long title, like the ones that left a sliver of screen for reading on a phone.
const title = "Mole-Braised Sujuk over Hoja de Aguacate Refried Navy Beans, with Ancho-Espresso Glaze and Smoky Escabeche de Cebolla";
const steps = Array.from({ length: 40 }, (_, i) => (i + 1) + ". Stir the beans and taste for salt before moving on.").join("\n");
const conversation = {
  id: "fixture-mobile-layout", title, updated: 1, last_accessed: 1, access_count: 0, favorite: false,
  settings: { audience: "A working professional.", cuisine: "greek", pantry: true, dessert: false, restrictions: [], must_not: "" },
  messages: [
    { role: "user", content: "Sujuk, navy beans, avocado leaves, ancho, espresso, onions. Let's impress my guests." },
    { role: "assistant", title, content: "Recipe Title: " + title + "\n\nA rich, smoky braise for a crowd.\n\n" + steps },
  ],
  photos: {},
};

async function openRecipe(page: Page) {
  await page.goto("./");
  await page.getByRole("button", { name: "Settings" }).click();
  await page.getByLabel("Import recipes").setInputFiles({ name: "recipes.json", mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify({ format: "chefbot-recipes", version: 1, conversations: [conversation] })) });
  await expect(page.getByText("Added 1, updated 0.")).toBeVisible();
  await page.goBack();
  await page.getByRole("button", { name: /^Mole-Braised Sujuk/ }).click();
  await expect(page.getByRole("heading", { name: title, level: 1 })).toBeVisible();
  await page.evaluate(() => document.fonts.ready);
}

// How much of the window shows recipe text: the part of the reply card that isn't hidden behind the composer.
function recipeShare(page: Page) {
  return page.evaluate(() => {
    const reply = document.querySelector(".reply")!.getBoundingClientRect();
    const composer = document.querySelector(".follow-up")!.getBoundingClientRect();
    const thread = document.querySelector(".thread")!.getBoundingClientRect();
    const top = Math.max(reply.top, thread.top, 0);
    const bottom = Math.min(reply.bottom, thread.bottom, composer.top, innerHeight);
    return Math.max(0, bottom - top) / innerHeight;
  });
}

for (const size of [{ width: 360, height: 800 }, { width: 412, height: 915 }]) {
  test(`gives the recipe most of a ${size.width}px phone screen`, async ({ page }, info) => {
    test.skip(info.project.name !== "phone", "phone layout");
    await page.setViewportSize(size);
    await openRecipe(page);
    const composer = page.locator(".follow-up");
    const input = page.getByLabel("Ask a follow-up");

    // The page scrolls, not a box inside it, and the composer is one slim row pinned to the bottom.
    expect(await page.getByRole("region", { name: "Recipe conversation" }).evaluate((node) => getComputedStyle(node).overflowY)).toBe("visible");
    await expect(input).toBeInViewport();
    await expect(page.getByRole("button", { name: "Serves 6" })).toBeHidden();
    const bar = (await composer.boundingBox())!;
    expect(bar.height).toBeLessThan(72);
    expect(Math.round(bar.y + bar.height)).toBe(size.height);
    const opening = await recipeShare(page);
    await page.screenshot({ path: info.outputPath(`phone-${size.width}-top.png`) });

    // Scrolled into the recipe, everything above it is gone and only the composer remains.
    await page.evaluate(() => window.scrollTo(0, 900));
    await expect(input).toBeInViewport();
    const reading = await recipeShare(page);
    expect(reading).toBeGreaterThan(0.88);
    await expect(page.getByRole("button", { name: "Jump to the bottom" })).toBeInViewport();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(size.width);
    await page.screenshot({ path: info.outputPath(`phone-${size.width}-reading.png`) });
    console.log(`${size.width}x${size.height}: recipe shows on ${Math.round(opening * 100)}% of the screen on opening, ${Math.round(reading * 100)}% while reading`);

    // The jump button lands on the end of the conversation.
    await page.getByRole("button", { name: "Jump to the bottom" }).click();
    await expect(page.getByRole("button", { name: "Export recipe" })).toBeInViewport();

    // Tapping the composer brings back the quick changes. With the keyboard open (the window shrinks, as
    // interactive-widget=resizes-content makes Chrome on Android do), the composer and chips stay above it.
    await input.click();
    await expect(page.getByRole("button", { name: "Serves 6" })).toBeVisible();
    await page.setViewportSize({ width: size.width, height: Math.round(size.height * 0.55) });
    await input.fill("Make it vegetarian");
    await expect(input).toBeFocused();
    await expect(input).toBeInViewport();
    await expect(page.getByRole("button", { name: "Serves 6" })).toBeInViewport();
    await expect(page.getByRole("button", { name: "Send reply" })).toBeInViewport();
    const keyboardBar = (await composer.boundingBox())!;
    expect(Math.round(keyboardBar.y + keyboardBar.height)).toBe(Math.round(size.height * 0.55));
    await page.screenshot({ path: info.outputPath(`phone-${size.width}-keyboard.png`) });
  });
}

test("keeps the boxed thread and full composer on desktop", async ({ page }, info) => {
  test.skip(info.project.name !== "desktop", "desktop layout");
  await openRecipe(page);
  const thread = page.getByRole("region", { name: "Recipe conversation" });
  expect(await thread.evaluate((node) => getComputedStyle(node).overflowY)).toBe("auto");
  expect(await page.evaluate(() => document.documentElement.scrollHeight)).toBe(page.viewportSize()!.height);
  await expect(page.getByText("Ask a follow-up", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Serves 6" })).toBeVisible();
  await thread.evaluate((node) => node.scrollTop = 300);
  await expect(page.getByRole("button", { name: "Jump to the bottom" })).toBeInViewport();
  await page.screenshot({ path: info.outputPath("desktop.png") });
});
