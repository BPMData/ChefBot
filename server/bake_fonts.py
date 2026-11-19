"""Prepare the three CJK font families at image build time."""
import sys
from pathlib import Path

from .app import export

if __name__ == "__main__":
    font_dir = Path(sys.argv[1])
    fonts = export.ensure_cjk_fonts("한글 かな 汉字", font_dir)
    # The shared detector picks Japanese for Han alongside kana. Fetch Chinese separately.
    fonts.update(export.ensure_cjk_fonts("汉字", font_dir))
    if fonts.keys() != export.CJK_FONT_URLS.keys():
        raise SystemExit("Could not prepare every CJK PDF font.")
