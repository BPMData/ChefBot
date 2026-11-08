"""Writes docs/research/<continent>.md: the research prompt from docs/CUISINE_TREE.md, filled in per continent.

Run from the repo root: .venv/bin/python tools/make_research_prompts.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from chefbot import prompts  # noqa: E402

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
    "near-east": ("Near & Middle East", '"Any" OPTIONS: none on this continent. Every node is a single cuisine.',
                  ["Turkish"]),
    "africa": ("Africa", '"Any" OPTIONS: none on this continent. Every node is a single cuisine.', []),
}


def existing_entries(labels: list[str]) -> str:
    if not labels:
        return "(None: the app has no cuisines from this continent yet. Skip the fact-check.)"
    out = []
    for label in labels:
        _, flavors = prompts.CUISINES[label]
        out.append(f"{label}\n  Description: {prompts.CUISINE_ABOUT[label]}\n  Classic flavors: {flavors}")
        if label in prompts.SWEET_FLAVORS:
            out.append(f"  Dessert-only flavors: {prompts.SWEET_FLAVORS[label]}")
        if label in prompts.SIGNATURE_INGREDIENTS:
            out.append(f"  Signature ingredients: {prompts.SIGNATURE_INGREDIENTS[label]}")
    return "\n".join(out)


def main():
    doc = (ROOT / "docs/CUISINE_TREE.md").read_text()
    template = doc.split("## Research prompt", 1)[1].split("```\n", 1)[1].split("\n```", 1)[0]
    taxonomy = doc.split("## Taxonomy\n\n", 1)[1].split("\n\n## ", 1)[0]
    lines = [re.sub(r"\s*\n\s*", " ", part).strip() for part in re.split(r"\n(?=- \*\*)", taxonomy)]
    out_dir = ROOT / "docs/research"
    out_dir.mkdir(exist_ok=True)
    for slug, (heading, any_rule, labels) in CONTINENTS.items():
        part = next(line for line in lines if line.startswith(f"- **{heading}:**"))
        part = part.replace("**", "")
        body = (template.replace("[TAXONOMY]", part).replace("[ANY RULE]", any_rule)
                .replace("[EXISTING]", existing_entries(labels)))
        assert not any(tag in body for tag in ("[TAXONOMY]", "[ANY RULE]", "[EXISTING]"))
        (out_dir / f"{slug}.md").write_text(body + "\n")
        print(f"wrote docs/research/{slug}.md")


if __name__ == "__main__":
    main()
