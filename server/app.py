"""ChefBot's browser API. Run from the repository root with uvicorn server.app:app."""
from __future__ import annotations

import asyncio
import base64
import binascii
import io
import logging
import os
import re
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal, TypeVar

import httpx
import nh3
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError, model_validator
from starlette.requests import ClientDisconnect

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from chefbot import api, cuisines, export, prompts

from .jobs import RecipeJobs
from .limits import GcsUsageStore, LIMITS, LimitReached, UsageLimits, UsageStore

ORIGINS = ["https://bpmdata.github.io", "http://localhost:5173"]
VISITOR_ID = re.compile(r"[A-Za-z0-9_-]{22,64}")
IMAGE_TYPES = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
PHOTO_BASE64 = 4 * ((LIMITS["photo_bytes"] + 2) // 3)
PDF_TAGS = {
    "p", "br", "hr", "ul", "ol", "li", "strong", "b", "em", "i", "code", "pre",
    "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "table", "thead", "tbody", "tr", "th", "td",
}
log = logging.getLogger(__name__)

UserText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=LIMITS["message_characters"])]
RecipeText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=LIMITS["recipe_characters"])]
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=250)]
JobId = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Turn(Input):
    role: Literal["user", "assistant"]
    content: RecipeText

    @model_validator(mode="after")
    def check_user_length(self):
        if self.role == "user" and len(self.content) > LIMITS["message_characters"]:
            raise ValueError("User message is too long")
        return self


