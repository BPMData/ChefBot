# Brief: build the cuisine tree

A self-contained task for a coding model with no memory of earlier sessions. The product decisions are made; your
job is to implement them. Where this brief and your own judgment disagree, follow the brief and note the
disagreement in the pull request. When something isn't covered, choose the smallest change that fits the existing
code and list it under "Choices I made" in the pull request.

## Read first

1. `CLAUDE.md`: ground rules (no emojis anywhere, dark theme, Fraunces + DM Sans, never commit secrets, always a
   pull request into `main`, never merge it).
2. `docs/CUISINE_TREE.md`: the plan, decisions and taxonomy.
3. `docs/research/FINDINGS.md`: what the research found and the quirks of its data.
4. `src/chefbot/prompts.py` and the cuisine parts of `src/main.py` (search for `cuisine`).

You don't need `HANDOFF.md` beyond its "Run, test, verify" section, and you don't need the raw reports in
`docs/research/results/raw/`.

## What exists today

- `prompts.CUISINES`: a flat dict, label -> (prompt name, flavor string), about 20 cuisines. Helpers keyed by the
  same labels: `SWEET_FLAVORS` (dessert-only, used only when Dessert is on), `SIGNATURE_INGREDIENTS` (used only if
  the user has them, otherwise mentioned in a Tips section), `CUISINE_TIPS` (extra Tips lines), `CUISINE_ABOUT`
  (text for the info sheet; never sent to the model).
- `prompts.system_prompt(audience, cuisine, dessert, restrictions)` builds the system prompt from those.
- `main.py`: `CUISINE_NAMES` (label -> chip text), one row of chips on the home screen, an info icon on the picked
  chip that opens a bottom sheet (`_cuisine_info`), Surprise me, and the recent-recipes list, which shows each
  saved chat's cuisine from `conversation.settings["cuisine"]` (a label string).
- Research data for all five continents: `docs/research/results/americas.json`, `asia.json`, `europe.json`,
  `near_east.json` and `africa.json` (65 nodes), plus `tunisian.json` (one more Africa node) and `afghan_pakistani.json` (Asia) if they exist by the
  time you start; if they don't, the build script must pick them up when they're added later. Ignore `near_east_run2.json` (a duplicate run; FINDINGS lists
  the few extras from it worth merging).

## What to build

### 1. Cuisine data the app ships

Create `src/chefbot/cuisines/` with one JSON file per continent (`americas.json`, `asia.json`, `europe.json`,
`near_east.json`, `africa.json`) and a loader module `src/chefbot/cuisines.py`. Everything under `src/` is packaged into the
Android app, so data files belong there, not in `docs/`.

Node schema (every node, every file):

```json
{
  "id": "us_cajun",
  "kind": "continent | country | cuisine | any",
  "label": "Cajun",
  "subtitle": "Roux, trinity, smoke, cayenne",
  "about": "2-3 sentences for the info sheet.",
  "prompt_name": "Cajun",
  "flavors": ["onion", "celery", "green bell pepper"],
  "sweet_only": [],
  "signature_ingredients": ["andouille sausage (substitute: smoked kielbasa plus extra black pepper)"],
  "tips": ["One instruction for the Tips section."],
  "pitfalls": ["One common mistake to avoid."],
  "avoid": ["filé powder"],
  "children": ["us_cajun", "us_creole"]
}
```

- `kind`: `continent` (top level, not selectable), `country` (a branch with children, not selectable), `cuisine` (a
  selectable leaf), `any` (the selectable "Any" leaf under a country: the outsider's picture of that country's
  food). A leaf has `"children": []`.
- `flavors`: display strings in one format: English first, then the native name and romanization in parentheses
  where they differ from the English, e.g. `"ginger (薑, goeng1)"`, `"Mexican oregano (orégano)"`, `"onion"`. Not
  the research's "native — romanization — English" form.
- `prompt_name`: how the prompt names the cuisine ("Cajun", "Sichuan (Chinese)", "Kanto (Japanese)").
- Ids: keep the research ids exactly (`us_cajun`, `mx_yucatan`, `sichuan`, `north_india`, `china_any`...).

