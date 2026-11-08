"""Audiences, cuisines, dietary rules and the prompts built from them.

Ported from RecipeGPT's personas.py (2024), with spelling fixes, a corrected allergen list
(FALCPA + the 2021 FASTER Act: nine allergens, sesame included) and rules for follow-up edits.
"""

# ---------------------------------------------------------------- audiences

AUDIENCES: dict[str, str] = {
    "A working professional.":
        "a working professional who would like to be able to whip up a quick but delicious weeknight meal.",
    "An important person you want to impress!":
        "an important person for whom you have all the time, money and energy you need to make a fancy dish "
        "that is sure to impress!",
    "A busy family with children.":
        "a busy family who requires a meal which is kid-friendly, can serve multiple people, and is both "
        "nutritious and tasty for children and adults.",
    "The elderly or mobility impaired.":
        "an elderly or mobility impaired individual who needs easy-to-make meals that don't require a lot of "
        "physical effort, finely chopping or mincing anything, or standing for long periods of time.",
    "A meal prepper who makes food for the entire week in one go.":
        "an avid meal prepper who needs meal-prep ideas that can be prepared on the weekend to eat during the "
        "following week, perfect for busy schedules. Make sure to specify if any ingredients should be stored "
        "separately after the food is prepared, i.e. lettuce stored separately from chicken or cooked noodles "
        "stored separately from a broth. If a cooked ingredient cannot be safely refrigerated for a week without "
        "eating, mention this.",
    "A solo diner who doesn't want to deal with leftovers.":
        "a solitary individual looking for single-serving recipes that are quick and easy to prepare and won't "
        "leave any leftovers.",
    "A health conscious individual who prefers food that's nutritious, high in protein and low in empty calories.":
        "a health enthusiast who prefers meals that are nutritious, low in unnecessary calories, include fresh "
        "produce (possibly organic) and are high in protein when possible.",
    "A college student with only a microwave.":
        "a college student who requires a simple recipe that can be prepared using only a microwave.",
}
DEFAULT_AUDIENCE = "A working professional."

# ---------------------------------------------------------------- cuisines
# label shown in the app -> (name used in the prompt, its classic seasonings)

NO_CUISINE = "Nothing in particular"

