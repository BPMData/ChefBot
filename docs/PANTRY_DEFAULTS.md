# Brief: Pantry defaults (research, then build)

You are working in the ChefBot repo at `/Users/murphb/Documents/Github/ChefBot`. Read `CLAUDE.md`, `HANDOFF.md`
and the gitignored `HANDOFF.local.md` (if present) first: they hold the ground rules (the repo is public, never
commit, print or type secrets, no emojis anywhere in the UI or the model's output, work on a branch and open a pull
request into `main`, never merge it yourself, check the GitHub Actions tests pass). Start a new branch from an
up-to-date `main`.

Two parts: **research** the pantry lists first, **then build** the feature on top of them. Decided with Bryan on
2026-11-15.

## What this is for

Today ChefBot builds a recipe only from what the user typed or photographed, plus generic staples (butter, oil,
salt and pepper, herbs and spices, milk) and the cuisine's classic flavors. A user who photographs only the
groceries they just bought gets a thin recipe, because ChefBot can't see the rice, soy sauce or dried chiles
already in their cupboard.

**Pantry defaults** is an opt-in switch: when it's on and a cuisine is picked, ChefBot assumes the user also has
the staples a home cook of that cuisine usually keeps on hand (for Korean: short-grain rice, kimchi, soy sauce,
doenjang, gochujang, gochugaru, garlic and scallions, sesame oil). Background: `docs/research/FINDINGS.md`,
"About the added-cuisines run" (the "Pantry defaults" bullet).

## Part 1: research the pantry lists

`tools/cuisine_pantry.json` holds a **draft** list for each of the 73 selectable cuisines (its `_note` says how it
was made). 45 are cleaned up from each cuisine's researched `pantry_assumed` field in
`docs/research/results/*.json`. **The other 28 were written by Claude from general knowledge and are not
researched:** `us_any`, `us_cajun`, `us_creole`, `us_southern_soul`, `us_tex_mex`, `mx_any`, `mx_northern_baja`,
`mx_central_oaxacan`, `mx_yucatan`, `caribbean_any`, `caribbean_cuban`, `caribbean_puerto_rican`,
`caribbean_jamaican`, `brazilian`, `peruvian`, `argentinian`, `italy_any`, `northern_italy`,
`southern_sicilian_italy`, `french`, `spanish`, `greek`, `russian`, `moroccan_north_african`, `ethiopian`,
`egyptian`, `nigerian`, `senegalese`.

1. **Research those 28** with real sources (cookbooks by authors from the cuisine, food historians, reputable
   food writing; not recipe-aggregator SEO pages). For each: what does an ordinary home cook of this cuisine,
   cooking it at home (in the US or in the country, say which), keep on hand week to week? Correct, add to or cut
   the draft.
2. **Spot-check the other 45** against their research: the Asian lists were very short in the research
   (2 to 4 items, hedged), so they were filled out; check those especially.
3. Save your sources and notes as `docs/research/results/raw/pantry_defaults.md`, and add a short "About the
   pantry-defaults run" section to `docs/research/FINDINGS.md` (what changed from the draft and why).

**House style for every list** (the lists are shown to users and sent to the model):
- 6 to 10 items. Staples that keep (pantry, fridge door, freezer) and everyday aromatics: oils and fats, grains
  and starches, dried beans, sauces and pastes, vinegars, dried chiles and spices, onions, garlic, citrus. **Not**
  the main protein or fresh vegetables a dish is built around.
- English first, the native term in parentheses only when it helps a US shopper: `"chili bean paste (doubanjiang)"`.
- No brand names, no hedging ("in many households"), no notes or prose. Each item is a short noun phrase.
- An item may overlap the cuisine's classic flavors, but don't just repeat the flavor list.
- Respect each cuisine's `avoid` list in `tools/cuisine_overrides.json` (Cajun: never filé powder).

## Part 2: build it

