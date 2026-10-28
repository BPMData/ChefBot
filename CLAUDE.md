# ChefBot: notes for Claude

ChefBot is Bryan's 2026 rewrite of his hand-written 2023 app RecipeGPT: a Flet (Python) recipe app with
conversation memory, for desktop, web and a sideloaded Android APK. **Read `HANDOFF.md` at the start of a session**:
it has the current state, what's pinned, the decisions and why, and the gotchas already hit. Private details
(secrets' locations, accounts, Bryan's phone, which saved recipes are his) are in the gitignored
`HANDOFF.local.md`; read it too when it exists, and never copy its contents into tracked files. `README.md` covers
features; `docs/EMAIL.md` covers the mail relay.

## Ground rules

- **Never modify `~/Documents/Github/RecipeGPT`.** It's kept exactly as Bryan left it.
- **The OpenRouter key** lives in a file outside the repo (see `HANDOFF.local.md`). Never commit it, print it,
  or type it into a UI field; pass it as `OPENROUTER_API_KEY` for dev runs. Same for any email secrets.
- **Don't modify Bryan's saved recipes** (see `HANDOFF.local.md` for which are his vs. test data).
- **The repo is public.** Keep personal details (email addresses, devices, file locations) out of tracked files.
- Ask before anything that downloads gigabytes (the Android toolchain), pushes to GitHub, or sends email.

## Bryan's preferences

- No emojis anywhere, in the UI or the model's output. Use Material icons, custom SVG, or plain text.
- Dark theme by default, Fraunces + DM Sans, content in a centered column on desktop.
- Quality over cost; no cost talk in the app. He prefers Chinese labs (Z.ai, Moonshot, DeepSeek).
- Plain-language explanations; commit messages end with the Co-Authored-By line.

## Working on it

- Tests: `.venv/bin/python -m pytest`. Run: `.venv/bin/flet run src/main.py` (desktop) or
  `--web --port 8551` for the browser pane. Restart the server after code changes.
- Keep `HANDOFF.md` (and `HANDOFF.local.md`) current: update its "Pinned" list and anything that changed at the end of a working session.
