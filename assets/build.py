#!/usr/bin/env python3
"""Generates every SVG used by the profile README.

    python3 assets/build.py

Artwork is fully self-contained (system fonts, no external images) so GitHub
renders it through its image proxy. Edit the copy/data below, re-run, commit.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent

# ── Design tokens ────────────────────────────────────────────────────────────
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

NAVY, DEEP, LINE = "#0A2540", "#061B31", "#1C3A5E"
WHITE, SOFT, MUTED, SUBTLE = "#FFFFFF", "#E3E8EE", "#ADBDCC", "#6B819B"
INK, INK_MUTED = "#0A2540", "#425466"
BLURPLE, LAVENDER, CYAN, MAGENTA, ORANGE, GREEN = (
    "#635BFF", "#B9B5FF", "#00D4FF", "#F96BEE", "#FFB86C", "#3ECF8E")

CODE = {  # syntax colours on DEEP
    "p": "#C9D6E3", "tag": "#7FD3FF", "attr": LAVENDER, "str": "#FFD58A",
    "num": "#FF9E7A", "kw": "#F98BE3", "fn": "#7FD3FF", "prompt": GREEN,
    "cmd": WHITE, "flag": LAVENDER, "com": "#5E7A99", "key": "#7FD3FF",
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
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "arrow-up": '<line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>',
    "arrow-up-right": '<line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/>',
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


# ── Helpers ──────────────────────────────────────────────────────────────────
def tw(s, size, bold=False, spacing=0.0, mono=False):
    """Rough rendered width of a string, used only for layout of pills/chips."""
    if mono:
        return len(s) * size * 0.6
    w = 0.0
    for c in s:
        if c.isupper() or c in "MW@%":
            w += 0.66
        elif c.isdigit():
            w += 0.58
        elif c in " .,:;'|!il·":
            w += 0.3
        else:
            w += 0.53
    return w * size * (1.06 if bold else 1) + spacing * len(s)


def icon(name, x, y, size=24, color=WHITE, width=2):
    s = size / 24
    return (f'<g transform="translate({x} {y}) scale({s:.4f})" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def brand(name, x, y, size=24, color=WHITE):
    return f'<path transform="translate({x} {y}) scale({size / 24:.4f})" fill="{color}" d="{BRANDS[name]}"/>'


def text(x, y, s, size, fill, weight=400, cls="", anchor="start", spacing=0, extra=""):
    attrs = f'x="{x}" y="{y}" font-size="{size}" font-weight="{weight}"'
    if fill:
        attrs += f' fill="{fill}"'
    if cls:
        attrs += f' class="{cls}"'
    if anchor != "start":
        attrs += f' text-anchor="{anchor}"'
    if spacing:
        attrs += f' letter-spacing="{spacing}"'
    return f"<text {attrs} {extra}>{escape(s)}</text>"


def code_line(x, y, tokens, size=14.5, cls="mono", extra=""):
    spans = "".join(f'<tspan fill="{CODE[k]}">{escape(t)}</tspan>' for t, k in tokens)
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve"{c} {extra}>{spans}</text>'


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


SHADOW = ('<filter id="shadow" x="-40%" y="-80%" width="180%" height="360%">'
          '<feDropShadow dx="0" dy="18" stdDeviation="20" flood-color="#000814" flood-opacity=".45"/></filter>')
BLUR = '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>'
GRID = ('<pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse">'
        '<path d="M36 0H0V36" stroke="#FFFFFF" stroke-opacity=".07"/></pattern>')
MESH_CSS = """
.b1{animation:d1 19s ease-in-out infinite alternate}@keyframes d1{to{transform:translate(110px,50px)}}
.b2{animation:d2 23s ease-in-out infinite alternate}@keyframes d2{to{transform:translate(-90px,60px)}}
.b3{animation:d3 17s ease-in-out infinite alternate}@keyframes d3{to{transform:translate(80px,-50px)}}
.b4{animation:d4 21s ease-in-out infinite alternate}@keyframes d4{to{transform:translate(-100px,-40px)}}
"""


def mesh(clip_id):
    """Stripe-style animated gradient mesh, clipped to `clip_id`."""
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
</g>"""


