# Near & Middle East Regional Cuisine Research

## Biggest surprises and disputes

The biggest accuracy issue is that **modern national labels do not map neatly onto older food regions**. Palestinian cooking is clearly identifiable, but it sits inside a shared Levantine repertoire spanning present-day Palestine, Jordan, Lebanon, and Syria; Reem Kassis explicitly cautions that national cuisines are comparatively recent categories and that many dishes and ingredients cross today’s borders. At the same time, dishes such as musakhan, maftoul, and particular preparations of maqluba carry especially strong Palestinian associations. citeturn541270search1turn541270search3

A second surprise is that the familiar Western shorthand for Persian food—“saffron and rosewater”—is too narrow for savory cooking. Encyclopaedia Iranica describes a much broader everyday palette built around turmeric, black pepper, herbs such as dill, mint, coriander, parsley and fenugreek, fruits and souring agents, with fiery heat generally restrained; rosewater is much more strongly associated with sweets, sherbets and perfumed preparations than with the savory center of the cuisine. citeturn560638search0turn560638search4

For Turkish cuisine, several items in the supplied flavor list are genuinely traditional but **not equally characteristic nationwide**. Pul biber, black pepper, kekik, mint, cumin and sumac have strong support as widely used seasonings, whereas pomegranate molasses is particularly important in southern and southeastern cooking, including Gaziantep and Hatay. Fenugreek is traditional, but it is strongly associated with particular foods and regions—especially çemen pastes and pastırma—rather than functioning as a universal everyday seasoning. citeturn445990view0turn313931search20turn313931search35turn256533search0turn256533search1

There is also a translation trap around Turkish **kekik**. English-language Turkish sources commonly call it “thyme,” but the Turkish culinary category can include closely related oregano/thymus-type herbs; recipe generation should therefore avoid automatically substituting generic supermarket thyme in every case. The safest app wording is “kekik, often sold as Turkish oregano or thyme,” with the exact herb allowed to vary regionally. citeturn445990view0turn313931search5

Finally, none of these cuisines supports a defensible statement that every household “always” stocks one particular prepared food or condiment. Because the requested `pantry_assumed` field implies that level of universality, I leave it empty for all three nodes rather than turn a common habit into a hard app rule. Regional and household variation is substantial in Iran, Türkiye and the Levant. citeturn942719search0turn313931search0turn541270search1

## Palestinian and Levantine

For this node, the safest model is **Palestinian cooking as the focal tradition inside the southern Levant**, not a claim that every listed food is uniquely Palestinian. Kassis notes that Palestine, Jordan, Syria and Lebanon share dishes because they occupy a connected food region with a long common history; she nevertheless singles out maftoul and maqluba as especially associated with Palestine, while musakhan is one of the most distinctly Palestinian dishes. citeturn541270search1turn541270search3

The savory seasoning core is more spice-forward than the stereotype of “just za’atar and tahini.” A Palestinian home repertoire commonly draws on allspice, cinnamon, cardamom, black pepper, cumin, sumac, za’atar, mint, garlic, tahini, lemon and olive oil. The Institute for Middle East Understanding identifies cinnamon, allspice, cardamom, nutmeg and black pepper among common Palestinian spices; Kassis describes allspice as especially dominant in her family’s cooking and identifies za’atar as both a herb and a condiment of za’atar, sumac, sesame and salt. citeturn541270search5turn541270search2turn541270search1

The app should not turn Kassis’s “nine-spice” into a universal Palestinian formula. Her published blend contains allspice, cinnamon, coriander, black pepper, cardamom, cumin, cloves, mace and nutmeg, but she explicitly identifies it as her mother’s blend and says ordinary baharat or Lebanese seven-spice can stand in with a somewhat different profile. citeturn942719search4turn541270search2

Regional variation matters especially in Gaza. Scholarship from the Institute for Palestine Studies describes Gazan cooking as particularly associated with seafood, chilies, dill, spices and pronounced sourness; treating all Palestinian cooking as one uniform Jerusalem-style flavor profile would therefore be a serious recipe-generation error. citeturn541270search9

Signature ingredients worth preserving rather than casually replacing include maftoul, freekeh, molokhia and, where a recipe specifically calls for it, taboon bread. The substitutes in the JSON are functional substitutions, not claims of equivalence.

## Persian

