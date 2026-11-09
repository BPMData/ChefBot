# Regional Cuisines of the Americas for Ingredient-Driven Recipe Generation

## Biggest surprises and disputes

The strongest finding is that several popular “rules” are useful restaurant shorthand but unsafe as hard recipe-generation rules. The most important example is **Cajun versus Creole**: the rural-Cajun/urban-Creole distinction has historical value, and Creole cooking is more strongly associated with tomatoes, but historians of Louisiana food stress substantial overlap. “Cajun never uses tomato,” “Creole always uses tomato,” “Cajun always begins with dark roux,” and “Creole means richer, butterier Cajun” are all too rigid for an authenticity engine. Gumbo alone can be built around roux, okra, filé, or combinations of them. citeturn783817search7turn783817search1turn783817search2

A second major correction is **Mexican seasoning**. UNESCO's description of traditional Mexican cuisine centers maize, beans, chiles, nixtamalization, milpa agriculture, tortillas, tamales and other Indigenous continuities; it does not support treating cumin, chocolate, cinnamon or achiote as a universal national flavor quartet. Cumin is legitimate in Mexican cooking but markedly regional and disproportionately salient in Tex-Mex; achiote is especially important in the Yucatán and southeast; chocolate belongs in some moles but emphatically not all of them. Regional scholarship by Diana Kennedy, Zarela Martínez and others is much safer for recipe steering than a single national spice template. citeturn365737search0turn793941search12turn793941search14

The requested “Any” nodes need to be understood as **export-image classifiers rather than national culinary summaries**. The international picture of the United States strongly overweights burgers, hot dogs, pizza, barbecue and fast-food culture; Paul Freedman's history explicitly discusses how such foods came to stand for “American cuisine” despite a much broader regional reality. Likewise, the Mexican export image often mixes Mexican forms with Mexican-American/Tex-Mex forms, while the generic “Caribbean” export image leans unusually heavily on Jamaican jerk, tropical-fruit, rum and coconut imagery. citeturn931366search0turn793941search16turn793941search17

Peruvian cuisine also needs a more precise model than “fish, potatoes and ají.” Ceviche is genuinely central enough to have UNESCO recognition, but Peru spans coast, Andes and Amazon, and its established Chinese-Peruvian chifa and Japanese-Peruvian Nikkei traditions make **kion** (ginger) and **sillao** (soy sauce) valid Peruvian signals in the right context. They are not, however, universal seasonings for every Peruvian recipe. citeturn262761search0turn262761search33

One current allergen detail is easy to miss: under current FDA guidance, **coconut is no longer classified as one of the US major tree-nut allergens**, although coconut allergy still exists and products still need ingredient-level assessment. That affects the Caribbean and Brazilian allergen notes below. citeturn469190search0turn469190search1

## Research method and data conventions

For this dataset, “correct” in the fact-check means both factually supported **and appropriately scoped**. “Disputed” means the statement has a real historical or culinary basis but becomes misleading when generalized. “Wrong” means it would predictably steer the recipe model toward a false rule or an incorrectly categorized flavor. Louisiana claims were checked particularly against the Southern Foodways Alliance, the Historic New Orleans Collection and Smithsonian material; Mexican claims against UNESCO, the Library of Congress bibliography and specialist regional scholarship; Peruvian claims against UNESCO and Smithsonian foodways material. citeturn783817search7turn365737search0turn262761search0

Because these cuisines overwhelmingly use Latin-script languages, the “romanization” in the JSON normally repeats the native spelling; where English and Spanish/French/Portuguese names coexist, both are retained when useful. `pantry_assumed` is intentionally empty in many nodes: a claim that cooks “always” possess a particular ingredient is much harder to defend than a claim that an ingredient is common. For shortcuts containing salt, brand formulations vary too much for a defensible fixed salt number, so the reliable machine rule is to derive salt-equivalent from the package sodium: `salt_g ≈ sodium_mg × 0.00254`, then subtract that amount from separately added salt.

The parent nodes—The Americas, United States, Mexico and Caribbean—are deliberately conservative routing profiles. They should have less influence on ingredient choice than their children because the historical sources consistently show very strong regional differentiation: Mexican cuisine is explicitly described as a living community system with local variation, Black and Southern US foodways changed through migration, and Louisiana Creole foodways continually evolved rather than remaining a single fixed canon. citeturn365737search0turn342355search1turn931366search18

## Fact-check: American, Cajun and Creole

### American

| Existing claim | Verdict | Check |
|---|---|---|
| “Home cooking from across the United States” | **Disputed** | The phrase is reasonable, but the examples that follow are too geographically selective to represent US home cooking as a whole; American food is markedly regional and migration-shaped. citeturn931366search0turn931366search11 |
| “smoky barbecue rubs” | **Correct, regionally** | Barbecue is an important US food tradition, but techniques, meats and sauces vary dramatically by region; it should not become a universal American seasoning profile. |
| “Chesapeake Bay seafood seasoned with Old Bay” | **Correct, regionally** | Old Bay originated on the Chesapeake Bay and remains explicitly marketed as a Chesapeake/Maryland seafood seasoning. citeturn793941search1turn793941search3 |
| “warm baking spices of holiday tables” | **Correct but weak as a national descriptor** | Such baking traditions exist, but they say more about sweets/holidays than everyday American savory cooking. Smithsonian material on US food history emphasizes much broader regional and social change. citeturn931366search11 |
| “Generous, bold and unfussy” | **Disputed** | This is a subjective stereotype, not a defensible culinary rule. American cooking includes highly elaborate as well as deliberately simple traditions. citeturn931366search0 |
| black pepper | **Correct** | Common in savory US cooking, though not uniquely American. |
| salt | **Correct but non-distinctive** | Ubiquitous rather than characteristic enough to help discriminate this cuisine. |
| garlic | **Correct** | Common across many US regional and immigrant traditions. |
| onion | **Correct** | Common and broadly useful. |
| paprika | **Disputed as national** | Important in numerous rubs, spice blends and regional dishes but not a national defining flavor. |
| chili powder | **Disputed as national** | Strongly relevant to Southwestern/Tex-Mex and chili traditions, less useful as a whole-US marker. Smithsonian's Tex-Mex history specifically documents the chile/cumin restaurant tradition. citeturn793941search14turn793941search16 |
| cayenne pepper | **Disputed as national** | Important in Southern/Louisiana and other hot-seasoning traditions, but too regionally weighted for a national core. |
| cinnamon | **Wrong category** | Valid in American cooking, but predominantly a sweet/baking flavor in this context and better placed in `sweet_only`. |
| oregano | **Disputed as national** | Common through Italian American, Southwestern, Mediterranean and other traditions, but not a uniquely national signature. |
| vanilla extract | **Wrong category** | Classic in US desserts and baking, not an everyday savory flavor; it belongs in `sweet_only`. |
| Old Bay | **Wrong as a national classic flavor** | It is strongly Chesapeake/Maryland-associated, despite broad national availability. citeturn793941search1turn793941search6 |

### American (Cajun)

| Existing claim | Verdict | Check |
|---|---|---|
| “country cooking of southern Louisiana's bayous and prairies” | **Correct, with qualification** | The rural Acadiana framing is useful, although Cajun food is not confined to stereotypical bayou landscapes. The Historic New Orleans Collection describes the rural/urban Cajun-Creole distinction as useful but porous. citeturn783817search7 |
| “from the Acadians: French-speaking settlers expelled from eastern Canada in the 1750s” | **Correct but incomplete** | Acadian displacement is fundamental, but Cajun cuisine subsequently incorporated Indigenous, African, Spanish, German and other Louisiana influences; “from the Acadians” should not imply a purely Acadian/French food lineage. citeturn783817search0turn783817search7 |
| “Rustic one-pot dishes such as gumbo, jambalaya and étouffée” | **Mostly correct** | One-pot and practical country cooking is a useful tendency, not a mandatory form. citeturn783817search7 |
| “built on a dark roux” | **Wrong as a blanket rule** | Dark roux is extremely important, but gumbo can use different combinations of roux, okra and filé, and not every étouffée or Cajun preparation needs dark roux. citeturn783817search1 |
| “holy trinity of onion, celery and green bell pepper” | **Correct** | This is a well-established Louisiana aromatic base. citeturn783817search2 |
| “with cayenne heat” | **Disputed as a defining rule** | Cayenne is characteristic, but Cajun food is not necessarily aggressively hot and can rely heavily on black pepper, herbs and layered seasoning. |
| “Not the same as Creole” | **Correct** | They are distinguishable traditions, but they overlap substantially. citeturn783817search7 |
| “Creole [is] the city cooking of New Orleans” | **Disputed/oversimplified** | New Orleans is the principal association, but rural Creole communities and broader Louisiana Creole identities also exist. citeturn783817search7turn931366search18 |
| “Creole uses more butter” | **Disputed** | This is not a reliable hard separator. |
| “Creole uses more tomatoes” | **Mostly correct as a tendency** | Tomatoes are more strongly associated with New Orleans Creole dishes, but “Cajun no tomato / Creole tomato” is not absolute. citeturn783817search7 |
| cayenne pepper | **Correct** | Characteristic, but dosage should not be forced high. |
| paprika | **Correct** | Common in Louisiana seasoning mixtures. |
| garlic | **Correct** | Common aromatic. |
| onion | **Correct** | Core member of the trinity. citeturn783817search2 |
| green bell peppers | **Correct** | Core member of the trinity. citeturn783817search2 |
| celery | **Correct** | Core member of the trinity. citeturn783817search2 |
| bay leaves | **Correct** | Common in long-simmered Louisiana dishes. |
| thyme | **Correct** | Characteristic herb. |
| oregano | **Disputed as core** | It appears in Cajun seasoning and recipes but is less foundational than the trinity, garlic, thyme, bay and peppers. |
| black pepper | **Correct** | Strongly characteristic. |
| white pepper | **Correct, but not universal** | Common in Louisiana seasoning practice but should not be mandatory. |

### American (Creole)

