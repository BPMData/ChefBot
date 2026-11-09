# Regional Cuisine Research: Africa

## Summary of biggest surprises and disputes

The largest modeling risk is treating the first node, **“Moroccan & North African,” as a generic North African cuisine**. Moroccan cooking is part of the Maghreb and shares ingredients and techniques with Algeria, Tunisia and other neighbors, but its canonical combinations are not interchangeable with theirs. Paula Wolfert, whose decades of field research are foundational for English-language documentation of Moroccan cooking, emphasizes distinct Moroccan traditions around tagines, couscous, preserved lemon, saffron, cumin and spice mixtures; harissa, by contrast, is much more strongly identified with Tunisia even though it is now used elsewhere in the Maghreb. Ras el hanout also has no single canonical recipe: compositions vary by merchant, household and intended dish. The safest implementation is therefore to make this node **Moroccan**, with North Africa treated as geographic context rather than permission to synthesize a pan-Maghrebi recipe. citeturn917402view1turn564873search3turn564873search4

Ethiopian food presents almost the opposite problem: restaurant shorthand often reduces it to “berbere + injera + spiced butter,” but the cuisine contains both intensely spiced *wot* and mild *alicha*, plus a large repertoire of Orthodox Christian fasting foods in which animal products are omitted. Berbere itself is a family-variable blend rather than a fixed formula, and *niter qibe* is a major flavoring but should not be hard-coded into every Ethiopian dish. Particularly distinctive aromatics such as korerima, koseret and besobela matter more than substituting ordinary “curry spices” if the goal is recognizably Ethiopian flavor. citeturn564873search0turn564873search1turn564873search2turn671185search46

Egyptian cuisine is often flattened into a generic “Middle Eastern” profile. Two especially useful corrections are that Egyptian *ta‘meya* is classically made from fava beans rather than the chickpea base common in many Levantine falafel traditions, and that cumin and coriander are unusually central to Egyptian everyday seasoning. Egypt's *dukkah/dokka* is also a category rather than one formula; an Egyptian terroir inventory documents versions containing varying combinations of cumin, coriander, sesame, nigella, pepper, sumac and seeds. citeturn826820search4turn189613view0turn564873search5

“Nigerian cuisine” requires the strongest regional guardrails of any node here. Nigeria contains hundreds of ethnic and linguistic communities, and ingredients such as ìrù, ogiri, uda, uziza, ehuru, yaji, egusi and ogbono belong to overlapping but not universally shared regional traditions. Ozoz Sokoh explicitly approaches Nigerian cooking as a diverse body of foodways rather than a tiny set of “national dishes”; her documentation also shows how both indigenous seasonings and imported pantry conventions such as dried thyme and Nigerian-style curry powder coexist. An AI should therefore avoid putting egusi, palm oil, crayfish, yaji or fermented locust beans into arbitrary Nigerian recipes simply because each is “Nigerian.” citeturn917402view4turn575825search0turn575825news42turn826820search6

Senegalese cooking has unusually well-documented fermented flavor builders. Chef Pierre Thiam identifies *nététou* (fermented locust bean), *yët* (fermented mollusk), *guedj* (dried/fermented fish), *kéthiakh* and related preserved products as important sources of depth; these are consequential both for authenticity and for allergen handling. *Ceebu jën* is formally recognized by UNESCO as Senegalese intangible cultural heritage and is associated especially with Saint-Louis, but the popular attribution of its invention to a single cook, Penda Mbaye, is better treated as an origin story than a hard historical fact. citeturn575825search4turn917402view5turn450887search0

## Fact-check

Per the supplied specification, the fact-check is **skipped**. There are no existing African cuisine descriptions or flavor lists in the app to classify as correct, wrong or disputed.

## Research findings and implementation guidance

For **Moroccan cooking**, the strongest recipe-steering signal is not “use lots of spices,” but balance. Wolfert describes Moroccan cooks as using spices to extend rather than bury the flavor of the main ingredient; cumin, ginger, turmeric, saffron, cinnamon, paprika, fresh coriander/cilantro, parsley and garlic recur, while preserved lemon and olives create profiles that are difficult to reproduce with fresh lemon alone. Chermoula is best modeled as a family of herb-garlic-spice marinades rather than as one fixed paste. Couscous should also be treated as a technique, not merely an ingredient: classic preparation involves steaming the grain over the stew rather than simply hydrating instant couscous. citeturn564873search3turn564873search4turn497095search4

