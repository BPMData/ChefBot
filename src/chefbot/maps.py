"""Map data loader, hit-testing (point-in-polygon), and cuisine region lookup."""
from __future__ import annotations

import json
import math
from pathlib import Path

from chefbot import cuisines

MAPS_DIR = Path(__file__).resolve().parent / "maps"
LEVEL_IDS = (
    "world",
    "americas",
    "asia",
    "europe",
    "near_east",
    "africa",
    "united_states",
    "mexico",
    "caribbean",
    "china",
    "japan",
    "india",
    "italy",
)


def _load_levels() -> dict[str, dict]:
    loaded: dict[str, dict] = {}
    for lid in LEVEL_IDS:
        path = MAPS_DIR / f"{lid}.json"
        loaded[lid] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


_LEVELS: dict[str, dict] = _load_levels()


def levels() -> dict[str, dict]:
    """Return all map levels keyed by level id."""
    return _LEVELS


def get_level(level_id: str) -> dict | None:
    """Return the map level dict for level_id, or None."""
    return _LEVELS.get(level_id)


def has_sublevel(node_id: str) -> bool:
    """Return True if node_id is a drill-down map level (continent or country)."""
    return node_id in _LEVELS and node_id != "world"


def all_region_ids() -> set[str]:
    """Return the set of all region ids present across all map levels."""
    out: set[str] = set()
    for lvl in _LEVELS.values():
        for reg in lvl["regions"]:
            out.add(reg["id"])
    return out


def point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    """Ray-casting point-in-polygon check for a closed ring of [x, y] points."""
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def dist_to_ring(x: float, y: float, ring: list[list[float]]) -> float:
    """Minimum Euclidean distance from (x, y) to any edge of ring."""
    best = float("inf")
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        dx, dy = x2 - x1, y2 - y1
        l2 = dx * dx + dy * dy
        if l2 == 0.0:
            d = math.hypot(x - x1, y - y1)
        else:
            t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / l2))
            d = math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
        if d < best:
            best = d
    return best


def hit_test(level_id: str, x: float, y: float, tolerance: float = 6.0) -> str | None:
    """Find the tapped region id at canvas coordinates (x, y) in level_id.

    First performs a bounding-box check followed by an exact point-in-polygon test
    (preferring smaller bounding-box area if nested/adjacent). Falls back to the
    nearest polygon boundary within `tolerance` pixels for thin islands/coastlines.
    """
    lvl = _LEVELS.get(level_id)
    if not lvl:
        return None

    exact_hits: list[tuple[float, str]] = []
    for reg in lvl["regions"]:
        x0, y0, x1, y1 = reg["bbox"]
        if x0 <= x <= x1 and y0 <= y <= y1:
            for poly in reg["polygons"]:
                if point_in_ring(x, y, poly):
                    area_est = (x1 - x0) * (y1 - y0)
                    exact_hits.append((area_est, reg["id"]))
                    break
    if exact_hits:
        exact_hits.sort(key=lambda item: item[0])
        return exact_hits[0][1]

    if tolerance > 0:
        best_d = tolerance
        best_id: str | None = None
        for reg in lvl["regions"]:
            x0, y0, x1, y1 = reg["bbox"]
            if x0 - tolerance <= x <= x1 + tolerance and y0 - tolerance <= y <= y1 + tolerance:
                for poly in reg["polygons"]:
                    d = dist_to_ring(x, y, poly)
                    if d <= best_d:
                        best_d = d
                        best_id = reg["id"]
        return best_id

    return None


def region_for_cuisine(node_id: str) -> tuple[dict, list[str]] | None:
    """Return (level_dict, highlighted_region_ids) for displaying a mini-map of node_id."""
    node = cuisines.get(node_id) or cuisines.resolve(node_id)
    if not node:
        return None
    nid = node["id"]
    kind = node.get("kind")

    if kind == "continent":
        return _LEVELS["world"], [nid]

    if kind == "any":
        for country_id, lvl in _LEVELS.items():
            if lvl.get("any_id") == nid:
                for cont_lvl in _LEVELS.values():
                    if any(r["id"] == country_id for r in cont_lvl["regions"]):
                        return cont_lvl, [country_id]
                return lvl, [r["id"] for r in lvl["regions"]]

    for lvl in _LEVELS.values():
        if any(r["id"] == nid for r in lvl["regions"]):
            return lvl, [nid]

    return None
