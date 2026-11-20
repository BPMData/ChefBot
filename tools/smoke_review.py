"""Live check of the lamb-fries review fixture with a configured development key."""
import asyncio
import os
import sys
import time
from pathlib import Path

from server.app import api, prompts
from server.jobs import RecipeJobs
from server.review import review_recipe

ROOT = Path(__file__).resolve().parents[1]


async def main():
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit("Set OPENROUTER_API_KEY for the live review check.")
    model = api.ChefBotAPI(key)
    jobs = RecipeJobs(model)
    source = (ROOT / "docs/review-loop/example-lamb-fries.md").read_text(encoding="utf-8")
    draft = source.split("## The reply\n", 1)[1].strip()
    messages = [
        {"role": "system", "content": prompts.system_prompt(prompts.DEFAULT_AUDIENCE, "greek")},
        {"role": "user", "content": prompts.first_message("lamb, fries, onion, chickpeas, tzatziki")},
    ]

    async def count(kind):
        print(f"Calling {kind} model.", flush=True)

    start = time.monotonic()
    try:
        result, findings = await asyncio.wait_for(review_recipe(
            model, messages, draft, count, print, lambda revised: jobs.draft(None, revised),
        ), timeout=600)
    except Exception as error:
        print(f"Review failed ({type(error).__name__}).", file=sys.stderr)
        return 1
    finally:
        await model.aclose()
    print(f"Review and corrections took {time.monotonic() - start:.1f} seconds.")
    for finding in findings:
        print(f"{finding['location']} — {finding['issue']} → {finding['fix']}")
    if findings:
        print(f"\n{result}")
    descriptions = " ".join(f"{item['issue']} {item['fix']}" for item in findings).lower()
    if "onion" not in descriptions or "chickpea" not in descriptions:
        print("Both fixture mistakes need to be identified.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
