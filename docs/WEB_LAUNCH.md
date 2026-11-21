# Plan: ChefBot for the web, without Flet (for Codex)

Decided with Bryan, 2026-11-19. This replaces the Flet server-mode plan in `docs/WEB_DEMO.md`; that file's
**limits, privacy and AGPL sections still apply** (sections 2, 3, 5, 7), its Flet and Cloud Run volume details don't.

Before anything: read `CLAUDE.md` (its ground rules apply to you), `HANDOFF.md`, `HANDOFF.local.md` if present,
and AllAboard's `docs/DEPLOYMENT.md` (BPMData/allaboard), which records hard-won Cloud Run rules this plan reuses.

## Android and browser parity, 2026-11-21

GitHub deployment [7945648675](https://github.com/BPMData/ChefBot/deployments/github-pages) identifies the
successful public Pages build as `351bd48a32d1bad2c03b6473055858029c0688bf`. It still served that build on
November 21. The local physical review used PR #43's web commit `b5cd7a767167bff27fa1278620d23df21530b3c8`
and the recovery fix `0c330aadf50e1cecccbb171f4a54e14175f52895`, based on merged PR #43. The web ran in a
disposable Chromium 160.0.8176.0 profile over USB against the offline fixture.

The installed ChefBot APK reports version `0.1.0` and Android version code `2001`. Android reports a
November 15 last update, and the installed base APK's SHA-256 matches the November 15 arm64 artifact
byte for byte. Bryan separately confirmed native ingredient recognition. His photo showed a nearly empty lo mein
container surrounded by empty cans. The APK identified noodles as the only ingredient. The remaining
handset observations came from the offline fixture and checks that required no model calls.

The APK is the UX reference, and the web can improve on it. The primary live web check is everyday
background use. Start a recipe, switch to another tab, window or app, then return to a completed recipe
in the original tab. Same-job recovery after a tab closure or browser force-stop is a secondary check.
In desktop Chromium with the offline FastAPI fixture, both a tab switch and a separate-window switch
left the reply to finish and save before returning. Each recipe generated one POST.

| Flow | Flet and handoff reference | Web review build and remaining verification |
| --- | --- | --- |
| Start a recipe | In-app camera with gallery and cancel. Saved preferences and an opening summary of the chosen options. | Browser camera capture and a separate image picker on touchscreens. Exclusions and pantry defaults persist. On the handset, the APK opened its camera and Gallery. Both web paths returned a disposable image and populated ingredients through the offline fixture. Bryan confirmed native recognition on the lo mein photo. Reserve any further model checks for the web. |
| Cuisine selection | The Flet list drills down through regions and has a separate About icon for each leaf. The native globe and regional maps open details on a leaf tap. | PR #42's compact searchable picker and automatic infoboxes from both entry points stay in place. One-finger drag worked on both apps. On the handset the web opened infoboxes automatically from the picker and map, and Android Back returned to the search or map. The APK opened details from the map and selected directly from the list. Offline Playwright also checks the globe zoom after Back. |
| Saved recipes | Flet Favorites has access-ranked continent, country and cuisine folders, recent shortcuts at the root and country level, and search across all starred recipes. | The APK's separate Favorites screen and recent shortcuts appeared on the handset. Web Favorites follows the Flet structure, with counts, five recent at the root, three per country, a separate Any cuisine folder, and breadcrumbs. Browser Back restores the folder and query. Playwright checks ranking, the legacy Greek label, cross-folder search, and version 1 backup round trips. IndexedDB and backup format stay in place. |
| Sharing and pictures | The Android share sheet can hand text, PDF and dish photo to a mail app. Dish pictures are generated from saved recipes. | Playwright checks text and both file signatures handed to Web Share. Browser and target app determine attachment support. Saved and imported replies can generate pictures using the saved title after the original job expires. A failed replacement leaves the previous image in place. On the handset Gmail received the complete fixture text, PDF and PNG from the web share sheet. The APK-to-Gmail check with a disposable pictured recipe remains open. |
| Stop | Flet can keep the streamed partial recipe. | The web API cancels the draft, review or revision in progress and replays a stopped event. The web restores the request for editing and keeps the previous saved reply and pictures. Only finished, checked replies enter history. |
| Background and recovery | Android has a foreground service, a system notification, and an automatic retry for some connection losses. | The server owns the job. The browser saves its ID before submitting, and reopens the same event stream after a tab or browser restart. The tab title and an in-app notice show replies that finish while away. A closed browser receives no push notification. Offline tests cover a new tab and a restarted disposable browser profile with one generation POST, including when the original response never reached the browser. The first handset force-stop replay returned 404 for the saved job. The recovery fix commits the visitor ID in IndexedDB before sending requests. On the handset both tab closure and force-stop recovered the original job. The force-stop test removed the legacy localStorage key before restart. The fixture logged one generation POST per test. The deployed web build still needs to prove normal background completion over mobile data. Test force-stop as a separate recovery case. |
| Settings | The APK owns its own settings and history. | Dark, Light and System appearance, optional email recipient, local recipes and version 1 backups. The service owns model selection, credentials and quotas. |

The result can be replayed for 30 minutes after completion as long as the service instance survives.
The previously reported one-hour recovery describes one production run. For the live web check, verify
that Pages serves the approved build with the matching API. Start a disposable recipe and leave the original
tab open. Switch to another tab, window or app while ChefBot is drafting and stay away long enough for the
reply to finish. On return, verify that the checked recipe is already saved and the API received one generation
POST. Include a phone on mobile data in this check.

For the separate recovery check, close the tab or force-stop the browser during a disposable generation.
Reopen the same profile within the replay window and verify that the recipe resumes or is ready from the
original job with one generation POST. Request-based Cloud Run CPU throttling can delay work after the
browser disconnects. Coordinate both publications after approval, starting with the API, which continues to
accept the older Pages client's requests.

### Physical Android review

Check out the SHA recorded in the PR. Keep the installed APK and its data in place. Record the installed
version name and code and the last-update date to distinguish builds that share a version number.

```bash
git rev-parse HEAD
adb shell dumpsys package io.github.bpmdata.chefbot | rg 'versionName|versionCode|lastUpdateTime'
```

Use disposable recipes in a dedicated Android browser profile and the offline fixture. From the repo root,
run the API and Vite in separate terminals with the normal dependencies installed. The fixture gives
requests containing `slow fixture` 20 seconds of drafting time with these settings.

```bash
CHEFBOT_USAGE_BUCKET= OPENROUTER_API_KEY= CHEFBOT_FIXTURE_JOB_TTL=120 CHEFBOT_FIXTURE_SLOW_SECONDS=20 \
  .venv/bin/python -m uvicorn --app-dir tests/server browser_fixture:app --host localhost --port 8911
VITE_API_URL=http://localhost:8911 npm --prefix web run dev -- --host localhost --port 5183
adb reverse tcp:5183 tcp:5183
adb reverse tcp:8911 tcp:8911
```

Open `http://localhost:5183/ChefBot/` on the phone through the USB connection. Review the following.

- Drag the globe with one finger. Open a cuisine from a globe region and from a typed picker search.
  Observe the infobox before choosing. Use system Back and confirm that the previous map or search returns.
  On the APK, check whether a list item opens its infobox directly or requires the About icon.
- Use Camera and Gallery with a disposable photo. Confirm that an image returns and populates ingredients.
- Generate a dish picture in the web fixture. Select Email or Share files and choose the intended mail app.
  Check the full text and both the PDF and the original image in the draft, then close the draft before sending.
  On the APK, use an existing disposable recipe with a picture if one is available.
- Star disposable recipes from different cuisines, reopen them at different rates, and check folder order,
  navigation and search. Record any installed-APK differences before applying the newer artifact as a reference.
- Start a recipe with `slow fixture carrots`. Switch to another app with the ChefBot tab still open. Return
  after it finishes and check the saved reply. Try Stop on a separate recipe. Tab closure and browser
  force-stop test same-job recovery. Reopen the same profile before replay expires and confirm one
  `POST /api/jobs` per generation. Reserve real model calls for the web. Live checks and both publications
  require Bryan's approval.

The review prompt checks numerical discrepancies and cooking steps that can overlap. The offline tests
cover that pipeline. Real-model timing and false-positive checks still require an approved live run.

## Why

- Flet's web mode redraws in Python on the server and ships every frame over a WebSocket. A browser-native front
  end is faster, and AllAboard (much heavier) already proves that stack on Bryan's Cloud Run.
- **A real globe:** MapLibre GL JS's globe view zooms smoothly from space to county level, instead of today's
  stacked flat maps.
- **The second-model check before showing a recipe** (HANDOFF backlog, "Second-model review loop") needs a good
  waiting screen. In a browser that's an EOMD piece (BPMData/EOMD) running directly, no web-view extension.
- **Generation runs on the server**, so closing the tab or switching apps doesn't lose a reply.

## What stays as it is

- **The Flet app (`src/main.py`) and the Android APK are untouched.** Desktop and Android keep working as today.
  A PWA may replace the APK later, only if it matches the app's feel on Bryan's phone; that's a later test, not
  this plan.
- `src/chefbot/api.py`, `prompts.py`, `cuisines.py` (+ `cuisines/*.json`), `recipe.py` and `export.py` import no
  Flet. The new server imports them; don't fork copies. If one needs a change, keep the Flet app's behaviour the
  same and its tests passing.

## The shape

```
Browser (bpmdata.github.io/ChefBot/, GitHub Pages, built from web/ by Actions)
  React + Vite + TS + Tailwind + motion (same stack as AllAboard), MapLibre GL JS, EOMD piece
  Saved recipes + pictures: IndexedDB in the visitor's own browser (no server storage per visitor)
        |  HTTPS: POST /api/jobs, GET /api/jobs/<id>/events (Server-Sent Events)
        v
Cloud Run "chefbot-api" (Python, FastAPI, imports src/chefbot/*)
  OPENROUTER_API_KEY from Secret Manager; usage counters in memory, saved as one JSON object in a bucket
        v
OpenRouter (main model, then the reviewer model)
```

Why the page lives on GitHub Pages rather than inside the Cloud Run container (AllAboard does the latter):
the page appears instantly even when the API is cold, and the cold start hides behind the "working" animation.
A project repo's Pages site is `bpmdata.github.io/ChefBot/` automatically; the hub only needs a link to it.

## Where to run

Phases 1 to 4 need nothing from Bryan's laptop and can run as a Codex cloud task, as long as the environment
can reach package registries (pip, npm). Two exceptions:

- **Phase 3's live check** needs a real OpenRouter key. Tests always mock the model; if the cloud task has no key,
  write the reviewer and its tests, and leave the live run on the lamb-fries example for a laptop session.
- **Phase 4's shapefiles** are gitignored. Download the public originals into `assets/maps/source/` (same folder
  names as `tools/build_map_data.py` expects): Natural Earth 10m admin 0 countries (the Palestine point-of-view
  edition) and 10m admin 1 states and provinces from naturalearthdata.com, and the Census Bureau's
  `cb_2025_us_county_500k` from census.gov. If the download is blocked, build the spike from the longitude and
  latitude already in `src/chefbot/maps/globe.json` and say so.

