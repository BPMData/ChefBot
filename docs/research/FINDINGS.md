# Cuisine research: findings so far

Read this instead of the raw reports. Status (2026-11-09): **research complete for all five continents** (ChatGPT
deep research, v2 prompts in `docs/research/<continent>.md`). 69 nodes: Americas 21, Asia 26, Europe 10, Near &
Middle East 3, Africa 5, plus 4 added cuisines in `additions.json` (Tunisian and Algerian for Africa, Afghan and
Pakistani for Asia).

Files (add a new report with `python3 tools/check_research.py <continent> <report.md>`: it checks the JSON and
fields, flags missing URLs and long labels, counts "never"/"always", and saves both files below):

- `results/<continent>.json` (`americas`, `asia`, `europe`, `near_east`, `africa`): the import data, one object
  per node with the 13 fields from the prompt. The checker normalizes shapes: every list field is a list of plain
  strings (reports gave some as single strings, and signature ingredients and shortcuts as objects).
- `results/near_east_run2.json`: the Near & Middle East was researched twice by accident. `near_east.json` is the
  primary (cleaner fields); run 2 has a few extras worth merging, listed below.
- `results/raw/<continent>.md`: the full reports, kept for reference. Only open one to check a specific claim or
  source. Inline citation markers in them are dead; the URLs in the JSON `sources` fields are the usable ones.

## Which service

ChatGPT deep research, v2 prompt. A first round compared it with Gemini on the Americas and Africa: Gemini
stated myths as hard rules ("Cajun never uses tomatoes", "Cuban and Puerto Rican food has zero heat"), seemed to
invent history, and its Africa run stopped after the intro. ChatGPT was careful and well sourced. With the v2
prompt it returned valid JSON with every field filled, a fact-check, URLs, and almost no "never"/"always".

Pasting the prompt from a phone can cut it off at the SCOPE section; copy it from a code block or attach the file.

## Importing the JSON: quirks to handle

- **Branch nodes:** `the_americas`, `asia`, `europe` (continents) and `eight_great_cuisines` are organizational
  only: ignore them as cuisines. `united_states`, `mexico`, `caribbean`, `china`, `japan`, `india` and `italy` are
  country aggregates (usable for the branch's info sheet); the `*_any` nodes are the "Any" picks (outsider's
  view). Near & Middle East and Africa have no branch nodes.
- **Ids for the other continents:** `northern_italy`, `southern_sicilian_italy`, `italy_any`, `french`, `spanish`,
  `greek`, `central_european`, `russian`; `palestinian_levantine`, `persian`, `turkish`;
  `moroccan_north_african` (label "Moroccan"), `ethiopian`, `egyptian`, `nigerian`, `senegalese`.
- **Ids:** the Americas prefixes them (`us_cajun`, `mx_yucatan`, `caribbean_cuban`), Asia doesn't (`sichuan`,
  `north_india`). Pick one scheme at import.
- **`flavors` format differs:** the Americas uses "native — romanization — English", which is redundant for Latin
  scripts ("oignon/onion — oignon/onion — onion"); Asia uses "English (romanization, native)". Normalize to one.
- **Cantonese romanization:** Asia uses Jyutping with tone numbers (`goeng1`), which is what the prompt asked for.
  The app's current Hong Kong list uses Yale-style accents; switch to Jyutping when importing.
- **Shortcuts and salt:** amounts are per weight of food (e.g. "15-20 g oyster sauce seasons about 500 g food").
  For store-bought blends, every report uses the label rule `salt_g ≈ sodium_mg × 0.0025` (1 g sodium is about
  2.5 g salt; some write 0.00254) and subtracts that from the added salt. They refuse to invent a fixed salt
  figure for blends that vary by brand, and mark guesses LOW CONFIDENCE. This fits the app's "salt in grams" rule.
- **Coconut:** per current FDA guidance it is no longer a major tree-nut allergen. The app's allergen rule already
  says so.

