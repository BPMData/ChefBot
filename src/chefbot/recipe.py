"""Small helpers for reading a recipe the model wrote."""
import re

_TITLE_LINE = re.compile(r"^.*Recipe Title:(.*)$", re.MULTILINE)


def extract_title(text: str) -> str | None:
    """The last 'Recipe Title: ...' in the text, without markdown decoration, or None.

    The last one wins because a revised recipe repeats the line with the new title.
    """
    matches = _TITLE_LINE.findall(text or "")
    for raw in reversed(matches):
        title = raw.strip().strip("*_#`\"' ").strip()
        if title:
            return title
    return None
