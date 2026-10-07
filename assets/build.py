#!/usr/bin/env python3
"""Generates every SVG used by the profile README.

    python3 assets/build.py            # rebuild all artwork
    python3 assets/build.py activity   # rebuild only the activity card (used by CI)

Artwork is fully self-contained (system fonts, no external images) so GitHub
renders it through its image proxy. Edit the copy/data below, re-run, commit.

When Pillow and the Inter font are installed, text is measured with real font
metrics and the build fails on any overflow, so layouts stay pixel-tight.
"""
import base64
import glob
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from typeset import Glyphs, width as tw_

OUT = Path(__file__).parent

# ── Design tokens ────────────────────────────────────────────────────────────
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

NAVY, DEEP, LINE = "#0A2540", "#061B31", "#1C3A5E"
WHITE, SOFT, MUTED, SUBTLE = "#FFFFFF", "#E3E8EE", "#ADBDCC", "#6B819B"
INK, INK_MUTED, UI_MUTED = "#0A2540", "#425466", "#6B7C93"
BLURPLE, LAVENDER, CYAN, MAGENTA, ORANGE, GREEN = (
    "#635BFF", "#B9B5FF", "#00D4FF", "#F96BEE", "#FFB86C", "#3ECF8E")

CODE = {  # syntax colours on DEEP
    "p": "#C9D6E3", "tag": "#7FD3FF", "attr": LAVENDER, "str": "#FFD58A",
    "num": "#FF9E7A", "kw": "#F98BE3", "fn": "#7FD3FF", "prompt": GREEN,
    "cmd": WHITE, "flag": LAVENDER, "com": "#7891AD", "key": "#7FD3FF",
}

# Feather-style line icons on a 24px grid.
ICONS = {
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "card": '<rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "cpu": ('<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/>'
            '<path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>'),
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "grid": ('<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/>'
             '<rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/>'),
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M8 10h.01M12 10h.01M16 10h.01"/>',
    "cloud": ('<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/>'
              '<path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>'),
    "package": ('<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>'
                '<polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>'),
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "heart": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
    "camera": '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>',
    "music": '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "arrow-up": '<line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>',
    "faceid": ('<path d="M7 3H5a2 2 0 0 0-2 2v2M17 3h2a2 2 0 0 1 2 2v2M7 21H5a2 2 0 0 1-2-2v-2M17 21h2a2 2 0 0 0 2-2v-2"/>'
               '<path d="M9 9v1M15 9v1M12 9v4h-1M9 16c1.7 1.2 4.3 1.2 6 0"/>'),
    "arrow-up-right": '<line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
}

# Filled brand marks on a 24px grid (Simple Icons).
BRANDS = {
    "x": "M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z",
    "linkedin": "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 4.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z",
    "npm": "M1.763 0C.786 0 0 .786 0 1.763v20.474C0 23.214.786 24 1.763 24h20.474c.977 0 1.763-.786 1.763-1.763V1.763C24 .786 23.214 0 22.237 0zM5.13 5.323l13.837.019-.009 13.836h-3.464l.01-10.382h-3.456L12.04 19.17H5.113z",
}

BASE_CSS = f"""
text{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""

# ── Text metrics ─────────────────────────────────────────────────────────────
_WEIGHTS = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"}
_FONT_DIRS = ["/usr/share/fonts", "/usr/local/share/fonts", "~/.fonts", "~/.local/share/fonts",
              "~/Library/Fonts", "/Library/Fonts"]
_fonts = {}


def _inter(weight):
    if weight not in _fonts:
        _fonts[weight] = None
        try:
            from PIL import ImageFont
            for d in _FONT_DIRS:
                hits = glob.glob(f"{os.path.expanduser(d)}/**/Inter-{_WEIGHTS[weight]}.[ot]tf", recursive=True)
                if hits:
                    _fonts[weight] = ImageFont.truetype(hits[0], 100)
                    break
        except Exception:
            pass
    return _fonts[weight]


def tw(s, size, weight=400, spacing=0.0, mono=False):
    """Rendered width of `s` in px (Inter metrics; a close stand-in for SF Pro / Segoe UI)."""
    if mono:
        return len(s) * size * 0.6 + spacing * len(s)
    font = _inter(weight)
    if font:
        return font.getlength(s) / 100 * size + spacing * len(s)
    w = sum(.66 if c.isupper() else .58 if c.isdigit() else .3 if c in " .,:;'|!il·" else .53 for c in s)
    return w * size * (1.06 if weight >= 600 else 1) + spacing * len(s)


def fit(s, size, maxw, weight=400, spacing=0.0, mono=False):
    w = tw(s, size, weight, spacing, mono)
    if w > maxw and (mono or _inter(weight)):
        raise SystemExit(f"✗ text overflow ({w:.0f}px > {maxw:.0f}px): {s!r}")
    return s


# ── SVG helpers ──────────────────────────────────────────────────────────────
def icon(name, x, y, size=24, color=WHITE, width=2):
    return (f'<g transform="translate({x} {y}) scale({size / 24:.4f})" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def brand(name, x, y, size=24, color=WHITE):
    return f'<path transform="translate({x} {y}) scale({size / 24:.4f})" fill="{color}" d="{BRANDS[name]}"/>'


def text(x, y, s, size, fill, weight=400, cls="", anchor="start", spacing=0, extra="", maxw=None):
    if maxw:
        fit(s, size, maxw, weight, spacing)
    attrs = f'x="{x:g}" y="{y:g}" font-size="{size}" font-weight="{weight}"'
    if fill:
        attrs += f' fill="{fill}"'
    if cls:
        attrs += f' class="{cls}"'
    if anchor != "start":
        attrs += f' text-anchor="{anchor}"'
    if spacing:
        attrs += f' letter-spacing="{spacing}"'
    return f"<text {attrs} {extra}>{escape(s)}</text>"


def code_line(x, y, tokens, size=15, cls="mono", extra="", maxw=None):
    if maxw:
        fit("".join(t for t, _ in tokens), size, maxw, mono=True)
    spans = "".join(f'<tspan fill="{CODE[k]}">{escape(t)}</tspan>' for t, k in tokens)
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" xml:space="preserve" class="{cls}" {extra}>{spans}</text>'


def glow(id_, color, opacity):
    return (f'<radialGradient id="{id_}"><stop offset="0" stop-color="{color}" stop-opacity="{opacity}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')


def lin(id_, *stops, x2=1, y2=0):
    st = "".join(f'<stop offset="{i / (len(stops) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(stops))
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{st}</linearGradient>'


def write(name, w, h, title, body, defs="", css=""):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-label="{escape(title)}" fill="none">\n<title>{escape(title)}</title>\n'
           f"<defs>{defs}<style>{BASE_CSS}{css}</style></defs>\n{body}\n</svg>\n")
    (OUT / name).write_text(svg, encoding="utf-8")


# Live numbers fetched daily by fetch_stats.py (absent until the first CI run).
STATS = json.loads((OUT / "stats.json").read_text()) if (OUT / "stats.json").exists() else {}


def fmt(n):
    if n < 1000:
        return str(n)
    for div, unit, at in ((1_000_000, "M", 999_500), (1000, "k", 1000)):
        if n >= at:
            v = f"{n / div:.1f}"
            return (v[:-2] if v.endswith(".0") or n >= div * 100 else v) + unit


def stat_row(right, y, items, min_x, size=14):
    """Right-aligned [icon] value pairs ending at `right` on baseline `y`."""
    out, cur = "", right
    for ic, val in reversed(items):
        w = tw(val, size, 600)
        out += text(round(cur - w, 1), y, val, size, SOFT, 600)
        cur -= w
        if ic:
            cur -= 21
            out += icon(ic, round(cur, 1), y - 12, 15, MUTED, 2.2)
        cur -= 16
    if items and cur + 16 < min_x:
        raise SystemExit(f"✗ stats row collides with eyebrow ({cur + 16:.0f} < {min_x:.0f})")
    return out


def lib_stats(key):
    if key == "all":
        if not STATS:
            return []
        total = sum(v.get("downloads", 0) for v in STATS.values())
        return [("package", str(len(STATS))), ("download", fmt(total))]
    s = STATS.get(key, {})
    return ([("star", str(s["stars"]))] if "stars" in s else []) + \
           ([("download", fmt(s["downloads"]))] if "downloads" in s else [])


def card_frame(x, y, w, h, rx, glows=""):
    """Navy card with clipped glows and a hairline border."""
    return (f'<clipPath id="cf"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>'
            f'<g clip-path="url(#cf)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{NAVY}"/>{glows}</g>'
            f'<rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h - 1.5}" rx="{rx - .75}" '
            f'stroke="{LINE}" stroke-width="1.5"/>')


SHADOW = ('<filter id="shadow" x="-40%" y="-80%" width="180%" height="360%">'
          '<feDropShadow dx="0" dy="18" stdDeviation="20" flood-color="#000814" flood-opacity=".42"/></filter>')
BLUR = '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>'
GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>'
         '<feColorMatrix type="saturate" values="0"/>'
         '<feComponentTransfer><feFuncA type="table" tableValues="0 .55"/></feComponentTransfer></filter>')
GRID = ('<pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse">'
        '<path d="M36 0H0V36" stroke="#FFFFFF" stroke-opacity=".07"/></pattern>')
MESH_CSS = """
.b1{animation:d1 19s ease-in-out infinite alternate}@keyframes d1{to{transform:translate(110px,50px)}}
.b2{animation:d2 23s ease-in-out infinite alternate}@keyframes d2{to{transform:translate(-90px,60px)}}
.b3{animation:d3 17s ease-in-out infinite alternate}@keyframes d3{to{transform:translate(80px,-50px)}}
.b4{animation:d4 21s ease-in-out infinite alternate}@keyframes d4{to{transform:translate(-100px,-40px)}}
"""


def mesh(clip_id):
    """Stripe-style animated gradient mesh with film grain, clipped to `clip_id`."""
    return f"""<g clip-path="url(#{clip_id})">
  <rect width="1200" height="600" fill="{BLURPLE}"/>
  <g filter="url(#blur)">
    <circle class="b1" cx="160" cy="40" r="260" fill="{BLURPLE}"/>
    <circle class="b2" cx="470" cy="150" r="230" fill="{MAGENTA}"/>
    <circle class="b3" cx="820" cy="30" r="270" fill="{CYAN}"/>
    <circle class="b4" cx="1110" cy="230" r="240" fill="{ORANGE}"/>
    <circle class="b2" cx="660" cy="330" r="190" fill="#7A73FF"/>
  </g>
  <rect width="1200" height="600" fill="url(#grid)"/>
  <rect width="1200" height="600" filter="url(#grain)" opacity=".35" style="mix-blend-mode:overlay"/>
