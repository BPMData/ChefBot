# AI Workflow Playbook (ChefBot)

How future AI sessions should plan, research, build, visually evaluate, and ship larger changes in ChefBot without polluting their main context window or shipping unverified model-memory guesses.

---

## Core Loop: Self-Directed Research -> Mechanical Audit -> Isolated Build -> Self-Critique

```
Inspect code & schemas -> Write gap-targeted research prompts
  -> Spawn isolated context-free workers in parallel
  -> Mechanically audit + synthesize into FINDINGS.md & overrides
  -> Implement data + pure logic + UI
  -> Self-evaluate (tests + rendered screenshots / geometry)
  -> Docs, full pytest, PR into main & verify Actions
```

---

## 1. Inspect Schemas, Builders, and Validators First

Before launching any research or writing prompts, read the code that consumes and validates the data:
- Data builders: `tools/build_cuisine_data.py`, `tools/cuisine_overrides.json`, `tools/cuisine_pantry.json`, `tools/build_map_data.py`
- Existing taxonomy & specs: `docs/CUISINE_TREE.md`, `docs/PANTRY_DEFAULTS.md`, `docs/BROWSE_BY_MAP.md`, `docs/GLOBE_BROWSER.md`, `docs/research/third-batch.md`
- Guardrails in tests: `tests/test_core.py`, `tests/test_maps.py`, `tests/test_text_fields.py`

Put every hard constraint directly into the research worker's prompt and output JSON schema upfront (for example: `label <= 20` characters, `subtitle <= 6` words, 6–10 `pantry` staples, no brand names, no generic `salt`, zero overlap with `avoid`).

---

## 2. Write Self-Aware Deep Research Prompts

Design research prompts around known LLM blind spots rather than asking open-ended summaries:
- **Anti-cliché rules:** Explicitly warn workers against export/restaurant clichés, merged neighboring stereotypes (e.g., conflating West & Central India with Punjabi-Mughlai `north_india`, or Tex-Mex cumin/cheddar with Indigenous North American cooking), and post-colonial commodity tropes presented as older traditions.
- **Authoritative sources only:** Require published cookbooks, culinary historians, or national food-composition authorities; reject SEO recipe blogs.
- **Honest uncertainty (`LOW CONFIDENCE`):** Tell workers to tag unstandardized brand-varying sodium/acid numbers or disputed historical claims as `LOW CONFIDENCE` rather than inventing false precision.
- **Cross-region boundary checks:** Ask workers to flag overlaps with existing neighbors (e.g., moving Rajasthan out of `north_india` when adding `central_west_india`).

---

## 3. Fan Out Research in Context-Free Parallel Subagents

Do **not** perform large multi-item web research inline in the coordinator conversation:
- Use `run_workflow` with `parallel(..., lambda item: agent(..., type_name="self", schema=...))` so each research target runs in its own fresh, isolated context window with `search_web` and zero cross-contamination between items.
- Have workers return **compact structured JSON** plus raw citations, writing archival reports to `docs/research/results/raw/<batch>.md` and structured payloads to `docs/research/results/<batch>.json`.
- Keep the main coordinator's context window clean for auditing, architecture, and implementation.

---

## 4. Audit Mechanically and Override Centrally

Never hand-edit generated files under `src/chefbot/cuisines/` or `src/chefbot/maps/`:
1. Run a quick Python audit over the raw research output to catch schema violations, `label`/`subtitle` limits, brand names, emojis, generic `salt`, and app-wide rules (such as `test_louisiana_recipes_never_suggest_file_and_offer_thickeners`, which bans `filé`/`sassafras` across all leaf `flavors`, or `avoid` prefix matching stripping valid `pantry` items in `build_cuisine_data.py`).
2. Record editorial choices, boundary updates, and disputes in `docs/research/FINDINGS.md`.
3. Put fixes in `tools/cuisine_overrides.json` and `PROPER_PREFIXES` / specs in `tools/build_cuisine_data.py`, then regenerate so builder reproducibility tests pass cleanly.

---

## 5. Inspect Source Geometry & Separate Pure Logic from UI

- **Maps & 3D globe:** Inspect shapefile records in `assets/maps/source/` first (antimeridian islands, overseas territories like French Guiana inside `FRA`, Census county/planning-region names). After running `tools/build_map_data.py`, print every generated `label_pos`, `center`, and `callout` coordinate to place non-overlapping `CALLOUT_POSITIONS` before relying on tests.
- **UI architecture:** Put sorting, grouping, search matching, and lineage resolution into pure Python modules (`src/chefbot/history.py`, `src/chefbot/favorites.py`) tested thoroughly with offline `pytest`, keeping `src/main.py` focused on layout and interaction (avoiding `capitalization=` on `ft.TextField` per `tests/test_text_fields.py` and guarding `.update()` against off-screen/unmounted controls).

---

## 6. Autonomous Self-Critique on Visuals & Outputs

When a task involves layout, visual candidates, or rendered graphics (maps, web views, charts, infographics):
- Do **not** ask the user to visually choose between rough options when you can inspect rendered screenshots yourself.
- Capture/save rendered PNGs (for example via headless browser screenshot or plot export), open them directly with multimodal file reading, and evaluate them against concrete criteria: readability at phone width (`375 px`), dark and light contrast, label/chip spacing, zero clipping, and factual alignment with checked sources.
- Note for ChefBot web checks: Flet renders to a single HTML5 `<canvas>`, so keep live web browser checks to a brief screenshot smoke check and include an on-device Android APK rebuild & phone verification checklist in the PR when UI changes.

---

## 7. Ship Cleanly in Stages

1. Commit only on a fresh branch created from up-to-date `main`.
2. Update `README.md`, `HANDOFF.md`, and relevant `docs/` specs to match the shipped behavior.
3. Run `.venv/bin/python -m pytest` after the final edit and confirm all tests pass.
4. Push, open a PR into `main` (never merge it), and watch `gh pr checks <pr> --watch` until GitHub Actions passes.