Phase 5 (deploy) needs `gcloud` signed in to Bryan's project: do it on his laptop.

## Phases (each ends in a commit; open the PR after phase 1 and keep pushing to it)

| Phase | Needs Bryan? | Done when |
|---|---|---|
| 1. API server, local | No | A recipe job runs end to end with a mocked model; tests pass |
| 2. Front end, local | No | Ingredients form, waiting animation, recipe card, saved recipes, at 375 px and desktop |
| 3. Review step | No (dev key for live checks) | Catches both mistakes in `docs/review-loop/example-lamb-fries.md` |
| 4. Globe spike | No | MapLibre globe with 3 cuisine regions, zooms to US counties |
| 5. Deploy | **Yes** | Pages URL makes a real recipe from a phone on mobile data |

Stop after any phase if the session runs out; say in the PR where you stopped.

### Phase 1: API server (`server/`)

- FastAPI app in `server/app.py`, its own `server/requirements.txt` (fastapi, uvicorn, httpx, markdown, fpdf2,
  pillow; no Flet). It adds `src/` to the path and imports `chefbot.api`, `chefbot.prompts`, `chefbot.cuisines`.
- Endpoints:
  - `GET /healthz` returns `{"status": "ok"}` (the front end pings it on load to wake the service).
  - `GET /api/cuisines`: the cuisine tree, for the picker and the globe.
  - `POST /api/jobs`: `{ingredients, must_not, cuisine, audience, dessert, pantry, history?}` (history = the
    earlier turns, for follow-up edits; the browser owns the conversation). Returns `{job_id}`.
  - `GET /api/jobs/<id>/events`: Server-Sent Events: `stage` (drafting / checking / fixing / done),
    `progress` (ingredient names and step count parsed from the draft as it streams, for the animation),
    `result` (final markdown, title, list of fixes), `error` (a plain message, safe to show).
    Reconnecting with the same id replays from the start; jobs are kept in memory 30 minutes after finishing.
  - `POST /api/photo/ingredients` (image, size-capped) and `POST /api/jobs/<id>/picture` (dish picture).
  - `POST /api/pdf` returns the PDF bytes from `export.recipe_pdf` (bake the CJK fonts into the image).