For **Ethiopian cooking**, an ingredient-aware generator should decide first whether it is making a red *wot*, a mild *alicha*, a sautéed *tibs*-type dish, or a fasting dish. Berbere is appropriate to many red stews but is not an all-purpose requirement. *Niter qibe* is deeply characteristic of non-fasting cookery, and korerima plus koseret are particularly important to its aroma; ordinary green cardamom is not an exact substitute for korerima. Injera traditionally depends on fermentation and teff, so a wheat tortilla, naan or an unfermented “flatbread” should never be silently represented as equivalent. citeturn564873search0turn564873search2turn826820search0turn671185search5

For **Egyptian cooking**, garlic, onion, cumin, coriander, lemon, vinegar and chile often do more work than a large multi-spice blend. The UNIDO Egyptian terroir inventory explicitly calls cumin and coriander essential elements of the cuisine's flavor profile and documents substantial variation in dokka. Useful dish-level anchors are *ful medames*, fava-bean *ta‘meya*, *molokhia* and *koshari*; those four alone prevent several common AI errors, including chickpea-only “Egyptian falafel,” making molokhia as ordinary spinach soup, and turning koshari into a seasoned rice pilaf. citeturn189613view0turn826820search4turn826820search5turn450887search20

For **Nigerian cooking**, recipe generation should begin with the dish family and regional tradition rather than with a national seasoning template. Fermented locust bean (*ìrù/daddawa*), fermented seed condiments such as ogiri, aromatic peppers and spices including uda, uziza and ehuru, dried seafood, red palm oil, melon seeds, ogbono and yaji all have strong identities but are not universally interchangeable. Yaji is especially important for allergen logic: suya-seasoning traditions frequently incorporate ground *kulikuli*, a peanut product, and Sokoh's own published formulation uses a peanut component. citeturn826820search7turn575825search0turn575825news42turn497095search10

For **Senegalese cooking**, the app should recognize a strong distinction among *ceebu jën*, yassa, mafé and other sauce-and-rice traditions rather than blending their signatures. The Senegalese embassy describes ceebu jën as fish, rice cooked in a tomato-rich broth and vegetables; yassa as grilled marinated chicken or fish finished with abundant onions and mustard; and mafé as a peanut-based stew. Rof is specifically associated with seasoning or stuffing fish for ceebu jën, while nokoss is a broader pounded aromatic base. Fermented fish and mollusk seasonings provide the deep savory note that an AI might otherwise incorrectly replace with soy sauce or Southeast Asian fish sauce. citeturn917402view5turn575825search25turn575825search4turn575825search12

Exact salt content is the least stable part of the requested shortcut data. Commercial berbere, ras el hanout, harissa, yaji, pepper-soup spice, bouillon and nokoss products vary substantially by maker. For that reason the JSON below gives reliable **use-by-weight guidance**, identifies blends that are traditionally capable of being salt-free, and marks generic salt estimates **LOW CONFIDENCE** rather than inventing precision. For packaged products, the safe conversion is: **salt-equivalent grams ≈ sodium milligrams in the amount used × 2.5 ÷ 1000**.

## Complete JSON array