# ── Hero ─────────────────────────────────────────────────────────────────────
def hero():
    W, H = 1200, 600
    L = 72
    defs = (BLUR + SHADOW + GRID
            + '<clipPath id="card"><rect x="12" y="0" width="1176" height="600" rx="28"/></clipPath>'
            + '<clipPath id="band"><polygon points="12,0 1188,0 1188,300 12,130"/></clipPath>'
            + lin("title", "#C3BEFF", "#80E9FF")
            + lin("cc", BLURPLE, "#8F6BFF", CYAN, x2=1, y2=1)
            + lin("ok", GREEN, CYAN, x2=1, y2=1)
            + lin("shine", "#FFFFFF00", "#FFFFFF66", "#FFFFFF00")
            + glow("pglow", BLURPLE, .55)
            + '<clipPath id="btn"><rect x="854" y="486" width="204" height="50" rx="12"/></clipPath>'
            + '<clipPath id="ccard"><rect x="854" y="170" width="204" height="128" rx="14"/></clipPath>')
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
        x = L + i * 196
        if i:
            stat_svg += f'<line x1="{x - 26}" y1="482" x2="{x - 26}" y2="548" stroke="{LINE}" stroke-width="1.5"/>'
        stat_svg += text(x, 516, n, 36, WHITE, 700, spacing=-0.5)
        stat_svg += text(x, 542, lbl, 12, SUBTLE, 700, spacing=1.4)

    eyebrow = "React Native  ·  iOS  ·  Android"
    pill_w = 52 + tw(eyebrow, 15, True)

    # Phone geometry
    px, py, sx, sy = 820, 36, 830, 46
    rows = ["Certificate pinned", "Face ID verified", "Risk check passed"]
    row_svg = ""
    for i, r in enumerate(rows):
        y = sy + 282 + i * 40
        row_svg += (f'<circle cx="{sx + 34}" cy="{y - 5}" r="10" fill="url(#ok)"/>'
                    + icon("check", sx + 27, y - 12, 14, WHITE, 3)
                    + text(sx + 54, y, r, 14, INK, 500))
        row_svg += f'<line x1="{sx + 24}" y1="{y + 16}" x2="{sx + 228}" y2="{y + 16}" stroke="#E3E8EE"/>'

    body = f"""
<g clip-path="url(#card)">
  <rect x="12" width="1176" height="600" fill="{NAVY}"/>
  <rect x="12" width="1176" height="600" fill="url(#grid)" opacity=".5"/>
  {mesh("band")}
  <ellipse cx="960" cy="560" rx="320" ry="160" fill="url(#pglow)"/>

  <!-- Copy -->
  <rect x="{L}" y="196" width="{pill_w:.0f}" height="38" rx="19" fill="#FFFFFF" fill-opacity=".07" stroke="#FFFFFF" stroke-opacity=".14"/>
  <circle class="pulse" cx="{L + 22}" cy="215" r="5" fill="{GREEN}"/>
  <circle cx="{L + 22}" cy="215" r="5" fill="{GREEN}"/>
  {text(L + 38, 220, eyebrow, 15, SOFT, 600, extra='xml:space="preserve"')}
  {text(L - 3, 306, "Trần Đình Huy", 66, WHITE, 700, spacing=-1.5)}
  {text(L, 354, "Senior React Native Engineer", 30, "url(#title)", 600, spacing=-0.3)}
  {text(L, 402, "I build secure, production-grade mobile apps —", 20, MUTED)}
  {text(L, 431, "and open-source the infrastructure behind them.", 20, MUTED)}
  {stat_svg}

  <!-- Phone -->
  <g class="float">
    <g filter="url(#shadow)">
      <rect x="{px}" y="{py}" width="272" height="548" rx="46" fill="#0B1220" stroke="#2A3B55" stroke-width="1.5"/>
    </g>
    <rect x="{sx}" y="{sy}" width="252" height="528" rx="37" fill="#F6F9FC"/>
    <rect x="{sx + 84}" y="{sy + 12}" width="84" height="26" rx="13" fill="#0B1220"/>
    {text(sx + 28, sy + 31, "9:41", 14, INK, 600)}
    <g fill="{INK}"><rect x="{sx + 186}" y="{sy + 24}" width="3" height="7" rx="1"/><rect x="{sx + 191}" y="{sy + 21}" width="3" height="10" rx="1"/><rect x="{sx + 196}" y="{sy + 18}" width="3" height="13" rx="1"/></g>
    <rect x="{sx + 205}" y="{sy + 19}" width="22" height="11" rx="3" stroke="{INK}" stroke-opacity=".5"/>
    <rect x="{sx + 207}" y="{sy + 21}" width="16" height="7" rx="1.5" fill="{INK}"/>

    {text(sx + 24, sy + 92, "Checkout", 24, INK, 700, spacing=-0.4)}
    {icon("lock", sx + 24, sy + 104, 13, GREEN, 2.5)}
    {text(sx + 42, sy + 115, "Secured connection", 12, "#6B7C93", 500)}

    <g clip-path="url(#ccard)">
      <rect x="854" y="170" width="204" height="128" fill="url(#cc)"/>
      <circle cx="1040" cy="180" r="70" fill="{MAGENTA}" opacity=".45"/>
      <circle cx="880" cy="300" r="60" fill="{CYAN}" opacity=".35"/>
    </g>
    <rect x="872" y="190" width="30" height="22" rx="5" fill="#FFE2A8" fill-opacity=".9"/>
    <path d="M1028 194a10 10 0 0 1 0 16M1034 190a16 16 0 0 1 0 24" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity=".85"/>
    {text(872, 262, "•••• 4242", 16, WHITE, 600, cls="mono", spacing=1)}
    {text(872, 283, "TRAN DINH HUY", 10, WHITE, 600, spacing=1.6, extra='opacity=".85"')}
    <circle cx="1024" cy="278" r="9" fill="#FFFFFF" fill-opacity=".55"/><circle cx="1036" cy="278" r="9" fill="#FFFFFF" fill-opacity=".35"/>

    {row_svg}
    {text(sx + 24, sy + 418, "Total", 13, "#6B7C93", 500)}
    {text(sx + 228, sy + 418, "₫1.250.000", 18, INK, 700, anchor="end")}
    <rect x="854" y="486" width="204" height="50" rx="12" fill="{BLURPLE}"/>
    <g clip-path="url(#btn)"><rect class="shine" x="810" y="486" width="70" height="50" fill="url(#shine)" transform="skewX(-20)"/></g>
    {text(956, 516, "Pay with Face ID", 15, WHITE, 600, anchor="middle")}
    <rect x="{sx + 76}" y="{sy + 512}" width="100" height="5" rx="2.5" fill="{INK}" fill-opacity=".25"/>
  </g>

  <!-- Floating toasts -->
  <g class="float2" filter="url(#shadow)">
    <rect x="566" y="168" width="266" height="68" rx="16" fill="#FFFFFF"/>
    <circle cx="602" cy="202" r="18" fill="url(#ok)"/>
    {icon("arrow-up", 592, 192, 20, WHITE, 2.6)}
    {text(632, 197, "OTA update shipped", 14, INK, 700)}
    {text(632, 217, "Rolled out to 50% · no review", 12, "#6B7C93", 500)}
  </g>
  <g class="float3" filter="url(#shadow)">
    <rect x="978" y="86" width="196" height="68" rx="16" fill="#FFFFFF"/>
    <circle cx="1014" cy="120" r="18" fill="url(#cc)"/>
    {icon("message", 1004, 110, 20, WHITE, 2.4)}
    {text(1044, 115, "OTP auto-filled", 14, INK, 700)}
    {text(1044, 135, "No SMS permission", 12, "#6B7C93", 500)}
  </g>
</g>
<rect x="12.5" y=".5" width="1175" height="599" rx="27.5" stroke="#FFFFFF" stroke-opacity=".08"/>"""
    write("hero.svg", W, H,
          "Trần Đình Huy — Senior React Native Engineer. I build secure, production-grade mobile apps "
          "and open-source the infrastructure behind them.", body, defs, css)


