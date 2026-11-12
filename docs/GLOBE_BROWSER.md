# Brief: a spinnable globe for the top of "Browse by map"

You are working in the ChefBot repo at `/Users/murphb/Documents/Github/ChefBot`. Read `CLAUDE.md` and
`HANDOFF.md` first: they hold the ground rules (the repo is public, never commit secrets, no emojis anywhere,
dark theme by default, Fraunces + DM Sans, work on a branch and open a pull request into `main`, never merge
it yourself).

"Browse by map" is already built and merged; `docs/BROWSE_BY_MAP.md` is the brief it was built from, and the
"Browse by map" entry in `HANDOFF.md` describes what exists. Read these before starting:

- `src/chefbot/maps.py`: level loading, `hit_test`, `has_sublevel`, `region_for_cuisine`.
- `src/chefbot/maps/*.json` and `tools/build_map_data.py`: the projected, simplified map data and its builder.
- `src/main.py`: `_render_map_level`, `_on_map_canvas_tap`, `_trigger_map_region` and the map-view code around
  them (search for `map_stack`).
- `tests/test_maps.py`.

## What to build

Replace only the **world level** of the map browser with a 3D-looking globe. Everything below it (the five
continent maps, the country maps, call-outs, the info sheet, its mini-map) stays exactly as it is.

1. **The globe.** An orthographic (seen-from-space) globe of the earth, with the five continents (Americas,
   Asia, Europe, Near East, Africa) filled in their existing `MAP_PALETTE` colours and the rest of the land muted,
   on a dark ocean disc with a subtle rim or shading so it reads as a sphere. Continent labels sit on the globe
   and only show for continents facing the viewer.
2. **It should feel physical:**
   - Drag with one finger to spin it (east-west and a limited north-south tilt, so it never turns upside down).
   - A flick keeps it spinning, slowing to a stop (momentum with friction).
   - Pinch to zoom in and out, within sensible limits.
   - Optional, Bryan's call: a slow idle spin until the first touch. Make it easy to turn off.
3. **Choosing a continent.** Tapping a continent highlights it, then the globe smoothly rotates to centre it
   and zooms toward it (about half a second, eased), then hands over to that continent's existing flat map.
   Back from a continent returns to the globe still facing that continent, not reset to the start.
4. **Only the globe moves.** Dragging spins the globe, but the flat continent and country maps keep their
   current behaviour (pinch-zoom; panning only while zoomed in, never past the edges; see PR #23).
5. **Phone first.** It has to feel smooth on Bryan's Android phone (a sideloaded APK; see "Android" in
   `HANDOFF.md`), then look right on desktop and in the browser.

## How to draw it in Flet

ChefBot uses Flet 1.0.5, which has no 3D or globe control. The likely route, using pieces the app already uses:

- `flet.canvas.Canvas` redrawn with an orthographic projection of the world outlines for the current rotation
  and zoom. Clip to the visible hemisphere (drop or cut paths that cross to the back of the sphere).
- `ft.GestureDetector` for drag (`on_pan_*`), pinch (`on_scale_*`) and tap. Tapping runs the inverse projection
  to latitude and longitude, then a point-in-polygon test in lat/lon.
- Momentum and the "fly to continent" animation driven from Python with a short async loop.

The risk is speed: every frame is a Python round trip plus a full canvas redraw. Keep it light:

- Ship a separate, coarser lat/lon outline file for the globe (for example `src/chefbot/maps/globe.json`, built
  by `tools/build_map_data.py` from the same Natural Earth country file). The existing world JSON is already
  projected flat, so it can't be reused directly.
- Aim for a few thousand points total, throttle redraws to what the device keeps up with, and drop detail while
  spinning if needed.
- Measure on the phone early, before polishing. If the canvas route can't get smooth, say so in the pull request
  with what you measured, and propose an alternative (for example a WebView with a small JavaScript globe on
  Android only, keeping the flat world map elsewhere) rather than shipping something laggy. Don't add a
  dependency or download anything without asking Bryan.

## Look and feel

- Use the app's theme colours (`ft.Colors.*`) and the existing `MAP_PALETTE`, in dark and light themes.
- Keep the existing top bar: Back arrow and "Browse by map" heading. Update the subtitle to say how to use the
  globe (for example "Spin the globe and tap a continent.").
- No emojis anywhere; Material icons only.

## Tests

Add to `tests/` (run `.venv/bin/python -m pytest`):

- The projection and its inverse round-trip, and points on the back of the globe are not visible or tappable.
- A tap at the projected centre of each continent hits that continent, at a few different rotations.
- Every continent in the cuisine tree has a region on the globe.
- The builder reproduces the committed `globe.json` when the source shapefiles are present (as the existing map
  data test does).

## Checking it

Run it in a browser with `.venv/bin/flet run --web --port 8551 src/main.py` at phone width (375 x 812) and on
desktop: spin, flick, pinch, tap each continent, use Back, and check that the continent maps still behave as
before. Restart the server after code changes. Bryan will test the APK on his phone. Note in the pull request
what you tested and how smooth it was.

## Finishing

- Update `HANDOFF.md`: what was built, the decisions you made, and anything left to do.
- Work on a new branch; commit messages end with a `Co-Authored-By` line for the model that wrote them.
- Open a pull request into `main` and make sure the GitHub Actions tests pass. Do not merge it.
