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
- Asia: China, the Eight Great Cuisines (Sichuan, Hunan, Cantonese, Shandong, Jiangsu, Zhejiang, Fujian, Anhui, Any); Japan (Kanto, Kansai, Any); India (North, South, Any); Korean; Thai; Vietnamese; Filipino; Indonesian; Malaysian & Singaporean.

"Any" OPTIONS: China, Japan and India each have an "Any" option; no other node does. "Any" means the internationally recognized version of that country's food: what people outside the country think of when they think of it. Research it as a node of its own. Say where that outside view is a cliché, a stereotype, or an export version that differs from home cooking, but describe the outside view itself accurately.

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
Chinese (Cantonese - Most common style in US)
  Description: From Guangdong province in southern China, around the Pearl River Delta and the city of Guangzhou. Fresh ingredients and light seasoning that lets them taste of themselves: steamed fish, quick stir-fries with wok hei (the smoky "breath of the wok"), dim sum. Most early Chinese emigrants came from here, which is why it's the style of most Chinese restaurants abroad.
  Classic flavors: ginger (jiang, 姜), green onions (cong, 葱), garlic (suan, 蒜), soy sauce (jiang you, 酱油), oyster sauce (hao you, 蚝油), fermented black beans (douchi, 豆豉), sesame oil (zhi ma you, 芝麻油), rice wine (mi jiu or Shaoxing jiu, 米酒 or 绍兴酒), white pepper (bai hu jiao, 白胡椒), and dried tangerine peel (chen pi, 陈皮)
Chinese (Hong Kong)
  Description: Cantonese cooking at its root, sharpened by a century and a half as a trading port and British colony. Known for siu mei roast meats (char siu, roast goose), fresh seafood, and cha chaan teng diners that serve milk tea, macaroni soup and baked pork chop rice.
  Classic flavors: ginger (薑; gēung), green onions or scallions (蔥; chūng), white pepper (白胡椒; baahk wùh jīu), soy sauce (醬油; jeung yàuh), oyster sauce (蠔油; hòuh yàuh), garlic (蒜; syun), sesame oil (芝麻油; jī màh yàuh), fermented black beans (豆豉; dauh sih), and, for siu mei roast meats such as char siu, five-spice powder (五香粉; ńgh hēung fán), star anise (八角; baat gok) and hoisin sauce (海鮮醬; hói sīn jeung)
Chinese (Sichuan)
  Description: From Sichuan province and Chongqing, in a mountain-ringed basin on the upper Yangtze River in southwest China. Famous for mala, the numbing tingle of Sichuan peppercorn with chili heat, and for fermented broad bean paste, but it has dozens of named flavor profiles, many of them not hot at all. Mapo tofu, kung pao chicken, twice-cooked pork.
  Classic flavors: Sichuan peppercorns (hua jiao, 花椒), dried chili peppers (gan la jiao, 干辣椒), broad bean chili paste (doubanjiang, 豆瓣酱), garlic (suan, 蒜), ginger (jiang, 姜), green onions or scallions (cong, 葱), pickled vegetables (pao cai, 泡菜), star anise (ba jiao, 八角), fermented black beans (douchi, 豆豉) and five-spice powder (wu xiang fen, 五香粉)
Chinese (Shandong)
  Description: Lu cuisine, from Shandong province on China's northeast coast, where the Yellow River meets the sea. Often called the oldest of China's great regional styles, and a major influence on Beijing's imperial court cooking: salty and savory, scallion-forward, with seafood, clear and milky broths, vinegar, and fast high-heat techniques like bao (explosion frying).
  Classic flavors: green onions or scallions (cong, 葱), ginger (jiang, 姜), garlic (suan, 蒜), soy sauce (jiang you, 酱油), rice wine (mi jiu, 米酒), sesame oil (zhi ma you, 芝麻油), star anise (ba jiao, 八角), white pepper (bai hu jiao, 白胡椒) and vinegar (cu, 醋)
  Signature ingredients: wood ear mushrooms (mu er, 木耳)
