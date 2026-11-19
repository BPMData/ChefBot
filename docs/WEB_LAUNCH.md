# Run order: put ChefBot online, linked from bpmdata.github.io (for Codex)

This is the order of work for one long session. **`docs/WEB_DEMO.md` is the spec** (what demo mode does, the
limits, the tests, the Cloud Run settings); this file says what to do first, what's new since that brief, and
where to stop. Where the two differ, this file wins.

Before anything: read `CLAUDE.md` (the ground rules apply to you too, not only to Claude), `HANDOFF.md`,
`HANDOFF.local.md` if present, then `docs/WEB_DEMO.md` in full.

## The shape of it

```
bpmdata.github.io/chefbot/     static landing page (GitHub Pages, repo BPMData/bpmdata.github.io)
        |  "Open ChefBot" button (new tab), plus a background ping that wakes the server
        v
Cloud Run service "chefbot"    Flet server web mode, CHEFBOT_DEMO=1, max 1 instance, min 0
        |  OPENROUTER_API_KEY from Secret Manager; /data = Cloud Storage bucket
        v
OpenRouter
```

Why not serve the app itself from GitHub Pages: Pages is static files only. The only static form of a Flet app is
`flet build web` (Pyodide in the browser), and then the OpenRouter key would be in the browser. Making that work
would mean a key-holding proxy (a Cloudflare Worker could do it) **and** rewriting `api.py`'s httpx streaming for
the browser, dropping `flet-camera`, and a 20+ MB first load. Not today; see "Later" at the bottom.

## Stop points

Each phase ends with a commit on the branch, so a session that runs out partway still leaves usable work.
Open the PR after phase 1 and keep pushing to it.

| Phase | Needs Bryan? | Done when |
|---|---|---|
| 1. Demo mode in the app | No | `WEB_DEMO.md` tests pass; demo off = no behaviour change |
| 2. Container, run locally | No | Docker image serves the app; two browser profiles see separate recipes |
| 3. Deploy to Cloud Run | **Yes** (approval, secret) | Cold-start URL works from a phone |
| 4. Landing page on bpmdata.github.io | Yes (approve the PR there) | `/chefbot/` opens and wakes the service |
| 5. Featured recipes | Yes (picks and approves each) | Optional today |

## Phase 1: demo mode (no cloud, no key, start here)

Build `WEB_DEMO.md` sections 1, 2, 3, 5 and 6 behind `CHEFBOT_DEMO=1`. Suggested order, smallest risk first:

1. `src/chefbot/demo.py`: `enabled()`, the limit numbers in one dict, and the in-memory counters with one lock,
   written through to `<data>/usage.json` after every change and read back on start.
2. Per-visitor history (`history.py` takes a root folder instead of a global; `main.py` waits for the visitor id
   before creating `History`; never a shared fallback). Write the `prune_photos` isolation test before touching it.
3. Lock settings: ignore stored key/model/thinking/dev mode/relay; hide those controls.
4. Limits wired into `reply()`, the picture call, the photo-reading call, and `send_text` (message length).
   Plain-language messages when hit; no cost talk.
5. "Source code" link (AGPL) and a one-line note that demo recipes are deleted after 30 days untouched.
6. Globe: idle spin off in demo mode. Leave the drag test for phase 3 (it needs real network latency).

Run `.venv/bin/python -m pytest` after each step. Commit, push, open the PR into `main` (never merge).

## Phase 2: container

`Dockerfile` + `.dockerignore` exactly as `WEB_DEMO.md` "How it runs" describes (pin `flet-web==1.0.5`, no
Android deps, bake in the CJK fonts, `FLET_SERVER_IP=0.0.0.0`, `FLET_SERVER_PORT=$PORT`,
`FLET_APP_STORAGE_DATA=/data/chefbot`). Run it with a local folder mounted at `/data` and Bryan's dev key passed
in the environment (never printed). Check at 375x812 and desktop, two profiles: separate recipes, a limit
triggers, photo upload and Save PDF download work. Add `tools/deploy.sh` with the `gcloud` commands, not yet run.

## Phase 3: deploy (ask Bryan first)