# ── Buttons ──────────────────────────────────────────────────────────────────
def button(name, label, mark, primary=False):
    size, h = 17, 52
    w = round(58 + tw(label, size, True) * 1.12 + (52 if primary else 26))
    fill = "url(#bg)" if primary else NAVY
    stroke = "" if primary else f'stroke="{LINE}" stroke-width="1.5"'
    arrow = icon("arrow-up-right", w - 38, 17, 18, WHITE, 2.4) if primary else ""
    defs = lin("bg", BLURPLE, "#8D7BFF")
    body = (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{(h - 2) / 2}" fill="{fill}" {stroke}/>'
            + brand(mark, 24, 16, 20)
            + text(54, 32, label, size, WHITE, 600) + arrow)
    write(name, w, h, label, body, defs)


# ── Section headers (adapt to light/dark) ────────────────────────────────────
def header(name, eyebrow, title, sub):
    css = (f".h{{fill:{INK}}}.s{{fill:{INK_MUTED}}}"
           f"@media (prefers-color-scheme: dark){{.h{{fill:#F6F9FC}}.s{{fill:{MUTED}}}}}")
    defs = lin("eb", BLURPLE, "#00B8E6")
    body = (text(12, 40, eyebrow, 14, "url(#eb)", 800, spacing=2.4)
            + text(10, 96, title, 42, "", 700, cls="h", spacing=-1.2)
            + text(12, 134, sub, 18, "", 400, cls="s"))
    write(name, 1200, 152, f"{title} {sub}", body, defs, css)