</g>"""


# ── Porcelain & Ink (2026 redesign) ──────────────────────────────────────────
# Light editorial system: white cards, ink navy type, one blurple accent. Every
# value below is an OKLCH ramp step; contrast is measured against the surface the
# text actually sits on (white unless noted).
P = {
    "surface": "#FFFFFF",
    "sunken": "#F3F6FA",      # inset panels, chips
    "line": "#E1E5EA",        # hairlines, dividers
    "text": "#0B223E",        # 16.00:1
    "text2": "#293E5C",       # 10.84:1 — secondary headings
    "muted": "#525F6F",       # 6.51:1 — body copy
    "subtle": "#6B7583",      # 4.67:1 — meta, small caps labels
    "accent": "#5957ED",      # 5.24:1 — eyebrows, links, primary fill
    "accentHi": "#666AF9",
    "accentLo": "#4F46E5",
    "success": "#009A5C",     # icon fill only (3.64:1 non-text)
}
INK_RGB = "11 34 62"  # P["text"] as rgb, for tinted shadows


def elevation(id_, small=False):
    """Two-layer tinted shadow: a crisp contact shadow plus a soft ambient one."""
    a, b = ((1, 1, .06), (4, 6, .05)) if small else ((1, 1.5, .05), (12, 16, .08))
    return (f'<filter id="{id_}" x="-10%" y="-10%" width="120%" height="140%" color-interpolation-filters="sRGB">'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="{a[1]}"/><feOffset dy="{a[0]}" result="a1"/>'
            f'<feFlood flood-color="rgb({INK_RGB})" flood-opacity="{a[2]}"/><feComposite in2="a1" operator="in" result="s1"/>'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="{b[1]}"/><feOffset dy="{b[0]}" result="a2"/>'
            f'<feFlood flood-color="rgb({INK_RGB})" flood-opacity="{b[2]}"/><feComposite in2="a2" operator="in" result="s2"/>'
            '<feMerge><feMergeNode in="s2"/><feMergeNode in="s1"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def surface_card(x, y, w, h, rx, inner=""):
    """White card: elevation shadow, clipped content, 1px ink hairline at 8%."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{P["surface"]}" filter="url(#elev)"/>'
            f'<clipPath id="cardclip"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>'
            f'<g clip-path="url(#cardclip)">{inner}</g>'
            f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{rx - .5}" '
            f'stroke="rgb({INK_RGB})" stroke-opacity=".08"/>')


def embed(path):
    return "data:image/webp;base64," + base64.b64encode((OUT / path).read_bytes()).decode()


