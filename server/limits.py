"""Single-worker model-call limits and whole-object Cloud Storage checkpoints."""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Protocol
from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field, ValidationError

LIMITS = {
    "new_recipes": 3,
    "replies": 10,
    "follow_ups": 5,
    "reply_cooldown_seconds": 10,
    "ingredient_photos": 2,
    "pictures": 2,
    "global_calls": 100,
    "message_characters": 4_000,
    "recipe_characters": 30_000,
    "history_characters": 100_000,
    "photo_bytes": 4 * 1024 * 1024,
    "photo_pixels": 12_000_000,
}

log = logging.getLogger(__name__)
METADATA_TOKEN = (
    "http://metadata.google.internal/computeMetadata/v1/"
    "instance/service-accounts/default/token"
)


class VisitorUsage(BaseModel):
    new_recipes: int = Field(0, ge=0)
    replies: int = Field(0, ge=0)
    ingredient_photos: int = Field(0, ge=0)
    pictures: int = Field(0, ge=0)
    last_reply: float | None = None


class Usage(BaseModel):
    day: str
    calls: int = Field(0, ge=0)
    visitors: dict[str, VisitorUsage] = Field(default_factory=dict)


class UsageStore(Protocol):
    async def load(self) -> Usage | None: ...
    async def save(self, usage: Usage) -> None: ...


class GcsUsageStore:
    """Use Cloud Run's runtime identity and the Storage JSON API."""
    def __init__(self, bucket: str, client: httpx.AsyncClient):
        self.bucket = quote(bucket, safe="")
        self.client = client
        self.token = ""
        self.token_expiry = 0.0

    async def headers(self) -> dict[str, str]:
        now = time.monotonic()
        if now >= self.token_expiry:
            response = await self.client.get(METADATA_TOKEN, headers={"Metadata-Flavor": "Google"})
            response.raise_for_status()
            token = response.json()
            self.token = token["access_token"]
            self.token_expiry = now + max(0, int(token["expires_in"]) - 60)
        return {"Authorization": f"Bearer {self.token}"}

    async def load(self) -> Usage | None:
        response = await self.client.get(
            f"https://storage.googleapis.com/storage/v1/b/{self.bucket}/o/usage.json",
            params={"alt": "media"},
            headers=await self.headers(),
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Usage.model_validate_json(response.content)

    async def save(self, usage: Usage) -> None:
        headers = await self.headers()
        response = await self.client.post(
            f"https://storage.googleapis.com/upload/storage/v1/b/{self.bucket}/o",
            params={"uploadType": "media", "name": "usage.json"},
            headers={**headers, "Content-Type": "application/json"},
            content=usage.model_dump_json(),
        )
        response.raise_for_status()


class LimitReached(Exception):
    pass


class UsageLimits:
    def __init__(self, store: UsageStore | None = None, clock=time.time):
        self.store = store
        self.clock = clock
        self.lock = asyncio.Lock()
        self.usage = Usage(day=self.day(self.clock()))
        self.restored = store is None
        self.retry_after = 0.0

    @staticmethod
    def day(now: float) -> str:
        return datetime.fromtimestamp(now, timezone.utc).date().isoformat()

    def roll_day(self, now: float) -> None:
        day = self.day(now)
        if self.usage.day != day:
            recent = {
                visitor: VisitorUsage(last_reply=counts.last_reply)
                for visitor, counts in self.usage.visitors.items()
                if counts.last_reply is not None
                and now - counts.last_reply < LIMITS["reply_cooldown_seconds"]
            }
            self.usage = Usage(day=day, visitors=recent)

    async def restore(self) -> None:
        now = self.clock()
        if self.restored or now < self.retry_after:
            return
        try:
            checkpoint = await self.store.load()
        except (httpx.HTTPError, ValidationError, ValueError, KeyError, OSError):
            log.warning("Could not read the ChefBot usage checkpoint. Using in-memory limits.")
            self.retry_after = now + 30
            return
        self.restored = True
        if checkpoint is None:
            return
        # If startup storage was unavailable, add the calls admitted before recovery.
        pending, self.usage = self.usage, checkpoint
        self.roll_day(now)
        if pending.day == self.usage.day:
            self.usage.calls += pending.calls
            for visitor, delta in pending.visitors.items():
                counts = self.usage.visitors.setdefault(visitor, VisitorUsage())
                counts.new_recipes += delta.new_recipes
                counts.replies += delta.replies
                counts.ingredient_photos += delta.ingredient_photos
                counts.pictures += delta.pictures
                if delta.last_reply is not None:
                    counts.last_reply = max(counts.last_reply or delta.last_reply, delta.last_reply)

    async def charge(self, visitor: str, kind: str) -> None:
        async with self.lock:
            await self.restore()
            now = self.clock()
            self.roll_day(now)
            if self.usage.calls >= LIMITS["global_calls"]:
                raise LimitReached("ChefBot is resting for the day. Try again tomorrow.")

            counts = self.usage.visitors.get(visitor, VisitorUsage())
            if kind in {"new_recipe", "follow_up"}:
                if kind == "new_recipe" and counts.new_recipes >= LIMITS["new_recipes"]:
                    raise LimitReached("You’ve reached today’s new recipe limit. Try again tomorrow.")
                if counts.replies >= LIMITS["replies"]:
                    raise LimitReached("You’ve reached today’s reply limit. Try again tomorrow.")
                if counts.last_reply is not None and now - counts.last_reply < LIMITS["reply_cooldown_seconds"]:
                    raise LimitReached("Wait a few seconds before asking for another reply.")
                counts.replies += 1
                counts.new_recipes += kind == "new_recipe"
                counts.last_reply = now
            elif kind == "ingredient_photo":
                if counts.ingredient_photos >= LIMITS["ingredient_photos"]:
                    raise LimitReached("You’ve reached today’s ingredient photo limit. Try again tomorrow.")
                counts.ingredient_photos += 1
            elif kind == "picture":
                if counts.pictures >= LIMITS["pictures"]:
                    raise LimitReached("You’ve reached today’s dish picture limit. Try again tomorrow.")
                counts.pictures += 1
            else:
                raise ValueError(f"Unknown model call type: {kind}")

            self.usage.calls += 1
            self.usage.visitors[visitor] = counts
            if self.store and self.restored:
                try:
                    await self.store.save(self.usage)
                except (httpx.HTTPError, ValidationError, ValueError, KeyError, OSError):
                    log.warning("Could not write the ChefBot usage checkpoint. Using in-memory limits.")
