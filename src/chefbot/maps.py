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
_GLOBE: dict = json.loads((MAPS_DIR / "globe.json").read_text(encoding="utf-8"))


def _precompute_ring_3d(ring: list[list[float]]) -> tuple:
    pts: list[tuple[float, float, float]] = []
    for lon, lat in ring:
        rlon = math.radians(lon)
        rlat = math.radians(lat)
        cl = math.cos(rlat)
        pts.append((cl * math.cos(rlon), cl * math.sin(rlon), math.sin(rlat)))
    open_pts = pts[:-1] if len(pts) > 1 else pts
    n = max(1, len(open_pts))
    sx = sum(p[0] for p in open_pts) / n
    sy = sum(p[1] for p in open_pts) / n
    sz = sum(p[2] for p in open_pts) / n
    norm = math.sqrt(sx * sx + sy * sy + sz * sz) or 1.0
    bx, by, bz = sx / norm, sy / norm, sz / norm
    cos_r = min(p[0] * bx + p[1] * by + p[2] * bz for p in pts)
    sin_r = math.sqrt(max(0.0, 1.0 - cos_r * cos_r)) if cos_r > 0.0 else 1.0
    is_major = len(ring) >= 8
    return (tuple(pts), bx, by, bz, cos_r, sin_r, is_major)


_GLOBE_3D: dict = {
    "background": [_precompute_ring_3d(p) for p in _GLOBE["background"]],
    "regions": {
        reg["id"]: [_precompute_ring_3d(p) for p in reg["polygons"]]
        for reg in _GLOBE["regions"]
    },
}


def get_globe() -> dict:
    """Return the coarse lat/lon globe dataset."""
    return _GLOBE


def globe_region(region_id: str) -> dict | None:
    """Return a globe continent dict by id, or None."""
    for reg in _GLOBE["regions"]:
        if reg["id"] == region_id:
            return reg
    return None


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


def _globe_matrix(center_lon: float, center_lat: float) -> tuple[float, float, float, float, float, float, float, float]:
    l0 = math.radians(center_lon)
    p0 = math.radians(center_lat)
    cl0, sl0 = math.cos(l0), math.sin(l0)
    cp0, sp0 = math.cos(p0), math.sin(p0)
    return (
        -sl0,
        cl0,
        -sp0 * cl0,
        -sp0 * sl0,
        cp0,
        cp0 * cl0,
        cp0 * sl0,
        sp0,
    )


def project_globe_vector(
    lon: float,
    lat: float,
    center_lon: float,
    center_lat: float,
) -> tuple[float, float, float]:
    """Project (lon, lat) in degrees to unit-sphere view space (x, y, z) where z >= 0 faces the viewer."""
    dlon = math.radians(lon - center_lon)
    phi = math.radians(lat)
    phi0 = math.radians(center_lat)
    cp, sp = math.cos(phi), math.sin(phi)
    cp0, sp0 = math.cos(phi0), math.sin(phi0)
    cdl, sdl = math.cos(dlon), math.sin(dlon)
    x3 = cp * sdl
    y3 = cp0 * sp - sp0 * cp * cdl
    z3 = sp0 * sp + cp0 * cp * cdl
    return x3, y3, z3


def project_globe_point(
    lon: float,
    lat: float,
    center_lon: float,
    center_lat: float,
    cx: float,
    cy: float,
    radius: float,
) -> tuple[float, float] | None:
    """Orthographically project (lon, lat) to screen (x, y), or None if on the back of the globe."""
    x3, y3, z3 = project_globe_vector(lon, lat, center_lon, center_lat)
    if z3 < 0.0:
        return None
    return cx + radius * x3, cy - radius * y3


def inverse_globe_point(
    sx: float,
    sy: float,
    center_lon: float,
    center_lat: float,
    cx: float,
    cy: float,
    radius: float,
) -> tuple[float, float] | None:
    """Inverse orthographic projection from screen (sx, sy) to (lon, lat), or None if outside the disc."""
    if radius <= 0.0:
        return None
    x = (sx - cx) / radius
    y = (cy - sy) / radius
    r2 = x * x + y * y
    if r2 > 1.0:
        return None
    z = math.sqrt(max(0.0, 1.0 - r2))
    phi0 = math.radians(center_lat)
    cp0, sp0 = math.cos(phi0), math.sin(phi0)
    sin_phi = max(-1.0, min(1.0, y * cp0 + z * sp0))
    phi = math.asin(sin_phi)
    dlon = math.atan2(x, z * cp0 - y * sp0)
    lon = ((center_lon + math.degrees(dlon) + 180.0) % 360.0) - 180.0
    lat = math.degrees(phi)
    return lon, lat


