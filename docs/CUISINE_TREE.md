# Planned: the cuisine tree

Status: planned (2026-11-08), not started. Replaces the flat list of cuisine chips with a drill-down by region.
The data for it comes from deep research runs (prompt below), not from a model's memory.

## Decisions

- **Drill-down, 1 to 3 levels.** Tap a continent, then a country or region, then (where it has them) a
  sub-style. A leaf picks the cuisine and closes the menu. On a phone: a modal with a back button and a
  breadcrumb ("Americas > Caribbean > Cuban").
- **"Any" on every country or region that has sub-styles**, meaning the internationally recognized version: what
  people outside that country think of as its food, not one regional sub-style picked at random. United States >
  Any is American food as people in Asia and Europe picture it (it keeps the current "American" list: Old Bay,
  vanilla, cinnamon). The research should still say where that outside view is a cliché or an export version.
- **No "Any" at the continent level** (there is no outsider's picture of "Asian food" to aim at). Surprise me
  covers that: it picks a random leaf.
- **Recent picks:** the last 4-5 cuisines as chips on the home screen, so a usual pick is one tap. The picked chip
  shows the path ("Caribbean · Cuban") and keeps the info icon.
- **One node shape everywhere:** `id`, `label` (max 20 characters, fits a chip), `subtitle` (the descriptor, e.g.
  "Mojo, sour orange, black beans", shown under the label, never part of it), and the prompt data: `about`,
  `flavors`, `sweet_only`, `signature_ingredients`, `pantry_assumed`, `shortcuts`, `allergen_notes`, `pitfalls`.
  Branches carry the data for their "Any" option.
- **Old saved chats** store cuisine labels like "Chinese (Hong Kong)": keep a map from old labels to new ids so the
  recent list still names them (Hong Kong folds into Cantonese).

## Taxonomy

- **The Americas:** United States (Cajun, Creole, Southern & Soul, Tex-Mex, New England Seafood, Any); Mexico
  (Northern & Baja, Central & Oaxacan, Yucatán, Any); Caribbean (Cuban, Puerto Rican, Jamaican, Any); Brazilian;
  Peruvian; Argentinian.
- **Asia:** China, the Eight Great Cuisines (Sichuan, Hunan, Cantonese, Shandong, Jiangsu, Zhejiang, Fujian,
  Anhui, Any); Japan (Kanto, Kansai, Any); India (North, South, Any); Korean; Thai; Vietnamese; Filipino;
  Indonesian; Malaysian & Singaporean.
- **Europe:** Italy (Northern, Southern & Sicilian, Any); French; Spanish; Greek; Central European (Germany,
  Austria, Czechia, Hungary, Poland); Russian.
- **Near & Middle East:** Palestinian & Levantine; Persian; Turkish.
- **Africa:** Moroccan & North African; Ethiopian; Egyptian; Nigerian; Senegalese.

## Research prompt

Run once per continent (one run for ~50 nodes comes back thin), then merge the JSON. Fill in the two bracketed
parts: the continent's piece of the taxonomy above, and the current `CUISINE_ABOUT` and `CUISINES` entries for
that continent from `src/chefbot/prompts.py`.

```
You are researching regional cuisines for a recipe app whose AI writes
recipes from the user's own ingredients. Accuracy matters more than
breadth: every claim will be shown to users or used to steer recipes.

SCOPE: the nodes in this tree (branches and leaves).
[PASTE ONE CONTINENT'S PART OF THE TAXONOMY HERE]

"Any" OPTIONS: every country or region with sub-styles also has an
"Any" option. "Any" means the internationally recognized version of that
country's food: what people outside the country think of when they think
of it (for the United States, American food as people in Asia and Europe
picture it). Research it as a node of its own. Say where that outside
view is a cliché, a stereotype, or an export version that differs from
home cooking, but describe the outside view itself accurately.

SOURCES: prefer recognized authorities on each cuisine (regional cookbook
authors with deep expertise, culinary historians, academic food studies,
national culinary institutions) over blogs and SEO recipe sites. Cite a
source for each history claim and each seasoning list. Where sources
disagree, say so and give both views. Mark anything you are unsure of
as LOW CONFIDENCE rather than smoothing it over.

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
13. sources: list with titles and authors or URLs.

Also fact-check these existing descriptions and flavor lists, and
mark each claim correct, wrong, or disputed, with a source:
[PASTE THE MATCHING CUISINE_ABOUT AND CUISINES ENTRIES]

OUTPUT: a short narrative summary of the biggest surprises and
disputes, then one JSON array with an object per node using exactly
the field names above. No emojis.
```
