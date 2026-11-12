import asyncio
import importlib.util
import json
from pathlib import Path

import httpx
import pytest

from chefbot import api, cuisines, prompts
from chefbot.history import Conversation, History
from chefbot.recipe import extract_title

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- prompts

def test_every_cuisine_builds_a_prompt():
    assert "from any cuisine or culture" in prompts.system_prompt(prompts.DEFAULT_AUDIENCE, prompts.NO_CUISINE)
    leaves = cuisines.leaves()
    assert len(leaves) >= 58
    for node in leaves:
        p = prompts.system_prompt(prompts.DEFAULT_AUDIENCE, node["id"])
        assert node["prompt_name"] in p
        assert node["flavors"][0] in p


def test_allergen_rule_names_nine_including_sesame():
    rule = prompts.RESTRICTIONS["Free of major food allergens"]
    assert "FALCPA" in rule and "FALCA " not in rule
    assert "nine" in rule and "sesame" in rule.lower()


def test_restrictions_override_classic_flavors():
    p = prompts.system_prompt(prompts.DEFAULT_AUDIENCE, "Korean", restrictions=["Gluten-free"])
    assert "gluten-free" in p.lower()
    assert "override the classic flavors" in p


def test_dessert_and_main_dish_wording():
    assert "DESSERT" in prompts.system_prompt(prompts.DEFAULT_AUDIENCE, "French", dessert=True)
    assert "not a dessert" in prompts.system_prompt(prompts.DEFAULT_AUDIENCE, "French", dessert=False)


def test_prompt_explains_follow_up_edits():
    assert "write out the complete revised recipe" in prompts.system_prompt(prompts.DEFAULT_AUDIENCE, "Thai")


def test_first_message_includes_must_not():
    m = prompts.first_message("eggs, rice", must_not="peanuts")
    assert '"""eggs, rice"""' in m and "peanuts" in m and '"Recipe Title: "' in m
    assert "VERY IMPORTANT" not in prompts.first_message("eggs")


# ---------------------------------------------------------------- titles

@pytest.mark.parametrize("text,title", [
    ("intro\nRecipe Title: Lemon Chicken\nsteps", "Lemon Chicken"),
    ("**Recipe Title: Lemon Chicken**", "Lemon Chicken"),
    ("## Recipe Title: Lemon Chicken", "Lemon Chicken"),
    ("Recipe Title: Old\n...\nRecipe Title: New One", "New One"),
    ("no title here", None),
])
def test_extract_title(text, title):
    assert extract_title(text) == title


# ---------------------------------------------------------------- history

def test_history_round_trip(tmp_path):
    h = History(tmp_path)
    c = Conversation(title="Soup", messages=[{"role": "system", "content": "s"}, {"role": "user", "content": "u"}])
    h.save(c)
    h.save_photo(c, 2, b"png-bytes")
    h.save(c)
    loaded = h.load()
    assert len(loaded) == 1 and loaded[0].title == "Soup" and loaded[0].photos == {"2": f"{c.id}-2.png"}
    assert loaded[0].chat_messages() == c.messages
    h.delete(c.id)
    assert h.load() == [] and not list((tmp_path / "photos").iterdir())


# ---------------------------------------------------------------- streaming (fake server)

def _sse(*objs):
    lines = [": OPENROUTER PROCESSING", ""]
    for o in objs:
        lines += [f"data: {o if isinstance(o, str) else json.dumps(o)}", ""]
    return "\n".join(lines).encode()


def _client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def _collect(chef, msgs):
    return [c async for c in chef.stream_chat(msgs)]