CUISINES: dict[str, tuple[str, str]] = {
    NO_CUISINE: ("", ""),
    "American": (
        "American",
        "black pepper, salt, garlic, onion, paprika, chili powder, cayenne pepper, cinnamon, oregano, "
        "vanilla extract and Old Bay"),
    "American (Cajun)": (
        "Cajun",
        "cayenne pepper, paprika, garlic, onion, green bell peppers, celery, bay leaves, thyme, oregano, and "
        "black and white pepper"),
    "American (Creole)": (
        "New Orleans Creole",
        "onion, celery and green bell peppers, garlic, butter, tomato paste, cayenne pepper, paprika, thyme, bay "
        "leaves, oregano, basil, parsley, green onions, black and white pepper, and Louisiana hot sauce"),
    "Chinese (Cantonese - Most common style in US)": (
        "Cantonese/Guangdong/Yue (Chinese)",
        "ginger (jiang, 姜), green onions (cong, 葱), garlic (suan, 蒜), soy sauce (jiang you, 酱油), "
        "oyster sauce (hao you, 蚝油), fermented black beans (douchi, 豆豉), sesame oil (zhi ma you, 芝麻油), "
        "rice wine (mi jiu or Shaoxing jiu, 米酒 or 绍兴酒), white pepper (bai hu jiao, 白胡椒), and dried "
        "tangerine peel (chen pi, 陈皮)"),
    "Chinese (Hong Kong)": (
        "Hong Kong",
        "ginger (薑; gēung), green onions or scallions (蔥; chūng), white pepper (白胡椒; baahk wùh jīu), "
        "soy sauce (醬油; jeung yàuh), oyster sauce (蠔油; hòuh yàuh), garlic (蒜; syun), sesame oil "
        "(芝麻油; jī màh yàuh), fermented black beans (豆豉; dauh sih), and, for siu mei roast meats such as "
        "char siu, five-spice powder (五香粉; ńgh hēung fán), star anise (八角; baat gok) and hoisin sauce "
        "(海鮮醬; hói sīn jeung)"),
    "Chinese (Sichuan)": (
        "Sichuan (Chinese)",
        "Sichuan peppercorns (hua jiao, 花椒), dried chili peppers (gan la jiao, 干辣椒), broad bean chili paste "
        "(doubanjiang, 豆瓣酱), garlic (suan, 蒜), ginger (jiang, 姜), green onions or scallions (cong, 葱), "
        "pickled vegetables (pao cai, 泡菜), star anise (ba jiao, 八角), fermented black beans (douchi, 豆豉) "
        "and five-spice powder (wu xiang fen, 五香粉)"),
    "Chinese (Shandong)": (
        "Shandong/Lu (Chinese)",
        "green onions or scallions (cong, 葱), ginger (jiang, 姜), garlic (suan, 蒜), soy sauce (jiang you, 酱油), "
        "rice wine (mi jiu, 米酒), sesame oil (zhi ma you, 芝麻油), star anise (ba jiao, 八角), white "
        "pepper (bai hu jiao, 白胡椒) and vinegar (cu, 醋)"),
    "Chinese (Jiangsu)": (
        "Huaiyang/Jianghuai (Chinese)",
        "ginger (jiang, 姜), green onions or scallions (cong, 葱), rice wine (mi jiu or Shaoxing jiu, 米酒 or "
        "绍兴酒), soy sauce (jiang you, 酱油), sugar (tang, 糖), vinegar (cu, 醋), sesame oil (zhi ma you, 芝麻油), "
        "and red fermented tofu (nan ru or fu ru, 南乳 or 腐乳)"),
    "French": (
        "French",
        "thyme (thym), bay leaf (feuille de laurier), parsley (persil), tarragon (estragon), chervil (cerfeuil), "
        "rosemary (romarin), nutmeg (noix de muscade), Dijon mustard (moutarde de Dijon), garlic (ail) and "
        "shallots (échalotes)"),
    "Greek": (
        "Greek",
        "oregano (ρίγανη; rígani), olive oil (ελαιόλαδο; elaiólado), lemon (λεμόνι; lemóni), dill (άνηθος; "
        "ánithos), mint (δυόσμος; dyósmos), bay leaf (φύλλο δάφνης; fýllo dáfnis), cinnamon (κανέλα; kanéla), "
        "nutmeg (μοσχοκάρυδο; moschokárydo), and fennel (μάραθος; márathos)"),
    "North Indian": (
        "North Indian",
        "turmeric (haldi), cumin (jeera), coriander (dhania), red chili powder (lal mirch), garam masala, "
        "green cardamom (elaichi), cloves (laung), black mustard seeds (rai), fenugreek (methi), and asafoetida "
        "(hing)"),
    "South Indian": (
        "South Indian",
        "mustard seeds (rai/kadugu), curry leaves (kadi patta/karuveppilai), tamarind (imli/puli), urad dal "
        "(ulundu paruppu/uddina bele), dried red chilies (lal mirch/sukku milagai), fenugreek seeds "
        "(methi/vendhayam/menthulu), asafoetida (hing/perungayam/inguva), black pepper (kali mirch/milagu), "
        "coriander seeds (dhania/dhaniya/malli), and turmeric (haldi/manjal)"),
    "Italian": (
        "Italian",
        "garlic (aglio), basil (basilico), oregano (origano), rosemary (rosmarino), sage (salvia), parsley "
        "(prezzemolo), red pepper flakes (peperoncino), fennel seeds (semi di finocchio), anchovies or anchovy "
        "paste (acciughe, as a seasoning), and nutmeg (noce moscata)"),
    "Japanese (Kansai)": (
        "Kansai (Japanese)",
        "dashi, Kansai shoyu (usukuchi soy sauce), mirin, sake, Kansai-style white miso, shichimi togarashi, "
        "sansho (Japanese pepper), yuzu, shiso, negi (scallions or green onions), bonito flakes (katsuobushi) "
        "and konbu"),
    "Japanese (Kanto)": (
        "Kanto (Japanese)",
        "Kanto shoyu (koikuchi soy sauce), dashi, wasabi, negi (scallions or green onions), ginger (shoga), "
        "nori, sansho (Japanese pepper), red miso (akamiso), sake, and tsuyu"),
    "Korean": (
        "Korean",
        "red pepper flakes (gochugaru, 고추가루), red pepper paste (gochujang, 고추장), soybean "
        "paste (doenjang, 된장), soy sauce (ganjang, 간장), garlic (maneul, 마늘), ginger (saenggang, 생강), "
        "green onions or scallions (pa, 파), sesame oil (chamgireum, 참기름), and sesame seeds "
        "(chamggae, 참깨)"),
    "Mexican": (
        "Mexican",
        "chilies (chiles), cumin (comino), cilantro and coriander (cilantro y coriandro), Mexican oregano "
        "(orégano), garlic (ajo), epazote, chocolate, cinnamon (canela), annatto (achiote), and lime (limón)"),
    "Peruvian": (
        "Peruvian",
        "ají amarillo, ají panca, cilantro (culantro), huacatay, cumin (comino), garlic (ajo), lime (limón), "
        "annatto (achiote), oregano (orégano), and ginger (kion)"),
    "Spanish": (
        "Spanish",
        "saffron (azafrán), paprika (pimentón), garlic (ajo), parsley (perejil), bay leaf (laurel), rosemary "
        "(romero), cumin (comino), thyme (tomillo), olive oil (aceite de oliva), and sherry vinegar (vinagre "
        "de Jerez)"),
    "Thai": (
        "Thai",
        "chilies (prik), galangal (kha), lemongrass (takrai), kaffir lime leaves (bai makrut), fish sauce "
        "(nam pla), Thai basil (horapa), coriander and cilantro (pak chi), tamarind (makham), coconut milk "
        "(nam kati), and palm sugar (nam tan pip)"),
    "Turkish": (
        "Turkish",
        "red pepper flakes (pul biber), sumac (sumak), mint (nane), cumin (kimyon), allspice (yenibahar), "
        "sesame seeds (susam), pomegranate molasses (nar ekşisi), fenugreek (çemen), oregano (kekik), and bay "
        "leaf (defne yaprağı)"),
    "Vietnamese": (
        "Vietnamese",
        "fish sauce (nước mắm), lemongrass (sả), lime (chanh), ginger (gừng), turmeric (nghệ), Vietnamese "
        "coriander (rau răm), Thai basil (húng quế), mint (húng lủi), star anise (đại hồi), and green onions "
        "or scallions (hành lá)"),
}

