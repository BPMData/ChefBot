# Map data sources

The "Browse by map" view and the cuisine info-sheet mini-maps use pre-projected, simplified outlines built by
`tools/build_map_data.py` into `src/chefbot/maps/*.json` from the following public-domain vector datasets:

1. **Natural Earth 1:10m Admin 0 — Countries (Palestine point-of-view edition, `ne_10m_admin_0_countries_pse`, v5.1.1)**
   - **Used for:** world continent outlines, continent-level country outlines, and Caribbean island outlines.
     Every country border comes from this single edition so adjacent outlines share consistent geometry.
   - **URL:** https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/
     (point-of-view editions: https://www.naturalearthdata.com/blog/admin-0-countries-point-of-views/)
   - **Licence:** Public domain (https://www.naturalearthdata.com/about/terms-of-use/). Made with Natural Earth.

2. **Natural Earth 1:10m Admin 1 — States, Provinces (`ne_10m_admin_1_states_provinces`, v5.1.1)**
   - **Used for:** United States states, Mexican states, Chinese provinces and municipalities, Japanese prefectures,
     Indian states and union territories, and Italian provinces (grouped into regions via the dataset's `region` field).
   - **URL:** https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/
   - **Licence:** Public domain (https://www.naturalearthdata.com/about/terms-of-use/). Made with Natural Earth.

3. **U.S. Census Bureau Cartographic Boundary File — County and Equivalent, 1:500,000 (`cb_2025_us_county_500k`, 2025)**
   - **Used for:** the 64 parishes of Louisiana (`STATEFP` 22) only, dividing the state into Acadiana (`us_cajun`,
     22 parishes), the New Orleans area (`us_creole`, Orleans, Jefferson, St. Bernard and Plaquemines parishes),
     and the remaining 38 parishes in `us_southern_soul`.
   - **URL:** https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
   - **Licence:** Public domain (U.S. Government work, 17 U.S.C. § 105).

## Rebuilding the map data

Unzip the three source archives into `assets/maps/source/` (git-ignored) and run:

```bash
.venv/bin/python tools/build_map_data.py
```
