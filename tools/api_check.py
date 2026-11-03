"""Scheduled checks that OpenRouter still works the way ChefBot expects (run by .github/workflows/api-checks.yml).

    python tools/api_check.py models     # free, no key: the models ChefBot uses still exist and can do their job
    OPENROUTER_API_KEY=... python tools/api_check.py recipe    # a real recipe, each model, a photo read (~1-2 cents)
    OPENROUTER_API_KEY=... python tools/api_check.py picture   # a real dish picture (~3-4 cents)

Exits 1 if anything is wrong, printing GitHub annotations (::error:: / ::warning::) that say what.
The model ids come from src/chefbot/api.py, so the checks follow the app when a model changes.
"""
import asyncio
import io
import os
import re
import sys
from datetime import date
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from chefbot import api, prompts  # noqa: E402
from chefbot.recipe import extract_title  # noqa: E402

MODELS_URL = "https://openrouter.ai/api/v1/models"
ENDPOINTS_URL = "https://openrouter.ai/api/v1/models/{id}/endpoints"
RETIRING_SOON_DAYS = 30


def _norm(name: str) -> str:
    """'Z.AI', 'z-ai', 'z-ai/fp8' -> 'zai' (provider names and slugs are spelled differently)."""
    return re.sub(r"[^a-z0-9]", "", name.split("/")[0].lower())


# ------------------------------------------------------------------ pure checks (tested offline)

def check_listing(listing: list[dict], today: date | None = None) -> tuple[list[str], list[str]]:
    """Check OpenRouter's model list against what ChefBot needs. Returns (errors, warnings)."""
    today = today or date.today()
    by_id = {m.get("id"): m for m in listing}
    errors, warnings = [], []
    needs = [(m.id, {"reasoning"}, {"image"} if m.vision else set(), set()) for m in api.MODELS.values()]
    needs.append((api.IMAGE_MODEL, set(), set(), {"image"}))
    for model_id, params, inputs, outputs in needs:
        m = by_id.get(model_id)
        if m is None:
            errors.append(f"{model_id}: no longer listed on OpenRouter (renamed or retired?)")
            continue
        arch = m.get("architecture") or {}
        missing = params - set(m.get("supported_parameters") or [])
        if missing:
            errors.append(f"{model_id}: no longer accepts {', '.join(sorted(missing))} (ChefBot always sends it)")
        if inputs - set(arch.get("input_modalities") or []):
            errors.append(f"{model_id}: no longer accepts images (ChefBot reads ingredient photos with it)")
        if outputs - set(arch.get("output_modalities") or []):
            errors.append(f"{model_id}: no longer outputs images (ChefBot draws dish pictures with it)")
        expires = m.get("expiration_date")
        if expires:
            try:
                left = (date.fromisoformat(str(expires)[:10]) - today).days
            except ValueError:
                left = 0
            msg = f"{model_id}: OpenRouter will retire it on {expires}"
            (errors if left <= RETIRING_SOON_DAYS else warnings).append(msg)
    return errors, warnings


def check_endpoints(model: api.Model, data: dict) -> list[str]:
    """The model's preferred host (ChefBot's provider pin) still serves it."""
    endpoints = (data.get("data") or {}).get("endpoints")
    if not isinstance(endpoints, list):
        return [f"{model.id}: OpenRouter's endpoint list changed shape (keys: {sorted(data)})"]
    hosts = {_norm(e.get(k) or "") for e in endpoints for k in ("tag", "provider_name")} - {""}
    if _norm(model.provider) not in hosts:
        return [f"{model.id}: {model.provider} no longer hosts it on OpenRouter (hosts now: "
                f"{', '.join(sorted(e.get('provider_name') or '?' for e in endpoints)) or 'none'})"]
    return []


# ------------------------------------------------------------------ the three checks

async def models_check() -> tuple[list[str], list[str]]:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(MODELS_URL)
        r.raise_for_status()
        listing = r.json().get("data")
        if not isinstance(listing, list):
            return [f"{MODELS_URL} changed shape (keys: {sorted(r.json())})"], []
        errors, warnings = check_listing(listing)
        for model in api.MODELS.values():
            r = await client.get(ENDPOINTS_URL.format(id=model.id))
            if r.status_code != 200:
                errors.append(f"{model.id}: endpoint list returned HTTP {r.status_code}")
                continue
            errors += check_endpoints(model, r.json())
    return errors, warnings


