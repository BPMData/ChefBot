"""Recipe jobs outlive individual HTTP requests, and keep their events for replay."""
from __future__ import annotations

import asyncio
import json
import logging
import re
import secrets
from dataclasses import dataclass, field

from chefbot import api, recipe

from .limits import LIMITS, LimitReached, UsageLimits
from .review import review_recipe

JOB_TTL_SECONDS = 30 * 60
JOB_TIMEOUT_SECONDS = 600
HEARTBEAT_SECONDS = 15
# Frozen here so settings for the desktop/Android app can evolve independently.
WEB_MODEL = "glm-5.3"
WEB_EFFORT = "high"

log = logging.getLogger(__name__)

HEADING = re.compile(r"^[#*_\s]*(ingredients|directions|instructions|method|steps)[:*_#\s]*$", re.I)
ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.+)")
OTHER_HEADING = re.compile(r"^\s*(?:#{1,6}\s|\*\*[^*]+\*\*:?\s*$)")
PARENTHETICAL = re.compile(r"\([^()]*\)")
QUANTITY = re.compile(r"^(?:[\d\s./⁄–-]+[¼½¾⅓⅔⅛]*|[¼½¾⅓⅔⅛])\s*")
UNIT = re.compile(
    r"^(?:(?:kg|mg|g|ml|l|oz|lb|lbs|tsp|tbsp|cups?|cloves?|cans?|pinch|dash|"
    r"small|medium|large|grams?|tablespoons?|teaspoons?)\b[.\s]*)+(?:of\s+)?",
    re.I,
)


def draft_progress(markdown: str) -> dict:
    ingredients: list[str] = []
    steps = 0
    section = ""
    for line in markdown.splitlines():
        heading = HEADING.match(line)
        if heading:
            section = heading[1].lower()
            continue
        item = ITEM.match(line)
        if item and section == "ingredients":
            label = PARENTHETICAL.sub("", item[1]).strip("*_ ")
            quantity = QUANTITY.match(label)
            if quantity:
                label = UNIT.sub("", label[quantity.end():])
            label = label.split(",", 1)[0].split(":", 1)[0].strip()
            if label and len(ingredients) < 24:
                ingredients.append(label[:64])
        elif item and section:
            steps += 1
        elif OTHER_HEADING.match(line):
            section = ""
    return {"ingredients": ingredients, "step_count": steps}


@dataclass
class RecipeJob:
    visitor: str
    id: str = field(default_factory=lambda: secrets.token_urlsafe(24))
    events: list[tuple[str, dict]] = field(default_factory=list)
    changed: asyncio.Event = field(default_factory=asyncio.Event)
    finished: bool = False
    result: dict | None = None
    expiry: asyncio.TimerHandle | None = None

    def emit(self, event: str, data: dict) -> None:
        self.events.append((event, data))
        self.changed.set()
        self.changed = asyncio.Event()

    async def stream(self):
        index = 0
        while True:
            while index < len(self.events):
                event, data = self.events[index]
                index += 1
                yield f"id: {index}\nevent: {event}\ndata: {json.dumps(data, ensure_ascii=True)}\n\n"
            if self.finished:
                return
            try:
                await asyncio.wait_for(self.changed.wait(), HEARTBEAT_SECONDS)
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"


class RecipeJobs:
    def __init__(self, model: api.ChefBotAPI, available: bool = True,
                 limits: UsageLimits | None = None, show_draft: bool = False):
        self.model = model
        self.available = available
        self.limits = limits
        self.show_draft = show_draft
        self.jobs: dict[str, RecipeJob] = {}
        self.tasks: set[asyncio.Task] = set()

    def start(self, visitor: str, messages: list[dict]) -> RecipeJob:
        job = RecipeJob(visitor)
        self.jobs[job.id] = job
        task = asyncio.create_task(self.run(job, messages))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return job

    def get(self, job_id: str, visitor: str) -> RecipeJob | None:
        job = self.jobs.get(job_id)
        return job if job and secrets.compare_digest(job.visitor, visitor) else None

    async def draft(self, job: RecipeJob | None, messages: list[dict]) -> str:
        markdown = ""
        progress = {"ingredients": [], "step_count": 0}
        parsed = 0
        async for chunk in self.model.stream_chat(messages, WEB_MODEL, WEB_EFFORT):
            if chunk.kind != "text":
                continue
            markdown += chunk.text
            if len(markdown) > LIMITS["recipe_characters"]:
                raise ValueError("The draft exceeded the recipe length limit")
            if job is not None and self.show_draft:
                job.emit("draft", {"delta": chunk.text})
            complete = markdown.rfind("\n")
            if job is not None and complete > parsed:
                parsed = complete
                new_progress = draft_progress(markdown[:complete])
                if new_progress != progress:
                    progress = new_progress
                    job.emit("progress", progress)
        if job is not None:
            final_progress = draft_progress(markdown)
            if final_progress != progress:
                job.emit("progress", final_progress)
        if not markdown.strip():
            raise ValueError("The model returned an empty reply")
        return markdown

    async def generate(self, job: RecipeJob, messages: list[dict]) -> dict:
        markdown = await self.draft(job, messages)
        fixes = []
        if self.limits is not None:
            markdown, fixes = await review_recipe(
                self.model, messages, markdown,
                charge=lambda kind: self.limits.charge(job.visitor, kind),
                stage=lambda stage: job.emit("stage", {"stage": stage}),
                revise=lambda revised_messages: self.draft(None, revised_messages),
            )
            if len(markdown) > LIMITS["recipe_characters"]:
                raise ValueError("The checked recipe exceeded the recipe length limit")
        return {"markdown": markdown, "title": recipe.extract_title(markdown), "fixes": fixes}

    async def run(self, job: RecipeJob, messages: list[dict]) -> None:
        job.emit("stage", {"stage": "drafting"})
        try:
            job.result = await asyncio.wait_for(self.generate(job, messages), JOB_TIMEOUT_SECONDS)
            job.emit("stage", {"stage": "done"})
            job.emit("result", job.result)
        except LimitReached as error:
            job.emit("error", {"message": str(error)})
        except Exception as error:
            # Provider errors can include request details. Keep them out of logs and SSE.
            log.warning("ChefBot recipe job failed (%s).", type(error).__name__)
            job.emit("error", {"message": "ChefBot couldn’t finish this reply. Please try again."})
        finally:
            job.finished = True
            job.changed.set()
            job.expiry = asyncio.get_running_loop().call_later(JOB_TTL_SECONDS, self.jobs.pop, job.id, None)

    async def close(self) -> None:
        tasks = list(self.tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for job in self.jobs.values():
            if job.expiry:
                job.expiry.cancel()
