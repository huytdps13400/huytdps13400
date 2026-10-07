"""Fit a phone screenshot to the hero render's screen and save assets/art/screen.webp.

    .venv/bin/python design/art/prep_screen.py path/to/screenshot.png [--drop Y0:Y1 ...]

--drop removes a horizontal band (source px), e.g. a profile row that shouldn't be public.
The render's screen (342×773 source px) is taller than a real iPhone's, so a too-wide
screenshot is extended at the bottom with its own bottom-edge colour (the home-indicator
zone) instead of cropping the sides, which would clip content against the bezel.
"""
import sys
from pathlib import Path
from PIL import Image

ASPECT = 342 / 773
args = sys.argv[1:]
src = Image.open(args[0]).convert("RGB")
for band in (a for i, a in enumerate(args) if i and args[i - 1] == "--drop"):
    y0, y1 = map(int, band.split(":"))
    w, h = src.size
    out = Image.new("RGB", (w, h - (y1 - y0)))
    out.paste(src.crop((0, 0, w, y0)), (0, 0)); out.paste(src.crop((0, y1, w, h)), (0, y0))
    src = out
w, h = src.size
if w / h > ASPECT:
    nh = round(w / ASPECT)
    out = Image.new("RGB", (w, nh), src.getpixel((w // 2, h - 2)))
    out.paste(src, (0, 0)); src = out
else:
    src = src.crop((0, 0, w, round(w / ASPECT)))
out = src.resize((600, round(600 / ASPECT)), Image.LANCZOS)
dst = Path(__file__).resolve().parents[2] / "assets/art/screen.webp"
out.save(dst, "WEBP", quality=90, method=6)
print(dst, out.size, dst.stat().st_size // 1024, "KB")
