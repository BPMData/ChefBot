# ChefBot handoff (as of 2026-11-12)

Everything a new session needs to keep going without the original conversation. Read this first, then
`README.md` (features, how models were chosen) and `docs/EMAIL.md` (mail relay setup).

## What this is

ChefBot is Bryan's 2026 rewrite of **RecipeGPT** (`../RecipeGPT`), a Streamlit app he wrote 100% by hand in
2023–24. **RecipeGPT is a time capsule: never modify it.** ChefBot is a personal demo piece, so quality matters
more than cost.

**Private details** (where secrets live, accounts, his phone, which saved recipes are his) are in
`HANDOFF.local.md`, which is gitignored. Read it too when it exists.

- One Python codebase on [Flet](https://flet.dev) **1.0.5** (Flutter UI): desktop, web, Android (sideloaded APK).
- Models via **OpenRouter**. The key lives in a file outside every repo (see `HANDOFF.local.md`); never commit
  it, never type it into a UI field; pass it as `OPENROUTER_API_KEY` for dev runs.
- On GitHub as **BPMData/ChefBot**, AGPLv3 (see README). Work goes on a branch with a PR into `main`; Claude
  opens the PR, Bryan merges it.

## Pinned (do these next, in this order)

**Raise with Bryan at the start of the next ChefBot implementation session** (he asked to be reminded):
**pantry defaults**, a setting ("Use cuisine pantry defaults") so a photo of only new groceries still gets a
sensible recipe, assuming the spices and staples a cook of the chosen cuisine usually has. Details and caveats in
`docs/research/FINDINGS.md` ("About the added-cuisines run"). Not started; drop this note once he decides.


1. **Mail relay: deployed (2026-10-28)** as Bryan's own Apps Script web app (`tools/mail-relay.gs`, setup in
   `docs/EMAIL.md`; account and status in `HANDOFF.local.md`). Direct SMTP with an app password fails
   (`SMTPServerDisconnected` during sign-in); the relay is the way.
   **Since 2026-10-28 the relay is a hidden developer option** (tap the "Settings" title 7 times; pref
   `chefbot.dev_mode` = "on"). Everyone else: Email on a phone opens the share sheet (subject + full plain-text recipe + PDF and
   photo attached; share_plus passes EXTRA_SUBJECT/EXTRA_TEXT/EXTRA_STREAM, so Gmail fills all three). On desktop
   it's a `mailto:` link with the whole recipe (shortened only on Windows, whose mail apps reject long links).
   Confirmations: a relay send keeps the dialog open with "Sent to ..." (or "Not sent: ..."). The share sheet
   result comes back when the user returns to ChefBot (after sending, in practice), so ChefBot says "Sent by
   your phone's mail app." (Bryan's wording). Strictly it only knows an app was picked, not that the email went.
2. **Android APK built and installed on Bryan's phone (2026-10-28).** Almost everything worked first try; only
   email was off (fixed: share sheet, see item 1). Re-test Email on the phone after installing the new build. See "Android" below for installing, rebuilding, signing,
   and deleting the ~13 GB toolchain.
3. **GitHub: public since 2026-10-28** (AGPLv3). Still to do: README screenshots.
   **Next after the cuisine tree: a public web demo** (Bryan, 2026-11-09: it's a portfolio piece, and recruiters
   won't run Flet commands). The plan, not started:
   - **Host it as a server app**, not a static build: Flet's web mode on a small always-on host (Fly.io, Render,
     Google Cloud Run or similar; pick one when building). A static `flet build web` would put the OpenRouter key in
     the browser, where anyone can copy it.
   - **A separate OpenRouter key with a hard credit limit** (openrouter.ai/keys), stored as the host's secret, plus
     per-visitor limits (a few recipes a day, a short reply cooldown) so a bot can't drain it. Pictures and photo
     reading are the expensive calls: lower limits there.
   - **Per-visitor storage.** Today the app keeps one shared history folder; on a public server every visitor
     would see everyone's recipes. Saved chats must be per browser (Flet's client storage or a visitor id).
   - **Demo settings:** hide the API key field, the relay and developer options; Email becomes the `mailto:` link;
     check that photo upload and Save PDF work in a browser (they use FilePicker uploads and downloads).
   - **A few featured recipes** that open instantly without spending anything, for visitors who just look.
   - Then README screenshots and the live link at the top of the README.