# ── Expertise grid ───────────────────────────────────────────────────────────
EXPERTISE = [
    ("lock", "Mobile security", BLURPLE, CYAN,
     ["SSL pinning, biometric auth and hardened key", "storage that hold up against real MITM attacks."],
     ["SSL Pinning", "Biometrics", "Keychain / Keystore", "Anti-fraud"]),
    ("card", "Payments", MAGENTA, ORANGE,
     ["Production checkout flows on Vietnam's leading", "gateways — built for real money, not demos."],
     ["VNPay", "ZaloPay", "Payoo"]),
    ("zap", "Release engineering", GREEN, CYAN,
     ["Automated pipelines and OTA updates that ship", "fixes in minutes instead of review cycles."],
     ["Fastlane", "Expo Updates", "CodePush", "TestFlight"]),
    ("cpu", "New Architecture", "#7A73FF", MAGENTA,
     ["Native modules on Nitro & TurboModules, 60 fps", "UI with Reanimated, state that scales."],
     ["Nitro", "TurboModules", "Reanimated", "TanStack Query"]),
]


def expertise():
    W, H, tw_, th = 1200, 568, 576, 266
    defs, body = "", ""
    for i, (ic, title, a, b, desc, chips) in enumerate(EXPERTISE):
        x = 12 + (i % 2) * (tw_ + 24)
        y = (i // 2) * (th + 24)
        defs += (lin(f"g{i}", a, b, x2=1, y2=1) + glow(f"r{i}", a, .32)
                 + f'<clipPath id="c{i}"><rect x="{x}" y="{y}" width="{tw_}" height="{th}" rx="22"/></clipPath>')
        body += (f'<g clip-path="url(#c{i})"><rect x="{x}" y="{y}" width="{tw_}" height="{th}" fill="{NAVY}"/>'
                 f'<circle cx="{x + tw_ - 40}" cy="{y + 10}" r="240" fill="url(#r{i})"/></g>'
                 f'<rect x="{x + .75}" y="{y + .75}" width="{tw_ - 1.5}" height="{th - 1.5}" rx="21.5" stroke="{LINE}" stroke-width="1.5"/>'
                 f'<rect x="{x + 36}" y="{y + 36}" width="54" height="54" rx="15" fill="url(#g{i})"/>'
                 + icon(ic, x + 50, y + 50, 26, WHITE, 2.2)
                 + text(x + 36, y + 134, title, 26, WHITE, 700, spacing=-0.5)
                 + text(x + 36, y + 168, desc[0], 17, MUTED)
                 + text(x + 36, y + 193, desc[1], 17, MUTED))
        cx = x + 36
        for c in chips:
            cw = tw(c, 13, True) + 28
            if cx + cw > x + tw_ - 30:
                break
            body += (f'<rect x="{cx:.0f}" y="{y + 214}" width="{cw:.0f}" height="30" rx="15" fill="#FFFFFF" '
                     f'fill-opacity=".06" stroke="#FFFFFF" stroke-opacity=".12"/>'
                     + text(round(cx + 14), y + 234, c, 13, SOFT, 600))
            cx += cw + 8
    write("expertise.svg", W, H,
          "Expertise: mobile security, payments, release engineering and the React Native New Architecture.",
          body, defs)


# ── Library cards ────────────────────────────────────────────────────────────
def flagship():
    W, H = 1200, 452
    L, cx, cy, cw, ch = 60, 612, 44, 536, 352
    defs = (glow("ga", BLURPLE, .40) + glow("gb", CYAN, .22) + lin("ok", GREEN, CYAN, x2=1, y2=1)
            + '<clipPath id="card"><rect x="12" y="0" width="1176" height="440" rx="26"/></clipPath>')
    css = """
.ln{animation:in .6s ease-out both}
@keyframes in{from{opacity:0;transform:translateY(6px)}}
.cur{animation:bl 1.1s steps(1) infinite}@keyframes bl{50%{opacity:0}}
"""
    feats = [("TrustKit + OkHttp", L, 286), ("Expo config plugin", L + 250, 286),
             ("Audit-mode rollout", L, 320), ("Signed OTA pin updates", L + 250, 320)]
    feat_svg = "".join(
        f'<circle cx="{x + 9}" cy="{y - 5}" r="9" fill="url(#ok)"/>' + icon("check", x + 3, y - 11, 12, WHITE, 3)
        + text(x + 28, y, s, 16, SOFT, 500) for s, x, y in feats)

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
    code_svg = "".join(
        code_line(cx + 24, cy + 72 + i * 24, toks, 14.5, cls="mono ln", extra=f'style="animation-delay:{.15 + i * .09:.2f}s"')
        for i, toks in enumerate(code) if toks)
    cmd_pill_w = 44 + tw("npm i react-native-ssl-manager", 15, mono=True)

    body = f"""
<g clip-path="url(#card)">
  <rect x="12" width="1176" height="440" fill="{NAVY}"/>
  <circle cx="60" cy="0" r="460" fill="url(#ga)"/>
  <circle cx="1188" cy="440" r="420" fill="url(#gb)"/>
</g>
<rect x="12.75" y=".75" width="1174.5" height="438.5" rx="25.25" stroke="{LINE}" stroke-width="1.5"/>

<rect x="{L}" y="44" width="{tw('FLAGSHIP · SECURITY', 12, True, 1.6) + 30:.0f}" height="30" rx="15" fill="{BLURPLE}" fill-opacity=".2" stroke="{BLURPLE}" stroke-opacity=".55"/>
{text(L + 15, 64, "FLAGSHIP · SECURITY", 12, LAVENDER, 700, spacing=1.6)}
{text(L - 2, 134, "react-native-ssl-manager", 38, WHITE, 700, spacing=-1)}
{text(L, 176, "Certificate pinning for React Native & Expo. Your", 18, MUTED)}
{text(L, 203, "app refuses every connection that doesn't match —", 18, MUTED)}
{text(L, 230, "even through Charles, Proxyman or a rogue Wi-Fi.", 18, MUTED)}
{feat_svg}
<rect x="{L}" y="356" width="{cmd_pill_w:.0f}" height="42" rx="11" fill="{DEEP}" stroke="{LINE}"/>
{code_line(L + 20, 382, [("$ ", "prompt"), ("npm i react-native-ssl-manager", "cmd")], 15)}
{text(L + cmd_pill_w + 18, 382, "v2 · Nitro Module", 14, SUBTLE, 600)}

<g>
  <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="{DEEP}" stroke="{LINE}"/>
  <circle cx="{cx + 22}" cy="{cy + 20}" r="6" fill="#FF5F57"/><circle cx="{cx + 42}" cy="{cy + 20}" r="6" fill="#FEBC2E"/><circle cx="{cx + 62}" cy="{cy + 20}" r="6" fill="#28C840"/>
  {text(cx + cw / 2, cy + 25, "zsh — my-app", 12, SUBTLE, 600, anchor="middle")}
  <line x1="{cx}" y1="{cy + 40}" x2="{cx + cw}" y2="{cy + 40}" stroke="{LINE}"/>
  {code_svg}
  <rect class="cur" x="{cx + 24 + tw('// pinned at app launch — zero JS changes', 14.5, mono=True) + 4:.0f}" y="{cy + 72 + 11 * 24 - 13}" width="8" height="16" fill="{CYAN}"/>
</g>"""
    write("lib-ssl-manager.svg", W, H,
          "react-native-ssl-manager — certificate pinning for React Native & Expo. TrustKit + OkHttp, "
          "Expo config plugin, audit mode and signed OTA pin updates.", body, defs, css)


LIBS = [
    ("lib-iconify.svg", "grid", MAGENTA, ORANGE, "#FFC1F7", "ICONS · iOS · ANDROID · WEB", "react-native-iconify",
     ["200,000+ icons from 150+ sets, loaded by name.", "Native caching via SDWebImage & Glide."],
     [("<", "p"), ("IconifyIcon", "tag"), (" name", "attr"), ("=", "p"), ('"mdi:rocket-launch"', "str"),
      (" size", "attr"), ("={", "p"), ("32", "num"), ("} />", "p")]),
    ("lib-sms-retriever.svg", "message", GREEN, CYAN, "#9FF0CB", "OTP · ANDROID · NITRO", "sms-retriever-nitro-module",
     ["One-tap OTP autofill on Android with zero SMS", "permissions. Nitro + TurboModules, Expo-ready."],
     [("const", "kw"), (" { smsCode } = ", "p"), ("useSMSRetriever", "fn"), ("({ onSuccess })", "p")]),
    ("lib-ota-updates.svg", "cloud", GREEN, BLURPLE, "#9FF0CB", "OTA · EXPO · SUPABASE", "supabase-expo-ota-updates",
     ["Self-hosted OTA updates for Expo on Supabase.", "Staged rollouts and auto-rollback on crash."],
     [("$ ", "prompt"), ("npx supabase-expo-ota-updates publish", "cmd"), (" --rollout", "flag"), (" 50", "num")]),
    ("lib-more.svg", "package", BLURPLE, CYAN, LAVENDER, "ALL PACKAGES", "More on npm",
     ["Also maintaining a multilingual country-code", "picker with search & Reanimated v3 support."],
     [("$ ", "prompt"), ("npm search", "cmd"), (" maintainer:huymobile", "str")]),
]


def lib_card(fname, ic, a, b, eye_c, eyebrow, title, desc, code):
    W, H, ch = 600, 356, 340
    defs = (lin("g", a, b, x2=1, y2=1) + glow("r", a, .34)
            + f'<clipPath id="card"><rect width="{W}" height="{ch}" rx="22"/></clipPath>')
    body = f"""
<g clip-path="url(#card)">
  <rect width="{W}" height="{ch}" fill="{NAVY}"/>
  <circle cx="{W - 20}" cy="0" r="330" fill="url(#r)"/>
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{ch - 1.5}" rx="21.25" stroke="{LINE}" stroke-width="1.5"/>
<rect x="36" y="36" width="56" height="56" rx="15" fill="url(#g)"/>
{icon(ic, 50, 50, 28, WHITE, 2.1)}
<circle cx="546" cy="64" r="20" stroke="#FFFFFF" stroke-opacity=".22" stroke-width="1.5"/>
{icon("arrow-up-right", 537, 55, 18, MUTED, 2.2)}
{text(36, 134, eyebrow, 12, eye_c, 700, spacing=1.6)}
{text(35, 172, title, 28, WHITE, 700, spacing=-0.6)}
{text(36, 208, desc[0], 17, MUTED)}
{text(36, 234, desc[1], 17, MUTED)}
<rect x="36" y="262" width="528" height="50" rx="11" fill="{DEEP}" stroke="{LINE}"/>
{code_line(56, 292, code, 14)}"""
    write(fname, W, H, f"{title} — {' '.join(desc)}", body, defs)


# ── X call-to-action ─────────────────────────────────────────────────────────
def x_card():
    W, H = 1200, 272
    defs = (glow("ga", MAGENTA, .30) + glow("gb", BLURPLE, .45)
            + '<clipPath id="card"><rect x="12" width="1176" height="260" rx="26"/></clipPath>')
    body = f"""
<g clip-path="url(#card)">
  <rect x="12" width="1176" height="260" fill="{NAVY}"/>
  <circle cx="1060" cy="40" r="360" fill="url(#gb)"/>
  <circle cx="760" cy="300" r="300" fill="url(#ga)"/>
</g>
<rect x="12.75" y=".75" width="1174.5" height="258.5" rx="25.25" stroke="{LINE}" stroke-width="1.5"/>
<circle cx="116" cy="130" r="56" fill="#000000" stroke="#FFFFFF" stroke-opacity=".18" stroke-width="1.5"/>
{brand("x", 94, 108, 44)}
{text(204, 112, "@TrninhHuy1", 38, WHITE, 700, spacing=-1)}
{text(206, 150, "React Native deep-dives, library launches and lessons", 18, MUTED)}
{text(206, 177, "from shipping secure mobile apps to production.", 18, MUTED)}
<rect x="902" y="102" width="236" height="56" rx="28" fill="#FFFFFF"/>
{brand("x", 934, 120, 20, INK)}
{text(966, 137, "Follow on X", 18, INK, 700)}
{icon("arrow-up-right", 1096, 121, 18, INK, 2.6)}"""
    write("x-card.svg", W, H, "Follow @TrninhHuy1 on X for React Native deep-dives and library launches.", body, defs)


# ── Footer ───────────────────────────────────────────────────────────────────
def footer():
    W, H = 1200, 300
    defs = (BLUR + GRID + lin("eb", "#C3BEFF", "#80E9FF")
            + '<clipPath id="card"><rect x="12" width="1176" height="288" rx="28"/></clipPath>')
    body = f"""
<g clip-path="url(#card)">
  <rect x="12" width="1176" height="288" fill="{NAVY}"/>
  <g transform="translate(0 120)">{mesh("band2")}</g>
</g>
<rect x="12.5" y=".5" width="1175" height="287" rx="27.5" stroke="#FFFFFF" stroke-opacity=".08"/>
{text(60, 66, "LET'S TALK", 14, "url(#eb)", 800, spacing=2.4)}
{text(58, 118, "Let's build something people trust.", 42, WHITE, 700, spacing=-1.2)}
{text(60, 156, "Open to senior React Native roles, consulting and open-source collaboration.", 18, MUTED)}"""
    # the band clip is defined in un-translated space; translate it back
    defs += '<clipPath id="band2"><polygon points="12,168 1188,168 1188,30 12,130"/></clipPath>'
    write("footer.svg", W, H, "Let's build something people trust. Open to senior React Native roles, "
          "consulting and open-source collaboration.", body, defs, MESH_CSS)


if __name__ == "__main__":
    hero()
    button("btn-x.svg", "Follow on X", "x", primary=True)
    button("btn-linkedin.svg", "LinkedIn", "linkedin")
    button("btn-npm.svg", "npm packages", "npm")
    header("h-expertise.svg", "01 — EXPERTISE", "Built for the hard parts of mobile.",
           "Security, payments and delivery — where a bug costs money, not just a crash report.")
    header("h-open-source.svg", "02 — OPEN SOURCE", "Libraries born in production.",
           "Each package started as a real problem in a shipping app. Now it solves yours.")
    header("h-x.svg", "03 — ON X", "Building in public.",
           "Deep-dives, launches and production lessons for the React Native community.")
    header("h-activity.svg", "04 — ACTIVITY", "Shipping, consistently.",
           "Live contribution streak and the last month on GitHub.")
    expertise()
    flagship()
    for lib in LIBS:
        lib_card(*lib)
    x_card()
    footer()
    print("✓ assets generated in", OUT)