Build all five files from the research JSON with a script, `tools/build_cuisine_data.py`, that does the
mechanical part. It must be rerunnable (the research files may be refreshed later):

- Drop organizational nodes (`the_americas`, `asia`, `europe`, `eight_great_cuisines`); add the five continent
  nodes yourself (`americas`, `asia`, `europe`, `near_east`, `africa`, labeled "The Americas", "Asia", "Europe",
  "Near & Middle East", "Africa"). Near & Middle East and Africa have no country level: their cuisines are the
  continent's direct children.
- Normalize `flavors` to the format above; turn `pitfalls` into short items; keep `about`, `subtitle`, `label`.
- Map `signature_ingredients` to the "item (substitute: ...)" form.
- `tips`: from the research `shortcuts`, keeping gram amounts and the salt-from-sodium rule.
- Apply the overrides in `tools/cuisine_overrides.json`, a small hand-edited file you create, which wins over the
  research. Start it with these decided overrides:
  - `us_cajun` and `us_creole`: `avoid` = ["filé powder"], filé removed from `flavors` and
    `signature_ingredients`, and `prompts.LOUISIANA_THICKENING` added to `tips`.
  - The quick fixes starred in `docs/research/FINDINGS.md` ("Corrections" section), where they apply to the
    research data.
  - Copy each `CUISINE_TIPS` entry in `prompts.py` into the matching node's `tips` (Cajun, Creole, Italian,
    Korean), so no current behavior is lost.
  - `us_any`: add cinnamon, vanilla and Old Bay to `flavors` (Bryan's call: savory latitude for all three).
  - `moroccan_north_african`: keep the research's label "Moroccan".
  - Don't merge anything from `near_east_run2.json`.

- Every list field in the research is already a list of plain strings (`tools/check_research.py` normalized
  them); signature ingredients read "item (substitute: ...)".
- Country nodes with sub-styles (`united_states`, `mexico`, `caribbean`, `china`, `japan`, `india`, `italy`) are
  branches: keep their `about` and `subtitle` for the browse list, and list their children in this order: the
  `*_any` child first, then the rest as the research orders them.

### 2. Loader and prompt

`src/chefbot/cuisines.py`:

- Loads every JSON file in `src/chefbot/cuisines/` once, validates it (unique ids; every child id exists; leaves
  have no children; labels at most 20 characters), and exposes: `get(id)`, `children(id)`, `continents()`,
  `leaves()`, `path(id)` (e.g. `["The Americas", "Caribbean", "Cuban"]`), and `chip_label(id)` (e.g.
  `"Caribbean · Cuban"`, or just `"Cajun"` when the country adds nothing obvious; your call, keep it under about 24
  characters).
- `LEGACY_IDS`: maps every old label in `prompts.CUISINES` to a new id, so saved chats keep their cuisine name:
  American -> `us_any`; American (Cajun) -> `us_cajun`; American (Creole) -> `us_creole`; both Cantonese and
  Hong Kong -> `cantonese`; Chinese (Sichuan/Shandong/Jiangsu) -> `sichuan`/`shandong`/`jiangsu`; Japanese
  (Kansai/Kanto) -> `kansai`/`kanto`; North Indian -> `north_india`; South Indian -> `south_india`; Korean,
  Thai, Vietnamese, Peruvian -> same names lowercased; Mexican -> `mx_any`; Italian -> `italy_any`; French,
  Greek, Spanish, Turkish -> `french`, `greek`, `spanish`, `turkish`. "Nothing in particular" stays the no-cuisine choice.

`prompts.system_prompt(audience, cuisine, dessert, restrictions)`: `cuisine` becomes a node id (or the no-cuisine
value). Keep every current behavior; read it from the node instead of the old dicts:

- flavors: "use only the ones that suit this dish" (today's wording);
- `sweet_only` only when `dessert` is on;
- signature ingredients only if the user has them, otherwise a Tips line (today's wording);
- `tips` into the Tips section; `avoid` as "Never use: ..."; `pitfalls` as a short "Common mistakes to avoid" list;
- dietary restrictions still override the cuisine's flavors (today's wording).

Then remove the old flat dicts (`CUISINES`, `SWEET_FLAVORS`, `SIGNATURE_INGREDIENTS`, `CUISINE_TIPS`,
`CUISINE_ABOUT`) and `CUISINE_NAMES` in `main.py`, once nothing uses them. Keep `LOUISIANA_THICKENING` and every
other prompt text in `prompts.py` unchanged.

### 3. The home screen and the picker (`src/main.py`)

Replace the row of about 20 cuisine chips in the "Pick a cuisine" card with:

- a row of chips: "Anything", then the last 5 picked cuisines (most recent first), each labeled with
  `chip_label(id)`. The picked chip keeps the info icon that opens the info sheet (reuse today's `_cuisine_info`
  and its bottom sheet, extended to show subtitle, about, flavors, dessert-only flavors and signature ingredients).
  Remember the recent picks across restarts in the same prefs store the app already uses (add a new pref key,
  stored as a JSON list of ids; see how `PREF_MUST_NOT` is saved).
- a "Browse cuisines" button, next to Surprise me, that opens the drill-down: a full-height bottom sheet, or a
  dialog if that works better at phone width. Level one: the continents as large tiles (a Material icon plus the
  name; no world map yet). Tapping a continent shows its countries and cuisines as a list with subtitles; a country
  shows its children, with "Any" first. A back button and a breadcrumb ("Americas > Caribbean") at the top.
  Tapping a leaf picks it, adds it to the recent chips, and closes the picker.
- Surprise me picks a random leaf (of any kind, including Any).
- The recent-recipes list and new conversations: store the node id in `settings["cuisine_id"]`. When showing a saved
  chat, read `cuisine_id`, or else map the old `settings["cuisine"]` label through `LEGACY_IDS`, or else show
  nothing. Never crash on an unknown value.

Keep the look: reuse the existing helpers (`card`, `section_title`, `heading`, `snack`, `soft_border`), theme
colors (`ft.Colors.PRIMARY`, `ON_SURFACE_VARIANT`...), Material icons, no emojis. It must work at phone width
(about 400 px) and in the centered desktop column.

### 4. Tests (`tests/`)

Update the tests that use the old dicts (`test_core.py`, `test_api.py`, `test_keepalive.py`; search for
`CUISINES`). Add tests that:

- every leaf builds a system prompt containing its `prompt_name` and its first flavor;
- the loader's validation catches a dangling child id and a label over 20 characters;
- every old label in `LEGACY_IDS` maps to an existing leaf;
- `sweet_only` appears only with dessert on; signature ingredients carry the "only if the user has them" wording;
- the Cajun and Creole prompts contain the no-filé rule and no node lists filé in `flavors`;
- `tools/build_cuisine_data.py` reproduces the committed `americas.json` and `asia.json` exactly (rerun check).

## Flet 1.0.5 notes

The app pins Flet 1.0.5, whose API differs from older Flet tutorials: `ft.Icons.X` and `ft.Colors.X` (not
`ft.icons`), `page.show_dialog(...)` and `page.pop_dialog()` for dialogs and bottom sheets, `ft.Alignment.CENTER`,
`ft.Padding(left=..., ...)`, `control.update()` after changing a control. Copy patterns from `main.py` rather than
from memory. A `ft.BottomSheet` with `scrollable=True` grows with its content; putting a scrolling `Column` inside
it makes it fill the screen.

## Checks before the pull request

- `python -m pytest` passes (install: `pip install "flet==1.0.5" "httpx>=0.28" "markdown>=3.7" "fpdf2>=2.8.4"
  "pillow==12.3.0" "pytest>=8" "pypdf>=5"`). The GitHub Actions workflow runs the same tests on the PR.
- Start the app if you can (`flet run --web --port 8551 src/main.py`) and look at the picker at phone width. If
  you can't run it, say so in the pull request.

## Deliverable

One branch, one pull request into `main`, not merged. The pull request lists: what changed, every override you
added to `tools/cuisine_overrides.json`, "Choices I made", and what you could not test. Don't change anything
outside the cuisine feature: email, export, keep-alive, settings and the Android build stay as they are.
