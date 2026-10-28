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
        "cayenne pepper, paprika, garlic, onion, bell peppers, celery, filé powder, bay leaves, thyme and "
        "Cajun seasoning"),
    "Chinese (Cantonese - Most common style in US)": (
        "Cantonese/Guangdong/Yue (Chinese)",
        "ginger (jiang, 姜), green onions (cong, 葱), garlic (suan, 蒜), soy sauce (jiang you, 酱油), "
        "oyster sauce (hao you, 蚝油), fermented black beans (douchi, 豆豉), sesame oil (zhi ma you, 芝麻油), "
        "rice wine (mi jiu or Shaoxing jiu, 米酒 or 绍兴酒), white pepper (bai hu jiao, 白胡椒), and dried "
        "tangerine peel (chen pi, 陈皮)"),
    "Chinese (Hong Kong)": (
        "Hong Kong",
        "five-spice powder (五香粉; wǔ xiāng fěn), star anise (八角; bā jiǎo), ginger (薑; gīng), green onions "
        "or scallions (蔥; cōng), garlic (蒜; suàn), oyster sauce (蠔油; háo yóu), soy sauce (醬油; jiàng yóu), "
        "sesame oil (芝麻油; zhī ma yóu), fermented black beans (豆豉; dòu chǐ), and hoisin sauce "
        "(海鮮醬; hǎi xiān jiàng)"),
    "Chinese (Sichuan)": (
        "Sichuan (Chinese)",
        "Sichuan peppercorns (hua jiao, 花椒), dried chili peppers (gan la jiao, 干辣椒), broad bean chili paste "
        "(doubanjiang, 豆瓣酱), garlic (suan, 蒜), ginger (jiang, 姜), green onions or scallions (cong, 葱), "
        "pickled vegetables (pao cai, 泡菜), star anise (ba jiao, 八角), fermented black beans (douchi, 豆豉) "
        "and five-spice powder (wu xiang fen, 五香粉)"),
    "Chinese (Shandong)": (
        "Shandong/Lu (Chinese)",
        "green onions or scallions (cong, 葱), ginger (jiang, 姜), garlic (suan, 蒜), soy sauce (jiang you, 酱油), "
        "rice wine (mi jiu, 米酒), sesame oil (zhi ma you, 芝麻油), star anise (ba jiao, 八角), wood ear "
        "mushrooms (mu er, 木耳) and vinegar (cu, 醋)"),
    "Chinese (Jiangsu)": (
        "Huaiyang/Jianghuai (Chinese)",
        "ginger (jiang, 姜), green onions or scallions (cong, 葱), rice wine (mi jiu or Shaoxing jiu, 米酒 or "
        "绍兴酒), soy sauce (jiang you, 酱油), sugar (tang, 糖), vinegar (cu, 醋), sesame oil (zhi ma you, 芝麻油), "
        "red fermented tofu (nan ru or fu ru, 南乳 or 腐乳), dried bamboo shoots (gan sun, 干笋), and osmanthus "
        "syrup (gui hua tang, 桂花糖)"),
    "French": (
        "French",
        "thyme (thym), bay leaf (feuille de laurier), parsley (persil), tarragon (estragon), chervil (cerfeuil), "
        "rosemary (romarin), nutmeg (noix de muscade), Dijon mustard (moutarde de Dijon), garlic (ail) and "
        "shallots (échalotes)"),
    "Greek": (
        "Greek",
        "oregano (ρίγανη; rígani), olive oil (ελαιόλαδο; elaiólado), lemon (λεμόνι; lemóni), dill (άνηθος; "
        "ánithos), mint (δυόσμος; dyósmos), bay leaf (φύλλο δάφνης; fýllo dáfnis), cinnamon (κανέλα; kanéla), "
        "nutmeg (μοσχοκάρυδο; moschokárydo), fennel (μάραθος; márathos), and mastiha (μαστίχα; mastícha)"),
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
        "(prezzemolo), red pepper flakes (peperoncino), fennel seeds (semi di finocchio), anchovies (acciughe), "
        "and nutmeg (noce moscata)"),
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
        "kimchi (김치), red pepper flakes (gochugaru, 고추가루), red pepper paste (gochujang, 고추장), soybean "
        "paste (doenjang, 된장), soy sauce (ganjang, 간장), garlic (maneul, 마늘), ginger (saenggang, 생강), "
        "green onions or scallions (pa, 파), sesame oil (chamgireum, 참기름), sesame seeds (chamggae, 참깨), "
        "and perilla leaves (kkaennip, 깻잎)"),
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

    if name:
        style = (f"from {name} cuisine, keeping in mind that the audience for your recipe is an enthusiast and "
                 f"expert in {name} cuisine who would like you to prepare a dish with authentic {name} spices and "
                 f"flavors. Make sure the recipe you suggest includes such classic {name} spices and flavors as "
                 f"{flavors}")
        staples_extra = f", as well as such classic {name} spices and flavors as {flavors},"
    else:
        style = "from any cuisine or culture"
        staples_extra = ","

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
Respond as if you were an acclaimed popular food blogger, renowned for your knowledge of cooking fundamentals,
your flair for modern creativity, and your ability to break things down into straightforward steps that anyone
can follow. Write in plain text and Markdown only: no emojis.

You are being asked to prepare a recipe for {audience_text} {dish} They will provide you with a list of
ingredients to use in the recipe. If you are not given any food items to use, please decline to generate a recipe.

{restriction_text}

Please suggest a recipe {style}. Your recipe may include other pantry staples such as {staples}{staples_extra}
but otherwise the primary ingredients for the recipe should come ONLY from the ingredients wrapped in triple
quotes in the user's first message.

Please keep in mind that you cannot include any non-food or harmful ingredients in your recipe. If you are asked
to provide a recipe using such ingredients, you will decline, or explain that you will provide a recipe that omits
the non-food or dangerous ingredients. You do not need to use every ingredient provided, but you should do your
best to use as many as possible.

Be precise, like a serious cookbook: exact quantities (US and metric), pan sizes, heat levels, temperatures,
timings, and doneness cues (internal temperatures for meat, poultry and fish). Explain the "why" behind a
technique when it matters.

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
        'Introduce yourself and the dish to your fellow foodies first, but when you get to the recipe itself, '
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
