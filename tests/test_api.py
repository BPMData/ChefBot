"""OpenRouter requests and replies (offline: every response here is canned), plus the scheduled API checks."""
import asyncio
import base64
import importlib.util
import json
import re
from datetime import date
from pathlib import Path

import httpx
import pytest

from chefbot import api, prompts
from chefbot.history import Conversation, History

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("api_check", ROOT / "tools" / "api_check.py")
api_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(api_check)


def _chef(handler) -> api.ChefBotAPI:
    return api.ChefBotAPI("k", httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def _reply(message: dict) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": message}]})


# ---------------------------------------------------------------- photo reading and dish pictures

def test_read_ingredients_sends_the_photo_to_the_vision_model():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return _reply({"content": ' "eggs, spinach, feta" '})

    assert asyncio.run(_chef(handler).read_ingredients(b"\x89PNG", "image/png")) == "eggs, spinach, feta"
    b = seen["body"]
    assert b["model"] == api.MODELS[api.PHOTO_MODEL].id and b["reasoning"]["effort"] == "low"
    text, image = b["messages"][0]["content"]
    assert text["text"] == prompts.INGREDIENTS_FROM_PHOTO
    assert image["image_url"]["url"] == "data:image/png;base64," + base64.b64encode(b"\x89PNG").decode()


def test_read_ingredients_no_food_is_empty():
    assert asyncio.run(_chef(lambda r: _reply({"content": "NO FOOD here"})).read_ingredients(b"x")) == ""
    assert asyncio.run(_chef(lambda r: _reply({"content": None})).read_ingredients(b"x")) == ""


def test_dish_photo_decodes_the_returned_image():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        url = "data:image/png;base64," + base64.b64encode(b"picture-bytes").decode()
        return _reply({"content": "", "images": [{"type": "image_url", "image_url": {"url": url}}]})

    assert asyncio.run(_chef(handler).dish_photo("Shakshuka")) == b"picture-bytes"
    assert seen["body"]["model"] == api.IMAGE_MODEL and "image" in seen["body"]["modalities"]
    assert "Shakshuka" in seen["body"]["messages"][0]["content"]


def test_dish_photo_without_an_image_says_so():
    with pytest.raises(api.ApiError, match="didn't return a picture"):
        asyncio.run(_chef(lambda r: _reply({"content": "I can't draw that."})).dish_photo("Soup"))


# ---------------------------------------------------------------- errors people see

@pytest.mark.parametrize("status, words", [
    (402, "out of credits"),
    (429, "Too many requests"),
    (503, "OpenRouter error 503: upstream down"),
])
def test_http_errors_have_plain_messages(status, words):
    handler = lambda r: httpx.Response(status, json={"error": {"message": "upstream down"}})
    with pytest.raises(api.ApiError, match=words):
        asyncio.run(_chef(handler).dish_photo("x"))
    with pytest.raises(api.ApiError, match=words):
        asyncio.run(_collect(_chef(handler)))


def test_error_body_that_isnt_json_still_reads_well():
    with pytest.raises(api.ApiError, match="OpenRouter error 502: <html>Bad gateway"):
        asyncio.run(_chef(lambda r: httpx.Response(502, text="<html>Bad gateway</html>")).dish_photo("x"))


def test_unreachable_is_a_connection_error():
    def handler(request):
        raise httpx.ConnectError("no network")
    with pytest.raises(api.ApiError, match="Couldn't reach OpenRouter"):
        asyncio.run(_chef(handler).dish_photo("x"))


async def _collect(chef):
    return [c async for c in chef.stream_chat([{"role": "user", "content": "hi"}])]


def test_stream_skips_garbled_lines_and_stops_at_done():
    body = "\n\n".join([
        ": OPENROUTER PROCESSING",
        'data: {"choices": [{"delta": {"content": "Soup "}}]}',
        "data: {not json",
        'data: {"choices": [{"delta": {}}]}',
        'data: {"choices": [{"delta": {"content": "time"}}]}',
        "data: [DONE]",
        'data: {"choices": [{"delta": {"content": " after the end"}}]}',
    ]).encode()
    chunks = asyncio.run(_collect(_chef(lambda r: httpx.Response(200, content=body))))
    assert "".join(c.text for c in chunks if c.kind == "text") == "Soup time"


def test_unknown_model_falls_back_to_the_default():
    seen = {}

    def handler(request):
        seen["model"] = json.loads(request.content)["model"]
        return httpx.Response(200, content=b"data: [DONE]\n\n")

    async def run():
        return [c async for c in _chef(handler).stream_chat([], "retired-model")]
    asyncio.run(run())
    assert seen["model"] == api.MODELS[api.DEFAULT_MODEL].id


# ---------------------------------------------------------------- settings that must stay consistent

def test_model_settings_are_consistent():
    assert api.DEFAULT_MODEL in api.MODELS and api.DEFAULT_EFFORT in api.EFFORTS
    assert api.MODELS[api.PHOTO_MODEL].vision, "the photo model must be able to read photos"


EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F️]")