def hit_test_globe_latlon(lon: float, lat: float) -> str | None:
    """Exact point-in-polygon check in geographic (lon, lat) degrees across the 5 continents."""
    for reg in _GLOBE["regions"]:
        for poly in reg["polygons"]:
            if point_in_ring(lon, lat, poly):
                return reg["id"]
    return None


def hit_test_globe(
    sx: float,
    sy: float,
    center_lon: float,
    center_lat: float,
    cx: float,
    cy: float,
    radius: float,
    tolerance_px: float = 6.0,
) -> str | None:
    """Return the continent id at screen point (sx, sy) on the globe, or None if ocean/back/outside."""
    inv = inverse_globe_point(sx, sy, center_lon, center_lat, cx, cy, radius)
    if inv is None:
        return None
    lon, lat = inv
    hit = hit_test_globe_latlon(lon, lat)
    if hit is not None:
        return hit

    if tolerance_px > 0.0 and radius > 0.0:
        tol_deg = min(5.0, math.degrees(tolerance_px / radius))
        cos_lat = max(0.2, math.cos(math.radians(lat)))
        best_d = tol_deg
        best_id: str | None = None
        for reg in _GLOBE["regions"]:
            for poly in reg["polygons"]:
                for i in range(len(poly) - 1):
                    lon1, lat1 = poly[i]
                    lon2, lat2 = poly[i + 1]
                    if max(lat1, lat2) < lat - tol_deg or min(lat1, lat2) > lat + tol_deg:
                        continue
                    x1 = (((lon1 - lon + 180.0) % 360.0) - 180.0) * cos_lat
                    y1 = lat1 - lat
                    x2 = (((lon2 - lon + 180.0) % 360.0) - 180.0) * cos_lat
                    y2 = lat2 - lat
                    if max(x1, x2) < -tol_deg or min(x1, x2) > tol_deg:
                        continue
                    dx, dy = x2 - x1, y2 - y1
                    l2 = dx * dx + dy * dy
                    if l2 == 0.0:
                        d = math.hypot(x1, y1)
                    else:
                        t = max(0.0, min(1.0, -(x1 * dx + y1 * dy) / l2))
                        d = math.hypot(x1 + t * dx, y1 + t * dy)
                    if d <= best_d:
                        best_d = d
                        best_id = reg["id"]
        return best_id
    return None


def _clip_and_project_ring_3d(
    ring_info: tuple,
    mat: tuple[float, float, float, float, float, float, float, float],
    cx: float,
    cy: float,
    radius: float,
) -> list[tuple[float, float]] | None:
    pts, bx, by, bz, cos_r, sin_r, _ = ring_info
    m00, m01, m10, m11, m12, m20, m21, m22 = mat
    dot_c = bx * m20 + by * m21 + bz * m22
    if cos_r > 0.0:
        if dot_c < -sin_r - 1e-6:
            return None
        if dot_c > sin_r + 1e-6:
            return [
                (cx + radius * (m00 * x + m01 * y), cy - radius * (m10 * x + m11 * y + m12 * z))
                for x, y, z in pts
            ]

    verts = [
        (m00 * x + m01 * y, m10 * x + m11 * y + m12 * z, m20 * x + m21 * y + m22 * z)
        for x, y, z in pts
    ]
    n = len(verts) - 1
    start = None
    for i in range(n):
        if verts[i][2] >= 0.0:
            start = i
            break
    if start is None:
        return None

    prev = verts[start]
    clipped: list[tuple[float, float]] = [(prev[0], prev[1])]
    exit_pt: tuple[float, float] | None = None
    for step in range(1, n + 1):
        cur = verts[(start + step) % n]
        pz, cz = prev[2], cur[2]
        if pz >= 0.0 and cz >= 0.0:
            clipped.append((cur[0], cur[1]))
        elif pz >= 0.0 and cz < 0.0:
            t = pz / (pz - cz)
            hx = prev[0] + t * (cur[0] - prev[0])
            hy = prev[1] + t * (cur[1] - prev[1])
            norm = math.hypot(hx, hy) or 1.0
            exit_pt = (hx / norm, hy / norm)
            clipped.append(exit_pt)
        elif pz < 0.0 and cz >= 0.0:
            t = pz / (pz - cz)
            hx = prev[0] + t * (cur[0] - prev[0])
            hy = prev[1] + t * (cur[1] - prev[1])
            norm = math.hypot(hx, hy) or 1.0
            enter_pt = (hx / norm, hy / norm)
            if exit_pt is not None:
                a0 = math.atan2(exit_pt[1], exit_pt[0])
                a1 = math.atan2(enter_pt[1], enter_pt[0])
                da = (a1 - a0 + math.pi) % (2.0 * math.pi) - math.pi
                arc_steps = max(1, int(abs(da) / 0.12))
                for k in range(1, arc_steps):
                    ang = a0 + da * (k / arc_steps)
                    clipped.append((math.cos(ang), math.sin(ang)))
            clipped.append(enter_pt)
            clipped.append((cur[0], cur[1]))
            exit_pt = None
        prev = cur

    if len(clipped) < 3:
        return None
    return [(cx + radius * x, cy - radius * y) for x, y in clipped]


