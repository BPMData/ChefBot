# Cuisine research prompt: Africa

Generated from `docs/CUISINE_TREE.md` and `src/chefbot/prompts.py` (2026-11-08). Paste everything below the line into a deep research tool.

---

You are researching regional cuisines for a recipe app whose AI writes
recipes from the user's own ingredients. Accuracy matters more than
breadth: every claim will be shown to users or used to steer recipes.

SCOPE: the nodes in this tree (branches and leaves).
- **Africa:** Moroccan & North African; Ethiopian; Egyptian; Nigerian; Senegalese.

"Any" OPTIONS: each node listed with an "Any" option has one; no other
node does. Caribbean > Any covers several countries: describe the shared
picture outsiders have, and note in pitfalls where islands differ and
would object to being lumped together. "Any" means the internationally recognized version of that
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
(None: the app has no cuisines from this continent yet. Skip this fact-check.)

OUTPUT: a short narrative summary of the biggest surprises and
disputes, then one JSON array with an object per node using exactly
the field names above. No emojis.