```json
[
  {
    "id": "moroccan_north_african",
    "label": "Moroccan",
    "subtitle": "Tagines, couscous, chermoula, preserved lemon",
    "about": "This node should represent Morocco specifically, on the Atlantic and Mediterranean edges of northwest Africa between the Rif, Atlas Mountains and Sahara, rather than a generic North African blend. Amazigh, Arab, Andalusi, Jewish, sub-Saharan African and Mediterranean histories all shaped a cuisine built around balanced spices, slow-cooked tagines, steamed couscous, preserved foods and herb-rich marinades. Representative dishes include couscous with vegetables, chicken tagine with preserved lemon and olives, harira and pastilla.",
    "flavors": [
      "كمون (kammun; Moroccan Arabic/Darija romanization: kammun) — cumin",
      "زنجبيل / سكنجبير (zanjabil / skanjbir; Darija: skanjbir) — ground ginger",
      "كركم (kurkum; Darija: l-kurkum) — turmeric",
      "زعفران (zaʿfaran; Darija: zaafran) — saffron",
      "قرفة (qirfa; Darija: qarfa) — cinnamon, also used in savory dishes",
      "تحميرة / فلفلة حلوة (tahmira / felfla hlwa; common Darija romanization) — paprika/sweet red pepper",
      "قزبر (qzbur; Darija romanization: qzbur) — fresh coriander/cilantro",
      "معدنوس (maʿdnus; Darija romanization: maadnous) — parsley",
      "ثوم (thum; Darija: touma) — garlic",
      "حامض مصير (hamid msayyar; common Darija romanization: lhamd msayyar) — salt-preserved lemon"
    ],
    "sweet_only": [
      "ماء الزهر (maʾ az-zahr; common romanization: ma zhar) — orange-blossom water, mainly sweets and sweet drinks",
      "ماء الورد (maʾ al-ward; common romanization: ma ward) — rose water, mainly sweets and confections"
    ],
    "signature_ingredients": [
      {
        "ingredient": "salt-preserved lemon",
        "substitute": "none; fresh lemon gives acidity but not the fermented peel aroma or texture"
      },
      {
        "ingredient": "smen, aged salted butter",
        "substitute": "clarified butter plus a little salt is only an approximation"
      },
      {
        "ingredient": "warqa pastry for pastilla",
        "substitute": "phyllo dough, approximate"
      },
      {
        "ingredient": "Moroccan green or purple olives",
        "substitute": "good-quality brined green olives"
      }
    ],
    "pantry_assumed": [],
    "techniques": [
      "slow, moist cooking in a tagine or heavy covered pot",
      "steaming couscous repeatedly over a stew or broth in classic preparation",
      "marinating fish or vegetables with chermoula",
      "preserving lemons in salt and their own juices",
      "combining savory meat or poultry with fruit, honey or cinnamon in selected dishes without making the whole cuisine generically sweet"
    ],
    "shortcuts": [
      {
        "product": "ras el hanout",
        "usually_contains": "variable mixture that may include cinnamon, ginger, turmeric, pepper, cardamom, nutmeg, mace, cloves, rose or other aromatics; there is no fixed formula",
        "swap_by_weight": "Use about 5-10 g per 1 kg of stew ingredients when a recipe calls for a Moroccan mixed-spice profile; start low because blends vary.",
        "salt_g": "0.0 g if the blend is explicitly salt-free; otherwise calculate from the package label. Do not assume all ras el hanout is salt-free."
      },
      {
        "product": "prepared chermoula",
        "usually_contains": "cilantro/coriander, parsley, garlic, cumin, paprika or chile, lemon and oil; formulas vary",
        "swap_by_weight": "About 60-100 g prepared chermoula can season 1 kg fish or vegetables in place of a freshly pounded marinade.",
        "salt_g": "LOW CONFIDENCE for generic products: brand-dependent. Calculate salt-equivalent from the sodium label."
      },
      {
        "product": "harissa paste",
        "usually_contains": "red chile, garlic, spices and oil; it is Tunisian in origin but is used in parts of Morocco and the wider Maghreb",
        "swap_by_weight": "Use roughly 10-20 g per 1 kg food when a Moroccan recipe specifically calls for harissa; do not use it as a universal Moroccan seasoning.",
        "salt_g": "LOW CONFIDENCE: commercial pastes vary substantially; calculate from the label."
      }
    ],
    "allergen_notes": [
      "Smen and clarified butter contain milk proteins unless specifically certified otherwise.",
      "Amlou, a Moroccan almond-argan-honey spread, contains tree nuts and should not be treated as an allergen-free general condiment.",
      "Sesame is used in some breads, sweets and seed mixtures; check garnishes and commercial blends.",
      "Pastilla/warqa and most breads contain wheat; some pastillas also contain egg and almonds."
    ],
    "pitfalls": [
      "Do not treat Moroccan as synonymous with all North African or Maghrebi cooking.",
      "Do not put harissa into every Moroccan dish; it is much more central to Tunisian cooking.",
      "Do not treat ras el hanout as one standardized recipe or as a required seasoning for every tagine.",
      "Do not make every Moroccan savory dish sweet with dried fruit and cinnamon.",
      "Do not replace preserved lemon with an equal amount of fresh lemon and claim the result is equivalent.",
      "Do not boil instant couscous and describe that method as the classic Moroccan couscous technique."
    ],
    "sources": [
      "https://www.bloomsbury.com/uk/food-of-morocco-9781408827468/",
      "https://www.saveur.com/article/Travels/Basics-of-Moroccan-Food/",
      "https://www.saveur.com/article/Recipes/Charmoula/",
      "The Food of Morocco, Paula Wolfert, 2011",
      "Couscous and Other Good Food from Morocco, Paula Wolfert, revised edition 1987",
      "Arabesque: A Taste of Morocco, Turkey, and Lebanon, Claudia Roden, 2006"
    ]
  },
  {
    "id": "ethiopian",
    "label": "Ethiopian",
    "subtitle": "Injera, berbere, wot, spiced butter",
    "about": "Ethiopia spans highlands around Addis Ababa and the northern plateau, the Rift Valley and hotter eastern and southern regions, so its food is highly regional. Highland Christian fasting practice, Muslim food traditions, indigenous crops and centuries of Red Sea and inland trade all contribute to a cuisine of fermented flatbreads, legumes, long-cooked onion stews, aromatic chile blends and spiced butter. Representative dishes include doro wot, misir wot, siga tibs and injera with vegetable and pulse dishes.",
    "flavors": [
      "በርበሬ (berbere; romanization: berbere) — complex red-chile spice blend",
      "ንጥር ቅቤ (niter qibe; also nit'ir qibe/niter kibbeh) — clarified butter infused with Ethiopian aromatics",
      "ኮረሪማ (korerima; also korarima) — Ethiopian cardamom",
      "ኮሰረት (koseret; also kosseret) — Lippia abyssinica, especially important in spiced butter",
      "በሶብላ (besobela; also besobila) — Ethiopian sacred basil",
      "ሚጥሚጣ (mitmita; romanization: mitmita) — hot chile seasoning, often with korerima and salt",
      "መከለሻ (mekelesha; romanization: mekelesha) — aromatic finishing-spice mixture",
      "ጥቁር አዝሙድ (tikur azmud; romanization: tikur azmud) — black cumin/nigella terminology varies by market",
      "ዝንጅብል (zinjibil; common romanization: zinjibil) — ginger",
      "ነጭ ሽንኩርት (nech shinkurt; romanization: nech shinkurt) — garlic, literally 'white onion'"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      {
        "ingredient": "teff flour",
        "substitute": "none for traditional teff injera; buckwheat or millet can imitate some flavor but not the same fermentation, texture or identity"
      },
      {
        "ingredient": "shiro flour, roasted ground chickpea or pulse flour seasoned for shiro",
        "substitute": "plain chickpea flour plus separately added Ethiopian seasonings, approximate"
      },
      {
        "ingredient": "ayib, fresh Ethiopian curd cheese",
        "substitute": "well-drained farmer cheese or mild ricotta, approximate"
      },
      {
        "ingredient": "korerima, Ethiopian cardamom",
        "substitute": "none exact; ordinary green cardamom is distinctly different"
      }
    ],
    "pantry_assumed": [],
    "techniques": [
      "fermenting teff batter before baking injera on a broad griddle",
      "slowly cooking large quantities of onion to build the base of wot",
      "braising red wot with berbere or preparing milder alicha without the same chile profile",
      "clarifying and perfuming butter to make niter qibe",
      "quick sautéing or searing meat for tibs"
    ],
    "shortcuts": [
      {
        "product": "commercial berbere",
        "usually_contains": "dried chile with varying combinations of fenugreek, ginger, korerima/cardamom, coriander, cloves, cinnamon, garlic and other spices",
        "swap_by_weight": "Use about 10-25 g per 1 kg finished stew ingredients depending on heat and concentration; classic wot can use more, so taste and recipe context matter.",
        "salt_g": "0.0 g only for a product labeled salt-free. Some blends contain salt, so calculate from the label."
      },
      {
        "product": "commercial niter qibe",
        "usually_contains": "clarified butter infused with combinations of korerima, koseret, besobela, fenugreek, ginger, garlic and other aromatics",
        "swap_by_weight": "Replace plain cooking butter or fat 1:1 by weight when the recipe calls for niter qibe; 20 g commercial niter qibe replaces 20 g homemade.",
        "salt_g": "Usually little or no added salt in traditional formulations, but packaged products vary; verify label."
      },
      {
        "product": "commercial mekelesha",
        "usually_contains": "warm finishing spices such as korerima/cardamom, cinnamon, cloves, black pepper, cumin, long pepper or nutmeg",
        "swap_by_weight": "Use about 1-3 g per 1 kg stew near the end of cooking rather than substituting it for berbere.",
        "salt_g": "Usually 0.0 g if sold as a pure spice blend; verify label."
      }
    ],
    "allergen_notes": [
      "Niter qibe is dairy and therefore contains milk unless a plant-oil fasting version is explicitly used.",
      "Restaurant or diaspora injera is sometimes blended with wheat or barley flour; pure teff is gluten-free but the finished bread must not be assumed wheat-free.",
      "Awaze may be loosened with beer; beer can introduce wheat or barley exposure depending on product.",
      "Commercial spice blends should be checked for undeclared or cross-contact allergens even though traditional berbere itself need not contain a major US allergen."
    ],
    "pitfalls": [
      "Do not put berbere into every Ethiopian dish; alicha and many vegetable or fasting dishes follow different seasoning patterns.",
      "Do not put butter into Orthodox Christian fasting dishes.",
      "Do not treat ordinary green cardamom as an exact replacement for korerima.",
      "Do not call an unfermented pancake or wheat tortilla injera.",
      "Do not make wot like a quick curry; extended onion cooking is a defining structural technique.",
      "Do not collapse Ethiopian and Eritrean cuisines into one undifferentiated recipe tradition even though they share many foods."
    ],
    "sources": [
      "https://www.hachetteindia.com/Home/bookdetails/Info/9780857834669/ethiopia",
      "https://www.si.edu/object/ethiopia-recipes-and-traditions-horn-africa-yohanis-gebreyesus-jeff-koehler%3Asiris_sil_1109218",
      "https://www.epicurious.com/recipes-menus/niter-kibbeh-herbs-spices-article",
      "https://www.epicurious.com/recipes/food/views/awaze-dipping-sauce",
      "Ethiopia: Recipes and Traditions from the Horn of Africa, Yohanis Gebreyesus with Jeff Koehler, 2018"
    ]
  },
  {
    "id": "egyptian",
    "label": "Egyptian",
    "subtitle": "Ful, ta'ameya, molokhia, cumin, garlic",
    "about": "Egyptian cooking follows the Nile Valley and Delta from Upper Egypt to Cairo, Alexandria and the Mediterranean coast, with additional traditions in oases and desert communities. Ancient agricultural continuity, Coptic and Islamic traditions, Ottoman rule and Mediterranean migration all contributed to a cuisine especially rich in breads, legumes, vegetables, garlic, cumin and coriander. Representative dishes include ful medames, fava-bean ta'ameya, molokhia and koshari.",
    "flavors": [
      "كمون (kammūn; Egyptian Arabic romanization: kammun) — cumin",
      "كزبرة (kuzbara; Egyptian Arabic romanization: kozbara) — coriander seed and fresh coriander",
      "ثوم (tūm; Egyptian Arabic romanization: tom) — garlic",
      "بصل (baṣal; Egyptian Arabic romanization: basal) — onion",
      "شطة (shaṭṭa; Egyptian Arabic romanization: shatta) — hot chile/chile condiment",
      "دقة / دُقّة (duqqa; common romanizations: dukkah, dokka) — pounded spice-and-seed mixture with highly variable formulas",
      "طحينة (taḥīna; romanization: tahina) — sesame paste",
      "خل (khall; romanization: khal) — vinegar, especially important to koshari and pickles",
      "ليمون (laymūn; Egyptian Arabic romanization: lamoun) — lemon",
      "حبة البركة (ḥabbat al-baraka; common romanization: habbet el-baraka) — nigella seed"
    ],
    "sweet_only": [
      "ماء الورد (māʾ al-ward; romanization: ma ward) — rose water, mainly confectionery and desserts",
      "ماء الزهر (māʾ al-zahr; romanization: ma zahr) — orange-blossom water, mainly desserts and sweets",
      "مستكة (mastika; romanization: mastika) — mastic, used particularly in sweets and dairy desserts"
    ],
    "signature_ingredients": [
      {
        "ingredient": "molokhia leaves, Corchorus/Jute mallow",
        "substitute": "none exact; spinach does not reproduce the characteristic mucilaginous texture"
      },
      {
        "ingredient": "small dried fava beans for ful",
        "substitute": "canned fava beans, with loss of some texture from long simmering"
      },
      {
        "ingredient": "split dried fava beans for ta'ameya",
        "substitute": "none if the dish is to remain classically Egyptian ta'ameya; chickpeas produce a different falafel tradition"
      },
      {
        "ingredient": "baladi bread",
        "substitute": "whole-wheat pita, approximate"
      }
    ],
    "pantry_assumed": [],
    "techniques": [
      "very slow simmering of fava beans for ful medames",
      "soaking, grinding and deep-frying herb-rich fava batter for ta'ameya",
      "making a garlic-coriander ta'leya and adding it as a sizzling aromatic finish to dishes such as molokhia",
      "stuffing vegetables and leaves with seasoned rice mixtures for mahshi",
      "frying onions deeply crisp and layering separate rice, lentil, pasta and sauces for koshari"
    ],
    "shortcuts": [
      {
        "product": "prepared dukkah/dokka",
        "usually_contains": "variable toasted coriander, cumin, sesame and pepper; many versions add nigella, nuts, sumac or other seeds",
        "swap_by_weight": "Use 5-15 g as a finishing seasoning rather than as a universal Egyptian spice blend.",
        "salt_g": "LOW CONFIDENCE for generic dukkah because formulas vary. Pure unsalted mixes contribute 0.0 g; packaged salted versions require label calculation."
      },
      {
        "product": "prepared tahini",
        "usually_contains": "ground sesame seed, sometimes only sesame and sometimes added salt",
        "swap_by_weight": "Replace homemade sesame paste 1:1 by weight; 30 g prepared tahini replaces 30 g homemade.",
        "salt_g": "0.0 g only if the ingredient list is sesame alone; otherwise calculate from label."
      },
      {
        "product": "canned ful/fava beans",
        "usually_contains": "cooked fava beans, water and often salt",
        "swap_by_weight": "About 240 g drained canned fava beans can replace roughly 80-100 g dry beans after cooking, but texture and flavor differ.",
        "salt_g": "LOW CONFIDENCE: highly brand-dependent; rinse and calculate from label rather than assuming a fixed value."
      }
    ],
    "allergen_notes": [
      "Tahini and many dukkah blends contain sesame.",
      "Dukkah may contain tree nuts such as hazelnut or almond even though nut-free Egyptian versions also exist.",
      "Samna/ghee and some pastry or rice preparations contain milk.",
      "Baladi bread, feteer, macaroni in koshari and many pastries contain wheat.",
      "Some pastries and baked dishes contain egg; do not infer egg-free status from the cuisine generally."
    ],
    "pitfalls": [
      "Do not use chickpeas as the default base for Egyptian ta'ameya; fava beans are the classic Egyptian distinction.",
      "Do not treat dukkah as a single standardized recipe.",
      "Do not replace molokhia with spinach and call the texture equivalent.",
      "Do not force a generic Levantine hummus-tabbouleh flavor template onto Egyptian dishes.",
      "Do not turn koshari into one-pot spiced rice; its separately prepared components and sauces are central to the dish.",
      "Do not assume Egyptian savory food is heavily perfumed with cinnamon, cardamom and allspice; garlic, cumin, coriander, onion, chile, lemon and vinegar are often more characteristic."
    ],
    "sources": [
      "https://www.unido.org/sites/default/files/files/2020-08/Inventorying_of_Egypian_Terroir_Food_Products.pdf",
      "https://artsandculture.google.com/story/RQWBwvS32ezWoQ",
      "https://doi.org/10.1186/s42779-023-00177-4",
      "https://www.metmuseum.org/de/perspectives/food-and-feasts-in-middle-kingdom-egypt",
      "The New Book of Middle Eastern Food, Claudia Roden, 2000"
    ]
  },
  {
    "id": "nigerian",
    "label": "Nigerian",
    "subtitle": "Peppers, fermented beans, soups, smoke",
    "about": "Nigeria stretches from the Atlantic mangrove and Niger Delta coast through humid forest zones to the savanna and Sahel, with Lagos, the Yoruba southwest, Igbo southeast and Hausa-speaking north representing only part of its culinary diversity. Hundreds of ethnic communities, long-distance West African trade, Atlantic exchange and British colonial history created many distinct soup, stew, grain, tuber, bean and grilled-food traditions rather than one uniform national pantry. Representative dishes include jollof rice, egusi soup, pepper soup and suya.",
    "flavors": [
      "àtà rodo (Yorùbá; romanization: ata rodo) — Scotch-bonnet-type hot pepper",
      "ìrù (Yorùbá; romanization: iru) — fermented African locust bean condiment",
      "daddawa (Hausa; romanization: daddawa) — fermented African locust bean condiment, related regional tradition",
      "ogiri (Igbo and neighboring usages; romanization: ogiri) — category of pungent fermented seed condiments",
      "uda (Igbo; romanization: uda) — grains of Selim/Xylopia aethiopica",
      "uziza (Igbo; romanization: uziza) — Piper guineense seed or leaf",
      "ehuru (Igbo; romanization: ehuru) — calabash nutmeg",
      "yaji (Hausa; romanization: yaji) — dry spice mixture associated especially with suya; peanut-containing yajin kuli is a major variant",
      "barkono (Hausa; romanization: barkono) — chile/pepper",
      "Nigerian curry powder (English trade name; no single indigenous national name) — an imported-style blend now established in many rice and stew preparations"
    ],
    "sweet_only": [],
    "signature_ingredients": [
      {
        "ingredient": "egusi, oil-rich melon seeds",
        "substitute": "hulled pepitas can approximate body and nuttiness but are not equivalent"
      },
      {
        "ingredient": "ogbono, Irvingia kernels",
        "substitute": "none; its characteristic draw/slippery thickening behavior is distinctive"
      },
      {
        "ingredient": "garri, roasted fermented cassava granules",
        "substitute": "none"
      },
      {
        "ingredient": "white African yam, Dioscorea rotundata",
        "substitute": "none exact; US orange sweet potato is not the same ingredient"
      },
      {
        "ingredient": "ugu, fluted pumpkin leaves",
        "substitute": "spinach or kale, approximate and dish-dependent"
      },
      {
        "ingredient": "unrefined red palm oil",
        "substitute": "none exact; neutral oil lacks its flavor and color"
      }
    ],
    "pantry_assumed": [],
    "techniques": [
      "frying or reducing pepper-and-tomato stew bases until concentrated and the oil separates",
      "pounding or grinding seeds, peppers, spices and fermented condiments",
      "thickening soups with ground egusi, ogbono or other region-specific seeds",
      "charcoal grilling thinly sliced spiced meat for suya",
      "steaming bean batter in leaves, ramekins or molds for moin moin"
    ],
    "shortcuts": [
      {
        "product": "commercial yaji or suya spice",
        "usually_contains": "chile, ginger and aromatic spices; yajin kuli or many suya blends also contain ground kulikuli/peanut",
        "swap_by_weight": "Use about 20-40 g blend per 1 kg sliced meat, depending on concentration.",
        "salt_g": "LOW CONFIDENCE: commercial blends vary and many are salted. Calculate from label; do not assume zero. Treat peanut status as mandatory label data."
      },
      {
        "product": "pepper-soup spice blend",
        "usually_contains": "variable combinations of uda, ehuru, uziza, alligator pepper and other regional spices",
        "swap_by_weight": "Use about 5-12 g per liter of soup as a starting range, then adjust to the blend.",
        "salt_g": "0.0 g for a clearly labeled pure spice blend; many commercial products add salt, so verify."
      },
      {
        "product": "bouillon cube or seasoning powder",
        "usually_contains": "salt, flavor enhancers, spices and flavorings; some contain soy, wheat or milk-derived ingredients",
        "swap_by_weight": "Do not replace herbs or indigenous fermented seasonings 1:1 with bouillon. When a recipe explicitly uses it, dose according to the label and reduce separate salt.",
        "salt_g": "No reliable generic value. Calculate salt-equivalent from the product's sodium label; brand differences are too large for a safe fixed number."
      }
    ],
    "allergen_notes": [
      "Yaji/suya spice frequently contains peanut through ground kulikuli; never assume a suya seasoning is peanut-free.",
      "Ground crayfish, dried shrimp and similar powdered seafood seasonings are shellfish.",
      "Stockfish and dried fish seasonings contain fish.",
      "Commercial bouillon and seasoning cubes may contain soy, wheat or milk ingredients depending on brand.",
      "Some fermented condiment names describe a process rather than one raw material, so ogiri and related products require ingredient-level allergen checking rather than name-based assumptions."
    ],
    "pitfalls": [
      "Do not model Nigeria as one uniform cuisine; regional and ethnic distinctions are fundamental.",
      "Do not add egusi, crayfish, palm oil or iru to every Nigerian soup or stew.",
      "Do not assume all yaji formulations are identical, and do not miss the common peanut component in suya seasoning.",
      "Do not substitute orange sweet potato for Nigerian white yam and call it yam without qualification.",
      "Do not use generic Indian curry powder as the defining flavor of Nigerian cooking even though Nigerian-style curry powder and dried thyme are common in some modern dishes.",
      "Do not describe jollof rice as the sole or universal centerpiece of Nigerian food."
    ],
    "sources": [
      "https://ozozsokoh.com/about",
      "https://www.kpl.gov/catalog/item/?i=ent%3A%2F%2FSD_ILS%2F0%2FSD_ILS%3A2012325",
      "https://www.seriouseats.com/nigerian-store-staples-8675787",
      "https://more.ctv.ca/shows/the-good-stuff-with-mary-berg/recipes/2026/beef-suya/",
      "https://academic.oup.com/ijfst/article/59/10/6866/7911750",
      "Chop Chop: Cooking the Food of Nigeria, Ozoz Sokoh, 2025",
      "Longthroat Memoirs: Soups, Sex and Nigerian Taste Buds, Yemisi Aribisala, 2016"
    ]
  },
  {
    "id": "senegalese",
    "label": "Senegalese",
    "subtitle": "Rice, fish, onion, peanut, fermentation",
    "about": "Senegal faces the Atlantic at Africa's westernmost bulge, with Dakar on the Cap-Vert peninsula, Saint-Louis near the Senegal River and Casamance south of The Gambia. Wolof, Lebou, Serer, Fulani, Mandinka, Jola and other communities, Atlantic trade, Islam and French colonial commerce all shaped a cuisine famous for deeply seasoned rice, fish, onion sauces, peanuts and fermented condiments. Representative dishes include ceebu jën, yassa, mafé and soupou kandia.",
    "flavors": [
      "nététou (Wolof; romanization: netetou/netetu) — fermented African locust bean",
      "guedj (Wolof culinary term; romanization: guedj) — dried or fermented fish used as a savory seasoning",
      "yët / yeet (Wolof; romanization: yet/yeet) — dried fermented cymbium sea snail/mollusk",
      "rof (Wolof culinary term; romanization: rof) — pounded parsley-garlic-chile herb mixture used especially to season or stuff fish",
      "nokoss (Wolof culinary term; romanization: nokoss) — pounded aromatic seasoning base, formulas varying by cook",
      "kaani (Wolof; romanization: kaani) — hot chile/pepper",
      "soble (Wolof; romanization: soble) — onion, a major aromatic especially in yassa",
      "xorom (Wolof; romanization: xorom) — salt",
      "daxaar / dakhar (Wolof; romanization: daxaar/dakhar) — tamarind",
      "moutarde (French/Senegalese usage; romanization: moutarde) — mustard, especially characteristic in many yassa preparations"
    ],
    "sweet_only": [
      "fleur d'oranger / orange-blossom water — used mainly in sweet drinks, desserts and some bissap preparations"
    ],
    "signature_ingredients": [
      {
        "ingredient": "broken rice used for ceebu jën",
        "substitute": "ordinary long-grain rice is usable but gives a different absorption and texture"
      },
      {
        "ingredient": "jaxatu/diakhatou, small bitter African eggplant",
        "substitute": "none exact; small eggplant plus a bitter green is only an approximation"
      },
      {
        "ingredient": "fonio",
        "substitute": "quinoa or fine couscous can fill a structural role but are not flavor-equivalent"
      },
      {
        "ingredient": "cassava root",
        "substitute": "none exact; potato changes both texture and flavor"
      },
      {
        "ingredient": "natural unsweetened peanut paste",
        "substitute": "unsweetened smooth peanut butter"
      }
    ],
    "pantry_assumed": [],
    "techniques": [
      "building ceebu jën as a layered one-pot fish, vegetable, broth and rice preparation",
      "pounding rof or nokoss aromatics in a mortar or processor",
      "marinating meat or fish in citrus and onion for yassa, often grilling before finishing in the onion sauce",
      "slowly simmering peanut-based sauces for mafé",
      "charcoal grilling meat for dibi and related grilled preparations"
    ],
    "shortcuts": [
      {
        "product": "prepared nokoss",
        "usually_contains": "garlic, onion or scallion, chile, pepper and parsley, sometimes ginger, nététou, bay or other aromatics",
        "swap_by_weight": "Use about 40-80 g prepared nokoss per 1 kg main ingredients as a starting point, depending on concentration.",
        "salt_g": "LOW CONFIDENCE: homemade nokoss may be unsalted or salted, while commercial products vary. Calculate from label."
      },
      {
        "product": "commercial bouillon cube or seasoning powder",
        "usually_contains": "salt, flavor enhancers, spices and flavorings; ingredient profiles vary widely",
        "swap_by_weight": "Use only when the intended Senegalese recipe calls for bouillon; do not treat it as a replacement for nététou, guedj or yët.",
        "salt_g": "No safe generic value. Calculate salt-equivalent from sodium on the label and reduce separate salt accordingly."
      },
      {
        "product": "prepared peanut butter for mafé",
        "usually_contains": "ground peanuts; US products may additionally contain sugar, salt and stabilizers",
        "swap_by_weight": "Use natural unsweetened peanut butter 1:1 by weight for Senegalese peanut paste; 100 g peanut butter replaces 100 g peanut paste.",
        "salt_g": "0.0 g if made from peanuts only; otherwise use the nutrition label."
      }
    ],
    "allergen_notes": [
      "Mafé and other peanut sauces contain peanuts.",
      "Yët/yeet is a mollusk and therefore a shellfish allergen under US labeling categories.",
      "Guedj and other dried or fermented fish seasonings contain fish.",
      "Commercial bouillon products may contain soy, wheat or milk ingredients depending on manufacturer.",
      "Mustard is not one of the nine major US allergens but is a regulated priority allergen in several other jurisdictions and should remain explicit in ingredient data."
    ],
    "pitfalls": [
      "Do not turn every Senegalese dish into a peanut stew; mafé is one important family, not the whole cuisine.",
      "Do not treat yassa as simply lemon chicken; the large quantity of onions, marination and often grilling are defining.",
      "Do not replace the fermented savory ingredients in ceebu jën automatically with soy sauce or Southeast Asian fish sauce.",
      "Do not treat rof and nokoss as identical even though their ingredients overlap.",
      "Do not hard-code the story that Penda Mbaye definitively invented ceebu jën; Saint-Louis origin is well established, while single-inventor attribution is better treated as tradition.",
      "Do not assume ceebu jën, yassa, mafé and dibi all use the same seasoning profile."
    ],
    "sources": [
      "https://ich.unesco.org/en/RL/ceebu-jn-the-culinary-art-of-senegal-01748",
      "https://ambsenegal.qa/en/senegal/gastronomie",
      "https://www.ifad.org/fr/w/opinions/entretien-avec-le-chef-cuisinier-pierre-thiam-des-recettes-du-changement",
      "https://www.nhpr.org/2015-10-19/senegalese-recipes-from-chef-pierre-thiam",
      "Yolele! Recipes from the Heart of Senegal, Pierre Thiam, 2008",
      "Senegal: Modern Senegalese Recipes from the Source to the Bowl, Pierre Thiam, 2015"
    ]
  }
]
```