# Classic flavors used only when the user asks for a dessert.
SWEET_FLAVORS: dict[str, str] = {
    "Chinese (Jiangsu)": "osmanthus syrup (gui hua tang, 桂花糖)",
    "Greek": "mastiha (μαστίχα; mastícha)",
}

# Classic main ingredients, not seasonings: used only if the user has them, otherwise mentioned in the Tips.
SIGNATURE_INGREDIENTS: dict[str, str] = {
    "Chinese (Shandong)": "wood ear mushrooms (mu er, 木耳)",
    "Chinese (Jiangsu)": "dried bamboo shoots (gan sun, 干笋)",
    "Korean": "perilla leaves (kkaennip, 깻잎)",
}

# Extra lines for the Tips section at the end of a recipe.
CUISINE_TIPS: dict[str, str] = {
    "American (Cajun)": (
        "Use the separate spices in the recipe itself, never a store-bought blend. Then add a tip for cooks short "
        "on time: most Cajun seasoning is paprika, cayenne, garlic, onion, black pepper, oregano and thyme plus a "
        "lot of salt, so say how many grams of blend would replace the spices in this recipe, and to cut the "
        "added salt if they use it."),
    "American (Creole)": (
        "Use the separate spices in the recipe itself, never a store-bought blend. Then add a tip for cooks short "
        "on time: most Creole seasoning is paprika, garlic, onion, cayenne, black and white pepper, oregano, thyme "
        "and basil plus a lot of salt, so say how many grams of blend would replace the spices in this recipe, "
        "and to cut the added salt if they use it."),
    "Italian": (
        "If the recipe uses anchovies, add a tip that anchovy-only fish sauce works as a substitute (check the "
        "label: just anchovies and salt), with the amount."),
    "Korean": (
        "Kimchi (김치) is in nearly every Korean kitchen. Write the recipe so it works without it, but if the "
        "user didn't list it, strongly recommend it in the Tips: served alongside, or cooked in if it suits "
        "the dish."),
}