Chinese (Jiangsu)
  Description: Huaiyang cuisine, from Jiangsu province on the lower Yangtze River and the Grand Canal (Yangzhou, Huai'an, Suzhou, Nanjing), long called a land of fish and rice. Delicate and slightly sweet, with precise knife work and slow braising, made to show off freshwater fish, crab and seasonal vegetables. Lion's head meatballs, Yangzhou fried rice.
  Classic flavors: ginger (jiang, 姜), green onions or scallions (cong, 葱), rice wine (mi jiu or Shaoxing jiu, 米酒 or 绍兴酒), soy sauce (jiang you, 酱油), sugar (tang, 糖), vinegar (cu, 醋), sesame oil (zhi ma you, 芝麻油), and red fermented tofu (nan ru or fu ru, 南乳 or 腐乳)
  Dessert-only flavors: osmanthus syrup (gui hua tang, 桂花糖)
  Signature ingredients: dried bamboo shoots (gan sun, 干笋)
Japanese (Kansai)
  Description: From western Japan around Osaka and Kyoto. Kombu-based dashi and light-colored usukuchi soy sauce keep food pale and delicate (and, surprisingly, a little saltier). Kyoto's refined kaiseki on one side, Osaka's street food like okonomiyaki and takoyaki on the other.
  Classic flavors: dashi, Kansai shoyu (usukuchi soy sauce), mirin, sake, Kansai-style white miso, shichimi togarashi, sansho (Japanese pepper), yuzu, shiso, negi (scallions or green onions), bonito flakes (katsuobushi) and konbu
Japanese (Kanto)
  Description: From eastern Japan around Tokyo, the old city of Edo. Bolder and darker: dark koikuchi soy sauce, bonito-rich dashi and sweet-salty sauces. Edomae sushi, soba with strong tsuyu, and tempura all began as Edo fast food.
  Classic flavors: Kanto shoyu (koikuchi soy sauce), dashi, wasabi, negi (scallions or green onions), ginger (shoga), nori, sansho (Japanese pepper), red miso (akamiso), sake, and tsuyu
North Indian
  Description: From Punjab and the northern plains, shaped by the Mughal courts: wheat breads like naan and roti, the tandoor clay oven, and rich gravies with ghee, cream, yogurt and paneer. Warm whole and ground spices, often finished with garam masala.
  Classic flavors: turmeric (haldi), cumin (jeera), coriander (dhania), red chili powder (lal mirch), garam masala, green cardamom (elaichi), cloves (laung), black mustard seeds (rai), fenugreek (methi), and asafoetida (hing)
South Indian
  Description: From Tamil Nadu, Kerala, Karnataka, Andhra Pradesh and Telangana: rice and lentils (dosa, idli, sambar), coconut and tamarind, and the tempering of mustard seeds and curry leaves sizzled in hot oil. Often hotter and more sour than northern cooking.
  Classic flavors: mustard seeds (rai/kadugu), curry leaves (kadi patta/karuveppilai), tamarind (imli/puli), urad dal (ulundu paruppu/uddina bele), dried red chilies (lal mirch/sukku milagai), fenugreek seeds (methi/vendhayam/menthulu), asafoetida (hing/perungayam/inguva), black pepper (kali mirch/milagu), coriander seeds (dhania/dhaniya/malli), and turmeric (haldi/manjal)
Korean
  Description: Built on fermentation: kimchi and the jang pastes and sauces (gochujang, doenjang, ganjang). A meal is rice, soup or stew, and a spread of small banchan side dishes; grilling and long-simmered stews (jjigae) are the heart of it.
  Classic flavors: red pepper flakes (gochugaru, 고추가루), red pepper paste (gochujang, 고추장), soybean paste (doenjang, 된장), soy sauce (ganjang, 간장), garlic (maneul, 마늘), ginger (saenggang, 생강), green onions or scallions (pa, 파), sesame oil (chamgireum, 참기름), and sesame seeds (chamggae, 참깨)
  Signature ingredients: perilla leaves (kkaennip, 깻잎)
Thai
  Description: A balance of sweet, sour, salty and spicy in every dish, using fresh herbs, pounded curry pastes, fish sauce, lime and palm sugar. Coconut milk is common in central and southern dishes.
  Classic flavors: chilies (prik), galangal (kha), lemongrass (takrai), kaffir lime leaves (bai makrut), fish sauce (nam pla), Thai basil (horapa), coriander and cilantro (pak chi), tamarind (makham), coconut milk (nam kati), and palm sugar (nam tan pip)
Vietnamese
  Description: Fresh and bright: fish sauce, lime, chili and a pile of fresh herbs at every meal. Clear, fragrant broths like pho come from the north around Hanoi; French rule left baguettes (bánh mì) and coffee.
  Classic flavors: fish sauce (nước mắm), lemongrass (sả), lime (chanh), ginger (gừng), turmeric (nghệ), Vietnamese coriander (rau răm), Thai basil (húng quế), mint (húng lủi), star anise (đại hồi), and green onions or scallions (hành lá)
