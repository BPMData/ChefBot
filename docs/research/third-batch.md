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
Three nodes, each a single cuisine. Use exactly these ids: us_new_england and us_italian_american (both regional cuisines within the United States), and roman_central_italy (Italy). New England (label "New England") replaces the app's existing "New England Seafood" node (fact-check below). Broaden it to the region's whole everyday cooking, not just the coast: seafood still, plus baked beans and brown bread, boiled dinner, johnnycakes, Indian pudding, maple, apples and cider, cranberries, and the Portuguese cooking of southeastern Massachusetts and Rhode Island. Say how much northern New England (Maine, New Hampshire, Vermont) differs from southern New England, what a recipe app should treat as the default, and keep clam-shack and lobster-pound tourist food apart from home cooking. Italian-American (label "Italian-American") is the Italian-American cooking of the New York City area only: the five boroughs, Long Island, Westchester and the lower Hudson Valley, northern and central New Jersey, and southwestern Connecticut (Fairfield and New Haven counties). Treat it as a regional American cuisine in its own right, not a failed copy of Italian food. Cover red-sauce home cooking (Sunday gravy, macaroni, chicken and eggplant parmigiana, baked ziti, stuffed shells, braciole, sausage and peppers, escarole and beans), the pork-store, salumeria and bakery traditions, pizza (the New York slice and New Haven apizza), the Feast of the Seven Fishes, and which Italian regions each dish comes from (mainly Campania, Sicily, Calabria, Puglia and Basilicata). Cover the local words (gravy versus sauce, macaroni for all pasta, mozz, gabagool and other dialect forms) and say which a recipe should use. The app's "Italian (Any)" node already describes the international image of Italian food (fact-check below): say clearly what belongs to this regional node instead. Roman & Central (label "Roman & Central") covers central Italy: Lazio and Rome, Umbria, Abruzzo and Marche, and possibly Tuscany. Northern Italy and Southern & Sicilian (Campania and Naples southward) are already researched; say how this cuisine differs from both. Cover Roman cooking in full (guanciale, pecorino romano, the four Roman pastas, quinto quarto offal, artichokes alla romana and alla giudia, Roman Jewish cooking), the shepherd and mountain cooking of Abruzzo, and Umbria's truffles, lentils and pork. Say in the summary whether Tuscany belongs in this node or should be its own, and why.

"Any" OPTIONS: none. Each node is a single cuisine.

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
New England Seafood
  Description: New England seafood cooking follows the cold Atlantic coast from Connecticut and Rhode Island through Massachusetts, New Hampshire and Maine, with ports, tidal flats and fishing towns central to the style. Indigenous coastal foodways, English colonial cooking, maritime trade and later immigrant fishing communities all contributed. New England clam chowder, lobster rolls, clambakes and baked or fried cod/haddock are representative.
  Classic flavors: black pepper, bay leaf, thyme, parsley, chives, onion, celery, lemon, mustard, Worcestershire sauce
  Signature ingredients: quahogs/hard clams (substitute: littleneck or canned clams for chowder), Maine/New England lobster (substitute: other cold-water lobster; shrimp only changes the dish substantially), salt cod (substitute: fresh cod plus added salt only for some preparations), haddock (substitute: cod or pollock)
Italian
  Description: This node deliberately represents the internationally recognized image of Italian food rather than a geographic region: pizza shops, red-sauce restaurants and diaspora kitchens made pasta, tomato sauce, garlic, basil and grated cheese global symbols of Italy. Much of this image was shaped by Italian migration to the Americas and later tourism and restaurant culture, so several famous dishes are export or Italian-American forms rather than everyday food across Italy. Representative dishes are spaghetti with meatballs, cream-style fettuccine Alfredo, pepperoni pizza and lasagna.
  Classic flavors: garlic (aglio), basil (basilico), oregano (origano), red chile flakes (peperoncino), parsley (prezzemolo), black pepper (pepe nero), olive oil (olio d'oliva), balsamic vinegar (aceto balsamico), anchovy (acciuga), rosemary (rosmarino)
  Dessert-only flavors: vanilla (vaniglia)
  Signature ingredients: Parmigiano-style hard cheese (substitute: supermarket Parmesan), fresh mozzarella (substitute: low-moisture mozzarella for baked dishes), prosciutto (substitute: thinly sliced cured ham), pancetta (substitute: unsmoked bacon if available; ordinary bacon is smokier), Arborio rice (substitute: another short-grain rice)
