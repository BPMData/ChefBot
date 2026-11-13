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
    assert "The Eight Great Cuisines (八大菜系)" in china_texts
    assert "Regional, diverse, technique-driven" in china_texts   # the usual subtitle stays
    app.map_stack = ["world", "asia"]   # Japan has no extra heading
    asyncio.run(app._trigger_map_region("japan"))
    assert not any("Great Cuisines" in t for t in collect_texts(app.root.content))
    app.map_stack = ["world", "asia"]
    app._render_map_level()
    asyncio.run(app._trigger_map_region("china"))

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


def test_globe_projection_round_trip_and_backside():
    cx, cy, radius = 180.0, 260.0, 150.0
    rotations = [(0.0, 0.0), (15.0, 20.0), (-80.0, 15.0), (110.0, -25.0), (-150.0, 45.0)]
    sample_points = [(10.0, 48.0), (-74.0, 4.5), (102.0, 35.0), (20.0, 6.0), (44.0, 26.0)]

    for clon, clat in rotations:
        for lon, lat in sample_points:
            _, _, z3 = maps.project_globe_vector(lon, lat, clon, clat)
            pt = maps.project_globe_point(lon, lat, clon, clat, cx, cy, radius)
            if z3 >= 0.0:
                assert pt is not None
                inv = maps.inverse_globe_point(pt[0], pt[1], clon, clat, cx, cy, radius)
                assert inv is not None
                assert abs(((inv[0] - lon + 180.0) % 360.0) - 180.0) < 1e-5
                assert abs(inv[1] - lat) < 1e-5
            else:
                assert pt is None

    # Point on exact back of globe is not visible and not tappable as that back continent
    # When centered on Central Pacific (-160, -15), Africa (20, 6) is on the back side.
    assert maps.project_globe_point(20.0, 6.0, -160.0, -15.0, cx, cy, radius) is None
    assert maps.hit_test_globe(cx, cy, -160.0, -15.0, cx, cy, radius) is None

    # Point outside the globe disc returns None
    assert maps.inverse_globe_point(cx + radius + 5.0, cy, 0.0, 0.0, cx, cy, radius) is None
    assert maps.hit_test_globe(cx + radius + 5.0, cy, 0.0, 0.0, cx, cy, radius) is None


def test_globe_continent_centers_and_cuisine_tree_coverage():
    globe = maps.get_globe()
    globe_ids = {r["id"] for r in globe["regions"]}
    cuisine_continent_ids = {c["id"] for c in cuisines.continents()}
    assert globe_ids == cuisine_continent_ids
    assert len({r["color"] for r in globe["regions"]}) == 5

    cx, cy, radius = 180.0, 260.0, 150.0
    for reg in globe["regions"]:
        rid = reg["id"]
        lon, lat = reg["center"]
        assert maps.hit_test_globe_latlon(lon, lat) == rid
        for dlon, dlat in ((0.0, 0.0), (22.0, -12.0), (-22.0, 14.0), (0.0, 28.0)):
            clon = ((lon + dlon + 180.0) % 360.0) - 180.0
            clat = max(-65.0, min(65.0, lat + dlat))
            pt = maps.project_globe_point(lon, lat, clon, clat, cx, cy, radius)
            assert pt is not None, f"Center of {rid!r} unexpectedly hidden at rotation ({clon}, {clat})"
            hit = maps.hit_test_globe(pt[0], pt[1], clon, clat, cx, cy, radius)
            assert hit == rid, f"Tap at projected center of {rid!r} at ({clon}, {clat}) hit {hit!r}"

    # Verify projected polygons and graticule build cleanly across diverse rotations
    for clon in (-150.0, -60.0, 15.0, 100.0):
        for clat in (-55.0, 0.0, 55.0):
            bg, regs = maps.project_globe_polygons(clon, clat, cx, cy, radius)
            assert sum(len(v) for v in regs.values()) + len(bg) > 0
            grat = maps.project_globe_graticule(clon, clat, cx, cy, radius)
            assert len(grat) > 0


