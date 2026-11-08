# Cuisine research: findings so far

Read this instead of the raw reports. Status (2026-11-08): **Americas and Asia done**; Europe, Near & Middle East
and Africa still to run (ChatGPT deep research, v2 prompts in `docs/research/<continent>.md`).

Files (add a new report with `python3 tools/check_research.py <continent> <report.md>`: it checks the JSON and
fields, flags missing URLs and long labels, counts "never"/"always", and saves both files below):

- `results/<continent>.json`: the import data, one object per node with the 13 fields from the prompt. `pitfalls`
  is always a list (the Americas report gave strings; converted).
- `results/raw/<continent>.md`: the full reports, kept for reference. Only open one to check a specific claim or
  source. Inline citation markers in them are dead; the URLs in the JSON `sources` fields are the usable ones.

## Which service

ChatGPT deep research, v2 prompt. A first round compared it with Gemini on the Americas and Africa: Gemini
stated myths as hard rules ("Cajun never uses tomatoes", "Cuban and Puerto Rican food has zero heat"), seemed to
invent history, and its Africa run stopped after the intro. ChatGPT was careful and well sourced. With the v2
prompt it returned valid JSON with every field filled, a fact-check, URLs, and almost no "never"/"always".

Pasting the prompt from a phone can cut it off at the SCOPE section; copy it from a code block or attach the file.

## Importing the JSON: quirks to handle

- **Branch nodes:** `the_americas` and `asia` (continents) and `eight_great_cuisines` are organizational only:
  ignore them as cuisines. `united_states`, `mexico`, `caribbean`, `china`, `japan` and `india` are country
  aggregates (usable for the branch's info sheet); the `*_any` nodes are the "Any" picks (outsider's view).
- **Ids:** the Americas prefixes them (`us_cajun`, `mx_yucatan`, `caribbean_cuban`), Asia doesn't (`sichuan`,
  `north_india`). Pick one scheme at import.
- **`flavors` format differs:** the Americas uses "native — romanization — English", which is redundant for Latin
  scripts ("oignon/onion — oignon/onion — onion"); Asia uses "English (romanization, native)". Normalize to one.
- **Cantonese romanization:** Asia uses Jyutping with tone numbers (`goeng1`), which is what the prompt asked for.
  The app's current Hong Kong list uses Yale-style accents; switch to Jyutping when importing.
- **Shortcuts and salt:** amounts are per weight of food (e.g. "15-20 g oyster sauce seasons about 500 g food").
  For store-bought blends, both reports use the label rule `salt_g ≈ sodium_mg × 0.00254` (1 g sodium is about
  2.54 g salt) and subtract that from the added salt. This fits the app's "salt in grams" rule.
- **Coconut:** per current FDA guidance it is no longer a major tree-nut allergen. The app's allergen rule already
  says so.

## Conflicts with Bryan's calls (decide before importing)

1. **American flavors:** the research marks cinnamon and vanilla as sweet-only and Old Bay as Chesapeake-specific,
   not national. Bryan's call (2026-11-08) was to keep all three in American savory (he wants them usable
   beyond holiday baking). In the tree, `us_any` (burgers, barbecue, fast food: the export image) replaces
   "American"; decide where cinnamon, vanilla and Old Bay go.
2. **Filé powder:** Bryan removed it from Cajun; the research lists it in `us_cajun` (flavors and signature
   ingredients) and `us_creole`. Drop it at import unless Bryan changes his mind.

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

## Themes for writing the entries

- Every flavor list is a vocabulary to draw on, not a checklist: a Sichuan dish doesn't need Sichuan pepper, a
  Thai dish doesn't need coconut milk. Matches ChefBot's "use only the ones that suit this dish".
- The "Any" nodes are export images (US: burgers, barbecue, diner food; Mexico: tacos, salsa, guacamole, partly
  Tex-Mex; Caribbean: leans on Jamaican jerk, tropical fruit, rum, coconut; China: fried rice, dumplings, sweet-savory
  stir-fries; Japan: sushi, ramen, tempura, teriyaki; India: butter chicken, tikka masala, naan, biryani). Mark them
  internally as export profiles.
- Use "in the style of" rather than "authentic" when the user's pantry forces big substitutions.
