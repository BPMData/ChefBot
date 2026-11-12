import importlib.util
import json
from pathlib import Path

import pytest

from chefbot import cuisines, maps

ROOT = Path(__file__).resolve().parents[1]


def test_every_selectable_cuisine_and_country_has_a_map_region():
    region_ids = maps.all_region_ids()

    # Every selectable leaf cuisine (except *_any) has a map region
    any_ids = {lvl["any_id"] for lvl in maps.levels().values() if lvl["any_id"]}
    for leaf in cuisines.leaves():
        if leaf["kind"] == "any":
            assert leaf["id"].endswith("_any")
            assert leaf["id"] in any_ids
        else:
            assert leaf["id"] in region_ids, f"Missing map region for leaf cuisine {leaf['id']!r}"

    # Every continent and country has both a map region in its parent level and its own drill-down level
    world_ids = {r["id"] for r in maps.get_level("world")["regions"]}
    for cont in cuisines.continents():
        cid = cont["id"]
        assert cid in world_ids
        cont_lvl = maps.get_level(cid)
        assert cont_lvl is not None
        cont_region_ids = {r["id"] for r in cont_lvl["regions"]}
        for child in cuisines.children(cid):
            assert child["id"] in cont_region_ids, f"Missing {child['id']!r} in continent map {cid!r}"
            if child["kind"] == "country":
                country_lvl = maps.get_level(child["id"])
                assert country_lvl is not None, f"Missing drill-down map level for country {child['id']!r}"
                country_region_ids = {r["id"] for r in country_lvl["regions"]}
                for grandchild in cuisines.children(child["id"]):
                    if grandchild["kind"] == "any":
                        assert country_lvl["any_id"] == grandchild["id"]
                    else:
                        assert grandchild["id"] in country_region_ids


def test_every_map_region_id_exists_in_cuisine_tree():
    for level_id, lvl in maps.levels().items():
        if level_id != "world":
            assert cuisines.get(level_id) is not None, f"Level id {level_id!r} not in cuisine tree"
        if lvl["any_id"] is not None:
            any_node = cuisines.get(lvl["any_id"])
            assert any_node is not None and any_node["kind"] == "any"
        for reg in lvl["regions"]:
            node = cuisines.get(reg["id"])
            assert node is not None, f"Region {reg['id']!r} in {level_id!r} does not exist in cuisine tree"
            assert reg["label"] == node["label"]
            assert reg["kind"] == node["kind"]
            assert len(reg["polygons"]) >= 1


def test_small_regions_and_known_cases_have_callouts():
    known_callout_ids = {
        "palestinian_levantine",
        "malaysian_singaporean",
        "caribbean",
        "caribbean_cuban",
        "caribbean_puerto_rican",
        "caribbean_jamaican",
        "us_cajun",
        "us_creole",
        "kanto",
        "kansai",
        "jiangsu",
        "zhejiang",
        "fujian",
        "anhui",
        "shandong",
    }
    seen_callouts: set[str] = set()
    world_lvl = maps.get_level("world")
    assert all(r["callout"] is None for r in world_lvl["regions"])
    assert len({r["color"] for r in world_lvl["regions"]}) == 5

    for level_id, lvl in maps.levels().items():
        w, h = lvl["width"], lvl["height"]
        chip_boxes: list[tuple[str, float, float, float, float]] = []
        for reg in lvl["regions"]:
            assert reg.get("color"), f"Region {reg['id']!r} in {level_id!r} is missing a color"
            x0, y0, x1, y1 = reg["bbox"]
            bw, bh = x1 - x0, y1 - y0
            callout = reg["callout"]
            if level_id != "world" and (bw < 44.0 or bh < 44.0):
                assert callout is not None, (
                    f"Small region {reg['id']!r} ({bw:.1f}x{bh:.1f} px) in {level_id!r} is missing a call-out"
                )
            if callout is not None:
                seen_callouts.add(reg["id"])
                lx, ly = callout["pos"]
                ax, ay = callout["anchor"]
                assert 0 <= ax <= w and 0 <= ay <= h
                assert 16 <= lx <= w - 16 and 16 <= ly <= h - 16
                chip_w = max(56.0, len(callout["label"]) * 6.5 + 16.0)
                chip_h = 26.0
                cx0, cy0 = lx - chip_w * 0.5, ly - chip_h * 0.5
                cx1, cy1 = lx + chip_w * 0.5, ly + chip_h * 0.5
                for other_id, ox0, oy0, ox1, oy1 in chip_boxes:
                    overlaps = not (cx1 < ox0 or cx0 > ox1 or cy1 < oy0 or cy0 > oy1)
                    assert not overlaps, (
                        f"Call-out chips {reg['id']!r} and {other_id!r} overlap on level {level_id!r}"
                    )
                chip_boxes.append((reg["id"], cx0, cy0, cx1, cy1))

    missing = known_callout_ids - seen_callouts
    assert not missing, f"Known small/crowded regions missing call-outs: {missing}"


