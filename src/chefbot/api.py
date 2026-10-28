"""Talking to models through OpenRouter (https://openrouter.ai): recipes, photo reading, dish pictures.

Plain httpx instead of the openai package: httpx is pure Python, which keeps the Android build simple.
"""
import base64
import json
from dataclasses import dataclass
from typing import AsyncIterator

import httpx

from . import prompts

API_URL = "https://openrouter.ai/api/v1/chat/completions"
APP_TITLE = "ChefBot"


@dataclass(frozen=True)
class Model:
    id: str            # OpenRouter model id
    label: str         # shown in Settings
    provider: str      # preferred host: the company that made the model
    vision: bool       # can read photos


# Picked from blind taste tests in Oct 2026 (see README). Requests go to the maker's own servers first,
# falling back to other hosts only if they're down.
MODELS: dict[str, Model] = {
    "glm-5.3": Model("z-ai/glm-5.3", "GLM 5.3 (Z.ai)", "z-ai", vision=False),
    "glm-5.3-flash": Model("z-ai/glm-5.3-flash", "GLM 5.3 Flash (Z.ai), fastest", "z-ai", vision=True),
    "kimi-k3.1-pro": Model("moonshotai/kimi-k3.1-pro", "Kimi K3.1 Pro (Moonshot), slow and thorough",
                           "moonshotai", vision=True),
}
DEFAULT_MODEL = "glm-5.3"
PHOTO_MODEL = "glm-5.3-flash"
IMAGE_MODEL = "google/gemini-3.1-flash-lite-image"

EFFORTS = ["low", "medium", "high"]
DEFAULT_EFFORT = "high"
MAX_TOKENS = 32000   # includes hidden thinking; generous so a recipe is never cut off


class ApiError(Exception):
    """Something went wrong talking to OpenRouter. The message is safe to show the user."""


@dataclass
class Chunk:
    kind: str          # "text" (recipe words), "thinking" (hidden reasoning happened), or "usage"
    text: str = ""
    usage: dict | None = None


def _friendly(status: int, body: str) -> str:
    try:
        msg = json.loads(body).get("error", {}).get("message", "")
    except Exception:
        msg = body[:200]
    if status == 401:
        return "OpenRouter didn't accept the API key. Check it in Settings."
    if status == 402:
        return "Your OpenRouter account is out of credits."
    if status == 429:
        return "Too many requests right now. Wait a moment and try again."
    return f"OpenRouter error {status}: {msg}" if msg else f"OpenRouter error {status}."


class ChefBotAPI:
    def __init__(self, api_key: str, client: httpx.AsyncClient | None = None):
        self.api_key = api_key.strip()
        self._client = client or httpx.AsyncClient(timeout=httpx.Timeout(600, connect=20))

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                "X-Title": APP_TITLE}

    async def _post(self, body: dict) -> dict:
        try:
            r = await self._client.post(API_URL, headers=self._headers(), json=body)
        except httpx.HTTPError as e:
            raise ApiError(f"Couldn't reach OpenRouter ({type(e).__name__}). Check your connection.") from e
        if r.status_code != 200:
            raise ApiError(_friendly(r.status_code, r.text))
        data = r.json()
        if "error" in data:
            raise ApiError(f"OpenRouter error: {data['error'].get('message', data['error'])}")
        return data

    async def stream_chat(self, messages: list[dict], model_key: str = DEFAULT_MODEL,
                          effort: str = DEFAULT_EFFORT) -> AsyncIterator[Chunk]:
        """Stream a reply to a recipe conversation. `messages` = system + user/assistant turns."""
        model = MODELS.get(model_key, MODELS[DEFAULT_MODEL])
        body = {
            "model": model.id,
            "messages": messages,
            "stream": True,
            "max_tokens": MAX_TOKENS,
            "temperature": 0.7,
            "reasoning": {"effort": effort if effort in EFFORTS else DEFAULT_EFFORT},
            "provider": {"order": [model.provider], "allow_fallbacks": True},
            "usage": {"include": True},
        }
        try:
            async with self._client.stream("POST", API_URL, headers=self._headers(), json=body) as r:
                if r.status_code != 200:
                    raise ApiError(_friendly(r.status_code, (await r.aread()).decode(errors="replace")))
                async for line in r.aiter_lines():
                    if not line.startswith("data: "):
                        continue          # blank lines and ": OPENROUTER PROCESSING" keep-alives
                    payload = line[6:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        obj = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    if "error" in obj:
                        raise ApiError(f"The model stopped with an error: {obj['error'].get('message', obj['error'])}")
                    if obj.get("usage"):
                        yield Chunk("usage", usage=obj["usage"])
                    for choice in obj.get("choices") or []:
                        delta = choice.get("delta") or {}
                        if delta.get("reasoning") or delta.get("reasoning_details"):
                            yield Chunk("thinking")
                        if delta.get("content"):
                            yield Chunk("text", delta["content"])
        except httpx.HTTPError as e:
            raise ApiError(f"Lost the connection to OpenRouter ({type(e).__name__}). Try again.") from e

    async def read_ingredients(self, image: bytes, mime: str = "image/jpeg") -> str:
        """List the food items visible in a photo. Returns '' when it sees no food."""
        model = MODELS[PHOTO_MODEL]
        data_url = f"data:{mime};base64,{base64.b64encode(image).decode()}"
        data = await self._post({
            "model": model.id,
            "max_tokens": 4000,
            "reasoning": {"effort": "low"},
            "provider": {"order": [model.provider], "allow_fallbacks": True},
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompts.INGREDIENTS_FROM_PHOTO},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]}],
        })
        text = (data["choices"][0]["message"].get("content") or "").strip().strip('"').strip()
        return "" if text.upper().startswith("NO FOOD") else text

    async def dish_photo(self, title: str) -> bytes:
        """A cookbook-style photo of the finished dish, as PNG/JPEG bytes."""
        data = await self._post({
            "model": IMAGE_MODEL,
            "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": prompts.dish_photo_prompt(title)}],
        })
        images = data["choices"][0]["message"].get("images") or []
        if not images:
            raise ApiError("The image model didn't return a picture. Try again.")
        url = images[0]["image_url"]["url"]
        return base64.b64decode(url.split(",", 1)[1])

    async def aclose(self):
        await self._client.aclose()
