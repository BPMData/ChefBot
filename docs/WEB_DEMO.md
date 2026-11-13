# Brief: put ChefBot on the web (Google Cloud Run)

You are working in the ChefBot repo at `/Users/murphb/Documents/Github/ChefBot`. Read `CLAUDE.md`, `HANDOFF.md`
and the gitignored `HANDOFF.local.md` (if present) first: they hold the ground rules (the repo is public, never
commit, print or type secrets, no emojis anywhere, work on a branch and open a pull request into `main`, never
merge it yourself). `HANDOFF.md` pinned item 3 has the original web-demo plan; this brief replaces it where they
differ.

## What this is for

A private tech demo. Bryan gives the link directly to people he chooses; it is not advertised. It runs on Bryan's
own OpenRouter key with strict usage limits. A few seconds of extra wait on the first visit after a quiet spell
is fine, so **the service scales to zero (minimum instances 0)**; don't keep an instance warm.

## How it runs

ChefBot is Python on Flet 1.0.5. Run it in **Flet's server web mode**: the Python runs on the server and the
browser gets Flet's web client over a WebSocket, so the OpenRouter key never reaches the browser. Do not use
`flet build web` (a static build would put the key in the browser, where anyone can copy it).

Host it on **Google Cloud Run** in the same Google Cloud project and region as Bryan's AllAboard app
(`~/Documents/Github/AllAboard`, which uses a Cloud Storage volume through `DATA_DIR`; look at its setup, don't
change it). Ask Bryan which project and region if it isn't clear.

- A `Dockerfile` (and `.dockerignore`: leave out `.venv`, `build`, `assets/maps/source`, tests, `.git`) that
  installs the app's own dependencies from `pyproject.toml`, plus whatever Flet needs to serve web mode (the
  `flet-web` package, pinned to 1.0.5 like `flet`). Install `flet-web` in the image: if it is missing, Flet tries
  to `pip install` it at start-up, which is slow and fragile on a cold start. Never install the Android-only
  dependencies.
- The server listens on `0.0.0.0` and the port in `$PORT`. Flet 1.0.5 already forces server web mode on Linux
  and reads `FLET_SERVER_IP` and `FLET_SERVER_PORT` from the environment (`flet/app.py`), so the container
  probably needs only `FLET_SERVER_IP=0.0.0.0` and `FLET_SERVER_PORT=$PORT` and no change to `ft.run(main)` at the
  end of `src/main.py`; confirm that locally in the container before changing code. Keep desktop and Android
  behaviour unchanged.
- Set `FLET_APP_STORAGE_DATA` to the mounted folder (for example `/data/chefbot`): `history.data_dir()` already
  uses it, so nothing else needs to learn where the volume is.
- The CJK PDF fonts (10 to 18 MB each) are downloaded from GitHub the first time a PDF needs them and cached
  under the data folder. Bake them into the image (or cache them under `/tmp`, shared by all visitors) so the first
  Korean, Japanese or Chinese PDF isn't slow and doesn't write to the bucket.
- Cloud Run settings, and why:
  - **Maximum instances 1:** each visitor's app lives in server memory while their tab is open, so every request
    must reach the same instance. With one instance, session affinity is redundant but harmless; leave it on.
    One instance also means usage counters can be guarded by a single in-process lock (see "Usage limits").
  - **Minimum instances 0**, request-based billing.
  - **Request timeout 3600 s** (the most Cloud Run allows), since a WebSocket counts as one long request, so it
    is cut after an hour. Flet keeps a disconnected session in memory for 3600 s by default
    (`DEFAULT_FLET_SESSION_TIMEOUT` in `flet_web`) and lets the browser reconnect to it; a reply that was
    streaming when the tab closed keeps going and still counts toward the limits. Test the reconnect, and test
    that a visitor who returns after the session expired starts clean without losing saved recipes.
  - About 1 vCPU and 1 GiB memory to start; adjust after testing. Python does all the work for every connected
    visitor (see "The map globe" below), so watch CPU, not only memory.
