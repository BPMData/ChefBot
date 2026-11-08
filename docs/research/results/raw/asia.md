# Regional Cuisines Research for Recipe Generation

## Biggest surprises and disputes

The largest structural issue is that several familiar cuisine labels are much less tidy than recipe apps often assume. China’s “Eight Great Cuisines” is a useful conventional taxonomy, but even the China Cuisine Association has argued that it is too coarse to represent Chinese food accurately; boundaries overlap, and labels such as “Jiangsu” and “Huaiyang” are especially easy to conflate. citeturn378911search11turn785151search30 India is even harder to divide into “North” and “South”: those are useful interface categories, but they collapse dozens of cuisines whose grains, fats, religious practices, spice systems, and historical influences differ substantially. Indian government and historical sources explicitly stress this regional diversity. citeturn730500search1turn730500search7turn730500search9

Several popular authenticity rules are better treated as stereotypes. Thai food does **not** require sweet, sour, salty, and spicy to appear in every individual dish; authoritative descriptions emphasize harmony across a dish or, often, across the meal. citeturn603902search7turn603902search12 Sichuan food is likewise not simply “málà”: a modern Sichuan culinary classification recognizes roughly two dozen flavor profiles, and a substantial share are neither strongly hot nor numbing. citeturn785151search0turn785151search4 South Indian food is not uniformly coconut-heavy or hotter than northern food, while North Indian food cannot accurately be reduced to Punjabi-Mughlai restaurant food with naan, cream, paneer, and tandoori meats. citeturn730500search2turn730500search3turn730500search7

Some “classic flavor” lists also mix seasonings with main ingredients or overly specialized ingredients. Coconut milk in Thai cooking, urad dal in South Indian cooking, nori in Japanese cooking, and pickled vegetables in Sichuan cooking can certainly shape flavor, but they are not all seasonings in the same sense as soy sauce, spices, aromatic roots, or fermented pastes. For a recipe-writing model, the practical distinction matters because these ingredients should not automatically be added merely to make a recipe “taste authentic.”

The biggest export-version issue is Chinese food outside China. Early Chinese restaurants in the United States were strongly shaped by immigrants from Guangdong, particularly Cantonese-speaking communities, but “most Chinese food abroad is Cantonese” is no longer defensible globally, and it was never a good description of Chinese diasporas in Southeast Asia, where Fujianese, Teochew, Hainanese, Hakka, and other traditions are foundational. Smithsonian and Library of Congress material supports the Guangdong/Cantonese dominance of the early U.S. story specifically, not a universal diaspora claim. citeturn111503search0turn111503search1turn111503search4

Japanese Kanto-versus-Kansai distinctions are real but should remain tendencies rather than hard recipe rules. Government sources support the classic comparison of kombu-forward, lighter-colored Kansai dashi and usukuchi soy sauce versus bonito-forward, darker Kanto preparations, but individual dishes, producers, and households vary considerably. Usukuchi is lighter in color yet is commonly saltier by concentration than koikuchi, so an AI should never substitute equal volumes solely on color. citeturn460734search0turn460734search1turn460734search6turn460734search11

For Korea, fermentation genuinely is foundational rather than a marketing simplification: kimchi, ganjang, doenjang, gochujang, jeotgal, and other fermented foods are embedded throughout the cuisine. However, “Korean food equals barbecue plus spicy stew” is much too narrow; vegetable banchan, soups, porridges, braises, pancakes, noodles, preserved foods, and seasonal preparations are equally important. citeturn603902search0turn603902search2turn603902search4

Vietnamese, Filipino, Indonesian, Malaysian, and Singaporean cuisines all resist simple national templates. Vietnamese food studies scholarship specifically warns against suppressing major northern, central, southern, ethnic, and historical distinctions under a single national profile. citeturn603902search9 Doreen Fernandez made the same point for the Philippines through dishes as different in origin as indigenous sinigang, indigenized Chinese pancit, and colonial-derived preparations. citeturn603902search11turn603902search13 Indonesia’s archipelagic diversity is similarly fundamental, while Malaysian and Singaporean foodways are inherently multiethnic rather than variants of one Malay template. citeturn865672search0turn865672search2turn865672search3turn865672search5

## Research and implementation notes

For app behavior, the safest model is to interpret every flavor and pantry list as a probability-weighted vocabulary rather than a mandatory checklist. A Sichuan recipe does not need Sichuan pepper; a Cantonese recipe does not need oyster sauce; a Japanese recipe does not need miso; a Korean recipe does not need gochujang; and a Thai recipe does not need coconut milk. The authoritative material repeatedly describes cuisines as repertoires of techniques and flavor structures rather than fixed ingredient sets. citeturn785151search0turn460734search12turn603902search4turn603902search7

The two organizational nodes, `asia` and `eight_great_cuisines`, are included because the requested tree explicitly says branches and leaves. They should **not** be used as authenticity-steering cuisine profiles: “Asia” is far too broad to have a coherent seasoning system, while “Eight Great Cuisines” is a taxonomy rather than a single cuisine. The China, Japan, and India branch objects are national-level aggregates; their “Any” objects instead describe the recognizable export or international image requested in the prompt.

Salt values in the shortcut fields are intentionally approximate when a commercial paste or sauce varies by brand. For a generative recipe system, product-label sodium should override these estimates. A useful conversion is that 1 g sodium corresponds to about 2.54 g sodium chloride; nevertheless, commercial fermented sauces contain other solids and should not be treated as literal salt gram-for-gram.

The sources emphasized here include Japan’s Ministry of Agriculture, Forestry and Fisheries, Korean governmental and cultural institutions, UNESCO intangible-heritage documentation, Indian governmental sources, Chinese culinary/cultural institutions, peer-reviewed food-studies literature, and specialist authors including Fuchsia Dunlop, Colleen Taylor Sen, Doreen Fernandez, Sri Owen, and other regional authorities. The conventional eight-cuisine classification itself is documented by Chinese cultural authorities, while current Chinese sources also caution that it is not exhaustive. citeturn378911search11turn785151search30

## Fact-check of the supplied descriptions

### Cantonese

**“From Guangdong province in southern China, around the Pearl River Delta and the city of Guangzhou.” — CORRECT, with qualification.** Cantonese/Yue cooking has important centers in Guangzhou and the Pearl River Delta, but Guangdong also contains distinct Chaoshan and Hakka traditions, so Cantonese should not be equated with every cuisine of Guangdong. Chinese cultural sources describe Shunde in the Pearl River Delta as an important center of Cantonese cooking. citeturn785151search12turn785151search17

**“Fresh ingredients and light seasoning that lets them taste of themselves.” — CORRECT as a tendency, not a rule.** Freshness, tenderness, balance, and preserving natural flavor are repeatedly identified as Cantonese ideals. citeturn785151search3turn785151search12turn785151search17

**“Steamed fish, quick stir-fries … dim sum.” — CORRECT as representative examples.** Seafood and dim sum are central emblematic forms, although neither defines the entire cuisine. citeturn785151search3turn785151search23

**“Wok hei (the smoky ‘breath of the wok’).” — CORRECT but oversimplified.** Wok hei is associated with high-heat wok cooking and literally invokes the “breath/energy” of the wok; “smoky” describes one sensory component, not the whole concept. It should not be imposed on steamed, braised, or gently cooked Cantonese dishes.

**“Most early Chinese emigrants came from here, which is why it’s the style of most Chinese restaurants abroad.” — WRONG as written globally; CORRECT for much early U.S. Chinese-restaurant history.** Early Chinese immigrants to the United States were disproportionately from Guangdong and early U.S. restaurants were strongly Cantonese-derived. The claim fails when generalized to the entire world, particularly Southeast Asia. citeturn111503search0turn111503search1turn111503search4

The flavor list is **mostly CORRECT** for ginger, scallion, garlic, soy sauce, oyster sauce, fermented black beans, sesame oil, and white pepper. Rice wine is common, but “mijiu or Shaoxing jiu” should not imply equivalence: Shaoxing wine is a specific Zhejiang-origin huangjiu widely used beyond Zhejiang. Chenpi is classically Cantonese but more specialized than ginger, scallion, soy, or oyster sauce; it should not be added automatically.

### Hong Kong

**The description is CORRECT.** Hong Kong cuisine has a Cantonese foundation transformed by migration, maritime trade, British colonialism, and later global influences. Cha chaan teng culture exemplifies this hybrid history, while Hong Kong-style milk tea developed from British tea traditions into a distinctly local form. citeturn111503search6turn111503search7turn111503search9turn111503search10

Siu mei, char siu, roast goose, seafood, milk tea, macaroni soup, and baked pork-chop rice are **CORRECT representative foods**. citeturn111503search10turn111503search11

The flavor ingredients are **mostly CORRECT**, but the romanization is **WRONG as “Jyutping.”** Standard Jyutping uses tone numbers, for example 薑 `goeng1`, 蔥 `cung1`, 蒜 `syun3`, 醬油 `zoeng3 jau4`; the supplied accented spellings resemble pronunciation guides rather than standard Jyutping.

Five-spice, star anise, and hoisin in siu mei are **DISPUTED as universal markers**. They occur in many roast-meat recipes, but char siu and other siu mei formulas vary considerably; none should be mandatory.

### Sichuan

**The geography is CORRECT.** Sichuan and Chongqing occupy the upper-Yangtze Sichuan Basin and surrounding mountains.

**“Famous for málà … and fermented broad-bean paste” — CORRECT.** Sichuan pepper, chiles, and Pixian-style doubanjiang are defining parts of the repertoire. citeturn785151search20turn785151search29

**“Dozens of named flavor profiles, many not hot at all.” — CORRECT.** Contemporary descriptions commonly enumerate about 24 flavor profiles and explicitly note that many are not strongly chile-hot or numbing. citeturn785151search0turn785151search4

Mapo tofu, gongbao/kung pao chicken, and twice-cooked pork are **CORRECT representative dishes**. citeturn785151search20

The flavor list is **mostly CORRECT**, especially huajiao, dried chile, doubanjiang, garlic, ginger, scallion, paocai, and douchi. Star anise and five-spice are **DISPUTED as top everyday signature flavors**; black vinegar, soy sauce, sesame paste/oil, preserved mustard greens such as yacai, and pickled chile are generally more useful recipe-steering signals. Paocai is genuinely important and historically embedded in Sichuan food culture. citeturn785151search27

### Shandong

The geography, strong seafood tradition, scallion use, clear and “milky” broths, and high-heat techniques are **mostly CORRECT**. Chinese cultural sources explicitly identify the cuisine as old and influential and describe clear and thick/milky soup traditions. citeturn785151search32

**“Often called the oldest of China’s great regional styles.” — DISPUTED/CONVENTIONAL CLAIM.** It is widely repeated in Chinese culinary literature, but “oldest cuisine” is not a historically testable absolute. citeturn785151search32

**“A major influence on Beijing’s imperial court cooking.” — BROADLY CORRECT but difficult to quantify.** Shandong cooks and techniques significantly influenced northern elite cooking, but Beijing court cuisine also drew from Jiangnan, Manchu, Muslim, and other traditions.

The seasoning list is **mostly plausible**, particularly scallion, ginger, garlic, soy, vinegar, sesame oil, and white pepper. Star anise belongs mainly to braises and stocks rather than functioning as a universal Shandong marker.

