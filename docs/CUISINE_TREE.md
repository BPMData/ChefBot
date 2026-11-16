# Planned: the cuisine tree

Status: planned (2026-11-08), not started. Replaces the flat list of cuisine chips with a drill-down by region.
The data for it comes from deep research runs (prompt below), not from a model's memory.

## Decisions

- **Drill-down, 1 to 3 levels.** Tap a continent, then a country or region, then (where it has them) a
  sub-style. A leaf picks the cuisine and closes the menu. On a phone: a modal with a back button and a
  breadcrumb ("Americas > Caribbean > Cuban").
- **"Any" only on country nodes that have sub-styles** (United States, Mexico, China, Japan, India, Italy), plus
  one exception, the Caribbean (several countries, but close enough that outsiders picture one cuisine),
  meaning the internationally recognized version: what people outside that country think of as its food, not one
  regional sub-style picked at random. United States >
  Any is American food as people in Asia and Europe picture it (it keeps the current "American" list: Old Bay,
  vanilla, cinnamon). The research should still say where that outside view is a cliché or an export version.
- **No "Any" anywhere else.** Not on continents (there is no "Asian food" to aim at) and not on other
  multi-country groupings. Leaves like Oaxacan are already specific.
  Surprise me covers "anything": it picks a random leaf.
- **Recent picks:** the last 4-5 cuisines as chips on the home screen, so a usual pick is one tap. The picked chip
  shows the path ("Caribbean · Cuban") and keeps the info icon.
- **One node shape everywhere:** `id`, `label` (max 20 characters, fits a chip), `subtitle` (the descriptor, e.g.
  "Mojo, sour orange, black beans", shown under the label, never part of it), and the prompt data: `about`,
  `flavors`, `sweet_only`, `signature_ingredients`, `pantry_assumed`, `shortcuts`, `allergen_notes`, `pitfalls`.
  Countries with sub-styles carry the data for their "Any" option.
- **Old saved chats** store cuisine labels like "Chinese (Hong Kong)": keep a map from old labels to new ids so the
  recent list still names them (Hong Kong folds into Cantonese).

## Taxonomy

- **The Americas:** United States (New Mexican, Hawaiian & Local, Cajun, Creole, Southern & Soul, Tex-Mex, New England,
  Italian-American, Any); Mexico
  (Northern & Baja, Central & Oaxacan, Yucatán, Any); Caribbean (Cuban, Puerto Rican, Jamaican, Any); Brazilian;
  Peruvian; Argentinian.
- **Asia:** China, the Eight Great Cuisines (Sichuan, Hunan, Cantonese, Shandong, Jiangsu, Zhejiang, Fujian,
  Anhui, Any); Japan (Kanto, Kansai, Any); India (North, South, Any); Korean; Thai; Vietnamese; Filipino;
  Indonesian; Malaysian & Singaporean; Afghan; Pakistani (added 2026-11-09; one node or two depending on what
  the research recommends).
- **Europe:** Italy (Northern, Roman & Central, Southern & Sicilian, Any); French; Spanish; Greek; Central European (Germany,
  Austria, Czechia, Hungary, Poland); Russian.
