"""Review complete recipes and apply one set of corrections before publishing."""
from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from chefbot import api, prompts, recipe

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1_000)]


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    issue: ShortText
    location: ShortText
    fix: ShortText
    severity: Literal["minor", "major"]
    before: str | None = Field(None, max_length=2_000)
    after: str | None = Field(None, max_length=2_000)

    def summary(self) -> dict:
        return self.model_dump(include={"issue", "location", "fix"})


class Review(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    issues: list[Finding] = Field(max_length=8)


def parse_findings(text: str) -> list[Finding]:
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        text = text.partition("\n")[2].removesuffix("```").strip()
    return Review.model_validate_json(text).issues


def apply_patches(draft: str, findings: list[Finding]) -> str | None:
    """Apply disjoint exact matches in one pass, or escalate to a complete revision."""
    edits = []
    for finding in findings:
        before, after = finding.before, finding.after
        if finding.severity == "major" or not before or after is None or before == after:
            return None
        start = draft.find(before)
        if start < 0 or draft.find(before, start + 1) >= 0:
            return None
        edits.append((start, start + len(before), after))
    index = 0
    parts = []
    for start, end, replacement in sorted(edits):
        if start < index:
            return None
        parts.extend([draft[index:start], replacement])
        index = end
    return "".join([*parts, draft[index:]])


async def review_recipe(
    model: api.ChefBotAPI,
    messages: list[dict],
    draft: str,
    charge: Callable[[str], Awaitable[None]],
    stage: Callable[[str], None],
    revise: Callable[[list[dict]], Awaitable[str]],
) -> tuple[str, list[dict]]:
    # A follow-up question can legitimately return an answer without a recipe.
    if not recipe.extract_title(draft):
        return draft, []

    stage("checking")
    await charge("review")
    context = {
        "recipe_instructions": messages[0]["content"],
        "user_requests": [message["content"] for message in messages if message["role"] == "user"],
        "draft": draft,
    }
    raw = await model.complete_chat([
        {"role": "system", "content": prompts.RECIPE_REVIEW},
        {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
    ], prompts.REVIEW_MODEL, prompts.REVIEW_EFFORT, 8_000)
    findings = parse_findings(raw)
    if not findings:
        return draft, []

    stage("fixing")
    summaries = [finding.summary() for finding in findings]
    fixed = apply_patches(draft, findings)
    if not fixed or not recipe.extract_title(fixed):
        await charge("revision")
        fixed = await revise([
            *messages, {"role": "assistant", "content": draft},
            {"role": "user", "content": prompts.RECIPE_REVISION + json.dumps(summaries, ensure_ascii=False)},
        ])
        if not recipe.extract_title(fixed) or fixed.strip() == draft.strip():
            raise ValueError("The revision did not return a corrected recipe")
    return fixed, summaries