# Shown in the app (the info sheet on the picked cuisine chip), never sent to the model.
CUISINE_ABOUT: dict[str, str] = {
    "American": (
        "Home cooking from across the United States: smoky barbecue rubs, Chesapeake Bay seafood seasoned with "
        "Old Bay, and the warm baking spices of holiday tables. Generous, bold and unfussy."),
    "American (Cajun)": (
        "The country cooking of southern Louisiana's bayous and prairies, from the Acadians: French-speaking "
        "settlers expelled from eastern Canada in the 1750s. Rustic one-pot dishes such as gumbo, jambalaya and "
        "étouffée, built on a dark roux and the \"holy trinity\" of onion, celery and green bell pepper, with "
        "cayenne heat. Not the same as Creole, the city cooking of New Orleans, which uses more butter and "
        "tomatoes."),
    "American (Creole)": (
        "The city cooking of New Orleans, shaped by its French and Spanish colonial rulers, by West African and "
        "Caribbean cooks (many of them enslaved), and later by Italian and German immigrants. Richer and more "
        "refined than its country cousin Cajun, with more butter, cream and tomatoes on the same base of onion, "
        "celery and green bell pepper. Shrimp Creole, red beans and rice, grillades and grits, and the city's "
        "tomato-red jambalaya."),
    "Chinese (Cantonese - Most common style in US)": (
        "From Guangdong province in southern China, around the Pearl River Delta and the city of Guangzhou. "
        "Fresh ingredients and light seasoning that lets them taste of themselves: steamed fish, quick stir-fries "
        "with wok hei (the smoky \"breath of the wok\"), dim sum. Most early Chinese emigrants came from here, "
        "which is why it's the style of most Chinese restaurants abroad."),
    "Chinese (Hong Kong)": (
        "Cantonese cooking at its root, sharpened by a century and a half as a trading port and British colony. "
        "Known for siu mei roast meats (char siu, roast goose), fresh seafood, and cha chaan teng diners that "
        "serve milk tea, macaroni soup and baked pork chop rice."),
    "Chinese (Sichuan)": (
        "From Sichuan province and Chongqing, in a mountain-ringed basin on the upper Yangtze River in southwest "
        "China. Famous for mala, the numbing tingle of Sichuan peppercorn with chili heat, and for fermented "
        "broad bean paste, but it has dozens of named flavor profiles, many of them not hot at all. Mapo tofu, "
        "kung pao chicken, twice-cooked pork."),
    "Chinese (Shandong)": (
        "Lu cuisine, from Shandong province on China's northeast coast, where the Yellow River meets the sea. "
        "Often called the oldest of China's great regional styles, and a major influence on Beijing's imperial "
        "court cooking: salty and savory, scallion-forward, with seafood, clear and milky broths, vinegar, and "
        "fast high-heat techniques like bao (explosion frying)."),
    "Chinese (Jiangsu)": (
        "Huaiyang cuisine, from Jiangsu province on the lower Yangtze River and the Grand Canal (Yangzhou, "
        "Huai'an, Suzhou, Nanjing), long called a land of fish and rice. Delicate and slightly sweet, with "
        "precise knife work and slow braising, made to show off freshwater fish, crab and seasonal vegetables. "
        "Lion's head meatballs, Yangzhou fried rice."),
    "French": (
        "The foundation of Western restaurant technique: stocks, mother sauces, butter, wine and slow braises, "
        "lifted by fresh herbs. Regional styles range from Normandy's butter and cream to Provence's olive oil, "
        "garlic and tomatoes."),
    "Greek": (
        "Mediterranean cooking built on olive oil, lemon and oregano: grilled meat and fish, vegetables, beans, "
        "yogurt, feta and phyllo. Centuries of Ottoman rule left warm spices like cinnamon in meat dishes such "
        "as moussaka and stifado."),
    "North Indian": (
        "From Punjab and the northern plains, shaped by the Mughal courts: wheat breads like naan and roti, the "
        "tandoor clay oven, and rich gravies with ghee, cream, yogurt and paneer. Warm whole and ground spices, "
        "often finished with garam masala."),
    "South Indian": (
        "From Tamil Nadu, Kerala, Karnataka, Andhra Pradesh and Telangana: rice and lentils (dosa, idli, sambar), "
        "coconut and tamarind, and the tempering of mustard seeds and curry leaves sizzled in hot oil. Often "
        "hotter and more sour than northern cooking."),
    "Italian": (
        "Regional to the core: butter, rice and polenta in the north; olive oil, tomatoes and dried pasta in the "
        "south. A few excellent ingredients, treated simply."),
    "Japanese (Kansai)": (
        "From western Japan around Osaka and Kyoto. Kombu-based dashi and light-colored usukuchi soy sauce keep "
        "food pale and delicate (and, surprisingly, a little saltier). Kyoto's refined kaiseki on one side, "
        "Osaka's street food like okonomiyaki and takoyaki on the other."),
    "Japanese (Kanto)": (
        "From eastern Japan around Tokyo, the old city of Edo. Bolder and darker: dark koikuchi soy sauce, "
        "bonito-rich dashi and sweet-salty sauces. Edomae sushi, soba with strong tsuyu, and tempura all began "
        "as Edo fast food."),
    "Korean": (
        "Built on fermentation: kimchi and the jang pastes and sauces (gochujang, doenjang, ganjang). A meal is "
        "rice, soup or stew, and a spread of small banchan side dishes; grilling and long-simmered stews (jjigae) "
        "are the heart of it."),
    "Mexican": (
        "Indigenous Mesoamerican foods (corn, chiles, beans, squash, cacao) blended with Spanish ingredients. "
        "Corn is nixtamalized for tortillas and masa; dried chiles are toasted and ground into sauces. Strongly "
        "regional, from Oaxaca's moles to the Yucatán's achiote."),
    "Peruvian": (
        "Andean, coastal and Amazonian cooking mixed with Spanish, African, Chinese (chifa) and Japanese "
        "(Nikkei) influences. Built around ají chiles, hundreds of potatoes, and very fresh fish: ceviche, lomo "
        "saltado, ají de gallina."),
    "Spanish": (
        "Olive oil, garlic, smoked pimentón and saffron. Tapas, rice dishes like Valencia's paella, slow stews, "
        "and cured ham, with sherry vinegar for brightness."),
    "Thai": (
        "A balance of sweet, sour, salty and spicy in every dish, using fresh herbs, pounded curry pastes, fish "
        "sauce, lime and palm sugar. Coconut milk is common in central and southern dishes."),
    "Turkish": (
        "From Anatolia and the Ottoman palace kitchens: kebabs, mezze, yogurt, flatbreads and stuffed "
        "vegetables, with tangy sumac, pul biber chili flakes and pomegranate molasses."),
    "Vietnamese": (
        "Fresh and bright: fish sauce, lime, chili and a pile of fresh herbs at every meal. Clear, fragrant "
        "broths like pho come from the north around Hanoi; French rule left baguettes (bánh mì) and coffee."),
}

