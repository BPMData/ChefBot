import { chromium, expect, test } from "@playwright/test";

const fixtureApi = "http://localhost:8911";
const photo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAMAAAACCAIAAAASFvFNAAAAEUlEQVR4nGP8v5QBApgYYAAAHsMBqGMfgmwAAAAASUVORK5CYII=";

function savedRecipe(title: string, cuisine: string, count: number, lastOpened: number) {
  return {
    id: title, title, favorite: true, updated: lastOpened, access_count: count, last_accessed: lastOpened,
    settings: { cuisine, must_not: "", audience: "A working professional.", dessert: false, pantry: false, restrictions: [] },
    messages: [{ role: "user", content: "carrots and cumin" }, { role: "assistant", title, content: "Roast the carrots." }],
    photos: { "1": photo },
  };
}

test("ranks Favorites folders and restores folder and search navigation", async ({ page }) => {
  await page.goto("./");
  await page.getByRole("button", { name: "Settings" }).click();
  const recipes = [
    savedRecipe("Failed Picture Carrots", "Greek", 1, 200),
    savedRecipe("Cajun Carrot Stew", "us_cajun", 10, 100),
    savedRecipe("Creole Carrots", "us_creole", 5, 800),
    savedRecipe("Imported Pantry Carrots", "Nothing in particular", 100, 300),
  ];
  await page.getByLabel("Import recipes").setInputFiles({
    name: "fixture-backup.json", mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify({ format: "chefbot-recipes", version: 1, conversations: recipes })),
  });
  await expect(page.getByText("Added 4, updated 0.")).toBeVisible();
  await page.getByRole("button", { name: "Back to recipes" }).click();
  await page.getByRole("button", { name: "Favorites", exact: true }).click();
  const folders = page.getByRole("list", { name: "Cuisine folders" });
  await expect(folders.getByRole("button")).toHaveText(["The Americas2 recipes", "Europe1 recipe", "Any cuisine1 recipe"]);
  await folders.getByRole("button", { name: /The Americas/ }).click();
  await folders.getByRole("button", { name: /United States/ }).click();
  await expect(folders.getByRole("button")).toHaveText(["Cajun1 recipe", "Creole1 recipe"]);
  await expect(page.getByRole("heading", { name: "Recently accessed" })).toBeVisible();
  await folders.getByRole("button", { name: /Cajun/ }).click();
  const crumb = page.getByRole("navigation", { name: "Favorites folders" });
  await expect(crumb.locator("[aria-current=page]")).toHaveText("Cajun");
  await page.getByRole("button", { name: /Cajun Carrot Stew/ }).click();
  await page.getByRole("button", { name: "Back to Favorites" }).click();
  await expect(crumb.locator("[aria-current=page]")).toHaveText("Cajun");
  const search = page.getByRole("textbox", { name: "Search favorites" });
  await search.fill("greek cumin");
  await page.getByRole("button", { name: /Failed Picture Carrots/ }).click();
  await page.getByRole("button", { name: "New picture" }).click();
  await expect(page.getByRole("status")).toHaveText("ChefBot couldn’t make a picture. Please try again.");
  await expect(page.getByRole("img", { name: "Failed Picture Carrots" })).toHaveAttribute("src", photo);
  await page.goBack();
  await expect(search).toHaveValue("greek cumin");
  await expect(crumb.locator("[aria-current=page]")).toHaveText("Cajun");
  await page.getByRole("button", { name: "Clear search" }).click();
  await crumb.getByRole("button", { name: "Favorites" }).click();
  await folders.getByRole("button", { name: /Any cuisine/ }).click();
  await page.getByRole("button", { name: /Imported Pantry Carrots/ }).click();
  await page.getByRole("button", { name: "New picture" }).click();
  const image = page.getByRole("img", { name: "Imported Pantry Carrots" });
  await expect(image).toBeVisible();
  await expect(image).not.toHaveAttribute("src", photo);
  await page.reload();
  await expect(image).not.toHaveAttribute("src", photo);
});