**“Signature ingredient: wood ear mushrooms.” — WRONG/WEAK.** Wood ear is widespread across China and not sufficiently diagnostic of Shandong. Seafood such as sea cucumber, prawns, shellfish, and yellow croaker, plus Shandong scallions, are more defining. Qingdao/Shandong sources emphasize seafood rather than wood ear. citeturn785151search45

### Jiangsu

**“Jiangsu cuisine = Huaiyang cuisine” — DISPUTED and too broad.** Huaiyang is centered particularly on Huai’an and Yangzhou and is one major Jiangsu tradition; Suzhou/Wuxi, Nanjing, and other Jiangsu areas have distinguishable cuisines. Some popular sources use “Jiangsu/Huaiyang” loosely, which explains the confusion. citeturn785151search2turn785151search14turn785151search21

Lower-Yangtze/Grand-Canal geography, freshwater produce, seasonality, precise knife work, and delicate braising are **CORRECT** for Huaiyang and much of Jiangsu’s prestige cuisine. citeturn785151search7turn785151search14turn785151search16

**“Delicate and slightly sweet.” — GENERALLY CORRECT but more true in some subregions than others.** Huaiyang sources describe light, fresh, gently sweet flavors. citeturn785151search21turn785151search25

Lion’s head meatballs and Yangzhou fried rice are **CORRECT representatives**. citeturn785151search15turn785151search26

Ginger, scallion, rice wine, soy, sugar, vinegar, and sesame oil are **CORRECT common flavorings**. Red fermented tofu is **DISPUTED as a core Jiangsu-wide seasoning**.

Osmanthus sugar/syrup as dessert-oriented is **MOSTLY CORRECT**, although osmanthus also appears in sweetened savory-sweet preparations and beverages, so “dessert-only” is slightly too rigid.

Dried bamboo shoots are **PLAUSIBLE but not uniquely defining**; freshwater crab, river fish, water bamboo, lotus products, and regionally important cured meats may provide stronger geographic signals.

### Japanese Kansai

The geography and Kyoto/Osaka contrast are **CORRECT**. JNTO describes Kansai as encompassing Kyoto’s refined traditions and Osaka’s okonomiyaki/takoyaki culture. citeturn460734search5

**“Kombu-based dashi and usukuchi soy sauce keep food pale and delicate.” — CORRECT as a regional tendency.** Japanese government sources explicitly contrast kombu-forward Osaka/Kansai dashi with bonito-forward Kanto and identify usukuchi as historically associated with Kansai cooking. citeturn460734search0turn460734search1

**“Usukuchi is surprisingly a little saltier.” — GENERALLY CORRECT for traditional formulations, but brand-dependent.** Light color does not mean lower sodium; do not substitute it as if it were “low-sodium soy sauce.” citeturn460734search1turn460734search11

The flavor list is **MIXED**. Dashi, usukuchi, mirin, sake, kombu, katsuobushi, sansho, negi, and Kyoto-style white miso are reasonable. “Kansai shoyu” is **not a formal soy-sauce category**; say usukuchi when that is what is meant. Yuzu and shiso are widespread Japanese ingredients rather than exclusively Kansai markers. Listing both dashi and its components as separate core flavors is redundant.

### Japanese Kanto

The stronger/darker general profile, koikuchi soy sauce, and greater bonito emphasis are **CORRECT tendencies**. citeturn460734search4turn460734search6

Edomae sushi and Edo tempura as urban Edo foods are **CORRECT**. Government sources describe both in connection with Edo street-food culture. citeturn460734search4turn460734search9

**“Soba … began as Edo fast food.” — WRONG in that wording.** Soba noodles predate Edo street stalls; what developed strongly in Edo was a particular urban soba culture and extensive stall/restaurant trade. citeturn460734search3

Koikuchi, dashi, wasabi, negi, ginger, sake, and tsuyu are **reasonable**. Red miso is **WEAK as a Kanto marker**; strongly red/mame-miso traditions are more characteristic of parts of central Japan such as Aichi. Nori is a food ingredient/garnish rather than a seasoning in the same category as soy or mirin.

### North Indian

**“From Punjab and the northern plains, shaped by the Mughal courts.” — DISPUTED because it makes one northern subset stand for the whole.** Punjab and Mughlai/Delhi-Lucknow traditions are important, but North India also includes very different cuisines of Kashmir, Rajasthan, Uttar Pradesh, Uttarakhand, Himachal, Bihar, and other areas. Historical sources emphasize India’s regional heterogeneity. citeturn730500search7turn730500search9

Wheat breads are **generally important**, but naan is far more restaurant/tandoor-associated than an everyday bread in many homes; roti/chapati/paratha are much safer defaults. citeturn730500search2

**“Rich gravies with ghee, cream, yogurt and paneer.” — CORRECT for Punjabi/Mughlai restaurant idioms, WRONG as a North-India-wide default.** Many northern home dishes are dry, broth-like, lentil-based, mustard-oil based, or otherwise dairy-light.

Turmeric, cumin, coriander, chile, garam masala, cardamom, cloves, fenugreek, and hing are **valid northern flavors**, though not all appear together. Black mustard seed is **less diagnostic of North India as a whole** than cumin, ajwain, fennel, black cardamom, dried mango, or kasuri methi depending on subregion.

### South Indian

The five-state geography is **CORRECT** as a modern broad grouping.

Rice, lentils, dosa, idli, sambar, tempering, mustard seed, curry leaves, and tamarind are **good broad signals**, but none is universal. India’s own tourism material warns that even Tamil Nadu alone contains multiple distinct cuisines. citeturn730500search3

**“Coconut …” — DISPUTED as a South-India-wide default.** Coconut is especially important in Kerala and many coastal cuisines, but much less universally dominant in interior Telangana, Andhra, northern Karnataka, and some Tamil traditions.

**“Often hotter and more sour than northern cooking.” — DISPUTED/STEREOTYPED.** Andhra and Telangana contain notably chile-hot traditions and tamarind is widespread, but “South hotter than North” is not a reliable authenticity rule.

The flavor list is broadly useful except for two important problems. **Urad dal is not primarily a seasoning**; it is a pulse used as a main structural ingredient as well as in tempering. **“Sukku milagai” for dried red chile is WRONG Tamil.** `Sukku` means dried ginger; dried chile is more appropriately `vara milagai`/`vatral milagai` depending on context.

### Korean

The fermentation description is **CORRECT**. Korean cultural authorities identify doenjang, ganjang, gochujang, kimchi, and fermented seafood as core elements of Korean food culture. citeturn603902search0turn603902search2turn603902search3

Rice with soup/stew and multiple banchan is **CORRECT as a traditional meal pattern**, although modern meals can be much simpler. citeturn603902search4

**“Grilling and long-simmered jjigae are the heart of it.” — TOO NARROW/DISPUTED.** They are important, but namul, guk, tang, jorim, bokkeum, jeon, noodles, porridges, kimchi, and preserved foods are equally structural.

The flavor list is excellent except for one spelling error: **`고추가루` is WRONG in standard Korean orthography; write `고춧가루`, gochutgaru/gochugaru.** The National Institute of Korean Language explicitly gives the standard spelling `고춧가루`. citeturn150695search0turn150695search3

Perilla leaf (`깻잎`, kkaennip) is **CORRECT** as a distinctive ingredient.

### Thai

**“A balance of sweet, sour, salty and spicy in every dish.” — WRONG.** Harmony is foundational, but authoritative Thai descriptions discuss balance within dishes and especially across a meal; individual dishes may be predominantly sour, bitter, salty, mild, rich, or fiery. citeturn603902search7turn603902search12

Fresh herbs, pounded curry pastes, fish sauce, lime, palm sugar, and regional use of coconut milk are **CORRECT**. Thai embassy material describes curry pastes based on fresh aromatics such as chile, shallot, shrimp paste, garlic, galangal, coriander root, lemongrass, makrut lime peel, and pepper. citeturn603902search7

The flavor list is broadly **CORRECT**, but coconut milk is better classified as a major ingredient than a seasoning. “Makrut lime” is the preferable English term for `มะกรูด / makrut`; the older common English name is increasingly avoided.

### Vietnamese

**“Fresh and bright.” — REASONABLE shorthand, not a rule.** Fresh herbs and contrasting textures are prominent in many Vietnamese traditions, but braised, fermented, roasted, and deeply savory foods are equally authentic. Food-studies scholarship specifically warns against flattening Vietnam’s regional cuisines. citeturn603902search9

**“Fish sauce, lime, chili and a pile of fresh herbs at every meal.” — WRONG as an absolute.** Fish sauce is exceptionally important; herbs are highly characteristic in many contexts. Lime and chile are not universal, particularly in northern cooking. citeturn603902search9turn603902search10

**“Pho comes from the north around Hanoi.” — BROADLY CORRECT but origin details are disputed.** Northern Vietnam, especially Hanoi/Nam Dinh, is widely associated with the dish’s emergence, while its exact birthplace and developmental history remain debated.

**“French rule left baguettes and coffee.” — CORRECT but incomplete.** French colonialism strongly influenced bread and coffee culture, while Vietnamese cooks localized both.

The flavor list is **mostly CORRECT**, but star anise is particularly associated with pho and certain braises rather than everyday Vietnamese cooking nationally. Thai/Vietnamese basil, rau răm, mint, lemongrass, fish sauce, ginger, scallion, and turmeric all occur prominently but with substantial regional variation. citeturn603902search9

## Cuisine design conclusions

For AI recipe generation, geographic cues should matter as much as ingredients. Sichuan recipes should think in named flavor structures and techniques rather than merely adding chile and Sichuan pepper. Cantonese recipes should prioritize ingredient quality, cutting, steaming, stir-frying, braising, roasting, and restraint rather than blindly adding oyster sauce. Huaiyang/Jiangsu should emphasize seasonality, knife work, freshwater ingredients, and controlled braising. Japanese Kanto/Kansai differences should influence stock and soy choices but not become hard prohibitions. These distinctions are supported by culinary institutions and specialist literature. citeturn785151search0turn785151search7turn460734search0turn460734search4

For Southeast Asia, avoid the common “one aromatic checklist” failure. Thai dishes do not all contain lemongrass, galangal, basil, coconut, lime, and fish sauce simultaneously. Indonesian food cannot be reduced to sambal and kecap manis, because Javanese, Sumatran, Balinese, Sulawesi, Minangkabau, and eastern Indonesian systems differ dramatically. Malaysian and Singaporean recipes require identification of Malay, Chinese, Indian, Peranakan, Eurasian, or mixed hawker lineage before authenticity can be judged. citeturn603902search7turn865672search0turn865672search4turn865672search5

For exported “Any” cuisines, the model should reproduce the recognizable international version when that node is deliberately chosen, while labeling that repertoire as an export/generalized form rather than treating it as representative home cooking. Chinese “Any” therefore reasonably includes fried rice, dumplings, stir-fries, sweet-savory sauces, soy, ginger, garlic, scallion, and dishes shaped by Cantonese-American and later Sichuan/Hunan influences. Japanese “Any” legitimately centers sushi, ramen, tempura, teriyaki, miso soup, soy, dashi, mirin, and rice vinegar. Indian “Any” legitimately evokes restaurant repertoires such as butter chicken, tikka masala, naan, dal, biryani, paneer, cumin, coriander, turmeric, garam masala, and chile, but this is substantially narrower than domestic Indian cooking. The historical development of export Chinese food is particularly well documented by Smithsonian sources. citeturn111503search0turn111503search2turn111503search4