def test_hit_test_and_info_sheet_mini_map_lookup():
    for level_id, lvl in maps.levels().items():
        for reg in lvl["regions"]:
            cx, cy = reg["center"]
            hit = maps.hit_test(level_id, cx, cy)
            assert hit == reg["id"], f"hit_test at center of {reg['id']!r} in {level_id!r} returned {hit!r}"

    for leaf in cuisines.leaves():
        res = maps.region_for_cuisine(leaf["id"])
        assert res is not None, f"region_for_cuisine returned None for {leaf['id']!r}"
        lvl, hi_ids = res
        lvl_rids = {r["id"] for r in lvl["regions"]}
        assert set(hi_ids) <= lvl_rids and len(hi_ids) >= 1


@pytest.mark.skipif(
    not (ROOT / "assets" / "maps" / "source" / "palestine_POV_ne_10m_admin_0_countries_pse").exists(),
    reason="Raw shapefiles in assets/maps/source/ are git-ignored",
)
def test_build_map_data_reproduces_committed_json():
    spec = importlib.util.spec_from_file_location("build_map_data", ROOT / "tools" / "build_map_data.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    built = builder.build_all()
    for level_id, data in built.items():
        committed = json.loads((ROOT / "src" / "chefbot" / "maps" / f"{level_id}.json").read_text(encoding="utf-8"))
        assert data == committed, f"Map data mismatch for {level_id}.json"


def test_map_browser_and_info_sheet_ui_flow(monkeypatch, tmp_path):
    import asyncio
    from types import SimpleNamespace
    import flet as ft
    import flet.canvas as cv
    import main as app_main

    monkeypatch.setenv("FLET_APP_STORAGE_DATA", str(tmp_path))
    dialogs: list[ft.Control] = []
    fake_view = SimpleNamespace(can_pop=True, on_confirm_pop=None)
    fake_page = SimpleNamespace(
        platform=ft.PagePlatform.MACOS,
        web=True,
        width=375.0,
        height=812.0,
        views=[fake_view],
        appbar=None,
        theme_mode=ft.ThemeMode.DARK,
        update=lambda: None,
        show_dialog=lambda d: dialogs.append(d),
        pop_dialog=lambda: dialogs.pop() if dialogs else None,
        run_task=lambda fn, *a: asyncio.run(fn(*a)),
    )

    app = app_main.ChefBotApp(fake_page)
    app.show_home()

    def collect_texts(ctrl) -> list[str]:
        out: list[str] = []
        if isinstance(ctrl, ft.Text) and ctrl.value:
            out.append(ctrl.value)
        if isinstance(ctrl, ft.TextButton) and isinstance(ctrl.content, str):
            out.append(ctrl.content)
        if isinstance(ctrl, ft.FilledTonalButton) and isinstance(ctrl.content, str):
            out.append(ctrl.content)
        for attr in ("controls", "content", "leading", "title"):
            sub = getattr(ctrl, attr, None)
            if isinstance(sub, list):
                for item in sub:
                    out.extend(collect_texts(item))
            elif isinstance(sub, ft.Control):
                out.extend(collect_texts(sub))
        return out

    def has_canvas(ctrl) -> bool:
        if isinstance(ctrl, cv.Canvas):
            return len(ctrl.shapes) > 0
        for attr in ("controls", "content"):
            sub = getattr(ctrl, attr, None)
            if isinstance(sub, list):
                if any(has_canvas(item) for item in sub):
                    return True
            elif isinstance(sub, ft.Control):
                if has_canvas(sub):
                    return True
        return False

    # 1. Home screen has "Browse by map" next to "Browse cuisines"
    home_texts = collect_texts(app.root.content)
    assert "Browse cuisines" in home_texts
    assert "Browse by map" in home_texts

    # 2. Open map browser at phone width (375 x 812): replaces root.content (not a dialog)
    dialogs.clear()
    app.open_map_browser()
    assert app.on_map is True
    assert dialogs == []
    assert app.map_stack == ["world"]
    assert "Browse by map" in collect_texts(app.root.content)
    assert "What have you got?" not in collect_texts(app.root.content)

    # 3. Drill down: World -> Asia -> China -> tap "sichuan" -> opens info sheet with mini-map & substitutes -> Pick
    asyncio.run(app._trigger_map_region("asia"))
    assert app.map_stack == ["world", "asia"]
    assert "Asia" in collect_texts(app.root.content)

    asyncio.run(app._trigger_map_region("china"))
    assert app.map_stack == ["world", "asia", "china"]
    china_texts = collect_texts(app.root.content)
    assert "Asia > China" in china_texts
    assert "Any" in china_texts

    # Verify every level renders cleanly and every leaf cuisine opens an info sheet with a mini-map
    for lid, lvl in maps.levels().items():
        app.map_stack = ["world"] if lid == "world" else ["world", lid]
        app._render_map_level()
        assert has_canvas(app.root.content), f"Level {lid!r} failed to render map canvas"
        if lvl["any_id"]:
            assert "Any" in collect_texts(app.root.content)

    app.map_stack = ["world", "asia", "china"]
    app._render_map_level()

    # Back goes up one level to Asia, then drill back into China
    app._map_back()
    assert app.map_stack == ["world", "asia"]
    asyncio.run(app._trigger_map_region("china"))
    assert app.map_stack == ["world", "asia", "china"]

    # Tap Sichuan on China map
    dialogs.clear()
    asyncio.run(app._trigger_map_region("sichuan"))
    assert len(dialogs) == 1
    sheet = dialogs[0]
    sheet_texts = collect_texts(sheet)
    assert "If you're missing one" in sheet_texts
    assert has_canvas(sheet), "Info sheet in map browser must include a mini-map Canvas at the top"

    # Find and click the "Pick China · Sichuan" gradient button in the info sheet
    col = sheet.content.content.content
    pick_btn = col.controls[-1].content
    pick_btn.on_click(None)
    assert app.on_map is False
    assert app.cuisine == "sichuan"
    assert "What have you got?" in collect_texts(app.root.content)

    # 4. Verify home screen info sheet also has the mini-map Canvas and substitutes
    dialogs.clear()
    app._cuisine_info("thai")
    assert len(dialogs) == 1
    assert has_canvas(dialogs[0])
    assert "If you're missing one" in collect_texts(dialogs[0])

    # 5. Test desktop resize (1280 x 800) and Back from world level closing map
    fake_page.width, fake_page.height = 1280.0, 800.0
    app.open_map_browser()
    app._on_resize(None)
    assert app.map_scale > 1.0
    app._map_back()
    assert app.on_map is False