| Existing claim | Verdict | Check |
|---|---|---|
| “city cooking of New Orleans” | **Mostly correct** | New Orleans is the cuisine's major center, but “urban only” erases rural Louisiana Creole communities. citeturn783817search7turn931366search18 |
| French and Spanish colonial rulers shaped it | **Correct** | These colonial histories are fundamental. citeturn931366search18 |
| West African and Caribbean cooks, many enslaved, shaped it | **Correct** | African and Afro-Creole knowledge was foundational; older cookbook narratives often minimized this. citeturn783817search6turn931366search18 |
| later Italian and German immigrants shaped it | **Correct** | Both became part of the New Orleans food landscape; Native American influence should also be named. citeturn783817search7 |
| “Richer and more refined than its country cousin Cajun” | **Wrong / historically loaded** | The “refined Creole versus rustic Cajun” opposition reproduces an old classed restaurant narrative and obscures Black working-class Creole traditions and overlap. citeturn783817search7turn931366search18 |
| “more butter, cream and tomatoes” | **Disputed** | Tomato is a useful tendency; butter and cream are not reliable defining separators. citeturn783817search7 |
| same onion-celery-bell-pepper base | **Correct, generally** | The trinity is widespread in both traditions. citeturn783817search2 |
| Shrimp Creole | **Correct** | Representative New Orleans Creole dish. |
| red beans and rice | **Correct** | Representative New Orleans food tradition. |
| grillades and grits | **Correct** | Representative Creole/New Orleans preparation. |
| “the city's tomato-red jambalaya” | **Correct as one important style, not universal** | Red jambalaya is strongly associated with New Orleans, but jambalaya also occurs in brown/non-tomato forms. citeturn783817search7 |
| onion | **Correct** | Core aromatic. |
| celery | **Correct** | Core aromatic. |
| green bell pepper | **Correct** | Core aromatic. |
| garlic | **Correct** | Characteristic. |
| butter | **Disputed as a “classic flavor”** | Used, but it is a cooking fat and milk allergen rather than a defining seasoning. |
| tomato paste | **Disputed in this exact form** | Tomato is characteristic of many Creole dishes; tomato paste specifically is not a universal canonical seasoning. |
| cayenne pepper | **Correct** | Characteristic but not obligatory. |
| paprika | **Correct** | Common in seasoning mixtures. |
| thyme | **Correct** | Characteristic herb. |
| bay leaves | **Correct** | Characteristic in simmered dishes. |
| oregano | **Disputed as core** | Used, but weaker as a defining signal than thyme/bay/trinity. |
| basil | **Disputed as core** | Legitimate in some Creole cooking, especially with Italian influence, but not a universal marker. |
| parsley | **Correct** | Common finishing/aromatic herb. |
| green onions | **Correct** | Common finishing aromatic. |
| black pepper | **Correct** | Common and characteristic. |
| white pepper | **Correct, but optional** | Common in Louisiana seasoning practice, not mandatory. |
| Louisiana hot sauce | **Correct as a common condiment** | Appropriate as an optional regional condiment rather than a required base flavor. |

## Fact-check: Mexican and Peruvian

### Mexican

| Existing claim | Verdict | Check |
|---|---|---|
| “Indigenous Mesoamerican foods (corn, chiles, beans, squash, cacao) blended with Spanish ingredients” | **Correct, broadly** | UNESCO identifies maize, beans and chile as core elements and explicitly describes Indigenous continuity alongside later additions. citeturn365737search0 |
| “Corn is nixtamalized for tortillas and masa” | **Correct** | Nixtamalization is a foundational documented process in traditional Mexican maize cookery. citeturn365737search0 |
| “dried chiles are toasted and ground into sauces” | **Correct, common rather than universal** | Toasting/grinding chile is a major technique across many regional sauces and moles. |
| “Strongly regional” | **Correct and important** | Specialist Mexican cookbooks and institutional sources repeatedly emphasize regional differences. citeturn793941search12turn793941search18 |
| “from Oaxaca's moles to the Yucatán's achiote” | **Correct** | Both are good examples of regional specificity; Oaxaca itself contains many cuisines, and Yucatán's recados make especially prominent use of achiote. citeturn449577search1turn449577search2 |
| chiles | **Correct** | Foundational across Mexican foodways. citeturn365737search0turn793941search24 |
| cumin / comino | **Disputed as national-core** | Legitimate Mexican spice, but its importance varies by region; cumin-forward seasoning is especially associated with Tex-Mex and northern/border repertoires. citeturn793941search14turn793941search23 |
| cilantro and coriander (“cilantro y coriandro”) | **Wrong / conflated** | Cilantro leaf is very common; coriander seed is a separate ingredient and substantially less useful as a universal Mexican marker. “Coriandro” also reads more like generic dictionary Spanish than the usual Mexican recipe distinction; `semilla de cilantro` is clearer for the seed. |
| Mexican oregano / orégano | **Correct** | Strong savory signal in many regions, though not every dish. |
| garlic / ajo | **Correct** | Widespread post-Conquest aromatic integrated deeply into Mexican cooking. |
| epazote | **Correct but regional/dish-specific** | A genuinely Mexican herb with strong use in beans, quesadillas and regional dishes, but not universal. |
| chocolate | **Disputed as a savory “classic flavor”** | Cacao is historically central, and chocolate appears in some moles, drinks and sweets, but treating it as a general savory seasoning causes the classic AI error “all mole = chocolate.” Oaxaca scholarship documents a far broader sauce repertoire. citeturn449577search1 |
| cinnamon / canela | **Disputed** | Important in Mexican sweets and drinks and legitimate in some savory moles/recados, but too sweet-associated to use as a default savory seasoning. |
| annatto / achiote | **Disputed as national-core** | Very important in Yucatán and parts of southeastern Mexico; much less useful as a countrywide default. citeturn449577search2 |
| lime / limón | **Correct** | A widely used condiment and acid, though it does not belong in every recipe. |

### Peruvian

| Existing claim | Verdict | Check |
|---|---|---|
| “Andean, coastal and Amazonian cooking” | **Correct** | Peru's culinary geography spans those ecological zones and should be modeled that way rather than as a purely coastal cuisine. citeturn262761search33 |
| Spanish influence | **Correct** | Colonial-era influence is foundational. |
| African influence | **Correct** | Afro-Peruvian foodways are a major component of the national culinary history. |
| Chinese/chifa influence | **Correct** | Chinese migration produced chifa, an established Peruvian tradition rather than a recent fusion category. citeturn262761search33 |
| Japanese/Nikkei influence | **Correct** | Japanese-Peruvian cooking is likewise an established strand of modern Peruvian cuisine. citeturn262761search33 |
| “Built around ají chiles” | **Correct as a broad tendency** | Ají varieties are among the strongest national flavor signals. |
| “hundreds of potatoes” | **Broadly correct but rhetorically imprecise** | Peru has extraordinary potato diversity, but the phrase is better treated as background biodiversity than a recipe-generation rule. |
| “very fresh fish” | **Disputed as national description** | Essential to coastal ceviche traditions, but it overgeneralizes the Andes and Amazon. UNESCO's ceviche inscription itself emphasizes regional/local variations. citeturn262761search0 |
| ceviche | **Correct** | Canonical and culturally significant enough to be inscribed by UNESCO. citeturn262761search0turn262761search2 |
| lomo saltado | **Correct** | Representative chifa-influenced national dish. |
| ají de gallina | **Correct** | Representative criollo dish. |
| ají amarillo | **Correct** | Major Peruvian chile signal. |
| ají panca | **Correct** | Major savory chile, especially for marinades and cooked sauces. |
| cilantro / culantro | **Correct** | `Culantro` is normal Peruvian Spanish for cilantro/coriander leaf; do not confuse it automatically with the Caribbean herb *Eryngium foetidum*. |
| huacatay | **Correct** | Distinctive Andean herb and strong regional marker. |
| cumin / comino | **Correct** | Common in many criollo, stew and meat preparations, though not universal. |
| garlic / ajo | **Correct** | Broadly characteristic. |
| lime / limón | **Correct** | Crucial to ceviche and many sauces/condiments; Peruvian `limón` is not always flavor-identical to the standard Persian lime sold in US supermarkets. citeturn262761search0 |
| annatto / achiote | **Disputed as top national flavor** | Legitimate in some Peruvian regions and dishes but less central nationally than the ají family; it should not displace rocoto or sillao in a compact flavor list. |
| oregano / orégano | **Correct** | Common in soups, stews, marinades and regional dishes. |
| ginger / kion | **Correct with scope** | A genuine Peruvian ingredient especially through chifa, Nikkei and many contemporary coastal preparations, but not a universal seasoning for traditional Andean or Amazonian dishes. citeturn262761search33 |

## Import dataset

The dataset below treats parent nodes as broad routers, uses the three `Any` records specifically for internationally recognizable export images, and keeps disputed or uncertain substitutions marked rather than pretending interchangeability. Exact packaged-product salt varies by manufacturer; when a shortcut mentions label sodium, the intended conversion is `salt_g ≈ sodium_mg × 0.00254`.

