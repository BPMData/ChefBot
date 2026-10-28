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
- On GitHub as **BPMData/ChefBot (private)** since 2026-10-28. Work goes on a branch with a PR into `main`.

## Pinned (do these next, in this order)

1. **Mail relay: deployed (2026-10-28)** as Bryan's Apps Script web app under overboard.reporting@gmail.com
   (`tools/mail-relay.gs`, setup in `docs/EMAIL.md`). The URL and secret are saved in the desktop prefs
   (`flutter.chefbot.relay_url` / `relay_secret`; check whether they're set, never print them). The `/exec` URL
   answers the hello check, and a test email (Galbijjim + photo + PDF) went through the relay to that inbox.
   **Still to confirm:** Bryan's look in Gmail at the inline image, the PDF attachment and the Korean name. Direct
   SMTP with an app password still fails (`SMTPServerDisconnected` during sign-in); the relay is the way.
   **Since 2026-10-28 the relay is a hidden developer option** (tap the "Settings" title 7 times; pref
   `chefbot.dev_mode` = "on"). Bryan's phone has the relay set (he copied the URL and secret over with
   `adb push`). Everyone else: Email on a phone opens the share sheet (subject + full plain-text recipe + PDF and
   photo attached; share_plus passes EXTRA_SUBJECT/EXTRA_TEXT/EXTRA_STREAM, so Gmail fills all three). On desktop
   it's a `mailto:` link with the whole recipe (shortened only on Windows, whose mail apps reject long links).
2. **Android APK built and installed on Bryan's Samsung (2026-10-28)** with `adb install -r` (USB debugging is on).
   He reported almost everything worked first try; only email was off (fixed: share sheet, see item 1). Re-test
   Email on the phone after installing the new build. See "Android" below for installing, rebuilding, signing,
   and deleting the ~13 GB toolchain.
3. **GitHub: done** (private repo; PR #1 with the 2026-10-28 work is merged). Still to do: README screenshots; maybe make it
   public later (ask first).

## Run, test, verify

```bash
cd ~/Documents/Github/ChefBot
.venv/bin/flet run src/main.py                       # desktop window (Bryan's normal way)
OPENROUTER_API_KEY="$(tr -d '[:space:]' < ../openrouter.txt)" \
  .venv/bin/flet run --web --port 8551 src/main.py   # web: what Claude uses with the browser pane
.venv/bin/python -m pytest                           # 29 offline tests
OPENROUTER_API_KEY=... .venv/bin/python tools/smoke.py   # live: recipe + follow-up edit (~1¢)
```

- The venv is Python 3.14 (`.venv`, plain pip; no uv on this Mac). Deps: flet[all]==1.0.5, httpx, markdown,
  fpdf2, pillow==12.3.0 (pinned for Android), pytest, pypdf.
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

## Android: build, install, clean up

First built 2026-10-28 on the MacBook (Flet 1.0.5, Flutter 3.44.8, JDK 17, Android SDK 36). It built on the first
try; the first run took about 20 minutes, mostly downloads.

```bash
cd ~/Documents/Github/ChefBot
.venv/bin/flet build apk --yes --split-per-abi \
  --splash-color "#110E0C" --splash-dark-color "#110E0C" \
  --android-adaptive-icon-background "#E8452C"
# output: build/apk/chefbot-arm64-v8a.apk (66 MB, for any modern phone),
#         chefbot-armeabi-v7a.apk (old 32-bit phones), chefbot-x86_64.apk (emulators)
.venv/bin/flet debug android      # run on a USB-connected phone (developer mode + USB debugging); `--show-devices`
```

- Config is in `pyproject.toml`: `[tool.flet]` org `io.github.bpmdata` (package `io.github.bpmdata.chefbot`),
  product `ChefBot`, `[tool.flet.app] path = "src"`. Permissions in the APK: INTERNET and ACCESS_NETWORK_STATE.
- **Pillow is pinned to 12.3.0** because Flet's Android package index has no 13.x (the Mac venv has 13.0.0; the
  pin is fine on desktop too). Its native libs (`libPIL-_imaging.so` etc.) are in the APK. If it were ever missing,
  `_add_photo()` leaves the photo out of the PDF instead of failing.
- **App icon:** `src/assets/icon.png` (1024x1024). It is the logo's hat, scaled to 92%, on a full-square version of
  the orange gradient, so the launcher's circle/squircle mask never clips the hat. Rendered from an SVG with
  macOS's own SVG support (a small Swift script; no rsvg/Inkscape on this Mac). The adaptive-icon background is
  `#E8452C`; the splash is `#110E0C`.