# ---------------------------------------------------------------- dietary rules

RESTRICTIONS: dict[str, str] = {
    "Kosher":
        "The recipe must be kosher. Kosher food follows Jewish dietary law: no pork or shellfish, animals "
        "slaughtered and certified according to kashrut, and meat and dairy never cooked or served together. "
        "Poultry counts as meat, and so does anything made from meat or poultry, such as chicken or beef broth, "
        "stock or bouillon: never combine these with butter, milk, cream, cheese or yogurt. Many authorities "
        "also don't cook fish together with meat. Call for kosher-certified packaged ingredients.",
    "Halal":
        "The recipe must be halal. Halal food complies with Islamic dietary law: no pork or pork products "
        "(including lard and gelatin from pork), no alcohol (including cooking wines such as mirin, sake, "
        "Shaoxing wine, sherry and wine), and meat slaughtered in the prescribed manner.",
    "Gluten-free":
        "The recipe must be gluten-free. Gluten is a protein in wheat, barley and rye; most flours, breads, "
        "pastas and noodles contain it. It also hides in ordinary soy sauce, gochujang, doenjang, many misos, "
        "hoisin, oyster sauce, malt vinegar, beer, bouillon and seasoning blends: call for tamari or certified "
        "gluten-free versions of these. The recipe is meant for people with celiac disease or gluten sensitivity.",
    "Keto":
        "The recipe must be keto. Keto (ketogenic) food is very low in carbohydrates and high in fat and "
        "protein, aiming to keep the body in ketosis: no grains, rice, pasta, bread, potatoes, sugar, or "
        "starchy vegetables.",
    "Vegetarian":
        "The recipe must be vegetarian. Vegetarian food excludes meat, poultry and fish, including broths, "
        "fish sauce, anchovies and gelatin made from them, but can include dairy, eggs and honey.",
    "Vegan":
        "The recipe must be vegan. Vegan food contains no animal products at all, including eggs, milk, butter, "
        "cheese, honey, fish sauce, gelatin and animal-based broths.",
    "Free of major food allergens":
        "The recipe must be free of all nine major food allergens defined by U.S. law (the Food Allergen "
        "Labeling and Consumer Protection Act, FALCPA, plus sesame, added by the FASTER Act in 2023): milk, eggs, "
        "fish (such as bass, flounder, cod), crustacean shellfish (such as crab, lobster, shrimp), tree nuts "
        "(such as almonds, walnuts, pecans), peanuts, wheat, soybeans, and sesame. Watch for hidden sources: "
        "butter, ghee and cheese (milk); fish sauce, anchovies and Worcestershire sauce (fish); soy sauce, "
        "tamari, miso, doenjang, gochujang and tofu (soy, often wheat too); sesame oil, sesame seeds and tahini "
        "(sesame); and ordinary flour, bread and noodles (wheat). Coconut is not one of the nine, but mention it "
        "if you use it, since some people with tree-nut allergies avoid it.",
    "Low calorie":
        "The recipe must be low calorie: reduced calories per serving, for weight management. Avoid heavy "
        "cream, large amounts of oil or butter, and fried components.",
    "Diabetic":
        "The recipe must be suitable for diabetics: low in sugar and refined carbohydrates, focused on foods "
        "with a low glycemic index to help manage blood sugar.",
}
MAX_RESTRICTIONS = 3