def test_stream_parses_text_thinking_and_usage():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        body = _sse({"choices": [{"delta": {"reasoning": "hmm"}}]},
                    {"choices": [{"delta": {"content": "Hello "}}]},
                    {"choices": [{"delta": {"content": "chef"}}]},
                    {"choices": [], "usage": {"cost": 0.001}},
                    "[DONE]")
        return httpx.Response(200, content=body, headers={"content-type": "text/event-stream"})

    chef = api.ChefBotAPI("k", _client(handler))
    chunks = asyncio.run(_collect(chef, [{"role": "user", "content": "hi"}]))
    assert "".join(c.text for c in chunks if c.kind == "text") == "Hello chef"
    assert any(c.kind == "thinking" for c in chunks)
    assert any(c.kind == "usage" and c.usage["cost"] == 0.001 for c in chunks)
    b = seen["body"]
    assert b["model"] == "z-ai/glm-5.3" and b["reasoning"]["effort"] == "high"
    assert b["provider"]["order"] == ["z-ai"] and b["max_tokens"] >= 16000 and b["stream"] is True


def test_stream_error_chunk_raises():
    def handler(request):
        return httpx.Response(200, content=_sse({"error": {"message": "boom"}}))

    with pytest.raises(api.ApiError, match="boom"):
        asyncio.run(_collect(api.ChefBotAPI("k", _client(handler)), []))


def test_bad_key_gives_friendly_message():
    def handler(request):
        return httpx.Response(401, json={"error": {"message": "No auth credentials found"}})

    with pytest.raises(api.ApiError, match="API key"):
        asyncio.run(_collect(api.ChefBotAPI("k", _client(handler)), []))


def test_prune_photos_keeps_only_used(tmp_path):
    h = History(tmp_path)
    c = Conversation(messages=[{"role": "system", "content": "s"}])
    h.save_photo(c, 2, b"keep")
    h.save(c)
    (tmp_path / "photos" / "orphan-9.png").write_bytes(b"x")
    assert h.prune_photos() == 1 and [f.name for f in (tmp_path / "photos").iterdir()] == [f"{c.id}-2.png"]


def test_history_keeps_everything(tmp_path):
    """No cap: the oldest recipe (and its photo) is never dropped to make room."""
    h = History(tmp_path)
    first = Conversation(title="First")
    h.save_photo(first, 2, b"png")
    h.save(first)
    for i in range(80):
        h.save(Conversation(title=f"Recipe {i}"))
    titles = [c.title for c in h.load()]
    assert len(titles) == 81 and "First" in titles
    assert (tmp_path / "photos" / f"{first.id}-2.png").exists()


def test_prune_photos_spares_kept_files(tmp_path):
    """Photos an in-flight edit or reply may still need survive a cleanup."""
    h = History(tmp_path)
    (tmp_path / "photos" / "pending-4.png").write_bytes(b"x")
    (tmp_path / "photos" / "orphan-9.png").write_bytes(b"x")
    assert h.prune_photos(keep={"pending-4.png"}) == 1
    assert [f.name for f in (tmp_path / "photos").iterdir()] == ["pending-4.png"]


def test_dessert_only_flavors_stay_out_of_savory_recipes():
    checked = 0
    for node in cuisines.leaves():
        if not node["sweet_only"]:
            continue
        savory = prompts.system_prompt(prompts.DEFAULT_AUDIENCE, node["id"], dessert=False)
        sweet_prompt = prompts.system_prompt(prompts.DEFAULT_AUDIENCE, node["id"], dessert=True)
        for sw in node["sweet_only"]:
            # Some flavors (like cinnamon or cardamom) can also appear in savory flavors/tips/pitfalls,
            # so check the 'and for desserts, ...' clause specifically, plus any sweet-only item not in savory.
            assert f"and for desserts, {', '.join(node['sweet_only'])}" not in savory
            assert f"and for desserts, {', '.join(node['sweet_only'])}" in sweet_prompt
            if sw not in ", ".join(node["flavors"]) and sw not in " ".join(node["tips"] + node["pitfalls"]):
                assert sw not in savory
            assert sw in sweet_prompt
            checked += 1
    assert checked > 0