Persian cooking is geographically difficult to summarize because Iran stretches from the humid Caspian shore across the Alborz and Zagros mountains to the dry plateau and Persian Gulf. Encyclopaedia Iranica explicitly warns against overgeneralization because climate, agriculture and ethnic traditions vary widely, although rice, wheat, herbs, vegetables, fruits, nuts and dairy underpin much of the shared repertoire. citeturn942719search0

The strongest recipe-writing cue is **balance rather than heat**. Iranica describes salt, black pepper, turmeric, saffron, cinnamon and marjoram as common seasonings and emphasizes dill, mint, coriander, parsley and fenugreek; strongly fiery seasoning is comparatively uncommon. Fruits and sour ingredients—including sour grapes, dried limes, tart cherries, prunes and citrus—are integral to savory stews and rice dishes, not merely garnishes. citeturn560638search0

Rice technique is a defining discriminator. Classic chelow involves soaking or washing, parboiling, draining and then steaming so that the grains remain distinct; tahdig is the browned crust created at the bottom of the pot. Polow differs by steaming rice with other ingredients or layering them into it. citeturn560638search1turn560638search3

Dried lime, **limu-ye omani**, is a particularly valuable signal for an AI recipe system because fresh lime is not an exact flavor replacement: dried lime contributes fermented, earthy bitterness as well as acidity. Najmieh Batmanglij describes it as a staple that gives a flavor fresh lime juice does not reproduce. citeturn560638search8

A second strong cue is fresh-herb density. Ghormeh sabzi and many soups, kuku and rice preparations depend on substantial amounts of herbs rather than token parsley. The app should also resist making every Persian dish saffron-heavy: saffron is emblematic and important, but the everyday savory system is broader. citeturn560638search0turn560638search6

## Turkish

Turkish cuisine is better modeled as a combination of **Anatolian regional cooking, Istanbul/Ottoman traditions and centuries of interaction with neighboring peoples**, rather than as food descending only from the Ottoman palace. Türkiye’s Ministry of Culture and Tourism attributes the cuisine’s diversity to Anatolian products, interaction with multiple cultures, and innovations in Seljuk and Ottoman palace kitchens. citeturn313931search0

The strongest pan-Turkish savory flavor signals are pul biber, black pepper, kekik, mint, cumin and sumac. GoTürkiye describes pul biber across soups, stews and casseroles; mint in salads, meze, dolma and yogurt dishes; cumin especially in köfte, meat dishes and sucuk; and sumac with kebabs, onion salads, çiğ köfte, fish and mantı. Bay leaf is traditional but more situational, particularly in tomato-based, meat, fish and preserved foods. citeturn445990view0

Allspice is authentic, especially in fillings, meat preparations and some regional cooking, but it should not be treated as an obligatory Turkish flavor. Fenugreek is also authentic: the Turkish Cultural Foundation identifies ground çemen otu as a traditional spice for pickles, soups and meat dishes, while regional sources document fenugreek-heavy çemen coatings for pastırma. That evidence supports “traditional and regionally important,” not “core to every Turkish savory dish.” citeturn256533search0turn256533search1turn256533search4

Pomegranate molasses needs similar restraint. Official regional material documents it extensively in Gaziantep and describes it as essential in southern Turkish cooking around Antakya/Hatay, while recipes from other regions use different souring agents. It is therefore correct as a Turkish ingredient but misleading as a universal national default. citeturn313931search20turn313931search35

For allergens, the app should treat tahini and sesame-containing za’atar as sesame risks; yogurt, ayran, cacık, kashk and many tarhana products as milk risks; wheat-based breads, yufka and tarhana as wheat risks; and nut-thickened sauces or garnishes as tree-nut risks. Under current U.S. labeling law, milk, egg, fish, crustacean shellfish, tree nuts, peanuts, wheat, soy and sesame are the nine major food allergens. citeturn493929search0

For packaged shortcuts, the safest way to account for salt is from the nutrition label rather than guessing from the cuisine. WHO states that 1 gram of salt corresponds to about 400 mg sodium, so `salt_g = sodium_mg × 0.0025`; this conversion is used in the JSON wherever the salt content of a variable commercial blend must be calculated. citeturn493929search7

## Fact-check of the supplied Turkish text