- **The key:** Bryan creates the OpenRouter key (with a hard credit limit set at openrouter.ai) and stores it in
  Secret Manager himself. The service reads it as the `OPENROUTER_API_KEY` environment variable through
  `--set-secrets`. Never see, print, log or commit the key; just reference the secret by name.
- **A storage volume:** mount a Cloud Storage bucket at `/data` (as AllAboard does) for saved recipes and usage
  counters, so they survive restarts and scale-to-zero.
- A deploy script or a short section in `README.md` with the exact `gcloud` commands, so Bryan can redeploy.

Ask Bryan before creating anything billable (buckets, services, secrets) and before the first deploy.

## Changes to the app (only in web demo mode)

Turn these on with an environment variable such as `CHEFBOT_DEMO=1`, set only on the Cloud Run service. With it
unset, the app must behave exactly as it does today on desktop and Android.

1. **Saved recipes are per visitor.** Today `src/chefbot/history.py` keeps every conversation (and its dish
   pictures) in one folder, so on a server every visitor would see everyone's recipes. In demo mode, give each
   browser a random visitor id kept in the browser (`ft.SharedPreferences`, which is the browser's local storage
   in web mode; settings already live there) and keep that visitor's history under `/data/visitors/<id>/`.
   Several visitors can be connected at once, so each session needs its own history folder, never a shared global.
   - **The visitor id must be known before history is touched.** `ChefBotApp.__init__` creates `History()`
     before settings load (`src/main.py`), and loading settings can time out on a slow first visit (see
     HANDOFF, `_load_prefs`). If the id isn't available, wait and show "still starting up"; never fall back to
     the shared folder, and never mint a fresh id that orphans the visitor's saved recipes.
   - **`prune_photos` is dangerous on a shared folder:** it deletes every photo not referenced by the current
     session (`src/main.py`, the call near `self.history.prune_photos(keep=...)`). It must only ever see one
     visitor's folder. Test that one visitor's activity leaves another's photos alone.
   - **Cleaning up:** dish pictures (about 1 MP each) and recipes from strangers pile up on the bucket. Add a
     Cloud Storage lifecycle rule (or a clean-up on start) that deletes visitor folders untouched for, say, 30
     days, and say so in the demo's footer or Settings.
2. **Usage limits**, enforced on the server and stored on the volume:
   - **Count model calls, not just recipes.** Every follow-up edit is another full model call with the whole
     conversation and high thinking (up to 32,000 tokens, `api.MAX_TOKENS`). Limit total replies per visitor per
     day, and also set: a cap on follow-ups per recipe, a maximum length for a typed message (`send_text` has
     none today), and a maximum size for an ingredient photo.
   - Per visitor: a few new recipes a day and a short cooldown between replies; pictures and ingredient-photo
     reading are the expensive calls, so allow fewer of them.
   - A global daily cap across all visitors, so a leaked link can't drain the key; past it, the app says the
     demo is resting for the day. **This and OpenRouter's own credit limit are the real protection:** a visitor
     id lives in the browser, so clearing site data mints a new one and resets the per-visitor limits. Treat the
     per-visitor limits as friendly, not secure.
   - Counters live on the Cloud Storage volume, where renames are not atomic and writes are slow. With one
     instance, keep the counters in memory behind one lock, write them through to the volume after each change,
     and read them back on start. Don't rely on file renames for correctness.
   - When a limit is hit, say so plainly in the UI, with no cost talk.
   - Put the numbers in one place so Bryan can change them; propose defaults in the pull request.