def test_no_emojis_in_prompts():
    texts = [v for v in vars(prompts).values() if isinstance(v, str)]
    texts += [prompts.system_prompt(prompts.DEFAULT_AUDIENCE, label) for label in prompts.CUISINES]
    texts += [prompts.first_message("eggs"), prompts.dish_photo_prompt("Soup")]
    assert not [t[:60] for t in texts if EMOJI.search(t)]


# ---------------------------------------------------------------- saved recipes survive a damaged file

def test_unreadable_saved_recipes_are_kept_aside_not_overwritten(tmp_path):
    h = History(tmp_path)
    h.file.write_text('[{"id": "abc", "messages": [', encoding="utf-8")      # cut off mid-write
    assert h.load() == []
    backups = list(tmp_path.glob("conversations.unreadable-*.json"))
    assert len(backups) == 1 and backups[0].read_text(encoding="utf-8").startswith('[{"id": "abc"')
    h.save(Conversation(messages=[{"role": "system", "content": "s"}]))     # the next save can't touch it
    assert backups[0].exists() and len(h.load()) == 1


def test_saved_recipes_that_arent_a_list_are_kept_aside(tmp_path):
    h = History(tmp_path)
    h.file.write_text('{"oops": true}', encoding="utf-8")
    assert h.load() == [] and list(tmp_path.glob("conversations.unreadable-*.json"))


# ---------------------------------------------------------------- the scheduled checks' own logic

def _listing(**changes):
    models = {m.id: {"id": m.id, "supported_parameters": ["reasoning", "max_tokens"],
                     "architecture": {"input_modalities": ["text", "image"] if m.vision else ["text"],
                                      "output_modalities": ["text"]}}
              for m in api.MODELS.values()}
    models[api.IMAGE_MODEL] = {"id": api.IMAGE_MODEL, "supported_parameters": [],
                               "architecture": {"input_modalities": ["text"], "output_modalities": ["image", "text"]}}
    for model_id, change in changes.items():
        if change is None:
            del models[model_id]
        else:
            models[model_id].update(change)
    return list(models.values())


def test_check_listing_passes_today():
    assert api_check.check_listing(_listing()) == ([], [])


def test_check_listing_spots_what_breaks_chefbot():
    default, photo = api.MODELS[api.DEFAULT_MODEL].id, api.MODELS[api.PHOTO_MODEL].id
    errors, _ = api_check.check_listing(_listing(**{
        default: {"supported_parameters": ["max_tokens"]},
        photo: {"architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}},
        api.IMAGE_MODEL: None,
    }))
    assert any(default in e and "reasoning" in e for e in errors)
    assert any(photo in e and "images" in e for e in errors)
    assert any(api.IMAGE_MODEL in e and "no longer listed" in e for e in errors)


def test_check_listing_warns_then_fails_as_retirement_nears():
    default = api.MODELS[api.DEFAULT_MODEL].id
    listing = _listing(**{default: {"expiration_date": "2027-06-01"}})
    errors, warnings = api_check.check_listing(listing, today=date(2026, 11, 1))
    assert not errors and "retire" in warnings[0]
    errors, _ = api_check.check_listing(listing, today=date(2027, 5, 20))
    assert "retire" in errors[0]


def test_check_endpoints_matches_the_provider_however_its_spelled():
    glm = api.MODELS[api.DEFAULT_MODEL]
    ok = {"data": {"endpoints": [{"provider_name": "Z.AI", "tag": "z-ai/fp8"}, {"provider_name": "DeepInfra"}]}}
    assert api_check.check_endpoints(glm, ok) == []
    gone = {"data": {"endpoints": [{"provider_name": "DeepInfra", "tag": "deepinfra"}]}}
    assert "no longer hosts it" in api_check.check_endpoints(glm, gone)[0]
    assert "changed shape" in api_check.check_endpoints(glm, {"models": []})[0]


def test_paid_checks_skip_without_a_key(monkeypatch, capsys):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr("sys.argv", ["api_check.py", "recipe"])
    assert api_check.main() == 0 and "skipped" in capsys.readouterr().out


def test_the_food_photo_is_a_real_png():
    from PIL import Image
    import io
    assert Image.open(io.BytesIO(api_check._food_photo())).format == "PNG"
