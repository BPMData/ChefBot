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
  `flet-web` package). Never install the Android-only dependencies.
- The server listens on `0.0.0.0` and the port in `$PORT`. Find the right `ft.run(...)` arguments for Flet 1.0.5
  server web mode; `src/main.py` ends with `ft.run(main)`. Keep desktop and Android behaviour unchanged.
- Cloud Run settings, and why:
  - **Session affinity on, maximum instances 1:** each visitor's app lives in server memory while their tab is
    open, so every request must reach the same instance.
  - **Minimum instances 0**, request-based billing.
  - **Request timeout 3600 s** (the most Cloud Run allows), since a WebSocket counts as one long request; check
    the app reconnects cleanly if the connection drops.
  - About 1 vCPU and 1 GiB memory to start; adjust after testing.
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
2. **Usage limits**, enforced on the server and stored on the volume:
   - Per visitor: a few new recipes a day and a short cooldown between replies; pictures and ingredient-photo
     reading are the expensive calls, so allow fewer of them.
   - A global daily cap across all visitors, so a leaked link can't drain the key; past it, the app says the
     demo is resting for the day.
   - When a limit is hit, say so plainly in the UI, with no cost talk.
   - Put the numbers in one place so Bryan can change them; propose defaults in the pull request.
3. **Hide what doesn't belong in a shared demo:** the OpenRouter key field (the server's key is always used),
   the hidden developer mode (tapping the Settings title 7 times) and the email relay. Email stays as the
   `mailto:` link it already is on desktop.
4. **Check browser features:** ingredient-photo upload (`FilePicker`), Save PDF and saving pictures must work in
   a browser on a phone and on desktop. Some may need Flet's web upload or download path; fix what doesn't.
5. **A source link** (for example "Source code" in Settings or a footer) to `https://github.com/BPMData/ChefBot`.
   ChefBot is AGPLv3, which requires offering the source to people who use it over a network.

## Tests

Add to `tests/` (run `.venv/bin/python -m pytest`; GitHub Actions runs them on every PR):

- With demo mode off, nothing changes (the existing tests keep passing).
- In demo mode, two visitor ids get separate histories, and neither can load the other's conversations.
- The limits: per-visitor recipe count, cooldown, picture limit and the global cap, including after a "restart"
  (counters read back from disk). Mock the model; tests never call OpenRouter.

## Checking it

- Locally: run the Docker image with a dev key passed as `OPENROUTER_API_KEY`, open it in two browser profiles
  at phone width (375 x 812) and desktop, and confirm each sees only its own recipes, the limits trigger, and
  photo upload and Save PDF work.
- After Bryan approves the first deploy: open the Cloud Run URL from a cold start (note how long the first
  load takes), make a recipe, and check that a second browser doesn't see it.
- Note in the pull request what you tested, the cold-start time, and the URL (the URL can go in
  `HANDOFF.local.md`, not in tracked files, since the link is private).

## Finishing

- Update `HANDOFF.md` (what was built, how to redeploy, decisions, anything left) and `HANDOFF.local.md` (the
  project, service, bucket and secret names, and the URL).
- Work on a new branch; commit messages end with a `Co-Authored-By` line for the model that wrote them.
- Open a pull request into `main` and make sure the GitHub Actions tests pass. Do not merge it.
