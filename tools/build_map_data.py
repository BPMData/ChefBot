"""Builds projected, simplified map data in src/chefbot/maps/*.json from assets/maps/source/.

Run from the repo root:
    .venv/bin/python tools/build_map_data.py
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import shapefile

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "assets" / "maps" / "source"
COUNTRIES_SHP = SOURCE_DIR / "palestine_POV_ne_10m_admin_0_countries_pse" / "ne_10m_admin_0_countries_pse.shp"
ADMIN1_SHP = SOURCE_DIR / "ne_10m_admin_1_states_provinces" / "ne_10m_admin_1_states_provinces.shp"
COUNTIES_SHP = SOURCE_DIR / "cb_2025_us_county_500k" / "cb_2025_us_county_500k.shp"
OUT_DIR = ROOT / "src" / "chefbot" / "maps"
CUISINES_DIR = ROOT / "src" / "chefbot" / "cuisines"

CANVAS_W = 360.0
CANVAS_H = 520.0
MIN_TAP_PX = 44.0

# Known cases from docs/BROWSE_BY_MAP.md (and regions < 44 x 44 px on phone) that get a call-out chip.
FORCE_CALLOUT_IDS = {
    "caribbean",
    "peruvian",
    "caribbean_cuban",
    "caribbean_puerto_rican",
    "caribbean_jamaican",
    "us_cajun",
    "us_creole",
    "us_new_england_seafood",
    "shandong",
    "jiangsu",
    "zhejiang",
    "fujian",
    "anhui",
    "hunan",
    "cantonese",
    "kanto",
    "kansai",
    "palestinian_levantine",
    "malaysian_singaporean",
    "korean",
    "filipino",
    "vietnamese",
    "thai",
    "afghan",
    "greek",
    "tunisian",
    "senegalese",
}

# Distinct palette key per region so every continent, country, and regional cuisine is visually distinct.
REGION_COLORS: dict[str, str] = {
    # World continents
    "americas": "coral",
    "europe": "blue",
    "near_east": "amber",
    "africa": "orange",
    "asia": "teal",
    # Americas
    "united_states": "blue",
    "mexico": "amber",
    "caribbean": "teal",
    "brazilian": "green",
    "peruvian": "coral",
    "argentinian": "purple",
    # Asia
    "china": "coral",
    "india": "amber",
    "pakistani": "green",
    "afghan": "purple",
    "korean": "blue",
    "japan": "pink",
    "thai": "orange",
    "vietnamese": "lime",
    "filipino": "cyan",
    "malaysian_singaporean": "indigo",
    "indonesian": "teal",
    # Europe
    "french": "blue",
    "spanish": "amber",
    "italy": "green",
    "central_european": "purple",
    "greek": "teal",
    "russian": "coral",
    # Near East
    "turkish": "coral",
    "palestinian_levantine": "teal",
    "persian": "amber",
    # Africa
    "moroccan_north_african": "coral",
    "algerian": "amber",
    "tunisian": "teal",
    "egyptian": "blue",
    "senegalese": "purple",
    "nigerian": "green",
    "ethiopian": "orange",
    # United States
    "us_tex_mex": "amber",
    "us_cajun": "coral",
    "us_creole": "purple",
    "us_southern_soul": "green",
    "us_new_england_seafood": "blue",
    # Mexico
    "mx_northern_baja": "amber",
    "mx_central_oaxacan": "coral",
    "mx_yucatan": "teal",
    # Caribbean
    "caribbean_cuban": "coral",
    "caribbean_jamaican": "green",
    "caribbean_puerto_rican": "amber",
    # China
    "sichuan": "coral",
    "hunan": "amber",
    "cantonese": "green",
    "shandong": "blue",
    "jiangsu": "teal",
    "anhui": "purple",
    "zhejiang": "orange",
    "fujian": "pink",
    # Japan
    "kanto": "coral",
    "kansai": "teal",
    # India
    "north_india": "amber",
    "south_india": "teal",
    # Italy
    "northern_italy": "blue",
    "southern_sicilian_italy": "coral",
}

NEAR_EAST_A3 = {
    "PSX", "ISR", "LBN", "SYR", "JOR", "IRN", "TUR",
    "IRQ", "SAU", "YEM", "OMN", "ARE", "QAT", "BHR", "KWT",
    "CYP", "GEO", "ARM", "AZE", "ESB", "WSB",
}

ACADIANA_PARISHES = {
    "Acadia", "Ascension", "Assumption", "Avoyelles", "Calcasieu", "Cameron",
    "Evangeline", "Iberia", "Iberville", "Jefferson Davis", "Lafayette", "Lafourche",
    "Pointe Coupee", "St. Charles", "St. James", "St. John the Baptist", "St. Landry",
    "St. Martin", "St. Mary", "Terrebonne", "Vermilion", "West Baton Rouge",
}
CREOLE_PARISHES = {"Orleans", "Jefferson", "St. Bernard", "Plaquemines"}
US_SOUTHEAST_STATES = {"AL", "GA", "MS", "SC", "NC", "TN", "AR"}
US_NEW_ENGLAND_STATES = {"ME", "NH", "VT", "MA", "RI", "CT"}

MX_NORTHERN_BAJA = {
    "Baja California", "Baja California Sur", "Sonora", "Chihuahua",
    "Coahuila", "Nuevo León", "Tamaulipas", "Sinaloa", "Durango",
}
MX_CENTRAL_OAXACAN = {
    "Oaxaca", "Puebla", "Distrito Federal", "México", "Morelos",
    "Tlaxcala", "Hidalgo", "Guerrero", "Michoacán", "Jalisco",
}
MX_YUCATAN = {"Yucatán", "Campeche", "Quintana Roo"}

JP_KANTO = {"Tokyo", "Kanagawa", "Saitama", "Chiba", "Ibaraki", "Tochigi", "Gunma"}
JP_KANSAI = {"Ōsaka", "Kyōto", "Hyōgo", "Nara", "Wakayama", "Shiga", "Mie"}

IN_NORTH = {
    "Punjab", "Haryana", "Delhi", "Uttar Pradesh", "Rajasthan",
    "Himachal Pradesh", "Uttarakhand", "Jammu and Kashmir", "Ladakh", "Chandigarh",
}
IN_SOUTH = {"Tamil Nadu", "Kerala", "Karnataka", "Andhra Pradesh", "Telangana", "Puducherry"}

IT_NORTH = {
    "Piemonte", "Valle d'Aosta", "Lombardia", "Trentino-Alto Adige",
    "Veneto", "Friuli-Venezia Giulia", "Liguria", "Emilia-Romagna",
}
IT_SOUTH = {"Campania", "Apulia", "Basilicata", "Calabria", "Sicily", "Molise"}

CENTRAL_EUROPE_A3 = {"DEU", "AUT", "CHE", "CZE", "SVK", "HUN", "POL"}
LEVANT_A3 = {"PSX", "LBN", "SYR", "JOR", "ISR"}


def load_node_labels() -> dict[str, dict]:
    nodes: dict[str, dict] = {}
    for name in ("americas", "asia", "europe", "near_east", "africa"):
        data = json.loads((CUISINES_DIR / f"{name}.json").read_text(encoding="utf-8"))
        for n in data:
            nodes[n["id"]] = n
    return nodes


def extract_rings(shape) -> list[list[tuple[float, float]]]:
    pts = [(float(x), float(y)) for x, y in shape.points]
    parts = list(shape.parts) + [len(pts)]
    return [pts[parts[i]:parts[i + 1]] for i in range(len(parts) - 1) if parts[i + 1] - parts[i] >= 4]


def clip_ring_rect(
    ring: list[tuple[float, float]], xmin: float, ymin: float, xmax: float, ymax: float
) -> list[tuple[float, float]]:
    pts = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else list(ring)
    if len(pts) < 3:
        return []
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if max(xs) < xmin or min(xs) > xmax or max(ys) < ymin or min(ys) > ymax:
        return []
    if min(xs) >= xmin and max(xs) <= xmax and min(ys) >= ymin and max(ys) <= ymax:
        pts.append(pts[0])
        return pts

    def clip_edge(poly, inside, intersect):
        if not poly:
            return []
        out = []
        prev = poly[-1]
        prev_in = inside(prev)
        for cur in poly:
            cur_in = inside(cur)
            if cur_in:
                if not prev_in:
                    out.append(intersect(prev, cur))
                out.append(cur)
            elif prev_in:
                out.append(intersect(prev, cur))
            prev, prev_in = cur, cur_in
        return out

    pts = clip_edge(pts, lambda p: p[0] >= xmin,
                    lambda a, b: (xmin, a[1] + (b[1] - a[1]) * (xmin - a[0]) / (b[0] - a[0])))
    pts = clip_edge(pts, lambda p: p[0] <= xmax,
                    lambda a, b: (xmax, a[1] + (b[1] - a[1]) * (xmax - a[0]) / (b[0] - a[0])))
    pts = clip_edge(pts, lambda p: p[1] >= ymin,
                    lambda a, b: (a[0] + (b[0] - a[0]) * (ymin - a[1]) / (b[1] - a[1]), ymin))
    pts = clip_edge(pts, lambda p: p[1] <= ymax,
                    lambda a, b: (a[0] + (b[0] - a[0]) * (ymax - a[1]) / (b[1] - a[1]), ymax))
    if len(pts) >= 3:
        pts.append(pts[0])
        return pts
    return []


def dissolve_rings(rings: list[list[tuple[float, float]]], precision: int = 4) -> list[list[tuple[float, float]]]:
    """Cancel shared interior directed edges (u -> v) and (v -> u) and stitch exterior cycles."""
    edges: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    for ring in rings:
        pts = [(round(x, precision), round(y, precision)) for x, y in ring]
        if len(pts) > 1 and pts[0] != pts[-1]:
            pts.append(pts[0])
        for i in range(len(pts) - 1):
            p1, p2 = pts[i], pts[i + 1]
            if p1 == p2:
                continue
            if (p2, p1) in edges:
                edges.remove((p2, p1))
            else:
                edges.add((p1, p2))
    adj: dict[tuple[float, float], list[tuple[float, float]]] = defaultdict(list)
    for p1, p2 in edges:
        adj[p1].append(p2)
    loops: list[list[tuple[float, float]]] = []
    while adj:
        start = next(iter(adj))
        stack = [start]
        pos = {start: 0}
        while stack:
            cur = stack[-1]
            nxt_list = adj.get(cur)
            if not nxt_list:
                pos.pop(cur, None)
                stack.pop()
                continue
            nxt = nxt_list.pop()
            if not nxt_list:
                del adj[cur]
            if nxt in pos:
                idx = pos[nxt]
                cycle = stack[idx:] + [nxt]
                for p in stack[idx + 1:]:
                    pos.pop(p, None)
                del stack[idx + 1:]
                if len(cycle) >= 4:
                    loops.append(cycle)
            else:
                pos[nxt] = len(stack)
                stack.append(nxt)
    return loops


def rdp(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    """Ramer-Douglas-Peucker polyline simplification."""
    if len(points) <= 2:
        return points
    x1, y1 = points[0]
    x2, y2 = points[-1]
    dx, dy = x2 - x1, y2 - y1
    denom = math.hypot(dx, dy)
    max_d = -1.0
    idx = 0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        if denom == 0.0:
            d = math.hypot(px - x1, py - y1)
        else:
            d = abs(dy * px - dx * py + x2 * y1 - y2 * x1) / denom
        if d > max_d:
            max_d = d
            idx = i
    if max_d > epsilon:
        left = rdp(points[: idx + 1], epsilon)
        right = rdp(points[idx:], epsilon)
        return left[:-1] + right
    return [points[0], points[-1]]


def simplify_ring(ring: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    if len(ring) < 4:
        return []
    open_pts = ring[:-1] if ring[0] == ring[-1] else list(ring)
    if len(open_pts) < 3:
        return []
    # Split closed ring at vertex 0 and its farthest vertex so RDP preserves closed loops
    x0, y0 = open_pts[0]
    split_idx = max(range(1, len(open_pts)), key=lambda i: math.hypot(open_pts[i][0] - x0, open_pts[i][1] - y0))
    half1 = rdp(open_pts[: split_idx + 1], epsilon)
    half2 = rdp(open_pts[split_idx:] + [open_pts[0]], epsilon)
    combined = half1[:-1] + half2
    if len(combined) < 4:
        return []
    return combined


def ring_area(ring: list[tuple[float, float]]) -> float:
    a = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        a += x1 * y2 - x2 * y1
    return abs(a) * 0.5


def ring_bbox(ring: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


def point_in_ring(x: float, y: float, ring: list[tuple[float, float]]) -> bool:
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


def dist_to_ring_edges(x: float, y: float, ring: list[tuple[float, float]]) -> float:
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


def visual_center(ring: list[tuple[float, float]]) -> tuple[float, float]:
    """Find an interior point inside `ring` that maximizes distance from its boundary."""
    x0, y0, x1, y1 = ring_bbox(ring)
    w, h = x1 - x0, y1 - y0
    if w < 1.0 or h < 1.0:
        return round((x0 + x1) * 0.5, 1), round((y0 + y1) * 0.5, 1)
    best_pt = ((x0 + x1) * 0.5, (y0 + y1) * 0.5)
    best_d = -1.0
    steps = 14
    for ix in range(1, steps):
        gx = x0 + w * (ix / steps)
        for iy in range(1, steps):
            gy = y0 + h * (iy / steps)
            if point_in_ring(gx, gy, ring):
                d = dist_to_ring_edges(gx, gy, ring)
                if d > best_d:
                    best_d = d
                    best_pt = (gx, gy)
    if best_d < 0:
        # Fallback: midpoint of vertices
        cx = sum(p[0] for p in ring[:-1]) / max(1, len(ring) - 1)
        cy = sum(p[1] for p in ring[:-1]) / max(1, len(ring) - 1)
        return round(cx, 1), round(cy, 1)
    return round(best_pt[0], 1), round(best_pt[1], 1)


def project_and_simplify(
    raw_regions: dict[str, list[list[tuple[float, float]]]],
    raw_bg: list[list[tuple[float, float]]],
    window: tuple[float, float, float, float],
    pad: tuple[float, float, float, float],
    epsilon: float = 0.65,
    min_area_px: float = 2.5,
) -> tuple[dict[str, list[list[list[float]]]], list[list[list[float]]]]:
    lon0, lat0, lon1, lat1 = window
    pad_l, pad_t, pad_r, pad_b = pad
    avail_w = CANVAS_W - pad_l - pad_r
    avail_h = CANVAS_H - pad_t - pad_b
    cos_lat = math.cos(math.radians((lat0 + lat1) * 0.5))
    geo_w = (lon1 - lon0) * cos_lat
    geo_h = lat1 - lat0
    scale = min(avail_w / geo_w, avail_h / geo_h)
    draw_w = geo_w * scale
    draw_h = geo_h * scale
    off_x = pad_l + (avail_w - draw_w) * 0.5
    off_y = pad_t + (avail_h - draw_h) * 0.5

    def proj_ring(ring: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [
            (off_x + (lon - lon0) * cos_lat * scale, off_y + (lat1 - lat) * scale)
            for lon, lat in ring
        ]

    def process_group(rings: list[list[tuple[float, float]]], keep_at_least_one: bool) -> list[list[list[float]]]:
        clipped = []
        for r in rings:
            c = clip_ring_rect(r, lon0, lat0, lon1, lat1)
            if c:
                clipped.append(c)
        if not clipped:
            return []
        dissolved = dissolve_rings(clipped, precision=4)
        projected = [proj_ring(r) for r in dissolved]
        projected.sort(key=ring_area, reverse=True)
        out: list[list[list[float]]] = []
        for idx, pr in enumerate(projected):
            area = ring_area(pr)
            if area < min_area_px and not (keep_at_least_one and idx == 0):
                continue
            simp = simplify_ring(pr, epsilon)
            if not simp and keep_at_least_one and idx == 0:
                x0, y0, x1, y1 = ring_bbox(pr)
                cx, cy = (x0 + x1) * 0.5, (y0 + y1) * 0.5
                r_px = max(2.0, (x1 - x0) * 0.5, (y1 - y0) * 0.5)
                simp = [
                    (cx - r_px, cy - r_px),
                    (cx + r_px, cy - r_px),
                    (cx + r_px, cy + r_px),
                    (cx - r_px, cy + r_px),
                    (cx - r_px, cy - r_px),
                ]
            if simp:
                rounded = [[round(x, 1), round(y, 1)] for x, y in simp]
                out.append(rounded)
        return out

    out_regions = {rid: process_group(rings, keep_at_least_one=True) for rid, rings in raw_regions.items()}
    out_bg = process_group(raw_bg, keep_at_least_one=False)
    return out_regions, out_bg


# Explicit call-out chip coordinates (lx, ly) on the 360 x 520 phone canvas for each level,
# carefully placed in margins / sea so leader lines are short and chips never overlap.
CALLOUT_POSITIONS: dict[str, dict[str, tuple[float, float]]] = {
    "world": {},
    "americas": {
        "caribbean": (294.0, 206.0),
        "peruvian": (72.0, 344.0),
    },
    "asia": {
        "afghan": (52.0, 134.0),
        "korean": (298.0, 112.0),
        "vietnamese": (298.0, 250.0),
        "filipino": (304.0, 308.0),
        "thai": (106.0, 354.0),
        "malaysian_singaporean": (118.0, 416.0),
    },
    "europe": {
        "greek": (244.0, 456.0),
    },
    "near_east": {
        "palestinian_levantine": (88.0, 304.0),
    },
    "africa": {
        "tunisian": (204.0, 56.0),
        "senegalese": (54.0, 252.0),
    },
    "united_states": {
        "us_new_england_seafood": (274.0, 114.0),
        "us_cajun": (176.0, 412.0),
        "us_creole": (268.0, 412.0),
    },
    "mexico": {},
    "caribbean": {
        "caribbean_cuban": (112.0, 148.0),
        "caribbean_jamaican": (116.0, 352.0),
        "caribbean_puerto_rican": (286.0, 344.0),
    },
    "china": {
        "shandong": (302.0, 186.0),
        "jiangsu": (304.0, 236.0),
        "anhui": (304.0, 284.0),
        "zhejiang": (304.0, 332.0),
        "fujian": (302.0, 382.0),
        "hunan": (162.0, 426.0),
        "cantonese": (258.0, 434.0),
    },
    "japan": {
        "kanto": (292.0, 326.0),
        "kansai": (96.0, 396.0),
    },
    "india": {},
    "italy": {},
}

LABEL_POS_OVERRIDES: dict[str, dict[str, tuple[float, float]]] = {
    "world": {
        "americas": (74.0, 224.0),
        "europe": (180.0, 198.0),
        "near_east": (228.0, 238.0),
        "africa": (186.0, 274.0),
        "asia": (292.0, 214.0),
    },
    "europe": {
        "italy": (126.0, 348.0),
    },
    "africa": {
        "moroccan_north_african": (54.0, 118.0),
        "algerian": (122.0, 148.0),
    },
}


def build_all() -> dict[str, dict]:
    nodes = load_node_labels()
    sf0 = shapefile.Reader(str(COUNTRIES_SHP))
    sf1 = shapefile.Reader(str(ADMIN1_SHP))
    sf2 = shapefile.Reader(str(COUNTIES_SHP))

    countries_by_a3: dict[str, list[list[tuple[float, float]]]] = defaultdict(list)
    country_records: list[tuple[dict, list[list[tuple[float, float]]]]] = []
    for sr in sf0.shapeRecords():
        rec = sr.record.as_dict()
        rings = extract_rings(sr.shape)
        a3 = rec["ADM0_A3"]
        if a3:
            countries_by_a3[a3].extend(rings)
        country_records.append((rec, rings))

    admin1_records: list[tuple[dict, list[list[tuple[float, float]]]]] = []
    for sr in sf1.shapeRecords():
        admin1_records.append((sr.record.as_dict(), extract_rings(sr.shape)))

    la_parishes: dict[str, list[list[tuple[float, float]]]] = defaultdict(list)
    for sr in sf2.shapeRecords():
        rec = sr.record.as_dict()
        if rec["STATEFP"] == "22":
            la_parishes[rec["NAME"]].extend(extract_rings(sr.shape))

    levels_out: dict[str, dict] = {}

    def finalize_level(
        level_id: str,
        raw_regions: dict[str, list[list[tuple[float, float]]]],
        raw_bg: list[list[tuple[float, float]]],
        window: tuple[float, float, float, float],
        pad: tuple[float, float, float, float],
        any_id: str | None = None,
        epsilon: float = 0.65,
        min_area_px: float = 2.5,
        anchor_overrides: dict[str, list[list[tuple[float, float]]]] | None = None,
    ) -> dict:
        proj_regions, proj_bg = project_and_simplify(
            raw_regions, raw_bg, window, pad, epsilon=epsilon, min_area_px=min_area_px
        )
        override_proj = {}
        if anchor_overrides:
            override_proj, _ = project_and_simplify(
                anchor_overrides, [], window, pad, epsilon=epsilon, min_area_px=0.5
            )

        level_callouts = CALLOUT_POSITIONS.get(level_id, {})
        level_label_pos = LABEL_POS_OVERRIDES.get(level_id, {})
        region_objs: list[dict] = []

        for rid, polys in proj_regions.items():
            node = nodes[rid]
            all_xs = [pt[0] for poly in polys for pt in poly]
            all_ys = [pt[1] for poly in polys for pt in poly]
            bbox = [round(min(all_xs), 1), round(min(all_ys), 1), round(max(all_xs), 1), round(max(all_ys), 1)]
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]

            best_poly = max(polys, key=lambda p: ring_area([(pt[0], pt[1]) for pt in p]))
            cx, cy = visual_center([(pt[0], pt[1]) for pt in best_poly])
            ax, ay = cx, cy
            if rid in override_proj and override_proj[rid]:
                ov_poly = max(override_proj[rid], key=lambda p: ring_area([(pt[0], pt[1]) for pt in p]))
                ax, ay = visual_center([(pt[0], pt[1]) for pt in ov_poly])
                if point_in_ring(ax, ay, [(pt[0], pt[1]) for pt in ov_poly]):
                    cx, cy = ax, ay

            needs_callout = level_id != "world" and (
                rid in FORCE_CALLOUT_IDS
                or rid in level_callouts
                or bw < MIN_TAP_PX
                or bh < MIN_TAP_PX
            )
            callout = None
            if needs_callout:
                lx, ly = level_callouts.get(rid, (cx, max(24.0, cy - 36.0)))
                callout = {
                    "anchor": [round(ax, 1), round(ay, 1)],
                    "pos": [round(lx, 1), round(ly, 1)],
                    "label": node["label"],
                }

            lbl_x, lbl_y = level_label_pos.get(rid, (cx, cy))
            region_objs.append({
                "id": rid,
                "kind": node["kind"],
                "label": node["label"],
                "color": REGION_COLORS.get(rid, "teal"),
                "bbox": bbox,
                "center": [cx, cy],
                "label_pos": [round(lbl_x, 1), round(lbl_y, 1)],
                "polygons": polys,
                "callout": callout,
            })

        return {
            "id": level_id,
            "width": int(CANVAS_W),
            "height": int(CANVAS_H),
            "any_id": any_id,
            "background": proj_bg,
            "regions": region_objs,
        }

    # 1. WORLD
    world_regions: dict[str, list[list[tuple[float, float]]]] = {
        "americas": [],
        "europe": [],
        "near_east": [],
        "asia": [],
        "africa": [],
    }
    world_bg: list[list[tuple[float, float]]] = []
    for rec, rings in country_records:
        a3 = rec["ADM0_A3"]
        cont = rec["CONTINENT"]
        if cont == "Antarctica":
            continue
        if cont in ("North America", "South America") or rec["REGION_UN"] == "Americas":
            world_regions["americas"].extend(rings)
        elif a3 in NEAR_EAST_A3:
            world_regions["near_east"].extend(rings)
        elif a3 == "RUS":
            # Split Russia at the Ural Mountains (60E) on the world overview map so Europe and Asia have natural shapes
            for r in rings:
                eu_part = clip_ring_rect(r, -180.0, -90.0, 60.0, 90.0)
                if eu_part:
                    world_regions["europe"].append(eu_part)
                as_part = clip_ring_rect(r, 60.0, -90.0, 180.0, 90.0)
                if as_part:
                    world_regions["asia"].append(as_part)
        elif cont == "Europe":
            # Exclude French Guiana from Europe on the world map
            for r in rings:
                x0, y0, x1, y1 = ring_bbox(r)
                if x1 < -30:
                    world_regions["americas"].append(r)
                else:
                    world_regions["europe"].append(r)
        elif cont == "Africa":
            world_regions["africa"].extend(rings)
        elif cont == "Asia":
            world_regions["asia"].extend(rings)
        else:
            world_bg.extend(rings)

    levels_out["world"] = finalize_level(
        "world",
        world_regions,
        world_bg,
        window=(-168.0, -56.0, 179.0, 74.0),
        pad=(8.0, 40.0, 8.0, 40.0),
        epsilon=0.8,
        min_area_px=3.0,
        anchor_overrides={
            "europe": countries_by_a3["DEU"] + countries_by_a3["FRA"] + countries_by_a3["POL"],
            "near_east": countries_by_a3["SAU"],
            "africa": countries_by_a3["COD"] + countries_by_a3["CAF"],
            "asia": countries_by_a3["CHN"],
        },
    )

    # 2. AMERICAS
    americas_map = {
        "united_states": {"USA"},
        "mexico": {"MEX"},
        "caribbean": {"CUB", "JAM", "PRI"},
        "brazilian": {"BRA"},
        "peruvian": {"PER"},
        "argentinian": {"ARG"},
    }
    am_regions = {k: [] for k in americas_map}
    am_bg = []
    for rec, rings in country_records:
        a3 = rec["ADM0_A3"]
        matched = False
        for rid, a3_set in americas_map.items():
            if a3 in a3_set:
                am_regions[rid].extend(rings)
                matched = True
                break
        if not matched and (rec["CONTINENT"] in ("North America", "South America") or rec["REGION_UN"] == "Americas" or a3 == "FRA"):
            am_bg.extend(rings)

    levels_out["americas"] = finalize_level(
        "americas",
        am_regions,
        am_bg,
        window=(-168.0, -56.0, -34.0, 72.0),
        pad=(14.0, 24.0, 18.0, 24.0),
        epsilon=0.7,
        min_area_px=2.5,
    )

    # 3. ASIA
    asia_map = {
        "china": {"CHN", "HKG", "MAC"},
        "japan": {"JPN"},
        "india": {"IND"},
        "korean": {"KOR", "PRK"},
        "thai": {"THA"},
        "vietnamese": {"VNM"},
        "filipino": {"PHL"},
        "indonesian": {"IDN"},
        "malaysian_singaporean": {"MYS", "SGP"},
        "afghan": {"AFG"},
        "pakistani": {"PAK"},
    }
    as_regions = {k: [] for k in asia_map}
    as_bg = []
    for rec, rings in country_records:
        a3 = rec["ADM0_A3"]
        matched = False
        for rid, a3_set in asia_map.items():
            if a3 in a3_set:
                as_regions[rid].extend(rings)
                matched = True
                break
        if not matched and rec["CONTINENT"] in ("Asia", "Europe", "Oceania"):
            as_bg.extend(rings)

    levels_out["asia"] = finalize_level(
        "asia",
        as_regions,
        as_bg,
        window=(60.0, -11.5, 146.5, 54.5),
        pad=(16.0, 24.0, 24.0, 32.0),
        epsilon=0.65,
        min_area_px=2.5,
        anchor_overrides={"malaysian_singaporean": countries_by_a3["SGP"] + countries_by_a3["MYS"][:1]},
    )

    # 4. EUROPE
    europe_map = {
        "italy": {"ITA"},
        "french": {"FRA"},
        "spanish": {"ESP"},
        "greek": {"GRC"},
        "central_european": CENTRAL_EUROPE_A3,
        "russian": {"RUS"},
    }
    eu_regions = {k: [] for k in europe_map}
    eu_bg = []
    for rec, rings in country_records:
        a3 = rec["ADM0_A3"]
        matched = False
        for rid, a3_set in europe_map.items():
            if a3 in a3_set:
                # Filter out overseas rings outside Europe
                eu_rings = [r for r in rings if ring_bbox(r)[2] > -12.0 and ring_bbox(r)[3] > 34.0]
                eu_regions[rid].extend(eu_rings)
                matched = True
                break
        if not matched:
            eu_bg.extend(rings)

    levels_out["europe"] = finalize_level(
        "europe",
        eu_regions,
        eu_bg,
        window=(-11.0, 34.5, 58.0, 71.2),
        pad=(14.0, 24.0, 14.0, 36.0),
        epsilon=0.65,
        min_area_px=2.5,
    )

    # 5. NEAR EAST
    ne_map = {
        "palestinian_levantine": LEVANT_A3,
        "persian": {"IRN"},
        "turkish": {"TUR"},
    }
    ne_regions = {k: [] for k in ne_map}
    ne_bg = []
    for rec, rings in country_records:
        a3 = rec["ADM0_A3"]
        matched = False
        for rid, a3_set in ne_map.items():
            if a3 in a3_set:
                ne_regions[rid].extend(rings)
                matched = True
                break
        if not matched:
            ne_bg.extend(rings)

    levels_out["near_east"] = finalize_level(
        "near_east",
        ne_regions,
        ne_bg,
        window=(25.5, 12.0, 63.8, 43.5),
        pad=(18.0, 24.0, 14.0, 24.0),
        epsilon=0.6,
        min_area_px=2.0,
        anchor_overrides={"palestinian_levantine": countries_by_a3["PSX"]},
    )

    # 6. AFRICA
    africa_map = {
        "moroccan_north_african": {"MAR"},
        "tunisian": {"TUN"},
        "algerian": {"DZA"},
        "ethiopian": {"ETH"},
        "egyptian": {"EGY"},
        "nigerian": {"NGA"},
        "senegalese": {"SEN"},
    }
    af_regions = {k: [] for k in africa_map}
    af_bg = []
    for rec, rings in country_records:
        a3 = rec["ADM0_A3"]
        matched = False
        for rid, a3_set in africa_map.items():
            if a3 in a3_set:
                af_regions[rid].extend(rings)
                matched = True
                break
        if not matched and rec["CONTINENT"] == "Africa":
            af_bg.extend(rings)

    levels_out["africa"] = finalize_level(
        "africa",
        af_regions,
        af_bg,
        window=(-19.0, -35.5, 52.0, 38.0),
        pad=(16.0, 28.0, 16.0, 24.0),
        epsilon=0.65,
        min_area_px=2.5,
    )

    # 7. UNITED STATES
    us_regions: dict[str, list[list[tuple[float, float]]]] = {
        "us_cajun": [],
        "us_creole": [],
        "us_southern_soul": [],
        "us_tex_mex": [],
        "us_new_england_seafood": [],
    }
    us_bg: list[list[tuple[float, float]]] = []
    for pname, rings in la_parishes.items():
        if pname in ACADIANA_PARISHES:
            us_regions["us_cajun"].extend(rings)
        elif pname in CREOLE_PARISHES:
            us_regions["us_creole"].extend(rings)
        else:
            us_regions["us_southern_soul"].extend(rings)

    for rec, rings in admin1_records:
        if rec["iso_a2"] != "US":
            continue
        postal = rec["postal"]
        if postal in ("AK", "HI", "LA"):
            continue
        if postal in US_SOUTHEAST_STATES:
            us_regions["us_southern_soul"].extend(rings)
        elif postal == "TX":
            us_regions["us_tex_mex"].extend(rings)
        elif postal in US_NEW_ENGLAND_STATES:
            us_regions["us_new_england_seafood"].extend(rings)
        else:
            us_bg.extend(rings)

    levels_out["united_states"] = finalize_level(
        "united_states",
        us_regions,
        us_bg,
        window=(-125.0, 24.2, -66.5, 49.6),
        pad=(10.0, 36.0, 14.0, 56.0),
        any_id="us_any",
        epsilon=0.6,
        min_area_px=1.5,
    )

    # 8. MEXICO
    mx_regions: dict[str, list[list[tuple[float, float]]]] = {
        "mx_northern_baja": [],
        "mx_central_oaxacan": [],
        "mx_yucatan": [],
    }
    mx_bg: list[list[tuple[float, float]]] = []
    for rec, rings in admin1_records:
        if rec["iso_a2"] != "MX":
            continue
        name = rec["name"]
        if name in MX_NORTHERN_BAJA:
            mx_regions["mx_northern_baja"].extend(rings)
        elif name in MX_CENTRAL_OAXACAN:
            mx_regions["mx_central_oaxacan"].extend(rings)
        elif name in MX_YUCATAN:
            mx_regions["mx_yucatan"].extend(rings)
        else:
            mx_bg.extend(rings)

    levels_out["mexico"] = finalize_level(
        "mexico",
        mx_regions,
        mx_bg,
        window=(-117.3, 14.3, -86.4, 32.8),
        pad=(12.0, 32.0, 16.0, 32.0),
        any_id="mx_any",
        epsilon=0.6,
        min_area_px=2.0,
    )

    # 9. CARIBBEAN
    car_map = {
        "caribbean_cuban": {"CUB"},
        "caribbean_puerto_rican": {"PRI"},
        "caribbean_jamaican": {"JAM"},
    }
    car_regions = {k: [] for k in car_map}
    car_bg = []
    for rec, rings in country_records:
        a3 = rec["ADM0_A3"]
        matched = False
        for rid, a3_set in car_map.items():
            if a3 in a3_set:
                car_regions[rid].extend(rings)
                matched = True
                break
        if not matched and rec["SUBREGION"] == "Caribbean":
            car_bg.extend(rings)

    levels_out["caribbean"] = finalize_level(
        "caribbean",
        car_regions,
        car_bg,
        window=(-85.3, 16.2, -64.2, 24.2),
        pad=(14.0, 48.0, 14.0, 48.0),
        any_id="caribbean_any",
        epsilon=0.5,
        min_area_px=1.5,
    )

    # 10. CHINA
    cn_map = {
        "sichuan": {"Sichuan", "Chongqing"},
        "hunan": {"Hunan"},
        "cantonese": {"Guangdong"},
        "shandong": {"Shandong"},
        "jiangsu": {"Jiangsu"},
        "zhejiang": {"Zhejiang"},
        "fujian": {"Fujian"},
        "anhui": {"Anhui"},
    }
    cn_regions = {k: [] for k in cn_map}
    cn_bg = []
    for rec, rings in admin1_records:
        iso = rec["iso_a2"]
        if iso in ("HK", "MO"):
            cn_regions["cantonese"].extend(rings)
            continue
        if iso != "CN":
            continue
        name = rec["name"]
        if name == "Paracel Islands":
            continue
        matched = False
        for rid, nset in cn_map.items():
            if name in nset:
                cn_regions[rid].extend(rings)
                matched = True
                break
        if not matched:
            cn_bg.extend(rings)

    levels_out["china"] = finalize_level(
        "china",
        cn_regions,
        cn_bg,
        window=(73.2, 18.0, 135.2, 53.8),
        pad=(10.0, 28.0, 56.0, 44.0),
        any_id="china_any",
        epsilon=0.6,
        min_area_px=2.0,
    )

    # 11. JAPAN
    jp_regions: dict[str, list[list[tuple[float, float]]]] = {
        "kanto": [],
        "kansai": [],
    }
    jp_bg: list[list[tuple[float, float]]] = []
    for rec, rings in admin1_records:
        if rec["iso_a2"] != "JP":
            continue
        name = rec["name"]
        # Filter out distant tiny Pacific islands of Tokyo south of 34.5N
        filtered = [r for r in rings if not (name == "Tokyo" and ring_bbox(r)[3] < 34.5)]
        if name in JP_KANTO:
            jp_regions["kanto"].extend(filtered)
        elif name in JP_KANSAI:
            jp_regions["kansai"].extend(filtered)
        else:
            jp_bg.extend(filtered)

    levels_out["japan"] = finalize_level(
        "japan",
        jp_regions,
        jp_bg,
        window=(129.0, 30.2, 145.9, 45.6),
        pad=(16.0, 24.0, 24.0, 24.0),
        any_id="japan_any",
        epsilon=0.55,
        min_area_px=1.5,
    )

    # 12. INDIA
    in_regions: dict[str, list[list[tuple[float, float]]]] = {
        "north_india": [],
        "south_india": [],
    }
    in_bg: list[list[tuple[float, float]]] = []
    for rec, rings in admin1_records:
        if rec["iso_a2"] != "IN":
            continue
        name = rec["name"]
        if name in ("Andaman and Nicobar", "Lakshadweep"):
            continue
        if name in IN_NORTH:
            in_regions["north_india"].extend(rings)
        elif name in IN_SOUTH:
            in_regions["south_india"].extend(rings)
        else:
            in_bg.extend(rings)

    levels_out["india"] = finalize_level(
        "india",
        in_regions,
        in_bg,
        window=(68.0, 7.8, 97.5, 37.2),
        pad=(14.0, 20.0, 14.0, 20.0),
        any_id="india_any",
        epsilon=0.6,
        min_area_px=2.0,
    )

    # 13. ITALY
    it_regions: dict[str, list[list[tuple[float, float]]]] = {
        "northern_italy": [],
        "southern_sicilian_italy": [],
    }
    it_bg: list[list[tuple[float, float]]] = []
    for rec, rings in admin1_records:
        if rec["iso_a2"] != "IT":
            continue
        reg = rec["region"]
        if reg in IT_NORTH:
            it_regions["northern_italy"].extend(rings)
        elif reg in IT_SOUTH:
            it_regions["southern_sicilian_italy"].extend(rings)
        else:
            it_bg.extend(rings)

    levels_out["italy"] = finalize_level(
        "italy",
        it_regions,
        it_bg,
        window=(6.5, 36.5, 18.7, 47.2),
        pad=(16.0, 20.0, 16.0, 20.0),
        any_id="italy_any",
        epsilon=0.55,
        min_area_px=1.5,
    )

    return levels_out


GLOBE_META: dict[str, dict[str, list[float]]] = {
    "americas": {"center": [-74.0, 4.5], "focus": [-78.0, 14.0]},
    "europe": {"center": [15.0, 50.0], "focus": [15.0, 50.0]},
    "near_east": {"center": [44.0, 26.0], "focus": [44.0, 26.0]},
    "africa": {"center": [20.0, 6.0], "focus": [20.0, 6.0]},
    "asia": {"center": [102.0, 35.0], "focus": [102.0, 35.0]},
}


def _simplify_and_subdivide_lonlat(
    rings: list[list[tuple[float, float]]],
    epsilon_deg: float,
    min_area_deg2: float,
    max_step_deg: float = 6.0,
) -> list[list[list[float]]]:
    """Dissolve shared borders, simplify in cos(lat)-weighted degrees, and subdivide long edges."""
    dissolved = dissolve_rings(rings, precision=4)
    out: list[list[list[float]]] = []
    for ring in dissolved:
        if len(ring) < 4:
            continue
        mean_lat = sum(p[1] for p in ring[:-1]) / max(1, len(ring) - 1)
        cos_lat = max(0.15, math.cos(math.radians(mean_lat)))
        if ring_area(ring) * cos_lat < min_area_deg2:
            continue
        scaled = [(lon * cos_lat, lat) for lon, lat in ring]
        simp_scaled = simplify_ring(scaled, epsilon_deg)
        if not simp_scaled:
            continue
        simp = [(x / cos_lat, y) for x, y in simp_scaled]
        subdivided = [simp[0]]
        for p2 in simp[1:]:
            p1 = subdivided[-1]
            span = math.hypot((p2[0] - p1[0]) * cos_lat, p2[1] - p1[1])
            if span > max_step_deg:
                steps = int(math.ceil(span / max_step_deg))
                for k in range(1, steps):
                    t = k / steps
                    subdivided.append((
                        p1[0] + t * (p2[0] - p1[0]),
                        p1[1] + t * (p2[1] - p1[1]),
                    ))
            subdivided.append(p2)
        rounded = [[round(x, 2), round(y, 2)] for x, y in subdivided]
        if len(rounded) >= 4:
            rounded[-1] = list(rounded[0])
            out.append(rounded)
    out.sort(key=lambda r: ring_area([(pt[0], pt[1]) for pt in r]), reverse=True)
    return out


def _simplify_antarctica_polar(rings: list[list[tuple[float, float]]], epsilon_deg: float = 0.6) -> list[list[list[float]]]:
    """Simplify Antarctica in south-polar stereographic coordinates so no +/-180 pole seam remains."""
    out: list[list[list[float]]] = []
    for r in rings:
        coast = [
            (lon, lat)
            for lon, lat in r[:-1]
            if lat > -85.5 and not (abs(abs(lon) - 180.0) < 0.01 and lat < -78.5)
        ]
        if len(coast) < 4:
            continue
        polar = [
            ((90.0 + lat) * math.cos(math.radians(lon)), (90.0 + lat) * math.sin(math.radians(lon)))
            for lon, lat in coast
        ]
        if ring_area(polar) < 2.0:
            continue
        polar.append(polar[0])
        simp = simplify_ring(polar, epsilon_deg)
        if len(simp) < 4:
            continue
        ring_ll = [
            [round(math.degrees(math.atan2(y, x)), 2), round(math.hypot(x, y) - 90.0, 2)]
            for x, y in simp
        ]
        ring_ll[-1] = list(ring_ll[0])
        out.append(ring_ll)
    return out


def build_globe() -> dict:
    """Build coarse lat/lon continent and background outlines for the 3D orthographic globe."""
    nodes = load_node_labels()
    sf0 = shapefile.Reader(str(COUNTRIES_SHP))
    globe_regions: dict[str, list[list[tuple[float, float]]]] = {
        "americas": [],
        "europe": [],
        "near_east": [],
        "asia": [],
        "africa": [],
    }
    globe_bg: list[list[tuple[float, float]]] = []
    antarctica_rings: list[list[tuple[float, float]]] = []

    for sr in sf0.shapeRecords():
        rec = sr.record.as_dict()
        rings = extract_rings(sr.shape)
        a3 = rec["ADM0_A3"]
        cont = rec["CONTINENT"]
        if cont == "Antarctica":
            antarctica_rings.extend(rings)
            continue
        if cont in ("North America", "South America") or rec["REGION_UN"] == "Americas":
            globe_regions["americas"].extend(rings)
        elif a3 in NEAR_EAST_A3:
            globe_regions["near_east"].extend(rings)
        elif a3 == "RUS":
            # Keep Chukotka (west of 180 / negative lon) with Asia; split European Russia at 60E
            for r in rings:
                eu_part = clip_ring_rect(r, 0.0, -90.0, 60.0, 90.0)
                if eu_part:
                    globe_regions["europe"].append(eu_part)
                as_east = clip_ring_rect(r, 60.0, -90.0, 180.0, 90.0)
                if as_east:
                    globe_regions["asia"].append(as_east)
                as_west = clip_ring_rect(r, -180.0, -90.0, 0.0, 90.0)
                if as_west:
                    globe_regions["asia"].append(as_west)
        elif cont == "Europe":
            for r in rings:
                if ring_bbox(r)[2] < -30:
                    globe_regions["americas"].append(r)
                else:
                    globe_regions["europe"].append(r)
        elif cont == "Africa":
            globe_regions["africa"].extend(rings)
        elif cont == "Asia":
            globe_regions["asia"].extend(rings)
        else:
            globe_bg.extend(rings)

    region_objs: list[dict] = []
    for rid, raw_rings in globe_regions.items():
        polys = _simplify_and_subdivide_lonlat(raw_rings, epsilon_deg=0.5, min_area_deg2=1.5)
        meta = GLOBE_META[rid]
        cx, cy = meta["center"]
        if not any(point_in_ring(cx, cy, [(pt[0], pt[1]) for pt in p]) for p in polys):
            raise ValueError(f"Globe center {meta['center']} is not inside {rid} polygons")
        node = nodes[rid]
        region_objs.append({
            "id": rid,
            "kind": node["kind"],
            "label": node["label"],
            "color": REGION_COLORS.get(rid, "teal"),
            "center": meta["center"],
            "focus": meta["focus"],
            "polygons": polys,
        })

    bg_polys = _simplify_and_subdivide_lonlat(globe_bg, epsilon_deg=0.6, min_area_deg2=2.0)
    bg_polys.extend(_simplify_antarctica_polar(antarctica_rings, epsilon_deg=0.6))
    return {
        "id": "globe",
        "background": bg_polys,
        "regions": region_objs,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    built = build_all()
    total_bytes = 0
    for level_id, data in built.items():
        path = OUT_DIR / f"{level_id}.json"
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
        path.write_text(text, encoding="utf-8")
        total_bytes += len(text.encode("utf-8"))
        callouts = [r["id"] for r in data["regions"] if r["callout"]]
        print(f"wrote {path.relative_to(ROOT)} ({len(text) / 1024:.1f} KB, {len(data['regions'])} regions, callouts={callouts})")
    globe_data = build_globe()
    globe_path = OUT_DIR / "globe.json"
    globe_text = json.dumps(globe_data, ensure_ascii=False, separators=(",", ":")) + "\n"
    globe_path.write_text(globe_text, encoding="utf-8")
    total_bytes += len(globe_text.encode("utf-8"))
    globe_pts = sum(len(p) for p in globe_data["background"]) + sum(
        len(p) for r in globe_data["regions"] for p in r["polygons"]
    )
    print(f"wrote {globe_path.relative_to(ROOT)} ({len(globe_text) / 1024:.1f} KB, {globe_pts} points)")
    print(f"total size across {len(built) + 1} map files: {total_bytes / 1024:.1f} KB")


if __name__ == "__main__":
    main()