### Data
- `tools/build_cuisine_data.py` reads `tools/cuisine_pantry.json` (skip the `_note` key) and writes a `pantry`
  list on every `cuisine` and `any` node. Remove any item matching the node's `avoid` list, as the builder already
  does for flavors. Rebuild with `.venv/bin/python tools/build_cuisine_data.py` and commit the generated
  `src/chefbot/cuisines/*.json`.

### The switch (home screen)
- In the "Pick a cuisine" card (`src/main.py`, `show_home`, the card with `self.cuisine_chips_row`), below the
  chips: a row with a switch labelled **"Pantry defaults"**, then an info button (`ft.Icons.INFO_OUTLINE`, the
  same look as the info buttons in the list browser, tooltip "About pantry defaults").
- Show the row only when a cuisine is picked (not "Anything"). Picking a cuisine updates it.
- Off by default. Remember it in a new pref, `PREF_PANTRY = "chefbot.pantry_defaults"` (`"on"`/`"off"`), added
  to `ALL_PREFS` and loaded with the others, like `PREF_MUST_NOT`.

### The info sheet (the (i) button)
A bottom sheet in the same style as `_cuisine_info` (`ft.BottomSheet`, drag handle, `heading(...)`, `MAX_WIDTH`):
- Heading "Pantry defaults".
- A short plain-language explanation, roughly: "Photographed only what you just bought? Turn this on and ChefBot
  assumes you also have the staples a [cuisine] home cook usually keeps in the cupboard. Anything it uses from
  this list is marked in the recipe, so you can check you have it. Your dietary needs and your 'Never use' list
  still come first."
- A section titled "With [chip label], ChefBot assumes you have" listing that cuisine's `pantry` items (as a
  bulleted list or one comma-separated line, matching `_cuisine_info_lines`'s `section()` style).
- Write the wording in Bryan's voice: plain, short, no exclamation marks, no emojis.

### The prompt
- `prompts.system_prompt(...)` gets a `pantry: bool = False` argument. When it's true and the node has a
  `pantry` list, add a paragraph near the staples sentence, roughly: "The user has turned on pantry defaults:
  assume they also have these staples a {name} home cook usually keeps on hand: {items}. Use any that suit the
  dish even though they aren't in the ingredients list, as supporting ingredients, not the main ones. In the
  ingredients list, mark each one you use with "(from your pantry)" so the user can check they have it." Keep
  the existing rule that dietary requirements and anything the user must not have override everything,
  including these items.
- When it's off, the prompt must be exactly what it is today (a test should check this).
- `start_recipe` passes the switch's value, stores `"pantry": True/False` in the conversation's `settings`, and
  adds a "Pantry defaults" tag to the request's display line when it's on. Old saved chats without the key
  behave as off.

### Tests (`tests/test_core.py`, offline)
- Every selectable leaf has a non-empty `pantry` of 6 to 10 short strings, no emojis, no brand names you
  removed, nothing from its `avoid` list.
- `system_prompt(..., pantry=True)` includes the items and the "(from your pantry)" instruction;
  `pantry=False` gives the same text as before the change.
- Run `.venv/bin/python -m pytest`; all tests pass.

### Check it in the app
Run `.venv/bin/flet run --web --port 8551 src/main.py` (restart after code changes; first load takes about 20 s;
Flutter draws on a canvas, so use screenshots). Check: the row hides for "Anything" and shows for a picked
cuisine, the switch survives a restart, the info sheet lists the right cuisine's items in dark and light themes,
and at phone width (375 px) the row doesn't wrap badly. Don't type the OpenRouter key into any field; if you need
a live recipe, ask Bryan to run one.

### Docs and PR
- `README.md` features: one line on pantry defaults.
- `HANDOFF.md`: replace the pantry-defaults Pinned note with what was built, and add a line under Bryan's
  preferences or Architecture if it helps the next session.
- Commit (messages end with the `Co-Authored-By` line for your model), push, open a PR into `main`, and confirm
  the GitHub Actions tests pass. Don't merge it.