3. **Hide and lock what doesn't belong in a shared demo:**
   - The OpenRouter key field, the hidden developer mode (tapping the Settings title 7 times) and the email
     relay. Email stays as the `mailto:` link it already is on desktop; check that a long recipe in a `mailto:`
     link works in phone browsers, and shorten it if not.
   - **Ignore what the browser has stored.** `ChefBotApp.start` reads the key, model, thinking level, email and
     relay settings from the browser's storage, and a stored key wins over `OPENROUTER_API_KEY`. In demo mode
     use only the server's key, and lock the model and thinking level to the server's choice: hide those two
     dropdowns and ignore any stored values.
4. **Check browser features:** ingredient-photo upload, Save PDF, Save HTML and saving pictures must work in a
   browser on a phone and on desktop. The code already handles web: `_save` uses `FilePicker.save_file` with the
   bytes (Flet's browser download), and `pick_photo` uses `pick_files(with_data=True)`, which returns the bytes
   in web mode. Expect them to work without Flet's upload directory or a secret key; confirm on iPhone Safari
   and Android Chrome, and fix only what fails. Share has no share sheet on most desktop browsers and falls back
   to copying the recipe, which is fine.
5. **A source link** (for example "Source code" in Settings or a footer) to `https://github.com/BPMData/ChefBot`.
   ChefBot is AGPLv3, which requires offering the source to people who use it over a network.
6. **The map globe (added after this brief was first written).** "Browse by map" has a 3D globe that Python
   redraws and spins (`GLOBE_IDLE_SPIN_DPS`, about 35 frames a second while moving, `src/main.py`). On the phone
   or desktop that is local; in server mode every frame goes from the server to the browser, and every drag
   event goes the other way, so it adds network latency and costs server CPU for each visitor who has the map
   open. In demo mode: turn the idle spin off, test the globe against the deployed service from a phone on
   mobile data, and if dragging is laggy, fall back to the flat world map or the list browser for the demo. The
   zoom animations between flat map levels run in Flutter and are not affected. Tell Bryan what you found.
7. **Featured recipes (question for Bryan, dropped from the original plan).** The 2026-11-09 plan in HANDOFF had a
   few featured recipes that open instantly and spend nothing, for visitors who only want to look or who hit a
   limit. This brief left them out without a reason. Ask Bryan whether to include them; if yes, store a few
   finished recipes as data files in the repo and open them read-only from the home screen.

## Tests

Add to `tests/` (run `.venv/bin/python -m pytest`; GitHub Actions runs them on every PR):

- With demo mode off, nothing changes (the existing tests keep passing).
- In demo mode, two visitor ids get separate histories, and neither can load the other's conversations.
- In demo mode, one visitor's `prune_photos` never deletes another visitor's photos.
- In demo mode, a stored key, model, thinking level or developer-mode flag in the browser's storage is ignored.
- In demo mode, with no visitor id yet, history stays unavailable and nothing is written to a shared folder.
- The limits: per-visitor recipe count, total replies per day, cooldown, picture limit, message and photo size
  limits, and the global cap, including after a "restart" (counters read back from disk). Mock the model; tests
  never call OpenRouter.

## Checking it

- Locally: run the Docker image with a dev key passed as `OPENROUTER_API_KEY`, open it in two browser profiles
  at phone width (375 x 812) and desktop, and confirm each sees only its own recipes, the limits trigger, and
  photo upload and Save PDF work. Also open "Browse by map" and drag the globe, and check CPU use with two or
  three profiles connected (see "The map globe").
- After Bryan approves the first deploy: open the Cloud Run URL from a cold start (note how long the first
  load takes), make a recipe, and check that a second browser doesn't see it.
- Note in the pull request what you tested, the cold-start time, and the URL (the URL can go in
  `HANDOFF.local.md`, not in tracked files, since the link is private).

## Finishing

- Update `HANDOFF.md` (what was built, how to redeploy, decisions, anything left) and `HANDOFF.local.md` (the
  project, service, bucket and secret names, and the URL).
- Work on a new branch; commit messages end with a `Co-Authored-By` line for the model that wrote them.
- Open a pull request into `main` and make sure the GitHub Actions tests pass. Do not merge it.