test("stops a replacement and keeps the saved reply", async ({ page }) => {
  await page.goto("./");
  await page.getByLabel("Ingredients", { exact: true }).fill("carrots and cumin");
  await page.getByRole("button", { name: "Make a recipe" }).click();
  await expect(page.getByRole("heading", { name: "Cumin Carrots", level: 1 })).toBeVisible();
  await page.getByRole("textbox", { name: "Ask a follow-up" }).fill("Make it spicy");
  await page.getByRole("button", { name: "Send reply" }).click();
  await expect(page.getByRole("heading", { name: "Spicy Cumin Carrots", level: 1 })).toBeVisible();
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByRole("textbox", { name: "Edit your follow-up" }).fill("slow fixture replacement");
  const accepted = page.waitForResponse((response) => new URL(response.url()).pathname === "/api/jobs" && response.status() === 202);
  await page.getByRole("button", { name: "Send reply" }).click();
  const { job_id } = await (await accepted).json();
  await page.getByRole("button", { name: "Stop", exact: true }).click();
  await expect(page.getByText("Stopped. You can edit your request and send it again.")).toBeVisible();
  await expect(page.getByRole("textbox", { name: "Edit your follow-up" })).toHaveValue("slow fixture replacement");
  await expect(page.getByText("Make it spicy", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Spicy Cumin Carrots", level: 1 })).toBeVisible();
  const visitor = await page.evaluate(() => localStorage.getItem("chefbot.visitor")!);
  const replay = await page.request.get(`${fixtureApi}/api/jobs/${job_id}/events`, { headers: { "X-Visitor-ID": visitor } });
  expect(await replay.text()).toContain("event: stopped");
  await page.reload();
  await expect(page.getByRole("textbox", { name: "Edit your follow-up" })).toHaveValue("slow fixture replacement");
});

test("recovers the same job in a new browser session when the submit response is lost", async ({}, info) => {
  const { baseURL, viewport, isMobile, hasTouch, launchOptions } = info.project.use;
  const profile = info.outputPath("disposable-browser-profile");
  const launch = () => chromium.launchPersistentContext(profile, { baseURL, viewport, isMobile, hasTouch, ...launchOptions });
  let context = await launch();
  let generationRequests = 0;
  let jobId = "";
  const observedReplays: string[] = [];
  let releaseSubmit: () => void = () => {};
  const holdResponse = new Promise<void>((resolve) => { releaseSubmit = resolve; });
  try {
    const first = context.pages()[0];
    let serverAccepted: () => void = () => {};
    const accepted = new Promise<void>((resolve) => { serverAccepted = resolve; });
    await first.route(fixtureApi + "/api/jobs", async (route) => {
      generationRequests += 1;
      const response = await route.fetch();
      expect(response.status()).toBe(202);
      jobId = (await response.json()).job_id;
      serverAccepted();
      await holdResponse;
      await route.abort().catch(() => {});
    });
    await first.goto("./");
    await first.getByLabel("Ingredients", { exact: true }).fill("slow fixture carrots");
    await first.getByRole("button", { name: "Make a recipe" }).click();
    await accepted;
    await first.close();
    releaseSubmit();
    await context.close();

    context = await launch();
    context.on("request", (request) => {
      const path = new URL(request.url()).pathname;
      if (request.method() === "POST" && path === "/api/jobs") generationRequests += 1;
      if (/^\/api\/jobs\/[^/]+\/events$/.test(path)) observedReplays.push(path);
    });
    const reopened = context.pages()[0];
    await reopened.goto("./");
    await expect(reopened.getByText("Ready: Cumin Carrots", { exact: true })).toBeVisible();
    await expect(reopened).toHaveTitle("Recipe ready · ChefBot");
    await reopened.getByRole("button", { name: "Open recipe" }).click();
    await expect(reopened.getByRole("heading", { name: "Cumin Carrots", level: 1 })).toBeVisible();
    await expect(reopened).toHaveTitle("ChefBot");
    expect(generationRequests).toBe(1);
    expect(observedReplays).toEqual([`/api/jobs/${jobId}/events`]);
  } finally {
    releaseSubmit();
    await context.close();
  }
});

test("saves a reply and shows a completion notice while browsing elsewhere", async ({ page }) => {
  await page.goto("./");
  await page.getByLabel("Ingredients", { exact: true }).fill("slow fixture carrots");
  await page.getByRole("button", { name: "Make a recipe" }).click();
  await expect(page.getByRole("heading", { name: "Writing your recipe" })).toBeVisible();
  await page.getByRole("button", { name: "Back to recipes" }).click();
  await page.getByRole("button", { name: "Favorites", exact: true }).click();
  await expect(page.getByText("Ready: Cumin Carrots", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Favorites", level: 1 })).toBeVisible();
  await page.getByRole("button", { name: "Open recipe" }).click();
  await expect(page.getByRole("heading", { name: "Cumin Carrots", level: 1 })).toBeVisible();
  await expect(page.getByText("Ready: Cumin Carrots", { exact: true })).toHaveCount(0);
});