def porcelain_hero():
    W, H = 1200, 660
    CX, CY, CW, CH, R = 36, 24, 1128, 600, 28  # margins leave room for the shadow to fade out
    L = CX + 56                              # copy column
    # Hero render (Codex): 1024px square, placed at S×S. Screen + island measured in source px.
    AX, AY, S = 577, 14, 620
    k = S / 1024
    sx, sy, sw, sh, sr = AX + 341 * k, AY + 116 * k, 342 * k, 773 * k, 50 * k
    ix, iy, iw, ih = AX + 456 * k, AY + 126 * k, 110 * k, 31 * k
    g = Glyphs()
    copy_max = AX + 40 * k - 24 - L           # stop 24px short of the ribbon's leftmost edge

    # ── copy ──
    off = 10
    name_size = 78
    body = g.text(L, 148 + off, "React Native · iOS · Android", 20, P["accent"], 600, tracking=.01, maxw=copy_max)
    body += g.text(L - 3, 230 + off, "Trần Đình Huy", name_size, P["text"], 700, tracking=-.035, maxw=copy_max)
    body += g.text(L - 1, 284 + off, "Senior React Native Engineer", 32, P["text2"], 650, tracking=-.02, maxw=copy_max)
    body += g.text(L, 336 + off, "I build secure, production-grade mobile apps —", 21, P["muted"], 400, maxw=copy_max)
    body += g.text(L, 368 + off, "and open-source the infrastructure behind them.", 21, P["muted"], 400, maxw=copy_max)

    stats = [("5+", "YEARS SHIPPING"), ("4", "OPEN-SOURCE LIBS"), ("3", "PAYMENT GATEWAYS")]
    x = L
    for i, (n, lbl) in enumerate(stats):
        if i:
            body += f'<line x1="{x:.1f}" y1="{430 + off}" x2="{x:.1f}" y2="{504 + off}" stroke="{P["line"]}"/>'
            x += 36
        body += g.text(x - 1, 466 + off, n, 46, P["text"], 700, tracking=-.03, tnum=True)
        body += g.text(x, 496 + off, lbl, 13.5, P["subtle"], 600, tracking=.08)
        x += max(tw_(n, 46, 700, tracking=-.03), tw_(lbl, 13.5, 600, tracking=.08)) + 36
    # Below the ribbon's left lobe the stats may run up to the phone frame (source x≈395).
    if x - 36 > AX + 395 * k - 32:
        raise SystemExit(f"✗ hero stats collide with the phone ({x - 36:.0f}px)")

    # ── phone screen UI (vector, drawn over the render's keyed screen) ──
    u = ""
    u += f'<rect width="{sw:.2f}" height="{sh:.2f}" rx="{sr:.2f}" fill="{P["surface"]}"/>'
    u += g.text(22, 20, "9:41", 12.5, P["text"], 600)
    u += (f'<g fill="{P["text"]}"><rect x="{sw - 64:.1f}" y="13" width="3" height="6" rx="1"/>'
          f'<rect x="{sw - 59:.1f}" y="11" width="3" height="8" rx="1"/><rect x="{sw - 54:.1f}" y="9" width="3" height="10" rx="1"/></g>'
          f'<rect x="{sw - 45:.1f}" y="9.5" width="21" height="10" rx="3" stroke="{P["text"]}" stroke-opacity=".45"/>'
          f'<rect x="{sw - 43:.1f}" y="11.5" width="15" height="6" rx="1.5" fill="{P["text"]}"/>')
    pad = 15
    u += g.text(pad + 2, 80, "Checkout", 23, P["text"], 700, tracking=-.02)
    # card on file
    py = 98
    u += (f'<rect x="{pad}" y="{py}" width="{sw - 2 * pad:.1f}" height="56" rx="12" fill="{P["sunken"]}" stroke="{P["line"]}"/>'
          + g.text(pad + 14, py + 23, "VISA", 13, "#1A1F71", 800, tracking=.02)
          + g.text(sw - pad - 12, py + 22, "Change", 10.5, P["accent"], 600, anchor="end")
          + g.text(pad + 14, py + 43, "•••• 4242", 12.5, P["text2"], 500, family="mono", tracking=.04))
    rows = ["Certificate pinned", "Face ID verified", "Risk check passed"]
    for i, r in enumerate(rows):
        y = 192 + i * 31
        u += ("<g>"
              f'<circle cx="{pad + 10}" cy="{y - 4}" r="8.5" fill="{P["success"]}"/>'
              + icon("check", pad + 4, y - 10, 12, "#FFFFFF", 3)
              + g.text(pad + 27, y, r, 11.5, P["text2"], 500, maxw=sw - 2 * pad - 30) + "</g>")
    u += f'<line x1="{pad}" y1="276" x2="{sw - pad:.1f}" y2="276" stroke="{P["line"]}"/>'
    u += g.text(pad + 1, 304, "Total", 12, P["subtle"], 500)
    u += g.text(sw - pad, 305, "₫1.250.000", 17, P["text"], 700, anchor="end", tracking=-.01, tnum=True)
    by, bw, bh = 324, sw - 2 * pad, 46
    label = "Pay with Face ID"
    gw = 16 + 8 + tw_(label, 13.5, 600)
    gx = pad + (bw - gw) / 2
    u += (f'<rect x="{pad}" y="{by}" width="{bw:.1f}" height="{bh}" rx="12" fill="url(#btn)"/>'
          f'<rect x="{pad + .5}" y="{by + .5}" width="{bw - 1:.1f}" height="{bh - 1}" rx="11.5" stroke="#FFFFFF" stroke-opacity=".22"/>'
          f'<clipPath id="btnclip"><rect x="{pad}" y="{by}" width="{bw:.1f}" height="{bh}" rx="12"/></clipPath>'
          f'<g clip-path="url(#btnclip)"><polygon class="shine" points="{pad - 60},{by + bh} {pad - 30},{by} {pad + 6},{by} {pad - 24},{by + bh}" fill="#FFFFFF" fill-opacity=".22"/></g>'
          + icon("faceid", round(gx, 1), by + 15, 16, "#FFFFFF", 2.2)
          + g.text(gx + 24, by + 28, label, 13.5, "#FFFFFF", 600))
    lock_lbl = "Secured with SSL pinning"
    lw = 11 + 6 + tw_(lock_lbl, 10.5, 500)
    lx = (sw - lw) / 2
    u += icon("lock", round(lx, 1), by + bh + 21, 11, P["subtle"], 2.4) + g.text(lx + 17, by + bh + 30, lock_lbl, 10.5, P["subtle"], 500)
    u += f'<rect x="{sw / 2 - 36:.1f}" y="{sh - 14:.1f}" width="72" height="4" rx="2" fill="{P["text"]}" fill-opacity=".22"/>'
    if (OUT / "art/screen.webp").exists():     # a real screenshot replaces the vector checkout UI
        u = f'<image href="{embed("art/screen.webp")}" width="{sw:.2f}" height="{sh:.2f}" preserveAspectRatio="xMidYMin slice"/>'
    screen = (f'<clipPath id="scr"><rect x="{sx:.2f}" y="{sy:.2f}" width="{sw:.2f}" height="{sh:.2f}" rx="{sr:.2f}"/></clipPath>'
              f'<g clip-path="url(#scr)"><g transform="translate({sx:.2f} {sy:.2f})">{u}</g></g>'
              f'<rect x="{ix:.2f}" y="{iy:.2f}" width="{iw:.2f}" height="{ih:.2f}" rx="{ih / 2:.2f}" fill="#05070A"/>')

    art = f'<image href="{embed("art/hero-art.webp")}" x="{AX}" y="{AY}" width="{S}" height="{S}"/>'
    defs = (elevation("elev")
            + f'<linearGradient id="btn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["accentHi"]}"/>'
              f'<stop offset="1" stop-color="{P["accentLo"]}"/></linearGradient>')
    css = """
.shine{animation:sh 4.5s 1.4s cubic-bezier(.4,0,.2,1) infinite}@keyframes sh{0%{transform:translateX(0)}35%,100%{transform:translateX(260px)}}
"""
    full = surface_card(CX, CY, CW, CH, R, art + screen) + body
    write("hero.svg", W, H,
          "Trần Đình Huy — Senior React Native Engineer. I build secure, production-grade mobile apps "
          "and open-source the infrastructure behind them.", full, defs + g.svg_defs(), css)


def porcelain_button(name, label, mark, primary=False):
    g = Glyphs()
    h, size, m = 52, 17, 16                  # pill height, label size, shadow margin
    lw = tw_(label, size, 600)
    pw = round(24 + 20 + 12 + lw + (12 + 16 + 22 if primary else 26))
    W, H = pw + 2 * m, h + 2 * m
    x, y = m, m - 3
    fg = "#FFFFFF" if primary else P["text"]
    if primary:
        pill = (f'<rect x="{x}" y="{y}" width="{pw}" height="{h}" rx="{h / 2}" fill="url(#bg)" filter="url(#glow)"/>'
                f'<rect x="{x + .5}" y="{y + .5}" width="{pw - 1}" height="{h - 1}" rx="{h / 2 - .5}" stroke="#FFFFFF" stroke-opacity=".22"/>')
        defs = (f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["accentHi"]}"/>'
                f'<stop offset="1" stop-color="{P["accentLo"]}"/></linearGradient>'
                '<filter id="glow" x="-20%" y="-40%" width="140%" height="200%" color-interpolation-filters="sRGB">'
                '<feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#5957ED" flood-opacity=".32"/></filter>')
    else:
        pill = (f'<rect x="{x}" y="{y}" width="{pw}" height="{h}" rx="{h / 2}" fill="#FFFFFF" filter="url(#elev)"/>'
                f'<rect x="{x + .5}" y="{y + .5}" width="{pw - 1}" height="{h - 1}" rx="{h / 2 - .5}" stroke="rgb({INK_RGB})" stroke-opacity=".12"/>')
        defs = elevation("elev", small=True)
    body = pill + brand(mark, x + 24, y + 16, 20, fg) + g.text(x + 56, y + 32.5, label, size, fg, 600)
    if primary:
        body += icon("arrow-up-right", round(x + 56 + lw + 12), y + 18, 16, fg, 2.4)
    write(name, W, H, label, body, defs + g.svg_defs())
    return W, H



# Page-level colours for artwork that sits directly on GitHub's page (headers), per theme.
THEMES = {
    "light": {"text": P["text"], "accent": P["accent"]},            # 16.00:1 / 5.24:1 on #FFFFFF
    "dark": {"text": "#F1F4F7", "accent": "#8F9BFB"},               # 17.14:1 / 7.43:1 on #0D1117
}


def porcelain_header(name, eyebrow, title):
    """Section header, emitted twice (name.svg + name-dark.svg) for a <picture> theme switch."""
    for theme, c in THEMES.items():
        g = Glyphs()
        body = (g.text(38, 40, eyebrow, 17, c["accent"], 700, tracking=.16, maxw=1124)
                + g.text(35, 104, title, 52, c["text"], 700, tracking=-.035, maxw=1124))
        write(name if theme == "light" else name.replace(".svg", "-dark.svg"),
              1200, 128, f"{eyebrow} {title}", body, g.svg_defs())