- **Limits** (`server/limits.py`, numbers in one dict): per-visitor (a random id the browser sends in a header;
  friendly, not secure) and a **global daily cap**, which together with the OpenRouter key's credit limit is the
  real protection. Counters in memory behind one lock, written to `gs://<bucket>/usage.json` after each change
  over the Cloud Storage JSON API (as AllAboard's `GcsBackend` does), read back on start, and **fail open** if
  the bucket is unreachable (AllAboard rule R7). Plain messages when a limit is hit; no cost talk.
- Model and thinking level are fixed on the server; the browser can't choose them. Max message length enforced.
- CORS: allow only the Pages origin (`https://bpmdata.github.io`) and `http://localhost:5173`.
- Tests in `tests/server/` with a mocked `OpenRouter` (never call the real API): job lifecycle, SSE replay,
  each limit including after a simulated restart, CORS, message and photo size caps.

### Phase 2: front end (`web/`)

- Vite + React 19 + TypeScript + Tailwind 4 + `motion`, mirroring AllAboard's `package.json` versions. Dark
  theme by default, Fraunces + DM Sans, content in a centered column on desktop. **No emojis**; icons are
  `lucide-react` or SVG.
- Screens: home (ingredients, must-not, cuisine picker, audience/dessert/pantry options, Recents and Favorites),
  the conversation (recipe card, follow-up box, Edit/Delete on the last follow-up, Try again), Settings
  (Source code link for AGPL, a note that recipes stay in this browser only). Port behaviour from `src/main.py`
  and `README.md`; don't invent new features.
- Storage: IndexedDB (via `idb-keyval` or similar) for conversations, favourites and pictures. Same fields as
  `history.py` (`favorite`, `access_count`, `last_accessed`, `updated`) so an export/import is possible later.
- **Keeping recipes safe** (browser storage can vanish; see "Recipe backups" below for why): call
  `navigator.storage.persist()` on the first save, and put export/import in Settings in this phase.
- Export: Copy, PDF (server endpoint), HTML (built in the browser), Email as a `mailto:` link (shorten long
  recipes, as `export.mailto_link` does), Share via `navigator.share` with copy as the fallback.
- Ingredient photos: `<input type="file" accept="image/*" capture="environment">`, resized in the browser
  before upload.
- **Waiting screen:** a placeholder animation built with `motion` first (dots that settle into the ingredient
  names from `progress` events, then a "Checking" stage). Leave a clean slot for an EOMD piece; making that piece
  happens in the EOMD repo under its own process, not here. The stages shown must be the real ones from the
  server, not a timer.
- Base URL of the API from `VITE_API_URL`. Playwright check at 375x812 and 1280x800.

### Phase 3: the review step (server)

Follow the flow already designed in HANDOFF's "Second-model review loop" backlog item, with one change Bryan
made today: **the recipe is shown only after it's checked**, behind the waiting screen. Draft with the main model;
send the full recipe to a fast reviewer from Z.ai, Moonshot or DeepSeek, asking for JSON issues (issue,
location, fix), not a rewrite; minor issues get targeted edits, major ones (diet, allergen, must-not violation,
missing step) one revision round with the main model. The result lists what was fixed ("Fixed 2 things", tap to
see). Put the reviewer model and prompt in `prompts.py` so the Flet app can adopt it later.
Check it on `docs/review-loop/example-lamb-fries.md` (both mistakes caught) and note the total time in the PR.
Keep a server flag that streams the draft instead (Bryan's earlier choice) in case the wait proves too long.

### Phase 4: globe spike (`web/src/globe/`)

- MapLibre GL JS v5, `projection: globe`. No third-party tile service: draw land and borders from Natural Earth
  GeoJSON shipped with the page, styled to match the app.
- Add a `--geojson` output to `tools/build_map_data.py` that writes the cuisine regions in longitude/latitude
  (skip its screen projection; reuse its region definitions). The source shapefiles are in
  `assets/maps/source/` on Bryan's Mac (gitignored); if they're missing, download the same Natural Earth and
  2025 Census files it names.
- Spike scope: three regions (one country-level, one Indian state group, one US county group such as
  Italian-American), hover and tap to pick, fly-to on tap. Report frame rate on a phone and the GeoJSON size.
  The full map replaces the cuisine picker only after Bryan sees the spike.
- The local preview uses 189,337 bytes of GeoJSON. In a single-worker Chromium run, the flight from the
  globe to New York City averaged 41.3 rendered frames/s at 375 × 812 and 39.3 at 1280 × 800.
  These are headless measurements. Record device performance during the phone check.

### Recipe backups (export in phase 2; Drive after phase 5 is live)

Why: recipes live in IndexedDB, which is lost when someone clears "cookies and site data" (not plain "cached
files"), in a private window, if the browser evicts it under storage pressure, and on **iPhone Safari after 7
days without a visit** (Safari's tracking protection; an app added to the Home Screen is exempt). Clearing site
data for `bpmdata.github.io` also clears every page on Bryan's hub at once, since they share one origin. Name the
database `chefbot` so it never collides with another hub page's storage.

1. **One file format** (`chefbot-recipes` JSON, with a `version` field): conversations with the same fields as
   `history.py`, pictures as base64. Used for single-recipe export, the full dump, Drive, and a later Flet import.
2. **Export:** "Export recipe" on each conversation (one `.json`), "Export all recipes" in Settings (one file).
   **Import** in Settings: merges by conversation id, newest `updated` wins, shows "Added 3, updated 1".
3. **Save to Google Drive**, copied from AllAboard (`src/lib/googleDrive.ts`, `src/lib/googleConfig.ts`, and its
   `PLANS_GOOGLE_DRIVE.md`): Google Identity Services token client, **`drive.file` scope only** (AllAboard's
   AGENTS rule 6: no sensitive scopes), token in memory, Google scripts loaded on click. ChefBot creates a
   `ChefBot recipes` folder and writes one file per conversation (`<title>.chefbot.json`), updating it when the
   conversation changes. With `drive.file`, ChefBot sees only the files it made, on any device, so "Restore from
   Drive" on a new phone lists that folder with no file picker. Offer a "Back up to Drive automatically" switch,
   off by default. **Use AllAboard's OAuth client** (same client id as `src/lib/googleConfig.ts`; decided with
   Bryan). Its authorized JavaScript origins must include exactly `https://bpmdata.github.io` (origins take no
   path or `/*`) and `http://localhost:5173` for dev; ask Bryan to confirm both are listed before testing.
4. **Plain warning** in Settings, and once after the third saved recipe if no backup exists: "Recipes are saved
   in this browser only. Clearing site data deletes them. Export them or back them up to Google Drive."
5. Tests: export then import gives back the same conversations and pictures; merge rules; a Playwright run that
   clears site data, imports the dump, and sees every recipe again. Mock Drive in tests.

### Phase 5: deploy (ask Bryan before each billable step)

- Same Google Cloud project and region as AllAboard (named in its `docs/DEPLOYMENT.md`). Service
  `chefbot-api`, Dockerfile-based, `--max-instances 1 --min-instances 0 --allow-unauthenticated`.
- **CPU throttling gotcha:** with request-based billing, Cloud Run throttles the CPU when no request is open,
  so a job whose browser disconnected may stall. Test it (start a recipe, close the tab, reopen 60 s later). If
  it stalls, deploy with `--no-cpu-throttling` (instances still scale to zero when idle) and say so in the PR.
- Bryan creates a **new** OpenRouter key with a hard credit limit and stores it in Secret Manager himself;
  reference it with `--set-secrets`. Never see, print or commit it. Bucket for `usage.json` only.
- Deploy workflows, modelled on AllAboard's `deploy.yml` but **`workflow_dispatch` only for now** (not on every
  push to `main`): `deploy-api.yml` (Cloud Run; Bryan adds the deployer credential as a repo secret) and
  `pages.yml` (build `web/` with `VITE_API_URL`, publish to Pages). Bryan switches Pages on in repo settings.
- Ask Bryan for the global daily cap and the key's credit limit before the link goes on his hub page: the hub
  makes it public.
- Hub link: a separate PR in `BPMData/bpmdata.github.io`, matching how AllAboard is listed there.

## Finishing

- PR into `main` (never merge), GitHub Actions tests passing, with: what was built, where you stopped, review-step
  timing, globe frame rate, proposed limits, CPU-throttling result.
- Update `HANDOFF.md` (Pinned list, architecture section for `server/` and `web/`, how to deploy) and
  `HANDOFF.local.md` (service, bucket, secret names, URLs). Commit messages end with a `Co-Authored-By` line naming
  the model that wrote them.

## Local API contract

From the repo root, install `server/requirements.txt` and run `uvicorn server.app:app --port 8000`.
`/healthz`, cuisines, and PDF work without OpenRouter credentials. Real model calls require
`OPENROUTER_API_KEY` in the server environment. The tests inject a mock transport.

- Send `X-Visitor-ID` on job, picture, photo, and PDF calls. Use a stable random UUID generated in the
  browser. The job's id and the originating visitor id are both needed to replay it.
- The cuisine response has an ordered `roots` array, a `nodes` object keyed by id, and the form options.
- For a new job, `ingredients` is the opening text. For a follow-up it is the new user message, and
  `history` contains prior raw user and assistant messages in complete pairs, starting with the
  original ingredients. Resend the original form options, including `must_not` and any `restrictions`.
- Read SSE with a streaming fetch so the visitor header can be sent. Every connection replays all events,
  so replace the progress display with each snapshot. Recipes are reviewed before the final `result`.
  Set `CHEFBOT_STREAM_DRAFT=1` on the API to display a provisional draft before checking. In that mode
  append each `draft.delta` to a fresh buffer on every connection and use only the final result for saving.
- The browser can supply a UUID v4 as `job_id` on `POST /api/jobs` and stores it before sending. The browser commits the visitor ID to IndexedDB before its first API request and migrates
  the original localStorage ID when present. Reopen or reconnect with `GET /api/jobs/<id>/events` under the same visitor ID. `POST /api/jobs/<id>/stop` cancels an
  active job and emits `stopped`. The previous request and saved reply remain available in the browser.
- Send the ingredient photo as raw JPEG, PNG, or WebP bytes. `POST /api/picture` takes `{title}` and
  returns image bytes. The original `/api/jobs/<id>/picture` endpoint continues to serve existing web clients.
  PDF accepts JSON with `title`, `markdown`, and an optional base64 `photo` without a data URL prefix.
- `CHEFBOT_USAGE_BUCKET` enables single-worker usage persistence with the Cloud Run runtime identity.
  The bucket only gets `usage.json`. Without it, local quotas are in memory. Build from the repository
  root with `docker build -f server/Dockerfile .` to include the CJK PDF fonts.

Run the browser app with `npm ci && npm run dev` from `web/` and open
`http://localhost:5173/ChefBot/`. The API defaults to `http://localhost:8000` for dev.
Run `npm test` from `web/` with the server dependencies installed in the root `.venv`. Playwright
starts a separate mocked API on port 8911 and Vite on port 5183. Your regular dev preview can keep running. To use another
Python or Chromium executable, set `CHEFBOT_TEST_PYTHON` or `PLAYWRIGHT_CHROMIUM_EXECUTABLE`.

## Deployment setup

Use the Google Cloud project and region from AllAboard's deployment guide. After Bryan approves the billable
steps, set up a usage bucket in that project and grant the ChefBot runtime service account
`roles/storage.objectUser` on that bucket. Give the same runtime identity access to the OpenRouter secret.
Bryan creates the separate, capped key and adds it to Secret Manager.

| GitHub Actions setting | Value |
|---|---|
| Secret `GCP_SA_KEY` | Credentials for the Cloud Run deployer |
| Variable `CHEFBOT_GCP_PROJECT` | AllAboard's Google Cloud project ID |
| Variable `CHEFBOT_GCP_REGION` | AllAboard's Cloud Run region |
| Variable `CHEFBOT_RUNTIME_SA` | ChefBot runtime service account email |
| Variable `CHEFBOT_USAGE_BUCKET` | Bare bucket name |
| Variable `CHEFBOT_OPENROUTER_SECRET` | Secret Manager name for the capped key |
| Optional variable `CHEFBOT_STREAM_DRAFT` | Set to `1` to show drafts during the review |
| Variable `CHEFBOT_API_URL` | Cloud Run HTTPS origin, available after the first API deploy |

After review and merge, dispatch **Deploy ChefBot API** from `main` and verify `/healthz`. Select **GitHub Actions**
as the Pages publishing source in repo settings, add the API origin to the repo variables, and dispatch
**Deploy ChefBot to Pages** from `main`. Open the Pages URL on a phone over mobile data and make a recipe.
Close the tab while it is drafting, reopen it after 60 seconds, and inspect the reply and server logs. If processing
stalled during the disconnect, get approval for instance-based billing and rerun the API workflow with
`cpu_always_allocated` enabled. The minimum instance count remains zero in either mode.