## Conflicts with Bryan's calls (all decided 2026-11-09)

1. **American flavors: decided, keep them.** The research marks cinnamon and vanilla as sweet-only and Old Bay as
   Chesapeake-specific. Bryan keeps all three as savory flavors of `us_any` (which replaces "American").
2. **Filé powder: decided, it's out** (Bryan, 2026-11-09). Drop it from `us_cajun` and `us_creole` at import. His
   thickeners instead, already in the app as `prompts.LOUISIANA_THICKENING`: okra; a dark roux plus a reduced,
   collagen-rich homemade stock; or xanthan gum weighed in grams (about 1 to 3 g per liter of liquid).

3. **Mastiha:** Bryan moved it to dessert-only for Greek. The research says it's mainly sweets, breads and liqueurs
   but has savory uses on Chios. Keeping it in `sweet_only` with that note is consistent with both.
4. **"Moroccan & North African": decided, it's "Moroccan"** (the research's advice: harissa is Tunisian and the
   Maghreb's cuisines aren't interchangeable). **Tunisian** (for harissa) and **Algerian** were added to Africa,
   and **Afghan** and **Pakistani** to Asia: one research run (`docs/research/additions.md`, result goes to
   `results/additions.json`).

## Corrections to the app's current entries

From the fact-checks. These entries are live in `src/chefbot/prompts.py` now (`CUISINE_ABOUT` is shown in the
info sheet; `CUISINES` flavors are sent to the model). The tree import replaces them; the starred ones are quick
fixes worth making sooner because they're plain errors.

**Americas**

- *Creole about: "Richer and more refined than its country cousin Cajun" is wrong (an old, classed restaurant
  story that hides Black working-class Creole cooking). Butter and cream aren't reliable separators; tomato is a
  tendency. Rural Creole communities exist outside New Orleans; Native American influence should be named.
- Cajun about: "built on a dark roux" is wrong as a blanket rule (gumbo can use roux, okra, filé or a mix);
  "cayenne heat" overstates it (often layered, not hot); lineage is Acadian plus Indigenous, African, Spanish,
  German. Oregano is weak as a core Cajun flavor.
- Creole flavors: "tomato paste" should be tomato; oregano and basil weak as core; butter is a fat, not a flavor.
- *Mexican flavors: "cilantro and coriander (cilantro y coriandro)" conflates leaf and seed; use cilantro (leaf),
  and "semilla de cilantro" if the seed is meant. Cumin and achiote are regional (cumin leans Tex-Mex and the
  north; achiote the Yucatán), chocolate and cinnamon are not default savory seasonings ("all mole = chocolate" is
  a classic AI error).
- Peruvian: "very fresh fish" is coastal only; achiote is weak nationally; rocoto and sillao (soy sauce, via chifa)
  are stronger; kion (ginger) is valid mainly through chifa and Nikkei.
- American: the description's examples are regional, and "generous, bold and unfussy" is a stereotype.

**Asia**