async def _stream(chef: api.ChefBotAPI, messages: list[dict], model: str, effort: str) -> tuple[str, bool]:
    text, usage = "", False
    async for c in chef.stream_chat(messages, model, effort):
        if c.kind == "text":
            text += c.text
        elif c.kind == "usage":
            usage = True
    return text, usage


def _food_photo() -> bytes:
    """A small drawn picture (a tomato on a plate) so the photo check needs no file."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (256, 256), "white")
    d = ImageDraw.Draw(img)
    d.ellipse((28, 28, 228, 228), fill="#e8e4dc", outline="#999999", width=3)
    d.ellipse((78, 78, 178, 178), fill="#d8321e")
    d.polygon([(128, 70), (118, 88), (138, 88)], fill="#2e7d32")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


async def recipe_check(key: str) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    chef = api.ChefBotAPI(key)
    try:
        # The real thing: the default model at the app's default thinking, a full recipe.
        messages = [{"role": "system", "content": prompts.system_prompt(prompts.DEFAULT_AUDIENCE, "Greek")},
                    {"role": "user", "content": prompts.first_message("chicken thighs, lemons, potatoes, oregano")}]
        try:
            text, usage = await _stream(chef, messages, api.DEFAULT_MODEL, api.DEFAULT_EFFORT)
            if not text.strip():
                errors.append(f"{api.DEFAULT_MODEL}: the stream finished with no recipe text")
            elif not extract_title(text):
                errors.append(f"{api.DEFAULT_MODEL}: the recipe has no 'Recipe Title:' line (titles would break)")
            if not usage:
                warnings.append(f"{api.DEFAULT_MODEL}: no usage chunk in the stream")
            print(f"{api.DEFAULT_MODEL}: {len(text)} characters, title {extract_title(text)!r}")
        except api.ApiError as e:
            errors.append(f"{api.DEFAULT_MODEL}: {e}")
        # The other models in Settings: just that they still stream (low thinking keeps it quick).
        for key_ in api.MODELS:
            if key_ == api.DEFAULT_MODEL:
                continue
            try:
                text, _ = await _stream(chef, [{"role": "user", "content": "Name one herb. One word."}], key_, "low")
                if not text.strip():
                    errors.append(f"{key_}: the stream finished with no text")
                print(f"{key_}: {text.strip()[:40]!r}")
            except api.ApiError as e:
                errors.append(f"{key_}: {e}")
        # Reading an ingredient photo.
        try:
            seen = await chef.read_ingredients(_food_photo(), "image/png")
            print(f"photo read: {seen[:80]!r}")
        except (api.ApiError, KeyError, IndexError) as e:
            errors.append(f"photo reading ({api.PHOTO_MODEL}): {type(e).__name__}: {e}")
    finally:
        await chef.aclose()
    return errors, warnings


async def picture_check(key: str) -> tuple[list[str], list[str]]:
    from PIL import Image
    chef = api.ChefBotAPI(key)
    try:
        data = await chef.dish_photo("Lemon Oregano Chicken with Crispy Potatoes")
        img = Image.open(io.BytesIO(data))
        img.load()
        print(f"picture: {img.format} {img.size[0]}x{img.size[1]}, {len(data) // 1024} KB")
        return [], []
    except (api.ApiError, KeyError, IndexError, ValueError, OSError) as e:
        return [f"dish picture ({api.IMAGE_MODEL}): {type(e).__name__}: {e}"], []
    finally:
        await chef.aclose()


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    if which not in ("models", "recipe", "picture"):
        print(__doc__)
        return 2
    if which == "models":
        errors, warnings = asyncio.run(models_check())
    else:
        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not key:
            print("::notice::No OPENROUTER_API_KEY secret yet, so this check was skipped.")
            return 0
        errors, warnings = asyncio.run((recipe_check if which == "recipe" else picture_check)(key))
    for w in warnings:
        print(f"::warning::{w}")
    for e in errors:
        print(f"::error::{e}")
    print("OK" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