# ---------------------------------------------------------------- prompts

def system_prompt(audience: str, cuisine: str, dessert: bool = False,
                  restrictions: list[str] | None = None) -> str:
    """The standing instructions for one recipe conversation."""
    audience_text = AUDIENCES.get(audience, AUDIENCES[DEFAULT_AUDIENCE])
    name, flavors = CUISINES.get(cuisine, CUISINES[NO_CUISINE])
    if dessert and cuisine in SWEET_FLAVORS:
        flavors += f", and for desserts, {SWEET_FLAVORS[cuisine]}"

    if name:
        style = (f"from {name} cuisine, keeping in mind that the audience for your recipe is an enthusiast and "
                 f"expert in {name} cuisine who would like you to prepare a dish with authentic {name} spices and "
                 f"flavors. Draw on classic {name} spices and flavors such as {flavors}, but use only the ones "
                 f"that suit this dish: you don't need all of them, and none should feel out of place")
        staples_extra = ", plus any of the classic flavors above,"
    else:
        style = "from any cuisine or culture"
        staples_extra = ","

    tips = []
    if cuisine in SIGNATURE_INGREDIENTS:
        sig = SIGNATURE_INGREDIENTS[cuisine]
        tips.append(f"{sig[0].upper() + sig[1:]} are signature {name} ingredients, not a seasoning: use them only if "
                    f"they're in the user's ingredients. If they're not, say in the Tips that if you have them, "
                    f"they're a classic of {name} cooking, but this recipe uses what you actually have on hand.")
    if cuisine in CUISINE_TIPS:
        tips.append(CUISINE_TIPS[cuisine])
    tips_text = ("End the recipe with a short Tips section. " + " ".join(tips)) if tips else ""

    restriction_text = ""
    if restrictions:
        rules = " ".join(RESTRICTIONS[r] for r in restrictions if r in RESTRICTIONS)
        restriction_text = (
            "In addition, the recipe you generate must meet the following dietary requirements. Please "
            "acknowledge your awareness of these dietary requirements in your response. " + rules + " "
            "These requirements override the classic flavors listed below: leave out or substitute any classic "
            "ingredient that would break them, and say what you substituted.")

    if dessert:
        dish = ("Your target audience would like a DESSERT recipe! Don't include any ingredients inappropriate "
                "for a dessert.")
        staples = "butter, oil, salt and pepper, brown and white sugar, herbs and spices, and milk"
    else:
        dish = "Make one savory main dish (with sides if they belong to it), not a dessert."
        staples = "butter, oil, salt and pepper, herbs and spices, and milk"

    return f"""\
Respond as an experienced food scientist and test kitchen developer who goes by the handle ChefBot, known for
your command of cooking fundamentals, your flair for modern creativity, and your ability to break things down into
straightforward steps that anyone can follow. Write in plain text and Markdown only: no emojis.

You are being asked to prepare a recipe for {audience_text} {dish} They will provide you with a list of
ingredients to use in the recipe. If you are not given any food items to use, please decline to generate a recipe.

{restriction_text}

Please suggest a recipe {style}. Your recipe may include other pantry staples such as {staples}{staples_extra}
but otherwise the primary ingredients for the recipe should come ONLY from the ingredients wrapped in triple
quotes in the user's first message. {tips_text}

Please keep in mind that you cannot include any non-food or harmful ingredients in your recipe. If you are asked
to provide a recipe using such ingredients, you will decline, or explain that you will provide a recipe that omits
the non-food or dangerous ingredients. You do not need to use every ingredient provided, but you should do your
best to use as many as possible.

Be precise, like a serious cookbook: exact quantities (US and metric), pan sizes, heat levels, temperatures,
timings, and doneness cues (internal temperatures for meat, poultry and fish). Explain the "why" behind a
technique when it matters.

Give salt in grams, always: a volume alongside is fine, never instead. Weigh baking ingredients in grams too.

Before you give a recipe, check your work:
- Dietary rules and anything the user must not have: re-read every ingredient against them, including hidden
  sources (Worcestershire sauce contains fish, soy sauce contains wheat, broth counts as the animal it came from).
  Name every substitution.
- Servings: the "Serves" line must match the quantities. For an adult main, plan roughly 150 to 225 g raw
  protein, 75 to 100 g dry pasta, or one medium potato as a side. When scaling, scale every quantity and note any
  change to pan size or timing.
- Ratios: salt (bread about 2% of the flour's weight, brines 5 to 6%, meat about 1% of its weight), leavening
  (about 1 teaspoon baking powder or 1/4 teaspoon baking soda per 125 g flour), rice to water, and dressings
  (about 3 parts oil to 1 part acid).
- Times: the total time must cover every step added together.
- Units: the US and metric amounts must match.
- History: if a pairing is unusual, say so. Never invent a tradition to justify it.

The user may come back and ask for changes ("no cucumber", "make it for six", "make it spicier", "how would
this have been made in 1817?"). When they do, write out the complete revised recipe with the change applied,
starting with one short line saying what you changed. Keep following every dietary requirement above. Keep the
"Recipe Title: " line, and change the title if the dish changes. If they only ask a question, just answer it.
""".replace("\n\n\n", "\n\n")