@pytest.mark.skipif(
    not (ROOT / "assets" / "maps" / "source" / "palestine_POV_ne_10m_admin_0_countries_pse").exists(),
    reason="Raw shapefiles in assets/maps/source/ are git-ignored",
)
def test_build_globe_data_reproduces_committed_json():
    spec = importlib.util.spec_from_file_location("build_map_data", ROOT / "tools" / "build_map_data.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    built = builder.build_globe()
    committed = json.loads((ROOT / "src" / "chefbot" / "maps" / "globe.json").read_text(encoding="utf-8"))
    assert built == committed


def test_globe_ui_drag_zoom_fly_back_and_labels(monkeypatch, tmp_path):
    import asyncio
    from types import SimpleNamespace
    import flet as ft
    import main as app_main

    monkeypatch.setenv("FLET_APP_STORAGE_DATA", str(tmp_path))
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
        show_dialog=lambda d: None,
        pop_dialog=lambda: None,
        run_task=lambda fn, *a: asyncio.run(fn(*a)),
    )

    app = app_main.ChefBotApp(fake_page)
    app.open_map_browser()
    assert app.map_stack == ["world"]
    assert app._globe_canvas is not None
    # At initial rotation (15E, 20N), Europe/Africa/Near East face the viewer; Americas (-74, 4.5) is on the limb/back
    assert app._globe_labels["europe"].visible is True
    assert app._globe_labels["africa"].visible is True

    # Drag east-west and extreme north/south -> tilt stays clamped to [-GLOBE_MAX_LAT, GLOBE_MAX_LAT]
    app._on_globe_scale_start(SimpleNamespace(local_focal_point=ft.Offset(180.0, 260.0)))
    assert app.globe_touched is True
    start_lon = app.globe_lon
    app._on_globe_scale_update(SimpleNamespace(
        pointer_count=1,
        scale=1.0,
        focal_point_delta=ft.Offset(80.0, 2000.0),
        local_focal_point=ft.Offset(260.0, 2260.0),
    ))
    assert app.globe_lon != start_lon
    assert app.globe_lat == app_main.GLOBE_MAX_LAT

    app._on_globe_scale_update(SimpleNamespace(
        pointer_count=1,
        scale=1.0,
        focal_point_delta=ft.Offset(0.0, -5000.0),
        local_focal_point=ft.Offset(260.0, -2740.0),
    ))
    assert app.globe_lat == -app_main.GLOBE_MAX_LAT

    # Pinch zoom clamps to [GLOBE_MIN_ZOOM, GLOBE_MAX_ZOOM]
    app._on_globe_scale_start(SimpleNamespace(local_focal_point=ft.Offset(180.0, 260.0)))
    app._on_globe_scale_update(SimpleNamespace(
        pointer_count=2, scale=10.0, focal_point_delta=None, local_focal_point=ft.Offset(180.0, 260.0),
    ))
    assert app.globe_zoom == app_main.GLOBE_MAX_ZOOM
    app._on_globe_scale_update(SimpleNamespace(
        pointer_count=2, scale=0.05, focal_point_delta=None, local_focal_point=ft.Offset(180.0, 260.0),
    ))
    assert app.globe_zoom == app_main.GLOBE_MIN_ZOOM
    app._on_globe_scale_end(SimpleNamespace(pointer_count=0, velocity=ft.Offset(0.0, 0.0)))

    # Fly to Americas, hand over to flat Americas map, then Back stays facing Americas
    asyncio.run(app._trigger_map_region("americas"))
    assert app.map_stack == ["world", "americas"]
    americas_focus = maps.globe_region("americas")["focus"]
    assert abs(app.globe_lon - americas_focus[0]) < 1e-3
    assert abs(app.globe_lat - americas_focus[1]) < 1e-3

    # Flat continent map still uses InteractiveViewer with boundary_margin=0
    # (app._map_layer is the current level's layer; map_body inside it holds the viewer)
    map_body_ctrl = app._map_layer.content.content
    assert isinstance(map_body_ctrl, ft.InteractiveViewer)
    # The zoom between levels ran to its end state: new layer at full size, old one faded out and hidden
    assert app._map_layer.opacity == 1.0 and app._map_layer.scale.scale == 1.0
    old_layer = app.root.content.controls[1].content.controls[0]
    assert old_layer.opacity == 0.0 and old_layer.visible is False
    assert map_body_ctrl.boundary_margin == ft.Margin.all(0)

    # Back returns to globe still facing Americas (not reset to GLOBE_INITIAL_LON/LAT)
    app._map_back()
    assert app.map_stack == ["world"]
    assert app._globe_canvas is not None
    assert abs(app.globe_lon - americas_focus[0]) < 1e-3
    assert abs(app.globe_lat - americas_focus[1]) < 1e-3
    assert app._globe_labels["americas"].visible is True
    assert app._globe_labels["asia"].visible is False

