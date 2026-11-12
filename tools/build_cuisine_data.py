"""Builds src/chefbot/cuisines/<continent>.json from docs/research/results/*.json and tools/cuisine_overrides.json.

Run from the repo root:
    .venv/bin/python tools/build_cuisine_data.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "docs" / "research" / "results"
OVERRIDES_PATH = ROOT / "tools" / "cuisine_overrides.json"
OUT_DIR = ROOT / "src" / "chefbot" / "cuisines"

ORGANIZATIONAL_IDS = {"the_americas", "asia", "europe", "eight_great_cuisines"}

CONTINENT_SPECS = [
    ("americas", "The Americas", "North, Central & South America, Caribbean",
     "Cuisines of North, Central and South America and the Caribbean."),
    ("asia", "Asia", "East, South, Southeast & Central Asia",
     "Cuisines of East, South, Southeast and Central Asia."),
    ("europe", "Europe", "Mediterranean, Western, Central & Eastern Europe",
     "Cuisines of Mediterranean, Western, Central and Eastern Europe."),
    ("near_east", "Near East", "Levant, Iran & Anatolia",
     "Cuisines of the Levant, Iran and Anatolia."),
    ("africa", "Africa", "North, West & East Africa",
     "Cuisines of North, West and East Africa."),
]

# Country branch nodes and the prefix/set of child ids belonging to each.
COUNTRY_CHILDREN: dict[str, list[str]] = {
    "united_states": [
        "us_any", "us_cajun", "us_creole", "us_southern_soul", "us_tex_mex", "us_new_england_seafood",
    ],
    "mexico": [
        "mx_any", "mx_northern_baja", "mx_central_oaxacan", "mx_yucatan",
    ],
    "caribbean": [
        "caribbean_any", "caribbean_cuban", "caribbean_puerto_rican", "caribbean_jamaican",
    ],
    "china": [
        "china_any", "sichuan", "hunan", "cantonese", "shandong", "jiangsu", "zhejiang", "fujian", "anhui",
    ],
    "japan": [
        "japan_any", "kanto", "kansai",
    ],
    "india": [
        "india_any", "north_india", "south_india",
    ],
    "italy": [
        "italy_any", "northern_italy", "southern_sicilian_italy",
    ],
}

ADDITION_CONTINENT = {
    "tunisian": "africa",
    "algerian": "africa",
    "afghan": "asia",
    "pakistani": "asia",
}

PROMPT_NAMES: dict[str, str] = {
    "us_any": "American",
    "us_cajun": "Cajun",
    "us_creole": "New Orleans Creole",
    "us_southern_soul": "Southern and Soul Food (American)",
    "us_tex_mex": "Tex-Mex",
    "us_new_england_seafood": "New England Seafood",
    "mx_any": "Mexican",
    "mx_northern_baja": "Northern Mexican and Baja",
    "mx_central_oaxacan": "Central Mexican and Oaxacan",
    "mx_yucatan": "Yucatecan (Mexican)",
    "caribbean_any": "Caribbean",
    "caribbean_cuban": "Cuban",
    "caribbean_puerto_rican": "Puerto Rican",
    "caribbean_jamaican": "Jamaican",
    "brazilian": "Brazilian",
    "peruvian": "Peruvian",
    "argentinian": "Argentinian",
    "china_any": "Chinese",
    "sichuan": "Sichuan (Chinese)",
    "hunan": "Hunan (Chinese)",
    "cantonese": "Cantonese (Chinese)",
    "shandong": "Shandong (Chinese)",
    "jiangsu": "Jiangsu (Chinese)",
    "zhejiang": "Zhejiang (Chinese)",
    "fujian": "Fujian (Chinese)",
    "anhui": "Anhui (Chinese)",
    "japan_any": "Japanese",
    "kanto": "Kanto (Japanese)",
    "kansai": "Kansai (Japanese)",
    "india_any": "Indian",
    "north_india": "North Indian",
    "south_india": "South Indian",
    "korean": "Korean",
    "thai": "Thai",
    "vietnamese": "Vietnamese",
    "filipino": "Filipino",
    "indonesian": "Indonesian",
    "malaysian_singaporean": "Malaysian and Singaporean",
    "afghan": "Afghan",
    "pakistani": "Pakistani",
    "italy_any": "Italian",
    "northern_italy": "Northern Italian",
    "southern_sicilian_italy": "Southern Italian and Sicilian",
    "french": "French",
    "spanish": "Spanish",
    "greek": "Greek",
    "central_european": "Central European",
    "russian": "Russian",
    "palestinian_levantine": "Palestinian and Levantine",
    "persian": "Persian",
    "turkish": "Turkish",
    "moroccan_north_african": "Moroccan",
    "tunisian": "Tunisian",
    "algerian": "Algerian",
    "ethiopian": "Ethiopian",
    "egyptian": "Egyptian",
    "nigerian": "Nigerian",
    "senegalese": "Senegalese",
}

ENGLISH_PRIMARY_NODES = {
    "united_states", "us_any", "us_cajun", "us_creole", "us_southern_soul", "us_new_england_seafood",
    "caribbean", "caribbean_any", "caribbean_jamaican",
}

PROPER_PREFIXES = (
    "Mexican", "Yucatecan", "Peruvian", "Jamaican", "Louisiana", "Worcestershire", "Old Bay",
    "Sichuan", "Pixian", "Shaoxing", "Zhenjiang", "Longjing", "Shandong", "Thai", "Vietnamese",
    "Dijon", "Pimentón", "Nigerian", "American", "Parmigiano", "Carnaroli", "Arborio", "Taleggio",
    "Sicilian", "Spanish", "Greek", "Hungarian", "Central European", "Persian", "Turkish",
    "Ethiopian", "Moroccan", "Hunan", "Zhejiang", "Chinese", "Maine", "Scotch", "Piper", "Lippia",
    "California", "Kyoto", "Italian", "Southeast Asian", "Indian", "Korean",
)


def _has_non_latin(text: str) -> bool:
    return any(
        ord(ch) > 0x024F and not (0x1E00 <= ord(ch) <= 0x1EFF) and not (0x2000 <= ord(ch) <= 0x206F)
        for ch in text
    )


def _lower_first(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    for p in PROPER_PREFIXES:
        if text.startswith(p):
            return text
    if len(text) > 1 and text[0].isupper() and text[1].islower():
        return text[0].lower() + text[1:]
    return text


def _swap_roman_and_script(inner: str) -> str:
    """Turn 'goeng1, 薑' or 'gochutgaru/gochugaru, 고춧가루' into '薑, goeng1' or '고춧가루, gochutgaru'."""
    if "," not in inner:
        return inner.strip()
    parts = [p.strip() for p in inner.split(",", 1)]
    if len(parts) == 2 and not _has_non_latin(parts[0]) and _has_non_latin(parts[1]):
        rom, native = parts
        if "/" in rom:
            rom = rom.split("/")[0].strip()
        if " / " in native:
            # e.g. South India: "kadugu, கடுகு / āvalu, ఆవాలు"
            sub_parts = [s.strip() for s in inner.split("/")]
            rebuilt = []
            for s in sub_parts:
                if "," in s:
                    r, n = [x.strip() for x in s.split(",", 1)]
                    if not _has_non_latin(r) and _has_non_latin(n):
                        rebuilt.append(f"{n}, {r}")
                    else:
                        rebuilt.append(s)
                else:
                    rebuilt.append(s)
            return " / ".join(rebuilt)
        return f"{native}, {rom}"
    return inner.strip()


def normalize_flavor(raw: str, node_id: str) -> str:
    """Normalize any research flavor string into 'English (native, romanization)' or 'English'."""
    s = raw.strip()

    # Case 1: 3-part 'native — romanization — English' (Americas, Near East)
    if s.count(" — ") == 2:
        native, rom, eng = [p.strip() for p in s.split(" — ")]
        # Strip trailing '; explanation' from Near East English part
        eng = eng.split(";")[0].strip()
        if " or, by extension," in eng:
            eng = eng.split(" or, by extension,")[0].strip()
        if eng == "za'atar herb":
            eng = "za'atar"
        if eng.endswith(" in many sweets/drinks"):
            eng = eng[: -len(" in many sweets/drinks")].strip()
        # Strip long trailing qualifiers after comma in flavor names
        if "," in eng:
            head, tail = eng.split(",", 1)
            if any(w in tail for w in ("especially", "mainly", "particularly", "commonly", "used", "overrepresented",
                                       "regionally", "savory", "ranging", "often", "though", "including", "a ")):
                eng = head.strip()
        eng = _lower_first(eng)
        if node_id in ("mexico",) and native == "orégano" and eng == "Mexican oregano":
            return "Mexican oregano (orégano)"
        if node_id in ENGLISH_PRIMARY_NODES:
            # In English-primary nodes, if native == rom and has no slash, native is the specific English name
            # (e.g. 'ketchup', 'barbecue sauce', 'Louisiana hot sauce', 'Worcestershire sauce').
            if native == rom and "/" not in native:
                return _lower_first(native)
            return eng
        # If native has slash with English equivalent, keep the non-English side
        if "/" in native:
            slash_parts = [p.strip() for p in native.split("/")]
            non_eng = [p for p in slash_parts if p.lower() != eng.lower()]
            native = non_eng[0] if non_eng else slash_parts[0]
        if "/" in rom:
            rom = native
        if native.lower() == eng.lower() or native.lower() in eng.lower():
            return eng
        if _has_non_latin(native) and rom and rom != native:
            return f"{eng} ({native}, {rom})"
        if rom and rom != native and not _has_non_latin(native):
            return f"{eng} ({rom})"
        return f"{eng} ({native})"

    # Case 2: 2-part 'left — right' (Europe, Africa, or Asia with trailing note)
    if " — " in s:
        left, right = [p.strip() for p in s.split(" — ", 1)]

        # Subcase 2a: Africa style 'كمون (kammun; ... romanization: kammun) — cumin'
        if "(" in left and ")" in left and not left.startswith(("soy ", "osmanthus", "white ", "dried ", "Longjing",
                                                                 "pandan", "kinako", "matcha", "rose ", "kewra",
                                                                 "saffron", "cardamom", "ube", "palm ", "coconut ")):
            m = re.match(r"^([^()]+)\(([^()]+)\)$", left)
            if m:
                native = m.group(1).strip()
                paren = m.group(2).strip()
                eng = right.split(";")[0].strip()
                if "," in eng:
                    head, tail = eng.split(",", 1)
                    if any(w in tail for w in ("mainly", "also", "used", "especially", "often", "particularly",
                                               "related", "literally", "category", "associated")):
                        eng = head.strip()
                eng = _lower_first(eng)
                if " / " in native:
                    native = native.split(" / ")[0].strip()
                # Extract romanization
                rom = ""
                if "romanization:" in paren:
                    rom = paren.split("romanization:")[-1].strip().split("/")[0].strip()
                elif ";" in paren:
                    rom = paren.split(";")[0].strip().split("/")[0].strip()
                else:
                    rom = paren.split("/")[0].strip()
                if _has_non_latin(native):
                    if rom and rom.lower() != eng.lower():
                        return f"{eng} ({native}, {rom})"
                    return f"{eng} ({native})"
                if "English trade name" in paren:
                    return _lower_first(native)
                if native.lower() == eng.lower():
                    return eng
                return f"{eng} ({native})"

        # Subcase 2b: 'fleur d'oranger / orange-blossom water — used mainly in sweet drinks...'
        if " / " in left and "(" not in left:
            parts = [p.strip() for p in left.split(" / ", 1)]
            return f"{_lower_first(parts[1])} ({parts[0]})"

        # Subcase 2c: Asia style with trailing note 'osmanthus (guìhuā, 桂花) — mainly sweets...'
        if "(" in left and left.endswith(")"):
            s = left
            # Fall through to Case 3 below

        # Subcase 2d: Europe style 'garlic — aglio (aglio)' or 'oregano — ρίγανη (rígani)'
        else:
            eng = _lower_first(left)
            # Strip trailing ', especially ...' after closing paren
            right_main = re.sub(r"\)\s*,.*$", ")", right).strip()
            if node_id == "central_european":
                # 'DE Kümmel (Kümmel), CS kmín (kmín), HU kömény (kömény), PL kminek (kminek)'
                words = re.findall(r"\(([^()]+)\)", right_main)
                if not words:
                    words = [re.sub(r"^[A-Z]{2}\s+", "", p.strip()) for p in right_main.split(";")[0].split(",")]
                dedup = []
                for w in words:
                    if w not in dedup and w.lower() != eng.lower():
                        dedup.append(w)
                return f"{eng} ({', '.join(dedup)})" if dedup else eng
            m = re.match(r"^([^()]+)\(([^()]+)\)$", right_main)
            if m:
                nat, rom = m.group(1).strip(), m.group(2).strip()
                if nat.lower() == rom.lower():
                    return eng if nat.lower() == eng.lower() else f"{eng} ({nat})"
                return f"{eng} ({nat}, {rom})"
            right_clean = right_main.split(",")[0].split(";")[0].strip()
            if right_clean.lower() == eng.lower():
                return eng
            return f"{eng} ({right_clean})"

    # Case 3: 'English (romanization, native)' or 'English (native; romanization)' (Asia, Additions)
    # Strip trailing note after closing paren like '), mainly sweets...'
    s = re.sub(r"\)\s*[,—-]\s*.*$", ")", s).strip()
    m = re.match(r"^([^()]+)\(([^()]+)\)$", s)
    if m:
        eng = _lower_first(m.group(1).strip())
        inner = m.group(2).strip()
        if ";" in inner:
            # Additions format: 'هريسة; harīsa'
            parts = [p.strip() for p in inner.split(";", 1)]
            nat, rom = parts[0], parts[1]
            if nat.lower() == rom.lower():
                return eng if nat.lower() == eng.lower() else f"{eng} ({nat})"
            return f"{eng} ({nat}, {rom})"
        inner_swapped = _swap_roman_and_script(inner)
        # Drop duplicate romanization when it equals English, e.g. 'dashi (だし, dashi)' -> 'dashi (だし)'
        if "," in inner_swapped and " / " not in inner_swapped:
            nat, rom = [p.strip() for p in inner_swapped.split(",", 1)]
            if rom.lower() == eng.lower():
                inner_swapped = nat
        if inner_swapped.lower() == eng.lower():
            return eng
        return f"{eng} ({inner_swapped})"

    return _lower_first(s)


def normalize_signature_ingredient(raw: str) -> str:
    """Normalize signature_ingredients to 'item (substitute: ...)' with English first."""
    s = raw.strip()
    sub = "none"
    if "(substitute:" in s:
        item_part, sub_part = s.split("(substitute:", 1)
        sub = sub_part.rstrip(")").strip()
    elif " — substitute:" in s:
        item_part, sub_part = s.split(" — substitute:", 1)
        sub = sub_part.strip()
    else:
        item_part = s

    item_part = item_part.strip()
    # Near East: 'مفتول — maftūl — hand-rolled Palestinian wheat granules'
    if item_part.count(" — ") == 2:
        nat, rom, desc = [p.strip() for p in item_part.split(" — ")]
        if nat.lower() == rom.lower():
            item_part = f"{_lower_first(desc)} ({nat})"
        else:
            item_part = f"{_lower_first(desc)} ({nat}, {rom})"
    elif " — " in item_part:
        # Russian: 'tvorog — творог (tvorog)'
        left, right = [p.strip() for p in item_part.split(" — ", 1)]
        m = re.match(r"^([^()]+)\(([^()]+)\)$", right)
        if m:
            nat, rom = m.group(1).strip(), m.group(2).strip()
            if left.lower() == rom.lower() or nat.lower() == rom.lower():
                item_part = f"{_lower_first(left)} ({nat})"
            else:
                item_part = f"{_lower_first(left)} ({nat}, {rom})"
        else:
            item_part = f"{_lower_first(left)} ({right})"
    else:
        # Swap '(rom, native)' in Asia signature ingredients if present
        m = re.match(r"^([^()]+)\(([^()]+)\)$", item_part)
        if m:
            eng = _lower_first(m.group(1).strip())
            inner = _swap_roman_and_script(m.group(2).strip())
            item_part = f"{eng} ({inner})"
        else:
            item_part = _lower_first(item_part)

    sub = _lower_first(sub)
    return f"{item_part} (substitute: {sub})"


def normalize_tips(shortcuts: list[str]) -> list[str]:
    """Turn research shortcuts into clean tips lines without brand names."""
    tips: list[str] = []
    for raw in shortcuts:
        s = raw.strip()
        if not s:
            continue
        # Africa dict-normalized format: 'product: X. usually contains: Y. swap by weight: Z.. salt g: W'
        if s.startswith("product: "):
            m = re.match(
                r"^product:\s*(.*?)\.\s*usually contains:\s*(.*?)\.\s*swap by weight:\s*(.*?)\.\s*salt g:\s*(.*)$",
                s,
            )
            if m:
                prod, contains, swap, salt = [g.strip().rstrip(".") for g in m.groups()]
                prod_cap = prod[0].upper() + prod[1:] if prod else prod
                s = f"{prod_cap} (usually {contains}): {_lower_first(swap)}. Salt: {_lower_first(salt)}."
        elif s.startswith("name: "):
            m = re.match(r"^name:\s*(.*?)\.\s*contains:\s*(.*?)\.\s*swap rule:\s*(.*)$", s)
            if m:
                prod, contains, swap = [g.strip().rstrip(".") for g in m.groups()]
                prod_cap = prod[0].upper() + prod[1:] if prod else prod
                s = f"{prod_cap} ({_lower_first(contains)}): {swap}."
        # Scrub any brand names if not already overridden
        s = re.sub(r"\bLe Phare du Cap Bon\b", "a typical packaged", s)
        s = re.sub(r"\bShan\b", "packaged", s)
        s = s.replace("..", ".")
        tips.append(s)
    return tips


def normalize_pitfalls(pitfalls: list[str]) -> list[str]:
    """Split multi-sentence pitfall paragraphs into short single-sentence items."""
    out: list[str] = []
    for raw in pitfalls:
        text = raw.strip()
        if not text:
            continue
        # Split on sentence boundaries '. ' followed by an uppercase letter or quote
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z'\"])", text)
        for p in parts:
            p = p.strip()
            if p:
                out.append(p)
    return out


def apply_overrides(node: dict, ov: dict) -> None:
    """Apply tools/cuisine_overrides.json entries to a normalized node."""
    for field in ("label", "subtitle", "about", "prompt_name", "flavors", "sweet_only",
                  "signature_ingredients", "tips", "pitfalls", "avoid"):
        if field in ov:
            node[field] = list(ov[field]) if isinstance(ov[field], list) else ov[field]

    for bad in ov.get("remove_flavors", []):
        bad_l = bad.lower()
        node["flavors"] = [f for f in node["flavors"] if bad_l not in f.lower()]

    for bad in ov.get("remove_signature_ingredients", []):
        bad_l = bad.lower()
        node["signature_ingredients"] = [s for s in node["signature_ingredients"] if bad_l not in s.lower()]

    for extra in ov.get("add_flavors", []):
        if all(extra.lower() != f.lower() for f in node["flavors"]):
            node["flavors"].append(extra)

    if "prepend_tips" in ov:
        existing = [t for t in node["tips"] if t not in ov["prepend_tips"]]
        node["tips"] = list(ov["prepend_tips"]) + existing

    if "append_tips" in ov:
        for t in ov["append_tips"]:
            if t not in node["tips"]:
                node["tips"].append(t)

    # Also ensure anything in avoid is never in flavors or signature_ingredients
    for avoided in node["avoid"]:
        root_word = avoided.split()[0].lower()
        node["flavors"] = [f for f in node["flavors"] if root_word not in f.lower()]
        node["signature_ingredients"] = [s for s in node["signature_ingredients"] if root_word not in s.lower()]


def build_node(raw: dict, kind: str, children: list[str], overrides: dict[str, dict]) -> dict:
    nid = raw["id"]
    selectable = kind in ("cuisine", "any")
    label = "Any" if kind == "any" else raw["label"].strip()
    node = {
        "id": nid,
        "kind": kind,
        "label": label,
        "subtitle": raw["subtitle"].strip(),
        "about": raw["about"].strip(),
        "prompt_name": PROMPT_NAMES.get(nid, raw["label"].strip()) if selectable else "",
        "flavors": [normalize_flavor(f, nid) for f in raw.get("flavors", [])],
        "sweet_only": [normalize_flavor(f, nid) for f in raw.get("sweet_only", [])],
        "signature_ingredients": [normalize_signature_ingredient(s) for s in raw.get("signature_ingredients", [])],
        "tips": normalize_tips(raw.get("shortcuts", [])),
        "pitfalls": normalize_pitfalls(raw.get("pitfalls", [])),
        "avoid": [],
        "children": list(children),
    }
    if nid in overrides:
        apply_overrides(node, overrides[nid])
    return node


def build_all() -> dict[str, list[dict]]:
    overrides: dict[str, dict] = {}
    if OVERRIDES_PATH.exists():
        overrides = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))

    # Load additions.json if present
    additions_by_continent: dict[str, list[dict]] = {"asia": [], "africa": []}
    additions_path = RESULTS_DIR / "additions.json"
    if additions_path.exists():
        for item in json.loads(additions_path.read_text(encoding="utf-8")):
            target = ADDITION_CONTINENT.get(item["id"])
            if target:
                additions_by_continent.setdefault(target, []).append(item)

    all_child_ids_under_countries = {cid for kids in COUNTRY_CHILDREN.values() for cid in kids}
    output: dict[str, list[dict]] = {}

    for cont_id, cont_label, cont_subtitle, cont_about in CONTINENT_SPECS:
        raw_list = json.loads((RESULTS_DIR / f"{cont_id}.json").read_text(encoding="utf-8"))
        # Merge additions for this continent
        extra_nodes = additions_by_continent.get(cont_id, [])
        if cont_id == "africa" and extra_nodes:
            # Place tunisian and algerian right after moroccan_north_african per taxonomy
            merged = []
            inserted = False
            for r in raw_list:
                merged.append(r)
                if r["id"] == "moroccan_north_african":
                    merged.extend(extra_nodes)
                    inserted = True
            if not inserted:
                merged.extend(extra_nodes)
            raw_list = merged
        elif extra_nodes:
            raw_list = raw_list + extra_nodes

        # Filter organizational nodes
        kept_raw = [r for r in raw_list if r["id"] not in ORGANIZATIONAL_IDS]
        raw_by_id = {r["id"]: r for r in kept_raw}

        # Determine direct children of this continent
        continent_children: list[str] = []
        for r in kept_raw:
            rid = r["id"]
            if rid not in all_child_ids_under_countries:
                continent_children.append(rid)

        continent_node = {
            "id": cont_id,
            "kind": "continent",
            "label": cont_label,
            "subtitle": cont_subtitle,
            "about": cont_about,
            "prompt_name": "",
            "flavors": [],
            "sweet_only": [],
            "signature_ingredients": [],
            "tips": [],
            "pitfalls": [],
            "avoid": [],
            "children": continent_children,
        }
        if cont_id in overrides:
            apply_overrides(continent_node, overrides[cont_id])

        nodes: list[dict] = [continent_node]
        # Add nodes in clean tree order: each top-level child of the continent, followed by its children if a country
        for top_id in continent_children:
            raw_node = raw_by_id[top_id]
            if top_id in COUNTRY_CHILDREN:
                # Order children: *_any first, then the rest in research order
                research_kids = [r["id"] for r in kept_raw if r["id"] in COUNTRY_CHILDREN[top_id]]
                any_kids = [cid for cid in research_kids if cid.endswith("_any")]
                other_kids = [cid for cid in research_kids if not cid.endswith("_any")]
                ordered_kids = any_kids + other_kids
                nodes.append(build_node(raw_node, "country", ordered_kids, overrides))
                for cid in ordered_kids:
                    ckind = "any" if cid.endswith("_any") else "cuisine"
                    nodes.append(build_node(raw_by_id[cid], ckind, [], overrides))
            else:
                ckind = "any" if top_id.endswith("_any") else "cuisine"
                nodes.append(build_node(raw_node, ckind, [], overrides))

        output[cont_id] = nodes

    return output


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    built = build_all()
    total = 0
    for cont_id, nodes in built.items():
        path = OUT_DIR / f"{cont_id}.json"
        path.write_text(json.dumps(nodes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        total += len(nodes)
        print(f"wrote {path.relative_to(ROOT)} ({len(nodes)} nodes)")
    print(f"total: {total} nodes across {len(built)} continents")


if __name__ == "__main__":
    main()
