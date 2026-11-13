# **Regional Culinary Knowledge Base: Quebecois, New Mexican, Hawaiian, and Colombian Nodes**

Four American regional cuisines—Quebecois (quebecois), New Mexican (us_new_mexican), Hawaiian and Local (us_hawaiian), and Colombian (colombian)—resist one-size-fits-all recipe generation because mainstream English-language food writing routinely flattens them into restaurant clichés1. For an AI writing recipes from a user's pantry, the primary rule across the consulted culinary historians, regional authorities, and national cultural institutions is that each node requires an explicit default register rather than a generic stereotype: modern Hawaii Local Food rather than mainland tiki pineapple tropes5, everyday Quebecois home cooking rather than seasonal *cabane à sucre* excess3, minimalist New Mexican chile-and-pinto cooking rather than cumin-heavy Tex-Mex4, and mild Andean Colombian staples rather than a flattened caricature of six distinct regions2.
Throughout this report, culinary rules are framed as tendencies (usually, often, in classic versions) rather than absolutes unless the consulted authorities show uniform agreement, and gaps or conflicting commercial nutrition panels are marked as LOW CONFIDENCE. The required summary of surprises and disputes, the verification audit table, the regional steering analysis with weight-based shortcut salt conversions, and the complete 13-field JSON array appear in sequence below.

## **1. Summary of Biggest Surprises and Disputes**

The sharpest culinary dispute uncovered in the consulted sources centers on cumin in New Mexican cooking. Prominent Santa Fe cookbook author Cheryl Alters Jamison and local restaurant critics maintain that classic New Mexican green and red chile sauces use no cumin, characterizing heavy cumin alongside *ancho* chili powder as a defining marker of Tex-Mex rather than New Mexico4. Yet at least one popular recipe blog in the consulted literature explicitly calls for cumin and cinnamon in New Mexican *carne adovada* red chile sauce14. Because popular practice diverges at the margins, a recipe engine should treat cumin as usually omitted in classic New Mexican dishes rather than enforcing an absolute ban.
In Hawaii, terminology itself dictates what an AI should cook by default. Culinary historian Rachel Laudan and *Kānaka Maoli* (Native Hawaiian) commentators emphasize that "Hawaiian food" strictly designates Native Hawaiian fare—such as *poi*, *kālua* pork, *laulau*, *lomi* salmon, and pre-contact *poke*—whereas the everyday diet across the islands is "Local Food," a 20th-century plantation-era synthesis uniting Native Hawaiian, Anglo-American, Chinese, Japanese, Korean, Filipino, and Portuguese foodways1. Contrary to mainland tourist menus, Hawaii has never designated an official state fruit, and adding pineapple to burgers, chicken, pizza, or poke is a mainland "Polynesian Pop" tiki cliché rather than traditional Local or Native Hawaiian cooking6.
Quebecois cuisine presents a dual misconception involving maple syrup and meat pies. Academic theses and family culinary memoirs show that everyday home cooking revolves around practical winter-storage dishes and 20th-century staples—*soupe aux pois*, *pâté chinois*, *ragoût de pattes et de boulettes*, *cretons*, *pâté à la viande*, freshwater fish, and apple or blueberry desserts—rather than pouring maple syrup over every savory plate, a practice tied mainly to seasonal *cabane à sucre* feasts and specific dishes like *fèves au lard* or glazed ham3. Even *tourtière* splits internally between ground-meat pie spiced with savory, clove, nutmeg, and allspice and Saguenay-Lac-Saint-Jean's *tourtière du Lac-Saint-Jean*, a deep Dutch-oven pot pie of cubed beef, pork, veal or venison, and potatoes flavored with thyme, bay leaf, and savory7.
Colombian cuisine surprises outside cooks primarily through its extreme regional fragmentation and mild everyday seasoning. Documented across 17 volumes of the Ministry of Culture's *Biblioteca Básica de Cocinas Tradicionales de Colombia*, the country spans six distinct natural food regions—Andean, Caribbean, Pacific, Orinoquía (Llanos), Amazon, and Insular—with no single national dish2. Main dishes are typically mild and aromatic rather than fiery, with heat commonly offered on the side via *ají*2. Commercial Colombian shortcuts also show severe labeling conflicts: export distributor pages for Triguisar directly contradict one another on whether the blend contains no salt or high salt23, while crowd-sourced databases for Ricostilla powder show conflicting salt values27. Finally, several sub-topics lacked direct coverage in the consulted sources—notably *guascas* and individual *hierbas de azotea* species in Colombia, Filipino-specific Local condiments in Hawaii, systematic comparisons between Quebecois and metropolitan French cooking, and dessert-only spice profiles outside Hawaii—and are therefore flagged LOW CONFIDENCE.

## **2. Verification and Fact-Check Audit**

The query referenced a fact-check specification "described at the end," but no separate claim list or fact-check rubric was included at the end of the prompt. To ensure full transparency for the recipe engine, the audit table below verifies the most consequential culinary rules, source disagreements, commercial salt calculations, and evidence gaps across the consulted authorities, retail labels, crowd-sourced databases, and culinary commentary.

| Node | Claim or Rule Checked | Evidence Status and Source Attribution | Confidence |
| :---- | :---- | :---- | :---- |
| us_new_mexican | Classic New Mexican cooking omits cumin | Supported by Jamison (quoted in local food commentary)4, *The Homesick Texan* (attributing cumin to Tex-Mex)13, and New Mexico culinary blogs11; contradicted by a general recipe blog adding cumin to *carne adovada*14. Treat as usually omitted, not absolute. | Medium-High (contested in popular blogs) |
| us_new_mexican | Red and green New Mexico chile are ripeness stages of the same plant | Confirmed by Jamison and encyclopedic summaries of NMSU Chile Pepper Institute work: green pods (July–October) ripen to red on the vine (October–December), adding earthiness and often more heat9. | High |
| us_new_mexican | Dessert-only spice profile | Consulted articles mention Spanish-origin *flan* and *natillas*, honey on *sopaipillas*9, and a light magazine reference to macaroons4, without detailing dessert-only spices. | LOW CONFIDENCE |
| us_hawaiian | "Local Food" is everyday island fare, separate from Native Hawaiian | Confirmed by historian Rachel Laudan1, *Kānaka Maoli* forum accounts16, and Hawaii cultural guides6. App should default to Local Food. | High |
| us_hawaiian | Filipino and Portuguese influences in Local Food | Both groups' plantation roles in creating the plate lunch are documented17, and Portuguese sausage in *loco moco* is confirmed31; specific Filipino-Local condiments or dishes lack details in the consulted sources. | Medium (Portuguese) / LOW CONFIDENCE (Filipino) |
| us_hawaiian | Aloha Shoyu sodium and sugar metrics | Safeway retail nutrition panel lists 780 mg sodium and 1 g sugar per 15 mL (1 tbsp)32; OpenFoodFacts crowd-sourced labels list 5.07–5.20 g sodium (12.67–13.0 g salt) and 6.67 g sugar per 100 mL33, matching mathematically (780 × 100 / 15 = 5,200 mg). | High |
| quebecois | Minced-meat *tourtière* vs. *tourtière du Lac-Saint-Jean* | Confirmed by an academic thesis7, Julian Armstrong references8, and regional accounts20: minced meat and warm spices vs. deep Dutch-oven cubed meats, potatoes, thyme, bay, and savory. | High |
| quebecois | Direct contrast between Quebecois and metropolitan French cooking | French-colonial histories by Francœur and Lambert are cited36, and dishes like *rillettes*-like *cretons* alongside *coquilles St-Jacques* and *pâté chinois* are documented7, but no source excerpt directly compares Quebecois with modern French cooking. | LOW CONFIDENCE |
| colombian | *Guascas* and individual *hierbas de azotea* species | The Cancillería showcase confirms Pacific *hierbas de azotea* as a category, but contains zero mentions of *guascas* and does not itemize individual *azotea* herbs10. | LOW CONFIDENCE |
| colombian | Triguisar and Ricostilla salt content | OpenFoodFacts cube panel for Ricostilla reports 48.18 g salt (19.27 g sodium) per 100 g39, whereas the Ricostilla powder page prints an inconsistent 13.23 g salt vs. 54.5% ingredient estimate27. Triguisar labels conflict sharply between 0 g/no salt23 and high salt25. | Medium (Ricostilla cubes) / LOW CONFIDENCE (Triguisar & powder) |