- **Near & Middle East:** Palestinian & Levantine; Persian; Turkish.
- **Africa:** Moroccan; Tunisian; Algerian; Ethiopian; Egyptian; Nigerian; Senegalese. ("Moroccan & North
  African" became Moroccan on the research's advice; Tunisian, for harissa, and Algerian were added 2026-11-09.)

### Second batch (decided 2026-11-13)

Fourteen more cuisines, now that the globe and maps make room. Prompts: `docs/research/additions-europe.md` and
`docs/research/additions-americas.md`. **Research done** (Antigravity runs, chosen from six):
`results/additions_europe.json`, `results/additions_americas.json`; notes and fixes in `research/FINDINGS.md`.

- **Europe:** Central European is **split** into German, Austrian, Hungarian, Polish and Czech. Also Portuguese,
  British, Irish (separate from British), Nordic (Finland stays in it), Georgian (under Europe).
- **The Americas:** Québécois (Canada), New Mexican and Hawaiian (under the United States), Colombian.
- **To do when the results are in:** the builder reads only `additions.json` today, so it needs the two new files
  and their placement; saved chats that used Central European need a mapping (as Hong Kong maps to Cantonese);
  each new node needs a map region (countries come free from the outlines; Hawaii and New Mexico need US state
  groupings).
- **Later candidates:** Tuscan (both third-batch runs say it is its own node); France and Spain as countries with regions; Barbecue, Lowcountry and
  Pacific Northwest (US); Chilean, Central American, Dominican, Haitian, Trinidadian; Balkan.

### Third batch (decided 2026-11-15, built 2026-11-15)

Three cuisines in one run. Prompt: `docs/research/third-batch.md` (`tools/make_research_prompts.py third-batch`).
**Research done (2026-11-15):** two runs (raw reports in `results/raw/third_batch_high.md` and
`third_batch_medium.md`). `results/third_batch.json` is the high run with fixes taken from the medium run; notes in
`research/FINDINGS.md`. Both runs say Tuscany should be its own node, so it is left out of Roman & Central.

- **New England** (`us_new_england`) replaces New England Seafood: the region's whole cooking, not just the coast.
  Saved chats with `us_new_england_seafood` need a `LEGACY_IDS` entry.
- **Italian-American** (`us_italian_american`, under the United States) is the New York City area only: the five
  boroughs, Long Island, Westchester and the lower Hudson Valley, northern and central NJ, and Fairfield and New
  Haven counties in CT (county outlines, like Cajun and Creole). The rest of CT stays New England; upstate NY,
  Philadelphia and Chicago are out (Bryan's call). Trim the Italian-American dishes out of Italian (Any) to match.
- **Roman & Central** (`roman_central_italy`): Lazio, Umbria, Abruzzo and Marche (Tuscany is a later candidate). Naples and Campania stay in Southern & Sicilian. Central Italy is blank on the map today.
- **Built (2026-11-15):** `tools/build_cuisine_data.py` reads `third_batch.json`; New England replaces New
  England Seafood in place, with `us_new_england_seafood` and "New England Seafood" in `LEGACY_IDS`. House-style
  fixes (tips without brand names or "LOW CONFIDENCE", tidier flavors) and the Italian (Any) fixes (no balsamic,
  speck or serrano for prosciutto, the Italian-American dishes moved out) are in `tools/cuisine_overrides.json`.
  Maps: NY, NJ and CT are drawn from county outlines; CT's 2025 Census file has planning regions, not counties,
  so Fairfield and New Haven became Western Connecticut, Greater Bridgeport and South Central Connecticut
  (Naugatuck Valley stays New England). Italy gets `IT_CENTRAL`. 73 leaves in all.

### Fourth batch (decided and built 2026-11-15)

Sixteen cuisines plus a new 6th continent (**Oceania**), bringing the tree to **89 leaves across 6 continents** (`src/chefbot/cuisines/oceania.json` added alongside the 5 existing files):

- **Oceania (`oceania`):** Australian (`australian`), New Zealander (`new_zealander`). First-class 6th continent on both the 3D globe and world map (`src/chefbot/maps/oceania.json`).
- **Asia (India):** West & Central India (`central_west_india` — Maharashtra, Gujarat, Rajasthan, Madhya Pradesh, Goa); Rajasthan moved out of North India's `about` override and map polygon set (`IN_CENTRAL_WEST`).
- **The Americas:** Venezuelan (`venezuelan`), Chilean (`chilean`), The Guianas (`guianas` — Guyana, Suriname, French Guiana), plus 4 new US nodes: Native American (`us_native_american`, distinguishing pre-colonial Three Sisters / manoomin / salmon traditions from post-reservation frybread, with Southwest/Plains/OK cluster polygons and a call-out chip), Pacific Northwest (`us_pacific_northwest`, WA & OR), Great Lakes (`us_great_lakes`, label <= 20 chars covering MN, WI, MI / Upper Midwest), and Appalachian (`us_appalachian`, WV & KY).
- **Near East:** Yemeni (`yemeni`), Iraqi (`iraqi`).
- **Africa:** South African (`south_african`), East African (`east_african`, Kenya & Tanzania / Swahili coast), Ghanaian (`ghanaian`), Central African (`central_african`, Congo Basin / Cameroon / Gabon belt).

All 16 include 9–10 researched `pantry` defaults (`tools/cuisine_pantry.json`), full `src/chefbot/maps/*.json` polygons and non-overlapping call-out chips, and citations in `docs/research/results/raw/fourth_batch.md` + `docs/research/FINDINGS.md`.

1. **Research (Bryan):** the five prompts in `docs/research/` are ready to paste whole (select all), one per continent, with the
   taxonomy and the current entries already filled in. Paste one into a deep research tool (for example
   claude.ai with Research turned on) and save the whole answer.
2. **House style (Claude, one continent per session):** bring an answer back to a session, uploaded as a file or
   pasted. Claude checks it, then turns it into ChefBot's entries in its house style.
3. **The UI** once the first continent's data is in, so the tree is built around real entries.
4. **The build:** `docs/REFACTOR_CUISINE_TREE.md` is a self-contained brief for a coding model (Google AI Studio
   first, then Claude reviews and fixes).

**UI idea to weigh then (Bryan):** the first level as a world map with each region shaded as one color band, tapped
anywhere in its band. The alternative is five tiles, each with a small outline of its region. Bands keep the map
feel and give each region a big tap target. To check: the Near East band is small next to Africa and Asia, and the
map needs to read clearly in both dark and light themes.

## Research prompt

Run once per continent (one run for ~50 nodes comes back thin). `tools/make_research_prompts.py` fills in the
bracketed parts (the continent's taxonomy, its "Any" rule, and the app's current entries for it) and writes
`docs/research/<continent>.md`. Rerun it after changing this template or the cuisines in `prompts.py`.

```
You are researching regional cuisines for a recipe app whose AI writes
recipes from the user's own ingredients. Accuracy matters more than
breadth: every claim will be shown to users or used to steer recipes.

REQUIRED OUTPUT (the app imports it, so do not skip or reshape it):
1. A short summary of the biggest surprises and disputes.
2. The fact-check described at the end.
3. One JSON array, in a code block, with one object per node, using
   exactly the 13 field names below. Write a fuller report as well if
   you like, but the JSON must come at the end and be complete for
   every node. No emojis.

SCOPE: the nodes in this tree (branches and leaves).
[TAXONOMY]

[ANY RULE]

SOURCES: prefer recognized authorities on each cuisine (regional cookbook
authors with deep expertise, culinary historians, academic food studies,
national culinary institutions) over blogs and SEO recipe sites. Give
full URLs in the JSON "sources" field: inline citation markers are lost
when the report is copied. Where sources disagree, say so and give both
views. Mark anything you are unsure of as LOW CONFIDENCE rather than
smoothing it over.

RULES, NOT ABSOLUTES: say "usually", "often" or "in classic versions"
unless the sources agree something is a firm rule. Write "never" or
"always" only when no tradition in that cuisine does otherwise, because
the app will enforce whatever you write as a hard rule.

FOR EACH NODE, return:
1. id: snake_case, stable.
2. label: what a phone chip shows, max 20 characters.
3. subtitle: max 6 words (e.g. "Mojo, sour orange, black beans").
4. about: 2-3 plain sentences: where it is (geography a non-expert can
   picture: rivers, coasts, mountains, cities), who shaped it (peoples,
   migrations, colonial or trade history), and its overall style. Name
   2-4 representative dishes.
5. flavors: the 8-12 seasonings, aromatics and condiments most
   characteristic of everyday savory cooking, each with the native name
   and a standard romanization (pinyin, Jyutping for Cantonese, Hepburn,
   Revised Romanization, etc.). Seasonings only, no main ingredients.
6. sweet_only: classic flavors used mainly in desserts or sweets
   (empty if none).
7. signature_ingredients: defining main ingredients a home cook outside
   the region may not have (e.g. wood ear mushrooms). For each, a
   substitute available in a typical US supermarket, or "none".
8. pantry_assumed: items a cook from this cuisine would always have
   (like kimchi in a Korean kitchen), if any.
9. techniques: 3-5 defining cooking methods.
10. shortcuts: common store-bought blends or pastes, what they usually
    contain, and how to swap them in by weight (salt in grams).
11. allergen_notes: hidden sources of the major US allergens (milk,
    egg, fish, shellfish, tree nuts, peanuts, wheat, soy, sesame) in
    this cuisine's common seasonings (e.g. fish sauce, shrimp paste,
    ghee, peanut-based sauces).
12. pitfalls: what an AI writing "authentic" recipes commonly gets
    wrong for this cuisine (confusions with neighbors, stereotypes,
    ingredients that don't belong, invented "traditions").
13. sources: full URLs (or title, author and year for books).

FACT-CHECK (required): mark each claim in these existing descriptions
and flavor lists as correct, wrong, or disputed, with a source:
[EXISTING]
```
