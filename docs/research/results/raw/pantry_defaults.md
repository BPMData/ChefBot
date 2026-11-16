# Pantry Defaults Research Notes (2026-11-15)

Research backing `tools/cuisine_pantry.json` for the 28 cuisines whose original research reports left `pantry_assumed` empty, plus a spot-check of the 45 cuisines that already had `pantry_assumed` data (especially the 23 Asian cuisines, which had only 2 to 4 hedged items in `asia.json`).

For each cuisine: what an ordinary home cook of that cuisine (cooking at home in the country or in a typical US household, noted below) keeps on hand week to week in the cupboard, fridge door, or freezer, excluding main proteins and fresh centerpiece vegetables.

## Part A: The 28 Researched Cuisines

### United States & Canada

- **`us_any` (American home cook, US)**
  - Sources: Samin Nosrat (*Salt, Fat, Acid, Heat*), Mark Bittman (*How to Cook Everything*), Irma S. Rombauer & Ethan Becker (*Joy of Cooking*).
  - Notes: Core US everyday kitchen relies on neutral cooking oil, butter, all-purpose flour, eggs, onions and garlic, ketchup and yellow mustard, mayonnaise, chicken broth, apple cider vinegar, and brown sugar. Added `apple cider vinegar` to the draft (keeps indefinitely, core acid across dressings, slaws, braises, and sauces).