## **Regional Culinary Profiles and App Steering Rules**

### **New Mexican (us_new_mexican)**

New Mexican cooking belongs to the Rio Grande corridor of the US Southwest, stretching from the southern Hatch Valley (Arrey to Hatch) through Albuquerque and Santa Fe into northern mountain valleys near Chimayó, Dixon, Embudo, and Taos4. According to Jamison, it is grounded in ancestral Puebloan "Three Sisters" agriculture—specifically blue and starchy corn, speckled pinto beans, and summer squash (*calabacitas*)—integrated with Spanish colonial wheat, livestock, lard, and dairy desserts such as *flan* and *natillas*9. This dual heritage sets New Mexican cooking firmly apart from both Tex-Mex and interior Mexican cuisines. Compared with Tex-Mex, which leans on heavy cumin, *ancho* chili powder, mashed refried beans, and richer cheese-heavy preparations13, classic New Mexican dishes are lighter40, usually omit cumin4, serve speckled pinto beans whole in their broth9, and reserve the spelling "chili" solely for Texas meat stew rather than New Mexico "chile"11. Compared with interior Mexican regional cooking—which employs varied dried chiles with raisin or fruity notes such as *pasilla*, *ancho*, and *habanero*41—New Mexican cuisine centers on local *Capsicum* peppers thickened in a wheat-flour roux, flat stacked blue-corn enchiladas, wheat-flour tortillas, and *sopaipillas* served alongside savory meals with a drizzle of honey to temper chile heat9.
The engine must treat red and green New Mexico chile as two ripeness stages of the same cultivar rather than separate crops. Planted in spring, pods harvested green from July through October have a crisp, vegetal, garlic-and-onion pungency28; they are typically flame-roasted, peeled, and chopped for green chile stew, *calabacitas*, and New Mexico's signature green chile cheeseburger4. Pods allowed to ripen on the plant from October through December turn red, gaining earthiness, subtle sweetness, and often higher heat before being dried—traditionally in *ristras*—and blended or milled for smooth sauces over stacked enchiladas, *carne adovada*, posole, or mashed potatoes4. While "Hatch" specifically designates valley-grown chiles protected by a 2012 New Mexico law and rooted in New Mexico State University breeding dating to Dr. Fabián García in 1894 (including *New Mexico 6-4*, *Big Jim*, and *Sandia*)28, northern valleys prize sweet, smoky *Chimayó* and Pueblo landraces (Acoma, Isleta, Zia)28. Ordering or plating both red and green sauces together on one dish is universally termed "Christmas"4.

### **Hawaiian and Local (us_hawaiian)**

Because every word in Hawaii's food vocabulary carries historical weight, historian Rachel Laudan and *Kānaka Maoli* sources note that "Hawaiian food" strictly denotes Native Hawaiian cuisine1. Pre-contact Polynesian settlers developed agriculture and fishing around taro (*kalo*, pounded into *poi* or *paʻiʻai*), sweet potato, *kālua* pig slow-steamed in an underground *imu* lined with hot rocks and wrapped in ti and banana leaves, *laulau*, *haupia*, and raw fish or octopus seasoned with *paʻakai ʻalaea* sea salt, *limu* seaweed, and roasted crushed *kukui* nut (*ʻinamona*)1. After Western contact and plantation-era migration, salted salmon was adapted into *lomi-lomi* salmon alongside tomatoes and scallions6. Today, however, everyday eating across the islands is "Local Food," a mid-20th-century public food culture forged on sugar and pineapple plantations where Native Hawaiian, Anglo-American, Chinese, Japanese, Korean, Filipino, and Portuguese workers shared meals15. For an ingredient-driven home recipe app, the default should be **Local Food**, while keeping genuine stovetop adaptations of Native Hawaiian dishes separately and accurately labeled so *Spam musubi*, *loco moco*, or plate lunches are never misattributed as Native Hawaiian1.
Local Food centers on the **plate lunch**—two scoops of white rice, creamy macaroni salad, and a savory protein—alongside *loco moco* (white rice, hamburger patty, brown gravy, fried egg, invented in Hilo), *Spam musubi*, *saimin* noodle soup, *manapua* pork buns, North Shore garlic butter shrimp, and modern *poke*5. Each migrant community left clear markers: Japanese *shoyu* (sweetened local soy sauce), *nori*, *ogo*, *Hon Dashi*, and *furikake*32; Chinese *char siu* five-spice seasoning, *manapua*, and *crack seed*15; Korean *gochugaru* chili flakes in modern poke46; Portuguese plantation heritage and Portuguese sausage variations in *loco moco*17; and Anglo-American beef patties, gravy, mayonnaise, and WWII canned Spam15. Filipino laborers are explicitly documented alongside these groups in assembling the plate lunch17, though specific Filipino-Local condiments or dishes were not detailed in the consulted sources (LOW CONFIDENCE). Above all, the app must guard against tourist-menu clichés: Hawaii has no official state fruit18, and putting pineapple on pizza, burgers, chicken, or skewers reflects mainland tiki culture rather than local cooking6, just as mainland poke bowls piled with avocado, mango, cucumber, and spicy mayo diverge from Hawaii's clean, lightly dressed cubed fish16.

### **Quebecois (quebecois)**

