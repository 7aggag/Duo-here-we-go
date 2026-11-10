"""Generates docs/assets/banner-{dark,light}.svg for the Duo Here We Go README."""
import sys
from pathlib import Path

PALETTES = {
    "dark": dict(bg="#0d1210", grid="#16201b", ink="#eef3ef", muted="#9aaba2", pill_bg="#14201a", pill_line="#24382d",
                 screen="#f6f8f6", card="#e6ece8", line="#c9d4ce", bar="#e3eae6", frame="#26332c", label="#cfdad3",
                 accent="#2fbf71", accent2="#f2b134", hinge="#f2b134", side="#dfe8e3", sel="#2fbf71"),
    "light": dict(bg="#f6f4ee", grid="#ebe7dc", ink="#14201a", muted="#5d6b63", pill_bg="#ffffff", pill_line="#dcd6c6",
                  screen="#ffffff", card="#eef2ef", line="#d3dcd6", bar="#eef2ef", frame="#1d2a23", label="#2b3a32",
                  accent="#1f9d5a", accent2="#c98a0c", hinge="#d99a12", side="#f1f5f2", sel="#1f9d5a"),
}

FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Helvetica, Arial, sans-serif"
AR_FONT = "'SF Arabic', 'Geeza Pro', 'Noto Sans Arabic', 'Segoe UI', Tahoma, sans-serif"


def rows(x, y, w, n, p, rtl=False, gap=34, h=26):
    out = []
    for i in range(n):
        yy = y + i * gap
        out.append(f'<rect x="{x}" y="{yy}" width="{w}" height="{h}" rx="7" fill="{p["card"]}"/>')
        dot_x = x + w - 20 if rtl else x + 8
        out.append(f'<rect x="{dot_x}" y="{yy + 6}" width="12" height="14" rx="4" fill="{p["line"]}"/>')
        bar_w = w * 0.55
        bx = x + w - 28 - bar_w if rtl else x + 28
        out.append(f'<rect x="{bx}" y="{yy + 8}" width="{bar_w}" height="5" rx="2.5" fill="{p["line"]}"/>')
        bx2 = x + w - 28 - bar_w * 0.6 if rtl else x + 28
        out.append(f'<rect x="{bx2}" y="{yy + 16}" width="{bar_w * 0.6}" height="4" rx="2" fill="{p["line"]}"/>')
    return "".join(out)


def vertical_bar(x, y, h, p, camera=True):
    """The iPhone Duo vertical bar column: status items on top, toolbar items below."""
    parts = [f'<rect x="{x}" y="{y}" width="30" height="{h}" fill="{p["bar"]}"/>']
    if camera:
        parts.append(f'<circle cx="{x + 15}" cy="{y + 14}" r="5" fill="{p["frame"]}"/>')
    parts.append(f'<rect x="{x + 7}" y="{y + 28}" width="16" height="4" rx="2" fill="{p["line"]}"/>')
    pill_y = y + h - 108
    parts.append(f'<rect x="{x + 4}" y="{pill_y}" width="22" height="92" rx="11" fill="{p["screen"]}" stroke="{p["line"]}"/>')
    for i in range(4):
        fill = p["accent"] if i == 0 else p["line"]
        parts.append(f'<rect x="{x + 10}" y="{pill_y + 10 + i * 20}" width="10" height="10" rx="3" fill="{fill}"/>')
    return "".join(parts)


def closed_duo(x, y, p):
    w, h = 190, 276
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{p["frame"]}"/>',
         f'<rect x="{x + 7}" y="{y + 7}" width="{w - 14}" height="{h - 14}" rx="16" fill="{p["screen"]}"/>']
    sx, sy, sw, sh = x + 7, y + 7, w - 14, h - 14
    s.append(f'<rect x="{sx + 12}" y="{sy + 16}" width="62" height="8" rx="4" fill="{p["frame"]}"/>')
    s.append(rows(sx + 10, sy + 36, sw - 30 - 20, 6, p))
    s.append(vertical_bar(sx + sw - 30, sy, sh, p))
    return "".join(s)


