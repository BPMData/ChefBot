"""The browser globe's data covers every drill-down level of the cuisine tree."""
import importlib.util
import json
from pathlib import Path

import pytest

from chefbot import cuisines

ROOT = Path(__file__).resolve().parents[1]
GLOBE = ROOT / "web" / "src" / "globe"
SOURCE = ROOT / "assets" / "maps" / "source" / "palestine_POV_ne_10m_admin_0_countries_pse"


def _load(name):
    return json.loads((GLOBE / name).read_text(encoding="utf-8"))


def _point_in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i, (xi, yi) in enumerate(ring):
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def test_every_level_has_a_view_highlights_and_anchors():
    views = _load("views.json")["views"]
    anchors = _load("anchors.json")
    features = {(f["properties"]["level"], f["properties"]["cuisine"]): f for f in _load("regions.geojson")["features"]}
    assert set(anchors["world"]) == {node["id"] for node in cuisines.continents()}
    levels = ["world"]
    pending = [node["id"] for node in cuisines.continents()]
    while pending:
        level = pending.pop(0)
        levels.append(level)
        pending += [child["id"] for child in cuisines.children(level) if cuisines.children(child["id"])]
    assert set(views) == set(levels)
    for level in levels[1:]:
        choices = [child["id"] for child in cuisines.children(level) if child["kind"] != "any"]
        assert set(anchors[level]) == set(choices), level
        for cuisine in choices:
            feature = features[(level, cuisine)]
            rings = [polygon[0] for polygon in feature["geometry"]["coordinates"]]
            assert any(_point_in_ring(*anchors[level][cuisine], ring) for ring in rings), (level, cuisine)
    assert {level for level, _ in features} == set(levels[1:])


@pytest.mark.skipif(not SOURCE.exists(), reason="Raw shapefiles in assets/maps/source/ are git-ignored")
def test_build_map_data_reproduces_committed_globe_geojson():
    spec = importlib.util.spec_from_file_location("build_map_data", ROOT / "tools" / "build_map_data.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    land, regions, anchors = builder.build_web_geojson()
    assert json.loads(json.dumps(regions)) == _load("regions.geojson")
    assert json.loads(json.dumps(anchors)) == _load("anchors.json")
    assert json.loads(json.dumps(land)) == _load("land.geojson")