**“From Anatolia …” — CORRECT.** Modern Turkish cuisine is rooted heavily in Anatolia, although it also incorporates Istanbul, Balkan, Black Sea, Caucasian, Mediterranean and other regional histories. Türkiye’s Ministry of Culture and Tourism explicitly identifies the products of Anatolia as one of the cuisine’s formative elements. citeturn313931search0

**“… and the Ottoman palace kitchens” — DISPUTED AS WRITTEN.** Ottoman palace cuisine was highly influential, but presenting Turkish cuisine as simply “from Anatolia and the Ottoman palace kitchens” understates rural, regional, Seljuk, nomadic, minority-community and cross-border influences. A better phrasing is “shaped by Anatolian regional traditions and, among many influences, Seljuk and Ottoman palace cooking.” citeturn313931search0turn942719search6

**“kebabs” — CORRECT.** Kebabs form a large and well-documented family of Turkish meat preparations, especially in Anatolia’s south and southeast, though they are only one part of the cuisine. citeturn313931search0turn313931search25

**“mezze” — CORRECT, with terminology note.** The Turkish spelling is **meze**. Small cold and hot dishes are a recognized part of Turkish eating culture, but they should not be used to characterize every meal or region. citeturn313931search27

**“yogurt” — CORRECT.** Yogurt is deeply embedded in soups, sauces, vegetable dishes, mantı accompaniments, drinks and breakfast foods. citeturn313931search27turn445990view0

**“flatbreads” — CORRECT.** Turkish repertoires include multiple flat or relatively flat breads and doughs, including pide, yufka, lavaş and bazlama; the category is appropriate so long as it is not reduced to one standard form. citeturn313931search27

**“stuffed vegetables” — CORRECT.** Dolma and sarma traditions are central and widespread, and official Turkish sources describe stuffed vegetables among characteristic forms. citeturn313931search0turn942719search6

**“with tangy sumac” — CORRECT.** Sumac is widely documented in kebabs, onion salads, çiğ köfte, fish and mantı. citeturn445990view0

**“pul biber chili flakes” — CORRECT.** Pul biber is among the most widely used Turkish spices and varies regionally in pepper type, heat and processing. citeturn445990view0

**“pomegranate molasses” — DISPUTED IF IMPLIED TO BE PAN-TURKISH.** Nar ekşisi is unquestionably traditional, particularly in Gaziantep, Hatay and other southern/southeastern cuisines, but it is not equally central throughout Türkiye. The description is accurate if changed to “and, especially in the south and southeast, pomegranate molasses.” citeturn313931search20turn313931search35

For the supplied “Classic flavors” list:

**Red pepper flakes (pul biber) — CORRECT.** Strong evidence supports broad use. citeturn445990view0

**Sumac (sumak) — CORRECT.** Widely documented, particularly with meat, onions, salads and some stuffed or grain dishes. citeturn445990view0

**Mint (nane) — CORRECT.** Common in soups, yogurt dishes, dolma, salads and meze. citeturn445990view0turn256533search0

**Cumin (kimyon) — CORRECT.** Particularly characteristic of köfte, meat dishes and sucuk. citeturn445990view0

**Allspice (yenibahar) — CORRECT, BUT SECONDARY.** It belongs to the Turkish spice repertoire, but evidence is weaker for ranking it alongside pul biber or black pepper as an everyday nationwide default. citeturn313931search5

**Sesame seeds (susam) — CORRECT, BUT BETTER CLASSIFIED AS A SEED/GARNISH THAN A CORE SPICE.** Sesame is conspicuous on simit and baked goods and also enters tahini-based foods, but it does not season savory cooking as broadly as pul biber, mint or cumin. GoTürkiye specifically identifies simit as sesame-coated. citeturn313931search27

**Pomegranate molasses (nar ekşisi) — DISPUTED AS A NATIONAL “CLASSIC FLAVOR.”** Authentic and highly important in parts of southern and southeastern Türkiye; too regional to enforce across all Turkish recipes. citeturn313931search20turn313931search35

**Fenugreek (çemen) — CORRECT, BUT REGIONAL/SPECIALIZED.** Fenugreek is traditional and used in some pickles, soups and meat dishes, and it is especially associated with çemen coatings for pastırma. It should not be a default addition to ordinary Turkish dishes. citeturn256533search0turn256533search1

