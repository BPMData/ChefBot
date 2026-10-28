# ChefBot handoff (as of 2026-10-28)

Everything a new session needs to keep going without the original conversation. Read this first, then
`README.md` (features, how models were chosen) and `docs/EMAIL.md` (mail relay setup).

## What this is

ChefBot is Bryan's 2026 rewrite of **RecipeGPT** (`~/Documents/Github/RecipeGPT`), a Streamlit app he wrote 100%
by hand in 2023–24. **RecipeGPT is a time capsule: never modify it.** ChefBot is a personal demo piece he'll use
himself (and maybe 1–2 others), so quality matters more than cost.

- One Python codebase on [Flet](https://flet.dev) **1.0.5** (Flutter UI): desktop, web, Android (sideloaded APK).
- Models via **OpenRouter**. The key lives in `~/Documents/Github/openrouter.txt` (outside every repo; never
  commit it, never type it into a UI field; pass it as `OPENROUTER_API_KEY` for dev runs).
- Local git only, on `main`, 3 commits. **Not pushed to GitHub yet.**

## Pinned (do these next, in this order)

1. **Mail relay: deployed (2026-10-28)** as Bryan's Apps Script web app under overboard.reporting@gmail.com
   (`tools/mail-relay.gs`, setup in `docs/EMAIL.md`). The URL and secret are saved in the desktop prefs
   (`flutter.chefbot.relay_url` / `relay_secret`; check whether they're set, never print them). The `/exec` URL
   answers the hello check, and a test email (Galbijjim + photo + PDF) went through the relay to that inbox.
   **Still to confirm:** Bryan's look in Gmail at the inline image, the PDF attachment and the Korean name. Direct
   SMTP with an app password still fails (`SMTPServerDisconnected` during sign-in); the relay is the way.
2. **Android APK never built.** See "Android" below. Ask before starting: it downloads several GB.
3. **Push to GitHub** (BPMData/ChefBot) once he's happy. Ask public vs private. Add screenshots to the README.

## Run, test, verify

```bash
cd ~/Documents/Github/ChefBot
.venv/bin/flet run src/main.py                       # desktop window (Bryan's normal way)
OPENROUTER_API_KEY="$(tr -d '[:space:]' < ../openrouter.txt)" \
  .venv/bin/flet run --web --port 8551 src/main.py   # web: what Claude uses with the browser pane
.venv/bin/python -m pytest                           # 25 offline tests
OPENROUTER_API_KEY=... .venv/bin/python tools/smoke.py   # live: recipe + follow-up edit (~1¢)
```

- The venv is Python 3.14 (`.venv`, plain pip; no uv on this Mac). Deps: flet[all]==1.0.5, httpx, markdown,
  fpdf2, pytest, pypdf.
- **Web dev mode quirks:** first page load takes ~20 s; Flutter draws on a canvas, so `find`/`read_page` see
  nothing: use screenshots and coordinates. After code changes, **restart the server** (hot reload leaves broken
  sessions). Use absolute paths in background shell commands (the shell's cwd drifts).
- **Dev storage:** `flet run` keeps recipes/photos in `src/.flet/storage/data/` (gitignored). On a phone it's
  `FLET_APP_STORAGE_DATA`; fallback `~/.chefbot`. Desktop settings (incl. secrets) are in the macOS defaults domain
  `com.appveyor.flet`; read single keys with `defaults read com.appveyor.flet flutter.chefbot.<key>`, never dump
  the whole domain (it holds the OpenRouter key and passwords).
- **Saved recipes that are Bryan's:** "Lazy Golden Chicken Stew", "Crispy Whole Fish with Papaya
  Sweet-and-Sour Glaze". Don't modify or add photos to them. Claude's test data: "Galbijjim (갈비찜)…",
  "Buta to Hakusai no Nimono Domburi, Bunka-era Style…" (the Kansai one). The recent list is ordered by last
  update, so positions change; check the title before clicking.
- Don't click Save PDF / Save HTML / Share in the browser pane (they download files onto the Mac). The export code
  is covered by `tests/test_export.py`.

## Architecture

```
src/main.py              UI: home form, recipe conversation, settings, per-reply actions, email dialog
src/chefbot/prompts.py   audiences, cuisines (+ classic seasonings), dietary rules, prompt text (ported from
                         RecipeGPT's personas.py; keep his voice)
src/chefbot/api.py       OpenRouter: streaming chat, photo -> ingredients, dish picture
src/chefbot/history.py   conversations + photos saved as JSON/PNGs; prune_photos()
src/chefbot/export.py    Markdown -> HTML page / PDF / email; SMTP + relay sending
src/chefbot/recipe.py    extract_title() (last "Recipe Title:" line wins)
tools/mail-relay.gs      Apps Script relay (secret + 40/day cap)
tools/make_static_fonts.py   cuts static PDF fonts from variable ones (already done; output committed)
tools/smoke.py           live API check
```

- **Memory:** a conversation is `system` + `user`/`assistant` turns; the system prompt tells the model to rewrite
  the complete recipe on change requests and keep a `Recipe Title:` line. User messages can carry a `display`
  field (the friendly summary shown instead of the raw prompt). Photos are stored per assistant-message index in
  `conv.photos` and never sent to the model.
- **Editing:** only the latest user follow-up (index ≥ 2) gets Edit/Delete. Edit is non-destructive until send
  (`editing_index`); Delete truncates from that index with Undo. Title recomputed via `_latest_title()`.

## Model decisions (and why)

Full table in `README.md`. Blind tests (judge: Claude Sonnet 5.5, a non-contestant) on random requests:

- Default **GLM 5.3 (`z-ai/glm-5.3`), thinking `high`**, `max_tokens` 32000, provider order `["z-ai"]` with
  fallbacks allowed. Bryan asked for medium/high thinking and wants the best result; above the cheapest settings
  the models were a statistical tie, so model + thinking are user settings (GLM 5.3 Flash, Kimi K3.1 Pro).
- **Thinking can't be disabled** on these models ("Reasoning is mandatory"), and Z.ai's own servers think a lot by
  default: a small token cap gives blank or truncated replies. Always send `reasoning.effort` explicitly.
- Photos: `z-ai/glm-5.3-flash` (full GLM 5.3 is text-only). Dish pictures: `google/gemini-3.1-flash-lite-image`
  (~3.4¢) with Bryan's original "modernist cookbook cover" prompt; he loved the result.
- Bryan prefers Chinese labs (Z.ai, Moonshot, DeepSeek) and wanted money to reach Z.ai, hence the provider pin.
  Kimi K2.6 failed a gluten-free test; the Sep build of DeepSeek V4.1 Flash is weaker than the Oct one.
- Free OpenRouter models were rejected: slow, rate-limited, and one gave wrong allergen advice.

## Bryan's preferences (UI and process)

- **No emojis anywhere** (UI or model output). Material icons, custom SVG, or plain text instead. The system
  prompt says "no emojis"; older saved recipes still contain a few.
- **Dark theme by default** (Light/System in Settings). Fonts: Fraunces (headings) + DM Sans (body), bundled.
  Content in a centered column (max 780 px) on desktop; it looked bad stretched full width.
- No cost talk in the UI ("costs about a cent" was removed: cost is his problem).
- "The 1817 version" quick tweak stays **BETA** with a strong hallucination warning; no year picker.
- Every reply has Copy (Markdown), PDF, HTML, Email, Share, Picture. Copy/actions act on that reply only.
- Plain-language explanations; he's technical but values brevity. He tests thoroughly and reports precisely.

## Android: plan and known facts

```bash
cd ~/Documents/Github/ChefBot
.venv/bin/flet build apk          # first run installs Flutter (its own copy) and asks to install JDK + Android SDK
# output: build/apk/*.apk  (consider --split-per-abi for a smaller arm64 APK)
.venv/bin/flet debug android      # run on a USB-connected phone (developer mode + USB debugging); `--show-devices`
```

- Config is in `pyproject.toml`: `[tool.flet]` org `io.github.bpmdata`, product `ChefBot`, `[tool.flet.app] path =
  "src"`. Android INTERNET permission is added by default.
- **App icon:** add `src/assets/icon.png` (1024×1024 PNG; SVG is ignored by the build). Render it from
  `src/assets/logo.svg` (the chef's-hat-on-orange-gradient logo). Optionally `--android-adaptive-icon-background`
  and a splash color (`--splash-color`, dark `#110E0C`).
- **Risks to check on a real phone:**
  - `fpdf2` needs **Pillow** and **fontTools** (Pillow has native code; Flet ships Android wheels for common
    packages, but verify the build picks it up). `markdown`, `httpx`, `defusedxml` are pure Python. We deliberately
    avoided the `openai` package (pydantic-core is native).
  - "Snap my fridge" uses `FilePicker.pick_files(file_type=IMAGE, with_data=True)`: on Android that opens the photo
    picker, maybe not the camera directly. If camera capture is wanted, check Flet 1.0's options (`--permissions
    camera`, a camera control) before building something custom. Never tested with a real fridge photo.
  - `Share.share_files` with the PDF + photo should open the Android share sheet (untested anywhere real).
  - `FilePicker.save_file(src_bytes=..., file_name=...)` is required on mobile/web (already done).
  - CJK fonts for PDFs download at first use (10–18 MB) into `<data>/fonts`; check that works on mobile data.
  - First launch needs the OpenRouter key typed in Settings (no env var on a phone). SharedPreferences on Android
    is plain app-private storage, acceptable for a personal sideload.
- Sideload: copy the APK to the phone, allow "install unknown apps" for the file manager, install.

## Flet 1.0 gotchas learned the hard way

- Services (`SharedPreferences`, `Clipboard`, `Share`, `FilePicker`, `UrlLauncher`) auto-register when constructed
  inside the page context; most methods are `async`.
- `page.run_task` **swallows exceptions** silently: use `ChefBotApp._run()`, which reports them.
- A `Chip` with no `on_select`/`on_click` renders disabled.
- `Dropdown` uses `on_select`. `TextField.border_radius/border_color` are deprecated: use
  `border=ft.OutlineInputBorder(...)` (see `soft_border()`).
- `SharedPreferences.get` can time out (10 s) on a slow first web load: prefs load in parallel with retries, the
  UI draws first, and `_need_key()` says "still starting up" until prefs arrive.
- Fonts fetched from GitHub at runtime fail in the browser (CORS): fonts are bundled in `src/assets/fonts`.
- **Scrolling the conversation (Flet 1.0.5, tested 2026-10-28):** `scroll_to(scroll_key=...)` does nothing, and
  toggling `auto_scroll` resets the list to the top. So the thread keeps `auto_scroll=True` (its pinning pauses
  while you're scrolled away from the end) and scrolls to measured pixel offsets: every message reports its height
  via `on_size_change` (`_add_to_thread`, `_offset_of`, `_scroll_to_end`). A new dish picture scrolls to the top of
  its reply; "Jump to the bottom" shows when far from the end; a new reply scrolls to the end first.
- Stopping a test server: `pkill -f "flet run ..."` leaves the child app process holding the port, so the next
  server fails to start (check its log) and the browser keeps showing old code. Kill whatever listens on the port
  (`lsof -ti tcp:8551 -sTCP:LISTEN`). A hidden Browser pane also skips animations; show it before scroll tests.
- **`flet run` hot-reloads whenever a source file changes, including Claude's edits while Bryan has the app open.**
  The reloaded session's `SharedPreferences` never answers (10 s timeouts), so settings can't be read or saved.
  This happened 2026-10-28. The app now treats an unreadable load as an error (it no longer opens a blank
  first-run Settings that would save over his real settings) and shows Save failures in the dialog. Before editing
  code, check whether his app is running (`ps ax | grep ChefBot/src/main.py`) and tell him to restart it afterwards.

## PDF gotchas (fpdf2 2.8.9)

- Use **static** font cuts (`src/assets/fonts/static`); variable fonts made exports take 16–48 s.
- Each cut needs a **unique internal name** (`static_instance()` rewrites the name table), or regular/bold collide.
- **Don't use `set_fallback_fonts`**: it scrambled long mixed-script paragraphs. `assign_fonts()` wraps every run the
  base font can't draw in an explicit `<font face>` instead; uncovered characters (emoji) are dropped.
- Models put lists right under a bold label with no blank line; `normalize_markdown()` fixes that before conversion.
- Exports drop the `Recipe Title:` line (the title is the heading).

## Backlog (nice to have)

- "Try again" on a reply; deleting a single older message.
- Auto-generate the dish picture after the first recipe (setting).
- README screenshots; a GitHub description.
- Old test conversations show raw `**Ingredients:**` in the first bubble (pre-redesign data); harmless.

OpenRouter spend during development: roughly $2 (model bake-offs, judges, pictures, live tests).
