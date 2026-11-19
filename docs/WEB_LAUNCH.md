# Plan: ChefBot for the web, without Flet (for Codex)

Decided with Bryan, 2026-11-19. This replaces the Flet server-mode plan in `docs/WEB_DEMO.md`; that file's
**limits, privacy and AGPL sections still apply** (sections 2, 3, 5, 7), its Flet and Cloud Run volume details don't.

Before anything: read `CLAUDE.md` (its ground rules apply to you), `HANDOFF.md`, `HANDOFF.local.md` if present,
and AllAboard's `docs/DEPLOYMENT.md` (BPMData/allaboard), which records hard-won Cloud Run rules this plan reuses.

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
   off by default. Bryan adds `https://bpmdata.github.io` as an authorized origin on the OAuth client (or makes a
   new client); ask which.
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
