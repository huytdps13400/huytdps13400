"""Slice Codex's 4×2 icon sheet into assets/art/icons/<key>.webp at one shared scale."""
from pathlib import Path
import numpy as np
from PIL import Image

here = Path(__file__).parent
KEYS = ["lock", "card", "zap", "cpu", "grid", "message", "cloud", "package"]
im = np.asarray(Image.open(here / "icons-raw.png").convert("RGB")).astype(np.float32)
hi = im >= 246
im[hi] = np.minimum(255, 246 + (im[hi] - 246) * 9 / 5)
H, W, _ = im.shape
cw, ch = W // 4, H // 2
boxes = []
for i in range(8):
    x0, y0 = (i % 4) * cw, (i // 4) * ch
    ink = im[y0:y0 + ch, x0:x0 + cw].min(-1) < 232      # ignore the faint glow
    ys, xs = np.nonzero(ink)
    boxes.append((x0 + xs.min(), y0 + ys.min(), x0 + xs.max(), y0 + ys.max()))
side = round(max(max(b[2] - b[0], b[3] - b[1]) for b in boxes) * 1.12)
src = Image.fromarray(im.round().astype(np.uint8))
for key, (a, b, c, d) in zip(KEYS, boxes):
    cx, cy = (a + c) / 2, (b + d) / 2
    tile = Image.new("RGB", (side, side), "white")
    tile.paste(src.crop((round(cx - side / 2), round(cy - side / 2), round(cx + side / 2), round(cy + side / 2))), (0, 0))
    tile.resize((288, 288), Image.LANCZOS).save(here.parent.parent / f"assets/art/icons/{key}.webp", "WEBP", quality=88, method=6)
    print(key, (a, b, c, d))
print("side", side)
