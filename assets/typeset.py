"""Text → SVG outlines, shaped with HarfBuzz from the vendored OFL fonts in ./fonts.

Outlining makes every card render identically on macOS, Windows, Linux and the
GitHub mobile app, whatever fonts the viewer has installed. Each glyph outline is
emitted once into <defs> and placed with <use>, so repeated letters cost a few bytes.
"""
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen

FONTS = Path(__file__).parent / "fonts"
FAMILIES = {"sans": "Inter[opsz,wght].ttf", "mono": "GeistMono[wght].ttf"}
_blobs, _fonts = {}, {}


def _font(family, weight, opsz):
    key = (family, weight, opsz)
    if key not in _fonts:
        if family not in _blobs:
            _blobs[family] = hb.Face(hb.Blob.from_file_path(str(FONTS / FAMILIES[family])))
        f = hb.Font(_blobs[family])
        axes = {"wght": weight}
        if family == "sans":
            axes["opsz"] = opsz
        f.set_variations(axes)
        _fonts[key] = f
    return _fonts[key]


def _opsz(size, family):
    # Inter's optical size axis runs 14–32: text cut below ~20px, display cut above.
    return max(14, min(32, size * 0.69)) if family == "sans" else None


def _shape(s, size, weight, family, tracking, tnum=False):
    font = _font(family, weight, _opsz(size, family))
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True, "calt": True, "tnum": tnum})
    upem = font.face.upem
    k = size / upem
    out, pen_x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((info.codepoint, pen_x + pos.x_offset * k, pos.y_offset * k))
        pen_x += pos.x_advance * k + tracking * size
    width = pen_x - (tracking * size if out else 0)
    return font, out, width, k


def width(s, size, weight=400, family="sans", tracking=0.0, tnum=False):
    """Rendered advance width in px; tracking is in em."""
    return _shape(s, size, weight, family, tracking, tnum)[2]


class Glyphs:
    """Collects glyph outlines for one SVG and renders text runs as <use> placements."""

    def __init__(self, prefix="g"):
        self.prefix, self.defs, self.ids = prefix, [], {}

    def _glyph(self, font, family, weight, gid):
        key = (family, weight, _opsz_key(font), gid)
        if key not in self.ids:
            pen = SVGPathPen(None, ntos=lambda v: f"{v:.0f}")
            font.draw_glyph_with_pen(gid, pen)
            d = pen.getCommands()
            gid_s = f"{self.prefix}{len(self.ids)}"
            self.ids[key] = gid_s if d else None
            if d:
                self.defs.append(f'<path id="{gid_s}" d="{d}"/>')
        return self.ids[key]

    def text(self, x, y, s, size, fill, weight=400, family="sans", tracking=0.0,
             anchor="start", maxw=None, extra="", tnum=False):
        font, glyphs, w, k = _shape(s, size, weight, family, tracking, tnum)
        if maxw is not None and w > maxw + 0.5:
            raise SystemExit(f"✗ text overflow ({w:.0f}px > {maxw:.0f}px): {s!r}")
        x0 = x - (w if anchor == "end" else w / 2 if anchor == "middle" else 0)
        uses = []
        for gid, gx, gy in glyphs:
            ref = self._glyph(font, family, weight, gid)
            if ref:
                uses.append(f'<use href="#{ref}" transform="translate({x0 + gx:.2f} {y - gy:.2f}) scale({k:.5f} -{k:.5f})"/>')
        paint = f'fill="{fill}" ' if fill else ""
        return f'<g {paint}{extra}>{"".join(uses)}</g>'

    def svg_defs(self):
        return "".join(self.defs)


def _opsz_key(font):
    return tuple(round(v, 2) for v in font.get_var_coords_design())