## Import JSON

```json
[
  {
    "id": "asia",
    "label": "Asia",
    "subtitle": "Navigation category, not cuisine",
    "about": "Asia spans an enormous area from East Asia through South and Southeast Asia and does not have one coherent cuisine. Treat this node as navigation only; representative cuisines in this tree range from Chinese and Japanese traditions to Indian, Korean and Southeast Asian foodways.",
    "flavors": [],
    "sweet_only": [],
    "signature_ingredients": [],
    "pantry_assumed": [],
    "techniques": [],
    "shortcuts": [],
    "allergen_notes": ["No continent-wide allergen assumptions are safe; child cuisines vary radically."],
    "pitfalls": ["Do not generate an 'authentic Asian' flavor profile. Route recipe steering to a country or region instead."],
    "sources": ["Colleen Taylor Sen, Feasts and Fasts: A History of Food in India, 2015", "Fuchsia Dunlop, Invitation to a Banquet: The Story of Chinese Food, 2023", "https://www.maff.go.jp/e/data/publish/attach/pdf/index-112.pdf", "https://link.springer.com/article/10.1186/s42779-019-0009-3"]
  },
  {
    "id": "china",
    "label": "China",
    "subtitle": "Regional, diverse, technique-driven",
    "about": "Chinese cooking spans northern wheat regions, the Yangtze basin, subtropical south, western plateaus and long coastlines. Migration, imperial courts, trade and highly regional agriculture produced many cuisines rather than one uniform style; representative dishes include jiaozi, red-braised pork, steamed fish and hand-pulled or cut noodles.",
    "flavors": ["soy sauce (jiàngyóu, 酱油)", "ginger (jiāng, 姜)", "scallion (cōng, 葱)", "garlic (suàn, 蒜)", "rice vinegar (mǐcù, 米醋)", "sesame oil (zhīmayóu, 芝麻油)", "rice wine (mǐjiǔ, 米酒)", "white pepper (báihújiāo, 白胡椒)", "fermented beans (dòuchǐ, 豆豉)", "star anise (bājiǎo, 八角)"],
    "sweet_only": ["osmanthus (guìhuā, 桂花) — mainly sweets and fragrant syrups in many regions"],
    "signature_ingredients": ["dried wood ear (mù'ěr, 木耳) — substitute: cremini for texture only", "dried shiitake (xiānggū, 香菇) — substitute: fresh shiitake", "Chinese black vinegar (xiāngcù/chéncù, 香醋/陈醋) — substitute: unseasoned rice vinegar plus a little balsamic", "Shaoxing wine (Shàoxīng jiǔ, 绍兴酒) — substitute: dry sherry"],
    "pantry_assumed": ["soy sauce", "neutral cooking oil", "rice or noodles depending on region"],
    "techniques": ["stir-frying", "steaming", "red-braising and other braises", "blanching", "roasting or poaching"],
    "shortcuts": ["Chinese five-spice (wǔxiāngfěn, 五香粉): usually star anise, cassia, fennel, clove and Sichuan pepper; use about 2-4 g per 500 g meat; usually 0 g salt.", "Commercial stir-fry sauces vary widely; for 30 g bottled sauce, reduce separately added salt by roughly 1-2 g and check label sodium."],
    "allergen_notes": ["Soy sauce and many fermented bean sauces contain soy and often wheat.", "Oyster sauce contains shellfish unless vegetarian.", "Sesame oil contains sesame.", "Some hoisin and bean sauces contain wheat and soy.", "Stocks and sauces may hide fish or shellfish."],
    "pitfalls": ["Do not treat Chinese cuisine as synonymous with Cantonese or Sichuan.", "Do not add five-spice, sesame oil or soy sauce to every dish.", "Do not assume all Chinese food is stir-fried.", "The Eight Great Cuisines taxonomy is conventional but incomplete."],
    "sources": ["Fuchsia Dunlop, Invitation to a Banquet: The Story of Chinese Food, 2023", "Fuchsia Dunlop, Every Grain of Rice, 2012", "https://en.chinaculture.org/2018-10/26/content_1288515.htm", "https://en.chinaculture.org/chineseway/2013-04/17/content_455945.htm"]
  },
  {
    "id": "eight_great_cuisines",
    "label": "Eight Great",
    "subtitle": "Canonical Chinese regional taxonomy",
    "about": "The Eight Great Cuisines are the conventional grouping of Shandong, Sichuan, Cantonese, Fujian, Jiangsu, Zhejiang, Hunan and Anhui traditions. The scheme is influential but not exhaustive and omits major food regions such as Beijing, Shanghai, Yunnan, Xinjiang and many ethnic cuisines.",
    "flavors": [],
    "sweet_only": [],
    "signature_ingredients": [],
    "pantry_assumed": [],
    "techniques": [],
    "shortcuts": [],
    "allergen_notes": ["Allergen risks depend on the selected child cuisine; soy, wheat, sesame, fish and shellfish recur frequently."],
    "pitfalls": ["Do not create one composite 'Eight Great Cuisines' recipe.", "Use this node for navigation; select an individual regional cuisine for recipe steering."],
    "sources": ["https://en.chinaculture.org/chineseway/2013-03/20/content_454167_2.htm", "https://en.chinaculture.org/2018-10/26/content_1288515.htm", "Fuchsia Dunlop, Invitation to a Banquet: The Story of Chinese Food, 2023"]
  },
  {
    "id": "sichuan",
    "label": "Sichuan",
    "subtitle": "Chile, peppercorn, fermented depth",
    "about": "Sichuan and Chongqing sit in a mountain-ringed basin along the upper Yangtze in southwest China. Migration and fertile agriculture helped produce a cuisine famous for intricate seasoning systems rather than heat alone; mapo tofu, gongbao chicken, twice-cooked pork and fish-fragrant eggplant are representative.",
    "flavors": ["Sichuan pepper (huājiāo, 花椒)", "dried chile (gānlàjiāo, 干辣椒)", "Pixian broad-bean paste (Píxiàn dòubàn, 郫县豆瓣)", "pickled chile (pàolàjiāo, 泡辣椒)", "garlic (suàn, 蒜)", "ginger (jiāng, 姜)", "scallion (cōng, 葱)", "black vinegar (xiāngcù, 香醋)", "fermented black beans (dòuchǐ, 豆豉)", "sesame oil (zhīmayóu, 芝麻油)", "sesame paste (zhīmajiàng, 芝麻酱)", "preserved mustard greens (yácài, 芽菜)"],
    "sweet_only": [],
    "signature_ingredients": ["Pixian doubanjiang — substitute: chile-bean sauce plus a little miso, imperfect", "yacai preserved mustard greens — substitute: finely chopped Tianjin preserved vegetable or mild pickled mustard", "Sichuan pepper — substitute: none for numbing aroma", "caiziyou roasted rapeseed oil — substitute: neutral oil plus a small amount toasted sesame oil, imperfect"],
    "pantry_assumed": ["chile products", "soy sauce", "vinegar", "garlic and ginger"],
    "techniques": ["stir-frying", "dry-frying (gānbiān)", "braising", "oil-infused cold dishes", "pickling and fermentation"],
    "shortcuts": ["Commercial Sichuan chile-bean paste: 20 g can replace about 20 g homemade fermented chile-bean seasoning; typically contributes roughly 2-4 g salt depending on brand.", "Five-spice is optional and dish-specific; if used, 2 g blend per 500 g meat, normally 0 g added salt."],
    "allergen_notes": ["Doubanjiang and douchi may contain wheat and soy.", "Soy sauce commonly contains wheat and soy.", "Sesame paste/oil contains sesame.", "Some preserved vegetables contain soy or wheat in seasoning."],
    "pitfalls": ["Do not make every dish málà.", "Do not confuse Sichuan food with Hunan food.", "Avoid drowning dishes in sweet bottled chili sauce.", "Star anise and five-spice are not universal Sichuan defaults."],
    "sources": ["Fuchsia Dunlop, The Food of Sichuan, 2019", "https://www.fuchsiadunlop.com/books/the-food-of-sichuan", "https://en.chinaculture.org/a/202308/08/WS64d18053a31035260b81acc0_3.html", "https://en.chinaculture.org/2015-06/12/content_616745_5.htm"]
  },
  {
    "id": "hunan",
    "label": "Hunan",
    "subtitle": "Fresh chile, smoke, sourness",
    "about": "Hunan lies south of the middle Yangtze, with humid river valleys, Dongting Lake and mountainous western areas. Its cooking prizes fresh and preserved chiles, smoked and cured foods, pickles and sharp savory flavors; steamed fish head with chopped chile, Chairman Mao's red-braised pork, farmhouse stir-fried pork and smoked meats are representative.",
    "flavors": ["fresh chile (xiānlàjiāo, 鲜辣椒)", "chopped salted chile (duòjiāo, 剁椒)", "dried chile (gānlàjiāo, 干辣椒)", "garlic (suàn, 蒜)", "ginger (jiāng, 姜)", "scallion (cōng, 葱)", "fermented black beans (dòuchǐ, 豆豉)", "rice vinegar (mǐcù, 米醋)", "soy sauce (jiàngyóu, 酱油)", "pickled vegetables (suāncài, 酸菜)"],
    "sweet_only": [],
    "signature_ingredients": ["duojiao chopped salted chiles — substitute: chopped Fresno or red jalapeño fermented or salted briefly", "Hunan smoked pork (làròu, 腊肉) — substitute: slab bacon, smokier and saltier", "dried long beans — substitute: fresh green beans, different flavor"],
    "pantry_assumed": ["fresh or preserved chiles", "garlic", "soy sauce", "pickles or preserved vegetables in many homes"],
    "techniques": ["stir-frying", "steaming with chopped chile", "smoking and curing", "braising", "pickling"],
    "shortcuts": ["Jarred chopped salted chile: use 20-30 g per 500 g main ingredient; often contributes about 1.5-3 g salt, so reduce added salt accordingly.", "Commercial black-bean chile sauce can replace douchi plus chile in quick dishes; 15 g often contributes about 1-2 g salt."],
    "allergen_notes": ["Soy sauce and many douchi sauces contain soy and wheat.", "Some chile-bean sauces contain soy or wheat.", "Sesame may appear in commercial sauces but is not mandatory."],
    "pitfalls": ["Do not automatically add Sichuan pepper; Hunan chile heat is usually not defined by málà.", "Do not make every Hunan dish extremely hot.", "Preserved, smoked and sour flavors are as important as fresh chile."],
    "sources": ["Fuchsia Dunlop, Revolutionary Chinese Cookbook: Recipes from Hunan Province, 2007", "https://www.fuchsiadunlop.com/books/revolutionary-chinese-cookbook", "https://en.chinaculture.org/2017-04/01/content_980114.htm"]
  },
  {
    "id": "cantonese",
    "label": "Cantonese",
    "subtitle": "Freshness, seafood, gentle seasoning",
    "about": "Cantonese cooking centers on Guangzhou, the Pearl River Delta and related Yue-speaking areas of Guangdong. Dense trade networks, subtropical agriculture and coastal seafood shaped a cuisine that often favors freshness and technical precision; steamed whole fish, white-cut chicken, char siu and dim sum are representative.",
    "flavors": ["ginger (goeng1, 薑)", "scallion (cung1, 蔥)", "garlic (syun3, 蒜)", "light soy sauce (saang1 cau1, 生抽)", "oyster sauce (hou4 jau4, 蠔油)", "fermented black beans (dau6 si6, 豆豉)", "sesame oil (zi1 maa4 jau4, 芝麻油)", "white pepper (baak6 wu4 ziu1, 白胡椒)", "rice wine (mai5 zau2, 米酒)", "dried tangerine peel (can4 pei4, 陳皮)"],
    "sweet_only": [],
    "signature_ingredients": ["dried shrimp (haa1 mai5, 蝦米) — substitute: none for exact flavor; omit for shellfish-free", "dried scallop (gon1 bui3, 乾貝) — substitute: dried shiitake for umami, not seafood flavor", "Chinese preserved sausage (laap6 coeng2, 臘腸) — substitute: mild sweet sausage, imperfect", "fresh whole fish — substitute: supermarket sea bass, trout or snapper"],
    "pantry_assumed": ["light soy sauce", "ginger", "scallions", "neutral oil"],
    "techniques": ["steaming", "stir-frying", "roasting and barbecue", "blanching/poaching", "braising"],
    "shortcuts": ["Prepared oyster sauce: 15-20 g seasons roughly 500 g food; commonly contributes around 1.5-2.5 g salt equivalent, label-dependent.", "Char siu sauce: 30-40 g per 500 g pork is a practical shortcut; commonly contributes roughly 2-4 g salt plus substantial sugar."],
    "allergen_notes": ["Oyster sauce contains shellfish unless vegetarian.", "Soy sauce usually contains soy and often wheat.", "Sesame oil contains sesame.", "XO sauce commonly contains dried scallop and shrimp and may contain soy.", "Dim sum wrappers and buns commonly contain wheat; some contain egg."],
    "pitfalls": ["Do not equate light seasoning with bland food.", "Do not add oyster sauce to every dish.", "Do not require wok hei in steamed or poached foods.", "Do not treat all Guangdong cooking as one undifferentiated Cantonese style."],
    "sources": ["Grace Young, The Breath of a Wok, 2004", "https://en.chinaculture.org/a/202602/26/WS699fa737a310d6866eb3a56b_3.html", "https://en.chinaculture.org/2018-03/24/content_1174194.htm", "https://www.si.edu/es/object/discovering-chinese-heritage-part-2-food%3Aposts_d0a0bfa4402bda7d876d478db0cfcd6a"]
  },
  {
    "id": "shandong",
    "label": "Shandong",
    "subtitle": "Scallion, seafood, powerful broths",
    "about": "Shandong projects into the Yellow Sea and Bohai Sea in northern China, with the lower Yellow River crossing the province. Lu cuisine is an old and influential northern tradition known for seafood, scallion, broths and exacting heat control; braised sea cucumber with scallion, sweet-and-sour carp, Dezhou braised chicken and quick-fried organ or seafood dishes are representative.",
    "flavors": ["scallion (cōng, 葱)", "ginger (jiāng, 姜)", "garlic (suàn, 蒜)", "soy sauce (jiàngyóu, 酱油)", "grain vinegar (cù, 醋)", "rice or grain wine (liàojiǔ, 料酒)", "sesame oil (zhīmayóu, 芝麻油)", "white pepper (báihújiāo, 白胡椒)", "star anise (bājiǎo, 八角)", "scallion oil (cōngyóu, 葱油)"],
    "sweet_only": [],
    "signature_ingredients": ["dried sea cucumber (hǎishēn, 海参) — substitute: king oyster mushroom for texture only", "yellow croaker (huángyú, 黄鱼) — substitute: sea bass or cod", "large Shandong scallion (Dàcōng, 大葱) — substitute: large leek plus scallion"],
    "pantry_assumed": ["scallions", "vinegar", "soy sauce", "stock ingredients"],
    "techniques": ["bao-style very rapid high-heat frying", "braising", "clear-stock and milky-stock making", "deep-frying", "quick stir-frying"],
    "shortcuts": ["Prepared chicken stock can replace long-made clear stock when necessary; choose unsalted and add salt separately.", "Five-spice is dish-specific, not a default; 2 g per 500 g braise, normally 0 g salt."],
    "allergen_notes": ["Soy sauce contains soy and often wheat.", "Seafood-heavy recipes may contain fish or shellfish.", "Oyster sauce occasionally appears and contains shellfish.", "Sesame oil contains sesame."],
    "pitfalls": ["Do not use wood ear as the defining Shandong ingredient.", "Do not turn all dishes sweet-and-sour.", "Do not describe 'oldest Chinese cuisine' as an uncontested fact."],
    "sources": ["https://en.chinaculture.org/chineseway/2013-04/17/content_455945.htm", "https://en.chinaculture.org/chineseway/2014-10/17/content_569364.htm", "Fuchsia Dunlop, Invitation to a Banquet: The Story of Chinese Food, 2023"]
  },
  {
    "id": "jiangsu",
    "label": "Jiangsu",
    "subtitle": "River fish, knife work, balance",
    "about": "Jiangsu stretches from the lower Yangtze and Grand Canal to lakes and the Yellow Sea; major culinary centers include Huai'an, Yangzhou, Nanjing, Suzhou and Wuxi. Huaiyang prestige cooking is especially known for seasonality and knife work, while southern Jiangsu can run sweeter; lion's-head meatballs, Yangzhou fried rice, Wensi tofu and squirrel-shaped mandarin fish are representative.",
    "flavors": ["ginger (jiāng, 姜)", "scallion (cōng, 葱)", "Shaoxing-style rice wine (huángjiǔ, 黄酒)", "light soy sauce (shēngchōu, 生抽)", "dark soy sauce (lǎochōu, 老抽)", "Zhenjiang black vinegar (Zhènjiāng xiāngcù, 镇江香醋)", "sugar (táng, 糖)", "sesame oil (zhīmayóu, 芝麻油)", "white pepper (báihújiāo, 白胡椒)"],
    "sweet_only": ["osmanthus sugar/syrup (guìhuā táng, 桂花糖) — mainly sweets, sweet soups and fragrant preparations"],
    "signature_ingredients": ["Zhenjiang black vinegar — substitute: rice vinegar plus a little balsamic", "water bamboo (jiāobái, 茭白) — substitute: asparagus hearts or bamboo shoots, imperfect", "freshwater crab — substitute: blue crab or Dungeness", "dried bamboo shoot (gānsǔn, 干笋) — substitute: canned bamboo shoot, milder"],
    "pantry_assumed": ["rice wine", "soy sauce", "sugar", "vinegar"],
    "techniques": ["fine knife work", "slow braising", "steaming", "stock making", "gentle simmering"],
    "shortcuts": ["Bottled Zhenjiang vinegar needs no blend; 10-15 g adds acidity with negligible salt in most brands.", "Commercial braising sauce can replace soy plus sugar in emergency; 30 g may contribute roughly 2-4 g salt, so check label."],
    "allergen_notes": ["Soy sauce usually contains soy and wheat.", "Seafood dishes may contain fish or shellfish.", "Sesame oil contains sesame.", "Some fermented tofu products contain soy and wheat."],
    "pitfalls": ["Do not equate all Jiangsu food with Huaiyang.", "Do not make every dish sweet.", "Do not automatically add red fermented tofu.", "Precision of texture and cutting is often more characteristic than aggressive seasoning."],
    "sources": ["Fuchsia Dunlop, Land of Fish and Rice, 2016", "https://en.chinaculture.org/2018-01/01/content_1129489.htm", "https://en.chinaculture.org/library/2008-01/30/content_29524.htm", "https://en.chinaculture.org/a/202604/13/WS69dc9479a310d6866eb43184_1.html"]
  },
  {
    "id": "zhejiang",
    "label": "Zhejiang",
    "subtitle": "Fresh, wine-fragrant, gently sweet",
    "about": "Zhejiang lies on China's east coast south of Shanghai, with Hangzhou and West Lake inland from the coast, Shaoxing amid waterways and Ningbo facing the sea. Its major subtraditions emphasize fresh seasonal ingredients, seafood, rice wine and restrained sweet-sour seasoning; West Lake fish in vinegar, Dongpo pork, Longjing shrimp and Ningbo-style seafood are representative.",
    "flavors": ["Shaoxing wine (Shàoxīng jiǔ, 绍兴酒)", "Zhejiang rice vinegar (mǐcù, 米醋)", "soy sauce (jiàngyóu, 酱油)", "ginger (jiāng, 姜)", "scallion (cōng, 葱)", "sugar (táng, 糖)", "sesame oil (zhīmayóu, 芝麻油)", "Longjing tea (Lóngjǐng chá, 龙井茶) — dish-specific", "fermented rice lees (jiǔzāo, 酒糟)"],
    "sweet_only": ["osmanthus (guìhuā, 桂花) — common in sweets and fragrant syrups"],
    "signature_ingredients": ["Shaoxing wine — substitute: dry sherry", "Longjing green tea — substitute: another delicate Chinese green tea", "freshwater fish — substitute: trout or bass", "fermented rice lees — substitute: sake kasu, imperfect"],
    "pantry_assumed": ["rice wine", "soy sauce", "vinegar", "sugar"],
    "techniques": ["braising", "steaming", "quick stir-frying", "wine-marinating/drunken preparations", "gentle simmering"],
    "shortcuts": ["Shaoxing cooking wine: 15-30 g per 500 g food; salted cooking wines may add 0.5-1.5 g salt, so check label.", "Premixed sweet-sour sauce is a poor default; if used, 25 g generally replaces roughly 10 g vinegar plus 10 g sugar and may add 1-2 g salt."],
    "allergen_notes": ["Soy sauce commonly contains soy and wheat.", "Seafood recipes may contain fish or shellfish.", "Sesame oil contains sesame.", "Some commercial cooking wines contain wheat-derived additives or added salt; check label."],
    "pitfalls": ["Do not make Zhejiang food generically sugary.", "Do not treat Longjing tea as an everyday seasoning.", "Do not collapse Zhejiang into Shanghai or Jiangsu cooking."],
    "sources": ["https://en.chinaculture.org/a/202505/08/WS681c47c7a310a04af22be1e7_4.html", "Fuchsia Dunlop, Land of Fish and Rice, 2016", "Fuchsia Dunlop, Invitation to a Banquet: The Story of Chinese Food, 2023"]
  },
  {
    "id": "fujian",
    "label": "Fujian",
    "subtitle": "Seafood, broths, fermented savor",
    "about": "Fujian faces the Taiwan Strait on China's mountainous southeast coast and historically connected China to maritime Southeast Asia. Coastal seafood, mountain produce, soups, red-fermented rice and diaspora networks shape its varied Fuzhou, southern Fujian and western traditions; Buddha Jumps Over the Wall, fish balls, oyster omelet and red-wine-lees dishes are representative.",
    "flavors": ["red rice wine lees (hóngzāo, 红糟)", "fish sauce (yúlù, 鱼露)", "rice wine (mǐjiǔ, 米酒)", "ginger (jiāng, 姜)", "scallion (cōng, 葱)", "garlic (suàn, 蒜)", "soy sauce (jiàngyóu, 酱油)", "rice vinegar (mǐcù, 米醋)", "white pepper (báihújiāo, 白胡椒)", "dried seafood seasoning such as dried shrimp (xiāmǐ, 虾米)"],
    "sweet_only": [],
    "signature_ingredients": ["red rice wine lees — substitute: sake kasu plus red yeast rice only if available; otherwise none", "dried scallop — substitute: dried shiitake for umami only", "fish balls with springy texture — substitute: supermarket fish balls", "dried razor clam or other dried seafood — substitute: dried shrimp if shellfish allowed"],
    "pantry_assumed": ["rice wine", "ginger", "dried seafood in many coastal kitchens"],
    "techniques": ["soup and stock making", "red-lees braising", "steaming", "quick stir-frying", "seafood drying/preservation"],
    "shortcuts": ["Bottled red-fermented rice cooking sauce can replace homemade hongzao; 20 g may contribute roughly 1-2 g salt depending on brand.", "Commercial fish sauce: 10 g may contribute roughly 1.5-2.5 g salt; reduce added salt aggressively."],
    "allergen_notes": ["Fish sauce contains fish.", "Dried shrimp/scallop and oyster preparations contain shellfish.", "Soy sauce contains soy and often wheat.", "Some fish balls contain egg, wheat or soy binders."],
    "pitfalls": ["Do not reduce Fujian cuisine to oyster sauce or generic seafood stir-fries.", "Do not assume every Fujian dish is sweet.", "Distinguish coastal Fujian, Fuzhou and Hokkien/diaspora traditions when possible."],
    "sources": ["https://en.chinaculture.org/a/202402/01/WS65bb0126a3104ef22be1e7_1.html", "https://guide.michelin.com/en/article/travel/the-must-eat-dishes-for-travelling-thais-destination-5-china", "Fuchsia Dunlop, Invitation to a Banquet: The Story of Chinese Food, 2023"]
  },
  {
    "id": "anhui",
    "label": "Anhui",
    "subtitle": "Mountain foods, braises, wild herbs",
    "about": "Anhui lies inland west of the lower Yangtze, with the Huangshan mountains and historic Huizhou in its south. Hui cuisine grew from mountain ingredients, preserved foods, bamboo shoots, mushrooms and careful braising; stinky mandarin fish, Li Hongzhang mixed stew, braised soft-shell turtle and bamboo-shoot dishes are representative.",
    "flavors": ["ginger (jiāng, 姜)", "scallion (cōng, 葱)", "garlic (suàn, 蒜)", "soy sauce (jiàngyóu, 酱油)", "rice wine (mǐjiǔ, 米酒)", "rock sugar (bīngtáng, 冰糖)", "star anise (bājiǎo, 八角)", "cassia (guìpí, 桂皮)", "dried chile (gānlàjiāo, 干辣椒) — regional", "sesame oil (zhīmayóu, 芝麻油)"],
    "sweet_only": [],
    "signature_ingredients": ["fresh or dried bamboo shoots (sǔn, 笋) — substitute: canned bamboo shoots", "wild or dried mushrooms (xiānggū, 香菇) — substitute: shiitake", "fermented/stinky mandarin fish (chòu guìyú, 臭鳜鱼) — substitute: none", "soft-shell turtle — substitute: chicken thighs for braising structure only"],
    "pantry_assumed": ["soy sauce", "rice wine", "dried mushrooms or preserved ingredients in many traditional kitchens"],
    "techniques": ["red-braising", "slow stewing", "steaming", "preserving/fermenting", "gentle frying"],
    "shortcuts": ["Chinese braising spice packets can replace whole star anise/cassia/clove; use 3-5 g spices per 1 kg food, usually 0 g salt unless packet is seasoned.", "Prepared soy-braising sauce: 30 g may contribute 3-5 g salt equivalent; use label sodium."],
    "allergen_notes": ["Soy sauce contains soy and often wheat.", "Some fermented fish preparations contain fish by definition.", "Sesame oil contains sesame."],
    "pitfalls": ["Do not confuse Anhui with Cantonese or Jiangsu merely because braising is common.", "Do not make all Hui food heavily spiced; ingredient preservation and mountain produce are key.", "Wild-game stereotypes should not be imposed on modern home cooking."],
    "sources": ["https://en.chinaculture.org/library/2008-01/30/content_29404.htm", "https://en.chinaculture.org/chineseway/2013-04/17/content_455945.htm", "Fuchsia Dunlop, Invitation to a Banquet: The Story of Chinese Food, 2023"]
  },
  {
    "id": "china_any",
    "label": "China Any",
    "subtitle": "International Chinese restaurant image",
    "about": "Outside China, 'Chinese food' often means an export repertoire shaped first by Cantonese-speaking migrants and later by Sichuan, Hunan, Taiwanese and other influences. Fried rice, dumplings, chow mein, sweet-and-sour dishes and stir-fries are recognizable international examples, but this is an export category rather than a faithful national summary.",
    "flavors": ["soy sauce (jiàngyóu, 酱油)", "ginger (jiāng, 姜)", "garlic (suàn, 蒜)", "scallion (cōng, 葱)", "sesame oil (zhīmayóu, 芝麻油)", "rice vinegar (mǐcù, 米醋)", "oyster sauce (háoyóu, 蚝油)", "white pepper (báihújiāo, 白胡椒)", "five-spice (wǔxiāngfěn, 五香粉)", "chile sauce (làjiāojiàng, 辣椒酱)"],
    "sweet_only": [],
    "signature_ingredients": ["water chestnuts — substitute: jicama", "bamboo shoots — substitute: canned bamboo shoots", "wood ear — substitute: mushrooms for texture only", "Chinese egg noodles — substitute: spaghetti in emergency"],
    "pantry_assumed": ["soy sauce", "garlic", "ginger", "neutral oil"],
    "techniques": ["stir-frying", "deep-frying", "steaming dumplings", "braising", "fried-rice cooking"],
    "shortcuts": ["Bottled stir-fry sauce: 30 g per 500 g ingredients; typically contributes about 2-4 g salt plus sugar.", "Five-spice: 2 g per 500 g where appropriate; generally 0 g salt."],
    "allergen_notes": ["Soy sauce and hoisin contain soy and commonly wheat.", "Oyster sauce contains shellfish.", "Sesame oil contains sesame.", "Egg noodles contain wheat and often egg.", "Peanuts appear in some American-Chinese and Sichuan-derived dishes."],
    "pitfalls": ["Label this as an international/export version, not representative Chinese home cooking.", "Do not put sesame oil, five-spice or sweet sauce into every dish.", "American chop suey and similar dishes are diaspora developments, not proof of a mainland regional tradition."],
    "sources": ["https://www.si.edu/es/object/discovering-chinese-heritage-part-2-food%3Aposts_d0a0bfa4402bda7d876d478db0cfcd6a", "https://americanhistory.si.edu/explore/topics/food/cooking-up-history", "Haiming Liu, From Canton Restaurant to Panda Express, 2015"]
  },
  {
    "id": "japan",
    "label": "Japan",
    "subtitle": "Dashi, fermentation, seasonality",
    "about": "Japan stretches from snowy Hokkaido to subtropical Okinawa, so regional food varies greatly despite common foundations. Rice agriculture, fisheries, Buddhist foodways, fermentation and later continental and Western influences shaped the cuisine; sushi, miso soup, grilled fish and simmered vegetables are representative.",
    "flavors": ["soy sauce (shōyu, 醤油)", "dashi (dashi, だし)", "miso (miso, 味噌)", "mirin (mirin, みりん)", "sake (sake, 酒)", "rice vinegar (komezu, 米酢)", "ginger (shōga, 生姜)", "scallion (negi, 葱)", "sesame (goma, 胡麻)", "wasabi (wasabi, 山葵)", "sansho pepper (sanshō, 山椒)"],
    "sweet_only": ["kinako roasted soybean flour (kinako, きな粉) — strongly associated with sweets though sometimes savory", "kuromitsu black sugar syrup (kuromitsu, 黒蜜)"],
    "signature_ingredients": ["kombu (昆布) — substitute: none exact; dried mushrooms for vegetarian umami", "katsuobushi (鰹節) — substitute: instant dashi or dried shiitake for vegetarian version", "miso — substitute: none exact", "nori (海苔) — substitute: other toasted seaweed, imperfect"],
    "pantry_assumed": ["soy sauce", "rice", "dashi ingredients or instant dashi", "miso or another fermented seasoning in many homes"],
    "techniques": ["dashi making", "grilling", "simmering (nimono)", "steaming", "raw preparation where appropriate"],
    "shortcuts": ["Instant dashi granules: about 3-5 g per liter replaces scratch dashi; many products add roughly 1-3 g salt per liter, so check label.", "Mentsuyu concentrate: dilute according to label; 30 g concentrate may contribute roughly 2-4 g salt depending on strength."],
    "allergen_notes": ["Soy sauce and miso contain soy and often wheat.", "Dashi commonly contains fish from katsuobushi.", "Sesame appears in goma dressings.", "Tempura batter and noodles commonly contain wheat; tempura often contains egg."],
    "pitfalls": ["Do not add teriyaki sauce to unrelated dishes.", "Do not treat sushi as the dominant form of home cooking.", "Dashi can be fish-based, kombu-based, shiitake-based or mixed."],
    "sources": ["https://www.maff.go.jp/e/data/publish/attach/pdf/index-112.pdf", "https://www.maff.go.jp/e/policies/market/dento_syoku/bunrui/syouyu-miso.html", "Elizabeth Andoh, Washoku, 2005"]
  },
  {
    "id": "kanto",
    "label": "Kanto",
    "subtitle": "Dark soy, bonito, Edo",
    "about": "Kanto surrounds Tokyo on eastern Honshu and includes the historic city of Edo. Urban Edo food culture favored darker koikuchi soy sauce and bonito-rich stocks and developed famous street and restaurant foods; Edomae sushi, Edo tempura, soba and grilled eel are representative.",
    "flavors": ["koikuchi soy sauce (koikuchi shōyu, 濃口醤油)", "bonito dashi (katsuo dashi, 鰹だし)", "mirin (mirin, みりん)", "sake (sake, 酒)", "rice vinegar (komezu, 米酢)", "wasabi (wasabi, 山葵)", "scallion (negi, 葱)", "ginger (shōga, 生姜)", "sansho (sanshō, 山椒)", "tsuyu (tsuyu, つゆ)"],
    "sweet_only": [],
    "signature_ingredients": ["katsuobushi — substitute: instant bonito dashi", "koikuchi soy sauce — substitute: standard Japanese soy sauce", "red vinegar for Edomae sushi (akazu, 赤酢) — substitute: rice vinegar plus a tiny amount brown sugar, imperfect"],
    "pantry_assumed": ["koikuchi-style soy sauce", "dashi ingredients", "mirin or sake"],
    "techniques": ["bonito-forward dashi making", "tempura frying", "sushi curing/marinating", "soba preparation", "grilling with tare"],
    "shortcuts": ["Mentsuyu: 30 g concentrate can replace soy/mirin/dashi base for noodles; often contributes 2-4 g salt.", "Instant bonito dashi: 3-5 g per liter; salt varies from near zero to several grams per liter."],
    "allergen_notes": ["Soy sauce and tsuyu contain soy and usually wheat.", "Dashi/tsuyu commonly contain fish.", "Soba noodles may contain wheat as binder.", "Tempura batter commonly contains wheat and sometimes egg."],
    "pitfalls": ["Do not claim soba originated as Edo fast food; soba predates Edo stall culture.", "Do not make red miso a mandatory Kanto marker.", "Dark color does not mean every Kanto dish should taste aggressively salty."],
    "sources": ["https://www.maff.go.jp/e/policies/market/k_ryouri/areastory/1272/index.html", "https://www.maff.go.jp/e/policies/market/k_ryouri/search_menu/6156/index.html", "https://www.japan.travel/en/sg/story/kanto-vs-kansai-battle-cuisines/"]
  },
  {
    "id": "kansai",
    "label": "Kansai",
    "subtitle": "Kombu, light soy, refinement",
    "about": "Kansai is western-central Japan around Osaka, Kyoto, Kobe and neighboring prefectures. Ancient court culture in Kyoto, merchant culture in Osaka and trade routes carrying kombu helped shape its food; Kyoto kaiseki, kitsune udon, Osaka okonomiyaki and takoyaki are representative.",
    "flavors": ["kombu dashi (konbu dashi, 昆布だし)", "usukuchi soy sauce (usukuchi shōyu, 淡口醤油)", "mirin (mirin, みりん)", "sake (sake, 酒)", "white miso (shiro miso, 白味噌) — especially Kyoto", "sansho (sanshō, 山椒)", "yuzu (yuzu, 柚子)", "scallion (negi, 葱)", "shichimi (shichimi tōgarashi, 七味唐辛子)", "katsuobushi (katsuobushi, 鰹節)"],
    "sweet_only": [],
    "signature_ingredients": ["kombu — substitute: none exact", "usukuchi soy sauce — substitute: koikuchi diluted slightly plus salt, color will differ", "Kyoto white miso — substitute: mild white miso"],
    "pantry_assumed": ["dashi ingredients", "soy sauce", "mirin or sake"],
    "techniques": ["kombu-forward dashi extraction", "gentle simmering", "griddling", "steaming", "kaiseki-style seasonal preparation"],
    "shortcuts": ["Shirodashi concentrate can replace kombu-dashi plus usukuchi; dilute by label and reduce salt because 30 g concentrate may supply roughly 3-5 g salt.", "Instant kombu dashi: 3-5 g per liter; salt varies by brand."],
    "allergen_notes": ["Usukuchi soy sauce contains soy and usually wheat.", "Combined dashi may contain bonito fish even when kombu-forward.", "Okonomiyaki/takoyaki contain wheat and commonly egg; takoyaki contains shellfish mollusk, though octopus is not one of the nine major U.S. allergens."],
    "pitfalls": ["Do not interpret 'light' soy as low-sodium.", "Do not make white miso universal across Kansai.", "Do not assume every Kansai stock is vegetarian kombu-only."],
    "sources": ["https://www.maff.go.jp/e/policies/market/k_ryouri/areastory/1443/index.html", "https://www.maff.go.jp/e/policies/market/dento_syoku/bunrui/syouyu-miso.html", "https://www.japan.travel/en/ca/cuisine/kansai/", "https://www.jstage.jst.go.jp/article/cookeryscience1995/37/1/37_21/_article/-char/en"]
  },
  {
    "id": "japan_any",
    "label": "Japan Any",
    "subtitle": "Sushi, ramen, teriyaki image",
    "about": "Internationally, Japanese food is commonly represented by sushi, ramen, tempura, teriyaki, miso soup and rice bowls. These are genuinely Japanese foods, but the export image underrepresents ordinary simmered dishes, grilled fish, pickles, regional foods and home-style vegetable cookery.",
    "flavors": ["soy sauce (shōyu, 醤油)", "dashi (dashi, だし)", "miso (miso, 味噌)", "mirin (mirin, みりん)", "rice vinegar (komezu, 米酢)", "sake (sake, 酒)", "ginger (shōga, 生姜)", "wasabi (wasabi, 山葵)", "sesame (goma, 胡麻)", "scallion (negi, 葱)"],
    "sweet_only": ["matcha (matcha, 抹茶) — internationally stereotyped as dessert flavor though also used as tea", "kuromitsu (kuromitsu, 黒蜜)"],
    "signature_ingredients": ["nori — substitute: toasted seaweed", "miso — substitute: none exact", "short-grain Japanese rice — substitute: California medium-grain", "katsuobushi — substitute: instant dashi"],
    "pantry_assumed": ["soy sauce", "rice", "miso or dashi ingredients in many households"],
    "techniques": ["sushi rice preparation", "tempura frying", "broth making", "grilling", "simmering"],
    "shortcuts": ["Bottled teriyaki sauce: 30 g per 500 g food; often contributes 2-4 g salt and significant sugar.", "Instant dashi: 3-5 g per liter; account for label sodium."],
    "allergen_notes": ["Soy sauce and miso contain soy and often wheat.", "Dashi often contains fish.", "Tempura usually contains wheat and may contain egg.", "Sesame dressings contain sesame.", "Ramen noodles contain wheat and sometimes egg."],
    "pitfalls": ["Treat this as an international stereotype/export view, not Japanese home cooking in full.", "Do not make everything sweet teriyaki.", "Do not use sushi ingredients to signal authenticity in unrelated dishes."],
    "sources": ["https://www.maff.go.jp/e/data/publish/attach/pdf/index-112.pdf", "Elizabeth Andoh, Washoku, 2005", "Naomi Moriyama and William Doyle, Japanese Women Don't Get Old or Fat, 2005"]
  },
  {
    "id": "india",
    "label": "India",
    "subtitle": "Spices, pulses, regional diversity",
    "about": "India stretches from the Himalayas and Indo-Gangetic plain to western deserts, tropical coasts and the southern peninsula. Religion, caste, trade, migration, Islamic courts and Portuguese and British colonialism all shaped highly regional cuisines; dal, vegetable sabzi, flatbreads and rice dishes appear widely but in radically different forms.",
    "flavors": ["cumin (jīrā/jeera, जीरा)", "coriander (dhaniyā/dhania, धनिया)", "turmeric (haldī/haldi, हल्दी)", "chile (mirch, मिर्च)", "ginger (adrak, अदरक)", "garlic (lahsun, लहसुन)", "mustard seed (rāī, राई)", "fenugreek (methī, मेथी)", "asafoetida (hīng, हींग)", "cardamom (ilāychī, इलायची)", "clove (lauṅg, लौंग)", "black pepper (kālī mirch, काली मिर्च)"],
    "sweet_only": ["rose water (gulāb jal, गुलाब जल) — mainly sweets/drinks though occasional savory use", "kewra water (kevṛā, केवड़ा) — mainly sweets and celebratory rice dishes"],
    "signature_ingredients": ["asafoetida — substitute: tiny amount garlic/onion where religious rules permit", "fresh curry leaves — substitute: none exact", "Indian dried chiles — substitute: cayenne plus paprika depending heat", "ghee — substitute: clarified butter or neutral oil"],
    "pantry_assumed": ["regional staple grain", "pulses", "several whole and ground spices"],
    "techniques": ["tadka/tempering", "slow simmering", "griddling breads", "pressure cooking", "dry-roasting and grinding spices"],
    "shortcuts": ["Garam masala: 2-5 g per 500 g dish; usually 0 g salt.", "Commercial curry powder: 5-10 g per 500 g; usually 0-1 g salt depending brand, but it is not a universal Indian household blend."],
    "allergen_notes": ["Ghee, butter, paneer and yogurt contain milk.", "Some sweets contain tree nuts.", "Peanuts are common in parts of western and southern India.", "Wheat is common in breads.", "Sesame appears in regional chutneys and sweets.", "Commercial hing often uses wheat flour as a carrier."],
    "pitfalls": ["Do not call every spiced sauce 'curry'.", "Do not assume every dish contains garam masala.", "Do not impose Punjabi restaurant ingredients nationally.", "Vegetarian does not mean vegan because dairy is common in many regions."],
    "sources": ["Colleen Taylor Sen, Feasts and Fasts: A History of Food in India, 2015", "https://doi.org/10.1186/s42779-022-00129-4", "https://www.indiaculture.gov.in/sites/default/files/festival_laopdr/pre_events/Festival%20of%20India%20Brochure-FINAL.pdf", "https://www.pib.gov.in/newsite/PrintRelease.aspx?lang=2&reg=48&relid=159991"]
  },
  {
    "id": "north_india",
    "label": "North India",
    "subtitle": "Wheat, dairy, warm spices",
    "about": "This broad app category covers the Indo-Gangetic plain, Punjab, Delhi, Rajasthan, Kashmir and Himalayan regions, whose cuisines differ substantially. Persianate and Mughal court traditions strongly shaped some urban northern cooking while farming and pastoral traditions shaped others; roti with dal or vegetables, kebabs, biryani and Punjabi-style tandoori foods are representative but not universal.",
    "flavors": ["cumin (jeera, जीरा)", "coriander (dhania, धनिया)", "turmeric (haldi, हल्दी)", "red chile (lal mirch, लाल मिर्च)", "garam masala (garam masala, गरम मसाला)", "green cardamom (chhoti elaichi, छोटी इलायची)", "black cardamom (badi elaichi, बड़ी इलायची)", "clove (laung, लौंग)", "fenugreek (methi, मेथी)", "asafoetida (hing, हींग)", "dried fenugreek leaf (kasuri methi, कसूरी मेथी)"],
    "sweet_only": ["rose water (gulab jal, गुलाब जल) — mainly sweets/drinks but also biryani or celebratory dishes", "saffron (kesar, केसर) — heavily associated with sweets but also savory rice dishes"],
    "signature_ingredients": ["kasuri methi — substitute: tiny amount dried fenugreek seed is not equivalent; best substitute none", "paneer — substitute: firm tofu for texture, not flavor", "black cardamom — substitute: green cardamom plus tiny smoked note, imperfect", "ghee — substitute: clarified butter"],
    "pantry_assumed": ["atta or another staple grain in many homes", "lentils/pulses", "cumin and coriander"],
    "techniques": ["tadka", "tandoor cooking in relevant regions", "dum steaming", "griddling flatbreads", "slow braising"],
    "shortcuts": ["Garam masala: 2-5 g per 500 g, generally 0 g salt.", "Tandoori masala: 10-15 g per 500 g protein; commercial mixes may add 1-3 g salt, so check label.", "Jarred tikka masala sauce: 150 g for roughly 500 g protein/vegetables can contribute 3-6 g salt plus dairy depending brand."],
    "allergen_notes": ["Milk is common in ghee, yogurt, cream and paneer.", "Wheat is common in roti, naan and paratha.", "Tree nuts may thicken Mughlai gravies.", "Commercial hing may contain wheat.", "Sesame and peanuts occur regionally but are not universal."],
    "pitfalls": ["Do not make naan the everyday bread everywhere.", "Do not put cream and paneer into every northern dish.", "Do not treat Punjabi-Mughlai restaurant food as all North Indian food.", "Black mustard seed is not a mandatory northern signature."],
    "sources": ["Colleen Taylor Sen, Feasts and Fasts: A History of Food in India, 2015", "https://www.eoiukraine.gov.in/indian-cuisine.php", "https://doi.org/10.1186/s42779-022-00129-4"]
  },
  {
    "id": "south_india",
    "label": "South India",
    "subtitle": "Rice, tamarind, curry leaves",
    "about": "This broad category covers Tamil Nadu, Kerala, Karnataka, Andhra Pradesh and Telangana, from tropical coasts to dry interior plateaus. Dravidian food traditions, temple cultures, maritime trade, Muslim communities and later colonial contacts produced enormous variation; dosa, idli, sambar, rasam and regional rice meals are familiar representatives rather than universal defaults.",
    "flavors": ["mustard seed (kadugu, கடுகு / āvalu, ఆవాలు)", "curry leaf (karuvēppilai, கருவேப்பிலை / karivepaku, కరివేపాకు)", "tamarind (puli, புளி / chintapandu, చింతపండు)", "dried red chile (vara milagai, வரமிளகாய் / endu mirapa, ఎండు మిరప)", "fenugreek (vendhayam, வெந்தயம் / menthulu, మెంతులు)", "asafoetida (perungayam, பெருங்காயம் / inguva, ఇంగువ)", "black pepper (milagu, மிளகு)", "coriander seed (malli, மல்லி)", "turmeric (manjal, மஞ்சள்)", "cumin (seeragam, சீரகம் / jeelakarra, జీలకర్ర)", "fresh ginger (inji, இஞ்சி)"],
    "sweet_only": ["cardamom (elakkai, ஏலக்காய்) — heavily used in sweets but also some savory dishes"],
    "signature_ingredients": ["fresh curry leaves — substitute: none exact", "tamarind pulp — substitute: lime plus a little brown sugar, imperfect", "urad dal — substitute: split mung for some batters, very different", "fresh coconut — substitute: unsweetened frozen coconut"],
    "pantry_assumed": ["rice or another regional grain", "pulses", "mustard seed/cumin and dried chile depending region", "tamarind in many but not all kitchens"],
    "techniques": ["tempering/tadka", "fermenting rice-lentil batters", "steaming", "griddling", "pressure-cooking pulses"],
    "shortcuts": ["Sambar powder: 10-15 g per 1 liter; traditionally spice-based and about 0 g salt, but check commercial labels.", "Rasam powder: 5-10 g per liter; normally about 0 g salt.", "Commercial coconut chutney powder varies; 15 g may contribute 0.5-2 g salt."],
    "allergen_notes": ["Coconut is a tree nut under U.S. labeling rules although clinical allergy patterns differ from most tree nuts.", "Peanuts are common in some Andhra, Telangana and Karnataka dishes.", "Sesame appears in chutneys and spice powders.", "Commercial hing may contain wheat.", "Yogurt/ghee introduce milk."],
    "pitfalls": ["Do not assume all South Indian dishes contain coconut.", "Do not call the region uniformly hotter than the north.", "Urad dal is a pulse, not merely a seasoning.", "Tamil 'sukku' means dried ginger, not dried chile."],
    "sources": ["https://www.incredibleindia.gov.in/en/tamil-nadu/chennai/a-foodies-guide-to-trying-local", "https://www.eoiukraine.gov.in/indian-cuisine.php", "Colleen Taylor Sen, Feasts and Fasts: A History of Food in India, 2015"]
  },
  {
    "id": "india_any",
    "label": "India Any",
    "subtitle": "Restaurant curry, naan, tandoor",
    "about": "Internationally recognized Indian food is disproportionately shaped by Punjabi, Delhi and Mughlai restaurant traditions plus globally popular biryanis and southern dishes such as dosa. Butter chicken, chicken tikka masala, naan, paneer dishes and dal are familiar export markers, but this image is far narrower and creamier than everyday Indian cooking.",
    "flavors": ["cumin (jeera)", "coriander (dhania)", "turmeric (haldi)", "red chile (lal mirch)", "garam masala", "ginger (adrak)", "garlic (lahsun)", "green cardamom (elaichi)", "clove (laung)", "fenugreek (methi)", "kasuri methi"],
    "sweet_only": ["rose water (gulab jal)", "cardamom (elaichi) — strongly associated with sweets but not dessert-only"],
    "signature_ingredients": ["paneer — substitute: firm tofu", "ghee — substitute: clarified butter", "kasuri methi — substitute: none exact", "basmati rice — substitute: another long-grain aromatic rice"],
    "pantry_assumed": ["ground spices", "rice or flour", "pulses"],
    "techniques": ["tadka", "tandoor-style roasting", "sauce reduction", "dum cooking", "flatbread cooking"],
    "shortcuts": ["Garam masala: 2-5 g per 500 g; 0 g salt in most blends.", "Tikka/tandoori seasoning: 10-15 g per 500 g; commercial mixes may supply 1-3 g salt.", "Jarred curry simmer sauce: 150-200 g per 500 g main ingredient; commonly supplies 4-8 g salt depending brand."],
    "allergen_notes": ["Milk is common in cream, butter, yogurt, paneer and ghee.", "Tree nuts may thicken restaurant gravies.", "Wheat is present in naan and many breads.", "Commercial spice blends may contain wheat or sesame depending manufacturer."],
    "pitfalls": ["Treat this as an export/restaurant cliché, not a national baseline.", "Do not assume all Indian sauces contain cream or tomato.", "Curry powder is not a universal Indian household seasoning."],
    "sources": ["Colleen Taylor Sen, Feasts and Fasts: A History of Food in India, 2015", "https://www.eoiukraine.gov.in/indian-cuisine.php", "https://doi.org/10.1186/s42779-022-00129-4"]
  },
  {
    "id": "korean",
    "label": "Korean",
    "subtitle": "Jang, garlic, chile, fermentation",
    "about": "Korean cuisine developed on the Korean Peninsula, with cold winters encouraging extensive preservation and fermentation and strong regional differences between coasts, mountains and plains. Rice, soups, banchan and fermented jang form major foundations; kimchi jjigae, bibimbap, bulgogi and doenjang jjigae are representative.",
    "flavors": ["red pepper flakes (gochutgaru/gochugaru, 고춧가루)", "red pepper paste (gochujang, 고추장)", "soybean paste (doenjang, 된장)", "soy sauce (ganjang, 간장)", "garlic (maneul, 마늘)", "ginger (saenggang, 생강)", "scallion (pa, 파)", "sesame oil (chamgireum, 참기름)", "sesame seed (chamkkae, 참깨)", "perilla oil (deulgireum, 들기름)", "fermented seafood (jeotgal, 젓갈)"],
    "sweet_only": [],
    "signature_ingredients": ["perilla leaves (kkaennip, 깻잎) — substitute: shiso, different flavor", "Korean radish (mu, 무) — substitute: daikon", "rice cakes (tteok, 떡) — substitute: none exact", "dried anchovies (myeolchi, 멸치) — substitute: bonito flakes for stock, different"],
    "pantry_assumed": ["kimchi in many households", "ganjang", "doenjang", "garlic", "sesame oil or seeds"],
    "techniques": ["fermentation", "simmering soups and jjigae", "grilling", "braising (jorim)", "seasoning/blanching vegetables as namul"],
    "shortcuts": ["Gochujang: 20 g contributes roughly 1-2.5 g salt plus sugar depending brand.", "Store-bought ssamjang: 20 g commonly contributes 1.5-3 g salt.", "Soup soy sauce: 10 g may contribute around 1.5-2 g salt."],
    "allergen_notes": ["Gochujang, doenjang and ganjang contain soy and frequently wheat.", "Sesame oil and seeds contain sesame.", "Jeotgal contains fish or shellfish depending type.", "Kimchi may contain fish sauce or salted shrimp.", "Jeon often contains wheat and egg."],
    "pitfalls": ["Do not make everything red, sweet and gochujang-heavy.", "Not all kimchi contains seafood or chile.", "Korean food is much broader than barbecue and jjigae.", "Use standard spelling 고춧가루, not 고추가루."],
    "sources": ["https://www.koreanculture.org/food", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?menuSn=903&vcontsId=229195", "https://english.visitkorea.or.kr/svc/contents/infoHtmlView.do?menuSn=254&vcontsId=172556", "https://krdict.korean.go.kr/eng/dicSearch/SearchView?ParaWordNo=25597&nation=eng"]
  },
  {
    "id": "thai",
    "label": "Thai",
    "subtitle": "Herbs, fish sauce, curry pastes",
    "about": "Thailand runs from northern mountains through the Chao Phraya plain to a long southern peninsula, producing sharply different regional cuisines. Trade with China, India, maritime Southeast Asia and Europeans added techniques and ingredients to older Tai foodways; tom yum, green curry, som tam and pad thai are familiar representatives but come from different regional histories.",
    "flavors": ["fish sauce (nam pla, น้ำปลา)", "fresh chile (phrik, พริก)", "lemongrass (takhrai, ตะไคร้)", "galangal (kha, ข่า)", "makrut lime leaf (bai makrut, ใบมะกรูด)", "shallot (hom daeng, หอมแดง)", "garlic (krathiam, กระเทียม)", "coriander root (rak phak chi, รากผักชี)", "tamarind (makham, มะขาม)", "palm sugar (nam tan pip, น้ำตาลปี๊บ)", "shrimp paste (kapi, กะปิ)", "Thai basil (horapha, โหระพา)"],
    "sweet_only": ["pandan (bai toei, ใบเตย) — mainly sweets/drinks though occasional savory use"],
    "signature_ingredients": ["galangal — substitute: ginger plus lime zest, noticeably different", "makrut lime leaves — substitute: lime zest plus bay leaf, imperfect", "Thai basil — substitute: Italian basil plus mint, imperfect", "palm sugar — substitute: light brown sugar"],
    "pantry_assumed": ["fish sauce in many non-vegetarian kitchens", "chiles", "garlic", "shallots"],
    "techniques": ["pounding curry pastes", "stir-frying", "grilling", "simmering curries/soups", "mortar-pounded salads"],
    "shortcuts": ["Commercial curry paste: 20-30 g per 400 ml coconut milk is typical; many brands contribute about 2-4 g salt and may contain shrimp.", "Fish sauce: 10 g commonly contributes about 2-2.5 g salt.", "Tom yum paste: 20 g per 500 ml liquid may add 2-4 g salt and often sugar."],
    "allergen_notes": ["Fish sauce contains fish.", "Shrimp paste contains shellfish.", "Many curry pastes contain shrimp paste.", "Peanuts are important in some dishes and garnishes but not universal.", "Soy sauce and oyster sauce introduce soy/wheat and shellfish respectively in Chinese-influenced dishes."],
    "pitfalls": ["Do not force sweet, sour, salty and spicy into every dish.", "Do not put coconut milk into all Thai curries or soups.", "Do not use peanut sauce as a generic Thai flavor.", "Northern, northeastern, central and southern cuisines differ substantially."],
    "sources": ["https://lima.thaiembassy.org/en/content/introduction-of-thai-food?cate=5d8467b415e39c31dc005b11", "David Thompson, Thai Food, 2002", "https://nutritioncenter.ctahr.hawaii.edu/wp-content/uploads/2022/07/Thai_pamphlet.pdf"]
  },
  {
    "id": "vietnamese",
    "label": "Vietnamese",
    "subtitle": "Fish sauce, herbs, rice",
    "about": "Vietnam stretches along the South China Sea from the Red River Delta around Hanoi through central mountains and coast to the Mekong Delta. Chinese rule and exchange, Cham and Khmer contacts, southward Vietnamese migration and French colonialism shaped distinct northern, central and southern cuisines; phở, bún chả, bánh xèo and cá kho are representative.",
    "flavors": ["fish sauce (nước mắm)", "scallion (hành lá)", "ginger (gừng)", "lemongrass (sả)", "garlic (tỏi)", "shallot (hành tím)", "lime (chanh)", "fresh chile (ớt)", "Vietnamese coriander (rau răm)", "Thai/Vietnamese basil (húng quế)", "mint (húng lủi)", "turmeric (nghệ)"],
    "sweet_only": ["pandan (lá dứa) — mainly sweets/drinks though occasional savory use"],
    "signature_ingredients": ["Vietnamese fish sauce — substitute: Thai fish sauce, flavor differs", "rice paper (bánh tráng) — substitute: supermarket rice wrappers", "rice vermicelli (bún) — substitute: Thai rice vermicelli", "rau răm — substitute: cilantro plus mint, imperfect"],
    "pantry_assumed": ["fish sauce in many non-vegetarian kitchens", "rice or rice noodles", "scallions and aromatics"],
    "techniques": ["clear-broth simmering", "grilling over charcoal", "stir-frying", "braising/caramel cooking", "table wrapping with herbs and rice paper"],
    "shortcuts": ["Fish sauce: 10 g commonly contributes roughly 2-2.5 g salt.", "Prepared phở spice packets usually contain star anise, cassia, clove, coriander and cardamom; use 5-10 g spices per 3-4 liters broth, normally 0 g salt unless seasoning mix.", "Bottled nuoc cham may contribute about 1-2 g salt per 30 g, brand-dependent."],
    "allergen_notes": ["Fish sauce contains fish.", "Shrimp paste and dried shrimp contain shellfish.", "Soy sauce introduces soy and often wheat.", "Peanuts appear in some noodle dishes and dipping sauces.", "Bánh mì contains wheat and may contain egg or milk depending bread and fillings."],
    "pitfalls": ["Do not put lime, chile and huge piles of herbs into every dish.", "Do not make all phở heavily spiced or sweet.", "Distinguish northern, central and southern flavor profiles when possible.", "French influence is important but does not explain the cuisine as a whole."],
    "sources": ["Andrea Nguyen, Into the Vietnamese Kitchen, 2006", "https://www.researchgate.net/publication/355187945_Contemporary_Vietnamese_Cuisine_In_Routledge_Handbook_of_Contemporary_Vietnam_2022", "https://www.researchgate.net/publication/305910163_Ethnic_Fermented_Foods_and_Beverages_of_Vietnam"]
  },
  {
    "id": "filipino",
    "label": "Filipino",
    "subtitle": "Vinegar, garlic, sour-savory depth",
    "about": "The Philippines is an archipelago of more than seven thousand islands between the South China Sea and Pacific, with major Luzon, Visayan and Mindanao traditions. Indigenous Austronesian foodways absorbed Chinese trade and migration, Spanish and Mexican colonial influences and later American influence; adobo, sinigang, pancit and kare-kare are representative.",
    "flavors": ["cane or coconut vinegar (sukà)", "soy sauce (toyò)", "fish sauce (patís)", "fermented shrimp or fish paste (bagoóng)", "garlic (bawang)", "onion (sibuyas)", "ginger (luya)", "calamansi (kalamansî)", "black pepper (pamintang itim)", "annatto (atsuete)", "bay leaf (dahon ng laurel)"],
    "sweet_only": ["ube (ube) — primarily sweets although modern savory uses exist", "pandan (pandan) — mainly sweets/drinks"],
    "signature_ingredients": ["calamansi — substitute: equal parts lime and mandarin/lemon juice", "bagoong alamang — substitute: shrimp paste, then adjust salt", "banana ketchup — substitute: tomato ketchup plus small amount sugar and vinegar, imperfect", "souring agents such as sampalok — substitute: tamarind concentrate"],
    "pantry_assumed": ["vinegar", "garlic", "rice", "soy sauce or fish sauce in many households"],
    "techniques": ["vinegar braising", "souring soups", "grilling", "stir-frying noodles", "stewing"],
    "shortcuts": ["Sinigang soup mix: commonly tamarind/sour flavor, salt and seasonings; 20 g packet may contribute roughly 5-8 g salt, so do not salt separately until tasted.", "Bottled adobo marinade: 30-40 g per 500 g meat; commonly contributes roughly 3-5 g salt.", "Bagoong: 10 g may contribute 1.5-3 g salt."],
    "allergen_notes": ["Soy sauce contains soy and often wheat.", "Patis contains fish.", "Bagoong may contain fish or shellfish.", "Kare-kare commonly contains peanuts.", "Pancit noodles may contain wheat or egg depending type."],
    "pitfalls": ["Do not describe Filipino food as merely Spanish-Asian fusion.", "Adobo is a technique/family of preparations, not one fixed recipe.", "Not every savory dish is sweet.", "Regional cuisines of Bicol, Ilocos, Visayas and Mindanao differ strongly."],
    "sources": ["Doreen G. Fernandez, Tikim: Essays on Philippine Food and Culture, 1994", "https://repository.si.edu/bitstreams/8f2c83a6-9e1d-4f0e-a887-6122fde26a65/download", "https://archium.ateneo.edu/phstudies/vol35/iss3/1/", "https://web.nlp.gov.ph/wp-content/uploads/2025/06/NLP-Bibliography-on-Philippine-Cuisines.pdf"]
  },
  {
    "id": "indonesian",
    "label": "Indonesian",
    "subtitle": "Bumbu, sambal, coconut, fermentation",
    "about": "Indonesia spans thousands of islands between the Indian and Pacific oceans, so Javanese, Sumatran, Balinese, Sulawesi and eastern Indonesian cuisines can differ dramatically. Austronesian foundations, the spice trade, Indian and Middle Eastern links, Chinese migration and Dutch colonialism all contributed; rendang, nasi goreng, soto and gado-gado are recognizable examples.",
    "flavors": ["chile (cabai)", "shallot (bawang merah)", "garlic (bawang putih)", "galangal (lengkuas)", "lemongrass (serai)", "turmeric (kunyit)", "candlenut (kemiri)", "shrimp paste (terasi)", "sweet soy sauce (kecap manis)", "tamarind (asam jawa)", "makrut lime leaf (daun jeruk)", "coriander seed (ketumbar)"],
    "sweet_only": ["pandan (daun pandan) — mainly sweets/drinks but also rice", "palm sugar (gula aren/gula jawa) — used in sweets and savory dishes, so not dessert-only"],
    "signature_ingredients": ["candlenut — substitute: macadamia or cashew for body; allergen profile changes", "terasi — substitute: Southeast Asian shrimp paste", "kecap manis — substitute: soy sauce plus palm/brown sugar", "tempe — substitute: firm tofu, different texture/flavor"],
    "pantry_assumed": ["shallots", "garlic", "chiles or sambal", "rice in many but not all regions"],
    "techniques": ["grinding bumbu pastes", "frying aromatics", "slow coconut-milk simmering", "grilling", "fermentation"],
    "shortcuts": ["Commercial sambal oelek: 15-30 g per 500 g food; may contribute about 1-2 g salt.", "Rendang paste: 40-50 g per 500 g meat; often contributes 2-5 g salt depending brand.", "Kecap manis: 15 g may contribute roughly 1-2 g salt plus substantial sugar."],
    "allergen_notes": ["Kecap manis contains soy and commonly wheat.", "Terasi contains shellfish.", "Candlenut is a tree nut-like seed and may pose allergy concerns; commercial products can cross-contact tree nuts.", "Peanut sauce is central to dishes such as gado-gado and satay sauces.", "Tempe contains soy."],
    "pitfalls": ["Do not make every Indonesian dish sweet with kecap manis.", "Do not use coconut milk universally.", "Do not equate Indonesian cuisine with Javanese food alone.", "Sambal is a category with many regional forms, not one recipe."],
    "sources": ["Sri Owen, Sri Owen's Indonesian Food, 2008", "https://interlinkbooks.com/product/sri-owens-indonesian-food/", "https://link.springer.com/article/10.1186/s42779-019-0009-3", "https://www.sciencedirect.com/science/article/pii/S1878450X21001128"]
  },
  {
    "id": "malaysian_singaporean",
    "label": "Malaysia & SG",
    "subtitle": "Malay, Chinese, Indian, Peranakan",
    "about": "Malaysia and Singapore sit at a historic maritime crossroads linking the Indian Ocean and South China Sea. Malay, Chinese, Indian, Peranakan, indigenous and colonial communities created overlapping but distinct food traditions; nasi lemak, laksa, roti canai, Hainanese chicken rice and char kway teow are representative across the combined app category.",
    "flavors": ["shrimp paste (belacan)", "chile paste/relish (sambal)", "lemongrass (serai)", "galangal (lengkuas)", "turmeric (kunyit)", "pandan (daun pandan)", "makrut lime leaf (daun limau purut)", "tamarind (asam jawa)", "coconut milk (santan) — ingredient as well as flavoring", "sweet soy sauce (kicap manis)", "light soy sauce (kicap cair)", "curry leaf (daun kari)"],
    "sweet_only": ["gula melaka/palm sugar — strongly used in sweets but also savory dishes", "pandan — strongly associated with sweets but not dessert-only"],
    "signature_ingredients": ["belacan — substitute: Southeast Asian shrimp paste", "candlenut (buah keras) — substitute: macadamia/cashew for body; allergen change", "asam gelugur/asam keping — substitute: tamarind", "buah keluak — substitute: none; do not improvise because improperly processed raw seeds are unsafe"],
    "pantry_assumed": ["rice", "chiles/sambal in many households", "soy sauces in many Chinese-influenced kitchens", "coconut milk in many Malay/Peranakan kitchens"],
    "techniques": ["pounding rempah spice pastes", "wok stir-frying", "coconut-milk simmering", "grilling", "braising"],
    "shortcuts": ["Commercial laksa paste: 30-50 g per 400 ml coconut milk/stock; often contributes 3-6 g salt and may contain shrimp.", "Sambal: 20 g commonly contributes 1-3 g salt depending type.", "Curry powder for meat/fish: 10-15 g per 500 g; usually 0-2 g salt depending brand."],
    "allergen_notes": ["Belacan and many sambals contain shellfish.", "Soy sauces contain soy and often wheat.", "Peanuts appear in satay sauce and some noodle dishes.", "Indian-derived breads contain wheat and may contain milk or egg.", "Coconut is a U.S.-regulated tree-nut allergen.", "Candlenut warrants caution for nut-sensitive users."],
    "pitfalls": ["Do not treat Malaysian and Singaporean cuisine as one ethnic cuisine; both are multiethnic systems.", "Do not call every coconut-chile dish laksa.", "Distinguish Malay, Chinese, Indian and Peranakan lineages when possible.", "Do not substitute ordinary raw kepayang seeds for safely processed buah keluak."],
    "sources": ["https://ich.unesco.org/en/RL/breakfast-culture-in-malaysia-dining-experience-in-a-multi-ethnic-society-02113", "https://ich.unesco.org/en/RL/hawker-culture-in-singapore-community-dining-and-culinary-practices-in-a-multicultural-urban-context-01568", "https://www.roots.gov.sg/ich-landing/ich/peranakan-cuisine-in-singapore", "https://www.sciencedirect.com/science/article/pii/S2352618117301737"]
  }
]
```