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
- Africa, one new node: Tunisian. Moroccan, Egyptian, Ethiopian, Nigerian and Senegalese are already researched; say clearly how Tunisian cooking differs from Moroccan and Algerian cooking, and give harissa its full due (what goes in it, regional versions, how it is used).

"Any" OPTIONS: none. This is a single cuisine.

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
(None: the app has no existing entries for these cuisines yet. Skip the fact-check.)