def test_signature_ingredients_only_if_the_user_has_them():
    checked = 0
    for node in cuisines.leaves():
        if not node["signature_ingredients"]:
            continue
        p = prompts.system_prompt(prompts.DEFAULT_AUDIENCE, node["id"])
        first_sig = node["signature_ingredients"][0]
        assert first_sig[1:] in p
        assert "use them only if they're in the user's ingredients" in p
        assert "Tips" in p
        checked += 1
    assert checked > 0


def test_cuisine_lists_have_no_shortcuts_or_duplicates():
    cajun = prompts.system_prompt(prompts.DEFAULT_AUDIENCE, "us_cajun")
    assert "never a store-bought blend" in cajun
    for node in cuisines.leaves():
        flavors_str = ", ".join(node["flavors"])
        assert prompts.system_prompt(prompts.DEFAULT_AUDIENCE, node["id"]).count(flavors_str) == 1


def test_every_cuisine_has_an_explainer():
    for node in cuisines.leaves():
        assert node["about"].strip() and node["subtitle"].strip()


def test_louisiana_recipes_never_suggest_file_and_offer_thickeners():
    for nid in ("us_cajun", "us_creole"):
        p = prompts.system_prompt(prompts.DEFAULT_AUDIENCE, nid)
        assert "Never use or suggest filé powder" in p
        assert "xanthan gum weighed in grams" in p
        assert "Never use: filé powder." in p
    for node in cuisines.leaves():
        for fl in node["flavors"]:
            assert "filé" not in fl.lower() and "sassafras" not in fl.lower()


def test_cuisine_validator_catches_dangling_child_and_long_label():
    valid_continent = {
        "id": "americas", "kind": "continent", "label": "The Americas", "subtitle": "s", "about": "a",
        "prompt_name": "", "flavors": [], "sweet_only": [], "signature_ingredients": [],
        "tips": [], "pitfalls": [], "avoid": [], "children": ["cuban"],
    }
    valid_leaf = {
        "id": "cuban", "kind": "cuisine", "label": "Cuban", "subtitle": "s", "about": "a",
        "prompt_name": "Cuban", "flavors": ["garlic"], "sweet_only": [], "signature_ingredients": [],
        "tips": [], "pitfalls": [], "avoid": [], "children": [],
    }
    cuisines.validate([valid_continent, valid_leaf])

    dangling = dict(valid_continent, children=["cuban", "missing_node"])
    with pytest.raises(ValueError, match="dangling child"):
        cuisines.validate([dangling, valid_leaf])

    overlong = dict(valid_leaf, label="A Label Over Twenty Characters")
    with pytest.raises(ValueError, match="exceeds 20 characters"):
        cuisines.validate([valid_continent, overlong])


def test_legacy_ids_map_to_existing_leaves():
    expected_old = {
        "American", "American (Cajun)", "American (Creole)",
        "Chinese (Cantonese - Most common style in US)", "Chinese (Hong Kong)",
        "Chinese (Sichuan)", "Chinese (Shandong)", "Chinese (Jiangsu)",
        "French", "Greek", "North Indian", "South Indian", "Italian",
        "Japanese (Kansai)", "Japanese (Kanto)", "Korean", "Mexican",
        "Peruvian", "Spanish", "Thai", "Turkish", "Vietnamese",
    }
    assert expected_old <= set(cuisines.LEGACY_IDS)
    assert cuisines.LEGACY_IDS["Chinese (Hong Kong)"] == "cantonese"
    leaf_ids = {n["id"] for n in cuisines.leaves()}
    for old_label, new_id in cuisines.LEGACY_IDS.items():
        assert new_id in leaf_ids, f"{old_label!r} mapped to non-leaf {new_id!r}"


def test_build_cuisine_data_reproduces_committed_json():
    spec = importlib.util.spec_from_file_location("build_cuisine_data", ROOT / "tools" / "build_cuisine_data.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    built = builder.build_all()
    for cont_id in ("americas", "asia", "europe", "near_east", "africa"):
        committed = json.loads((ROOT / "src" / "chefbot" / "cuisines" / f"{cont_id}.json").read_text(encoding="utf-8"))
        assert built[cont_id] == committed