- Cantonese: "the style of most Chinese restaurants abroad" is true of early US history, not worldwide (Southeast
  Asia's Chinese diasporas are mostly Fujianese, Teochew, Hainanese, Hakka). Chenpi is specialized; Shaoxing wine
  is not the same as mijiu.
- Hong Kong: romanization should be Jyutping with tone numbers; five-spice, star anise and hoisin are optional
  siu mei flavors, not markers.
- Sichuan: star anise and five-spice are weak; black vinegar, yacai (preserved mustard greens), pickled chile and
  sesame paste are better signals. "Dozens of flavor profiles, many not hot" is confirmed (about 24).
- Shandong: "oldest" is a conventional claim, not testable. *Wood ear as its signature ingredient is wrong (found
  all over China); seafood (sea cucumber, prawns, yellow croaker) and Zhangqiu scallions are more defining.
- Jiangsu: Huaiyang is one Jiangsu tradition (Huai'an, Yangzhou), not all of Jiangsu (Suzhou/Wuxi and Nanjing
  differ). Red fermented tofu is disputed as core; osmanthus isn't strictly dessert-only; dried bamboo shoots are
  weak (freshwater crab, river fish, water bamboo and lotus are stronger).
- Kansai: "Kansai shoyu" isn't a soy sauce category (say usukuchi); yuzu and shiso aren't Kansai-specific; dashi
  plus its own components is redundant.
- *Kanto: "soba began as Edo fast food" is wrong (soba is older; Edo developed the stall culture). Red miso is
  weak (more Aichi); nori is an ingredient, not a seasoning.
- North Indian: Punjab and Mughlai stand in for all of North India; naan is mostly restaurant food (roti, chapati
  and paratha are home defaults); cream and paneer gravies are a restaurant idiom. Black mustard seed is weak;
  ajwain, fennel, black cardamom, amchur (dried mango) and kasuri methi are better, by subregion.
- South Indian: coconut isn't universal (mainly Kerala and the coast); "hotter and more sour" is a stereotype.
  *Urad dal is a pulse, not a seasoning. *"sukku milagai" is wrong Tamil (sukku is dried ginger): dried red chile
  is "vara milagai".
- Korean: *고추가루 should be 고춧가루 (standard spelling). "Grilling and jjigae are the heart of it" is too narrow
  (namul, soups, braises, jeon, noodles, porridges matter as much).
- *Thai: "a balance of sweet, sour, salty and spicy in every dish" is wrong: the balance is across the meal.
  Coconut milk is an ingredient, not a seasoning; "kaffir lime" should be "makrut lime".
- Vietnamese: "fish sauce, lime, chili and herbs at every meal" is wrong as an absolute (lime and chile less so in
  the north); star anise is mainly pho and braises. Pho's exact origin is debated.

**Europe and Near East** (the app's French, Greek, Italian, Spanish and Turkish entries)

- French: "the foundation of Western restaurant technique" is disputed (Carême and Escoffier shaped professional
  kitchens, but it overstates); the rest of the description and every flavor is correct. Add chives.
- Greek: "Ottoman rule left warm spices like cinnamon" is disputed: cinnamon and allspice in savory braises are
  right, but the history is Byzantine, Venetian and eastern Mediterranean as much as Ottoman, and modern
  béchamel moussaka is a 20th-century codification. Fennel is mainly Cretan and island cooking. Add thyme,
  parsley, allspice and garlic.
- Italian: "a few excellent ingredients, treated simply" is disputed (ragù, stuffed pasta and timballi are just as
  traditional). Fennel seed is regional, not national; oregano and peperoncino lean southern, nutmeg and sage
  northern. The tree's Northern and Southern & Sicilian nodes handle this.
- *Spanish: "smoked pimentón" is wrong as a blanket: only Pimentón de la Vera is smoked (Murcia's isn't). Saffron is
  emblematic but dish-specific; rosemary, cumin, thyme and sherry vinegar are regional (sherry vinegar is
  Andalusian).
- Turkish (both runs agree): "from the Ottoman palace kitchens" is too narrow (Anatolian regional and folk cooking,
  Seljuk, nomadic and minority traditions too). *Pomegranate molasses is southern and southeastern (Gaziantep,
  Hatay), not national. *Fenugreek is specialized (çemen paste, pastırma), not an everyday flavor. Sesame is a
  garnish and tahini, not a seasoning. Kekik covers several oregano and thyme-type herbs. Add black pepper,
  garlic, and pepper and tomato pastes (biber and domates salçası), which matter more than a spice mix. "Mezze"
  is spelled "meze" in Turkish.

## New cuisines: what matters most

Highlights for writing the entries; the JSON has the detail.

- **Southern & Soul, Tex-Mex, New England:** soul food is its own African American tradition, not a synonym for
  Southern; Tex-Mex is a Tejano regional cuisine, not failed Mexican (cumin, flour tortillas, yellow cheese and
  chili gravy are part of it).
- **Mexico regions, Caribbean, Brazil, Argentina:** Yucatán needs achiote, sour orange and slow cooking (not
  habanero on a taco); Cuban food is garlic-citrus-cumin, rarely chile-hot; mofongo means green plantain; dendê
  is Bahian, not national Brazilian; Argentine asado is salt and slow embers, and Italian immigration (pizza,
  pasta, milanesa) is as Argentine as beef.
- **China's other regions:** Hunan is sour and dry-hot (not mala); Zhejiang fresh and mellow; Fujian soups and red
  yeast rice; Anhui wild herbs, braises.
- **Southeast Asia:** Filipino, Indonesian and Malaysian & Singaporean resist one template (Indonesia is many
  islands' cuisines; Malaysia and Singapore are Malay, Chinese, Indian, Peranakan and hawker lineages).
- **Northern Italy / Southern & Sicilian / Italian (Any):** north is butter, rice, polenta, sage, no automatic
  tomato or oregano; Sicily has saffron, raisins, pine nuts, wild fennel and agrodolce. Italian (Any) is openly the
  export image (spaghetti and meatballs, cream Alfredo and pepperoni pizza are Italian-American).
- **Central European:** five countries; paprika is Hungarian, not a shared default; caraway, marjoram, dill,
  horseradish and juniper vary by country. Treat as loose guidance.
- **Russian:** sourness, brine, fermentation, rye, buckwheat, mushrooms and cabbage, not just dill and sour cream;
  borscht is shared, especially Ukrainian.
- **Palestinian & Levant:** allspice-forward warm spices, sumac, za'atar (the herb and the blend), tahini, lemon;
  musakhan, maqluba and maftoul are especially Palestinian, many other dishes are shared across the Levant; Gaza
  cooks hotter, with dill and chile. Don't make Reem Kassis's family nine-spice a universal formula; shakshuka is
  North African, not a Palestinian default.
- **Persian:** sour fruit, herbs and rice technique (parboil and steam, deliberate tahdig) over spice; dried lime is
  not replaceable by fresh; saffron is iconic but not everywhere; rosewater mainly sweets; little chile heat.
- **Moroccan:** balance, not spice overload; preserved lemon, saffron, cumin, ginger, chermoula; harissa is
  Tunisian; not every tagine is sweet; couscous is steamed.
- **Ethiopian:** red wot vs mild alicha vs tibs vs fasting dishes (no butter); berbere isn't in everything;
  korerima isn't green cardamom; injera is fermented teff.
- **Egyptian:** cumin, coriander, garlic, lemon, vinegar; ta'ameya is fava, not chickpea; molokhia isn't spinach;
  koshari's parts are cooked separately.
- **Nigerian:** start from the dish family and region (Yoruba, Igbo, Hausa...), not a national template; don't put
  egusi, crayfish, palm oil or iru in everything. *Yaji/suya spice usually contains peanut (kulikuli).
- **Tunisian:** harissa (dried chile, garlic, salt, coriander; caraway common), tabil (coriander or a coriander-based
  blend), olive oil, seafood, lablabi, brik; harissa is a cooking base as well as a condiment, but not compulsory
  in every dish, and Tunisian tajine is a baked egg dish, not a stew. Couscous is shared Maghrebi heritage
  (UNESCO, 2020).
- **Algerian:** dersa (garlic-chile paste, variants), cinnamon-scented white sauces and chile-garlic red sauces, frik
  (green wheat), rechta (steamed noodles); not just "one white sauce, one red sauce"; "sauce algérienne" (the
  mayonnaise) isn't Algerian.
- **Afghan:** palaw (parboil and steam), browned onions, mantu (usually steamed) vs ashak (usually boiled, gandana
  filling), chakka and qurut; Persian and Central Asian ties, but not a branch of Persian; chile and turmeric do
  appear. **Keep Afghan and Pakistani as two nodes** (the research's recommendation); they meet in Pashtun
  borderland food like chapli kebab.
- **Pakistani:** bhunai, tarka, dum, karahi styles (Peshawari, Lahori, Karachi), nihari, Sindhi biryani; shares a
  lot with North India (Punjabi, Mughal), so differences are regional, not categorical. Kewra and rosewater also
  go in biryani, not only sweets.
- **Senegalese:** ceebu jën (UNESCO-listed, from Saint-Louis), yassa (lots of onion, mustard, often grilled) and mafé
  (peanut) are distinct; fermented nététou, guedj and yët give depth (fish and shellfish allergens); don't swap
  in soy or fish sauce.

**Near East run 2 extras worth merging into `near_east.json`:** Palestinian: Gaza's hotter, dill-forward cooking in
`about`, and jameed, akkawi/nabulsi cheese and the fresh za'atar herb as signature ingredients. Persian: golpar
and sumac as flavors, advieh as a variable blend. Turkish: kaymak and bulgur grades as signature ingredients.

**About the added-cuisines run:** the first attempt was poor (Wikipedia-only sources, native names in the wrong
languages, factual errors) and Bryan had to push ChatGPT through several corrections; the saved version is the
corrected one, with good sources (UNESCO, Roden, Saberi, Ayubi, Usmani, Bouayed). Two things differ from the other
continents:

- **Brand names:** its shortcuts cite specific products (Le Phare du Cap Bon harissa, Shan biryani, karahi and
  nihari mixes) with label-derived salt. Bryan doesn't want brands named in recipes: keep the numbers as
  "a typical packaged mix contributes about X g salt per 10 g" and drop the brand.
- **Pantry defaults (an idea for Bryan):** its `pantry_assumed` lists what a cook of that cuisine probably has on
  hand (spices, oil, rice, couscous...) as soft defaults, so a user who photographs only new groceries still gets
  a sensible recipe. The other continents mostly left `pantry_assumed` empty. If Bryan wants this, it would be a
  setting ("Use cuisine pantry defaults"), the other continents' lists would need filling, and the prompt must say
  the item was assumed, not seen, and honor dietary rules and "never use". Not part of the cuisine-tree build.

## Themes for writing the entries

- Every flavor list is a vocabulary to draw on, not a checklist: a Sichuan dish doesn't need Sichuan pepper, a
  Thai dish doesn't need coconut milk. Matches ChefBot's "use only the ones that suit this dish".
- The "Any" nodes are export images (US: burgers, barbecue, diner food; Mexico: tacos, salsa, guacamole, partly
  Tex-Mex; Caribbean: leans on Jamaican jerk, tropical fruit, rum, coconut; China: fried rice, dumplings, sweet-savory
  stir-fries; Japan: sushi, ramen, tempura, teriyaki; India: butter chicken, tikka masala, naan, biryani; Italy:
  red sauce, garlic, basil, pizza, pasta). Mark them
  internally as export profiles.
- Use "in the style of" rather than "authentic" when the user's pantry forces big substitutions.
- Don't police "authenticity" by ingredient origin: tomatoes, peppers, potatoes and paprika arrived from the
  Americas and are now foundational in Italy, Spain and Hungary.
- Allergens hide in prepared condiments more than in single spices (pesto, romesco, alioli, za'atar, tahini, yaji,
  bouillon cubes): the prompt should tell the model to check those.

## Second batch (2026-11-13): 14 cuisines, Antigravity

**Use:** `results/additions_europe.json` and `results/additions_americas.json` (full reports in `results/raw/`),
from Gemini agents in Antigravity. Six reports were compared (ChatGPT deep research, Gemini deep research and
Antigravity, each for both continents); Bryan chose Antigravity for both.

- **ChatGPT: not saved.** Most likely its lighter fallback once the month's full deep research runs were used
  up: two sources per cuisine, many from SEO sites, and plain errors (Portuguese "pimentão-doce" for Austrian
  paprika, "Senf (English mustard)", made-up native names such as Nordic "Alleholjende" and Irish "Gorg", Hawaiian
  "ulu" for green onion, which means breadfruit, aji amarillo as a New Mexican ingredient, Tafelspitz "stewed with
  cream"). If ChatGPT is used again, check it ran the full version.
- **Gemini deep research: kept as a second opinion** (`*_gemini.json`, `raw/*_gemini.md`). Well sourced but
  over-hedged: "LOW CONFIDENCE" on obvious staples (caraway in Czech), thin on Austrian, Czech and Irish
  seasoning, nothing on Ashkenazi cooking, and no guascas for Colombian. Worth checking for Scottish and Welsh
  cookbook history and the Jagerschnitzel regional split, which Antigravity covers more briefly.
- **Antigravity: the best of the six.** Specific seasoning for every cuisine, real authorities (Lang, Gundel,
  Plachutta, FitzGibbon, Allen, Nilsson, Goldstein, Capalbo, Hercules; Jamison, DeWitt and Bosland, Laudan, Hiura,
  Francoeur, Armstrong, Velasquez, Colombia's Ministry of Culture), product labels checked for salt and allergens.
  It agreed with both of Bryan's decisions below on its own.

**Fix in the house-style pass:**

- **Europe subtitles are too long** (five items each); trim to 3-4 for the chips. The Americas ones fit.
- **Irish overweights seaweed:** dulse leads its subtitle and two of nine flavors are seaweeds. Move dulse to
  signature ingredients; everyday Irish cooking is butter, parsley, thyme, pepper, malt vinegar, mustard.
- **Nine "never"/"always" in Europe** (Polish, Czech, Portuguese, Nordic). Most are fair (kmin is not cumin, never
  raw Mexican chorizo for chourico, always desalt bacalhau), but ChefBot enforces these as hard rules: reword each.
- **Austrian Tafelspitz cut:** it says "tri-tip / top sirloin cap"; tri-tip is a different cut. Top sirloin cap
  (picanha) only.
- **Hawaiian romanization:** "Hoyu" for oyster sauce is not a word; "Gomabura" should be "goma abura".
- **Colombian hogao:** cumin and achiote are common additions, not the core (scallion and tomato).
- **Quebecois:** "oreilles de crisse" is a Quebec swear form; write "oreilles de Christ" or "fried salt pork".
- **Field shapes:** allergen notes and pitfalls came as lists in the Americas file; the checker flattens them.
- **Label:** use "Hawaiian & Local" (decided), not Antigravity's "Hawaiian / Local".

**Decided with Bryan (2026-11-13):**
1. **Finland stays in Nordic.** Its seasoning (salt, allspice, black pepper, dill) is nearly Sweden's; what
   differs is ingredients (sour rye, wild mushrooms, lake fish, Karelian pasties), which the Nordic entry should
   mention. Split later only if recipes come out too Swedish.
2. **Georgian stays under Europe.** Gemini suggested the Near East on ingredient overlap, but Georgians mostly see
   themselves as European ("Caucasus" is the neutral term; EU candidate since 2023). Check the Europe map reaches
   far enough east to show Georgia.

3. **German default:** one everyday style for the whole country, neither Bavarian nor northern; Bavarian,
   Swabian or northern dishes only when the user's ingredients or request point there.
4. **Hawaiian default:** everyday island "local food" (plate lunch, poke, kalua pork, saimin, shoyu chicken).
   Native Hawaiian food (poi, laulau, kalo) is part of what people in Hawaii eat, so it sits inside that default,
   but recipes name it as Native Hawaiian rather than calling plantation-era local dishes "Hawaiian". Chip label:
   "Hawaiian & Local".