**Oregano (kekik) — CORRECT WITH A TRANSLATION CAVEAT.** Kekik is widely used, especially with meat, but English “oregano” or “thyme” does not map perfectly onto the Turkish herb category. citeturn445990view0turn313931search5

**Bay leaf (defne yaprağı) — CORRECT, BUT SECONDARY.** It is traditional in fish, meat, tomato-based dishes, pickles and preserves, but it is not a universal everyday flavor. citeturn445990view0

A more defensible short Turkish flavor list for recipe steering would prioritize **pul biber, black pepper, kekik, mint, cumin, sumac, garlic, tomato or pepper paste**, with allspice, bay, pomegranate molasses and fenugreek activated according to dish and region rather than inserted by default. citeturn445990view0turn313931search20turn256533search0

## Import JSON

```json
[
  {
    "id": "palestinian_levantine",
    "label": "Palestinian & Levant",
    "subtitle": "Sumac, olive oil, allspice, tahini",
    "about": "Centered on Palestine and the southern Levant along the eastern Mediterranean coast and the inland hills around Jerusalem, the West Bank and Gaza, this cuisine belongs to a wider food region shared with Jordan, Lebanon and Syria. Palestinian Arab village and city traditions, Ottoman-era exchange, trade and migration all shaped it; classic dishes include musakhan, maqluba, maftoul and mujaddara. Many foods are shared across the Levant, so these dishes should not automatically be described as uniquely Palestinian.",
    "flavors": [
      "بهار حلو — bahār ḥilw — allspice; especially important in Palestinian meat, rice and stuffed dishes",
      "سماق — summāq — sumac; tart seasoning central to musakhan and common with onions, salads and meats",
      "زعتر — zaʿtar — za'atar herb or, by extension, the condiment made from za'atar, sumac, sesame and salt",
      "كمون — kammūn — cumin",
      "قرفة — qirfa — cinnamon; used in savory rice, meat and stuffing as well as sweets",
      "هيل — hayl — cardamom; used in savory cooking as well as coffee and sweets",
      "فلفل أسود — filfil aswad — black pepper",
      "نعناع — naʿnāʿ — mint, fresh or dried",
      "ثوم — thūm — garlic",
      "طحينة — ṭaḥīna — tahini, a sesame paste used as a sauce and seasoning",
      "عصير ليمون — ʿaṣīr laymūn — lemon juice",
      "دبس الرمان — dibs al-rummān — pomegranate molasses; common in the Levant but dish- and region-dependent"
    ],
    "sweet_only": [
      "ماء الزهر — māʾ al-zahr — orange-blossom water; mainly sweets, syrups and drinks",
      "ماء الورد — māʾ al-ward — rosewater; mainly sweets and syrups",
      "محلب — maḥlab — mahlab, aromatic cherry-kernel spice used mainly in breads and sweets"
    ],
    "signature_ingredients": [
      {
        "ingredient": "مفتول — maftūl — hand-rolled Palestinian wheat granules",
        "substitute": "pearl couscous for texture only; flavor and production are not equivalent"
      },
      {
        "ingredient": "فريكة — farīka/freekeh — roasted green wheat",
        "substitute": "bulgur, preferably coarse; less smoky"
      },
      {
        "ingredient": "ملوخية — mulūkhiyya — jute mallow leaves",
        "substitute": "frozen molokhia if fresh is unavailable; spinach is only a functional substitute and lacks the characteristic texture"
      },
      {
        "ingredient": "خبز طابون — khubz ṭābūn — taboon bread",
        "substitute": "thick pita or naan; neither reproduces taboon flavor exactly"
      },
      {
        "ingredient": "عكوب — ʿakkūb — Gundelia, a seasonal wild thistle used in some Palestinian cooking",
        "substitute": "artichoke hearts for a rough functional substitute; none is exact"
      }
    ],
    "pantry_assumed": [],
    "techniques": [
      "Layer rice, vegetables and meat in one pot and invert after cooking, as in maqluba",
      "Roast or bake bread-based dishes so seasoned oil, onions and meat soak into the bread, as in musakhan",
      "Stuff vegetables or grape leaves with seasoned rice and sometimes meat, then simmer",
      "Charcoal-grill or roast meats and vegetables",
      "Slow-simmer vegetable, legume and meat stews and finish many dishes with lemon, sumac or another souring element"
    ],
    "shortcuts": [
      "Store-bought za'atar: commonly contains za'atar-type herb, sumac, sesame and salt. Substitute 1:1 by weight for a homemade za'atar condiment. Because salt varies by brand, calculate salt from the label: salt_g = sodium_mg × 0.0025 for the quantity used, and reduce added recipe salt by that amount.",
      "Baharat or Lebanese seven-spice: Reem Kassis specifically recommends these as convenient substitutes for her family's Palestinian nine-spice, with a slightly different flavor. Use 1:1 by weight for the ground spice quantity; many versions contain no salt, but verify the label. If sodium is 0 mg, salt contribution is 0 g.",
      "Prepared tahini sauce is not the same as plain tahini. If a recipe calls for tahini paste, substitute only plain sesame tahini 1:1 by weight; prepared sauces may already contain lemon, garlic, water and salt. Use the package sodium to calculate salt_g = sodium_mg × 0.0025."
    ],
    "allergen_notes": [
      "Sesame: tahini is sesame paste, and most za'atar condiment blends contain sesame.",
      "Milk: yogurt and labneh are common accompaniments and sauces; do not assume a white sauce is dairy-free.",
      "Tree nuts: pine nuts, almonds, pistachios and walnuts occur frequently as garnishes, fillings or sauce components.",
      "Wheat: pita, taboon bread, freekeh, bulgur and maftoul contain wheat.",
      "Egg, fish and shellfish are dish-specific rather than routine hidden components of the core spice blends.",
      "Commercial spice blends and sauces must still be checked for U.S.-labelled milk, egg, fish, crustacean shellfish, tree nuts, peanuts, wheat, soy and sesame."
    ],
    "pitfalls": [
      "Do not call every shared Levantine dish uniquely Palestinian, Lebanese, Syrian or Jordanian; borders are newer than many dishes.",
      "Do not treat za'atar as simply dried thyme: the word can mean the herb itself or a condiment usually combining the herb with sumac, sesame and salt.",
      "Do not make Reem Kassis's family nine-spice a universal Palestinian formula.",
      "Do not add pomegranate molasses, tahini or za'atar to every dish merely to make it seem 'Middle Eastern.'",
      "Do not insert shakshuka as a Palestinian default; it is North African in origin even though versions are now eaten elsewhere.",
      "Do not flatten Gazan cooking into the same profile as Jerusalem or the northern West Bank; Gaza has especially strong seafood, chili, dill and sour traditions."
    ],
    "sources": [
      "The Palestinian Table, Reem Kassis, 2017",
      "The Arabesque Table, Reem Kassis, 2021",
      "https://freshairarchive.org/segments/palestinian-cook-kitchen-powerful-place-not-life-sentence",
      "https://www.jamesbeard.org/recipes/nine-spice-mix",
      "https://imeu.org/resources/resources/palestinian-cuisine/328",
      "https://www.palestine-studies.org/sites/default/files/jq-articles/How%20Dough%20Rises%20in%20Gaza%20-%20Palestine%E2%80%99s%20Foremothers%20and%20Recipes%20against%20Genocide.pdf",
      "The Gaza Kitchen: A Palestinian Culinary Journey, Laila El-Haddad and Maggie Schmitt, 2012",
      "https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies",
      "https://www.who.int/news-room/fact-sheets/detail/sodium-reduction"
    ]
  },
  {
    "id": "persian",
    "label": "Persian",
    "subtitle": "Herbs, saffron, dried lime, sour fruit",
    "about": "Persian cooking developed across the Iranian plateau between the Caspian Sea and Persian Gulf, divided by the Alborz and Zagros mountain ranges and containing sharply different climates. Persian-speaking court and urban traditions interacted for centuries with Iran's many regional peoples and with trade routes linking Central Asia, the Caucasus, Mesopotamia and the Indian Ocean. Representative dishes include ghormeh sabzi, fesenjan, chelow kabab and tahchin.",
    "flavors": [
      "زردچوبه — zardchūbeh — turmeric; a major everyday savory spice",
      "زعفران — zaʿfarān — saffron; emblematic but not required in every dish",
      "فلفل سیاه — felfel-e siyāh — black pepper",
      "دارچین — dārchīn — cinnamon; used in savory as well as sweet dishes",
      "لیمو عمانی — līmū-ye ʿomānī — dried lime; sour, earthy and slightly bitter",
      "نعناع — naʿnāʿ — mint, often dried in cooked dishes",
      "شوید — shevid — dill",
      "گشنیز — geshnīz — coriander/cilantro",
      "جعفری — jaʿfari — parsley",
      "شنبلیله — shanbalīleh — fenugreek leaf",
      "غوره — ghūreh — unripe sour grapes or verjuice",
      "رب انار — robb-e anār — pomegranate concentrate/molasses; especially important in northern and some regional dishes"
    ],
    "sweet_only": [
      "گلاب — golāb — rosewater; mainly sweets, sherbets and perfumed preparations, though occasional savory exceptions exist",
      "هل — hel — cardamom; especially prominent in tea, sweets and desserts, though it can appear in savory rice preparations",
      "گل محمدی — gol-e moḥammadi — dried Damask rose petals; mainly sweets, drinks and aromatic spice mixtures"
    ],
    "signature_ingredients": [
      {
        "ingredient": "زرشک — zereshk — barberries",
        "substitute": "dried cranberries soaked briefly in lemon juice; sweeter and not equivalent"
      },
      {
        "ingredient": "لیمو عمانی — līmū-ye ʿomānī — dried limes",
        "substitute": "fresh lime juice plus a small amount of lime zest; misses the fermented earthy bitterness"
      },
      {
        "ingredient": "کشک — kashk — fermented dried dairy product, usually reconstituted",
        "substitute": "strained Greek yogurt mixed with a little feta for body; flavor is not equivalent"
      },
      {
        "ingredient": "موسیر — mūsīr — Persian shallot",
        "substitute": "ordinary shallot plus a small amount of garlic"
      },
      {
        "ingredient": "غوره — ghūreh — unripe sour grapes",
        "substitute": "verjuice if available; otherwise lemon juice diluted slightly with water"
      }
    ],
    "pantry_assumed": [],
    "techniques": [
      "Parboil, drain and steam long-grain rice to keep grains separate in chelow",
      "Build tahdig by deliberately browning the bottom layer of rice, bread or potato",
      "Brown ingredients and then slow-simmer khoresh stews until integrated",
      "Fry or sauté large quantities of herbs before simmering in dishes such as ghormeh sabzi",
      "Marinate meat or poultry and grill over direct heat for kabab"
    ],
    "shortcuts": [
      "Commercial advieh: formulas vary by dish and producer and may contain cinnamon, cardamom, cumin, rose, nutmeg or other spices. Substitute 1:1 by weight only when the blend is intended for the same dish family; do not treat 'advieh' as one universal formula. If the label shows 0 mg sodium, salt contribution is 0 g; otherwise salt_g = sodium_mg × 0.0025.",
      "Prepared or frozen ghormeh-sabzi herb mixtures can replace the same prepared herb component by weight, but verify whether they are raw, fried or salted before substitution. For a salted product, calculate salt_g from sodium_mg × 0.0025.",
      "Bottled pomegranate molasses may replace homemade reduced pomegranate concentrate 1:1 by weight as a starting point, but sweetness and acidity vary substantially by brand; adjust sourness rather than adding sugar automatically."
    ],
    "allergen_notes": [
      "Milk: kashk, yogurt, butter and ghee can appear in sauces, toppings and rice preparations.",
      "Tree nuts: walnuts are fundamental to fesenjan; almonds and pistachios are common in rice dishes, garnishes and sweets.",
      "Egg: tahchin and kuku commonly contain egg.",
      "Wheat: flatbreads, reshteh noodles and some ash preparations contain wheat.",
      "Sesame is present in some breads and regional foods but is not a universal hidden component of Persian spice blends.",
      "Fish and shellfish become especially relevant in Caspian and Persian Gulf regional cooking rather than as routine components of standard spice mixtures.",
      "Commercial blends and prepared sauces should be checked for all nine U.S. major allergens."
    ],
    "pitfalls": [
      "Do not make every Persian dish sweet, floral or saffron-heavy.",
      "Do not make Persian food generically hot with large amounts of chile; classic seasoning is usually aromatic rather than strongly fiery.",
      "Do not replace dried lime with fresh lime and claim the flavor is identical.",
      "Do not omit the parboil-and-steam process when a classic chelow texture is intended.",
      "Do not assume all Iranian regional cuisines are identical to a Tehran-centered Persian canon; Caspian, Azeri, Kurdish, southern and other regional traditions differ substantially.",
      "Do not use the word 'tahdig' for any crispy rice without preserving the deliberate bottom-crust technique."
    ],
    "sources": [
      "https://www.iranicaonline.org/articles/cooking/cooking-iii-principles-and-ingredients-of-modern-persian-cooking/",
      "https://www.iranicaonline.org/articles/berenj-rice/berenj-rice-iii-in-cooking/",
      "https://www.iranicaonline.org/articles/berenj-rice/berenj-rice-i-in-iran/",
      "https://www.iranicaonline.org/articles/rose-water/",
      "https://www.iranicaonline.org/articles/mint-herb/",
      "Food of Life: Ancient Persian and Modern Iranian Cooking and Ceremonies, Najmieh Batmanglij, 2011 edition",
      "Cooking in Iran: Regional Recipes and Kitchen Secrets, Najmieh Batmanglij, 2018",
      "https://www.splendidtable.org/story/2019/03/07/najmieh-batmanglij-returns-to-iran-persian-culinary-journey",
      "https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies",
      "https://www.who.int/news-room/fact-sheets/detail/sodium-reduction"
    ]
  },
  {
    "id": "turkish",
    "label": "Turkish",
    "subtitle": "Pul biber, yogurt, sumac, herbs",
    "about": "Turkish cuisine spans Anatolia between the Black Sea, Aegean and Mediterranean and includes Istanbul at the Bosporus, with major regional differences from the southeast to the Aegean coast. It was shaped by Anatolian foodways, Turkic migrations, Seljuk and Ottoman kitchens, and long interaction with Balkan, Caucasian, Mediterranean and Middle Eastern communities. Representative dishes include mantı, dolma and sarma, kebabs, börek and olive-oil vegetable dishes.",
    "flavors": [
      "pul biber — pul biber — dried red-pepper flakes, ranging from mild to hot",
      "karabiber — karabiber — black pepper",
      "kekik — kekik — Turkish oregano/thyme-type dried herb; botanical identity varies",
      "nane — nane — mint, especially common dried in soups and yogurt dishes",
      "kimyon — kimyon — cumin, particularly with köfte, meat and sucuk",
      "sumak — sumak — sumac, used for tartness with onions, kebabs, salads, fish and other dishes",
      "yenibahar — yenibahar — allspice; traditional but not a universal default",
      "biber salçası — biber salçası — concentrated red-pepper paste, especially important in many Anatolian and southeastern dishes",
      "domates salçası — domates salçası — tomato paste, a common cooked seasoning base",
      "sarımsak — sarımsak — garlic",
      "nar ekşisi — nar ekşisi — pomegranate molasses/sour pomegranate concentrate; especially important in southern and southeastern cuisines",
      "defne yaprağı — defne yaprağı — bay leaf, particularly for fish, meat, tomato-based dishes and preserves"
    ],
    "sweet_only": [
      "damla sakızı — damla sakızı — mastic, mainly in puddings, ice cream and sweets",
      "gül suyu — gül suyu — rosewater, mainly desserts and sweets",
      "mahlep — mahlep — mahlab, mainly sweet and festive breads and pastries"
    ],
    "signature_ingredients": [
      {
        "ingredient": "yufka — yufka — thin rolled flatbread or pastry sheets",
        "substitute": "lavash for flatbread uses or phyllo for layered pastry uses; neither is universally interchangeable"
      },
      {
        "ingredient": "tarhana — tarhana — fermented dried grain-yogurt soup base",
        "substitute": "none"
      },
      {
        "ingredient": "sucuk — sucuk — highly seasoned cured sausage",
        "substitute": "a garlicky beef sausage; chorizo is only a rough functional substitute and has a different spice profile"
      },
      {
        "ingredient": "pastırma — pastırma — pressed, cured beef coated with çemen",
        "substitute": "bresaola plus garlic and fenugreek for a rough functional substitute; none is exact"
      },
      {
        "ingredient": "erişte — erişte — Turkish cut egg noodles",
        "substitute": "wide supermarket egg noodles"
      }
    ],
    "pantry_assumed": [],
    "techniques": [
      "Grill skewered, minced or whole cuts of meat over direct heat for kebab families",
      "Cook vegetables slowly in olive oil and often serve them warm or cool in zeytinyağlı preparations",
      "Stuff or roll vegetables and grape leaves as dolma and sarma",
      "Layer or roll thin dough with cheese, greens or meat for börek",
      "Temper yogurt carefully into soups or sauces and often finish with butter bloomed with dried mint or red pepper"
    ],
    "shortcuts": [
      "Biber salçası: commercial pepper paste can replace homemade pepper paste 1:1 by weight as a starting point. Many jars are salted, so calculate salt_g = sodium_mg × 0.0025 from the nutrition label for the weight used and subtract that salt from the recipe.",
      "Domates salçası: concentrated supermarket tomato paste can usually replace Turkish tomato paste 1:1 by weight, but concentration varies; adjust liquid and browning rather than assuming identical strength. Account for labeled sodium using salt_g = sodium_mg × 0.0025.",
      "Nar ekşisi: use a product whose main ingredient is pomegranate rather than a generic sweet 'pomegranate sauce' when classic sourness is intended. Substitute 1:1 by weight as a starting point; sweetness, acidity and salt vary by product.",
      "Köfte baharı: commercial meatball-spice blends vary; one documented traditional formulation combines coriander, black pepper, cloves, bay and wild thyme. Use 1:1 by weight only in recipes that actually call for köfte seasoning. If salted, derive salt from the label using salt_g = sodium_mg × 0.0025."
    ],
    "allergen_notes": [
      "Sesame: tahin is sesame paste; sesame also coats simit and appears in some breads and sweets.",
      "Milk: yogurt is pervasive in sauces, soups and accompaniments; ayran and cacık also contain dairy, and tarhana commonly contains yogurt or another fermented dairy component.",
      "Wheat: yufka, pide, börek dough, bulgur, many noodles and most tarhana contain wheat.",
      "Egg: some börek doughs or fillings, erişte and dishes such as menemen or egg-bound mixtures contain egg.",
      "Tree nuts: walnuts, pistachios, hazelnuts, almonds or pine nuts occur in some sauces, fillings, pilafs and garnishes.",
      "Fish and shellfish are relevant in coastal dishes but are not standard components of the main spice blends.",
      "Peanut and soy are not traditional core seasonings; their presence in commercial sauces or manufactured foods should be determined from the label rather than inferred from the cuisine."
    ],
    "pitfalls": [
      "Do not reduce Turkish cuisine to kebab, hummus and baklava; vegetable dishes, legumes, grains, soups, yogurt dishes and regional foods are equally important.",
      "Do not describe modern Turkish cuisine as deriving solely from Ottoman palace cooking.",
      "Do not add pomegranate molasses to every Turkish dish; it is particularly important in southern and southeastern traditions.",
      "Do not add fenugreek to ordinary Turkish recipes merely because çemen is traditional; its use is specialized and regional.",
      "Do not assume kekik always means the exact same botanical herb as supermarket English thyme.",
      "Do not treat all pul biber as Aleppo pepper; Turkish red-pepper flakes vary substantially by region and processing, and isot is a distinct Şanlıurfa pepper product.",
      "Do not make every meze tahini-based; yogurt, vegetables, legumes, olive oil, herbs and seafood also form major meze families."
    ],
    "sources": [
      "https://www.ktb.gov.tr/EN-98790/culinary-culture.html",
      "https://www.ktb.gov.tr/EN-98797/the-ottoman-cuisine.html",
      "https://goturkiye.com/gastronomy/blog/10-most-popular-spices-in-turkish-cuisine",
      "https://www.turkish-cuisine.org/regional-cuisine-4/southeast-anatolian-region-127/ottoman-heritage-3/ingredients-7/ingredients-unique-to-turkish-cuisine-68/ingredients-7/ingredients-used-in-turkish-cuisine-66/spices-74.html",
      "https://www.kulturportali.gov.tr/turkiye/gaziantep/neyenir/gazantep-mutfagi",
      "https://goturkiye.com/gastronomy/blog/rediscovering-turkish-cuisine-in-antakya-hatay",
      "https://www.kulturportali.gov.tr/portal/kastamonu-pastirmasi",
      "https://goturkiye.com/gastronomy/turkish-cuisine",
      "https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies",
      "https://www.who.int/news-room/fact-sheets/detail/sodium-reduction"
    ]
  }
]
```