"""Cut fixed-weight fonts for PDFs out of the bundled variable fonts (run once; output is committed).

    .venv/bin/python tools/make_static_fonts.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from chefbot.export import ASSET_FONTS, static_instance  # noqa: E402

OUT = ASSET_FONTS / "static"
JOBS = [("DMSans.ttf", 400, "DMSans-Regular.ttf"), ("DMSans.ttf", 700, "DMSans-Bold.ttf"),
        ("Fraunces.ttf", 700, "Fraunces-Bold.ttf"),
        ("NotoSans.ttf", 400, "NotoSans-Regular.ttf"), ("NotoSans.ttf", 700, "NotoSans-Bold.ttf")]

for src, weight, name in JOBS:
    path = static_instance(ASSET_FONTS / src, weight, OUT / name)
    print(f"{name}: {path.stat().st_size // 1024} KB")