def project_globe_polygons(
    center_lon: float,
    center_lat: float,
    cx: float,
    cy: float,
    radius: float,
    fast: bool = False,
) -> tuple[list[list[tuple[float, float]]], dict[str, list[list[tuple[float, float]]]]]:
    """Project visible globe polygons into screen coordinates, clipped to the front hemisphere."""
    mat = _globe_matrix(center_lon, center_lat)
    bg_out: list[list[tuple[float, float]]] = []
    for ring_info in _GLOBE_3D["background"]:
        if fast and not ring_info[6]:
            continue
        proj = _clip_and_project_ring_3d(ring_info, mat, cx, cy, radius)
        if proj:
            bg_out.append(proj)

    regions_out: dict[str, list[list[tuple[float, float]]]] = {}
    for rid, ring_list in _GLOBE_3D["regions"].items():
        polys: list[list[tuple[float, float]]] = []
        for ring_info in ring_list:
            if fast and not ring_info[6]:
                continue
            proj = _clip_and_project_ring_3d(ring_info, mat, cx, cy, radius)
            if proj:
                polys.append(proj)
        regions_out[rid] = polys
    return bg_out, regions_out


def _build_graticule_lines(step_deg: int = 30) -> list[tuple[tuple[float, float, float], ...]]:
    lines: list[tuple[tuple[float, float, float], ...]] = []
    for lat in range(-60, 61, step_deg):
        rlat = math.radians(lat)
        cl, sl = math.cos(rlat), math.sin(rlat)
        pts = []
        for lon in range(-180, 181, 8):
            rlon = math.radians(lon)
            pts.append((cl * math.cos(rlon), cl * math.sin(rlon), sl))
        lines.append(tuple(pts))
    for lon in range(-180, 180, step_deg):
        rlon = math.radians(lon)
        co, so = math.cos(rlon), math.sin(rlon)
        pts = []
        for lat in range(-80, 81, 8):
            rlat = math.radians(lat)
            cl = math.cos(rlat)
            pts.append((cl * co, cl * so, math.sin(rlat)))
        lines.append(tuple(pts))
    return lines


_GRATICULE_3D = _build_graticule_lines(30)


def project_globe_graticule(
    center_lon: float,
    center_lat: float,
    cx: float,
    cy: float,
    radius: float,
) -> list[list[tuple[float, float]]]:
    """Return visible screen polylines for latitude/longitude graticule curves."""
    m00, m01, m10, m11, m12, m20, m21, m22 = _globe_matrix(center_lon, center_lat)
    segments: list[list[tuple[float, float]]] = []
    for line in _GRATICULE_3D:
        cur_seg: list[tuple[float, float]] = []
        prev: tuple[float, float, float] | None = None
        for x, y, z in line:
            vx = m00 * x + m01 * y
            vy = m10 * x + m11 * y + m12 * z
            vz = m20 * x + m21 * y + m22 * z
            if prev is None:
                if vz >= 0.0:
                    cur_seg.append((cx + radius * vx, cy - radius * vy))
            else:
                px, py, pz = prev
                if pz >= 0.0 and vz >= 0.0:
                    cur_seg.append((cx + radius * vx, cy - radius * vy))
                elif pz >= 0.0 and vz < 0.0:
                    t = pz / (pz - vz)
                    hx = px + t * (vx - px)
                    hy = py + t * (vy - py)
                    norm = math.hypot(hx, hy) or 1.0
                    cur_seg.append((cx + radius * hx / norm, cy - radius * hy / norm))
                    if len(cur_seg) >= 2:
                        segments.append(cur_seg)
                    cur_seg = []
                elif pz < 0.0 and vz >= 0.0:
                    t = pz / (pz - vz)
                    hx = px + t * (vx - px)
                    hy = py + t * (vy - py)
                    norm = math.hypot(hx, hy) or 1.0
                    cur_seg = [
                        (cx + radius * hx / norm, cy - radius * hy / norm),
                        (cx + radius * vx, cy - radius * vy),
                    ]
            prev = (vx, vy, vz)
        if len(cur_seg) >= 2:
            segments.append(cur_seg)
    return segments
