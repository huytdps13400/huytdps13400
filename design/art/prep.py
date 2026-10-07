"""One-off: turn Codex's raw render into the production WebP embedded by build.py.

- lifts the near-white background (≥246) to pure #FFFFFF so it melts into the card
- paints the chroma-key screen and its anti-aliased fringe black (the vector UI covers it)
"""
from pathlib import Path
import numpy as np
from PIL import Image

here = Path(__file__).parent
im = np.asarray(Image.open(here / "hero-art-raw.png").convert("RGB")).astype(np.float32)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
spill = (g - np.maximum(r, b)) > 40          # key green and its fringe
im[spill] = 0
hi = im >= 246
im[hi] = np.minimum(255, 246 + (im[hi] - 246) * 9 / 5)
out = Image.fromarray(im.round().astype(np.uint8))
dst = here.parent.parent / "assets/art/hero-art.webp"
out.save(dst, "WEBP", quality=86, method=6)
print(dst, dst.stat().st_size // 1024, "KB")
