import { defineConfig } from "@playwright/test";
import { resolve } from "node:path";

export default defineConfig({
  testDir: "./tests",
  timeout: 35_000,
  webServer: [
    {
      command: `${process.env.CHEFBOT_TEST_PYTHON ?? ".venv/bin/python"} -m uvicorn --app-dir tests/server browser_fixture:app --host localhost --port 8911`,
      cwd: resolve(".."),
      url: "http://localhost:8911/healthz",
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --host localhost",
      env: { VITE_API_URL: "http://localhost:8911" },
      url: "http://localhost:5173/ChefBot/",
      reuseExistingServer: false,
    },
  ],
  use: {
    baseURL: "http://localhost:5173/ChefBot/",
    actionTimeout: 6_000,
    reducedMotion: "reduce",
    launchOptions: { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE },
  },
  projects: [
    { name: "phone", use: { viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true } },
    { name: "desktop", use: { viewport: { width: 1280, height: 800 } } },
  ],
});