Same Google Cloud project and region as AllAboard (look at AllAboard's setup, change nothing there).
Ask before each billable thing:

1. Bryan makes a **new** OpenRouter key with a hard credit limit and puts it in Secret Manager himself. You only
   reference the secret name.
2. Bucket for `/data`, with a lifecycle rule deleting objects older than 30 days under `visitors/`.
   (Lifecycle rules go by object age, not "folder untouched"; every save rewrites the conversation file, so an
   active visitor's recent files stay. Note this in HANDOFF.)
3. `gcloud run deploy` with: `--max-instances 1 --min-instances 0 --timeout 3600 --session-affinity
   --cpu 1 --memory 1Gi --set-secrets OPENROUTER_API_KEY=<secret>:latest`, the volume mount, `CHEFBOT_DEMO=1`,
   `--allow-unauthenticated`.
4. Test from a cold start (record the time), on a phone on mobile data: make a recipe, drag the globe, open in a
   second browser and confirm it can't see the first one's recipe. If the globe drags badly, default demo mode to
   the flat map and say so in the PR.

The URL goes in `HANDOFF.local.md`. It will also be public once phase 4 links it, which is fine (see below).

## Phase 4: landing page on bpmdata.github.io

A separate repo (`BPMData/bpmdata.github.io`): its own branch and its own PR; never push to its main branch.
Match that site's existing style; read its structure before adding anything.

- `chefbot/index.html`: one screen. What ChefBot is in two sentences, one or two screenshots (take them in
  phase 3 from the live demo, dark theme), an **"Open ChefBot"** button to the Cloud Run URL in a new tab, a note
  that the first open after a quiet spell takes a few seconds, and links to the GitHub repo and the Android APK
  release if one exists. No emojis. Fraunces + DM Sans to match the app.
- **Wake the server early:** on page load, `fetch(CLOUD_RUN_URL, {mode: "no-cors"})` once, so the cold start
  happens while the visitor reads. Nothing else in the page talks to the service.
- **Link, don't iframe.** Inside an iframe on another site, the browser treats ChefBot's storage as third-party:
  Safari partitions and expires it, which would mint new visitor ids and lose people's saved recipes. A new tab
  avoids that.
- Add a card or link to ChefBot from the hub's front page, the same way the other projects are listed.

## Decision for Bryan before phase 4

`WEB_DEMO.md` assumed a private link, not advertised. Linking it from the hub homepage makes it public. That's
fine **if** the global daily cap and the OpenRouter credit limit are set low enough that a crawler or a shared
link can only burn a day's cap. Codex: ask Bryan for the global daily reply cap and the credit limit he wants
before publishing the link, and put both in the PR description.

## Cloudflare (optional, only if it saves effort)

Not needed for any phase above. Two places it could help, if Bryan's Cloudflare account already has a domain:

- **A nicer URL:** a Worker on `chefbot.<his domain>` that proxies HTTP and WebSocket traffic to the Cloud Run
  URL (Workers pass WebSocket upgrades through `fetch`). Test that the Flet WebSocket and session reconnect still
  work through it before switching the landing page's link.
- **An edge kill switch:** the Worker can return a "resting" page without waking Cloud Run when a flag in
  Workers KV is set. The in-app global cap already covers this, so it's a nice-to-have.

Don't move the app itself to Workers: Python Workers can't run a Flet server.

## Finishing

- PR into `main` with what was built, the tests, the cold-start time, the globe finding, the proposed limits.
  Check the GitHub Actions tests pass. Don't merge.
- Update `HANDOFF.md` (Pinned list: web demo built/deployed, how to redeploy) and `HANDOFF.local.md` (project,
  region, service, bucket, secret names, URL).
- Commit messages end with a `Co-Authored-By` line naming the model that wrote them.

## Later (not this session)

Static `flet build web` on Pages with a Cloudflare Worker holding the key and enforcing limits. Upside: no server
to run, no WebSocket, the globe runs locally, recipes live in the browser with no bucket. Cost: `api.py` needs a
browser-side streaming path, the camera and keep-alive extensions must be skipped, and the first load is slow.
Worth a spike only once the Cloud Run demo is live.