class JobInput(Input):
    ingredients: UserText
    job_id: JobId | None = None
    must_not: str = Field("", max_length=LIMITS["message_characters"])
    cuisine: str = Field(prompts.NO_CUISINE, max_length=100)
    audience: str = Field(prompts.DEFAULT_AUDIENCE, max_length=160)
    dessert: bool = False
    pantry: bool = False
    restrictions: list[str] = Field(default_factory=list, max_length=prompts.MAX_RESTRICTIONS)
    history: list[Turn] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_options_and_history(self):
        if self.cuisine != prompts.NO_CUISINE and not cuisines.resolve(self.cuisine):
            raise ValueError("Choose a cuisine from the picker")
        if self.audience not in prompts.AUDIENCES or any(r not in prompts.RESTRICTIONS for r in self.restrictions):
            raise ValueError("Choose an audience and dietary rules from the form")
        roles = [turn.role for turn in self.history]
        if roles != ["user", "assistant"] * (len(roles) // 2):
            raise ValueError("History must contain complete user and assistant pairs")
        if sum(len(turn.content) for turn in self.history) > LIMITS["history_characters"]:
            raise ValueError("The conversation is too long")
        return self

    def messages(self) -> list[dict]:
        system = prompts.system_prompt(self.audience, self.cuisine, self.dessert, self.restrictions, self.pantry)
        turns = [turn.model_dump() for turn in self.history] + [{"role": "user", "content": self.ingredients}]
        turns[0]["content"] = prompts.first_message(turns[0]["content"], self.must_not)
        return [{"role": "system", "content": system}, *turns]


class PictureInput(Input):
    title: Title


class PdfInput(Input):
    title: Title
    markdown: RecipeText
    photo: str | None = Field(None, max_length=PHOTO_BASE64)


T = TypeVar("T", bound=Input)


async def read_body(request: Request, cap: int, message: str) -> bytes:
    length = request.headers.get("content-length", "")
    if length.isascii() and length.isdigit() and (len(length) > 12 or int(length) > cap):
        raise HTTPException(413, message)
    body = bytearray()
    try:
        async for chunk in request.stream():
            if len(chunk) > cap - len(body):
                raise HTTPException(413, message)
            body.extend(chunk)
    except ClientDisconnect:
        raise HTTPException(400, "The connection closed before the request arrived.") from None
    return bytes(body)


async def json_input(request: Request, model: type[T], cap: int) -> T:
    raw = await read_body(request, cap, "This request is too large.")
    try:
        return model.model_validate_json(raw)
    except ValidationError:
        raise HTTPException(422, "Check the recipe fields and message lengths and try again.") from None


def visitor_id(request: Request) -> str:
    visitor = request.headers.get("x-visitor-id", "")
    if not VISITOR_ID.fullmatch(visitor):
        raise HTTPException(400, "ChefBot is still starting up. Reload this page and try again.")
    return visitor


def image_type(data: bytes) -> str:
    try:
        with Image.open(io.BytesIO(data), formats=list(IMAGE_TYPES)) as image:
            if image.width * image.height > LIMITS["photo_pixels"]:
                raise HTTPException(413, "That photo is too large. Resize it and try again.")
            mime = IMAGE_TYPES[image.format]
            image.verify()
    except Image.DecompressionBombError:
        raise HTTPException(413, "That photo is too large. Resize it and try again.") from None
    except (OSError, SyntaxError, ValueError):
        raise HTTPException(415, "Choose a JPEG, PNG, or WebP photo.") from None
    return mime


def render_pdf(body: PdfInput, font_dir: Path) -> bytes:
    photo = None
    if body.photo:
        try:
            photo = base64.b64decode(body.photo, validate=True)
        except (ValueError, binascii.Error):
            raise HTTPException(415, "Choose a JPEG, PNG, or WebP photo.") from None
        if len(photo) > LIMITS["photo_bytes"]:
            raise HTTPException(413, "That photo is too large. Resize it and try again.")
        image_type(photo)
    fonts = {}
    for key in export.cjk_needed(body.title + body.markdown):
        regular = font_dir / f"NotoSans{key.upper()}-Regular.ttf"
        bold = font_dir / f"NotoSans{key.upper()}-Bold.ttf"
        if regular.is_file() and bold.is_file():
            fonts[key] = (regular, bold)
    return export.recipe_pdf(
        body.title, body.markdown, photo, fonts,
        html_filter=lambda html: nh3.clean(html, tags=PDF_TAGS, attributes={}, link_rel=None),
    )


def cuisine_tree() -> dict:
    roots = cuisines.continents()
    nodes = {}
    remaining = list(reversed(roots))
    while remaining:
        node = remaining.pop()
        nodes[node["id"]] = node
        remaining.extend(reversed(cuisines.children(node["id"])))
    return {
        "roots": [root["id"] for root in roots],
        "nodes": nodes,
        "legacy_ids": cuisines.LEGACY_IDS,
        "audiences": list(prompts.AUDIENCES),
        "default_audience": prompts.DEFAULT_AUDIENCE,
        "restrictions": list(prompts.RESTRICTIONS),
        "no_cuisine": prompts.NO_CUISINE,
        "limits": {key: LIMITS[key] for key in ("message_characters", "follow_ups", "photo_bytes")},
    }


def create_app(model: api.ChefBotAPI | None = None, usage_store: UsageStore | None = None,
               clock=None, review: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        key = os.getenv("OPENROUTER_API_KEY", "").strip()
        bucket = os.getenv("CHEFBOT_USAGE_BUCKET", "").strip()
        backend = model if model is not None else api.ChefBotAPI(key)
        async with httpx.AsyncClient(timeout=5, trust_env=False) as storage_client:
            store = usage_store or (GcsUsageStore(bucket, storage_client) if bucket else None)
            limits = UsageLimits(store, **({"clock": clock} if clock is not None else {}))
            await limits.restore()
            jobs = RecipeJobs(
                backend, available=bool(key or model is not None),
                limits=limits if review else None, show_draft=os.getenv("CHEFBOT_STREAM_DRAFT") == "1",
            )
            application.state.jobs = jobs
            application.state.job_starts = asyncio.Lock()
            application.state.limits = limits
            application.state.pdf_slots = asyncio.Semaphore(2)
            application.state.font_dir = Path(os.getenv("CHEFBOT_PDF_FONTS", "/opt/chefbot/pdf-fonts"))
            try:
                yield
            finally:
                await jobs.close()
                if model is None:
                    await backend.aclose()

    application = FastAPI(lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware, allow_origins=ORIGINS, allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Visitor-ID"], expose_headers=["Content-Disposition"],
    )

    async def charge(request: Request, visitor: str, kind: str) -> None:
        if not request.app.state.jobs.available:
            raise HTTPException(503, "ChefBot’s recipe service is unavailable right now.")
        try:
            await request.app.state.limits.charge(visitor, kind)
        except LimitReached as error:
            raise HTTPException(429, str(error)) from None

    @application.get("/healthz")
    async def health():
        return {"status": "ok"}

    @application.get("/api/cuisines")
    async def list_cuisines():
        return cuisine_tree()

    @application.post("/api/jobs", status_code=202)
    async def create_job(request: Request, visitor: str = Depends(visitor_id)):
        body = await json_input(request, JobInput, 8 * (LIMITS["history_characters"] + 2 * LIMITS["message_characters"]))
        if len(body.history) // 2 > LIMITS["follow_ups"]:
            raise HTTPException(429, "This recipe has reached its follow-up limit. Start a new recipe to continue.")
        jobs = request.app.state.jobs
        async with request.app.state.job_starts:
            # Claim a client-supplied id only once, including simultaneous submissions.
            if body.job_id and body.job_id in jobs.jobs:
                if jobs.get(body.job_id, visitor) is None:
                    raise HTTPException(409, "This recipe request already exists.")
                return {"job_id": body.job_id}
            await charge(request, visitor, "follow_up" if body.history else "new_recipe")
            job = jobs.start(visitor, body.messages(), body.job_id)
        return {"job_id": job.id}

    @application.get("/api/jobs/{job_id}/events")
    async def job_events(job_id: str, request: Request, visitor: str = Depends(visitor_id)):
        job = request.app.state.jobs.get(job_id, visitor)
        if job is None:
            raise HTTPException(404, "This recipe job is no longer available.")
        return StreamingResponse(job.stream(), media_type="text/event-stream", headers={
            "Cache-Control": "no-store", "X-Accel-Buffering": "no",
        })

    @application.post("/api/jobs/{job_id}/stop", status_code=204)
    async def stop_job(job_id: str, request: Request, visitor: str = Depends(visitor_id)):
        jobs = request.app.state.jobs
        job = jobs.get(job_id, visitor)
        if job is None:
            raise HTTPException(404, "This recipe job is no longer available.")
        jobs.stop(job)
        return Response(status_code=204)

    @application.post("/api/photo/ingredients")
    async def read_photo(request: Request, visitor: str = Depends(visitor_id)):
        photo = await read_body(request, LIMITS["photo_bytes"], "That photo is too large. Resize it and try again.")
        mime = await asyncio.to_thread(image_type, photo)
        await charge(request, visitor, "ingredient_photo")
        try:
            ingredients = await request.app.state.jobs.model.read_ingredients(photo, mime)
        except Exception as error:
            log.warning("ChefBot ingredient photo failed (%s).", type(error).__name__)
            raise HTTPException(502, "ChefBot couldn’t read this photo. Please try again.") from None
        return {"ingredients": ingredients}

    @application.post("/api/jobs/{job_id}/picture")
    async def dish_picture(job_id: str, request: Request, visitor: str = Depends(visitor_id)):
        job = request.app.state.jobs.get(job_id, visitor)
        if job is None:
            raise HTTPException(404, "This recipe job is no longer available.")
        if not job.result or not job.result["title"]:
            raise HTTPException(409, "Wait until the recipe is ready before asking for a picture.")
        return await make_picture(request, visitor, job.result["title"][:250])

    @application.post("/api/picture")
    async def saved_dish_picture(request: Request, visitor: str = Depends(visitor_id)):
        body = await json_input(request, PictureInput, 4096)
        return await make_picture(request, visitor, body.title)

    async def make_picture(request: Request, visitor: str, title: str):
        await charge(request, visitor, "picture")
        try:
            photo = await request.app.state.jobs.model.dish_photo(title)
            if len(photo) > LIMITS["photo_bytes"]:
                raise ValueError("The generated picture is too large")
            mime = await asyncio.to_thread(image_type, photo)
        except Exception as error:
            log.warning("ChefBot dish picture failed (%s).", type(error).__name__)
            raise HTTPException(502, "ChefBot couldn’t make a picture. Please try again.") from None
        return Response(photo, media_type=mime, headers={"Cache-Control": "no-store"})

    @application.post("/api/pdf")
    async def make_pdf(request: Request, visitor: str = Depends(visitor_id)):
        body = await json_input(request, PdfInput, PHOTO_BASE64 + 8 * LIMITS["recipe_characters"] + 4096)
        async with request.app.state.pdf_slots:
            try:
                pdf = await asyncio.to_thread(render_pdf, body, request.app.state.font_dir)
            except HTTPException:
                raise
            except Exception as error:
                log.warning("ChefBot PDF export failed (%s).", type(error).__name__)
                raise HTTPException(422, "ChefBot couldn’t export this recipe as a PDF.") from None
        return Response(pdf, media_type="application/pdf", headers={
            "Content-Disposition": f'attachment; filename="{export.file_stem(body.title).encode("ascii", "ignore").decode().strip("-") or "recipe"}.pdf"',
            "Cache-Control": "no-store",
        })

    return application


app = create_app()
