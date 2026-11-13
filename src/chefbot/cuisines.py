"""Cuisine taxonomy loader, validator, and lookup helpers."""
from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "cuisines"
CONTINENT_FILES = ("americas", "asia", "europe", "near_east", "africa")

# Maps every legacy label from the old flat prompts.CUISINES dict to a leaf node id.
LEGACY_IDS: dict[str, str] = {
    "American": "us_any",
    "American (Cajun)": "us_cajun",
    "American (Creole)": "us_creole",
    "Chinese (Cantonese - Most common style in US)": "cantonese",
    "Chinese (Hong Kong)": "cantonese",
    "Chinese (Sichuan)": "sichuan",
    "Chinese (Shandong)": "shandong",
    "Chinese (Jiangsu)": "jiangsu",
    "Japanese (Kansai)": "kansai",
    "Japanese (Kanto)": "kanto",
    "North Indian": "north_india",
    "South Indian": "south_india",
    "Korean": "korean",
    "Thai": "thai",
    "Vietnamese": "vietnamese",
    "Peruvian": "peruvian",
    "Mexican": "mx_any",
    "Italian": "italy_any",
    "French": "french",
    "Greek": "greek",
    "Spanish": "spanish",
    "Turkish": "turkish",
    "central_european": "german",
    "Central European": "german",
}


def validate(nodes: list[dict]) -> None:
    """Validate unique ids, existing children, leaf/branch consistency, and label <= 20 chars."""
    seen: set[str] = set()
    by_id: dict[str, dict] = {}
    for node in nodes:
        nid = node.get("id", "")
        if not nid:
            raise ValueError("Node is missing an 'id'")
        if nid in seen:
            raise ValueError(f"Duplicate cuisine node id: {nid!r}")
        seen.add(nid)
        by_id[nid] = node

        label = node.get("label", "")
        if not label or len(label) > 20:
            raise ValueError(f"Node {nid!r} label {label!r} exceeds 20 characters (len={len(label)})")

    for node in nodes:
        nid = node["id"]
        kind = node.get("kind")
        kids = node.get("children", [])
        for cid in kids:
            if cid not in by_id:
                raise ValueError(f"Node {nid!r} has dangling child id {cid!r}")
        if kind in ("cuisine", "any") and kids:
            raise ValueError(f"Leaf node {nid!r} (kind={kind!r}) must not have children")
        if kind in ("continent", "country") and not kids:
            raise ValueError(f"Branch node {nid!r} (kind={kind!r}) must have children")


def _load() -> tuple[list[dict], dict[str, dict], dict[str, str]]:
    all_nodes: list[dict] = []
    for name in CONTINENT_FILES:
        path = DATA_DIR / f"{name}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        all_nodes.extend(data)
    validate(all_nodes)
    by_id = {n["id"]: n for n in all_nodes}
    parent_of: dict[str, str] = {}
    for n in all_nodes:
        for cid in n.get("children", []):
            parent_of[cid] = n["id"]
    return all_nodes, by_id, parent_of


_ALL_NODES, _BY_ID, _PARENT_OF = _load()


def get(node_id: str) -> dict | None:
    """Return the node dict for node_id, or None if not found."""
    if not node_id:
        return None
    return _BY_ID.get(node_id)


def resolve(cuisine: str) -> dict | None:
    """Resolve a leaf node id or legacy cuisine label to its selectable leaf node dict, or None."""
    if not cuisine:
        return None
    node = _BY_ID.get(cuisine) or _BY_ID.get(LEGACY_IDS.get(cuisine, ""))
    if node and node.get("kind") in ("cuisine", "any"):
        return node
    return None


def children(node_id: str) -> list[dict]:
    """Return the child node dicts of node_id in tree order."""
    node = _BY_ID.get(node_id)
    if not node:
        return []
    return [_BY_ID[cid] for cid in node.get("children", []) if cid in _BY_ID]


def continents() -> list[dict]:
    """Return the five continent nodes in display order."""
    return [_BY_ID[cid] for cid in CONTINENT_FILES if cid in _BY_ID]


def leaves() -> list[dict]:
    """Return all selectable leaf nodes (kind in {'cuisine', 'any'})."""
    return [n for n in _ALL_NODES if n.get("kind") in ("cuisine", "any")]


def path(node_id: str) -> list[str]:
    """Return breadcrumb labels from the continent down to node_id."""
    if node_id not in _BY_ID:
        return []
    chain: list[str] = []
    cur: str | None = node_id
    while cur and cur in _BY_ID:
        chain.append(_BY_ID[cur]["label"])
        cur = _PARENT_OF.get(cur)
    chain.reverse()
    return chain


def chip_label(node_id: str) -> str:
    """Return a concise chip label (<= 24 chars) for a cuisine node id."""
    node = _BY_ID.get(node_id) or _BY_ID.get(LEGACY_IDS.get(node_id, ""))
    if not node:
        return "Anything"
    if node["kind"] == "any":
        return node["prompt_name"] or node["label"]
    parent_id = _PARENT_OF.get(node["id"])
    parent = _BY_ID.get(parent_id) if parent_id else None
    if (
        parent
        and parent["kind"] == "country"
        and parent["id"] != "united_states"
        and parent["label"].lower() not in node["label"].lower()
    ):
        combined = f"{parent['label']} · {node['label']}"
        if len(combined) <= 24:
            return combined
    return node["label"]