def art_icon(key, x, y, size):
    """A Codex-rendered glass icon if present, else the line icon in the accent colour."""
    f = OUT / f"art/icons/{key}.webp"
    if f.exists():
        return f'<image href="{embed(f"art/icons/{key}.webp")}" x="{x}" y="{y}" width="{size}" height="{size}"/>'
    s = size * .6
    return icon(key, x + (size - s) / 2, y + (size - s) / 2, s, P["accent"], 1.8)


EXPERTISE_P = [
    ("lock", "Mobile security", ["SSL pinning, biometric auth and hardened key", "storage that hold up against real MITM attacks."],
     ["SSL Pinning", "Biometrics", "Keystore"]),
    ("card", "Payments", ["Production checkout flows on Vietnam's leading", "gateways — built for real money, not demos."],
     ["VNPay", "ZaloPay", "Payoo"]),
    ("zap", "Release engineering", ["Automated pipelines and OTA updates that ship", "fixes in minutes instead of review cycles."],
     ["Fastlane", "Expo Updates", "TestFlight"]),
    ("cpu", "New Architecture", ["Native modules on Nitro & TurboModules, 60 fps", "UI with Reanimated, state that scales."],
     ["Nitro", "TurboModules", "Reanimated"]),
]


def porcelain_expertise():
    X0, Y0, GAP = 36, 24, 24
    cw, ch, R, pad = (1128 - GAP) // 2, 344, 24, 40
    W, H = 1200, Y0 + 2 * ch + GAP + 36
    g = Glyphs()
    body = ""
    for i, (ic, title, desc, chips) in enumerate(EXPERTISE_P):
        x = X0 + (i % 2) * (cw + GAP)
        y = Y0 + (i // 2) * (ch + GAP)
        inner = cw - 2 * pad
        body += (f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="{R}" fill="{P["surface"]}" filter="url(#elev)"/>'
                 f'<rect x="{x + .5}" y="{y + .5}" width="{cw - 1}" height="{ch - 1}" rx="{R - .5}" stroke="rgb({INK_RGB})" stroke-opacity=".08"/>'
                 + art_icon(ic, x + pad - 14, y + 20, 120)
                 + g.text(x + pad - 1, y + 186, title, 30, P["text"], 700, tracking=-.025, maxw=inner)
                 + g.text(x + pad, y + 224, desc[0], 19, P["muted"], maxw=inner)
                 + g.text(x + pad, y + 252, desc[1], 19, P["muted"], maxw=inner))
        cx = x + pad
        for c in chips:
            w = round(tw_(c, 15, 600) + 28)
            if cx + w > x + cw - pad:
                raise SystemExit(f"✗ chip row overflows in {title!r} at {c!r}")
            body += (f'<rect x="{cx}" y="{y + 276}" width="{w}" height="34" rx="17" fill="{P["sunken"]}" stroke="{P["line"]}"/>'
                     + g.text(cx + 14, y + 298, c, 15, P["text2"], 600))
            cx += w + 8
    write("expertise.svg", W, H,
          "Expertise: mobile security, payments, release engineering and the React Native New Architecture.",
          body, elevation("elev") + g.svg_defs())

# ── Hero ─────────────────────────────────────────────────────────────────────
def hero():
    W, H, L = 1200, 612, 66
    px, py, pw, ph = 820, 26, 272, 548          # phone body
    sx, sy, sw, sh = px + 10, py + 10, 252, 528  # screen
    cx, cy = sx + 24, sy + 124                   # credit card
    bx, by = sx + 24, sy + 440                   # pay button

    defs = (BLUR + SHADOW + GRID + GRAIN
            + '<clipPath id="card"><rect x="18" y="0" width="1164" height="600" rx="28"/></clipPath>'
            + '<clipPath id="band"><polygon points="18,0 1182,0 1182,300 18,130"/></clipPath>'
            + f'<clipPath id="screen"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="37"/></clipPath>'
            + f'<clipPath id="btn"><rect x="{bx}" y="{by}" width="204" height="50" rx="12"/></clipPath>'
            + f'<clipPath id="ccard"><rect x="{cx}" y="{cy}" width="204" height="128" rx="14"/></clipPath>'
            + lin("title", "#C3BEFF", "#80E9FF")
            + lin("cc", BLURPLE, "#8F6BFF", CYAN, x2=1, y2=1)
            + lin("ok", GREEN, CYAN, x2=1, y2=1)
            + lin("bezel", "#4A5878", "#111A2C", "#2B3753", x2=1, y2=1)
            + '<linearGradient id="glare" x1="0" y1="0" x2="1" y2="1">'
              '<stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>'
            + lin("shine", "#FFFFFF00", "#FFFFFF66", "#FFFFFF00")
            + glow("pglow", BLURPLE, .55))
    css = MESH_CSS + """
.float{animation:fl 6s ease-in-out infinite alternate}
.float2{animation:fl 7s 1.2s ease-in-out infinite alternate}
.float3{animation:fl 8s .6s ease-in-out infinite alternate}
@keyframes fl{to{transform:translateY(-12px)}}
.pulse{transform-box:fill-box;transform-origin:center;animation:pu 2.4s ease-out infinite}
@keyframes pu{from{transform:scale(1);opacity:.7}to{transform:scale(3);opacity:0}}
.shine{animation:sh 3.8s ease-in-out infinite}
@keyframes sh{0%{transform:translateX(-120px)}55%,100%{transform:translateX(320px)}}
"""
    stats = [("5+", "YEARS SHIPPING"), ("4", "OPEN-SOURCE LIBS"), ("3", "PAYMENT GATEWAYS")]
    stat_svg = ""
    for i, (n, lbl) in enumerate(stats):
        x = L + i * 200
        if i:
            stat_svg += f'<line x1="{x - 28}" y1="480" x2="{x - 28}" y2="550" stroke="{LINE}" stroke-width="1.5"/>'
        stat_svg += text(x, 516, n, 38, WHITE, 700, spacing=-0.3)
        stat_svg += text(x, 543, lbl, 14, "#8FA3B8", 700, spacing=1.1, maxw=170)

    eyebrow = "React Native  ·  iOS  ·  Android"
    pill_w = round(54 + tw(eyebrow, 15, 600))

    rows = ["Certificate pinned", "Face ID verified", "Risk check passed"]
    row_svg = ""
    for i, r in enumerate(rows):
        y = sy + 282 + i * 40
        row_svg += (f'<circle cx="{sx + 34}" cy="{y - 5}" r="10" fill="url(#ok)"/>'
                    + icon("check", sx + 27, y - 12, 14, WHITE, 3)
                    + text(sx + 54, y, r, 14, INK, 500, maxw=170)
                    + f'<line x1="{sx + 24}" y1="{y + 16}" x2="{sx + 228}" y2="{y + 16}" stroke="#E3E8EE"/>')

    dots = "".join(f'<circle cx="{cx + 22 + i * 10}" cy="{cy + 86}" r="3" fill="#FFFFFF"/>' for i in range(4))

    body = f"""
<g clip-path="url(#card)">
  <rect x="18" width="1164" height="600" fill="{NAVY}"/>
  <rect x="18" width="1164" height="600" fill="url(#grid)" opacity=".5"/>
  {mesh("band")}
  <ellipse cx="960" cy="560" rx="320" ry="160" fill="url(#pglow)"/>

  <!-- Copy -->
  <rect x="{L}" y="194" width="{pill_w}" height="38" rx="19" fill="#FFFFFF" fill-opacity=".07" stroke="#FFFFFF" stroke-opacity=".14"/>
  <circle class="pulse" cx="{L + 22}" cy="213" r="5" fill="{GREEN}"/>
  <circle cx="{L + 22}" cy="213" r="5" fill="{GREEN}"/>
  {text(L + 38, 218, eyebrow, 15, SOFT, 600, extra='xml:space="preserve"')}
  {text(L - 3, 304, "Trần Đình Huy", 68, WHITE, 700, spacing=-1.0, maxw=480)}
  {text(L, 354, "Senior React Native Engineer", 31, "url(#title)", 600, spacing=-0.2, maxw=480)}
  {text(L, 403, "I build secure, production-grade mobile apps —", 21, MUTED, maxw=488)}
  {text(L, 434, "and open-source the infrastructure behind them.", 21, MUTED, maxw=488)}
  {stat_svg}

  <!-- Phone -->
  <g class="float">
    <g fill="#26324C">
      <rect x="{px - 3}" y="{py + 108}" width="5" height="26" rx="2"/>
      <rect x="{px - 3}" y="{py + 150}" width="5" height="50" rx="2"/>
      <rect x="{px - 3}" y="{py + 210}" width="5" height="50" rx="2"/>
      <rect x="{px + pw - 2}" y="{py + 170}" width="5" height="78" rx="2"/>
    </g>
    <g filter="url(#shadow)"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="46" fill="url(#bezel)"/></g>
    <rect x="{px + 3}" y="{py + 3}" width="{pw - 6}" height="{ph - 6}" rx="43" fill="#05080F"/>
    <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="37" fill="#F6F9FC"/>
    <rect x="{sx + 84}" y="{sy + 12}" width="84" height="26" rx="13" fill="#05080F"/>
    {text(sx + 28, sy + 31, "9:41", 14, INK, 600)}
    <g fill="{INK}"><rect x="{sx + 186}" y="{sy + 24}" width="3" height="7" rx="1"/><rect x="{sx + 191}" y="{sy + 21}" width="3" height="10" rx="1"/><rect x="{sx + 196}" y="{sy + 18}" width="3" height="13" rx="1"/></g>
    <rect x="{sx + 205}" y="{sy + 19}" width="22" height="11" rx="3" stroke="{INK}" stroke-opacity=".5"/>
    <rect x="{sx + 207}" y="{sy + 21}" width="16" height="7" rx="1.5" fill="{INK}"/>

    {text(sx + 24, sy + 92, "Checkout", 24, INK, 700, spacing=-0.4)}
    {icon("lock", sx + 24, sy + 104, 13, GREEN, 2.5)}
    {text(sx + 42, sy + 115, "Secured connection", 12, UI_MUTED, 500)}

    <g clip-path="url(#ccard)">
      <rect x="{cx}" y="{cy}" width="204" height="128" fill="url(#cc)"/>
      <circle cx="{cx + 186}" cy="{cy + 10}" r="70" fill="{MAGENTA}" opacity=".45"/>
      <circle cx="{cx + 26}" cy="{cy + 130}" r="60" fill="{CYAN}" opacity=".35"/>
    </g>
    <rect x="{cx + 18}" y="{cy + 20}" width="30" height="22" rx="5" fill="#FFE2A8" fill-opacity=".92"/>
    <path d="M{cx + 18} {cy + 31}h30M{cx + 33} {cy + 20}v22" stroke="#C99A4B" stroke-opacity=".5"/>
    <path d="M{cx + 174} {cy + 24}a10 10 0 0 1 0 16M{cx + 180} {cy + 20}a16 16 0 0 1 0 24" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity=".85"/>
    {dots}
    {text(cx + 66, cy + 92, "4242", 16, WHITE, 600, cls="mono", spacing=1.5)}
    {text(cx + 18, cy + 113, "TRAN DINH HUY", 10, WHITE, 600, spacing=1.6, extra='opacity=".85"')}
    <circle cx="{cx + 170}" cy="{cy + 108}" r="9" fill="#FFFFFF" fill-opacity=".55"/><circle cx="{cx + 182}" cy="{cy + 108}" r="9" fill="#FFFFFF" fill-opacity=".35"/>

    {row_svg}
    {text(sx + 24, sy + 418, "Total", 13, UI_MUTED, 500)}
    {text(sx + 228, sy + 418, "₫1.250.000", 18, INK, 700, anchor="end")}
    <rect x="{bx}" y="{by}" width="204" height="50" rx="12" fill="{BLURPLE}"/>
    <g clip-path="url(#btn)"><rect class="shine" x="{bx - 44}" y="{by}" width="70" height="50" fill="url(#shine)" transform="skewX(-20)"/></g>
    {text(bx + 102, by + 30, "Pay with Face ID", 15, WHITE, 600, anchor="middle")}
    <rect x="{sx + 76}" y="{sy + 512}" width="100" height="5" rx="2.5" fill="{INK}" fill-opacity=".25"/>
    <g clip-path="url(#screen)"><polygon points="{sx},{sy} {sx + 170},{sy} {sx},{sy + 260}" fill="url(#glare)" opacity=".22"/></g>
  </g>

  <!-- Floating notifications -->
  <g class="float2">
    <g filter="url(#shadow)"><rect x="566" y="168" width="266" height="68" rx="16" fill="#FFFFFF"/></g>
    <rect x="566.5" y="168.5" width="265" height="67" rx="15.5" stroke="{INK}" stroke-opacity=".06"/>
    <circle cx="602" cy="202" r="18" fill="url(#ok)"/>
    {icon("arrow-up", 592, 192, 20, WHITE, 2.6)}
    {text(632, 197, "OTA update shipped", 14, INK, 700, maxw=180)}
    {text(632, 217, "Rolled out to 50% · no review", 12, UI_MUTED, 500, maxw=186)}
  </g>
  <g class="float3">
    <g filter="url(#shadow)"><rect x="978" y="72" width="192" height="68" rx="16" fill="#FFFFFF"/></g>
    <rect x="978.5" y="72.5" width="191" height="67" rx="15.5" stroke="{INK}" stroke-opacity=".06"/>
    <circle cx="1014" cy="106" r="18" fill="url(#cc)"/>
    {icon("message", 1004, 96, 20, WHITE, 2.4)}
    {text(1044, 101, "OTP auto-filled", 14, INK, 700, maxw=116)}
    {text(1044, 121, "No SMS permission", 12, UI_MUTED, 500, maxw=116)}
  </g>
</g>
<rect x="18.5" y=".5" width="1163" height="599" rx="27.5" stroke="#FFFFFF" stroke-opacity=".08"/>"""
    write("hero.svg", W, H,
          "Trần Đình Huy — Senior React Native Engineer. I build secure, production-grade mobile apps "
          "and open-source the infrastructure behind them.", body, defs, css)


# ── Buttons ──────────────────────────────────────────────────────────────────
def button(name, label, mark, primary=False):
    size, h = 17, 52
    lw = tw(label, size, 600)
    w = round(54 + lw + (14 + 18 + 22 if primary else 26))
    fill = "url(#bg)" if primary else NAVY
    stroke = "" if primary else f'stroke="{LINE}" stroke-width="1.5"'
    arrow = icon("arrow-up-right", round(54 + lw + 14), 17, 18, WHITE, 2.4) if primary else ""
    body = (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{(h - 2) / 2}" fill="{fill}" {stroke}/>'
            + brand(mark, 24, 16, 20) + text(54, 32, label, size, WHITE, 600) + arrow)
    write(name, w, h, label, body, lin("bg", BLURPLE, "#8D7BFF"))


# ── Section headers (adapt to light/dark) ────────────────────────────────────
def header(name, eyebrow, title, sub):
    css = (f".h{{fill:{INK}}}.s{{fill:{INK_MUTED}}}"
           f"@media (prefers-color-scheme: dark){{.h{{fill:#F6F9FC}}.s{{fill:{MUTED}}}}}")
    body = (text(18, 38, eyebrow, 15, "url(#eb)", 800, spacing=2.4)
            + text(16, 98, title, 46, "", 700, cls="h", spacing=-0.6, maxw=1164)
            + text(18, 140, sub, 20, "", 400, cls="s", maxw=1164))
    write(name, 1200, 160, f"{title} {sub}", body, lin("eb", BLURPLE, "#00B8E6"), css)


# ── Expertise grid ───────────────────────────────────────────────────────────
EXPERTISE = [
    ("lock", "Mobile security", BLURPLE, CYAN,
     ["SSL pinning, biometric auth and hardened key", "storage that hold up against real MITM attacks."],
     ["SSL Pinning", "Biometrics", "Keystore", "Anti-fraud"]),
    ("card", "Payments", MAGENTA, ORANGE,
     ["Production checkout flows on Vietnam's leading", "gateways — built for real money, not demos."],
     ["VNPay", "ZaloPay", "Payoo"]),
    ("zap", "Release engineering", GREEN, CYAN,
     ["Automated pipelines and OTA updates that ship", "fixes in minutes instead of review cycles."],
     ["Fastlane", "Expo Updates", "CodePush", "TestFlight"]),
    ("cpu", "New Architecture", "#7A73FF", MAGENTA,
     ["Native modules on Nitro & TurboModules, 60 fps", "UI with Reanimated, state that scales."],
     ["Nitro", "TurboModules", "Reanimated", "TanStack"]),
]


def expertise():
    tw_, th, gap = 570, 298, 24
    W, H = 1200, th * 2 + gap
    defs, body = "", ""
    for i, (ic, title, a, b, desc, chips) in enumerate(EXPERTISE):
        x = 18 + (i % 2) * (tw_ + gap)
        y = (i // 2) * (th + gap)
        inner = x + tw_ - 36
        defs += (lin(f"g{i}", a, b, x2=1, y2=1) + glow(f"r{i}", a, .32)
                 + f'<clipPath id="c{i}"><rect x="{x}" y="{y}" width="{tw_}" height="{th}" rx="22"/></clipPath>')
        body += (f'<g clip-path="url(#c{i})"><rect x="{x}" y="{y}" width="{tw_}" height="{th}" fill="{NAVY}"/>'
                 f'<circle cx="{x + tw_ - 40}" cy="{y + 10}" r="250" fill="url(#r{i})"/></g>'
                 f'<rect x="{x + .75}" y="{y + .75}" width="{tw_ - 1.5}" height="{th - 1.5}" rx="21.25" stroke="{LINE}" stroke-width="1.5"/>'
                 f'<rect x="{x + 36}" y="{y + 36}" width="56" height="56" rx="15" fill="url(#g{i})"/>'
                 + icon(ic, x + 50, y + 50, 28, WHITE, 2.1)
                 + text(x + 35, y + 140, title, 28, WHITE, 700, spacing=-0.3, maxw=inner - x)
                 + text(x + 36, y + 177, desc[0], 19, MUTED, maxw=inner - x - 36)
                 + text(x + 36, y + 205, desc[1], 19, MUTED, maxw=inner - x - 36))
        chx = x + 36
        for c in chips:
            cw = round(tw(c, 15, 600) + 30)
            if chx + cw > inner:
                raise SystemExit(f"✗ chip row overflows in {title!r} at {c!r}")
            body += (f'<rect x="{chx}" y="{y + 228}" width="{cw}" height="34" rx="17" fill="#FFFFFF" '
                     f'fill-opacity=".06" stroke="#FFFFFF" stroke-opacity=".12"/>'
                     + text(chx + 15, y + 250, c, 15, SOFT, 600))
            chx += cw + 8
    write("expertise.svg", W, H,
          "Expertise: mobile security, payments, release engineering and the React Native New Architecture.",
          body, defs)


# ── Library cards ────────────────────────────────────────────────────────────
def flagship():
    W, H, L = 1200, 492, 66
    wx, wy, ww, wh = 606, 44, 528, 392  # code window
    defs = glow("ga", BLURPLE, .40) + glow("gb", CYAN, .22) + lin("ok", GREEN, CYAN, x2=1, y2=1)
    css = """
.ln{animation:in .6s ease-out both}
@keyframes in{from{opacity:0;transform:translateY(6px)}}
.cur{animation:bl 1.1s steps(1) infinite}@keyframes bl{50%{opacity:0}}
"""
    feats = [("TrustKit + OkHttp", L, 304), ("Expo config plugin", L + 262, 304),
             ("Audit-mode rollout", L, 342), ("Signed OTA pin updates", L + 262, 342)]
    feat_svg = "".join(
        f'<circle cx="{x + 10}" cy="{y - 6}" r="10" fill="url(#ok)"/>' + icon("check", x + 3, y - 13, 14, WHITE, 3)
        + text(x + 30, y, s, 17, SOFT, 500, maxw=230) for s, x, y in feats)

    code = [
        [("$ ", "prompt"), ("npx react-native-ssl-manager pins api.example.com", "cmd")],
        [],
        [("// ssl_config.json", "com")],
        [("{", "p")],
        [('  "sha256Keys"', "key"), (": {", "p")],
        [('    "api.example.com"', "key"), (": [", "p")],
        [('      "sha256/r/mIkG3eEpVdm+u/ko/cwxzOMo1…="', "str"), (",", "p")],
        [('      "sha256/YLh1dUR9y6Kja30RrAn7JKnbQG…="', "str")],
        [("    ]", "p")],
        [("  }", "p")],
        [("}", "p")],
        [("// pinned at app launch — zero JS changes", "com")],
    ]
    lh, top = 26, wy + 78
    code_svg = "".join(
        code_line(wx + 24, top + i * lh, toks, 15.5, cls="mono ln",
                  extra=f'style="animation-delay:{.15 + i * .09:.2f}s"', maxw=ww - 48)
        for i, toks in enumerate(code) if toks)
    last = "".join(t for t, _ in code[-1])
    cmd = "npm i react-native-ssl-manager"
    cmd_w = round(46 + tw("$ " + cmd, 16, mono=True))
    eyebrow = "FLAGSHIP · SECURITY"

    body = f"""
{card_frame(18, 0, 1164, 480, 26, '<circle cx="66" cy="0" r="480" fill="url(#ga)"/><circle cx="1182" cy="480" r="440" fill="url(#gb)"/>')}
<rect x="{L}" y="44" width="{round(tw(eyebrow, 14, 700, 1.6) + 32)}" height="32" rx="16" fill="{BLURPLE}" fill-opacity=".2" stroke="{BLURPLE}" stroke-opacity=".55"/>
{text(L + 16, 65, eyebrow, 14, LAVENDER, 700, spacing=1.6)}
{stat_row(wx - 40, 65, ([(None, "v" + STATS["ssl"]["version"])] if "version" in STATS.get("ssl", {}) else []) + lib_stats("ssl"), L + tw(eyebrow, 14, 700, 1.6) + 48)}
{text(L - 2, 142, "react-native-ssl-manager", 40, WHITE, 700, spacing=-0.5, maxw=wx - L - 30)}
{text(L, 188, "Certificate pinning for React Native & Expo. Your", 19, MUTED, maxw=wx - L - 40)}
{text(L, 217, "app refuses every connection that doesn't match —", 19, MUTED, maxw=wx - L - 40)}
{text(L, 246, "even through Charles, Proxyman or a rogue Wi-Fi.", 19, MUTED, maxw=wx - L - 40)}
{feat_svg}
<rect x="{L}" y="390" width="{cmd_w}" height="46" rx="12" fill="{DEEP}" stroke="{LINE}"/>
{code_line(L + 22, 419, [("$ ", "prompt"), (cmd, "cmd")], 16)}
{text(L + cmd_w + 18, 419, "Nitro · New Arch", 15, SUBTLE, 600, maxw=wx - L - cmd_w - 40)}

<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="{DEEP}" stroke="{LINE}"/>
<circle cx="{wx + 22}" cy="{wy + 20}" r="6" fill="#FF5F57"/><circle cx="{wx + 42}" cy="{wy + 20}" r="6" fill="#FEBC2E"/><circle cx="{wx + 62}" cy="{wy + 20}" r="6" fill="#28C840"/>
{text(wx + ww / 2, wy + 25, "zsh — my-app", 13, SUBTLE, 600, anchor="middle")}
<line x1="{wx}" y1="{wy + 40}" x2="{wx + ww}" y2="{wy + 40}" stroke="{LINE}"/>
{code_svg}
<rect class="cur" x="{round(wx + 24 + tw(last, 15.5, mono=True) + 5)}" y="{top + 11 * lh - 14}" width="9" height="18" fill="{CYAN}"/>"""
    write("lib-ssl-manager.svg", W, H,
          "react-native-ssl-manager — certificate pinning for React Native & Expo. TrustKit + OkHttp, "
          "Expo config plugin, audit mode and signed OTA pin updates.", body, defs, css)


# Small product illustrations, right-aligned to x=564 in the top row of a card.
def art_icons():
    items = [("star", ORANGE), ("heart", MAGENTA), ("zap", CYAN), ("camera", GREEN), ("music", LAVENDER)]
    out = ""
    for i, (ic, c) in enumerate(items):
        x = 300 + i * 52
        out += (f'<g class="pop" style="animation-delay:{i * .18:.2f}s">'
                f'<rect x="{x}" y="42" width="44" height="44" rx="12" fill="#FFFFFF" fill-opacity=".06" stroke="#FFFFFF" stroke-opacity=".12"/>'
                + icon(ic, x + 11, 53, 22, c, 2) + "</g>")
    return out, ".pop{animation:pop 5s ease-in-out infinite}@keyframes pop{0%,100%{transform:translateY(0)}12%{transform:translateY(-6px)}24%{transform:translateY(0)}}"


def art_otp():
    out = ""
    for i, d in enumerate("482916"):
        x = 296 + i * 44
        out += (f'<rect x="{x}" y="40" width="36" height="48" rx="10" fill="#FFFFFF" fill-opacity=".06" stroke="#FFFFFF" stroke-opacity=".14"/>'
                f'<rect class="hl" x="{x}" y="40" width="36" height="48" rx="10" stroke="{GREEN}" stroke-width="1.5" style="animation-delay:{i * .12:.2f}s"/>'
                + text(x + 18, 72, d, 22, WHITE, 700, anchor="middle", extra=f'class="dg" style="animation-delay:{i * .12:.2f}s"'))
    css = (".dg,.hl{animation:dg 8s ease-out infinite both}"
           "@keyframes dg{0%,3%{opacity:0}7%,95%{opacity:1}99%,100%{opacity:0}}"
           ".hl{animation-name:hl}@keyframes hl{0%,3%{opacity:0}6%{opacity:1}14%,100%{opacity:0}}")
    return out, css


def art_rollout():
    x, y, w = 288, 39, 264
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="50" rx="12" fill="#FFFFFF" fill-opacity=".06" stroke="#FFFFFF" stroke-opacity=".12"/>'
           f'<circle cx="{x + 20}" cy="{y + 19}" r="4" fill="{GREEN}"/>'
           + text(x + 32, y + 24, "v2.4.1", 14, WHITE, 600, cls="mono")
           + text(x + w - 16, y + 24, "50% rollout", 13, GREEN, 700, anchor="end")
           + f'<rect x="{x + 16}" y="{y + 34}" width="{w - 32}" height="6" rx="3" fill="#FFFFFF" fill-opacity=".1"/>'
           f'<rect class="grow" x="{x + 16}" y="{y + 34}" width="{(w - 32) / 2}" height="6" rx="3" fill="url(#bar)"/>')
    css = (".grow{transform-box:fill-box;transform-origin:left;animation:gr 5s ease-in-out infinite}"
           "@keyframes gr{0%{transform:scaleX(0)}45%,85%{transform:scaleX(1)}100%{transform:scaleX(1);opacity:0}}")
    return out, css


def art_packages():
    items = [("SSL", BLURPLE), ("ICN", MAGENTA), ("SMS", GREEN), ("OTA", CYAN), ("+1", "#2A4466")]
    out = ""
    for i, (lbl, c) in enumerate(items):
        x = 370 + i * 40
        out += (f'<circle cx="{x}" cy="64" r="22" fill="{c}" stroke="{NAVY}" stroke-width="3"/>'
                + text(x, 68, lbl, 11, WHITE, 800, anchor="middle", spacing=.4))
    return out, ""


LIBS = [
    ("lib-iconify.svg", "grid", MAGENTA, ORANGE, "#FFC1F7", "ICONS · iOS · ANDROID · WEB", "react-native-iconify",
     ["200,000+ icons from 150+ sets, loaded by name.", "Native caching via SDWebImage & Glide."],
     [("<", "p"), ("IconifyIcon", "tag"), (" name", "attr"), ("=", "p"), ('"mdi:rocket-launch"', "str"),
      (" size", "attr"), ("={", "p"), ("32", "num"), ("} />", "p")], art_icons, "iconify"),
    ("lib-sms-retriever.svg", "message", GREEN, CYAN, "#9FF0CB", "OTP · ANDROID · NITRO", "sms-retriever-nitro-module",
     ["One-tap OTP autofill on Android, zero SMS", "permissions. Nitro + TurboModules, Expo-ready."],
     [("const", "kw"), (" { smsCode } = ", "p"), ("useSMSRetriever", "fn"), ("({ onSuccess })", "p")], art_otp, "sms"),
    ("lib-ota-updates.svg", "cloud", GREEN, BLURPLE, "#9FF0CB", "OTA · EXPO · SUPABASE", "supabase-expo-ota-updates",
     ["Self-hosted OTA updates for Expo on Supabase.", "Staged rollouts and auto-rollback on crash."],
     [("$ ", "prompt"), ("npx supabase-expo-ota-updates publish", "cmd"), (" --rollout", "flag"), (" 50", "num")],
     art_rollout, "ota"),
    ("lib-more.svg", "package", BLURPLE, CYAN, LAVENDER, "ALL PACKAGES", "More on npm",
     ["Also maintaining a multilingual country-code", "picker with search & Reanimated v3 support."],
     [("$ ", "prompt"), ("npm search", "cmd"), (" maintainer:huymobile", "str")], art_packages, "all"),
]


def lib_card(fname, ic, a, b, eye_c, eyebrow, title, desc, code, art, key):
    W, ch, H = 600, 360, 376
    art_svg, art_css = art()
    defs = lin("g", a, b, x2=1, y2=1) + lin("bar", GREEN, CYAN) + glow("r", a, .34)
    body = f"""
{card_frame(12, 0, 576, ch, 22, f'<circle cx="{W - 32}" cy="0" r="340" fill="url(#r)"/>')}
<rect x="48" y="36" width="56" height="56" rx="15" fill="url(#g)"/>
{icon(ic, 62, 50, 28, WHITE, 2.1)}
{art_svg}
{text(48, 140, eyebrow, 14, eye_c, 700, spacing=1.5, maxw=504)}
{stat_row(552, 140, lib_stats(key), 48 + tw(eyebrow, 14, 700, 1.5))}
{text(47, 180, title, 30, WHITE, 700, spacing=-0.3, maxw=504)}
{text(48, 218, desc[0], 19, MUTED, maxw=504)}
{text(48, 246, desc[1], 19, MUTED, maxw=504)}
<rect x="48" y="272" width="504" height="52" rx="12" fill="{DEEP}" stroke="{LINE}"/>
{code_line(68, 304, code, 14.5, maxw=464)}"""
    write(fname, W, H, f"{title} — {' '.join(desc)}", body, defs, art_css)


# ── X call-to-action ─────────────────────────────────────────────────────────
def x_card():
    W, H = 1200, 272
    label = "Follow on X"
    bw = round(32 + 20 + 12 + tw(label, 18, 700) + 14 + 18 + 28)
    bx = 1134 - bw
    body = f"""
{card_frame(18, 0, 1164, 260, 26, '<circle cx="1060" cy="40" r="360" fill="url(#gb)"/><circle cx="760" cy="300" r="300" fill="url(#ga)"/>')}
<circle cx="122" cy="130" r="56" fill="#000000" stroke="#FFFFFF" stroke-opacity=".18" stroke-width="1.5"/>
{brand("x", 100, 108, 44)}
{text(210, 114, "@TrninhHuy1", 40, WHITE, 700, spacing=-0.5)}
{text(212, 153, "React Native deep-dives, library launches and lessons", 19, MUTED, maxw=bx - 236)}
{text(212, 181, "from shipping secure mobile apps to production.", 19, MUTED, maxw=bx - 236)}
<rect x="{bx}" y="102" width="{bw}" height="56" rx="28" fill="#FFFFFF"/>
{brand("x", bx + 32, 120, 20, INK)}
{text(bx + 64, 137, label, 18, INK, 700)}
{icon("arrow-up-right", round(bx + 64 + tw(label, 18, 700) + 14), 121, 18, INK, 2.6)}"""
    write("x-card.svg", W, H, "Follow @TrninhHuy1 on X for React Native deep-dives and library launches.", body,
          glow("ga", MAGENTA, .30) + glow("gb", BLURPLE, .45))


# ── Footer ───────────────────────────────────────────────────────────────────
def footer():
    W, H = 1200, 300
    label = "Say hello on X"
    bw = round(32 + 20 + 12 + tw(label, 18, 700) + 14 + 18 + 28)
    bx = 1134 - bw
    defs = (BLUR + GRID + GRAIN + lin("eb", "#C3BEFF", "#80E9FF")
            + '<clipPath id="card"><rect x="18" width="1164" height="288" rx="28"/></clipPath>'
            # band clip lives in the mesh's translated space (+120px)
            + '<clipPath id="band2"><polygon points="18,168 1182,168 1182,30 18,130"/></clipPath>')
    body = f"""
<g clip-path="url(#card)">
  <rect x="18" width="1164" height="288" fill="{NAVY}"/>
  <g transform="translate(0 120)">{mesh("band2")}</g>
</g>
<rect x="18.5" y=".5" width="1163" height="287" rx="27.5" stroke="#FFFFFF" stroke-opacity=".08"/>
{text(66, 64, "LET'S TALK", 15, "url(#eb)", 800, spacing=2.4)}
{text(64, 118, "Let's build something people trust.", 46, WHITE, 700, spacing=-0.6, maxw=bx - 100)}
{text(66, 158, "Open to senior React Native roles, consulting and open-source collaboration.", 20, MUTED, maxw=1068)}
<rect x="{bx}" y="72" width="{bw}" height="56" rx="28" fill="#FFFFFF"/>
{brand("x", bx + 32, 90, 20, INK)}
{text(bx + 64, 107, label, 18, INK, 700)}
{icon("arrow-up-right", round(bx + 64 + tw(label, 18, 700) + 14), 91, 18, INK, 2.6)}"""
    write("footer.svg", W, H, "Let's build something people trust. Open to senior React Native roles, "
          "consulting and open-source collaboration.", body, defs, MESH_CSS)


# ── Activity (refreshed daily by .github/workflows/activity.yml) ─────────────
LEVELS = ["#FFFFFF", "#3B40B8", "#4B4FE0", "#7C7CFF", CYAN]


def _streaks(days):
    counts = [c for _, c in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today may not have activity yet
        i -= 1
    while i >= 0 and counts[i]:
        current, i = current + 1, i - 1
    return current, longest


def activity():
    src = OUT / "activity.json"
    days = []
    if src.exists():
        cal = json.loads(src.read_text())["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        days = [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
        total = cal["totalContributions"]
    if not days:  # empty state until the first CI run
        end = date.today()
        start = end - timedelta(days=end.weekday() + 1 + 52 * 7)
        days = [((start + timedelta(d)).isoformat(), 0) for d in range((end - start).days + 1)]
        total = None

    current, longest = _streaks(days)
    best_date, best = max(days, key=lambda d: d[1])
    nonzero = sorted(c for _, c in days if c)

    def level(c):
        if not c or not nonzero:
            return 0
        q = [nonzero[int(len(nonzero) * p)] for p in (.25, .5, .75)]
        return 1 + sum(c > t for t in q)

    W, H, L = 1200, 412, 66
    first = date.fromisoformat(days[0][0])
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    weeks = (offset + len(days) + 6) // 7
    gx, gy = 110, 206
    pitch = round((1134 - gx + 4) / weeks, 2)
    cell = round(pitch - 4, 2)

    stats = [
        (f"{total:,}" if total is not None else "—", "", "Contributions in the last year"),
        (str(current), " days" if current != 1 else " day", "Current streak"),
        (str(longest), " days" if longest != 1 else " day", "Longest streak"),
        (str(best) if best else "—", "", f"Best day · {date.fromisoformat(best_date):%b %-d}" if best else "Best day"),
    ]
    stat_svg = ""
    for i, (n, unit, lbl) in enumerate(stats):
        x = L + i * 270
        if i:
            stat_svg += f'<line x1="{x - 30}" y1="68" x2="{x - 30}" y2="136" stroke="{LINE}" stroke-width="1.5"/>'
        stat_svg += (f'<text x="{x}" y="102" font-size="42" font-weight="700" fill="{WHITE}" letter-spacing="-0.4">{escape(n)}'
                     f'<tspan font-size="20" font-weight="600" fill="{MUTED}" letter-spacing="0">{escape(unit)}</tspan></text>'
                     + text(x, 130, lbl, 15, MUTED, 500, maxw=236))

    cells, months, last_month = "", "", None
    for i, (d, c) in enumerate(days):
        col, row = divmod(offset + i, 7)
        x, y = gx + col * pitch, gy + row * pitch
        lv = level(c)
        op = ' fill-opacity=".06"' if lv == 0 else ""
        cells += (f'<rect class="c" x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3.5" fill="{LEVELS[lv]}"{op} '
                  f'style="animation-delay:{col * 18}ms"><title>{c} on {d}</title></rect>')
        m = d[:7]
        if row == 0 or i == 0:
            if m != last_month and col < weeks - 2:
                months += text(round(x, 1), gy - 14, f"{date.fromisoformat(d):%b}", 14, "#8FA3B8", 600)
            last_month = m
    days_lbl = "".join(text(L, gy + r * pitch + cell - 3, n, 14, "#8FA3B8", 600) for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))

    legend_x = 1134 - round(tw("More", 13, 600)) - 10 - 5 * (cell + 4) + 4
    legend = text(legend_x - 10, 372, "Less", 13, SUBTLE, 600, anchor="end")
    for i, c in enumerate(LEVELS):
        op = ' fill-opacity=".06"' if i == 0 else ""
        legend += f'<rect x="{legend_x + i * (cell + 4):.1f}" y="{372 - cell + 2:.1f}" width="{cell}" height="{cell}" rx="3.5" fill="{c}"{op}/>'
    legend += text(1134, 372, "More", 13, SUBTLE, 600, anchor="end")

    stamp = (f"Updated {datetime.now(timezone.utc):%b %-d, %Y} · refreshed daily by GitHub Actions"
             if total is not None else "Syncing with GitHub…")
    body = f"""
{card_frame(18, 0, 1164, 400, 26, f'<circle cx="1182" cy="0" r="420" fill="url(#ga)"/><circle cx="18" cy="400" r="360" fill="url(#gb)"/>')}
{stat_svg}
<line x1="{L}" y1="160" x2="1134" y2="160" stroke="{LINE}"/>
{months}{days_lbl}
<g>{cells}</g>
{text(L, 372, stamp, 13, SUBTLE, 500)}
{legend}"""
    css = ".c{animation:ap .5s ease-out both}@keyframes ap{from{opacity:0}}"
    write("activity.svg", W, H, f"GitHub activity: {stats[0][0]} contributions in the last year, "
          f"current streak {current} days, longest streak {longest} days.", body,
          glow("ga", BLURPLE, .30) + glow("gb", CYAN, .14), css)


if __name__ == "__main__":
    if sys.argv[1:] == ["activity"]:
        activity()
        sys.exit()
    porcelain_hero()
    for args in (("btn-x.svg", "Follow on X", "x", True), ("btn-linkedin.svg", "LinkedIn", "linkedin"),
                 ("btn-npm.svg", "npm packages", "npm")):
        print(args[0], porcelain_button(*args))
    porcelain_header("h-expertise.svg", "01 — EXPERTISE", "Built for the hard parts of mobile.")
    header("h-open-source.svg", "02 — OPEN SOURCE", "Libraries born in production.",
           "Each package started as a real problem in a shipping app. Now it solves yours.")
    header("h-x.svg", "03 — ON X", "Building in public.",
           "Deep-dives, launches and production lessons for the React Native community.")
    header("h-activity.svg", "04 — ACTIVITY", "Shipping, consistently.",
           "A year of contributions, refreshed every day.")
    porcelain_expertise()
    flagship()
    for lib in LIBS:
        lib_card(*lib)
    x_card()
    footer()
    activity()
    print("✓ assets generated in", OUT)
