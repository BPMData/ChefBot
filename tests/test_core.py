import asyncio
import json

import httpx
import pytest

from chefbot import api, prompts
from chefbot.history import Conversation, History
from chefbot.recipe import extract_title


# ---------------------------------------------------------------- prompts

def test_every_cuisine_builds_a_prompt():
    for label, (name, flavors) in prompts.CUISINES.items():
        p = prompts.system_prompt(prompts.DEFAULT_AUDIENCE, label)
        if name:
            assert name in p and flavors[:20] in p
        else:
            assert "from any cuisine or culture" in p


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