def half_open_duo(x, y, p, rtl):
    w, h = 400, 280
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{p["frame"]}"/>',
         f'<rect x="{x + 7}" y="{y + 7}" width="{w - 14}" height="{h - 14}" rx="16" fill="{p["screen"]}"/>']
    sx, sy, sw, sh = x + 7, y + 7, w - 14, h - 14
    bar_x = sx + sw - 30
    # The hinge splits the whole display, so the half that holds the bar is narrower (measured: 455 vs 371 pt).
    hinge_x = sx + sw / 2
    wide, narrow = sw / 2, sw / 2 - 30
    sidebar_x, side_w = (hinge_x, narrow) if rtl else (sx, wide)
    detail_x, half = (sx, wide) if rtl else (hinge_x, narrow)
    s.append(f'<rect x="{sidebar_x}" y="{sy}" width="{side_w}" height="{sh}" fill="{p["side"]}"/>')
    s.append(f'<rect x="{sidebar_x + (side_w - 70 if rtl else 12)}" y="{sy + 16}" width="58" height="8" rx="4" fill="{p["frame"]}"/>')
    s.append(rows(sidebar_x + 10, sy + 36, side_w - 20, 5, p, rtl=rtl))
    s.append(f'<rect x="{sidebar_x + 10}" y="{sy + 36 + 34}" width="{side_w - 20}" height="26" rx="7" fill="none" '
             f'stroke="{p["sel"]}" stroke-width="2"/>')
    s.append(f'<rect x="{detail_x + 14}" y="{sy + 16}" width="{half - 28}" height="82" rx="10" fill="url(#hero)"/>')
    tx = detail_x + half - 14 - 90 if rtl else detail_x + 14
    s.append(f'<rect x="{tx}" y="{sy + 112}" width="90" height="9" rx="4.5" fill="{p["frame"]}"/>')
    for i, frac in enumerate((0.8, 0.62, 0.7)):
        lw = (half - 28) * frac
        lx = detail_x + half - 14 - lw if rtl else detail_x + 14
        s.append(f'<rect x="{lx}" y="{sy + 132 + i * 14}" width="{lw}" height="5" rx="2.5" fill="{p["line"]}"/>')
    bx = detail_x + half - 14 - 96 if rtl else detail_x + 14
    s.append(f'<rect x="{bx}" y="{sy + sh - 44}" width="96" height="24" rx="12" fill="{p["frame"]}"/>')
    s.append(f'<rect x="{hinge_x - 10}" y="{sy}" width="20" height="{sh}" fill="{p["hinge"]}" opacity="0.10"/>')
    s.append(f'<line x1="{hinge_x}" y1="{sy + 4}" x2="{hinge_x}" y2="{sy + sh - 4}" stroke="{p["hinge"]}" '
             f'stroke-width="2" stroke-dasharray="5 5"/>')
    s.append(vertical_bar(bar_x, sy, sh, p))
    return "".join(s)


def svg(p):
    W, H = 1280, 640
    grid = "".join(f'<path d="M{x} 0V{H}" stroke="{p["grid"]}"/>' for x in range(0, W, 40))
    grid += "".join(f'<path d="M0 {y}H{W}" stroke="{p["grid"]}"/>' for y in range(0, H, 40))
    devices_y = 290
    c_x, o1_x, o2_x = 110, 360, 810
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Duo Here We Go</title>
<desc id="d">Ready your iOS app for iPhone Duo, in English and Arabic. Three iPhone Duo drawings: closed, half-open in English, and half-open in Arabic where the sidebar moves beside the vertical bar while the bar stays on the right.</desc>
<defs>
<linearGradient id="title" x1="0" x2="1"><stop offset="0" stop-color="{p["accent"]}"/><stop offset="1" stop-color="{p["accent2"]}"/></linearGradient>
<linearGradient id="hero" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["accent"]}"/><stop offset="1" stop-color="{p["accent2"]}"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" fill="{p["bg"]}"/>
<g opacity="0.6">{grid}</g>
<g font-family="{FONT}" text-anchor="middle">
<rect x="{W / 2 - 170}" y="34" width="340" height="34" rx="17" fill="{p["pill_bg"]}" stroke="{p["pill_line"]}"/>
<circle cx="{W / 2 - 146}" cy="51" r="5" fill="{p["accent"]}"/>
<text x="{W / 2 + 8}" y="56" font-size="16" fill="{p["muted"]}">Agent skill · SwiftUI &amp; UIKit · iPhone Duo</text>
<text x="{W / 2}" y="140" font-size="76" font-weight="800" letter-spacing="-1.5" fill="url(#title)">Duo Here We Go</text>
<text x="{W / 2}" y="194" font-size="30" font-weight="700" fill="{p["ink"]}">Ready your iOS app for iPhone Duo, in English <tspan fill="{p["accent2"]}">and</tspan> <tspan font-family="{AR_FONT}" fill="{p["accent2"]}">العربية</tspan>.</text>
<text x="{W / 2}" y="232" font-size="19" fill="{p["muted"]}">Apple's resizability skill first, then the vertical bar, the hinge and right-to-left, with one before/after report.</text>
</g>
{closed_duo(c_x, devices_y - 4, p)}
{half_open_duo(o1_x, devices_y, p, rtl=False)}
{half_open_duo(o2_x, devices_y, p, rtl=True)}
<g font-family="{FONT}" font-size="17" text-anchor="middle" fill="{p["label"]}">
<text x="{c_x + 95}" y="604"><tspan font-weight="700">Closed</tspan> · vertical bar</text>
<text x="{o1_x + 200}" y="604"><tspan font-weight="700">Half-open · English</tspan> · columns meet the hinge</text>
<text x="{o2_x + 200}" y="604"><tspan font-weight="700">Half-open · <tspan font-family="{AR_FONT}">العربية</tspan></tspan> · the bar stays right</text>
</g>
</svg>
"""


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, palette in PALETTES.items():
        (out / f"banner-{name}.svg").write_text(svg(palette), encoding="utf-8")
        print(out / f"banner-{name}.svg")
