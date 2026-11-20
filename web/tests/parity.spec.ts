import { expect, test } from "@playwright/test";

test("keeps preferences, restores a closed tab's job, and finds the saved recipe by ingredient", async ({ page, context }, info) => {
  let jobs = 0;
  context.on("request", (request) => { if (request.method() === "POST" && request.url().endsWith("/api/jobs")) jobs++; });
  await page.goto("./");
  await page.getByRole("button", { name: "Settings" }).click();
  await page.getByLabel("Appearance").selectOption("light");
  await page.goBack();
  await page.getByLabel("Never use", { exact: true }).fill("walnuts");
  await page.getByRole("button", { name: "Surprise me" }).click();
  const preview = page.getByRole("dialog");
  const cuisine = await preview.getByRole("heading", { level: 2 }).innerText();
  await preview.getByRole("button", { name: "Use " + cuisine, exact: true }).click();
  await page.getByLabel("Pantry defaults").check();
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await expect(page.getByLabel("Never use", { exact: true })).toHaveValue("walnuts");
  await expect(page.getByRole("button", { name: "Anything", exact: true })).toBeVisible();
  await page.getByRole("button", { name: cuisine, exact: true }).click();
  await page.getByRole("button", { name: "Use " + cuisine, exact: true }).click();
  await expect(page.getByLabel("Pantry defaults")).toBeChecked();
  await page.getByLabel("Ingredients", { exact: true }).fill("carrots, marjoram");
  await page.screenshot({ path: info.outputPath("home-light.png") });
  const post = page.waitForRequest((request) => request.url().endsWith("/api/jobs"));
  await page.getByRole("button", { name: "Make a recipe" }).click();
  expect((await post).postDataJSON()).toMatchObject({ ingredients: "carrots, marjoram", must_not: "walnuts", pantry: true });
  await expect(page.getByRole("heading", { name: "Writing your recipe" })).toBeVisible();
  await page.close();

  const reopened = await context.newPage();
  await reopened.goto("./");
  await reopened.getByRole("button", { name: /New recipe In progress/ }).click();
  await expect(reopened.getByRole("heading", { name: "Cumin Carrots", level: 1 })).toBeVisible();
  expect(jobs).toBe(1);
  await expect(reopened.getByText("Never: walnuts")).toBeVisible();
  await reopened.goBack();
  await reopened.getByLabel("Search recipes").fill("MARJORAM roast");
  await expect(reopened.getByRole("button", { name: /^Cumin Carrots/ })).toBeVisible();
  await reopened.getByLabel("Search recipes").fill("plums");
  await expect(reopened.getByText("No matching recipes.")).toBeVisible();
  await reopened.getByLabel("Search recipes").fill("");
  reopened.once("dialog", (dialog) => dialog.dismiss());
  await reopened.getByRole("button", { name: "Delete Cumin Carrots" }).click();
  await expect(reopened.getByRole("button", { name: /^Cumin Carrots/ })).toBeVisible();
  reopened.once("dialog", (dialog) => dialog.accept());
  await reopened.getByRole("button", { name: "Delete Cumin Carrots" }).click();
  await expect(reopened.getByText("Recipes you make appear here.")).toBeVisible();
  await reopened.reload();
  await expect(reopened.getByText("Recipes you make appear here.")).toBeVisible();
  await reopened.getByLabel("Never use", { exact: true }).fill("");
  await reopened.reload();
  await expect(reopened.getByLabel("Never use", { exact: true })).toHaveValue("");
});