- **`us_cajun` (Cajun home cook, southern Louisiana / US)**
  - Sources: Donald Link (*Real Cajun*), Isaac Toups (*Chasing the Gator*), Paul Prudhomme (*Chef Paul Prudhomme's Louisiana Kitchen*).
  - Notes: Everyday Cajun home kitchens keep the trinity (yellow onions, celery, green bell peppers), garlic, scallions and flat-leaf parsley, long-grain white rice, all-purpose flour and neutral oil (or bacon drippings/lard) for roux, Louisiana hot sauce, chicken stock, and bay leaves. Filé powder is excluded per `tools/cuisine_overrides.json`. Dropped the draft's `"for a roux"` prose tag.

- **`us_creole` (New Orleans Creole home cook, Louisiana / US)**
  - Sources: Leah Chase (*The Dooky Chase Cookbook*), Paul Prudhomme (*Chef Paul Prudhomme's Louisiana Kitchen*).
  - Notes: Shares the trinity, long-grain white rice, garlic, and Louisiana hot sauce with Cajun cooking, plus butter and all-purpose flour, canned tomatoes, scallions and flat-leaf parsley, Worcestershire sauce, Creole mustard, and dried red kidney beans (a weekly Monday staple in New Orleans). Filé powder is excluded per `tools/cuisine_overrides.json`. Added `dried red kidney beans` and `scallions and flat-leaf parsley` (combining cleanly within 10 items).

- **`us_southern_soul` (Southern & Soul Food home cook, US)**
  - Sources: Edna Lewis (*The Taste of Country Cooking*), Toni Tipton-Martin (*Jubilee*), Bryant Terry (*Vegan Soul Kitchen*).
  - Notes: The draft missed two pillars emphasized by Lewis, Tipton-Martin, and Terry: **stone-ground grits** (paired with cornmeal as `"cornmeal and grits"`) and **dried black-eyed peas** (field peas). Also keeps all-purpose flour, buttermilk, bacon drippings or lard, neutral oil (trimmed `"for frying"`), onions and garlic, apple cider vinegar, hot sauce, and brown sugar or molasses.

- **`us_tex_mex` (Tex-Mex home cook, Texas / US)**
  - Sources: Robb Walsh (*The Tex-Mex Cookbook*), Lisa Fain (*The Homesick Texan Cookbook*).
  - Notes: Flour and corn tortillas, canned pinto or refried beans, long-grain white rice, chili powder and ground cumin, canned tomatoes or tomato sauce, onions and garlic, pickled jalapeños, Cheddar or Monterey Jack, and lard or neutral oil accurately represent everyday Texas-Mexican home pantries. Capitalized `Cheddar`.

### Mexico

- **`mx_any` (Mexican home cook, Mexico or US)**
  - Sources: Diana Kennedy (*The Essential Cuisines of Mexico*), Rick Bayless (*Authentic Mexican*), Pati Jinich (*Treasures of the Mexican Table*).
  - Notes: Per `docs/research/FINDINGS.md`, ground cumin leans Tex-Mex and northern Mexico rather than all of Mexico, so dropped `ground cumin` from `mx_any`. Replaced generic `"fresh and dried chiles"` with `"dried chiles (ancho, guajillo, árbol)"` (true shelf-stable pantry staples across Kennedy, Bayless, and Jinich). Kept corn tortillas or masa harina, dried or canned black or pinto beans, white rice, white onions and garlic, tomatoes, Mexican oregano, lard or neutral oil, and limes.

- **`mx_northern_baja` (Northern Mexican & Baja home cook, northern Mexico / US)**
  - Sources: Pati Jinich (*Foods of La Frontera*), Diana Kennedy (*The Essential Cuisines of Mexico*).
  - Notes: Wheat flour tortillas dominate over corn in the north, alongside dried pinto beans, dried red chiles (guajillo, ancho, chiltepín), white onions and garlic, tomatoes, Mexican oregano and ground cumin (cumin is genuinely northern), lard or neutral oil, limes, and queso fresco. Updated the draft's vague `chile colorado` label to name the dried chiles and added `tomatoes` and `ground cumin`.

- **`mx_central_oaxacan` (Central Mexican & Oaxacan home cook, central/southern Mexico)**
  - Sources: Diana Kennedy (*Oaxaca al Gusto*), Bricia Lopez (*Oaxaca: Home Cooking from the Heart of Mexico*), Roberto Santibáñez (*Truly Mexican*).
  - Notes: Corn tortillas or masa harina, dried black beans, dried chiles (ancho, guajillo, pasilla), white onions and garlic, tomatoes and tomatillos, lard or neutral oil, Mexican oregano, dried avocado leaves (*hoja de aguacate*), and sesame seeds with Ceylon cinnamon (*canela*, foundational to Oaxacan moles and everyday guisados). Moved `chipotle` out of the dried chile list since ancho, guajillo, and pasilla are the dry cupboard backbone; added `sesame seeds and Ceylon cinnamon (canela)`.

- **`mx_yucatan` (Yucatecan home cook, Yucatán peninsula)**
  - Sources: David Sterling (*Yucatán: Recipes from a Culinary Expedition*), Diana Kennedy (*The Essential Cuisines of Mexico*).
  - Notes: Achiote paste (*recado rojo*), sour orange juice (or orange and lime juice), habanero chiles, dried black beans, corn tortillas, red and white onions, garlic, lard or neutral oil, and Mexican oregano with allspice. Tightened phrasing to match house style.

### Caribbean

- **`caribbean_any` (Pan-Caribbean home cook, islands or diaspora)**
  - Sources: Jessica B. Harris (*Sky Juice and Flying Fish*, *Iron Pots and Wooden Spoons*).
  - Notes: Draft had 7 items; added `allspice and curry powder` and `neutral oil` to reflect the shared English-speaking and broader Caribbean store (Jamaica, Trinidad, Barbados, Guyana), alongside long-grain white rice, dried or canned beans or pigeon peas, onions/garlic/bell peppers, scallions and fresh thyme, limes, Scotch bonnet or hot pepper sauce, and coconut milk.

- **`caribbean_cuban` (Cuban home cook, Cuba or diaspora)**
  - Sources: Nitza Villapol (*Cocina Criolla*), Maricel Presilla (*Gran Cocina Latina*).
  - Notes: Draft had 9 items; added `tomato sauce or tomato paste` (essential for Cuban *picadillo*, *ropa vieja*, and *potajes* in Villapol and Presilla), alongside long-grain white rice, dried black beans, olive oil, garlic, onions and green bell peppers, sour orange juice (or orange and lime), ground cumin and dried oregano, bay leaves, and dry white cooking wine (*vino seco*).

- **`caribbean_puerto_rican` (Puerto Rican home cook, Puerto Rico or US diaspora)**
  - Sources: Illyanna Maisonet (*Diasporican*), Von Diaz (*Coconuts & Collards*), Maricel Presilla (*Gran Cocina Latina*).
  - Notes: Medium-grain white rice, sofrito (*recaíto*, kept in fridge/freezer), canned or dried pink beans, pigeon peas (*gandules*), adobo seasoning, annatto (*achiote*) or sazón, olives and capers (*alcaparrado*), canned tomato sauce, olive oil, and white or cider vinegar (Maisonet and Diaz emphasize oil/lard and vinegar as foundational daily pantry items). Removed prose `"homemade or frozen"`.

- **`caribbean_jamaican` (Jamaican home cook, Jamaica or diaspora)**
  - Sources: Norma Shirley (Jamaican culinary profiles/anthologies), Jessica B. Harris (*Sky Juice and Flying Fish*).
  - Notes: Draft omitted **Jamaican curry powder** and **browning sauce or soy sauce** (essential for curried dishes, brown stew, and oxtail) and fresh ginger. Added `Jamaican curry powder`, `browning sauce or soy sauce`, and combined `garlic, onions and fresh ginger` alongside long-grain white rice, dried red kidney beans, coconut milk, scallions, fresh thyme, Scotch bonnet peppers, and allspice (pimento) berries.

### South America

- **`brazilian` (Brazilian home cook, Brazil)**
  - Sources: *Dona Benta: Comer Bem*, Leticia Moreinos Schwartz (*The Brazilian Kitchen*), Neide Rigo (*Come-se*), Bela Gil (*Bela Cozinha*).
  - Notes: Long-grain white rice, dried black or carioca beans, garlic and onions, cassava flour (*farinha de mandioca*, not just premade farofa), neutral oil, limes, parsley and scallions (*cheiro-verde*), bay leaves (standard in *feijão* in *Dona Benta* and Schwartz), and tomatoes. Kept *azeite de dendê* out as regional (Bahian), matching `FINDINGS.md`.

- **`peruvian` (Peruvian home cook, Peru)**
  - Sources: Gastón Acurio (*Peru: The Cookbook*), Virgilio Martínez (*The Latin American Cookbook*).
  - Notes: Draft was strong (limes, red onions, *ají amarillo* and *ají panca* pastes, garlic, fresh cilantro, white rice, potatoes, ground cumin, evaporated milk) but omitted **soy sauce (*sillao*)**, which `FINDINGS.md` and Acurio highlight as a daily national Peruvian staple via *chifa* (*lomo saltado*, *arroz chaufa*). Combined the two *ají* pastes into `"ají amarillo and ají panca pastes"` to include `"soy sauce (sillao)"` within 10 items.

- **`argentinian` (Argentinian home cook, Argentina)**
  - Sources: Francis Mallmann (*Seven Fires*), Narda Lepes (*Comer y pasarla bien*).
  - Notes: Per `FINDINGS.md`, everyday Argentine home cooking relies heavily on Italian-Argentine staples (pasta, milanesa, pizza, tarta) alongside *asado* and chimichurri. Replaced generic `"coarse salt for grilling"` (salt is already in base generic staples) and added `onions`, `plain breadcrumbs (pan rallado)` (for milanesas), and `dried pasta`, while using the local term `"dried oregano and crushed red chile (ají molido)"`.

### Italy, Western Europe, Greece & Russia

- **`italy_any` (International / general Italian home cook)**
  - Sources: Marcella Hazan (*Essentials of Classic Italian Cooking*), `FINDINGS.md` (Third batch notes).
  - Notes: Added `butter` (cornerstone of Hazan's classic sauces alongside olive oil) to dried pasta, extra-virgin olive oil, canned plum tomatoes or passata, garlic and onions, a wedge of Parmesan, dried oregano, black pepper, and Arborio rice. Kept balsamic vinegar out per `FINDINGS.md`.

- **`northern_italy` (Northern Italian home cook, northern Italy)**
  - Sources: Marcella Hazan (*Essentials of Classic Italian Cooking*), Rachel Roddy (*Two Kitchens*).
  - Notes: Added `extra-virgin olive oil` and `garlic` alongside butter, Parmigiano-Reggiano, risotto rice (Carnaroli or Arborio), coarse cornmeal (polenta), onions/carrots/celery (*soffritto*), dry white wine, broth, and dried egg pasta.

- **`southern_sicilian_italy` (Southern Italian & Sicilian home cook)**
  - Sources: Rachel Roddy (*Two Kitchens*, *My Kitchen in Rome*).
  - Notes: Roddy highlights dried legumes (chickpeas, lentils, white beans) as a rural southern/Sicilian staple alongside extra-virgin olive oil, dried durum-wheat pasta, canned tomatoes and passata, garlic, dried chile (*peperoncino*), dried oregano, salt-packed capers and anchovies, pecorino or ricotta salata, and plain breadcrumbs (*pangrattato*). Added `dried chickpeas or white beans` and removed `"for toasting"` prose.

- **`french` (French home cook, France or US)**
  - Sources: Patricia Wells (*The French Kitchen Cookbook*, *Bistro Cooking*).
  - Notes: Included `olive oil` alongside butter (`"butter and olive oil"`, reflecting Provençal and modern French kitchens in Wells) and `garlic` and `onions` alongside shallots (`"shallots, onions and garlic"`), keeping Dijon mustard, dry white wine, red wine vinegar, crème fraîche or heavy cream, thyme and bay leaves, all-purpose flour, chicken stock, and eggs.

- **`spanish` (Spanish home cook, Spain)**
  - Sources: Claudia Roden (*The Food of Spain*), Penelope Casas (*The Foods and Wines of Spain*), José Andrés (*Made in Spain*), `FINDINGS.md`.
  - Notes: Per `FINDINGS.md`, `pimentón` is not universally smoked (Murcia's isn't), so changed `"smoked paprika (pimentón)"` to `"paprika (pimentón)"`. Roden and Casas also emphasize **lentils** alongside chickpeas and **potatoes** as daily Spanish cupboard staples, so updated to `"dried chickpeas and lentils"` and `"potatoes"` (combining `"garlic and onions"` to stay within 10 items).

- **`greek` (Greek home cook, Greece)**
  - Sources: Diane Kochilas (*The Country Cooking of Greece*, *The Ikaria Way*, *My Greek Table*).
  - Notes: Kochilas emphasizes **Kalamata olives** and **tomato paste** alongside extra-virgin olive oil, lemons, dried oregano, garlic and onions, feta, red wine vinegar, canned tomatoes, Greek yogurt, and dried beans or lentils. Combined `"garlic and onions"` and `"canned tomatoes and tomato paste"` to include `"Kalamata olives"`.

- **`russian` (Russian home cook, Russia)**
  - Sources: Darra Goldstein (*A Taste of Russia*, *Beyond the North Wind*), Anya Von Bremzen (*Please to the Table*).
  - Notes: Added `sauerkraut or brined pickles` (emphasized across Goldstein and Von Bremzen as the foundational preserved winter staple, producing *rassol* brine) to sunflower oil, butter, sour cream (*smetana*), fresh dill, onions and carrots, potatoes/beets/cabbage, buckwheat groats (*grechka*), rye bread, and bay leaves.

### Africa

- **`moroccan_north_african` (Moroccan home cook, Morocco)**
  - Sources: Paula Wolfert (*The Food of Morocco*, *Couscous and Other Good Food from Morocco*).
  - Notes: Wolfert documents **tomato paste** and **green or black olives** as everyday Moroccan kitchen staples alongside olive oil, preserved lemons, garlic and onions, ground cumin/sweet paprika/ginger/turmeric, cinnamon, couscous, fresh cilantro and parsley, and chickpeas. Added both (`tomato paste`, `green or black olives`) for 10 items.

- **`ethiopian` (Ethiopian home cook, Ethiopia or US diaspora)**
  - Sources: Yohanis Gebreyesus (*Ethiopia: Recipes and Traditions from the Horn of Africa*), Marcus Samuelsson (*Marcus Off Duty*).
  - Notes: Draft omitted **neutral oil** (essential for Ethiopian Orthodox fasting days, which forbid *niter kibbeh* for much of the year, as noted in `FINDINGS.md`) and **turmeric** (for mild *alicha* stews) and split peas (*kik*). Added `neutral oil`, `turmeric`, and `"red lentils (misir) and split peas"`.

- **`egyptian` (Egyptian home cook, Egypt)**
  - Sources: Claudia Roden (*The New Book of Middle Eastern Food*).
  - Notes: Roden highlights **tahini** and **white vinegar** (essential for *koshary*, *fattah*, *ful*, and *salatet tahina*) as ubiquitous in Egyptian kitchens. Combined dried fava beans and chickpeas (`"dried fava beans and chickpeas"`) and vinegar with lemons (`"white vinegar and lemons"`) to include `tahini` within 10 items.

- **`nigerian` (Nigerian home cook, Nigeria or diaspora)**
  - Sources: Yewande Komolafe (*My Everyday Lagos Kitchen*), Ozoz Sokoh (*Chop Chop: Cooking the Food of Nigeria* / Kitchen Butterfly).
  - Notes: Komolafe and Sokoh highlight **neutral oil** alongside red palm oil, plus **fresh ginger and garlic** alongside onions in everyday Nigerian stew bases (*obe ata*, jollof). Updated `"palm oil"` to `"red palm oil and neutral oil"` and `"onions"` to `"onions, garlic and ginger"`, and specified `"long-grain parboiled rice"` (the Nigerian jollof standard).

- **`senegalese` (Senegalese home cook, Senegal or diaspora)**
  - Sources: Pierre Thiam (*Senegal*, *Simply West African*), `FINDINGS.md`.
  - Notes: Draft omitted **Dijon mustard**, which is central to *yassa* (one of Senegal's three pillars alongside *ceebu jën* and *mafé*). Combined `"onions and garlic"` to add `"Dijon mustard"`, and removed the prose parenthetical from `"unsweetened peanut butter"`.

---

## Part B: Spot-Check of the Other 45 Cuisines

Checked against `docs/research/results/{asia,additions,additions_americas,additions_europe,third_batch,near_east_run2}.json` and authoritative cookbooks for the 23 Asian cuisines (where `asia.json` only had 2 to 4 hedged items).

### Asian Cuisines (23)
- **China (`china_any`, `sichuan`, `hunan`, `cantonese`, `shandong`, `jiangsu`, `zhejiang`, `fujian`, `anhui`)**
  - Sources: Fuchsia Dunlop (*Every Grain of Rice*, *The Food of Sichuan*, *Revolutionary Chinese Cookbook*, *Land of Fish and Rice*), Eileen Yin-Fei Lo (*Mastering the Art of Chinese Cooking*), Grace Young (*Stir-Frying to the Sky's Edge*).
  - Changes from draft: Clarified generic `"rice"` to `"white rice"` across regional lists; added `scallions` and `neutral oil` where missing (`sichuan`, `hunan`, `jiangsu`, `zhejiang`, `fujian`); added `garlic` and `toasted sesame oil` to `cantonese`; added `Shaoxing rice wine` and tightened `"wheat flour for buns and noodles"` -> `"all-purpose wheat flour"` in `shandong`; added `garlic` and `"rapeseed or neutral oil"` in `anhui`.
- **Japan (`japan_any`, `kanto`, `kansai`)**
  - Sources: Elizabeth Andoh (*Washoku*, *Kansai Cookbook*), Shizuo Tsuji (*Japanese Cooking: A Simple Art*), Nancy Singleton Hachisu (*Japan: The Cookbook*).
  - Changes from draft: Added `toasted sesame oil` to `japan_any`, `rice vinegar` to `kanto` and `kansai` (one of the foundational *sashisu-se* seasonings), and tightened `kansai`'s `"thick Worcestershire-style sauce (for okonomiyaki)"` -> `"Japanese brown sauce (tonkatsu or okonomiyaki sauce)"`.
- **South & Central Asia (`india_any`, `north_india`, `south_india`, `pakistani`, `afghan`)**
  - Sources: Madhur Jaffrey (*An Invitation to Indian Cooking*), Meera Sodha (*Made in India*), Chandra Padmanabhan (*Dakshin*), `additions.json`.
  - Changes from draft: Added `plain yogurt` to `india_any` and `north_india`; added `ground coriander` (a core North Indian *masala dabba* spice) to `north_india`; added `shallots or onions` and specified `"short- or medium-grain rice"` in `south_india`. `pakistani` and `afghan` already matched `additions.json` cleanly (omitting generic salt).
- **Korea & Southeast Asia (`korean`, `thai`, `vietnamese`, `filipino`, `indonesian`, `malaysian_singaporean`)**
  - Sources: Maangchi (*Maangchi's Real Korean Cooking*), Hyosun Ro (*Korean Bapsang*), Leela Punyaratabandhu (*Simple Thai Food*), Andrea Nguyen (*Into the Vietnamese Kitchen*, *Vietnamese Food Any Day*), Yasmin Newman (*7000 Islands*).
  - Changes from draft: Added `dried kelp (dasima) and dried anchovies` (essential Korean *yuksu* soup stock staples in Maangchi and Hyosun Ro) to `korean`; clarified `"rice"` -> `"white rice"` in `filipino`, `indonesian`, and `malaysian_singaporean`; added `neutral oil` to `malaysian_singaporean`. `thai` and `vietnamese` matched the sources well as drafted.

### Remaining 22 Researched Cuisines (Americas, Europe, Near East, North Africa)
- Spot-checked against `additions.json`, `additions_americas.json`, `additions_europe.json`, `third_batch.json`, and `near_east_run2.json`.
- Changes from draft:
  - `us_new_mexican`: Added `Cheddar and Monterey Jack` (present in `additions_americas.json` research, omitted from draft).
  - `us_new_england`: Removed hedging parenthetical `"(especially in northern New England)"` from `"pure maple syrup"`.
  - `portuguese`: Reworded `"crusty bread, including stale"` -> `"crusty or day-old bread"`.
  - `hungarian`: Dropped `"(for nokedli)"` parenthetical from `"all-purpose flour and eggs"`.
  - `us_hawaiian`, `us_italian_american`, `quebecois`, `colombian`, `roman_central_italy`, `british`, `irish`, `nordic`, `german`, `austrian`, `polish`, `czech`, `georgian`, `palestinian_levantine`, `persian`, `turkish`, `tunisian`, `algerian`: All matched their researched lists cleanly, with brand names and generic salt already excluded.