def first_message(ingredients: str, must_not: str = "") -> str:
    """The user's opening message: their ingredients plus the formatting rules."""
    must_not_text = ""
    if must_not.strip():
        must_not_text = (f"In addition, it is VERY IMPORTANT that the recipe you create does NOT include any of "
                         f"the following: {must_not.strip()}. In your response, mention that you are aware of "
                         f"these restrictions and took them into account. ")
    return (
        f'The ingredients list is: """{ingredients.strip()}""" If the ingredients list directly above is empty or '
        'contains no food items, DO NOT generate a recipe. Please reply that you are sorry, but you can only '
        'generate a recipe if given ingredients in the first place. '
        'If the ingredients list is long, indicating perhaps everything the user has in their fridge or bought '
        'while grocery shopping, simply choose a few ingredients that you think would make the best dish and use '
        'those. Before you begin generating your recipe, double check the ingredients list to make sure you '
        'understood the ingredients properly. For example, chicken or beef broth is a liquid, not the meat itself: '
        'if you have only broth, you cannot make a meat dish (though for dietary rules, broth still counts as the '
        'animal it came from). '
        f'{must_not_text}'
        'Start with a short introduction of yourself and the dish (two or three sentences, no chit-chat), then '
        'give the recipe a title on its own line beginning with the exact string "Recipe Title: ".'
    )


INGREDIENTS_FROM_PHOTO = """\
You are helping a recipe-creation assistant by listing the ingredients you see in a photograph of food items
(a fridge, a pantry, a table of groceries). List only the food items you can actually see, comma-separated,
without commentary. For example, a good response would be:
"Milk, carrots, eggs, bell peppers, mushrooms."
A bad response would be:
"A carton of eggs, which can be used in multiple recipes, from omelets to baked dishes. A bottle of milk, a staple
for many recipes including sauces, batters, and baked goods."
Be specific when you can tell (chicken thighs, not just chicken; Napa cabbage, not just cabbage). If you see no
food at all, reply with exactly: NO FOOD
"""


def dish_photo_prompt(title: str) -> str:
    """The cookbook-cover photo prompt from RecipeGPT's 'modernist Bon Appétit' style."""
    return (f"High clarity, modernist cookbook cover photograph of {title}. Top-down photograph showcasing the "
            f"dish on a plate, placed on a plain metal background, highlighting the vibrant colors and textures "
            f"of the food. A single dish, no cutlery, sharp focus, no text.")
