"""Local Playwright backend. Serves the real API with deterministic model replies."""
import asyncio
import io

from PIL import Image

from server.app import create_app
from server.limits import LIMITS
from chefbot.api import Chunk

LIMITS["reply_cooldown_seconds"] = 0


class FixtureModel:
    async def stream_chat(self, messages, *args):
        follow_up = len(messages) > 2
        title, seasoning = ("Spicy Cumin Carrots", "chili flakes") if follow_up else ("Cumin Carrots", "cumin")
        yield Chunk("text", f"Recipe Title: {title}\n\n**Ingredients**\n\n- 225 g carrots\n- 1 tsp {seasoning}\n")
        await asyncio.sleep(1.2)
        yield Chunk("text", f"\n**Instructions**\n\n1. Roast the carrots.\n2. Add {seasoning}.")

    async def read_ingredients(self, image, mime):
        return "carrots, cumin"

    async def dish_photo(self, title):
        output = io.BytesIO()
        Image.new("RGB", (80, 56), (190, 90, 40)).save(output, "PNG")
        return output.getvalue()


app = create_app(FixtureModel())
