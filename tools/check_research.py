"""Checks a deep research report and saves its JSON to docs/research/results/<continent>.json.

Usage, from the repo root:
    .venv/bin/python tools/check_research.py <continent> <report.md or data.json>
For example: tools/check_research.py europe ~/Downloads/deep-research-report.md
The report is also copied to docs/research/results/raw/<continent>.md.
"""
import json
import re
import shutil
import sys
from pathlib import Path

FIELDS = ["id", "label", "subtitle", "about", "flavors", "sweet_only", "signature_ingredients", "pantry_assumed",
          "techniques", "shortcuts", "allergen_notes", "pitfalls", "sources"]
MAY_BE_EMPTY = {"sweet_only", "signature_ingredients", "pantry_assumed"}
RESULTS = Path(__file__).resolve().parent.parent / "docs/research/results"


def normalize(node: dict):
    """One shape for every report: list fields are lists of plain strings."""
    for field in FIELDS[4:12]:
        value = node.get(field)
        if isinstance(value, str):
            value = [value] if value else []
        items = []
        for item in value or []:
            if isinstance(item, dict) and "ingredient" in item:
                item = f"{item['ingredient']} (substitute: {item.get('substitute', 'none')})"
            elif isinstance(item, dict):
                item = ". ".join(f"{k.replace('_', ' ')}: {v}" for k, v in item.items())
            items.append(item)
        node[field] = items


def main(continent: str, report: str):
    text = Path(report).read_text()
    if report.endswith(".json"):          # the JSON on its own, without the narrative report
        data = json.loads(text)
    else:
        found = re.search(r"```json\n(.*?)(\n```|\Z)", text, re.S)
        if not found:
            sys.exit("No ```json block in the report: rerun the research (the JSON is required).")
        data = json.loads(found.group(1))
    problems = 0
    for node in data:
        missing = [f for f in FIELDS if f not in node]
        empty = [f for f in FIELDS if f in node and not node[f] and f not in MAY_BE_EMPTY]
        urls = sum("http" in json.dumps(s) for s in node.get("sources", []))
        flag = []
        if missing:
            flag.append(f"missing {missing}")
        if empty:
            flag.append(f"empty {empty}")
        if len(node.get("label", "")) > 20:
            flag.append("label over 20 characters")
        if not urls:
            flag.append("no source URLs")
        problems += bool(flag)
        print(f"{node.get('id', '?'):32} flavors={len(node.get('flavors', [])):2} sources={urls} url "
              f"{'; '.join(flag)}")
        normalize(node)
    words = json.dumps(data).lower()
    print(f"\n{len(data)} nodes, {problems} with problems; 'never' x{words.count('never')}, "
          f"'always' x{words.count('always')} (check these aren't false hard rules)")
    (RESULTS / f"{continent}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    (RESULTS / "raw").mkdir(parents=True, exist_ok=True)
    raw = RESULTS / "raw" / f"{continent}{Path(report).suffix}"
    if Path(report).resolve() != raw.resolve():
        shutil.copyfile(report, raw)
    print(f"saved docs/research/results/{continent}.json and raw/{continent}.md")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
