"""Guard against Flet's `capitalization` option on text fields.

Flet 1.0 doesn't pass it to the keyboard; it adds a formatter that rewrites the text on every keystroke and
drops the keyboard's in-progress word. On Android that resets the keyboard: voice typing stops after a few
characters and caps lock turns off after one letter.
"""
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


def test_no_text_field_uses_capitalization():
    offenders = [f"{p.relative_to(SRC)}:{n}" for p in SRC.rglob("*.py")
                 for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
                 if "capitalization=" in line and not line.lstrip().startswith("#")]
    assert not offenders, f"TextField capitalization breaks Android keyboards: {offenders}"
