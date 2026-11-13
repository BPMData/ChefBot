"""Writes docs/research/<continent>.md: the research prompt from docs/CUISINE_TREE.md, filled in per continent.

Run from the repo root: .venv/bin/python tools/make_research_prompts.py [slug ...]
With slugs (e.g. additions-europe), writes only those; the prompts already run are kept as they were sent.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from chefbot import cuisines  # noqa: E402

ANY_COUNTRY = (
    '"Any" means the internationally recognized version of that country\'s food: what people outside the '
    "country think of when they think of it{example}. Research it as a node of its own. Say where that outside "
    "view is a cliché, a stereotype, or an export version that differs from home cooking, but describe the "
    "outside view itself accurately.")

CONTINENTS = {   # slug: (taxonomy heading, "Any" rule, the app's current cuisines from this continent)
    "americas": ("The Americas",
                 '"Any" OPTIONS: United States, Mexico and the Caribbean each have an "Any" option; no other node '
                 "does. " + ANY_COUNTRY.format(example=" (for the United States, American food as people in Asia "
                                                       "and Europe picture it)")
                 + " Caribbean > Any covers several countries: describe the shared picture outsiders have, and "
                   "note in pitfalls where islands differ and would object to being lumped together.",
                 ["American", "American (Cajun)", "American (Creole)", "Mexican", "Peruvian"]),
    "asia": ("Asia",
             '"Any" OPTIONS: China, Japan and India each have an "Any" option; no other node does. '
             + ANY_COUNTRY.format(example=""),
             ["Chinese (Cantonese - Most common style in US)", "Chinese (Hong Kong)", "Chinese (Sichuan)",
              "Chinese (Shandong)", "Chinese (Jiangsu)", "Japanese (Kansai)", "Japanese (Kanto)", "North Indian",
              "South Indian", "Korean", "Thai", "Vietnamese"]),
    "europe": ("Europe",
               '"Any" OPTIONS: Italy has an "Any" option; no other node does. ' + ANY_COUNTRY.format(example=""),
               ["French", "Greek", "Italian", "Spanish"]),
    "near-east": ("Near East", '"Any" OPTIONS: none on this continent. Every node is a single cuisine.',
                  ["Turkish"]),
    "africa": ("Africa", '"Any" OPTIONS: none on this continent. Every node is a single cuisine.', []),
    # Cuisines added after the first five runs, researched together. Their ids are fixed so the build script
    # can place them: tunisian and algerian go under Africa, afghan and pakistani under Asia.
    "additions": ("Africa", '"Any" OPTIONS: none. Each node is a single cuisine.', [],
                  "Four new nodes, each a single cuisine. Use exactly these ids: tunisian, algerian (both in "
                  "Africa), afghan, pakistani (both in Asia). Moroccan, Egyptian, North Indian and Persian are "
                  "already researched. Say clearly how Tunisian and Algerian differ from each other and from "
                  "Moroccan cooking, and give harissa its full due (what goes in it, regional versions, how it is "
                  "used). Say how Afghan and Pakistani differ from North Indian, Persian and each other, describe "
                  "what they share (especially Pashtun cooking on both sides of the border), and say in the "
                  "summary whether a recipe app should treat Afghan and Pakistani as one combined node or two, "
                  "and why."),
    # Second batch (2026-11-13), two runs. Results go to results/additions_europe.json and
    # results/additions_americas.json. The five Central European ids replace the old central_european node.
    "additions-europe": ("Europe", '"Any" OPTIONS: none. Each node is a single cuisine.', [],
                         "Ten new nodes in Europe, each a single cuisine. Use exactly these ids: german, austrian, "
                         "hungarian, polish, czech, portuguese, british, irish, nordic, georgian. The first five "
                         "replace one combined \"Central European\" node, so above all say clearly how each differs "
                         "from the other four (seasonings, fats, starches, signature techniques), and where they "
                         "truly share a tradition (Habsburg court cooking, Jewish Ashkenazi cooking, dumplings, "
                         "sauerkraut), say so instead of inventing differences. German: say how much the south "
                         "(Bavaria, Swabia) differs from the north, and what a recipe app should treat as the "
                         "default. Portuguese: say how it differs from Spanish, which is already researched. "
                         "British and Irish are separate nodes: say what is genuinely Irish rather than British, "
                         "and note in British where Scottish and Welsh cooking differ from English. Nordic covers "
                         "Denmark, Norway, Sweden, Finland and Iceland: say in the summary whether Finland fits "
                         "or should be its own node, and keep New Nordic restaurant cooking apart from home "
                         "cooking. Georgian: describe what sets it apart from Russian, Turkish and Persian "
                         "cooking (all already researched), and say in the summary whether an app should file it "
                         "under Europe or the Near East."),
    "additions-americas": ("The Americas", '"Any" OPTIONS: none. Each node is a single cuisine.', [],
                           "Four new nodes in the Americas, each a single cuisine. Use exactly these ids: "
                           "quebecois (Quebec, Canada), us_new_mexican and us_hawaiian (both regional cuisines "
                           "within the United States), colombian. Tex-Mex, Mexican (Northern & Baja, Central & "
                           "Oaxacan, Yucatan), Peruvian and Southern & Soul are already researched. New Mexican: "
                           "say clearly how it differs from Tex-Mex and from Mexican cooking, give New Mexico "
                           "chile (red and green, Hatch) its full due, and explain \"Christmas\". Hawaiian: "
                           "cover local food as people in Hawaii eat it today (plate lunch, poke, Japanese, "
                           "Chinese, Filipino, Korean and Portuguese influences) and Native Hawaiian food, say "
                           "which the app should default to, and flag tourist-menu clichés (pineapple on "
                           "everything). Quebecois: separate everyday home cooking from cabane a sucre and "
                           "restaurant dishes, and say how it differs from French cooking. Colombian: say how "
                           "much the regions differ (Andean, Caribbean coast, Pacific coast, Llanos) and what "
                           "a recipe app should treat as the default."),
}


def existing_entries(labels: list[str]) -> str:
    """The app's entries for these old cuisine labels, now read from the cuisine tree."""
    if not labels:
        return "(None: the app has no existing entries for these cuisines yet. Skip the fact-check.)"
    out = []
    for label in labels:
        node = cuisines.get(cuisines.LEGACY_IDS[label])
        out.append(f"{label}\n  Description: {node['about']}\n  Classic flavors: {', '.join(node['flavors'])}")
        if node.get("sweet_only"):
            out.append(f"  Dessert-only flavors: {', '.join(node['sweet_only'])}")
        if node.get("signature_ingredients"):
            out.append(f"  Signature ingredients: {', '.join(node['signature_ingredients'])}")
    return "\n".join(out)


def main():
    doc = (ROOT / "docs/CUISINE_TREE.md").read_text()
    template = doc.split("## Research prompt", 1)[1].split("```\n", 1)[1].split("\n```", 1)[0]
    taxonomy = doc.split("## Taxonomy\n\n", 1)[1].split("\n\n## ", 1)[0]
    lines = [re.sub(r"\s*\n\s*", " ", part).strip() for part in re.split(r"\n(?=- \*\*)", taxonomy)]
    out_dir = ROOT / "docs/research"
    out_dir.mkdir(exist_ok=True)
    only = sys.argv[1:]
    for slug, (heading, any_rule, labels, *scope) in CONTINENTS.items():
        if only and slug not in only:
            continue
        part = scope[0] if scope else next(line for line in lines if line.startswith(f"- **{heading}:**"))
        part = part.replace("**", "")
        body = (template.replace("[TAXONOMY]", part).replace("[ANY RULE]", any_rule)
                .replace("[EXISTING]", existing_entries(labels)))
        assert not any(tag in body for tag in ("[TAXONOMY]", "[ANY RULE]", "[EXISTING]"))
        (out_dir / f"{slug}.md").write_text(body + "\n")
        print(f"wrote docs/research/{slug}.md")


if __name__ == "__main__":
    main()