- **Signing:** the APK is signed with Flutter's automatic debug key (`~/.android/debug.keystore`, "CN=Android
  Debug"). That's fine for sideloading. But Android only installs an update over an existing app if the key
  matches: an APK built on another computer (e.g. Bryan's PC) has a different debug key, so the phone will refuse
  it until ChefBot is uninstalled, which **deletes its saved recipes and settings on the phone**. To keep one key,
  copy `~/.android/debug.keystore` to the new computer's `~/.android/` before building there (or set up a proper
  release keystore).
- **Phone checklist** (on Bryan's Samsung 2026-10-28 "almost everything worked"; Email was the problem, since reworked):
  - Settings: type the OpenRouter key (no env var on a phone). It's kept in app-private SharedPreferences.
  - A recipe from the home form, and a follow-up change.
  - "Photograph my ingredients instead" (was "Snap my fridge"): `FilePicker.pick_files(file_type=IMAGE, with_data=True)` probably opens the photo picker,
    not the camera. If camera capture is wanted, look at Flet 1.0's options (`--permissions camera`, a camera
    control) before building something custom.
  - PDF (with and without a photo), Share: worked on Bryan's Samsung (2026-10-28). The old "Open in mail
    app" `mailto:` path on the phone dropped the PDF and cut the recipe at 6,000 characters; replaced by the share
    sheet (needs a re-test on the phone).
    CJK fonts for PDFs download on first use (10–18 MB) into `<data>/fonts`.
  - Dish picture.

### Sideloading onto the phone

1. Get `build/apk/chefbot-arm64-v8a.apk` onto the phone: AirDrop doesn't reach Android, so use Google Drive, email
   it to yourself, or a USB cable (Android File Transfer / the phone's "File transfer" mode).
2. Tap the APK in the Files app (or Drive, or Gmail). Android asks to allow that app to "install unknown apps":
   allow it (Settings > Apps > Special app access > Install unknown apps), then go back and tap Install.
3. Play Protect may warn about an unknown developer: choose "Install anyway" (or "More details" > "Install anyway").
4. Updating later: install the new APK the same way; data is kept as long as it was built with the same key (see
   Signing).

With USB debugging on, `~/Android/sdk/platform-tools/adb install -r build/apk/chefbot-arm64-v8a.apk` also works.

### What the toolchain put on the Mac (delete to reclaim ~13 GB)

Measured right after the first build (2026-10-28). Everything below was created by `flet build apk`; nothing in
`~/Library` changed. Before: 91 GB free; after: 74 GB free.

| Folder | Size | What it is |
| --- | --- | --- |
| `~/.gradle` | 4.1 GB | Gradle and its downloaded Android build libraries |
| `~/flutter` | 3.8 GB | Flutter SDK 3.44.8 (Flet's own copy) |
| `~/Android` | 3.8 GB | Android SDK (`~/Android/sdk`: build-tools 34-35, platforms 34-36, NDK, CMake, platform-tools/adb) |
| `~/Documents/Github/ChefBot/build` | 2.6 GB | Build output incl. the APKs (gitignored) |
| `~/.pub-cache` | 731 MB | Dart/Flutter packages |
| `~/java` | 308 MB | JDK 17.0.13 |
| `~/.flet/cache` | 59 MB | Flet build template and the Python-for-Android runtime |
| `~/.android` | 6 MB | **Holds `debug.keystore`, the signing key** (see Signing): copy it somewhere before deleting |
| `~/.dart-tool`, `~/.flutter`, `~/.cookiecutters`, `~/.cookiecutter_replay` | < 1 MB | Tool settings and template caches |

Keep `~/.flet/client` (the desktop app's Flet runtime, there before the build). To remove everything (copy the APK
and `~/.android/debug.keystore` somewhere first if wanted):

```bash
rm -rf ~/.gradle ~/flutter ~/Android ~/.pub-cache ~/java ~/.flet/cache ~/.android \
       ~/.dart-tool ~/.flutter ~/.cookiecutters ~/.cookiecutter_replay ~/Documents/Github/ChefBot/build
```

The next `flet build apk` downloads it all again.

## Flet 1.0 gotchas learned the hard way

- Services (`SharedPreferences`, `Clipboard`, `Share`, `FilePicker`, `UrlLauncher`) auto-register when constructed
  inside the page context; most methods are `async`.
- **Android back button (2026-10-28):** the root view (`page.views[0]`) has `can_pop` and `on_confirm_pop`, which wrap
  Flutter's PopScope. `show_chat` sets `can_pop = False`, so back fires `_on_back`, which goes home and calls
  `confirm_pop(False)`; `show_home` sets it back to `True`, so back on the home screen leaves the app. An open
  dialog closes first on its own. Untested on the phone yet (web can't press the system back button).
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