```json
[
  {
    "id": "the_americas",
    "label": "The Americas",
    "subtitle": "Corn, chiles, smoke, citrus",
    "about": "The Americas span Arctic coasts, temperate plains, tropical islands, mountains and rainforests, so there is no single pan-American cuisine. Indigenous foodways were transformed by European colonization, the Atlantic slave trade, Asian migration and later mass migration; maize, chiles, beans, cassava and many other native crops remained foundational in large areas. Representative cross-regional dishes include tamales, barbecue, feijoada and ceviche, but this node should be treated as a broad routing category rather than a recipe style.",
    "flavors": [
      "chile/chili — chile/chili — chile pepper",
      "ajo/garlic — ajo/garlic — garlic",
      "cebolla/onion — cebolla/onion — onion",
      "orégano/oregano — orégano/oregano — oregano",
      "comino/cumin — comino/cumin — cumin",
      "cilantro/coriander leaf — cilantro/coriander leaf — cilantro",
      "limón/lime — limón/lime — lime or sour citrus",
      "vinagre/vinegar — vinagre/vinegar — vinegar",
      "pimienta negra/black pepper — pimienta negra/black pepper — black pepper",
      "achiote/annatto — achiote/annatto — annatto"
    ],
    "sweet_only": [
      "vainilla/vanilla — vainilla/vanilla — vanilla, mainly sweet in many regions"
    ],
    "signature_ingredients": [
      "nixtamalized maize/masa — substitute: masa harina",
      "cassava/yuca products — substitute: potato only when texture, not identity, matters",
      "regional chile varieties — substitute: closest dried/fresh chile by heat and fruitiness, but expect flavor loss"
    ],
    "pantry_assumed": [],
    "techniques": [
      "nixtamalizing and grinding maize",
      "live-fire grilling, smoking and pit cooking",
      "stewing and braising",
      "frying",
      "acid marination and pickling"
    ],
    "shortcuts": [],
    "allergen_notes": [
      "No pan-American allergen profile is reliable. Common hidden risks across subregions include wheat/soy in commercial bouillon and soy sauce, fish in Worcestershire or fish sauce, shellfish in dried-shrimp seasonings, peanuts/tree nuts in some moles and sauces, and milk/egg in creamy bottled dressings."
    ],
    "pitfalls": "Do not turn this into a universal 'Latin' flavor profile: the United States, Mexico, the Caribbean and South America differ sharply, and Indigenous traditions differ even within countries. Avoid hard rules at this level; route to the narrowest child node available.",
    "sources": [
      "Sophie D. Coe, America's First Cuisines, 1994",
      "https://ich.unesco.org/en/RL/traditional-mexican-cuisine-ancestral-ongoing-community-culture-the-michoacan-paradigm-00400",
      "https://nmaahc.si.edu/explore/stories/black-foodways-and-cuisine",
      "https://ich.unesco.org/en/RL/practices-and-meanings-associated-with-the-preparation-and-consumption-of-ceviche-an-expression-of-peruvian-traditional-cuisine-01952"
    ]
  },
  {
    "id": "united_states",
    "label": "United States",
    "subtitle": "Regional, immigrant, Indigenous, diverse",
    "about": "The United States stretches from Atlantic and Gulf coasts through the Great Plains and Rockies to the Pacific, with Alaska and Hawai‘i adding still more distinct foodways. Native peoples, enslaved Africans, European colonists and successive migrations from Latin America, Asia and elsewhere shaped a highly regional cuisine; industrial food and restaurant culture later created national forms. Representative dishes include barbecue, fried chicken, clam chowder and hamburgers, but no seasoning set represents all US home cooking.",
    "flavors": [
      "black pepper — black pepper — black pepper",
      "garlic — garlic — garlic",
      "onion — onion — onion",
      "paprika — paprika — paprika",
      "chile powder — chile powder — blended ground chiles/spices",
      "mustard — mustard — prepared or dry mustard",
      "vinegar — vinegar — vinegar",
      "bay leaf — bay leaf — bay leaf",
      "oregano — oregano — oregano",
      "hot sauce — hot sauce — chile-vinegar sauce"
    ],
    "sweet_only": [
      "vanilla extract — vanilla extract — vanilla",
      "cinnamon — cinnamon — cinnamon"
    ],
    "signature_ingredients": [
      "regional smoked meats — substitute: supermarket smoked sausage or bacon when appropriate",
      "hominy/grits — substitute: polenta only for texture, not exact flavor",
      "regional chile products — substitute: closest available chile"
    ],
    "pantry_assumed": [],
    "techniques": [
      "grilling and barbecue/smoking",
      "roasting and baking",
      "pan- and deep-frying",
      "braising and slow cooking",
      "casserole and one-pot cooking"
    ],
    "shortcuts": [
      "Commercial barbecue rub: often salt, sugar, paprika, chile, garlic and onion; replace an equal weight of recipe dry rub and reduce added salt using salt_g ≈ sodium_mg × 0.00254 from the label. Commercial poultry/seasoned-salt blends vary too much for a national rule; use 1:1 by weight only after checking sodium and ingredient order."
    ],
    "allergen_notes": [
      "Worcestershire sauce commonly contains fish (anchovy). Soy sauce contains soy and often wheat. Ranch-style or creamy bottled seasonings can contain milk and egg; some barbecue sauces contain soy or wheat depending on brand. Peanut and tree-nut ingredients are regional rather than nationally characteristic."
    ],
    "pitfalls": "Do not equate US cuisine with fast food or with one Southern/Tex-Mex profile. 'American' restaurant exports overrepresent burgers, pizza, fried chicken, barbecue and sweet sauces, while home cooking is far more regional and immigrant-shaped.",
    "sources": [
      "Paul Freedman, American Cuisine: And How It Got This Way, 2019",
      "https://americanhistory.si.edu/explore/exhibitions/food",
      "https://www.si.edu/object/american-cuisine-and-how-it-got-way-paul-freedman:siris_sil_1115275",
      "Andrew F. Smith, ed., The Oxford Companion to American Food and Drink, 2007"
    ]
  },
  {
    "id": "us_cajun",
    "label": "Cajun",
    "subtitle": "Roux, trinity, smoke, cayenne",
    "about": "Cajun food is rooted in Acadiana, the bayous and prairies of southern Louisiana west and southwest of New Orleans. Acadian descendants mixed French traditions with Indigenous, African, Spanish, German and other local influences, using rice, pork, game and Gulf or swamp foods in practical country cooking. Gumbo, jambalaya, crawfish étouffée and boudin are representative; many, but not all, savory dishes begin with onion, celery and green bell pepper.",
    "flavors": [
      "oignon/onion — oignon/onion — onion",
      "céleri/celery — céleri/celery — celery",
      "poivron vert/green bell pepper — poivron vert/green bell pepper — green bell pepper",
      "ail/garlic — ail/garlic — garlic",
      "cayenne — cayenne — cayenne pepper",
      "paprika — paprika — paprika",
      "feuille de laurier/bay leaf — feuille de laurier/bay leaf — bay leaf",
      "thym/thyme — thym/thyme — thyme",
      "poivre noir/black pepper — poivre noir/black pepper — black pepper",
      "filé — filé — ground sassafras leaf"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      "andouille sausage — substitute: smoked kielbasa plus extra black pepper/cayenne",
      "tasso — substitute: smoked ham",
      "crawfish — substitute: shrimp, though flavor changes",
      "filé powder — substitute: none for its exact flavor; okra or roux can thicken by a different tradition"
    ],
    "pantry_assumed": [],
    "techniques": [
      "making roux from pale to very dark, depending on dish",
      "sweating the trinity",
      "one-pot simmering and braising",
      "rice cooking",
      "smoking/using smoked pork"
    ],
    "shortcuts": [
      "Jarred roux: typically flour cooked in fat; use roughly the same weight as finished roux called for, then thin into hot liquid. Cajun seasoning: often salt, paprika, cayenne, garlic/onion and herbs; replace the same weight of combined dry seasonings and reduce salt by salt_g ≈ sodium_mg × 0.00254 from the label."
    ],
    "allergen_notes": [
      "Worcestershire used in some Louisiana recipes contains fish (anchovy). Commercial stocks, bouillon and spice blends can contain wheat, soy or milk depending on brand. Shellfish is common in seafood gumbos and étouffées, but it is a main ingredient rather than a hidden seasoning."
    ],
    "pitfalls": "Do not require a dark roux in every Cajun dish; étouffées, fricassées and gumbos vary, and some gumbos are thickened with okra or filé. Do not enforce 'Cajun never uses tomatoes': tomato use is less associated with classic Cajun than Creole cooking, but the rural/urban and tomato/no-tomato divide is an oversimplification. Excessive cayenne is another stereotype; seasoning is often layered rather than simply hot.",
    "sources": [
      "https://folklife-media.si.edu/docs/festival/program-book-articles/FESTBK1985_05.pdf",
      "https://hnoc.org/publishing/first-draft/taste-creole-and-cajun-cuisine-10-stories",
      "https://www.southernfoodways.org/interview/a-short-history-of-gumbo/",
      "John D. Folse, The Encyclopedia of Cajun & Creole Cuisine, 2004"
    ]
  },
  {
    "id": "us_creole",
    "label": "Creole",
    "subtitle": "Tomato, trinity, herbs, sauces",
    "about": "Louisiana Creole cooking is most strongly associated with New Orleans and the lower Mississippi River/Gulf world, though Creole identity also exists in rural Louisiana. It developed through French and Spanish colonial rule and the cooking knowledge of African and Afro-Creole people, with Caribbean, Native American, German, Italian and other influences. Shrimp Creole, gumbo, red beans and rice, grillades and jambalaya are representative, and restaurant, home and working-class Creole traditions are not identical.",
    "flavors": [
      "onion — onion — onion",
      "celery — celery — celery",
      "green bell pepper — green bell pepper — green bell pepper",
      "garlic — garlic — garlic",
      "tomato — tomato — tomato paste or tomato",
      "cayenne — cayenne — cayenne pepper",
      "paprika — paprika — paprika",
      "thyme — thyme — thyme",
      "bay leaf — bay leaf — bay leaf",
      "parsley — parsley — parsley",
      "green onion — green onion — scallion",
      "Louisiana hot sauce — Louisiana hot sauce — vinegar chile sauce"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      "Creole mustard — substitute: Dijon plus a little whole-grain mustard",
      "andouille — substitute: smoked kielbasa",
      "tasso — substitute: smoked ham",
      "filé powder — substitute: none for exact flavor"
    ],
    "pantry_assumed": [],
    "techniques": [
      "roux-making",
      "sweating the trinity",
      "long simmering and braising",
      "sauce-making",
      "rice cookery"
    ],
    "shortcuts": [
      "Creole seasoning: usually salt, paprika, cayenne, garlic/onion and herbs; swap 1:1 by weight for the recipe's dry seasoning mix and reduce added salt from label sodium with salt_g ≈ sodium_mg × 0.00254. Bottled Creole mustard can replace prepared mustard 1:1 by weight but is sharper and grainier."
    ],
    "allergen_notes": [
      "Worcestershire sauce contains fish (anchovy). Remoulade commonly contains egg when mayonnaise-based and may contain fish via Worcestershire. Commercial stocks and spice blends may contain wheat, soy or milk depending on brand."
    ],
    "pitfalls": "Do not define Creole as simply 'fancy Cajun' or claim it always uses cream, butter or tomatoes. Historians emphasize overlap and continual change; New Orleans Creole cooking also includes Black working-class traditions. Red jambalaya is common in New Orleans, but jambalaya exists in many forms, including brown versions.",
    "sources": [
      "https://americanhistory.si.edu/explore/stories/300-years-and-counting-new-look-new-orleans-and-creole-cuisine",
      "https://folklife-media.si.edu/docs/festival/program-book-articles/FESTBK1985_05.pdf",
      "https://hnoc.org/publishing/first-draft/taste-creole-and-cajun-cuisine-10-stories",
      "Leah Chase, The Dooky Chase Cookbook, 1990"
    ]
  },
  {
    "id": "us_southern_soul",
    "label": "Southern & Soul",
    "subtitle": "Greens, corn, smoke, hot sauce",
    "about": "Southern food spans the Atlantic seaboard, Appalachia, the Deep South and Gulf states; soul food is a related African American tradition rooted especially in the South and carried nationwide during the Great Migrations. Indigenous crops and techniques, West and Central African knowledge, European settlement, enslavement and later migration all shaped these cuisines. Fried chicken, greens with potlikker, cornbread, Hoppin' John and barbecue are representative, but Southern food and soul food are overlapping rather than interchangeable.",
    "flavors": [
      "black pepper — black pepper — black pepper",
      "cayenne — cayenne — cayenne pepper",
      "hot sauce — hot sauce — vinegar chile sauce",
      "garlic — garlic — garlic",
      "onion — onion — onion",
      "smoked paprika — smoked paprika — smoked paprika",
      "mustard — mustard — mustard",
      "vinegar — vinegar — vinegar",
      "bay leaf — bay leaf — bay leaf",
      "thyme — thyme — thyme"
    ],
    "sweet_only": [
      "vanilla — vanilla — vanilla",
      "cinnamon — cinnamon — cinnamon",
      "nutmeg — nutmeg — nutmeg"
    ],
    "signature_ingredients": [
      "stone-ground grits — substitute: coarse polenta, with flavor/texture loss",
      "country ham — substitute: prosciutto plus a little smoke, or smoked ham",
      "sorghum syrup — substitute: molasses, sweeter and stronger",
      "benne seeds — substitute: sesame seeds"
    ],
    "pantry_assumed": [],
    "techniques": [
      "slow-simmering greens and legumes",
      "cornbread and biscuit baking",
      "frying",
      "barbecue/smoking",
      "braising"
    ],
    "shortcuts": [
      "Seasoned salt: replace the same weight of recipe salt-plus-spices, but calculate its salt from label sodium (salt_g ≈ sodium_mg × 0.00254). Bottled hot sauce can replace vinegar plus cayenne only approximately; start around 1:1 by weight with the vinegar component and reduce separately added cayenne to taste."
    ],
    "allergen_notes": [
      "Worcestershire contains fish. Some bottled barbecue sauces and bouillon contain soy or wheat; creamy dressings contain milk/egg. Peanut oil and peanuts appear in some Southern cooking, and sesame/benne is traditional in parts of the coastal South."
    ],
    "pitfalls": "Do not reduce soul food to 'slave scraps' or portray it as uniformly unhealthy; scholarship documents skilled Black cooks, agriculture, entrepreneurship and celebration. Do not merge all Southern barbecue into one sauce or meat style, and do not assume every Southern dish belongs specifically to soul food.",
    "sources": [
      "Adrian Miller, Soul Food: The Surprising Story of an American Cuisine, One Plate at a Time, 2013",
      "Toni Tipton-Martin, Jubilee: Recipes from Two Centuries of African American Cooking, 2019",
      "https://nmaahc.si.edu/foodways",
      "https://www.southernfoodways.org/oral-history/southern-bbq-trail/"
    ]
  },
  {
    "id": "us_tex_mex",
    "label": "Tex-Mex",
    "subtitle": "Chile gravy, cumin, cheese, tortillas",
    "about": "Tex-Mex developed in Texas, especially San Antonio and South Texas, from long-standing Mexican and Tejano foodways interacting with Anglo-American commerce and later restaurant culture. It is a Mexican American regional cuisine, not a mistaken version of Mexican food. Chili con carne, cheese enchiladas with chile gravy, nachos, breakfast tacos and fajitas are representative.",
    "flavors": [
      "comino — comino — cumin",
      "chile ancho — chile ancho — ancho chile",
      "chile en polvo — chile en polvo — chile powder blend",
      "ajo — ajo — garlic",
      "cebolla — cebolla — onion",
      "orégano — orégano — oregano",
      "pimentón/paprika — pimentón/paprika — paprika",
      "cilantro — cilantro — cilantro",
      "jalapeño — jalapeño — jalapeño chile",
      "lima/limón — lima/limón — lime"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      "yellow or processed melting cheese — substitute: mild cheddar plus Monterey Jack",
      "masa harina — substitute: fresh masa; no close wheat substitute",
      "dried ancho chiles — substitute: mild New Mexico dried chile",
      "Mexican chorizo — substitute: fresh pork sausage seasoned with chile, vinegar and garlic"
    ],
    "pantry_assumed": [],
    "techniques": [
      "griddling tortillas",
      "simmering chile gravy and chili",
      "broiling or baking enchiladas",
      "grilling fajita meats",
      "frying tacos/chips"
    ],
    "shortcuts": [
      "Commercial chili powder: usually ground chile plus cumin, oregano, garlic and sometimes salt; replace the same weight of those dry spices, then adjust salt from sodium. Taco seasoning packets: often chile, cumin, garlic/onion, starch and substantial salt; use about 8–10 g per 450 g meat as a starting shortcut, LOW CONFIDENCE because brands vary; subtract label-derived salt."
    ],
    "allergen_notes": [
      "Flour tortillas contain wheat. Cheese and queso contain milk. Commercial taco/chili seasonings may contain wheat, soy or milk depending on brand; some Worcestershire-containing marinades add fish."
    ],
    "pitfalls": "Do not 'correct' Tex-Mex into interior Mexican cuisine: yellow cheese, cumin-forward chile gravy, combination plates and crispy tacos have their own regional history. Conversely, do not label every burrito, chimichanga or fish taco Tex-Mex; some were popularized in other US-Mexican regional traditions.",
    "sources": [
      "Robb Walsh, The Tex-Mex Cookbook, 2004",
      "https://americanhistory.si.edu/explore/exhibitions/food/online/resetting-table/mexican-food-revolution/tex-mex-invasion",
      "https://www.si.edu/object/tex-mex-cookbook-history-recipes-and-photos-robb-walsh:siris_sil_1174732",
      "https://folklife-media.si.edu/docs/festival/program-book-articles/FESTBK2008_14.pdf"
    ]
  },
  {
    "id": "us_new_england_seafood",
    "label": "New England Seafood",
    "subtitle": "Clams, lobster, butter, herbs",
    "about": "New England seafood cooking follows the cold Atlantic coast from Connecticut and Rhode Island through Massachusetts, New Hampshire and Maine, with ports, tidal flats and fishing towns central to the style. Indigenous coastal foodways, English colonial cooking, maritime trade and later immigrant fishing communities all contributed. New England clam chowder, lobster rolls, clambakes and baked or fried cod/haddock are representative.",
    "flavors": [
      "black pepper — black pepper — black pepper",
      "bay leaf — bay leaf — bay leaf",
      "thyme — thyme — thyme",
      "parsley — parsley — parsley",
      "chives — chives — chives",
      "onion — onion — onion",
      "celery — celery — celery",
      "lemon — lemon — lemon",
      "mustard — mustard — mustard",
      "Worcestershire sauce — Worcestershire sauce — savory anchovy sauce"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      "quahogs/hard clams — substitute: littleneck or canned clams for chowder",
      "Maine/New England lobster — substitute: other cold-water lobster; shrimp only changes the dish substantially",
      "salt cod — substitute: fresh cod plus added salt only for some preparations",
      "haddock — substitute: cod or pollock"
    ],
    "pantry_assumed": [],
    "techniques": [
      "steaming shellfish",
      "chowder simmering",
      "clambake-style steaming over hot stones/seaweed or modern covered-pot analogs",
      "baking/broiling fish",
      "frying seafood"
    ],
    "shortcuts": [
      "Canned clam broth/juice can replace homemade clam liquor by equal weight, but taste for salt. Seafood seasoning blends can replace the recipe's dry spice mix 1:1 by weight only if flavor profile fits; subtract label-derived salt using salt_g ≈ sodium_mg × 0.00254."
    ],
    "allergen_notes": [
      "Fish and shellfish are central allergens. Worcestershire contains fish. Chowders often contain milk/cream and sometimes butter; lobster-roll dressing commonly contains egg via mayonnaise. Breaded fried seafood and rolls contain wheat."
    ],
    "pitfalls": "Do not assume every chowder is cream-thickened: Rhode Island clear chowders and tomato-based styles exist in the wider region. Do not turn every seafood dish into Old Bay/Chesapeake seasoning; that profile belongs more strongly to the Mid-Atlantic. Avoid overcooking lobster and clams.",
    "sources": [
      "https://www.loc.gov/folklife/maritime/onefood.html",
      "https://www.maine.gov/sos/maineatlas/explore-the-atlas/lobster-roll",
      "Jasper White, 50 Chowders, 2000",
      "Brooke Dojny, The New England Cookbook, 1999"
    ]
  },
  {
    "id": "us_any",
    "label": "Any",
    "subtitle": "Burgers, barbecue, fried chicken",
    "about": "Outside the United States, 'American food' is often pictured through nationally exported restaurant and media forms rather than regional home cooking: burgers, hot dogs, pizza, barbecue, fried chicken, steaks and diner-style comfort food. That image grew alongside mass production, fast-food systems and postwar restaurant culture, but it is a cliché of a much more diverse country. Representative export-image dishes include hamburgers, hot dogs, barbecue ribs and fried chicken.",
    "flavors": [
      "black pepper — black pepper — black pepper",
      "garlic powder — garlic powder — garlic powder",
      "onion powder — onion powder — onion powder",
      "paprika — paprika — paprika",
      "chili powder — chili powder — chile-spice blend",
      "mustard — mustard — mustard",
      "ketchup — ketchup — tomato condiment",
      "barbecue sauce — barbecue sauce — sweet-tangy sauce",
      "hot sauce — hot sauce — chile-vinegar sauce",
      "pickle relish — pickle relish — sweet/sour pickle condiment"
    ],
    "sweet_only": [
      "vanilla extract — vanilla extract — vanilla",
      "cinnamon — cinnamon — cinnamon"
    ],
    "signature_ingredients": [
      "American-style processed cheese — substitute: mild cheddar plus Monterey Jack",
      "liquid smoke — substitute: smoked paprika for aroma only, not true smoke",
      "cornmeal grits — substitute: coarse polenta"
    ],
    "pantry_assumed": [],
    "techniques": [
      "grilling",
      "deep-frying",
      "smoking/barbecue",
      "griddle cooking",
      "baking"
    ],
    "shortcuts": [
      "Bottled barbecue sauce can replace a homemade sweet-tart barbecue glaze 1:1 by weight, but reduce added sugar, vinegar and salt after tasting. Burger/grill seasoning blends can replace combined salt/spices 1:1 by weight; derive salt from sodium on the label."
    ],
    "allergen_notes": [
      "Processed cheese contains milk. Burger buns and pizza crust contain wheat; mayonnaise-based sauces contain egg. Worcestershire in burger or barbecue sauces contains fish; soy sauce in some barbecue sauces adds soy and often wheat. Peanut-containing desserts and peanut oil occur but are not universal."
    ],
    "pitfalls": "Treat this as the international export stereotype, not a claim about what Americans usually cook at home. Do not force Old Bay, ranch, maple syrup or bacon into unrelated dishes merely because they read as 'American.' Pizza in this node means Americanized pizza styles, not Italian cuisine.",
    "sources": [
      "Paul Freedman, American Cuisine: And How It Got This Way, 2019",
      "https://www.si.edu/object/american-cuisine-and-how-it-got-way-paul-freedman:siris_sil_1115275",
      "https://blogs.loc.gov/inside_adams/2010/05/mcdonald%E2%80%99s-bar-b-que/",
      "https://americanhistory.si.edu/explore/exhibitions/food"
    ]
  },
  {
    "id": "mexico",
    "label": "Mexico",
    "subtitle": "Maize, chiles, beans, regional sauces",
    "about": "Mexico spans northern deserts, central highlands, tropical Gulf and Pacific coasts and the Yucatán Peninsula, and its food is intensely regional. Indigenous Mesoamerican systems centered on maize, beans, squash and chiles combined with ingredients and techniques introduced under Spanish colonial rule and later migrations. Tortillas, tamales, pozole and mole are representative national forms, but their ingredients and methods vary widely by region.",
    "flavors": [
      "chile — chile — chile pepper",
      "ajo — ajo — garlic",
      "cebolla — cebolla — onion",
      "orégano mexicano — orégano mexicano — Mexican oregano",
      "cilantro — cilantro — cilantro",
      "epazote — epazote — epazote",
      "achiote — achiote — annatto",
      "limón — limón — Mexican lime",
      "comino — comino — cumin, regionally important rather than universal",
      "canela — canela — Mexican/Ceylon cinnamon, savory in some moles"
    ],
    "sweet_only": [
      "vainilla — vainilla — vanilla, mainly sweet though not exclusively",
      "canela — canela — cinnamon, often sweet though also savory"
    ],
    "signature_ingredients": [
      "masa/nixtamalized maize — substitute: masa harina",
      "tomatillo — substitute: canned tomatillos; green tomato plus lime is only a rough fallback",
      "fresh and dried Mexican chiles — substitute: closest chile by heat, fruitiness and smoke",
      "hoja santa — substitute: none; fennel leaf plus tarragon is only a flavor approximation"
    ],
    "pantry_assumed": [],
    "techniques": [
      "nixtamalizing and grinding maize",
      "toasting and grinding chiles/spices",
      "comal roasting",
      "simmering and frying sauces",
      "steaming tamales"
    ],
    "shortcuts": [
      "Achiote paste: usually annatto with garlic, spices, acid and salt; for 10 g homemade annatto-spice paste use about 10 g commercial paste, then reduce added salt from label sodium. Prepared mole paste can replace homemade mole base only recipe-by-recipe; start about 1:1 by weight for the concentrated paste specified, then thin according to label or recipe. Commercial adobo/seasoning powders vary; use 1:1 by weight only with salt correction."
    ],
    "allergen_notes": [
      "Mole and pipián may contain peanuts, sesame and/or tree nuts. Commercial bouillon may contain wheat, soy or milk. Some modern bottled sauces contain soy; dairy is common in garnishes but not a hidden universal seasoning."
    ],
    "pitfalls": "Do not treat cumin as the defining national Mexican spice; its prominence varies and is often exaggerated by Tex-Mex templates. Do not assume all tortillas are flour, all food is very hot, or all moles contain chocolate. Regional chile choices matter and are not interchangeable without changing the dish.",
    "sources": [
      "https://ich.unesco.org/en/RL/traditional-mexican-cuisine-ancestral-ongoing-community-culture-the-michoacan-paradigm-00400",
      "Diana Kennedy, The Essential Cuisines of Mexico, 2000",
      "Jeffrey M. Pilcher, Planet Taco: A Global History of Mexican Food, 2012",
      "https://guides.loc.gov/bibliografia-anotada-alimentacion/paises/mexico"
    ]
  },
  {
    "id": "mx_northern_baja",
    "label": "Northern & Baja",
    "subtitle": "Wheat, grilled meat, seafood, chiles",
    "about": "Northern Mexico covers arid border states such as Sonora, Chihuahua, Coahuila and Nuevo León, while Baja California is a long Pacific/Gulf peninsula with strong fishing and border-city traditions. Indigenous foodways, Spanish ranching and wheat agriculture, cattle culture, border exchange and in Baja later Asian and Mediterranean influences all matter. Carne asada, flour tortillas, machaca and cabrito are northern signatures; Baja fish tacos and seafood tostadas represent the peninsula.",
    "flavors": [
      "chiltepin — chiltepín — chiltepin chile",
      "chile colorado — chile colorado — dried red chile",
      "ajo — ajo — garlic",
      "cebolla — cebolla — onion",
      "orégano mexicano — orégano mexicano — Mexican oregano",
      "comino — comino — cumin",
      "cilantro — cilantro — cilantro",
      "limón — limón — lime",
      "vinagre — vinagre — vinegar",
      "pimienta negra — pimienta negra — black pepper"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      "large Sonoran-style flour tortillas — substitute: thin burrito-size flour tortillas",
      "chiltepin — substitute: pequin chile, then crushed red pepper as rough fallback",
      "machaca — substitute: shredded dried beef or jerky rehydrated, LOW CONFIDENCE",
      "fresh Pacific shellfish — substitute: locally fresh shrimp, scallops or white fish"
    ],
    "pantry_assumed": [],
    "techniques": [
      "charcoal/live-fire grilling",
      "flour-tortilla griddling",
      "drying and rehydrating meat",
      "frying fish/tacos",
      "raw or lightly cured seafood preparations"
    ],
    "shortcuts": [
      "Carne-asada seasoning: often salt, garlic, pepper, chile/cumin; use equal weight for the recipe's dry seasoning and reduce salt from label sodium. Bottled hot sauce or salsa can stand in for a simple chile-acid table sauce 1:1 by weight, but not for a cooked salsa with specific chiles."
    ],
    "allergen_notes": [
      "Flour tortillas contain wheat. Baja fried-fish batters contain wheat and sometimes egg; creamy taco sauces often contain egg via mayonnaise and may contain milk. Soy sauce, used in some Baja/border marinades, contains soy and often wheat; shellfish is common on the peninsula."
    ],
    "pitfalls": "Do not collapse northern Mexico into Tex-Mex: cumin and yellow cheese should not be automatic. Northern Mexico itself is diverse, and Baja seafood is not simply 'carne asada by the sea.' The claim that flour tortillas are 'inauthentic Mexican' is wrong in northern regions, where wheat has a long history.",
    "sources": [
      "https://www.loc.gov/folklife/guides/Mexico.html",
      "Diana Kennedy, My Mexico: A Culinary Odyssey with More Than 300 Recipes, 1998",
      "Rosa Yocupicio Buitimea, Recetario indígena de Sonora, 2000",
      "Javier Plascencia & others, The Baja California Cookbook, 2019"
    ]
  },
  {
    "id": "mx_central_oaxacan",
    "label": "Central & Oaxacan",
    "subtitle": "Masa, moles, herbs, dried chiles",
    "about": "This node combines the central Mexican highlands with Oaxaca to the south, so it contains multiple Indigenous and mestizo cuisines rather than one style. Central markets and maize cookery connect with Oaxaca's exceptionally diverse Zapotec, Mixtec and other Indigenous traditions, alongside Afro-Mexican and Spanish influences. Tacos and tlacoyos, pozole, mole poblano, mole negro, tlayudas and memelas are representative across parts of this broad zone.",
    "flavors": [
      "chile guajillo — chile guajillo — guajillo chile",
      "chile ancho — chile ancho — ancho chile",
      "chile pasilla — chile pasilla — pasilla chile",
      "ajo — ajo — garlic",
      "cebolla — cebolla — onion",
      "epazote — epazote — epazote",
      "hoja santa — hoja santa — hoja santa",
      "orégano mexicano — orégano mexicano — Mexican oregano",
      "canela — canela — Mexican/Ceylon cinnamon",
      "clavo — clavo — clove",
      "semilla de cilantro — semilla de cilantro — coriander seed"
    ],
    "sweet_only": [
      "vainilla — vainilla — vanilla",
      "canela — canela — cinnamon, although it also enters savory moles"
    ],
    "signature_ingredients": [
      "chilhuacle chiles — substitute: ancho plus pasilla; not exact",
      "hoja santa — substitute: none; fennel/tarragon approximation only",
      "quesillo/Oaxaca cheese — substitute: low-moisture mozzarella",
      "masa fresca — substitute: reconstituted masa harina"
    ],
    "pantry_assumed": [],
    "techniques": [
      "comal-roasting and charring",
      "toasting/grinding chiles, seeds and spices",
      "nixtamalizing and shaping masa",
      "frying and simmering sauces",
      "clay-pot or slow braising"
    ],
    "shortcuts": [
      "Prepared mole paste: use as the recipe's concentrated mole base by weight, commonly diluted several-fold; because brands vary greatly, follow the package ratio and treat salt/sugar as already present. Jarred salsa can replace a simple table salsa 1:1 by weight only when its chile and roast profile match."
    ],
    "allergen_notes": [
      "Moles and pipianes commonly can contain peanuts, sesame and tree nuts; some contain wheat bread/tortilla as thickener. Commercial mole pastes may also contain soy. Quesillo and crema contain milk."
    ],
    "pitfalls": "Do not market Oaxaca as 'the land of seven moles' as if there were only seven; the cuisine is much more diverse. Do not assume every mole contains chocolate or is sweet. This combined node can hide major differences between Puebla/Mexico City/central highlands and Oaxaca, so use dish-specific chile and herb choices.",
    "sources": [
      "Diana Kennedy, Oaxaca al Gusto: An Infinite Gastronomy, 2010",
      "https://utpress.utexas.edu/9780292722668/",
      "Zarela Martínez, The Food and Life of Oaxaca, 1997",
      "https://festival.si.edu/blog/bricia-lopez-oaxacalifornia"
    ]
  },
  {
    "id": "mx_yucatan",
    "label": "Yucatán",
    "subtitle": "Achiote, sour orange, habanero",
    "about": "The Yucatán Peninsula sits between the Gulf of Mexico and Caribbean, centered on the states of Yucatán, Campeche and Quintana Roo. Maya culinary foundations mix with Spanish colonial, Caribbean, Middle Eastern and other immigrant influences; underground pit cooking and recados are especially distinctive. Cochinita pibil, relleno negro, sopa de lima and papadzules are representative.",
    "flavors": [
      "achiote — achiote — annatto",
      "naranja agria — naranja agria — sour orange",
      "chile habanero — chile habanero — habanero chile",
      "orégano yucateco — orégano yucateco — Yucatecan oregano",
      "ajo — ajo — garlic",
      "pimienta gorda — pimienta gorda — allspice",
      "comino — comino — cumin",
      "clavo — clavo — clove",
      "canela — canela — cinnamon",
      "epazote — epazote — epazote"
    ],
    "sweet_only": [
      "vainilla — vainilla — vanilla"
    ],
    "signature_ingredients": [
      "Seville/sour orange — substitute: roughly equal parts orange and lime juice, then adjust acidity",
      "banana leaves — substitute: parchment plus foil for enclosure, but aroma is lost",
      "xcatic chile — substitute: Anaheim plus a little habanero",
      "achiote seeds/paste — substitute: annatto powder; paprika gives color but not flavor"
    ],
    "pantry_assumed": [],
    "techniques": [
      "pib/earth-oven roasting or wrapped slow roasting",
      "grinding recados",
      "char-roasting chiles and aromatics",
      "simmering stews and black recado dishes",
      "tortilla and masa cookery"
    ],
    "shortcuts": [
      "Commercial recado rojo/achiote paste: replace homemade recado 1:1 by weight as a starting point, then reduce salt and acid because brands vary. For sour-orange marinade, bottled naranja agria can replace fresh juice 1:1 by weight; check salt if seasoned. Salt correction: salt_g ≈ sodium_mg × 0.00254."
    ],
    "allergen_notes": [
      "Commercial recados and bouillon may contain wheat, soy or other allergens depending on brand. Pepita-based sauces contain pumpkin seed, which is not one of the nine major US allergens but can still cause allergy. Some papadzul-like or modern sauces may add dairy, but milk is not a defining hidden seasoning."
    ],
    "pitfalls": "Do not replace achiote with generic chili powder or make cochinita simply 'spicy pulled pork.' Habanero is often served in salsa or condiment form rather than making every dish searingly hot. Yucatecan cuisine is not merely Mexican food plus citrus; recados, Maya techniques and local herbs matter.",
    "sources": [
      "David Sterling, Yucatán: Recipes from a Culinary Expedition, 2014",
      "https://utpress.utexas.edu/9780292735811/",
      "Diana Kennedy, The Essential Cuisines of Mexico, 2000"
    ]
  },
  {
    "id": "mx_any",
    "label": "Any",
    "subtitle": "Tacos, salsa, chiles, lime",
    "about": "Outside Mexico, the internationally recognized picture centers on tacos, tortillas, salsa, guacamole, enchiladas and chile-forward sauces. That image mixes genuine Mexican national forms with restaurant exports and, especially in the United States and Europe, Tex-Mex elements such as heavy cumin, yellow cheese and hard-shell combination plates. Representative export-image dishes are tacos, enchiladas, guacamole and salsa, but the real national cuisine is far more regionally specific.",
    "flavors": [
      "chile — chile — chile pepper",
      "ajo — ajo — garlic",
      "cebolla — cebolla — onion",
      "cilantro — cilantro — cilantro",
      "limón — limón — lime",
      "orégano mexicano — orégano mexicano — Mexican oregano",
      "comino — comino — cumin, overrepresented abroad",
      "jalapeño — jalapeño — jalapeño chile",
      "chipotle — chipotle — smoked jalapeño",
      "achiote — achiote — annatto"
    ],
    "sweet_only": [
      "vainilla — vainilla — vanilla",
      "canela — canela — cinnamon"
    ],
    "signature_ingredients": [
      "masa harina — substitute: fresh masa",
      "tomatillos — substitute: canned tomatillos",
      "Mexican dried chiles — substitute: closest named chile where possible",
      "queso fresco — substitute: mild feta with less salt, imperfect"
    ],
    "pantry_assumed": [],
    "techniques": [
      "griddling tortillas",
      "roasting/charring salsa ingredients",
      "frying and simmering sauces",
      "grilling",
      "braising"
    ],
    "shortcuts": [
      "Taco seasoning packets are an export shortcut, not a Mexican default: if used, replace the recipe's combined chile/cumin/garlic/onion/salt by equal weight and subtract label-derived salt. Jarred salsa can replace table salsa 1:1 by weight when convenience matters, but should not stand in for mole or a dish-specific cooked sauce."
    ],
    "allergen_notes": [
      "Flour tortillas contain wheat. Cheese/crema contain milk. Mole can contain peanuts, sesame and tree nuts; commercial taco seasoning or sauces may contain wheat/soy depending on brand."
    ],
    "pitfalls": "Flag hard-shell tacos with ground beef, large amounts of yellow cheese and cumin-heavy packet seasoning as Tex-Mex/American export conventions rather than universal Mexican norms. Do not call every chile sauce 'mole' or assume chocolate, sour cream and cheddar belong in all Mexican dishes.",
    "sources": [
      "Jeffrey M. Pilcher, Planet Taco: A Global History of Mexican Food, 2012",
      "https://americanhistory.si.edu/explore/exhibitions/food/online/resetting-table/mexican-food-revolution",
      "https://folklife.si.edu/magazine/social-power-of-the-taco",
      "Diana Kennedy, The Essential Cuisines of Mexico, 2000"
    ]
  },
  {
    "id": "caribbean",
    "label": "Caribbean",
    "subtitle": "Scallion, thyme, chile, allspice",
    "about": "The Caribbean is an island region stretching from the Greater Antilles to the Lesser Antilles and nearby mainland-facing islands, so it contains many cuisines rather than one. Indigenous Caribbean foodways, European empires, the forced migration of Africans, indentured South Asian labor, Chinese migration and intra-Caribbean movement created overlapping but distinct traditions. Jerk, rice-and-peas dishes, roast pork, curries and plantain preparations are representative across different islands, not universal to all.",
    "flavors": [
      "scallion/cebollín — scallion/cebollín — scallion",
      "thyme/tomillo — thyme/tomillo — thyme",
      "allspice/pimento/pimienta gorda — allspice/pimento/pimienta gorda — allspice",
      "hot chile/ají — hot chile/ají — hot chile",
      "garlic/ajo — garlic/ajo — garlic",
      "ginger/jengibre — ginger/jengibre — ginger",
      "lime/limón — lime/limón — lime",
      "vinegar/vinagre — vinegar/vinagre — vinegar",
      "culantro/cilantro — culantro/cilantro — culantro or cilantro",
      "bay leaf/laurel — bay leaf/laurel — bay leaf"
    ],
    "sweet_only": [
      "vanilla/vainilla — vanilla/vainilla — vanilla",
      "nutmeg/nuez moscada — nutmeg/nuez moscada — nutmeg in many sweets/drinks"
    ],
    "signature_ingredients": [
      "culantro/recao — substitute: cilantro, weaker and different",
      "Scotch bonnet — substitute: habanero",
      "saltfish — substitute: other salted cod",
      "pigeon peas/gandules — substitute: canned pigeon peas; black-eyed peas only as a texture fallback"
    ],
    "pantry_assumed": [],
    "techniques": [
      "marinating and live-fire grilling",
      "stewing/braising",
      "frying",
      "rice-and-legume one-pot cooking",
      "pickling and pepper-sauce making"
    ],
    "shortcuts": [
      "Caribbean green seasoning and sofrito jars vary by island: use 1:1 by weight only when the product matches the target cuisine, then reduce fresh aromatics. Jerk paste can replace a homemade jerk marinade concentrate roughly 1:1 by weight; salt varies, so derive salt from label sodium."
    ],
    "allergen_notes": [
      "Soy sauce in Jamaican-style marinades contains soy and often wheat. Fish sauce or salted fish adds fish; dried shrimp/shrimp pastes in some island traditions add shellfish. Peanut sauces occur in some Caribbean contexts but are not pan-Caribbean. Coconut is widely used but, per current FDA guidance, coconut is no longer treated as a major tree-nut allergen for US labeling."
    ],
    "pitfalls": "Never flatten the Caribbean into 'jerk + coconut + rum.' Cuba, Puerto Rico, Jamaica, Trinidad and Tobago, Haiti, Barbados and other islands have different colonial, linguistic and migration histories. Use a country/island child node whenever possible.",
    "sources": [
      "https://folklife-media.si.edu/docs/festival/program-book-articles/FESTBK1989_09.pdf",
      "https://nmaahc.si.edu/explore/stories/black-foodways-and-cuisine",
      "Jessica B. Harris, Sky Juice and Flying Fish: Traditional Caribbean Cooking, 1991",
      "https://www.fda.gov/food/food-allergensgluten-free-guidance-documents-regulatory-information/frequently-asked-questions-food-allergen-labeling-guidance-industry"
    ]
  },
  {
    "id": "caribbean_cuban",
    "label": "Cuban",
    "subtitle": "Garlic, sour orange, cumin, oregano",
    "about": "Cuban cuisine developed on the large island of Cuba, between Florida, the Gulf of Mexico and the Caribbean. Taíno continuities, Spanish colonial foodways, African and Afro-Cuban traditions, Caribbean exchange and later Chinese and other migrations all contributed. Ropa vieja, lechón asado, moros y cristianos or congrí, picadillo and ajiaco are representative.",
    "flavors": [
      "ajo — ajo — garlic",
      "naranja agria — naranja agria — sour orange",
      "comino — comino — cumin",
      "orégano — orégano — oregano",
      "cebolla — cebolla — onion",
      "pimiento — pimiento — bell pepper",
      "laurel — laurel — bay leaf",
      "pimienta negra — pimienta negra — black pepper",
      "vinagre — vinagre — vinegar",
      "cilantro — cilantro — cilantro"
    ],
    "sweet_only": [
      "vainilla — vainilla — vanilla",
      "canela — canela — cinnamon"
    ],
    "signature_ingredients": [
      "sour orange — substitute: orange juice plus lime juice",
      "malanga — substitute: taro, closest; potato is a weaker texture substitute",
      "boniato — substitute: white sweet potato",
      "culantro — substitute: cilantro"
    ],
    "pantry_assumed": [],
    "techniques": [
      "mojo marination and roasting",
      "sofrito sautéing",
      "stewing/braising",
      "rice-and-bean cooking",
      "frying plantains and croquettes"
    ],
    "shortcuts": [
      "Bottled mojo criollo can replace homemade mojo 1:1 by weight for marinade volume, but check salt and acidity; reduce salt using label sodium. Jarred sofrito can replace freshly sautéed sofrito roughly 1:1 by weight, LOW CONFIDENCE because formulas and water content vary."
    ],
    "allergen_notes": [
      "Some bottled mojo or bouillon contains wheat/soy depending on brand. Cuban sandwich mustard is usually allergen-light, but mayonnaise in some diaspora versions adds egg. Croquettes often contain milk, egg and wheat; these are dish components, not hidden foundational seasonings."
    ],
    "pitfalls": "Do not make all Cuban food hot; chile heat is usually less central than garlic, citrus, cumin and oregano. Do not assume the Miami Cuban sandwich is identical to all Cuban home cooking, and do not erase African or Chinese contributions by describing the cuisine as simply Spanish-Caribbean.",
    "sources": [
      "Ana Sofía Peláez, The Cuban Table, 2014",
      "https://www.smithsonianmag.com/travel/ajiaco-cuba-food-history-atlas-of-eating-cultural-travel-180960688/",
      "https://guides.loc.gov/bibliografia-anotada-alimentacion/paises/cuba",
      "Nitza Villapol, Cocina al Minuto, various editions"
    ]
  },
  {
    "id": "caribbean_puerto_rican",
    "label": "Puerto Rican",
    "subtitle": "Sofrito, adobo, achiote, culantro",
    "about": "Puerto Rican cuisine comes from the mountainous and coastal island of Puerto Rico in the Greater Antilles. Taíno ingredients and techniques, Spanish colonization, African and Afro-Puerto Rican foodways and later US influence all shaped it. Arroz con gandules, pernil, pasteles, mofongo and asopao are representative.",
    "flavors": [
      "recao/culantro — recao/culantro — culantro",
      "ají dulce — ají dulce — sweet chile",
      "ajo — ajo — garlic",
      "orégano — orégano — oregano",
      "achiote — achiote — annatto",
      "sofrito — sofrito — aromatic herb-pepper base",
      "adobo — adobo — garlic-oregano seasoning",
      "cilantro — cilantro — cilantro",
      "pimienta negra — pimienta negra — black pepper",
      "vinagre — vinagre — vinegar"
    ],
    "sweet_only": [
      "vainilla — vainilla — vanilla",
      "canela — canela — cinnamon",
      "nuez moscada — nuez moscada — nutmeg, especially drinks/sweets"
    ],
    "signature_ingredients": [
      "ají dulce — substitute: mini sweet pepper plus a tiny piece of habanero for aroma, LOW CONFIDENCE",
      "culantro/recao — substitute: cilantro",
      "gandules — substitute: canned pigeon peas",
      "green plantain — substitute: none for mofongo; starchy banana is not equivalent"
    ],
    "pantry_assumed": [],
    "techniques": [
      "pilon pounding/mashing",
      "sofrito sautéing",
      "roasting pork",
      "rice-and-legume one-pot cooking",
      "steaming wrapped pasteles"
    ],
    "shortcuts": [
      "Jarred sofrito: use about the same weight as fresh blended sofrito, then cook it out; salt content varies. Packet sazón: often salt, coriander/garlic, annatto and sometimes MSG; replace an equal weight of recipe dry seasoning only after calculating salt from label sodium. Adobo seasoning likewise needs sodium-based salt correction."
    ],
    "allergen_notes": [
      "Commercial sazón, adobo and bouillon can contain wheat, soy or other allergens depending on brand, so verify labels. Mayo-based sauces contain egg. Pasteles and mofongo are not inherently major-allergen foods, but fillings and commercial seasonings can introduce allergens."
    ],
    "pitfalls": "Do not confuse Puerto Rican sofrito with tomato-heavy Italian soffritto or assume it is the same as every Caribbean sofrito. Do not call mofongo Dominican or Cuban by default; related mashed-plantain dishes exist elsewhere, but mofongo is strongly identified with Puerto Rico. Heat from hot chiles is optional in much home cooking.",
    "sources": [
      "Cruz Miguel Ortíz Cuadra, Eating Puerto Rico: A History of Food, Culture, and Identity, 2013",
      "Illyanna Maisonet, Diasporican: A Puerto Rican Cookbook, 2022",
      "https://www.smithsonianmag.com/travel/a-brief-history-of-puerto-ricos-beloved-mofongo-180979947/",
      "https://guides.loc.gov/bibliografia-anotada-alimentacion/paises/puerto-rico"
    ]
  },
  {
    "id": "caribbean_jamaican",
    "label": "Jamaican",
    "subtitle": "Pimento, Scotch bonnet, thyme, scallion",
    "about": "Jamaican cuisine comes from the mountainous island of Jamaica in the Greater Antilles. Indigenous Taíno legacies, British colonial rule, African and Maroon foodways, and later Indian, Chinese and other migrations shaped a cuisine with strong live-fire, curry and one-pot traditions. Jerk pork or chicken, ackee and saltfish, curry goat, rice and peas and escovitch fish are representative.",
    "flavors": [
      "pimento — pimento — allspice",
      "Scotch bonnet — Scotch bonnet — Scotch bonnet chile",
      "thyme — thyme — thyme",
      "scallion — scallion — scallion",
      "ginger — ginger — ginger",
      "garlic — garlic — garlic",
      "black pepper — black pepper — black pepper",
      "Jamaican curry powder — Jamaican curry powder — turmeric-forward curry blend",
      "browning — browning — caramelized sugar coloring/seasoning",
      "vinegar — vinegar — vinegar",
      "soy sauce — soy sauce — fermented soy seasoning"
    ],
    "sweet_only": [
      "nutmeg — nutmeg — nutmeg",
      "vanilla — vanilla — vanilla"
    ],
    "signature_ingredients": [
      "ackee — substitute: none for identity; hearts of palm only mimics texture poorly",
      "Scotch bonnet — substitute: habanero",
      "pimento wood/leaves — substitute: allspice berries plus hardwood smoke, imperfect",
      "saltfish — substitute: other salted cod"
    ],
    "pantry_assumed": [],
    "techniques": [
      "jerking over live fire/smoke",
      "long stewing and braising",
      "frying and escovitch pickling",
      "rice-and-peas absorption cooking",
      "currying"
    ],
    "shortcuts": [
      "Jerk paste: use roughly the same weight as a concentrated homemade jerk paste, then reduce fresh chile/scallion/thyme and salt; brands vary widely. Jamaican curry powder can replace the combined ground curry spices 1:1 by weight, but bloom it in fat and adjust salt separately if the blend is salted."
    ],
    "allergen_notes": [
      "Soy sauce contains soy and often wheat. Worcestershire, sometimes used in jerk or brown-stew recipes, contains fish. Commercial browning and curry blends vary; check labels for wheat/soy. Saltfish is fish, and shellfish is common in some seafood dishes."
    ],
    "pitfalls": "Do not reduce jerk to a dry 'jerk spice' of cayenne and cinnamon; pimento, Scotch bonnet, thyme, scallion and smoke are central signals. Do not assume all Jamaican food is very hot or all curry is Indian-style; Jamaican curry powders and techniques developed locally. Avoid calling generic barbecue 'jerk.'",
    "sources": [
      "Enid Donaldson, The Real Taste of Jamaica, 1993",
      "https://folklife-media.si.edu/docs/festival/program-book-articles/FESTBK1989_09.pdf",
      "Caroline Sullivan, Classic Jamaican Cooking, 1995",
      "https://www.unesco.org/sites/default/files/medias/fichiers/2023/11/EN_Caribbean%20Cultural%20Resources.pdf"
    ]
  },
  {
    "id": "caribbean_any",
    "label": "Any",
    "subtitle": "Jerk, coconut, rum, tropical spice",
    "about": "Outside the region, 'Caribbean food' is often imagined as a bright tropical blend of jerk spice, coconut, rum, rice and peas, plantains, seafood and hot pepper. That shared picture borrows heavily from Jamaican and tourist-facing island cuisines and obscures major differences among Spanish-, English-, French-, Dutch- and Creole-speaking islands. Representative export-image dishes include jerk chicken, rice and peas, fried plantains and coconut-based seafood stews.",
    "flavors": [
      "allspice/pimento — allspice/pimento — allspice",
      "Scotch bonnet/habanero — Scotch bonnet/habanero — hot chile",
      "thyme — thyme — thyme",
      "scallion — scallion — scallion",
      "garlic/ajo — garlic/ajo — garlic",
      "ginger/jengibre — ginger/jengibre — ginger",
      "lime/limón — lime/limón — lime",
      "rum/ron — rum/ron — rum",
      "curry powder — curry powder — Caribbean curry blend",
      "browning — browning — caramelized sugar seasoning"
    ],
    "sweet_only": [
      "vanilla/vainilla — vanilla/vainilla — vanilla",
      "nutmeg/nuez moscada — nutmeg/nuez moscada — nutmeg"
    ],
    "signature_ingredients": [
      "Scotch bonnet — substitute: habanero",
      "culantro/recao — substitute: cilantro",
      "green plantain — substitute: none exact",
      "saltfish — substitute: salted cod"
    ],
    "pantry_assumed": [],
    "techniques": [
      "marinating and grilling",
      "stewing",
      "frying",
      "rice-and-legume cooking",
      "pickling"
    ],
    "shortcuts": [
      "Jerk seasoning or paste can shortcut only Jamaican-leaning dishes, not 'Caribbean' cuisine generally; use equal weight to the homemade paste and correct salt from sodium. Canned coconut milk can replace freshly squeezed coconut milk 1:1 by weight but may be richer; thin with water if needed."
    ],
    "allergen_notes": [
      "Soy sauce in jerk-style marinades contains soy and often wheat; Worcestershire contains fish. Coconut is not currently classed by FDA as a major tree nut allergen, though individual coconut allergy exists. Commercial curry/seasoning blends can contain wheat or other allergens."
    ],
    "pitfalls": "This is deliberately an outsider stereotype node. Do not apply jerk, coconut or rum to Cuban or Puerto Rican dishes automatically, and do not present 'island food' as one cuisine. Many Caribbean cooks would object to collapsing their distinct national and ethnic traditions into this profile.",
    "sources": [
      "Jessica B. Harris, Sky Juice and Flying Fish, 1991",
      "https://folklife-media.si.edu/docs/festival/program-book-articles/FESTBK1989_09.pdf",
      "https://www.fda.gov/food/food-allergensgluten-free-guidance-documents-regulatory-information/frequently-asked-questions-food-allergen-labeling-guidance-industry"
    ]
  },
  {
    "id": "brazilian",
    "label": "Brazilian",
    "subtitle": "Garlic, dendê, chiles, herbs",
    "about": "Brazil spans the Amazon basin, Atlantic coast, dry Northeast, central savannas and temperate South, so its cuisine is strongly regional. Indigenous food systems, Portuguese colonization, enslaved Africans and later Italian, Japanese, German, Arab and other migrations shaped different local tables. Feijoada, moqueca, acarajé, pão de queijo and churrasco are representative national or regional icons rather than a single unified style.",
    "flavors": [
      "alho — alho — garlic",
      "cebola — cebola — onion",
      "pimenta-malagueta — pimenta-malagueta — malagueta chile",
      "azeite de dendê — azeite de dendê — red palm oil",
      "cheiro-verde — cheiro-verde — parsley/scallion herb mix",
      "coentro — coentro — cilantro, especially North/Northeast",
      "cominho — cominho — cumin",
      "louro — louro — bay leaf",
      "urucum/colorau — urucum/colorau — annatto",
      "limão — limão — lime",
      "vinagre — vinagre — vinegar"
    ],
    "sweet_only": [
      "baunilha — baunilha — vanilla",
      "canela — canela — cinnamon",
      "cravo — cravo — clove"
    ],
    "signature_ingredients": [
      "farinha de mandioca — substitute: coarse cassava flour; no wheat-flour equivalent for farofa",
      "azeite de dendê — substitute: none exact; neutral oil plus paprika only mimics color",
      "polvilho azedo/doce — substitute: tapioca starch, but sour starch flavor is lost",
      "queijo coalho — substitute: halloumi or low-moisture grilling cheese"
    ],
    "pantry_assumed": [],
    "techniques": [
      "stewing beans and meats",
      "moqueca-style covered simmering",
      "frying acarajé and salgados",
      "churrasco/live-fire grilling",
      "toasting cassava flour for farofa"
    ],
    "shortcuts": [
      "Tempero completo: commercial garlic/onion/herb seasoning often contains substantial salt; replace equal weight of the recipe's garlic-onion-salt seasoning and subtract salt from label sodium. Bottled molho de pimenta can replace a simple chile-vinegar condiment 1:1 by weight, not fresh malagueta in cooked dishes."
    ],
    "allergen_notes": [
      "Bahian acarajé and vatapá commonly involve shrimp, so shellfish can be hidden in pastes/fillings. Vatapá may contain peanuts or cashews. Soy sauce is common in Japanese-Brazilian contexts and contains soy/often wheat. Cheese-based dishes contain milk; commercial bouillon may contain soy/wheat/milk."
    ],
    "pitfalls": "Do not make all Brazilian food Bahian: dendê, coconut and strong malagueta are regionally important, not universal. Do not treat feijoada as the sole national template or assume every Brazilian dish contains black beans. Distinguish Bahian moqueca from Espírito Santo moqueca, which traditionally uses different fat and coloring choices.",
    "sources": [
      "https://pesquisaescolar.fundaj.gov.br/pt-br/artigo/culinaria-brasileira/",
      "https://www.gov.br/secretariageral/pt-br/consea/acervo/publicacoes/alimentacao-adequada-e-saudavel/alimentos-regionais-brasileiros-2a-edicao.pdf",
      "Jessica B. Harris, Tasting Brazil, 1992",
      "https://festival.si.edu/2020/brazil"
    ]
  },
  {
    "id": "peruvian",
    "label": "Peruvian",
    "subtitle": "Ají, lime, cilantro, huacatay",
    "about": "Peru runs from a cold, seafood-rich Pacific coast across the Andes to the Amazon, and its cuisine reflects all three ecological zones. Indigenous Andean and coastal traditions combined with Spanish and African influences and, from the nineteenth century onward, major Chinese and Japanese migrations that helped shape chifa and Nikkei cuisines. Ceviche, lomo saltado, ají de gallina and causa are representative.",
    "flavors": [
      "ají amarillo — ají amarillo — yellow ají chile",
      "ají panca — ají panca — panca chile",
      "rocoto — rocoto — rocoto chile",
      "culantro — culantro — cilantro",
      "huacatay — huacatay — black mint",
      "ajo — ajo — garlic",
      "comino — comino — cumin",
      "limón — limón — Peruvian lime",
      "orégano — orégano — oregano",
      "kion — kion — ginger",
      "sillao — sillao — soy sauce"
    ],
    "sweet_only": [
      "canela — canela — cinnamon",
      "vainilla — vainilla — vanilla",
      "clavo — clavo — clove"
    ],
    "signature_ingredients": [
      "ají amarillo paste — substitute: yellow bell pepper plus habanero, rough only",
      "huacatay — substitute: mint plus basil/tarragon, rough only",
      "choclo — substitute: large-kernel frozen corn; standard sweet corn is sweeter",
      "cancha/chulpe corn — substitute: corn nuts only as a texture shortcut",
      "chuño — substitute: potato starch only for thickening, not identity"
    ],
    "pantry_assumed": [],
    "techniques": [
      "acid marination for ceviche",
      "wok stir-frying for chifa/lomo saltado",
      "pachamanca/earth-oven or high-heat roasting",
      "ají-paste frying and sauce making",
      "potato pressing/mashing"
    ],
    "shortcuts": [
      "Jarred ají amarillo or ají panca paste can replace homemade chile paste 1:1 by weight if it is a plain paste; salted/acidified brands require salt/acid adjustment. Bottled sillao can replace soy sauce 1:1 by weight; note soy and wheat. Commercial anticucho paste can replace a homemade chile-garlic-vinegar marinade concentrate approximately 1:1 by weight, LOW CONFIDENCE because formulas vary."
    ],
    "allergen_notes": [
      "Sillao/soy sauce contains soy and often wheat. Chifa sauces may include oyster sauce, which contains shellfish, and some preparations use sesame oil. Ají de gallina and huancaína sauces commonly contain milk and may contain wheat from bread/crackers; peanuts or nuts occur in some sauces and sweets."
    ],
    "pitfalls": "Do not describe all Peruvian food as ceviche plus hundreds of potatoes. Chifa and Nikkei are Peruvian traditions with their own histories, not garnish-level 'Asian fusion.' Ginger is important especially in chifa/Nikkei and some ceviche styles but is not a universal everyday seasoning; annatto is less central nationally than ají amarillo/panca.",
    "sources": [
      "https://ich.unesco.org/en/RL/practices-and-meanings-associated-with-the-preparation-and-consumption-of-ceviche-an-expression-of-peruvian-traditional-cuisine-01952",
      "https://festival.si.edu/2015/peru/foodways/smithsonian",
      "Tony Custer, The Art of Peruvian Cuisine, 2003",
      "Gastón Acurio, Peru: The Cookbook, 2015"
    ]
  },
  {
    "id": "argentinian",
    "label": "Argentinian",
    "subtitle": "Beef, parsley, oregano, ají",
    "about": "Argentina stretches from subtropical northwestern valleys and pampas grasslands to Patagonia and the South Atlantic coast. Indigenous Andean and Guaraní traditions, Spanish colonial foodways, gaucho cattle culture and especially large Italian and other European migrations shaped modern regional cooking. Asado, empanadas, locro, milanesa and pasta are representative, with strong provincial variation.",
    "flavors": [
      "ajo — ajo — garlic",
      "perejil — perejil — parsley",
      "orégano — orégano — oregano",
      "ají molido — ají molido — crushed mild red chile",
      "pimentón — pimentón — paprika",
      "comino — comino — cumin, especially northwest",
      "laurel — laurel — bay leaf",
      "pimienta negra — pimienta negra — black pepper",
      "vinagre — vinagre — vinegar",
      "chimichurri — chimichurri — herb-garlic-vinegar condiment"
    ],
    "sweet_only": [
      "vainilla — vainilla — vanilla",
      "canela — canela — cinnamon"
    ],
    "signature_ingredients": [
      "matambre cut — substitute: flank steak, butterflied",
      "provoleta — substitute: thick-cut provolone suitable for grilling",
      "ají molido argentino — substitute: mild crushed red pepper plus paprika",
      "charqui — substitute: unsweetened dried beef/jerky, rehydrated"
    ],
    "pantry_assumed": [],
    "techniques": [
      "asado/live-fire grilling",
      "empanada baking or frying",
      "slow stewing",
      "breaded frying for milanesa",
      "pasta and ñoqui making"
    ],
    "shortcuts": [
      "Prepared chimichurri can replace homemade chimichurri 1:1 by weight, but bottled versions may be saltier/oilier; correct salt from sodium. Empanada seasoning blends often combine paprika, cumin, oregano and chile; use equal weight for the dry spices and adjust salt if included."
    ],
    "allergen_notes": [
      "Provoleta and many pasta fillings contain milk. Milanesa breading contains wheat and egg. Soy is not a defining traditional seasoning but may appear in contemporary marinades; packaged bouillon can contain wheat/soy/milk."
    ],
    "pitfalls": "Do not make Argentine food uniformly spicy; ají molido is often mild and hot chile is not the national default. Do not treat chimichurri as a mandatory marinade for every steak: it is commonly a table condiment. Northwest locro/empanadas differ markedly from Buenos Aires Italian-influenced cooking and Patagonian lamb traditions.",
    "sources": [
      "https://www.argentina.gob.ar/node/434311",
      "https://www.argentina.gob.ar/sites/default/files/bancos/2022-08/Recetario_Federal_Sin_TACC_05082022.pdf",
      "Francis Mallmann, Seven Fires: Grilling the Argentine Way, 2009",
      "https://www.argentina.gob.ar/node/439597"
    ]
  }
]
```