4. **Keep replies alive when the app is in the background: works on the phone (2026-11-03).** It took three
   builds: pyjnius couldn't reach the extension's Java code (see "pyjnius can't find the app's own classes").
   Still to try: the screen-locked case and the airplane-mode fallback below.
   Before: switching apps mid-reply let Android freeze ChefBot (logcat: "Skipping
   setProcessStateToThread due to frozen status"), the stream died, and you came back to "Lost the connection to
   OpenRouter". Now (see "Background replies" under Architecture): a foreground service with a notification
   while anything is being written, a "Ready: <title>" notification if it finishes while you're away, and, as
   the fallback Bryan also asked for, an automatic retry when you come back if the stream died anyway.
   Build with `rm -rf build && .venv/bin/flet build apk --yes` (start clean after extension changes, see the
   build gotcha), install, then on the phone:
   - First recipe: Android 13+ asks to allow notifications (allow it). The shade shows "ChefBot is writing your
     recipe" while it streams; it goes away when the reply ends.
   - Send a follow-up, switch to another app straight away, wait a minute: "Ready: <title>" arrives; tap it and
     the finished recipe is there.
   - Same with the screen locked (the service holds a wake lock).
   - Fallback: turn on airplane mode mid-reply while in another app, then off, then return: the card says it lost
     the connection, then it starts that reply again (once).
   - If anything misbehaves: `adb logcat -d | grep -iE -A12 "keep-alive|keepalive|jnius"` (Python logs under
     the tag `flet.python`, the Java side under `KeepAlive`).

5. **Later: a second-pass recipe audit.** After each recipe, send it to the cheapest, fastest model that does the
   job well enough, to check only: ingredient weights and ratios, timings, and that the dietary rules and
   "never use" list were followed. Undecided: what happens when it finds a problem (a note under the reply, or an
   automatic fix). For now the main prompt has a "check your work" list (`prompts.system_prompt`).

6. **In progress: the cuisine tree.** Replace the flat cuisine chips with a drill-down by continent and region
   (about 50 cuisines), built from deep research rather than model memory. Plan, decisions and taxonomy:
   `docs/CUISINE_TREE.md`. Ready-to-paste prompts: `docs/research/<continent>.md` (rebuild with
   `tools/make_research_prompts.py`).
   **Where it stands (2026-11-09):** research is **complete for all five continents** (65 nodes, ChatGPT deep
   research, v2 prompt). Everything learned, including import quirks, open questions for Bryan and corrections to
   the app's current entries: `docs/research/FINDINGS.md` (read it first; the raw reports in
   `docs/research/results/raw/` are only for checking a specific claim). Data: `docs/research/results/*.json`.
   Added 2026-11-09: Tunisian and Algerian (Africa), Afghan and Pakistani (Asia), researched together and saved as
   `docs/research/results/additions.json` (kept as two nodes, Afghan and Pakistani, per the research). That run
   also raised an idea for Bryan: per-cuisine "pantry defaults" (see FINDINGS).
   **Build plan (2026-11-09):** Bryan will have Google AI Studio attempt the refactor from the self-contained brief
   `docs/REFACTOR_CUISINE_TREE.md` (data under `src/chefbot/cuisines/`, a loader, the drill-down picker, recent
   picks, legacy ids for saved chats, tests). Claude's job afterwards: review its pull request, fix its mistakes,
   then do the house-style pass on the entries.
   **2026-11-12:** Gemini's `gemini-step1` attempt (BPMData/ChefBot_Gemini_Experimental) was ported in as-is on
   branch `cuisine-browser` (list drill-down in a bottom sheet). Changed: continent subtitles are geographic only
   (no flavor profiles), and "Near & Middle East" is now "Near East". Reviewed and fixed: 19 cuisines listed
   the same item as a classic flavor and as a "signature ingredient, use only if you have it" (contradictory
   prompt); the builder now drops the duplicate. Data files were CRLF, now LF. Saved "Hong Kong" chats map to
   Cantonese (Bryan's call, 2026-11-12: no separate Hong Kong node). Open question: 12 cuisines' tips carry raw research
   notation (`salt_g ≈ sodium_mg × 0.00254`) into the prompt. Still to do: the house-style pass on the entries.
   **2026-11-12 ("Browse by map" on branch `browse-by-map`):** Built the full-screen interactive map browser beside
   "Browse cuisines" (`docs/BROWSE_BY_MAP.md`).
   - **Data & build pipeline (`tools/build_map_data.py`, `src/chefbot/maps/*.json`, `docs/MAP_SOURCES.md`):**
     Reads the git-ignored public-domain shapefiles in `assets/maps/source/` (`palestine_POV_ne_10m_admin_0_countries_pse`
     for all country outlines, `ne_10m_admin_1_states_provinces` for states/provinces/Italian regions, and
     `cb_2025_us_county_500k` `STATEFP == "22"` for the 64 Louisiana parishes) using `pyshp` (dev dependency only).
     Dissolves shared interior edges within multi-polygon regions, projects to a 360 x 520 phone canvas, and
     simplifies with Ramer-Douglas-Peucker into 13 lightweight JSON files (`world`, 5 continents, 7 multi-region
     countries; 236 KB total). Distant island territories (such as Tokyo's southern Pacific islands below 34.5N,
     Paracel Islands, and overseas European departments) are filtered out of regional bounds so mainland regions
     fill the frame cleanly.
   - **Map UI & hit-testing (`src/chefbot/maps.py`, `src/main.py`):**
     Replaces `self.root.content` with a full-screen map view (top bar with Back arrow, breadcrumb heading, and a
     plain "Any" button on the 7 country levels; `ft.InteractiveViewer` for pinch-zoom and pan; `flet.canvas.Canvas`
     wrapped in `ft.GestureDetector` with bounding-box + ray-casting point-in-polygon hit-testing and 6 px coastal
     tolerance; `ft.Stack` for on-map labels and non-overlapping call-out chips connected by leader lines). Each
     continent, country, and regional cuisine is assigned a distinct color from `MAP_PALETTE` (built-in `ft.Colors`
     shades: coral, blue, amber, orange, teal, green, purple, pink, cyan, indigo, lime) so neighboring regions and
     the five world continents are scannable at a glance without needing call-outs for Europe or Near East on the
     world map, with a brief highlight on tap before drilling down or opening the cuisine info sheet.
   - **Info sheet mini-map:** Added `_cuisine_mini_map()` at the top of `_cuisine_info_lines()` so both the list
     browser, the map browser, and the home screen chip's info icon display a small regional map with the selected
     cuisine highlighted, keeping all existing info sections (including "If you're missing one" substitutes) intact.
   - **Tests (`tests/test_maps.py`):** Verifies every selectable leaf cuisine, country, and continent has a map
     region, every map region id exists in the cuisine tree, all small regions (`< 44 x 44` px) and known cases
     have non-overlapping call-outs, point-in-polygon `hit_test` and `region_for_cuisine` work for all nodes, the
     builder reproduces committed JSON when source shapefiles are present, and the UI drill-down/pick/Back flow works
     at phone and desktop sizes.
   - **Still to do:** House-style pass on cuisine entries (including the 12 tips with raw `salt_g` formula notation),
     pantry defaults decision with Bryan.
   - **2026-11-12, tested on the phone:** works well. Fixed (PR #23): at 1x the map could be dragged around;
     the viewer's boundary margin is now 0, so it only pans while pinch-zoomed, within the map's edges.
   - **Next (Bryan's idea, 2026-11-12):** replace the flat world level with a spinnable, zoomable globe that
     flies to the chosen continent. Brief for Gemini (Antigravity): `docs/GLOBE_BROWSER.md`. Claude reviews
     its pull request afterwards.

## Run, test, verify

```bash
cd ~/Documents/Github/ChefBot
.venv/bin/flet run src/main.py                       # desktop window (Bryan's normal way)
OPENROUTER_API_KEY=... \
  .venv/bin/flet run --web --port 8551 src/main.py   # web: what Claude uses with the browser pane
.venv/bin/python -m pytest                           # offline tests (GitHub runs them on every PR,
                                                     # push to main, and on demand: Actions > Tests)
                                                     # (CI installs flet too: test_keepalive drives reply())
OPENROUTER_API_KEY=... .venv/bin/python tools/smoke.py   # live: recipe + follow-up edit (~1¢)
```

- The venv is Python 3.14 (`.venv`, plain pip; no uv on this Mac). Deps: flet[all]==1.0.5, httpx, markdown,
  fpdf2, pillow==12.3.0 (pinned for Android), flet-camera==1.0.5, pytest, pypdf.
- **Web dev mode quirks:** first page load takes ~20 s; Flutter draws on a canvas, so `find`/`read_page` see
  nothing: use screenshots and coordinates. After code changes, **restart the server** (hot reload leaves broken
  sessions). Use absolute paths in background shell commands (the shell's cwd drifts).
  Check no old `main.py` process is still running before testing: a leftover keeps answering on the port. In a
  cloud session the browser can't reach www.gstatic.com, so Flutter never loads; have Playwright serve
  `flutter-canvaskit/*` from `flet_web/web/canvaskit/` in the venv (`page.route` + `fulfill`).
- **Dev storage:** `flet run` keeps recipes/photos in `src/.flet/storage/data/` (gitignored). On a phone it's
  `FLET_APP_STORAGE_DATA`; fallback `~/.chefbot`. Desktop settings (incl. secrets) are in the macOS defaults domain
  `com.appveyor.flet`; read single keys with `defaults read com.appveyor.flet flutter.chefbot.<key>`, never dump
  the whole domain (it holds the OpenRouter key and passwords).
- **Saved recipes:** some are Bryan's and must never be modified (the list is in `HANDOFF.local.md`). The
  recent list is ordered by last update, so positions change; check the title before clicking.
- Don't click Save PDF / Save HTML / Share in the browser pane (they download files onto the Mac). The export code
  is covered by `tests/test_export.py`.

### Scheduled API checks (added 2026-10-31)

`.github/workflows/api-checks.yml` runs `tools/api_check.py`: **daily** `models` (free, no key: OpenRouter's
public model list; ids, `reasoning` support, image in/out, retirement dates, Z.ai still hosting GLM),
**Sundays** `recipe` (a full recipe from the default model at default thinking, a one-word reply from each other
model, a photo read of a drawn tomato), **the 1st of the month** `picture` (a dish picture). Model ids come from
`api.py`, so the checks follow model changes. A failed scheduled run emails the repo owner. A retirement date
more than 30 days out is a warning; within 30 days it fails. Run one by hand: Actions > API checks > Run
workflow. GitHub turns scheduled workflows off after 60 days without a commit; re-enable from the Actions tab.

**Still to do (Bryan):** add the key so the Sunday and monthly checks run (until then they skip with a
notice). On GitHub: the repo > Settings > Secrets and variables > Actions > New repository secret, name
`OPENROUTER_API_KEY`, value = the key from the file noted in `HANDOFF.local.md`. Ideally a separate OpenRouter
key just for this, with a small credit limit (openrouter.ai/keys lets you set one), so it can be revoked
alone. GitHub never shows secrets in logs or hands them to pull requests from forks.

## Architecture

```
src/main.py              UI: home form, list & map cuisine browsers, recipe conversation, settings, email dialog
src/chefbot/cuisines.py  cuisine tree loader, validator, breadcrumb paths, chip labels (`src/chefbot/cuisines/*.json`)
src/chefbot/maps.py      map level loader, point-in-polygon hit-testing, mini-map lookup (`src/chefbot/maps/*.json`)
src/chefbot/prompts.py   audiences, cuisines (+ classic seasonings), dietary rules, prompt text (ported from
                         RecipeGPT's personas.py; since 2026-11-08 the persona is a food scientist and
                         test kitchen developer, not a food blogger; salt always in grams)
src/chefbot/api.py       OpenRouter: streaming chat, photo -> ingredients, dish picture
src/chefbot/history.py   conversations + photos saved as JSON/PNGs; prune_photos()
src/chefbot/export.py    Markdown -> HTML page / PDF / email; SMTP + relay sending
src/chefbot/recipe.py    extract_title() (last "Recipe Title:" line wins)
src/chefbot/android.py   Android-only pyjnius calls: MediaStore save to Downloads, media scan
src/chefbot/keepalive.py keeps replies alive in the background (foreground service + notifications)
packages/flet-keepalive/ ChefBot's own Flet extension: the Android foreground service (Java) behind keepalive.py
tools/build_cuisine_data.py  builds `src/chefbot/cuisines/*.json` from `docs/research/results/`
tools/build_map_data.py      builds `src/chefbot/maps/*.json` from `assets/maps/source/` (dev dep `pyshp`)
tools/mail-relay.gs      Apps Script relay (secret + 40/day cap)
tools/make_static_fonts.py   cuts static PDF fonts from variable ones (already done; output committed)
tools/smoke.py           live API check
```

- **Memory:** a conversation is `system` + `user`/`assistant` turns; the system prompt tells the model to rewrite
  the complete recipe on change requests and keep a `Recipe Title:` line. User messages can carry a `display`
  field (the friendly summary shown instead of the raw prompt). Photos are stored per assistant-message index in
  `conv.photos` and never sent to the model.
- **Editing:** only the latest user follow-up (index ≥ 2) gets Edit/Delete. Edit is non-destructive until send
  (`editing_index`); Delete truncates from that index with Undo. Title recomputed via `_latest_title()`. If an
  edited message gets no reply at all (offline, out of credit), `send_text` puts the original message and reply
  (and photos) back and stays in edit mode with the new text in the box. Tested 2026-10-28 by running the web
  server with `HTTPS_PROXY=http://127.0.0.1:9` (every request fails like having no signal).
- **Replies finish in the background:** leaving a chat (back arrow or phone back) no longer stops the reply.
  `reply()` keeps streaming, saves the complete answer, refreshes the home list and says "Ready: <title>".
  Reopening that chat shows the same live `Conversation` and re-attaches the card being written
  (`self.working`, `self.live_bubbles`). "Busy" is per conversation (`busy` property), so another chat isn't
  blocked. A chat still writing can't be deleted from the list. Only Stop cuts a reply short.
- **Background replies (2026-10-31; Android).** `chefbot/keepalive.py` holds a foreground service
  (`packages/flet-keepalive`, see below) open while a reply or dish picture is in progress
  (`with self.keepalive.holding(WRITING)` around each stream attempt), so Android doesn't freeze the process. It
  asks for the notification permission once per run on the first reply (Android 13+; without it the service
  still works, the notifications just don't show). `_on_lifecycle` tracks `away` (HIDE/PAUSE) and back
  (SHOW/RESUME); a reply that finishes while away posts "Ready: <title>", cleared on return. **Auto-retry:**
  if the stream fails with `api.ConnectionLost` and ChefBot went away during it, `reply()` drops the partial
  text, waits until you're back (Android won't start the service from the background) and streams once more.
  A loss while on screen is shown as before. It waits `RETRY_SETTLE` (1 s) before deciding, because a frozen
  process hears about going away only after it thaws, possibly after the error. Elsewhere (desktop, web) the
  keep-alive has no backend and does nothing; the retry still applies.
- **`packages/flet-keepalive`** is ChefBot's own Flet extension. The Android part is Java (no Kotlin, so it
  builds whatever Kotlin setup the template has): `KeepAliveService` (type `dataSync`, `stopWithTask`, a
  30-minute partial wake lock, stops itself on Android 15's 6-hours-a-day `onTimeout`) and `KeepAliveReceiver`
  (posts/clears the "Ready" notification; a broadcast because a backgrounded app can't start a service). Python
  sends both Intents by class name with only android.* classes (see the pyjnius gotcha below). Its manifest adds the
  service and the FOREGROUND_SERVICE, FOREGROUND_SERVICE_DATA_SYNC, POST_NOTIFICATIONS and WAKE_LOCK
  permissions; the manifest merger puts them in the app (Flet's build has no setting for a `<service>`, which
  is why `flutter_foreground_task` wasn't used: it needs one in the app's manifest). The Dart side is an empty
  `Extension` that `flet build` needs to register the plugin. It's wired in through `[tool.flet.android]`
  `dependencies` + `[tool.flet.android.dev_packages]` (pip builds it from the folder). The Java compiles against
  the Android 16 framework (checked 2026-10-31 with javac); the full Gradle build hasn't run yet.
- **A damaged saved-recipes file is set aside, never overwritten (2026-10-31).** `History.load()` used to
  return an empty list for unreadable JSON, and the next `save()` then wrote only the new recipe over it. Now it
  renames the file to `conversations.unreadable-<time>.json` (logged) and starts fresh. Writes were already
  atomic (temp file + replace), so this only matters for disk errors or hand edits.
- **No cap on saved recipes** (was 60, silently dropping the oldest). `prune_photos(keep=...)` spares photos a
  pending edit or running reply may still need.
- Note: the Browser pane's dev-server sandbox can't read `../openrouter.txt`; for live web tests start the server
  from Bash with the key in the environment and open the URL with `preview_start {url}`.

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
- **Kimi K3.1 Pro needs `temperature: 1` (2026-11-03).** Moonshot started refusing 0.7 ("invalid temperature: only
  1 is allowed for this model"); the first GitHub run of the Sunday API check caught it. Temperature is now
  per model (`Model.temperature`, default 0.7). Errors now include the provider's own message
  (`_provider_detail`), which is how this one was found.
- Free OpenRouter models were rejected: slow, rate-limited, and one gave wrong allergen advice.

## Bryan's preferences (UI and process)

- **No emojis anywhere** (UI or model output). Material icons, custom SVG, or plain text instead. The system
  prompt says "no emojis"; older saved recipes still contain a few.
- **Dark theme by default** (Light/System in Settings). Fonts: Fraunces (headings) + DM Sans (body), bundled.
  Content in a centered column (max 780 px) on desktop; it looked bad stretched full width.
- No cost talk in the UI ("costs about a cent" was removed: cost is his problem).
- "The 1817 version" quick tweak stays **BETA** with a strong hallucination warning; no year picker.
- Every reply has Copy (Markdown), PDF, HTML, Email, Share, Picture. Copy/actions act on that reply only.
- **Cuisines** (`prompts.py`): `CUISINES` (classic flavors, used only where they suit the dish), `SWEET_FLAVORS`
  (desserts only), `SIGNATURE_INGREDIENTS` (only if the user has them, else a Tips line), `CUISINE_TIPS` (e.g. the
  Cajun seasoning shortcut goes in Tips, never the ingredients), `CUISINE_ABOUT` (the app's info sheet; never sent
  to the model). Bryan's calls (2026-11-08): cinnamon, vanilla and Old Bay stay in American savory; filé powder is
  out; kimchi is "strongly recommended" for Korean, not required. Creole (New Orleans) added beside Cajun.
- Every user message has Copy (always shown). It copies what the bubble shows: for the opening request that's
  the friendly `display` summary, not the raw prompt.
- Plain-language explanations; he's technical but values brevity. He tests thoroughly and reports precisely.

## Android: build, install, clean up

First built 2026-10-28 on the MacBook (Flet 1.0.5, Flutter 3.44.8, JDK 17, Android SDK 36). It built on the first
try; the first run took about 20 minutes, mostly downloads.

```bash
cd ~/Documents/Github/ChefBot
.venv/bin/flet build apk --yes     # split-per-abi, splash, icon background, camera permission: all in pyproject.toml
# output: build/apk/chefbot-arm64-v8a.apk (66 MB, for any modern phone),
#         chefbot-armeabi-v7a.apk (old 32-bit phones), chefbot-x86_64.apk (emulators)
.venv/bin/flet debug android      # run on a USB-connected phone (developer mode + USB debugging); `--show-devices`
```

**A second, beta copy beside the normal app** (added 2026-11-09, for trying a branch such as AI Studio's cuisine
tree): build that branch with its own package id and name. Android treats it as a different app, with its own
saved recipes and settings (enter the API key again in its Settings); the normal ChefBot is untouched. Not yet
tried on the phone.

```bash
git checkout <branch> && rm -rf build
.venv/bin/flet build apk --yes --bundle-id io.github.bpmdata.chefbotbeta --product "ChefBot Beta"
~/Android/sdk/platform-tools/adb install build/apk/chefbot-arm64-v8a.apk
git checkout main                  # and rebuild without the flags for the normal app
```

- Config is in `pyproject.toml`: `[tool.flet]` org `io.github.bpmdata` (package `io.github.bpmdata.chefbot`),
  product `ChefBot`, `permissions = ["camera"]`, `[tool.flet.app] path = "src"`, `[tool.flet.splash]` and
  `[tool.flet.android]` (split_per_abi, adaptive icon background). Permissions in the APK: INTERNET,
  ACCESS_NETWORK_STATE, CAMERA (plus RECORD_AUDIO and old-storage ones that the camera plugin declares itself;
  ChefBot initializes the camera with audio off, so the microphone is never requested). Since 2026-10-31 also
  FOREGROUND_SERVICE, FOREGROUND_SERVICE_DATA_SYNC, POST_NOTIFICATIONS and WAKE_LOCK, from `flet-keepalive`.
- **Pillow is pinned to 12.3.0** because Flet's Android package index has no 13.x (the Mac venv has 13.0.0; the
  pin is fine on desktop too). Its native libs (`libPIL-_imaging.so` etc.) are in the APK. If it were ever missing,
  `_add_photo()` leaves the photo out of the PDF instead of failing.
- **App icon:** `src/assets/icon.png` (1024x1024). It is the logo's hat, scaled to 92%, on a full-square version of
  the orange gradient, so the launcher's circle/squircle mask never clips the hat. Rendered from an SVG with
  macOS's own SVG support (a small Swift script; no rsvg/Inkscape on this Mac). The adaptive-icon background is
  `#E8452C`; the splash is `#110E0C`.
- **Signing:** the APK is signed with Flutter's automatic debug key (`~/.android/debug.keystore`, "CN=Android
  Debug"). That's fine for sideloading. But Android only installs an update over an existing app if the key
  matches: an APK built on another computer has a different debug key, so the phone will refuse
  it until ChefBot is uninstalled, which **deletes its saved recipes and settings on the phone**. To keep one key,
  copy `~/.android/debug.keystore` to the new computer's `~/.android/` before building there (or set up a proper
  release keystore).
- **Phone checklist** (2026-10-28: "almost everything worked"; Email was the problem, since reworked):
  - Settings: type the OpenRouter key (no env var on a phone). It's kept in app-private SharedPreferences.
  - A recipe from the home form, and a follow-up change.
  - "Photograph my ingredients instead": on a phone it opens ChefBot's own camera screen (`flet-camera` 1.0.5, a
    live preview + shutter, back lens, 720p "high" preset, no audio), with Gallery and Cancel buttons. If the
    camera can't start (no permission, no camera) it falls back to the gallery picker. On desktop/web it's the
    file picker. Camera added 2026-10-28; untested on the phone so far.
  - Dish pictures: tap one for full screen (a dialog, so the phone's back button closes it; pinch to zoom). The
    download button saves the original (about 1 MP, as the image model made it) straight to the phone's shared
    `Download` folder through MediaStore (`android.save_to_downloads`, via pyjnius, an Android-only dependency in
    `[tool.flet.android]`), so it's indexed the moment it's written. Fallbacks: a plain file write plus a media
    scan (Samsung's scan took 10+ s), then the save dialog. Desktop: `~/Downloads`. The viewer shows a green check
    and "Saved to Downloads" (a snackbar would be hidden behind it). On one Samsung the picture took ~30 s to
    appear in Gallery/My Files although MediaStore had it within the same second as the write, so check whether
    the delay is before the write (in ChefBot) or the phone's apps refreshing.
  - PDF (with and without a photo), Share: worked on the phone (2026-10-28). The old "Open in mail
    app" `mailto:` path on the phone dropped the PDF and cut the recipe at 6,000 characters; replaced by the share
    sheet (needs a re-test on the phone).
    CJK fonts for PDFs download on first use (10–18 MB) into `<data>/fonts`.
  - Dish picture.

- **pyjnius can't find the app's own classes (2026-11-02).** The first keep-alive builds failed on the phone with
  `ClassNotFoundException: io.github.bpmdata.keepalive.KeepAlive` (`adb logcat -d | grep -iE -A12
  "keep-alive|jnius"`), even with the class in the APK. Python's threads look classes up with Android's system
  class loader, which only knows android.* classes. On the event-loop thread even Flet's own
  `MAIN_ACTIVITY_HOST_CLASS_NAME` class isn't found (2026-11-03); `android.py` only works because it runs in
  `asyncio.to_thread` workers. So `flet_keepalive` uses only android.* classes: the app's Context from
  `ActivityThread.currentApplication()` (falling back to Flet's way, then that on a worker thread), and Intents
  addressed by class name (`setClassName`) to its service, receiver and `PermissionActivity` (an invisible screen
  that asks for the notification permission, since Python has no Activity to ask from). Do the same for any
  future Java code ChefBot ships. (An app-level `-keep` rule in `[tool.flet.android] proguard_rules` was added on
  the way; harmless, kept.)
- **Build gotcha (2026-10-28):** "chefbot depends on flet_camera from path which doesn't exist
  (build/flutter-packages/flet_camera)" means the cached `build/flutter` project is stale. Deleting only
  `build/flutter` or `build/site-packages` doesn't help (`build/.hash` says it's up to date); `rm -rf build` and
  rebuild (about 4 minutes, nothing re-downloads). Copy the APK out first if you want to keep it.

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
`~/Library` changed.

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
- Deliberate fallbacks log a warning to the `chefbot` logger (stderr; logcat on Android) instead of `pass`.
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
- **`flet run` hot-reloads whenever a source file changes, including Claude's edits while the app is open.**
  The reloaded session's `SharedPreferences` never answers (10 s timeouts), so settings can't be read or saved.
  This happened 2026-10-28. The app now treats an unreadable load as an error (it no longer opens a blank
  first-run Settings that would save over his real settings) and shows Save failures in the dialog. Before editing
  code, check whether Bryan's app is running (`ps ax | grep ChefBot/src/main.py`) and tell him to restart it
  afterwards.
- **Android: the HTTPS certificate file can disappear while the app is open (2026-11-07).** httpx re-reads
  `SSL_CERT_FILE` (Flet sets it on Android) each time a client is made, so saving Settings later crashed with
  `FileNotFoundError` in `ssl.create_default_context`. `api.ssl_context()` now loads the certificates once into
  memory (falling back to certifi) and every httpx client uses it. Make any new client with `verify=ssl_context()`.
  Needs an APK rebuild to reach the phone.
- **Markdown quotes and code blocks need theme colors (2026-11-11).** Flutter's default quote box is a fixed light
  blue and code blocks get a light highlighter background, so in the dark theme a quoted or fenced corrected step
  showed as faint light text on a bright block. `md_style()` sets `blockquote_decoration` (surface box, orange
  left bar); `md_code_style()` and `MD_CODE_THEME` (a transparent highlighter `root`) do the same for code blocks.
  Pass all three to any new `ft.Markdown`. Checked in the web build (dark theme).
- **Never use `capitalization=` on a TextField (2026-11-11).** Flet doesn't tell the keyboard; it adds a formatter
  that rewrites the text on every keystroke and drops the keyboard's in-progress word, so Android resets the
  keyboard: voice typing stopped after a few characters and double-tap caps lock lasted one letter. Removed from the
  ingredients box and the chat box; follow-ups get their first letter capitalized on send instead.
  `tests/test_text_fields.py` guards it. Needs an APK rebuild to reach the phone.

## PDF gotchas (fpdf2 2.8.9)

- Use **static** font cuts (`src/assets/fonts/static`); variable fonts made exports take 16–48 s.
- Each cut needs a **unique internal name** (`static_instance()` rewrites the name table), or regular/bold collide.
- **Don't use `set_fallback_fonts`**: it scrambled long mixed-script paragraphs. `assign_fonts()` wraps every run the
  base font can't draw in an explicit `<font face>` instead; uncovered characters (emoji) are dropped.
- Models put lists right under a bold label with no blank line; `normalize_markdown()` fixes that before conversion.
- Exports drop the `Recipe Title:` line (the title is the heading).

## Backlog (nice to have)

- **Second-model review loop (idea, 2026-11-11, not started).** Bryan's view: asking the model to double-check
  itself never matches a real second check, so every recipe should pass through a separate, faster model.
  Test case with the mistakes it must catch: `docs/review-loop/example-lamb-fries.md` (onion cooked but never
  added; chickpeas "crisped" by simmering in water).
  - *Flow (Bryan's pick):* **stream first, check after, fix automatically.** The reply streams as now (nobody
    starts cooking in 30 seconds). When it ends, a status line under the bubble says "Checking..."; the reviewer
    gets the whole recipe and returns a short list of issues as JSON (issue, location, fix), not a rewrite, so
    it's fast. No issues: "Checked". Minor issues: targeted edits, swapped in once. Major issues (diet/allergen/
    must-not violation, missing step): one revision round with the main model, then swap. "Fixed 2 things", tap
    to see what changed. Text only ever changes once, after the stream ends.
  - *What it checks:* every ingredient used in the steps is in the list and gets added; quantities match; methods
    do what the step says (crisp, sear, reduce); times and temperatures are plausible; notes match the steps;
    diet/allergen/must-not rules; the user's ingredients are actually used.
  - *Optional loading animation* (for the check and any revision round). **Decided 2026-11-11: use EOMD**, Bryan's
    own repo (github.com/BPMData/EOMD: 3D canvas motion graphics in single offline HTML files, which an AI writes
    as small JSON pieces). Chosen over Rive because an AI can write and change EOMD pieces, while Rive's `.riv`
    files are binary and have to be made by hand in Rive's editor. Plan: bundle a small EOMD piece as an asset
    in `flet-webview` and drive it live from Python with JavaScript calls (e.g. ingredient names spelled in 3D
    dots as they stream, a new stage when checking starts). Check first that `flet-webview` 1.0.5 runs on
    Android and can run JavaScript. Desktop fallback (the web view doesn't run on every desktop): a
    pre-rendered loop (EOMD's `tools/html_to_mp4.py`, converted to animated WebP for `ft.Image`). The new piece
    itself is made in the EOMD repo, following its own process. Rive (`flet-rive` 1.0.5) is the backup if the
    web view doesn't work on Android. Any new extension package means an APK rebuild. No emojis.
  - *Before shipping:* run the reviewer on the test case, then the existing judged recipe set with and without
    the review step; compare scores and time it. Reviewer: a fast model from one of Bryan's preferred labs.
    Pairs with Spoonacular idea 2 below (a hard-data allergen check).
- "Try again" on a reply; deleting a single older message.
- If Android kills ChefBot outright mid-reply (not just freezes it; rare with the keep-alive), the follow-up being
  answered is lost: it's only saved together with its reply. Saving the user message first would let the
  auto-retry pick it up after a restart.
- Auto-generate the dish picture after the first recipe (setting).
- README screenshots; a GitHub description.
- Old test conversations show raw `**Ingredients:**` in the first bubble (pre-redesign data); harmless.
- **Spoonacular integration (idea, 2026-11-09, not started).** Use it only for hard data the model guesses at,
  never for recipe search or meal planning (the chat already does those). It's optional: with no key, hide the
  extras. The key is handled like the OpenRouter one (Settings, env var for dev, never committed).
  1. Nutrition panel: a "Nutrition" button on a finished recipe that sends the ingredient list to Spoonacular's
     nutrition analysis and shows a facts panel. Do this first. Test it offline with a recorded response.
  2. Dietary/allergen check: Spoonacular is an independent check on the model's output. Parse the recipe's
     ingredients and flag anything that conflicts with a stated restriction or allergen (e.g. "nut-free" but
     the recipe has almond flour, "vegetarian" but it uses fish sauce or gelatin). This could run in the app as
     a warning and in tests as a regression check. Caveat: Spoonacular's allergen/diet tagging is ingredient-
     based and imperfect (cross-contamination, brand-specific ingredients), so it's a second check, not a
     guarantee; say so in the UI.
  3. Lower priority: unit conversion/scaling with real densities (good for baking), substitutes.
  Free tier is ~150 points/day (a nutrition call is ~1-2), which is fine for one user but not a shared class key.
- **Kimi K3.1 Pro: keep it, fixed (decided 2026-11-09, done 2026-11-12 in PR #11).** Always sent temperature 1
  (Moonshot refuses anything else) and **medium** thinking: `Model.efforts=("medium",)`, `api.effort_for()` picks
  the level actually sent, and Settings greys out Thinking at "Medium" while Kimi is picked (your choice for the
  other models is kept). Medium scored best (6.6 vs 5.8 for high) and is far faster (51 s vs 92 s). Kept because
  its score was the top one, within the tie.