Academic food studies and Quebec family memoirs demonstrate that Quebecois cooking operates across three separate spheres that an AI should never conflate3. Everyday home cooking centers on frugal winter-pantry staples and mid-century family meals documented in Lac-Saint-Jean and Montreal-area accounts: yellow split-pea soup (*soupe aux pois*) with salt pork and summer savory, *pâté chinois* (ground beef, corn, mashed potatoes), *ragoût de pattes et de boulettes*, spiced ground-pork *cretons* spread on toast, baked beans (*fèves au lard*) simmered with molasses or maple syrup, ground-meat *pâté à la viande*, freshwater fish (*doré*, *achigan*, smoked sturgeon), game, apple crisp (*croustade aux pommes*), and wild blueberry pie, alongside modern family staples such as homemade lasagna or macaroni with soy sauce7. The spring *cabane à sucre* (sugar shack) forms a distinct seasonal ritual around boiling maple sap, serving communal platters of crisp fried salted pork fatback (*oreilles de crisse*), tall oven-baked cast-iron omelettes, *fèves au lard*, *soupe aux pois*, *cretons*, *tourtière*, maple pie (*tarte au sirop d'érable*), *grand-pères au sirop d'érable*, and boiled maple taffy poured over snow (*tire d'érable*)8. Restaurant cooking splits further between roadside diner *poutine* (often relying on commercial sauces like St-Hubert)52 and modern haute sugar shacks exemplified by Martin Picard's *Au Pied de Cochon* and *Érablière Shefford*, which graft foie gras, lobster bisque, and blood sausage onto rustic templates19.
Although historians Jean-Marie Francœur and Michel Lambert trace Quebec's culinary origins to New France36 and classic dishes share structural DNA with France—such as *cretons* resembling French *rillettes*8 alongside family preparations of *soupe à l'oignon gratinée* and *coquilles St-Jacques*7—no consulted source excerpt provided a direct systematic comparison contrasting Quebecois with metropolitan French cooking (LOW CONFIDENCE). What the documented repertoire clearly shows is a divergence driven by harsh winters, lumber camps (source of Mauricie *oreilles de crisse*), wild berries and game, maple sap, heavy reliance on cured pork and lard, summer savory (*sarriette*) and warming baking spices in meat pies, and New England or British borrowings such as *pâté chinois* and Boston-inspired baked beans7. Regional pie terminology also matters: everyday Montreal-area *tourtière* is a shallow ground-pork-and-beef pie seasoned with savory, clove, nutmeg, and allspice, whereas *tourtière du Lac-Saint-Jean* is a deep Dutch-oven casserole of cubed meats and potatoes seasoned with thyme, bay leaf, and savory8.

### **Colombian (colombian)**

Colombian food cannot be reduced to one national recipe because geography splits the country into six natural culinary zones—Andean, Caribbean, Pacific, Orinoquía (Llanos), Amazon, and Insular—leading anthropologist Julián Estrada to remark, "Culinarily, Colombia is an entire continent"2. According to travel guides and Colombia's Ministry of Culture and Cancillería documentation, the cool **Andean** highlands (Bogotá, Medellín, Boyacá) favor generous soups, stews, native and *criolla* potatoes, beans, maize *arepas*, *ajiaco*, *bandeja paisa*, *sancocho*, and tripe stews2. The **Caribbean coast**, shaped by Indigenous, Spanish, African, and Levantine (Lebanese and Palestinian) communities, is anchored by coconut rice (*arroz con coco*), fried horse mackerel, *mango biche* ceviche, cassava *carimañolas*, and *arepa e' huevo*2. The **Pacific coast** centers on Afro-Colombian and Indigenous traditions built around coconut-milk *encocao*, *piangua* shellfish tamals, leaf-wrapped fish (*pandao*), *aborrajados*, fermented cane *viche*, and aromatic *hierbas de azotea* ("rooftop herbs")10. Meanwhile, the eastern **Orinoquía (Llanos)** plains emphasize beef (*pisillo llanero* stuffed into rice tamals), river fish, and *majule* (plantain and fresh-curd Christmas custard served with *cachapas* or *tungos*)2.
Because no single national dish represents all six regions2, a single-node recipe app should **default to mild Andean-style home cooking foundations**—*hogao* savory sauce, white rice, beans, potatoes, *arepas*, garlic, cumin, *achiote* (*color*), and tabletop *ají*—while flagging Caribbean/Pacific coconut seafood and Llanos meat-and-plantain traditions as distinct regional branches. The Cancillería showcase also leaves two important herbal gaps: it notes Pacific *hierbas de azotea* without listing their individual botanical species, and it never mentions *guascas* (often cited elsewhere for Bogotá *ajiaco*)10; both omissions are flagged LOW CONFIDENCE.

## **Commercial Shortcuts and Weight-Based Salt Conversions**

Because home cooks frequently rely on regional sauces, dry spice packets, and bouillons, the table below records verified compositions, allergen risks, and weight-based salt conversions (using the standard sodium × 2.5 conversion factor alongside label-printed salt values).

| Node | Commercial Shortcut | Primary Ingredients | Salt / Sodium Benchmark | Weight-Based Swap Guidance | Allergen Notes |
| :---- | :---- | :---- | :---- | :---- | :---- |
| quebecois | St-Hubert Poutine Gravy Sauce (398 mL can)53 | Water (~89.4%), modified corn starch (~3.9%), salt, wheat flour (~1.8%), chicken broth/fat, hydrolyzed soy/corn protein, onion/garlic powder, vinegar, spices53 | OpenFoodFacts lists 1.75 g salt (0.7 g sodium) per 100 mL (~7.0 g per 398 mL can)53; *Les Trésors d'Érable* lists 1.44 g salt (volume unprinted, LOW CONFIDENCE)55 | Omit 1.75 g salt (~0.3 tsp) per 100 mL (~100 g) canned sauce used; replaces ~90–95 mL seasoned broth plus ~5.7 g starch and wheat flour53 | Wheat (gluten), soy, sulfites53; other St-Hubert sauces declare milk, egg, or barley56 |
| quebecois | Knorr Bovril Liquid Beef Concentrate (250 mL)57 | Water, salt, hydrolyzed soy/corn/wheat protein, MSG, modified corn starch, yeast extract, beef extract, wheat flour, spices57 | Retail listing reports 1,070 mg sodium (~2.68 g salt equiv) per 10 mL (2 tsp) serving57 | Omit ~2.7 g salt for every 10 mL concentrate added to gravy, soup, or stew | Soy, wheat, sulfites; may contain milk57 |
| us_new_mexican | BUENO Frozen Red Chile Puree (14 oz / 397 g)42 | Roasted/ground New Mexico red chile pods and water only58 | 0 g salt, 0 mg sodium58 | 397 g puree replaces roughly 12 boiled and blended dried pods42; add ~3–6 g (½–1 tsp) salt when simmering with water and roux42 | None in pure puree58; prepared BUENO Hot Enchilada Sauce contains lactose (milk), wheat gluten, and soy59 |
| us_hawaiian | Aloha Shoyu Original Soy Sauce32 | Water, wheat gluten, salt, sugar, fermented soybeans, caramel color, preservatives32 | Safeway lists 780 mg sodium (1.95 g salt equiv) and 1 g sugar per 15 mL (1 tbsp)32; OpenFoodFacts lists 12.67–13.0 g salt per 100 mL33 | Omit ~1.95 g salt per 15 mL (~13 g salt per 100 mL); swap with slightly diluted standard soy sauce plus 1 g sugar per 15 mL | Wheat (gluten), soy32 (separate gluten-free SKU exists60) |
| us_hawaiian | NOH Chinese Barbecue Char Siu Mix (72 g pouch)49 | Cane sugar, salt, powdered soy sauce (wheat, soy), 5-spice (ginger, aniseed, fennel, cinnamon, cloves), onion, garlic, Red 349 | H-E-B label lists 370 mg sodium and 11 g sugar per 12 g serving (2,220 mg sodium / ~5.55 g salt equiv and 66 g sugar per 72 g pouch)49 | Replace 72 g pouch with 66 g sugar + ~5.6 g salt + five-spice, onion powder, and garlic powder | Wheat, soy; shared equipment with tree nuts, eggs, milk49 |
| colombian | Triguisar *Condimento en Polvo* (70 g box)23 | Cumin, corn/rice starch, black pepper, annatto, turmeric, garlic, E102; **salt disputed**23 | **DISPUTED (LOW CONFIDENCE):** Ubuy UK says no salt24; Danish site lists salt in ingredients yet 0 g in table23; Lebanese and Polish sites warn of high salt25 | Read box before salting; food blog DIY swaps 1 tbsp each annatto, turmeric, garlic powder, cumin, and black pepper + 1 tsp salt (2,344 mg sodium / ~5.86 g salt per batch)61 | Celery declared on Danish distributor page23; no US Top 9 allergens declared in reviewed panels |
| colombian | Ricostilla *Caldo de Costillas* Cubes (Quala)39 | Salt (~55%), rice flour, flavors, sugar, hydrogenated fat, MSG, inosinate/guanylate, onion, celery, parsley, garlic, pepper, beef rib39 | OpenFoodFacts cube panel lists 48.18 g salt (19.27 g sodium) per 100 g39; powder page prints garbled 13.23 g salt (LOW CONFIDENCE)27 | Omit ~4.82 g salt (~1.93 g sodium) for every 10 g cube dissolved in a recipe | Celery declared27; check *Doña Gallina*62 and *salsa negra*10 labels separately (LOW CONFIDENCE) |

## **3. Cuisine Knowledge Base JSON**

```json
[
  {
    "id": "quebecois",
    "label": "Québécois",
    "subtitle": "Salt pork, savory, maple, spices",
    "about": "Quebecois cuisine comes from eastern Canada, spanning Montreal, the Mauricie woodlands, and the Saguenay-Lac-Saint-Jean region. Shaped by French colonists adapting to harsh winters alongside Indigenous ingredients, lumber-camp traditions, and New England and British neighbors, everyday home cooking centers on frugal, slow-simmered comfort food distinct from seasonal sugar-shack feasts. Representative dishes include soupe aux pois, tourtiere or pate a la viande, pate chinois, and feves au lard.",
    "flavors": [
      "sarriette (summer savory)",
      "sel (salt)",
      "oignon (onion)",
      "ail (garlic)",
      "clou de girofle (clove)",
      "muscade (nutmeg)",
      "toute-epice / piment de la Jamaique (allspice)",
      "thym (thyme)",
      "feuille de laurier (bay leaf)",
      "persil (parsley)",
      "feuilles de celeri (celery leaves)",
      "sirop d'erable (maple syrup, mainly in feves au lard, glazed ham, and sugar-shack dishes)"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      "lard sale (salted pork fatback or salt pork) -> US supermarket salt pork or unsmoked pork belly (smoked bacon alters traditional pea soup flavor)",
      "pois jaunes (dried yellow peas) -> dried yellow split peas (US supermarket bean aisle)",
      "bleuets (wild Quebec blueberries) -> frozen wild blueberries or standard fresh blueberries",
      "venaison de cerf ou d'orignal (venison or moose for Tourtiere du Lac-Saint-Jean) -> cubed beef chuck and pork shoulder",
      "dore / achigan / esturgeon fume (walleye, bass, or smoked sturgeon) -> mild flaky white freshwater fish or smoked trout"
    ],
    "pantry_assumed": [
      "pure maple syrup",
      "salt pork or pork lard",
      "dried yellow split peas",
      "potatoes and yellow onions",
      "summer savory (sarriette)",
      "warming pie spices (clove, nutmeg, allspice)",
      "all-purpose flour",
      "commercial poutine/brown gravy mix or liquid beef concentrate (often)"
    ],
    "techniques": [
      "Long, gentle simmering of dried-legume and cured-pork dishes (soupe aux pois, feves au lard, ragout de pattes et de boulettes)",
      "Lard-crust pie baking for minced-meat tourtiere and deep Dutch-oven Tourtiere du Lac-Saint-Jean",
      "Pan-rendering and crisping salted pork fatback (oreilles de crisse) and slow-cooking pork spreads (cretons)",
      "Boiling maple syrup over snow (tire d'erable) and poaching dumplings in maple syrup (grand-peres)"
    ],
    "shortcuts": [
      "St-Hubert Poutine Gravy Sauce (398 mL can): usually contains ~89.4% water, modified corn starch (~3.9%), wheat flour (~1.8%), salt, chicken broth/fat, hydrolyzed soy/corn protein, onion/garlic powder, vinegar, and spices; OpenFoodFacts lists 1.75 g salt (0.7 g sodium) per 100 mL (~7.0 g salt per 398 mL can), though an alternate distributor listing shows 1.44 g salt without serving volume (LOW CONFIDENCE). Omit ~1.75 g salt per 100 mL used, replacing roughly 90-95 mL seasoned broth and ~5.7 g thickener.",
      "Knorr Bovril Liquid Beef Bouillon Concentrate (250 mL): contains water, salt, hydrolyzed soy/corn/wheat proteins, MSG, beef extract, yeast extract, wheat flour, spices, and sulfites; retail nutrition panel lists 1,070 mg sodium (~2.68 g salt equiv) per 10 mL (2 tsp) serving — omit ~2.7 g salt for every 10 mL added."
    ],
    "allergen_notes": "Traditional home seasonings are largely free of major US allergens, though butter, cream, and eggs appear in salads, baked omelettes, and pies. Hidden wheat, soy, milk, and egg appear in popular commercial shortcuts: St-Hubert canned poutine sauce declares wheat (gluten) and soy (and other St-Hubert menu sauces declare milk, egg, or barley), while Knorr Bovril liquid beef concentrate contains soy and wheat and carries a may-contain milk warning.",
    "pitfalls": [
      "Treating seasonal cabane a sucre spreads (oreilles de crisse, giant baked omelettes) or restaurant poutine as everyday home cooking, overlooking staples like pate chinois, soupe aux pois, cretons, or home macaroni with soy sauce.",
      "Adding maple syrup indiscriminately to savory dishes; everyday soups, cretons, and meat pies usually remain savory unless styled specifically as maple ham, feves au lard, or sugar-shack dishes.",
      "Confusing Montreal-style minced-meat pate a la viande (spiced with clove, nutmeg, and allspice) with Tourtiere du Lac-Saint-Jean, a deep Dutch-oven pot pie of cubed beef, pork, veal or venison, and potatoes flavored with thyme, bay leaf, and savory.",
      "Assuming Quebecois cooking mirrors modern metropolitan French dining; the consulted sources lack a direct comparative treatise (LOW CONFIDENCE on exact French-vs-Quebec culinary divergence) and also omit detailed sweet-only baking spice profiles (LOW CONFIDENCE)."
    ],
    "sources": [
      "https://constellation.uqac.ca/id/eprint/5920/1/PlamondonLalancette_uqac_0862_10709.pdf",
      "https://www.collectionscanada.gc.ca/obj/thesescanada/vol2/002/MR75957.PDF",
      "http://degroupe.free.fr/PDF/cuisine/Genese%20de%20la%20cuisine%20Quebecoise.pdf",
      "https://quebecuisine.ca/employee/michel_lambert/",
      "https://archipel.uqam.ca/11430/1/M15380.pdf",
      "https://en.wikipedia.org/wiki/Tourti%C3%A8re",
      "Made in Quebec: A Culinary Journey, Julian Armstrong, 2014",
      "https://urbanguidequebec.com/cabanes-a-sucre-a-guide-to-quebec-sugar-shacks/",
      "https://willtravelforfood.com/2019/03/08/sugar-shack-cabane-a-sucre-montreal-2019/",
      "https://world.openfoodfacts.org/product/0066701001029/poutine-gravy-sauce-st-hubert",
      "https://www.st-hubert.com/en/nutritional.html",
      "https://caffeinecam.com/products/knorr-bovril-beef-bouillon-beef-gravy-250ml-imported-from-canada"
    ]
  },
  {
    "id": "us_new_mexican",
    "label": "New Mexican",
    "subtitle": "Red and green chile, pinto beans",
    "about": "New Mexican cuisine is rooted along the Rio Grande valley in the US Southwest, extending from the southern Hatch Valley past Albuquerque and Santa Fe into northern foothills around Chimayo and Taos. It evolved from Puebloan Three Sisters farming of corn, pinto beans, and squash layered with Spanish colonial wheat, livestock, lard, and dairy custards. Lighter and less heavily spiced than Tex-Mex, representative dishes include stacked blue-corn enchiladas, green chile stew, posole, and sopaipillas.",
    "flavors": [
      "chile verde (roasted New Mexico green chile)",
      "chile colorado / chile rojo (dried or pureed New Mexico red chile)",
      "chile de Chimayo (sweet-smoky northern New Mexico heirloom red chile)",
      "ajo (garlic)",
      "cebolla (onion)",
      "oregano (dried oregano)",
      "sal (salt)",
      "azucar (pinch of sugar occasionally added to balance red chile sauce)",
      "miel (honey, classic savory-meal condiment drizzled on sopaipillas)",
      "comino (cumin — DISPUTED: usually omitted in classic New Mexican sauces; occasional in modern adaptations, LOW CONFIDENCE)"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      "Hatch or New Mexico green chile (fresh or frozen roasted) -> US supermarket fresh Anaheim peppers (roasted and peeled) or canned fire-roasted green chiles (milder flavor)",
      "dried New Mexico or Chimayo red chile pods -> dried mild-to-medium New Mexico pods in supermarket Latin sections (avoid swapping with Tex-Mex ancho chili powder)",
      "blue corn tortillas or blue cornmeal -> yellow or white corn tortillas (alters color and toasted flavor)",
      "dried posole (nixtamalized hominy corn) -> canned white hominy, drained and simmered",
      "speckled pinto beans -> US supermarket dried or canned pinto beans (simmered whole rather than mashed)"
    ],
    "pantry_assumed": [
      "frozen roasted green chile",
      "dried red chile pods, powder, or frozen red chile puree",
      "dried pinto beans",
      "onions and garlic",
      "dried oregano",
      "all-purpose flour and neutral oil or pork lard (for sauce roux and sopaipillas)",
      "corn and flour tortillas"
    ],
    "techniques": [
      "Flame-roasting whole green chiles, steaming, peeling blistered skins, and chopping",
      "Cooking a light oil-or-lard and wheat-flour roux to simmer pureed red chile or chopped green chile into thickened sauce without scorching",
      "Slow back-of-the-stove simmering of whole speckled pinto beans and posole hominy",
      "Deep-frying leavened dough into hollow sopaipillas and layering flat stacked enchiladas"
    ],
    "shortcuts": [
      "BUENO Frozen Red Chile Puree (14 oz / 397 g): contains only roasted red chile pods and water with 0 g salt and no additives; 1 tub (397 g) replaces roughly 12 boiled and blended dried pods — add ~3-6 g (1/2-1 tsp) salt when diluting with water and a flour roux.",
      "Commercial Hot Enchilada Sauce (BUENO): contains water, roasted red chile, salt, modified corn starch, lactose, hydrolyzed corn/soy/wheat proteins, yeast extract, and onion powder; retail label lists 70 mg sodium (~0.18 g salt equiv) per serving across 8 servings (~1.4 g salt equiv per container, container net weight unverified — LOW CONFIDENCE), so withhold added salt until tasting."
    ],
    "allergen_notes": "Pure New Mexico chiles and frozen red chile purees contain no major US allergens. However, traditional homemade and restaurant red and green chile sauces usually hide wheat because they rely on a wheat-flour roux for body, and commercial prepared enchilada sauces frequently declare hidden milk (lactose), soy (hydrolyzed soy protein), and wheat gluten.",
    "pitfalls": [
      "Adding cumin and ancho-based Tex-Mex chili powder automatically; prominent New Mexican authorities stress omitting cumin so chile, garlic, and oregano lead, though some popular recipes include a pinch.",
      "Using the Texas meat-stew spelling 'chili' instead of 'chile', or defaulting to Tex-Mex mashed refried beans, rolled yellow-cheddar casseroles, and tomatillo salsas.",
      "Treating green and red chile as separate plants rather than unripe vs. vine-ripened stages of the same cultivar, or assuming all New Mexico chile is 'Hatch' while overlooking northern Chimayo and Pueblo landraces.",
      "Serving sopaipillas solely as a dessert rather than alongside savory chile plates with honey (or stuffed with meat and beans), or misreading 'Christmas' (serving both red and green chile sauces together); note also that dessert-only spice profiles lacked documentation in consulted texts (LOW CONFIDENCE)."
    ],
    "sources": [
      "https://santafe.com/heating-it-up-with-new-mexican-food/",
      "https://fivegraces.com/wp-content/uploads/2024/01/Table_NM_22_Summer_Issue_lowres-copy-2.pdf",
      "https://cpi.nmsu.edu/_assets/documents/Eating-Well.pdf",
      "https://en.wikipedia.org/wiki/New_Mexico_chile",
      "https://kids.kiddle.co/New_Mexico_chile",
      "https://www.nmgastronome.com/?p=56992",
      "https://www.nmgastronome.com/?p=30339",
      "https://www.thefooddictator.com/the-hirshon-new-mexican-stuffed-sopapillas-with-carne-adovada-and-red-chile-sauce/",
      "https://buenofoods.com/products/red-chile/",
      "https://buenofoods.com/red-chile-sauce-from-package/",
      "https://www.ralphs.com/p/bueno-foods-hot-enchilada-sauce/0007800419311"
    ]
  },
  {
    "id": "us_hawaiian",
    "label": "Hawaiian & Local",
    "subtitle": "Shoyu, sesame, alaea salt, limu",
    "about": "Set across the Hawaiian Islands of the central Pacific including Oahu, Maui, and the Big Island, everyday island eating is Local Food rather than ancient Polynesian fare alone. Polynesian voyagers established Native Hawaiian (Kanaka Maoli) staples like taro and imu-roasted pork, and later Anglo-American contact plus plantation migrations from China, Japan, Korea, the Philippines, and Portugal created a shared working-class cuisine. Representative Local dishes are the plate lunch, shoyu ahi poke, loco moco, and Spam musubi, alongside Native Hawaiian kalua pork, laulau, poi, and lomi salmon.",
    "flavors": [
      "shoyu (醤油, Hepburn: shōyu, local mildly sweet soy sauce)",
      "goma-abura (ごま油, Hepburn: goma-abura, toasted sesame oil)",
      "pa'akai 'alaea (Hawaiian red iron-oxide mineral sea salt)",
      "'inamona (Hawaiian roasted, salted crushed kukui candlenut)",
      "limu / ogo (Hawaiian limu; Japanese オゴ, Hepburn: ogo, edible seaweed)",
      "negi (ネギ, Hepburn: negi, green onion / scallion)",
      "tamanegi (玉ねぎ, Hepburn: tamanegi, Maui or sweet yellow onion)",
      "shoga (生姜, Hepburn: shōga, fresh ginger)",
      "ninniku (大蒜 / にんにく, Hepburn: ninniku, garlic)",
      "gochugaru / togarashi (고춧가루, Revised Romanization: gochugaru; 唐辛子, Hepburn: tōgarashi, Korean chili powder or red pepper flakes)",
      "wuxiangfen (五香粉, pinyin: wǔxiāngfěn, Chinese five-spice powder, used in local char siu)",
      "furikake (振り掛け, Hepburn: furikake, nori-sesame rice seasoning)"
    ],
    "sweet_only": [
      "lilikoi (passion fruit; primarily used in juices, jams, and sweets, occasionally fish glazes)",
      "pineapple (fresh fruit, dried snacks, cookies, and cocktail garnishes — not everyday savory cooking)"
    ],
    "signature_ingredients": [
      "sashimi-grade ahi (yellowfin or bigeye tuna) or tako (octopus) -> verified sushi-grade or sashimi-grade tuna or salmon from a fish counter (choose only fish handled for raw consumption)",
      "limu / ogo (Hawaiian seaweed) -> dried wakame or hijiki (US supermarket Asian aisle, rehydrated and chopped)",
      "'inamona (roasted kukui candlenut) -> finely chopped toasted macadamia nuts with coarse sea salt",
      "kalo / poi (fermented taro paste) and lu'au taro leaves -> none for true poi in standard US supermarkets (taro corms appear only in specialty/Asian markets)",
      "ti and banana leaves (for imu kalua pig and laulau) -> none in standard US supermarkets (heavy foil traps steam in oven adaptations without leaf aroma)",
      "Portuguese sausage -> mild smoked pork sausage or kielbasa (lacks exact island seasoning balance — LOW CONFIDENCE)"
    ],
    "pantry_assumed": [
      "short- or medium-grain white rice",
      "local-style shoyu (such as Aloha Shoyu)",
      "toasted sesame oil",
      "canned Spam",
      "mayonnaise and elbow macaroni (for plate-lunch mac salad)",
      "garlic, ginger, green onions, and sweet or yellow onions",
      "nori sheets and furikake"
    ],
    "techniques": [
      "Raw fish curing and gentle tossing (poke) or hand-massaging salted salmon with tomatoes and scallions (lomi)",
      "Underground hot-rock steaming wrapped in ti and banana leaves (imu for kalua pork and laulau; adapted via slow roasting/braising)",
      "Pan-searing and glazing (Spam for musubi, North Shore garlic butter shrimp, loco moco hamburger patties)",
      "Steaming and simmering rice-and-noodle comfort dishes (manapua pork buns, saimin noodle broth)"
    ],
    "shortcuts": [
      "Aloha Shoyu (Original): contains water, wheat gluten, salt, sugar, fermented soybeans, caramel color, and preservatives; retail label lists 780 mg sodium (~1.95 g salt equiv) and 1 g sugar per 15 mL (1 tbsp), matching OpenFoodFacts values of 12.67-13.0 g salt per 100 mL. Omit ~1.95 g salt per 15 mL added, or mimic with slightly diluted standard soy sauce plus 1 g sugar per 15 mL.",
      "Aloha Shoyu Poke Sauce (Tanioka's): contains soy sauce, water, ginger, chili sauce, and garlic; retail page lists 470 mg sodium (~1.18 g salt equiv) per serving (serving weight unprinted — LOW CONFIDENCE on per-100 g salt).",
      "NOH Chinese Barbecue Char Siu Seasoning Mix (72 g pouch): contains cane sugar, salt, powdered soy sauce, 5-spice, onion, garlic, and Red 3; label lists 2,220 mg sodium (~5.55 g salt equiv) and 66 g sugar per 72 g pouch (370 mg sodium per 12 g serving) — swap 1 pouch with 66 g sugar + ~5.6 g salt + five-spice, onion powder, and garlic powder.",
      "NOH Kalua Seasoning Salt and Japanese Hon Dashi bonito base appear in local recipes, though exact label salt figures were unverified in consulted texts (LOW CONFIDENCE)."
    ],
    "allergen_notes": "Local Hawaii condiments carry dense US Top 9 allergens: local shoyu (including Aloha Shoyu), poke sauces, and NOH char siu mixes contain wheat (wheat gluten) and soy; toasted sesame oil and furikake contain sesame; traditional 'inamona (kukui nut) and its macadamia (or peanut) substitutes trigger tree-nut and peanut warnings; Hon Dashi used in saimin broths contains fish (bonito); ahi, tako, and garlic shrimp introduce fish and shellfish; and macaroni salad mayonnaise plus loco moco add egg and milk.",
    "pitfalls": [
      "Putting pineapple on everything (pizza, burgers, chicken, skewers, or poke) — a mainland tiki and 'Polynesian Pop' cliché rather than authentic Native Hawaiian or Local cooking.",
      "Conflating Native Hawaiian cuisine with everyday plantation Local Food; avoid labeling Spam musubi, loco moco, or plate lunches as traditional Native Hawaiian food (default to Local Food and tag Native Hawaiian dishes separately).",
      "Turning poke into an overloaded mainland salad bowl piled with avocado, cucumber, mango, and spicy mayo instead of clean cubed ahi lightly seasoned with shoyu, sesame oil, onions, 'alaea salt, limu, and 'inamona.",
      "Inventing unverified Filipino-Local condiment details; while Filipino plantation labor shaped the plate lunch, specific Filipino-Local condiments or dishes were not documented in the consulted texts (LOW CONFIDENCE)."
    ],
    "sources": [
      "https://www.researchgate.net/publication/310768496_Homegrown_Cuisines_or_Naturalized_Cuisines_The_History_of_Food_in_Hawaii_and_Hawaii's_Place_in_Food_History",
      "https://vdoc.pub/documents/the-food-of-paradise-exploring-hawaiis-culinary-heritage-5vnh8f7idod0",
      "The Food of Paradise: Exploring Hawaii's Culinary Heritage, Rachel Laudan, 1996",
      "https://dokumen.pub/hawaii-regional-cuisine-the-food-movement-that-changed-the-way-hawaii-eats-9780824879518.html",
      "https://www.researchgate.net/publication/365972879_Using_Authenticity_Exoticism_and_Creativity_to_Express_Deliciousness_and_Valorize_Food_Signifying_Good_Taste_in_Food_on_Yelp",
      "https://tikikulture.com/food-recipes/",
      "https://sobremesapress.com/world/traditional-american-food/",
      "https://giftbasketdelivery.com/blogs/state-fruit/hawaii-state-fruit",
      "https://feedthepudge.com/traditional-hawaiian-style-ahi-poke/",
      "https://www.abeautifulplate.com/shoyu-ahi-poke/",
      "https://www.safeway.com/shop/pd/aloha-specialty-food-shoyu-24-oz/127051010",
      "https://world.openfoodfacts.org/product/0873934002026/aloha-soy-sauce-aloha-shoyu-company-ltd",
      "https://www.mercato.com/item/aloha-shoyu-poke-sauce-taniokas-12-ounces/737056",
      "https://www.heb.com/product-detail/noh-of-hawaii-chinese-barbecue-char-siu-seasoning-mix/180058"
    ]
  },
  {
    "id": "colombian",
    "label": "Colombian",
    "subtitle": "Hogao, aji, cumin, annatto, cilantro",
    "about": "Colombian cuisine spans northwestern South America across six sharply contrasting regions: the cool Andean highlands (Bogota, Medellin, Boyaca), the tropical Caribbean and Pacific coasts, the eastern Orinoquia (Llanos) plains, the Amazon, and the islands. Shaped by Indigenous, Spanish, African, and Levantine (Lebanese and Palestinian) traditions, it has no single national dish, so an app should default to mild Andean everyday pantry cooking while tagging coastal coconut seafood and Llanos beef-and-plantain traditions separately. Representative dishes include Andean ajiaco, bandeja paisa, and sancocho alongside Caribbean coconut rice (arroz con coco).",
    "flavors": [
      "hogao (traditional Colombian savory cooking sauce; exact household recipe unitemized in consulted sources — LOW CONFIDENCE)",
      "aji (tabletop chile pepper condiment, usually served on the side)",
      "achiote / color (annatto)",
      "comino (ground cumin)",
      "ajo (garlic)",
      "cebolla (onion)",
      "cilantro (coriander leaf)",
      "curcuma (turmeric)",
      "pimienta negra (black pepper)",
      "hierbas de azotea (Pacific 'rooftop herbs'; individual species not itemized in consulted sources — LOW CONFIDENCE)",
      "salsa negra (Colombian dark savory condiment sauce)"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      "papa criolla (small yellow Andean potatoes) -> baby Yukon Gold potatoes (firmer texture — LOW CONFIDENCE)",
      "platano (green and ripe plantains) -> US supermarket large produce-section plantains; none if green plantains are unavailable",
      "yuca (cassava) -> frozen peeled yuca in US Latin/freezer aisles, or waxy potatoes in sancocho (alters texture)",
      "cuajada (fresh curd cheese, used in Llanos majule) -> drained mild queso fresco or farmer's cheese (LOW CONFIDENCE)",
      "maize / arepa flour (for arepas) -> specialty Colombian arepa flour in US supermarket Latin aisles; none if only coarse cornmeal is stocked (LOW CONFIDENCE)",
      "piangua (Pacific mangrove shellfish) -> none (clams or mussels only loosely approximate — LOW CONFIDENCE)"
    ],
    "pantry_assumed": [
      "hogao (or savory cooking-sauce ingredients)",
      "tabletop aji sauce",
      "white rice",
      "dried beans, potatoes, cassava, or plantains",
      "arepas or maize flour",
      "garlic, cumin, and annatto (achiote / color)",
      "commercial seasoning/bouillon cubes or powders (such as Ricostilla, Triguisar, or Dona Gallina — often)"
    ],
    "techniques": [
      "Simmering savory hogao bases and perfuming broths with annatto, cumin, and Pacific hierbas de azotea",
      "Gentle, long simmering of multi-starch, multi-meat soups and stews (ajiaco, sancocho, Andes tripe stew)",
      "Griddling arepas and frying stuffed maize, cassava, and plantain items (arepa e' huevo, carimanolas, empanadas, aborrajados)",
      "Simmering seafood in coconut milk (encocao), wrapping fish or tamals in plantain leaves (pandao, piangua tamal), and cold-curing ceviches"
    ],
    "shortcuts": [
      "Triguisar / La Gran Cocina Condimento en Polvo (70 g): contains cumin, corn/rice starch, black pepper, annatto, turmeric, garlic, and Yellow 5; DISPUTED SALT (LOW CONFIDENCE) — UK listing claims no salt, Danish listing includes salt in ingredients yet prints 0 g in nutrition table, and Lebanese/Polish sites warn of high salt. Always check the box; a popular food-blog DIY swaps 1 tbsp each annatto, turmeric, garlic powder, cumin, and black pepper + 1 tsp salt (2,344 mg sodium / ~5.86 g salt per batch).",
      "Ricostilla Caldo de Costillas Cubes (Quala): contains salt (~55%), rice flour, beef rib flavorings, sugar, hydrogenated fat, MSG, inosinate/guanylate, onion, celery, parsley, garlic, and pepper; OpenFoodFacts cube panel lists 48.18 g salt (19.27 g sodium) per 100 g (powder page prints inconsistent 13.23 g salt — LOW CONFIDENCE). Omit ~4.82 g salt per 10 g cube used.",
      "Dona Gallina (Ricompleto): widely stocked Colombian bouillon, though exact ingredient and sodium panels were absent in consulted sources (LOW CONFIDENCE)."
    ],
    "allergen_notes": "Core Colombian spices, hogao, and aji are largely free of US Top 9 allergens, though milk enters through fresh curd (cuajada) dishes like majule and cheese breads like pandebono, eggs appear in dishes like tenderloin on horseback and arepa e' huevo, and coastal cooking relies on fish and shellfish. Reviewed Triguisar and Ricostilla panels declare celery (an EU major allergen) rather than US Top 9 allergens, but salsa negra and Dona Gallina labels lacked full verification in consulted sources and should be checked for hidden soy, wheat, or fish.",
    "pitfalls": [
      "Making Colombian main dishes aggressively fiery; traditional cooking is mild and aromatic (though hot peppers appear in some recipes), with heat commonly adjusted at the table via aji.",
      "Collapsing all six regions into bandeja paisa or ajiaco, ignoring Caribbean and Pacific coconut-milk seafood dishes (arroz con coco, encocao) and Llanos beef and plantain-curd traditions.",
      "Assuming one fixed salt number for Triguisar despite conflicting export labels, or failing to subtract ~4.82 g salt per 10 g Ricostilla cube.",
      "Overclaiming unverified botanicals: guascas (absent from the consulted Cancilleria guide), individual species inside Pacific hierbas de azotea, and sweet-only dessert flavorings were not documented in the consulted texts (LOW CONFIDENCE)."
    ],
    "sources": [
      "https://www.cancilleria.gov.co/sites/default/files/FOTOS2025/ColombianCuisineForTheWorld.pdf",
      "Gran Libro de la Cocina Colombiana, Biblioteca Basica de Cocinas Tradicionales de Colombia Vol. 09, Carlos Ordonez Caicedo, 2012",
      "https://www.researchgate.net/profile/Jorge_Melo4/publication/275715946_Alimentacion_y_cocina_Bibliografia_basica/links/5854297d08ae81995eb1cfdc/%5Cl%20%22_Toc408498392%22",
      "https://osf.io/download/g34t8/",
      "https://esimglobe.com/th/blogs/news/guide-colombia-cuisine-of",
      "https://tasteoflatinamerica.dk/english_en/triguisar-70g.html",
      "https://www.u-buy.co.uk/product/O7F6V28-triguisar-colombian-seasoning-mix-3-pack",
      "https://www.ubuy.com.lb/en/product/O7F6V28-triguisar-colombian-seasoning-mix-3-pack",
      "https://afromarket.pl/product/la-gran-cocina-color-70g-triguisar/",
      "https://www.mycolombianrecipes.com/homemade-powdered-seasoning/",
      "https://world.openfoodfacts.org/product/7702354012427/caldo-de-costillas-ricostilla",
      "https://world.openfoodfacts.org/product/7702354946036/ricostilla-quala"
    ]
  }
]
```

#### **Works cited**

> 1. (PDF) Using Authenticity, Exoticism, and Creativity to Express, [https://www.researchgate.net/publication/365972879_Using_Authenticity_Exoticism_and_Creativity_to_Express_Deliciousness_and_Valorize_Food_Signifying_Good_Taste_in_Food_on_Yelp](https://www.researchgate.net/publication/365972879_Using_Authenticity_Exoticism_and_Creativity_to_Express_Deliciousness_and_Valorize_Food_Signifying_Good_Taste_in_Food_on_Yelp)
> 2. Guide to Colombian Cuisine: Regions, Dishes and Ordering Tips, [https://esimglobe.com/th/blogs/news/guide-colombia-cuisine-of](https://esimglobe.com/th/blogs/news/guide-colombia-cuisine-of)
> 3. THE MYTH OF QUÉBEC'S TRADITIONAL CUISINE, [https://www.collectionscanada.gc.ca/obj/thesescanada/vol2/002/MR75957.PDF](https://www.collectionscanada.gc.ca/obj/thesescanada/vol2/002/MR75957.PDF)
> 4. Red or Green–New Mexico's Food Scene Was on Fire in 2022, [https://www.nmgastronome.com/?p=56992](https://www.nmgastronome.com/?p=56992)
> 5. The Food Of Paradise: Exploring Hawaii's Culinary Heritage [PDF], [https://vdoc.pub/documents/the-food-of-paradise-exploring-hawaiis-culinary-heritage-5vnh8f7idod0](https://vdoc.pub/documents/the-food-of-paradise-exploring-hawaiis-culinary-heritage-5vnh8f7idod0)
> 6. Food & Recipes - Tiki Kulture, [https://tikikulture.com/food-recipes/](https://tikikulture.com/food-recipes/)
> 7. Histoire de la gastronomie québécoise : l'émergence d'une identité, [https://constellation.uqac.ca/id/eprint/5920/1/PlamondonLalancette_uqac_0862_10709.pdf](https://constellation.uqac.ca/id/eprint/5920/1/PlamondonLalancette_uqac_0862_10709.pdf)
> 8. Cabanes à Sucre: A Guide to Quebec Sugar Shacks, [https://urbanguidequebec.com/cabanes-a-sucre-a-guide-to-quebec-sugar-shacks/](https://urbanguidequebec.com/cabanes-a-sucre-a-guide-to-quebec-sugar-shacks/)
> 9. Heating It Up with New Mexican Food - SantaFe.com, [https://santafe.com/heating-it-up-with-new-mexican-food/](https://santafe.com/heating-it-up-with-new-mexican-food/)
> 10. [https://www.cancilleria.gov.co/sites/default/files/FOTOS2025/ColombianCuisineForTheWorld.pdf](https://www.cancilleria.gov.co/sites/default/files/FOTOS2025/ColombianCuisineForTheWorld.pdf)
> 11. Dining New Mexico - Gil's Thrilling (And Filling) Blog, [https://www.nmgastronome.com/?page_id=432](https://www.nmgastronome.com/?page_id=432)
> 12. 2014: A Thrilling (And Filling) Year in Food, [https://www.nmgastronome.com/?p=30339](https://www.nmgastronome.com/?p=30339)
> 13. Homesick Texan's Culinary Journey | PDF | Pickling - Scribd, [https://www.scribd.com/document/748541974/The-Homesick-Texan-Cookbook](https://www.scribd.com/document/748541974/The-Homesick-Texan-Cookbook)
> 14. The Hirshon New Mexican Stuffed Sopapillas With Carne Adovada, [https://www.thefooddictator.com/the-hirshon-new-mexican-stuffed-sopapillas-with-carne-adovada-and-red-chile-sauce/](https://www.thefooddictator.com/the-hirshon-new-mexican-stuffed-sopapillas-with-carne-adovada-and-red-chile-sauce/)
> 15. Homegrown Cuisines or Naturalized Cuisines? The History of Food, [https://www.researchgate.net/publication/310768496_Homegrown_Cuisines_or_Naturalized_Cuisines_The_History_of_Food_in_Hawaii_and_Hawaii's_Place_in_Food_History](https://www.researchgate.net/publication/310768496_Homegrown_Cuisines_or_Naturalized_Cuisines_The_History_of_Food_in_Hawaii_and_Hawaii's_Place_in_Food_History)
> 16. "Traditional Hawaiian food" : r/IndianCountry - Reddit, [https://www.reddit.com/r/IndianCountry/comments/ybsqnf/traditional_hawaiian_food/](https://www.reddit.com/r/IndianCountry/comments/ybsqnf/traditional_hawaiian_food/)
> 17. Why Traditional American Food Isn't Just Burgers and Hot Dogs, [https://sobremesapress.com/world/traditional-american-food/](https://sobremesapress.com/world/traditional-american-food/)
> 18. Hawaii State Fruit: Why Pineapple Tells the Story - Gift Basket Delivery, [https://giftbasketdelivery.com/blogs/state-fruit/hawaii-state-fruit](https://giftbasketdelivery.com/blogs/state-fruit/hawaii-state-fruit)
> 19. Montreal's best urban sugar shacks, the 2019 edition, [https://willtravelforfood.com/2019/03/08/sugar-shack-cabane-a-sucre-montreal-2019/](https://willtravelforfood.com/2019/03/08/sugar-shack-cabane-a-sucre-montreal-2019/)
> 20. Tourtiere : r/ottawa - Reddit, [https://www.reddit.com/r/ottawa/comments/zpu08n/tourtiere/](https://www.reddit.com/r/ottawa/comments/zpu08n/tourtiere/)
> 21. Recette De Pate A La Viande - Elearning, [https://elearning.asc.edu.ag/recette-de-pate-la-viande-2](https://elearning.asc.edu.ag/recette-de-pate-la-viande-2)
> 22. Masterchef Colombia- Modernity, Globalization and the ... - OSF, [https://osf.io/download/g34t8/](https://osf.io/download/g34t8/)
> 23. Colombian Spice Mix "Triguisar" 70g, [https://tasteoflatinamerica.dk/english_en/triguisar-70g.html](https://tasteoflatinamerica.dk/english_en/triguisar-70g.html)
> 24. Buy Triguisar Colombian Seasoning Mix - 3 Pack at Ubuy UK, [https://www.u-buy.co.uk/product/O7F6V28-triguisar-colombian-seasoning-mix-3-pack](https://www.u-buy.co.uk/product/O7F6V28-triguisar-colombian-seasoning-mix-3-pack)
> 25. Buy Triguisar Colombian Seasoning Mix - 3 Pack at Ubuy Lebanon, [https://www.ubuy.com.lb/en/product/O7F6V28-triguisar-colombian-seasoning-mix-3-pack](https://www.ubuy.com.lb/en/product/O7F6V28-triguisar-colombian-seasoning-mix-3-pack)
> 26. La Gran Cocina Color 70g Triguisar - Afromarket - African Shop, [https://afromarket.pl/product/la-gran-cocina-color-70g-triguisar/](https://afromarket.pl/product/la-gran-cocina-color-70g-triguisar/)
> 27. Ricostilla – Quala – 108 g - Open Food Facts, [https://world.openfoodfacts.org/product/7702354946036/ricostilla-quala](https://world.openfoodfacts.org/product/7702354946036/ricostilla-quala)
> 28. New Mexico chile - Wikipedia, [https://en.wikipedia.org/wiki/New_Mexico_chile](https://en.wikipedia.org/wiki/New_Mexico_chile)
> 29. New Mexico chile Facts for Kids, [https://kids.kiddle.co/New_Mexico_chile](https://kids.kiddle.co/New_Mexico_chile)
> 30. Hawaiian Dishes, Ranked by a Local Who Actually Eats - hawaii.top, [https://hawaii.top/2026/09/17/hawaiian-dishes/](https://hawaii.top/2026/09/17/hawaiian-dishes/)
> 31. 22 Hawaiian foods that tell the story of the islands - CookUnity, [https://www.cookunity.com/blog/hawaiian-foods](https://www.cookunity.com/blog/hawaiian-foods)
> 32. Aloha Specialty Food Shoyu - 24 Oz - Safeway, [https://www.safeway.com/shop/pd/aloha-specialty-food-shoyu-24-oz/127051010](https://www.safeway.com/shop/pd/aloha-specialty-food-shoyu-24-oz/127051010)
> 33. Aloha shoyu soy sauce – Aloha Shoyu Company Ltd., [https://world.openfoodfacts.org/product/0873934002040/aloha-shoyu-soy-sauce-aloha-shoyu-company-ltd](https://world.openfoodfacts.org/product/0873934002040/aloha-shoyu-soy-sauce-aloha-shoyu-company-ltd)
> 34. Aloha Soy Sauce – Aloha Shoyu Company Ltd. - Open Food Facts, [https://world.openfoodfacts.org/product/0873934002026/aloha-soy-sauce-aloha-shoyu-company-ltd](https://world.openfoodfacts.org/product/0873934002026/aloha-soy-sauce-aloha-shoyu-company-ltd)
> 35. Tourtière - Wikipedia, [https://en.wikipedia.org/wiki/Tourti%C3%A8re](https://en.wikipedia.org/wiki/Tourti%C3%A8re)
> 36. Cuisine québécoise - Wikipédia, [https://fr.wikipedia.org/wiki/Cuisine_qu%C3%A9b%C3%A9coise](https://fr.wikipedia.org/wiki/Cuisine_qu%C3%A9b%C3%A9coise)
> 37. Ma fourchette voyage - Montréal - Archipel UQAM, [https://archipel.uqam.ca/11430/1/M15380.pdf](https://archipel.uqam.ca/11430/1/M15380.pdf)
> 38. de la cuisine quebecoise - Free, [http://degroupe.free.fr/PDF/cuisine/Genese%20de%20la%20cuisine%20Quebecoise.pdf](http://degroupe.free.fr/PDF/cuisine/Genese%20de%20la%20cuisine%20Quebecoise.pdf)
> 39. Caldo de costillas – Ricostilla – 12 cubos - Open Food Facts, [https://world.openfoodfacts.org/product/7702354012427/caldo-de-costillas-ricostilla](https://world.openfoodfacts.org/product/7702354012427/caldo-de-costillas-ricostilla)
> 40. Full text of "Vogue" - Internet Archive, [https://archive.org/stream/vogue179julnewy/vogue179julnewy_djvu.txt](https://archive.org/stream/vogue179julnewy/vogue179julnewy_djvu.txt)
> 41. Eating-Well.pdf - Chile Pepper Institute - New Mexico State University, [https://cpi.nmsu.edu/_assets/documents/Eating-Well.pdf](https://cpi.nmsu.edu/_assets/documents/Eating-Well.pdf)
> 42. Red Chile Sauce (From Red Chile Puree) Recipe - Bueno Foods, [https://buenofoods.com/red-chile-sauce-from-package/](https://buenofoods.com/red-chile-sauce-from-package/)
> 43. Traditional Red Chile Sauce (From Red Chile Pods) - Bueno Foods, [https://buenofoods.com/traditional-red-chile-sauce/](https://buenofoods.com/traditional-red-chile-sauce/)
> 44. Peppers: Numex? Other favorites? | Houzz Forum, [https://www.houzz.com/discussions/2102285/peppers-numex-other-favorites](https://www.houzz.com/discussions/2102285/peppers-numex-other-favorites)
> 45. History of Hawaiian Cuisine | PDF | Foods - Scribd, [https://www.scribd.com/document/315344334/Cuisine-of-Hawaii](https://www.scribd.com/document/315344334/Cuisine-of-Hawaii)
> 46. Shoyu Ahi Poke (Hawaiian Ahi Poke Bowl Recipe) - A Beautiful Plate, [https://www.abeautifulplate.com/shoyu-ahi-poke/](https://www.abeautifulplate.com/shoyu-ahi-poke/)
> 47. Traditional Hawaiian-Style Ahi Poke - feedthepudge, [https://feedthepudge.com/traditional-hawaiian-style-ahi-poke/](https://feedthepudge.com/traditional-hawaiian-style-ahi-poke/)
> 48. Tako Poke Recipe - Keeping It Relle, [https://keepingitrelle.com/tako-poke/](https://keepingitrelle.com/tako-poke/)
> 49. NOH of Hawaii Chinese Barbecue Char Siu Seasoning Mix - H-E-B, [https://www.heb.com/product-detail/noh-of-hawaii-chinese-barbecue-char-siu-seasoning-mix/180058](https://www.heb.com/product-detail/noh-of-hawaii-chinese-barbecue-char-siu-seasoning-mix/180058)
> 50. Can anybody tell me about traditional Quebecois food? - Reddit, [https://www.reddit.com/r/Quebec/comments/ytb3jq/can_anybody_tell_me_about_traditional_quebecois/](https://www.reddit.com/r/Quebec/comments/ytb3jq/can_anybody_tell_me_about_traditional_quebecois/)
> 51. Tong | PDF | Canada | Berry - Scribd, [https://www.scribd.com/document/470306875/tong](https://www.scribd.com/document/470306875/tong)
> 52. Stock & Gravy - Food Basics, [https://www.foodbasics.ca/aisles/pantry/herbs-spices-sauces/stock-gravy](https://www.foodbasics.ca/aisles/pantry/herbs-spices-sauces/stock-gravy)
> 53. Poutine Gravy Sauce – St Hubert – 398 ml - Open Food Facts, [https://world.openfoodfacts.org/product/0066701001029/poutine-gravy-sauce-st-hubert](https://world.openfoodfacts.org/product/0066701001029/poutine-gravy-sauce-st-hubert)
> 54. Commercial Food Service Inc. Product List Department Section, [https://cfsfood.ca/hubfs/CFS%20Product%20Catalog-1.pdf?hsLang=en](https://cfsfood.ca/hubfs/CFS%20Product%20Catalog-1.pdf?hsLang=en)
> 55. St Hubert poutine sauce - original recipe, [https://lestresorsderable.com/en/poutine-sauce/126-st-hubert-poutine-sauce-original-recipe-0066701000343.html](https://lestresorsderable.com/en/poutine-sauce/126-st-hubert-poutine-sauce-original-recipe-0066701000343.html)
> 56. Nutritional & Allergen Information | St-Hubert Restaurants, [https://www.st-hubert.com/en/nutritional.html](https://www.st-hubert.com/en/nutritional.html)
> 57. Knorr Bovril Beef Bouillon 250ml - Caffeinecam, [https://caffeinecam.com/products/knorr-bovril-beef-bouillon-beef-gravy-250ml-imported-from-canada](https://caffeinecam.com/products/knorr-bovril-beef-bouillon-beef-gravy-250ml-imported-from-canada)
> 58. New Mexico Red Chile - Bueno Foods, [https://buenofoods.com/products/red-chile/](https://buenofoods.com/products/red-chile/)
> 59. Bueno Foods Hot Enchilada Sauce, 16 OZ - Ralphs, [https://www.ralphs.com/p/bueno-foods-hot-enchilada-sauce/0007800419311](https://www.ralphs.com/p/bueno-foods-hot-enchilada-sauce/0007800419311)
> 60. Aloha Shoyu Gluten-Free Soy Sauce, 10 oz - Walmart.com, [https://www.wal-mart.com/ip/Aloha-Shoyu-Gluten-Free-Soy-Sauce-10-oz/184475285](https://www.wal-mart.com/ip/Aloha-Shoyu-Gluten-Free-Soy-Sauce-10-oz/184475285)
> 61. Homemade Powdered Seasoning - My Colombian Recipes, [https://www.mycolombianrecipes.com/homemade-powdered-seasoning/](https://www.mycolombianrecipes.com/homemade-powdered-seasoning/)
> 62. Fresh Market - Fine Fare Brentwood, [https://www.finefarebrentwood.com/subcategory/cca83882-0ef6-4846-9a49-2c5bb06b49b4](https://www.finefarebrentwood.com/subcategory/cca83882-0ef6-4846-9a49-2c5bb06b49b4)