test("keeps the composer in reach and sends tweaks against the selected recipe", async ({ page }, info) => {
  const steps = Array.from({ length: 60 }, (_, i) => (i + 1) + ". Stir the carrots.").join("\n");
  const conversation = {
    id: "fixture-long-recipe", title: "Roasted carrots", updated: 1, last_accessed: 1, access_count: 0, favorite: true,
    settings: { audience: "A working professional.", cuisine: "greek", pantry: true, dessert: false, restrictions: [], must_not: "peanuts" },
    messages: [{ role: "user", content: "carrots" }, { role: "assistant", title: "Roasted carrots", content: "Recipe Title: Roasted carrots\n\n" + steps }],
    photos: {},
  };
  await page.goto("./");
  await page.getByRole("button", { name: "Settings" }).click();
  await page.getByLabel("Import recipes").setInputFiles({ name: "recipes.json", mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify({ format: "chefbot-recipes", version: 1, conversations: [conversation] })) });
  await expect(page.getByText("Added 1, updated 0.")).toBeVisible();
  await page.goBack();
  await page.getByRole("button", { name: /^Roasted carrots/ }).click();
  const input = page.getByLabel("Ask a follow-up");
  await expect(input).toBeInViewport();
  await page.getByRole("region", { name: "Recipe conversation" }).evaluate((node) => node.scrollTop = 300);
  await expect(input).toBeInViewport();
  await expect(page.getByRole("button", { name: "Jump to the bottom" })).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(page.viewportSize()!.width);
  await page.screenshot({ path: info.outputPath("conversation.png") });

  await page.getByRole("button", { name: "The 1817 version (beta)" }).click();
  await expect(page.getByRole("dialog", { name: "Historical recipes (beta)" })).toBeVisible();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(input).toHaveValue("");
  const request = page.waitForRequest((req) => req.url().endsWith("/api/jobs"));
  await page.getByRole("button", { name: "Serves 6" }).click();
  const body = (await request).postDataJSON();
  expect(body.ingredients).toBe("Scale it to serve 6.");
  expect(body.history).toEqual(conversation.messages.map(({ role, content }) => ({ role, content })));
  expect(body).toMatchObject(conversation.settings);
  await expect(page.getByRole("heading", { name: "Spicy Cumin Carrots", level: 1 })).toBeVisible();

  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByLabel("Edit your follow-up").fill("Use fewer carrots");
  await page.route("**/api/jobs/*/events", (route) => route.fulfill({ status: 404, body: "{}" }));
  await page.getByRole("button", { name: "Send reply" }).click();
  await expect(page.getByLabel("Edit your follow-up")).toHaveValue("Use fewer carrots");
  await expect(page.getByText("Scale it to serve 6.", { exact: true })).toHaveCount(1);
  await expect(page.getByRole("heading", { name: "Spicy Cumin Carrots", level: 1 })).toBeVisible();
});

test("browses a compact region grid and previews a cuisine before choosing it", async ({ page }, info) => {
  await page.goto("./");
  await page.getByLabel("Ingredients", { exact: true }).fill("chickpeas");
  await page.getByRole("button", { name: "Browse cuisines", exact: true }).click();
  const picker = page.getByRole("dialog", { name: "Browse cuisines" });
  const tiles = picker.locator(".catalog-tile");
  await expect(tiles).toHaveCount(6);
  await expect(tiles.first().locator(".region-icon path")).toHaveCount(1);
  await page.evaluate(() => document.fonts.ready);
  const [first, second] = await tiles.evaluateAll((buttons) => buttons.map((button) => {
    const { x, y } = button.getBoundingClientRect();
    return { x, y };
  }));
  expect(first.y).toBe(second.y);
  expect(second.x).toBeGreaterThan(first.x);
  await page.screenshot({ path: info.outputPath("cuisine-browser.png") });
  await picker.getByLabel("Find a cuisine").fill("Greek");
  await picker.getByRole("button", { name: "Greek", exact: true }).click();
  const details = page.getByRole("dialog", { name: "Greek", exact: true });
  await expect(details.getByRole("img", { name: "Greek region highlighted" })).toBeVisible();
  await expect(details.getByText("Classic flavors", { exact: true })).toBeVisible();
  await expect(details.getByRole("button", { name: "Use Greek" })).toBeInViewport();
  await page.screenshot({ path: info.outputPath("cuisine-info.png") });
  await page.goBack();
  await expect(picker.getByLabel("Find a cuisine")).toHaveValue("Greek");
  await picker.getByRole("button", { name: "Greek", exact: true }).click();
  await details.getByRole("button", { name: "Use Greek" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.getByLabel("Ingredients", { exact: true })).toHaveValue("chickpeas");
  await page.getByRole("button", { name: "Greek", exact: true }).click();
  await expect(details).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(details).toHaveCount(0);
});
