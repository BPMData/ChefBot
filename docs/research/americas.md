You are researching regional cuisines for a recipe app whose AI writes
recipes from the user's own ingredients. Accuracy matters more than
breadth: every claim will be shown to users or used to steer recipes.

SCOPE: the nodes in this tree (branches and leaves).
- **The Americas:** United States (Cajun, Creole, Southern & Soul, Tex-Mex, New England Seafood, Any); Mexico (Northern & Baja, Central & Oaxacan, Yucatán, Any); Caribbean (Cuban, Puerto Rican, Jamaican, Any); Brazilian; Peruvian; Argentinian.

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
American
  Description: Home cooking from across the United States: smoky barbecue rubs, Chesapeake Bay seafood seasoned with Old Bay, and the warm baking spices of holiday tables. Generous, bold and unfussy.
  Classic flavors: black pepper, salt, garlic, onion, paprika, chili powder, cayenne pepper, cinnamon, oregano, vanilla extract and Old Bay
American (Cajun)
  Description: The country cooking of southern Louisiana's bayous and prairies, from the Acadians: French-speaking settlers expelled from eastern Canada in the 1750s. Rustic one-pot dishes such as gumbo, jambalaya and étouffée, built on a dark roux and the "holy trinity" of onion, celery and green bell pepper, with cayenne heat. Not the same as Creole, the city cooking of New Orleans, which uses more butter and tomatoes.
  Classic flavors: cayenne pepper, paprika, garlic, onion, green bell peppers, celery, bay leaves, thyme, oregano, and black and white pepper
American (Creole)
  Description: The city cooking of New Orleans, shaped by its French and Spanish colonial rulers, by West African and Caribbean cooks (many of them enslaved), and later by Italian and German immigrants. Richer and more refined than its country cousin Cajun, with more butter, cream and tomatoes on the same base of onion, celery and green bell pepper. Shrimp Creole, red beans and rice, grillades and grits, and the city's tomato-red jambalaya.
  Classic flavors: onion, celery and green bell peppers, garlic, butter, tomato paste, cayenne pepper, paprika, thyme, bay leaves, oregano, basil, parsley, green onions, black and white pepper, and Louisiana hot sauce
Mexican
  Description: Indigenous Mesoamerican foods (corn, chiles, beans, squash, cacao) blended with Spanish ingredients. Corn is nixtamalized for tortillas and masa; dried chiles are toasted and ground into sauces. Strongly regional, from Oaxaca's moles to the Yucatán's achiote.
  Classic flavors: chilies (chiles), cumin (comino), cilantro and coriander (cilantro y coriandro), Mexican oregano (orégano), garlic (ajo), epazote, chocolate, cinnamon (canela), annatto (achiote), and lime (limón)
Peruvian
  Description: Andean, coastal and Amazonian cooking mixed with Spanish, African, Chinese (chifa) and Japanese (Nikkei) influences. Built around ají chiles, hundreds of potatoes, and very fresh fish: ceviche, lomo saltado, ají de gallina.
  Classic flavors: ají amarillo, ají panca, cilantro (culantro), huacatay, cumin (comino), garlic (ajo), lime (limón), annatto (achiote), oregano (orégano), and ginger (kion)

OUTPUT: a short narrative summary of the biggest surprises and
disputes, then one JSON array with an object per node using exactly
the field names above. No emojis.
