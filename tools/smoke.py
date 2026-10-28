"""Live check against OpenRouter: one recipe, then a follow-up edit in the same conversation.

    OPENROUTER_API_KEY=... python tools/smoke.py [model] [effort]
"""
import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from chefbot import api, prompts  # noqa: E402
from chefbot.recipe import extract_title  # noqa: E402


async def turn(chef, messages, model, effort):
    t, text, thinking, cost = time.time(), "", 0, 0.0
    async for c in chef.stream_chat(messages, model, effort):
        if c.kind == "text":
            text += c.text
        elif c.kind == "thinking":
            thinking += 1
        elif c.kind == "usage":
            cost = c.usage.get("cost", 0) or 0
    print(f"  {time.time() - t:.1f}s, {thinking} thinking chunks, ${cost:.4f}, title: {extract_title(text)!r}")
    return text


async def main():
    model = sys.argv[1] if len(sys.argv) > 1 else api.DEFAULT_MODEL
    effort = sys.argv[2] if len(sys.argv) > 2 else api.DEFAULT_EFFORT
    chef = api.ChefBotAPI(os.environ["OPENROUTER_API_KEY"])
    messages = [
        {"role": "system", "content": prompts.system_prompt("An important person you want to impress!", "Greek")},
        {"role": "user", "content": prompts.first_message("lamb shoulder, cucumbers, yogurt, lemons, potatoes, feta")},
    ]
    print(f"[{model} / {effort}] first recipe")
    first = await turn(chef, messages, model, effort)
    messages.append({"role": "assistant", "content": first})
    messages.append({"role": "user", "content": "Looks great, but no cucumber please, not my thing. Everything else the same."})
    print("follow-up: no cucumber")
    second = await turn(chef, messages, model, effort)
    print("  cucumber in first:", "cucumber" in first.lower(), "| cucumber in revision:", "cucumber" in second.lower())
    print("  revision opens with:", second.strip().splitlines()[0][:160])
    Path(os.environ.get("SMOKE_OUT", "/tmp")).joinpath("smoke_revision.md").write_text(first + "\n\n=====\n\n" + second)
    await chef.aclose()


asyncio.run(main())
