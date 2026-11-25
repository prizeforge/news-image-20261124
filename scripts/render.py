#!/usr/bin/env python3
"""Render the 24 November 2026 front page, v4 — 36 stories (1024x1024) with Pillow.

Leader-format front page expanded from 4 to 36 verified stories:
- Kicker, giant serif date masthead, one-line sub-deck
- 7 region chips (36 stories total) + day-order timeline + IN NUMBERS strip
- 4 prominent original leads (HUANG lead + chart; COP31, KYIV, SERANG cards)
- 10 small illustrated stories with custom vector pictograms (#5-#14)
- Numbered ALSO ON two-column list (#15-#36)
- Dotted world map with 14 numbered pins + HOW SURE + DATE CHECK + footer

Deterministic: fixed palette, fixed fonts, fixed geometry, no timestamps.
Run:  python3 scripts/render.py   -> writes assets/entry.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "entry.png")

W, H = 1024, 1024
PAPER = (247, 243, 234)      # cream paper background
BAND_BG = (239, 233, 220)    # warm tinted band for pictograms
CARD_ALT = (252, 249, 243)   # subtle warm highlight
INK = (20, 29, 52)           # deep navy ink
BODY_INK = (34, 43, 64)      # high-contrast dark navy body copy
RED = (188, 46, 36)          # brick red (dateline, kickers, hazards)
GREEN = (22, 118, 62)        # market green (strictly stock chart + confirmed)
GREEN_FILL = (230, 244, 235) # flat market-green tint inside chart only
BLUE = (31, 78, 121)         # Europe / official chip
TEAL = (31, 107, 74)         # Asia chip
AMBER = (166, 98, 22)        # Middle East chip
PLUM = (108, 49, 98)         # Africa chip
OCEAN = (42, 112, 134)       # Oceania chip
OCHRE = (138, 92, 42)        # South America chip
GREY = (92, 102, 118)        # smoke & secondary labels
SMOKE_LIGHT = (146, 154, 166)
LIGHT = (255, 255, 255)      # crisp panel white
GRID = (206, 200, 186)       # rules & chart grid

FONT_DIR = "/usr/share/fonts/truetype/noto"
_FONT_CACHE = {}


def font(name, size):
    key = (name, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _FONT_CACHE[key]


def font_or(name, fallback, size):
    key = (name, fallback, size)
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
        except OSError:
            _FONT_CACHE[key] = ImageFont.truetype(os.path.join(FONT_DIR, fallback), size)
    return _FONT_CACHE[key]


F_BLACK = lambda s: font("NotoSansDisplay-Black.ttf", s)
F_COND_BLACK = lambda s: font("NotoSansDisplay-CondensedBlack.ttf", s)
F_COND_BOLD = lambda s: font("NotoSansDisplay-CondensedBold.ttf", s)
F_COND_MED = lambda s: font("NotoSansDisplay-CondensedMedium.ttf", s)
F_BOLD = lambda s: font("NotoSansDisplay-Bold.ttf", s)
F_MED = lambda s: font("NotoSans-Medium.ttf", s)
F_REG = lambda s: font("NotoSans-Regular.ttf", s)
F_SEMI = lambda s: font("NotoSans-SemiBold.ttf", s)
F_ITALIC = lambda s: font("NotoSans-Italic.ttf", s)
F_SERIF_BLACK = lambda s: font_or("NotoSerifDisplay-Black.ttf",
                                  "NotoSansDisplay-Black.ttf", s)

BADGE_COLORS = {
    "CONFIRMED": GREEN,
    "OFFICIAL": BLUE,
    "REPORTED": RED,
}


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap, returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, text, fnt, fill, max_w, leading, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError(f"Text overflow ({len(lines)} > {max_lines}): {text!r}")
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_centered_text(draw, cx, cy, text, fnt, fill):
    """Draw text visually centered at (cx, cy) using exact glyph bbox."""
    bb = draw.textbbox((0, 0), text, font=fnt)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    draw.text((cx - tw / 2 - bb[0], cy - th / 2 - bb[1]), text, font=fnt, fill=fill)


def rule(draw, x0, y, x1, wdt, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=wdt)


def draw_dashed_line(draw, x0, y, x1, fill, dash=6, gap=4, width=2):
    x = x0
    while x < x1:
        draw.line([(x, y), (min(x + dash, x1), y)], fill=fill, width=width)
        x += dash + gap


def badge(draw, x, y, text, fill, fg=LIGHT, fnt=None, h=16, pad=10):
    """Small filled pill badge; returns width used."""
    fnt = fnt or F_BOLD(10)
    tw = draw.textlength(text, font=fnt)
    w = tw + pad
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill)
    draw_centered_text(draw, x + w / 2, y + h / 2, text, fnt, fg)
    return w


def badge_outline(draw, x, y, text, color, fnt=None, h=14, pad=8):
    """Small outline pill badge; returns width used."""
    fnt = fnt or F_BOLD(9)
    tw = draw.textlength(text, font=fnt)
    w = tw + pad
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2,
                           outline=color, width=1)
    draw_centered_text(draw, x + w / 2, y + h / 2, text, fnt, color)
    return w


def pin_num(d, cx, cy, num, r=7):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=LIGHT, width=1)
    draw_centered_text(d, cx, cy, str(num), F_BOLD(9), LIGHT)


# ---------------------------------------------------------------- big lead card pictograms
# Compact band height for the three big cards (#2, #3, #4): 52px inside 166px wide card.

def draw_globe_band(d, x0, y0, pw, bh):
    """Cracked globe pictogram + NO DEAL stamp."""
    cx = x0 + 38
    cy = y0 + bh // 2
    r = 21
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LIGHT, outline=INK, width=2)
    d.ellipse([cx - 10, cy - r, cx + 10, cy + r], outline=INK, width=2)
    d.line([(cx, cy - r), (cx, cy + r)], fill=INK, width=1)
    d.line([(cx - r, cy), (cx + r, cy)], fill=INK, width=2)
    d.arc([cx - r + 2, cy - r + 4, cx + r - 2, cy - 2], 185, 355, fill=INK, width=1)
    d.arc([cx - r + 2, cy + 2, cx + r - 2, cy + r - 4], 5, 175, fill=INK, width=1)

    crack = [
        (cx - 12, cy - 18),
        (cx - 3, cy - 6),
        (cx - 8, cy + 1),
        (cx + 3, cy + 6),
        (cx - 2, cy + 14),
        (cx + 8, cy + 19),
    ]
    d.line(crack, fill=RED, width=3, joint="curve")
    d.line([(cx - 3, cy - 6), (cx + 8, cy - 10)], fill=RED, width=2)

    bx0, by0, bx1, by1 = x0 + 68, y0 + 8, x0 + pw - 22, y0 + bh - 8
    d.rectangle([bx0, by0, bx1, by1], fill=LIGHT, outline=RED, width=2)
    cx_box = (bx0 + bx1) / 2
    cy_mid = (by0 + by1) / 2
    f_no = F_COND_BLACK(17)
    draw_centered_text(d, cx_box, cy_mid - 8, "NO", f_no, RED)
    draw_centered_text(d, cx_box, cy_mid + 8, "DEAL", f_no, RED)
    pin_num(d, x0 + pw - 11, y0 + 11, 2)


def draw_kyiv_band(d, x0, y0, pw, bh):
    """Damaged five-storey apartment block with smoke + 14 MISSING."""
    base_y = y0 + bh - 4
    bx0 = x0 + 10
    d.ellipse([bx0 + 34, y0 + 4, bx0 + 52, y0 + 18], fill=SMOKE_LIGHT)
    d.ellipse([bx0 + 44, y0 + 3, bx0 + 64, y0 + 19], fill=GREY)
    d.ellipse([bx0 + 56, y0 + 6, bx0 + 74, y0 + 21], fill=SMOKE_LIGHT)

    d.rectangle([bx0, y0 + 13, bx0 + 28, base_y], fill=INK)
    d.polygon([
        (bx0 + 28, y0 + 13),
        (bx0 + 36, y0 + 13),
        (bx0 + 42, y0 + 21),
        (bx0 + 49, y0 + 18),
        (bx0 + 54, y0 + 29),
        (bx0 + 64, y0 + 27),
        (bx0 + 64, base_y),
        (bx0 + 28, base_y),
    ], fill=INK)
    d.polygon([
        (bx0 + 64, base_y - 10),
        (bx0 + 72, base_y - 6),
        (bx0 + 78, base_y),
        (bx0 + 64, base_y),
    ], fill=INK)

    for row in range(4):
        wy = y0 + 17 + row * 8
        for wx in (bx0 + 4, bx0 + 13, bx0 + 21):
            d.rectangle([wx, wy, wx + 4, wy + 5], fill=PAPER)
        if row >= 1:
            d.rectangle([bx0 + 31, wy, bx0 + 35, wy + 5], fill=PAPER)
        if row >= 2:
            d.rectangle([bx0 + 40, wy, bx0 + 44, wy + 5], fill=PAPER)
    d.line([(bx0 + 41, y0 + 19), (bx0 + 49, y0 + 16), (bx0 + 55, y0 + 25)],
           fill=RED, width=2)
    d.line([(bx0 - 2, base_y), (bx0 + 80, base_y)], fill=INK, width=2)

    ax_center = x0 + 122
    draw_centered_text(d, ax_center, y0 + 19, "14", F_COND_BLACK(34), INK)
    draw_centered_text(d, ax_center, y0 + 41, "MISSING", F_COND_BLACK(11), RED)
    pin_num(d, x0 + pw - 11, y0 + 11, 3)


def draw_factory_band(d, x0, y0, pw, bh):
    """Burning factory with flame & smoke + 24 DEAD."""
    base_y = y0 + bh - 4
    fx0 = x0 + 10
    d.ellipse([fx0 + 8, y0 + 4, fx0 + 26, y0 + 17], fill=SMOKE_LIGHT)
    d.ellipse([fx0 + 21, y0 + 4, fx0 + 41, y0 + 18], fill=GREY)
    d.ellipse([fx0 + 35, y0 + 6, fx0 + 53, y0 + 20], fill=SMOKE_LIGHT)

    d.rectangle([fx0 + 3, y0 + 12, fx0 + 11, y0 + 32], fill=INK)
    d.rectangle([fx0, y0 + 32, fx0 + 76, base_y], fill=INK)
    d.polygon([
        (fx0, y0 + 32), (fx0 + 19, y0 + 19), (fx0 + 19, y0 + 32),
        (fx0 + 38, y0 + 19), (fx0 + 38, y0 + 32), (fx0 + 57, y0 + 19),
        (fx0 + 76, y0 + 32),
    ], fill=INK)
    d.polygon([
        (fx0 + 31, y0 + 33), (fx0 + 29, y0 + 18), (fx0 + 39, y0 + 23),
        (fx0 + 47, y0 + 7), (fx0 + 54, y0 + 20), (fx0 + 62, y0 + 10),
        (fx0 + 68, y0 + 33),
    ], fill=RED)
    d.polygon([
        (fx0 + 41, y0 + 32), (fx0 + 47, y0 + 17), (fx0 + 53, y0 + 26),
        (fx0 + 58, y0 + 19), (fx0 + 61, y0 + 32),
    ], fill=PAPER)
    for wx in (fx0 + 7, fx0 + 22, fx0 + 37, fx0 + 52):
        d.rectangle([wx, y0 + 37, wx + 8, y0 + 44], fill=PAPER)
    d.line([(fx0 - 2, base_y), (fx0 + 78, base_y)], fill=INK, width=2)

    ax_center = x0 + 122
    draw_centered_text(d, ax_center, y0 + 19, "24", F_COND_BLACK(34), RED)
    draw_centered_text(d, ax_center, y0 + 41, "DEAD", F_COND_BLACK(11), INK)
    pin_num(d, x0 + pw - 11, y0 + 11, 4)


# ---------------------------------------------------------------- 10 small pictograms (44x32 box)

def draw_mini_pic(d, kind, x, y, w=44, h=32):
    """Draw a crisp flat-editorial mini pictogram inside (x, y, x+w, y+h).
    Top-left 14x14 corner is kept clear for the numbered red pin.
    """
    d.rectangle([x, y, x + w, y + h], fill=BAND_BG, outline=INK, width=1)
    cx, cy = x + w // 2, y + h // 2

    if kind == "hormuz":
        # Tanker hull + naval mine with spikes (shifted right/down of pin)
        d.line([(x + 3, y + 26), (x + w - 3, y + 26)], fill=BLUE, width=2)
        d.polygon([(x + 9, y + 18), (x + 31, y + 18), (x + 28, y + 25), (x + 11, y + 25)], fill=INK)
        d.rectangle([x + 14, y + 13, x + 20, y + 18], fill=INK)
        mx, my = x + 36, y + 15
        d.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=RED)
        for dx, dy in [(-6, 0), (6, 0), (0, -6), (0, 6), (-4, -4), (4, -4), (-4, 4), (4, 4)]:
            d.line([(mx, my), (mx + dx, my + dy)], fill=RED, width=1)

    elif kind == "libya":
        # Tilted sinking warship + red blast
        d.line([(x + 3, y + 26), (x + w - 3, y + 26)], fill=BLUE, width=2)
        d.polygon([(x + 9, y + 22), (x + 35, y + 15), (x + 37, y + 21), (x + 13, y + 25)], fill=INK)
        d.polygon([(x + 19, y + 19), (x + 27, y + 17), (x + 26, y + 12), (x + 18, y + 14)], fill=INK)
        d.polygon([(x + 30, y + 7), (x + 34, y + 13), (x + 40, y + 10), (x + 36, y + 16), (x + 29, y + 15)], fill=RED)

    elif kind == "shenzhou":
        # Rocket lifting off + red exhaust (centered right of pin)
        rx = x + 26
        d.polygon([(rx, y + 3), (rx - 5, y + 12), (rx - 5, y + 22), (rx + 5, y + 22), (rx + 5, y + 12)], fill=INK)
        d.polygon([(rx - 5, y + 17), (rx - 9, y + 23), (rx - 5, y + 22)], fill=INK)
        d.polygon([(rx + 5, y + 17), (rx + 9, y + 23), (rx + 5, y + 22)], fill=INK)
        d.ellipse([rx - 2, y + 10, rx + 2, y + 14], fill=PAPER)
        d.polygon([(rx - 4, y + 22), (rx, y + 30), (rx + 4, y + 22)], fill=RED)

    elif kind == "fifa":
        # World Cup trophy + soccer ball (shifted right of pin)
        tx = x + 20
        d.polygon([(tx - 5, y + 8), (tx + 5, y + 8), (tx + 3, y + 18), (tx - 3, y + 18)], fill=AMBER)
        d.rectangle([tx - 2, y + 18, tx + 2, y + 24], fill=AMBER)
        d.rectangle([tx - 5, y + 24, tx + 5, y + 27], fill=INK)
        bx, by = x + 34, y + 19
        d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=LIGHT, outline=INK, width=2)
        d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=INK)

    elif kind == "senegal":
        # AFCON shield/cup + "1-0"
        d.polygon([(x + 11, y + 10), (x + 23, y + 10), (x + 21, y + 20), (x + 17, y + 26), (x + 13, y + 20)], fill=TEAL, outline=INK)
        draw_centered_text(d, x + 33, cy + 1, "1-0", F_COND_BLACK(12), RED)

    elif kind == "huawei":
        # Microchip + 10/12 (shifted right/down of pin)
        d.rectangle([x + 10, y + 11, x + 24, y + 25], fill=INK)
        d.rectangle([x + 14, y + 15, x + 20, y + 21], fill=PAPER)
        for p in (13, 18, 23):
            d.line([(x + 7, y + p), (x + 10, y + p)], fill=INK, width=1)
            d.line([(x + 24, y + p), (x + 27, y + p)], fill=INK, width=1)
        draw_centered_text(d, x + 35, y + 12, "10", F_COND_BLACK(11), RED)
        draw_centered_text(d, x + 35, y + 23, "/12", F_COND_BOLD(9), INK)

    elif kind == "sanofi":
        # Pharma capsule + $41B (shifted right/down of pin)
        d.rounded_rectangle([x + 12, y + 9, x + 26, y + 17], radius=4, fill=BLUE)
        d.rounded_rectangle([x + 19, y + 9, x + 27, y + 17], radius=4, fill=LIGHT, outline=BLUE, width=1)
        draw_centered_text(d, x + 30, y + 24, "$41B", F_COND_BLACK(11), INK)

    elif kind == "selloff":
        # Downward red jagged market drop (starts past pin corner)
        pts = [(x + 12, y + 11), (x + 19, y + 14), (x + 24, y + 12), (x + 31, y + 22), (x + 39, y + 25)]
        d.line(pts, fill=RED, width=3, joint="curve")
        d.polygon([(x + 40, y + 26), (x + 34, y + 26), (x + 39, y + 20)], fill=RED)

    elif kind == "hanoi":
        # Hot pot bowl + explosion star
        d.chord([x + 8, y + 15, x + 26, y + 28], 0, 180, fill=INK)
        d.line([(x + 7, y + 21), (x + 27, y + 21)], fill=INK, width=2)
        d.polygon([(x + 29, y + 6), (x + 32, y + 12), (x + 39, y + 9), (x + 35, y + 16),
                   (x + 41, y + 20), (x + 33, y + 20), (x + 30, y + 25), (x + 27, y + 18), (x + 23, y + 13)], fill=RED)

    elif kind == "quasar":
        # Deep space + black hole + relativistic jet
        d.rectangle([x + 1, y + 1, x + w - 1, y + h - 1], fill=INK)
        qx, qy = x + 25, y + 17
        d.line([(x + 13, y + 27), (x + w - 6, y + 6)], fill=RED, width=2)
        d.ellipse([qx - 8, qy - 4, qx + 8, qy + 4], outline=LIGHT, width=2)
        d.ellipse([qx - 3, qy - 3, qx + 3, qy + 3], fill=INK, outline=RED, width=1)
        for sx, sy in [(x + 20, y + 6), (x + 37, y + 24), (x + 14, y + 18), (x + 35, y + 9)]:
            d.point((sx, sy), fill=LIGHT)


# ---------------------------------------------------------------- world map
# Coarse landmask as (row, col_start, col_end) ranges on a 92 x 18 grid.
LAND = {
    0: [(12, 18), (33, 39), (56, 90)],
    1: [(10, 20), (32, 40), (50, 90)],
    2: [(8, 22), (34, 38), (48, 90)],
    3: [(6, 24), (44, 46), (48, 55), (56, 88)],
    4: [(10, 28), (43, 47), (50, 56), (58, 86)],
    5: [(14, 29), (43, 48), (54, 60), (63, 84)],
    6: [(15, 29), (44, 47), (55, 59), (63, 80)],
    7: [(16, 26), (44, 46), (55, 58), (64, 73), (70, 74)],
    8: [(18, 25), (26, 34), (42, 56), (65, 70), (71, 74)],
    9: [(21, 24), (27, 36), (43, 56), (70, 82)],
    10: [(28, 36), (44, 55), (72, 80)],
    11: [(28, 35), (45, 54), (74, 84)],
    12: [(29, 34), (46, 53), (75, 84)],
    13: [(29, 33), (47, 52), (76, 83)],
    14: [(30, 32), (76, 82)],
    15: [(30, 32)],
    16: [(30, 31)],
    17: [],
}

# Pins for all 14 illustrated stories (staggered to avoid collisions):
PINS = [
    (1, 14, 5),    # Nvidia (Santa Clara, US)
    (2, 54, 6),    # COP31 (Antalya, Turkiye)
    (3, 51, 3),    # Kyiv / Dymer, Ukraine
    (4, 75, 12),   # Serang, Indonesia
    (5, 58, 8),    # Strait of Hormuz
    (6, 48, 7),    # Off Benghazi, Libya
    (7, 74, 4),    # Shenzhou 24 (China)
    (8, 20, 7),    # Women's World Cup 2031 (N. America)
    (9, 41, 9),    # Senegal (AFCON)
    (10, 25, 5),   # Huawei (Brooklyn / NYC)
    (11, 43, 4),   # Sanofi (Paris)
    (12, 28, 6),   # Tech sell-off (Wall St / NYC)
    (13, 72, 8),   # Hanoi blast (Vietnam)
    (14, 46, 1),   # ESA Euclid / Quasar (Europe)
]


def draw_world_map(d, x0, y0, w, h):
    """Dotted world map with 14 numbered pins."""
    cols, rows = 92, 18
    px, py = w / cols, h / rows
    for r in range(rows):
        for (c0, c1) in LAND.get(r, []):
            for c in range(c0, c1 + 1):
                cx = x0 + (c + 0.5) * px
                cy = y0 + (r + 0.5) * py
                d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6],
                          fill=(148, 138, 118))
    for (num, c, r) in PINS:
        cx = x0 + (c + 0.5) * px
        cy = y0 + (r + 0.5) * py
        rad = 6.2
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                  fill=RED, outline=LIGHT, width=1)
        draw_centered_text(d, cx, cy, str(num), F_BOLD(8), LIGHT)


# ---------------------------------------------------------------- story data (all facts strictly from notes/expansion-stories.md)

SMALL_CARDS = [
    (5, "hormuz", "MIDDLE EAST · TUE 24", "REPORTED",
     "TANKERS HIT BY MINES IN HORMUZ",
     "Iran says 3 oil tankers hit mines late Mon (US unconfirmed); US sanctions 2 dozen exchange houses.",
     "Horizon · Newsquawk · JAWS · GeoQuest"),
    (6, "libya", "AFRICA · TUE 24", "CONFIRMED",
     "UKRAINE SINKS RUSSIAN WARSHIP",
     "Ukrainian naval drones strike Russian warship near Benghazi; Libya condemns attack.",
     "AP · Reuters · Horizon"),
    (7, "shenzhou", "ASIA · TUE 24", "OFFICIAL",
     "SHENZHOU 24 LIFTS OFF",
     "Launches 2 Chinese astronauts & Pakistani Zeeshan Ali, 1st foreign astronaut on Tiangong.",
     "AP · Straits Times · GeoQuest"),
    (8, "fifa", "N. AMERICA · MON 23", "OFFICIAL",
     "WOMEN'S WORLD CUP HOSTS",
     "US, Mexico, Costa Rica, Jamaica host 48-team 2031; England, Scotland, Wales & NI host 2035.",
     "FIFA · CNN · AP · USA Today"),
    (9, "senegal", "AFRICA · TUE 24", "OFFICIAL",
     "SENEGAL GETS AFCON BACK",
     "CAS reinstates Senegal (1-0 final), overturning CAF ruling that gave title to Morocco.",
     "Reuters · CNN · Sportsnet"),
    (10, "huawei", "N. AMERICA · TUE 24", "OFFICIAL",
     "HUAWEI GUILTY: 10 OF 12",
     "Brooklyn jury convicts on trade-secret theft, bank fraud & Iran sanctions; sentencing 14 Sep 2027.",
     "BBC · CNN · Reuters · AP"),
    (11, "sanofi", "EUROPE · TUE 24", "OFFICIAL",
     "SANOFI BUYS INSMED FOR $41B",
     "$41B cash at $175/sh (17% premium; Insmed +14%); biggest pharma deal in 3 years.",
     "Reuters · Investopedia · CNBC"),
    (12, "selloff", "N. AMERICA · TUE 24", "CONFIRMED",
     "TECH SELLS OFF AFTER RALLY",
     "Nasdaq -1.5%, S&P -0.5%, Dow +0.9%; NVDA -6%, Analog Devices -17%, Anthropic <$83 IPO.",
     "Investopedia · Motley Fool · Reuters"),
    (13, "hanoi", "ASIA · TUE 24", "CONFIRMED",
     "HANOI BLAST KILLS 6",
     "Suspected gas leak blast at Hanoi hot pot eatery (8am) kills 6, hurts 10+; 14+ in hospital.",
     "AP · Reuters"),
    (14, "quasar", "EUROPE · TUE 24", "OFFICIAL",
     "OLDEST QUASAR EVER FOUND",
     "ESA Euclid finds J1504+6252 \"Dun Aonghasa\" (630M yrs post-Big Bang, ~360M-sun black hole, z>8).",
     "Reuters · Sky & Tel. · PopSci · ESA"),
]

# Remaining 22 stories (#15-#36) for ALSO ON 2-column numbered list
# (num, region_short, badge_type, headline, summary, sources)
ALSO_ON = [
    (15, "ASIA", "CONFIRMED", "NORTH KOREA EXPELS SWISS DIPLOMAT",
     "Pyongyang shuts Switzerland's new office & expels senior envoy over youth-camp war sanctions.",
     "AP · Daily Maverick"),
    (16, "OCEANIA", "OFFICIAL", "SOLOMON ISLANDS PICKS AUSTRALIA",
     "New treaty names Australia primary security partner, dropping security pact with China.",
     "AP · ABC News AU · GeoQuest"),
    (17, "N.AM", "REPORTED", "US READIES NEW TARIFFS",
     "Trump admin poised to release Sec. 301 probe; tariffs planned on China, EU & others.",
     "AP · Reuters"),
    (18, "ASIA", "REPORTED", "HASINA PLANS RETURN ON 16 DEC",
     "Ousted Bangladesh leader, sentenced to death, says she will return from exile 16 Dec.",
     "AP · BBC"),
    (19, "S.AM", "REPORTED", "HOSTAGES TAKEN IN CARTAGENA",
     "Armed men take hostages in Cartagena, one of Colombia's top tourist cities.",
     "AP · NXplace"),
    (20, "M.EAST", "REPORTED", "RIYADH TOWER HIT, 11 HURT",
     "Houthi drone hurts 11 at PIF Tower; Houthis say Saudi strikes killed 17 in Hodeidah, 25 south.",
     "Al Jazeera · Horizon"),
    (21, "ASIA", "OFFICIAL", "14 NATIONS BACK ICJ ROHINGYA RULING",
     "UK, Spain, Canada, Australia & 10 others affirm ICJ Myanmar genocide ruling (Mon 23).",
     "Horizon (3)"),
    (22, "N.AM", "REPORTED", "UN CHIEF WANTS AI RULES PACT",
     "Antonio Guterres urges multilateral framework to limit AI risks within a year (Mon 23).",
     "Horizon (2)"),
    (23, "N.AM", "CONFIRMED", "US MEASLES TOLL REACHES 14",
     "Cases near 6,000, 14 deaths; Pennsylvania reports 9th death, outbreak in 46 counties.",
     "NXplace · Horizon"),
    (24, "M.EAST", "REPORTED", "GAZA NOW \"TOXIC LAND\"",
     "Oxfam report says Israeli attacks contaminated almost the whole Gaza territory.",
     "Horizon (2)"),
    (25, "ASIA", "CONFIRMED", "NEPAL QUAKE 5.6",
     "M5.6 quake (EMSC 5.3) hits Koshi near China border 7:17am; Olangchung Gola epicentre.",
     "PTI · Nature World · Jagran Josh"),
    (26, "N.AM", "OFFICIAL", "MEXICO TO TRY \"EL CHAPO ISIDRO\"",
     "Fausto Meza Flores to face drug & weapons trial in Mexico despite US extradition request.",
     "Horizon · Reuters"),
    (27, "M.EAST", "CONFIRMED", "IRAN LASHES SINGER 74 TIMES",
     "Parastoo Ahmadi, 3 musicians & producer sentenced to 74 lashes in Qom for unveiled singing.",
     "Horizon (2)"),
    (28, "EUROPE", "REPORTED", "EU'S 22ND RUSSIA SANCTIONS",
     "EC proposes ~60 more banks, crypto networks & ban on Russian symbols at EU sports.",
     "JAWS · GeoQuest · Horizon"),
    (29, "EUROPE", "CONFIRMED", "ZAPORIZHZHIA HIT AGAIN",
     "Night strikes kill 2, wound 30+ (incl. 4 minors & a baby); city struck twice in one day.",
     "Horizon (2)"),
    (30, "EUROPE", "OFFICIAL", "NATO AWACS TO POLAND",
     "NATO deploys AWACS detection aircraft to Poland after 3 missiles fall on its territory.",
     "Horizon · Global Intel"),
    (31, "EUROPE", "OFFICIAL", "UK WARNS OF RUSSIAN SABOTAGE",
     "Defence ministry & MI5 warn firms backing Ukraine to \"act now\" against Russian sabotage.",
     "JAWS · BBC"),
    (32, "EUROPE", "REPORTED", "PIP SHAKE-UP HITS THOUSANDS",
     "Timms UK disability benefits review proposes PIP overhaul; hundreds of thousands may lose aid.",
     "The Guardian · BBC"),
    (33, "N.AM", "REPORTED", "ILHAN OMAR HOME SEARCH ROW",
     "Records show DOJ & judge debated constitutional limits on searching Rep. Omar's home.",
     "PBS · GeoQuest"),
    (34, "EUROPE", "OFFICIAL", "HUNTLEY'S KILLER JAILED AGAIN",
     "Inmate who murdered Ian Huntley receives a second whole-life prison sentence.",
     "Sky News · BBC"),
    (35, "N.AM", "OFFICIAL", "DOJ'S $8B SCAM CRACKDOWN",
     "DOJ charges 800+ suspects, recovers $8B+ in largest anti-scam surge (400+ cases, 85 districts).",
     "NY Post · Fox News · DOJ"),
    (36, "N.AM", "OFFICIAL", "GIULIANI GETS MEDAL OF FREEDOM",
     "Trump awards Rudy Giuliani, 82, Presidential Medal of Freedom in private Oval Office ceremony.",
     "Reuters · AP · USA Today"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 20
    R = W - M  # 1004, usable width = 984

    # ---- 1. Top kicker bar (y=6..24) ----
    kf = F_BOLD(13)
    d.text((M, 6), "THE WORLD IN ONE PAGE", font=kf, fill=RED)
    right = "36 STORIES  ·  7 REGIONS  ·  21–24 NOV 2026"
    d.text((R - d.textlength(right, font=kf), 6), right, font=kf, fill=INK)
    rule(d, M, 23, R, 2, INK)

    # ---- 2. Masthead (y=24..71) ----
    draw_centered_text(d, W / 2, 47, "Tuesday 24 November 2026",
                       F_SERIF_BLACK(47), INK)
    rule(d, M, 71, R, 2, INK)

    # ---- 3. Sub-deck (y=73..89) ----
    deck = ("Huang returns as Nvidia chief  ·  COP31 collapses  ·  14 missing in Kyiv  ·  "
            "24 dead in Serang  ·  Hormuz mines  ·  Sanofi $41B deal  ·  Shenzhou 24")
    draw_centered_text(d, W / 2, 81, deck, F_ITALIC(13), BODY_INK)

    # ---- 4. Region chips (y=91..109) ----
    cy = 91
    x = M
    chips = [
        ("EUROPE 10", BLUE),
        ("NORTH AMERICA 11", RED),
        ("ASIA 7", TEAL),
        ("MIDDLE EAST 4", AMBER),
        ("AFRICA 2", PLUM),
        ("SOUTH AMERICA 1", OCHRE),
        ("OCEANIA 1", OCEAN),
    ]
    cf = F_BOLD(10)
    for label, color in chips:
        x += badge(d, x, cy, label, color, fnt=cf, h=16, pad=10) + 5
    note = "EVERY STORY DATED 21–24 NOV 2026"
    nf = F_BOLD(10)
    d.text((R - d.textlength(note, font=nf), cy + 2), note, font=nf, fill=GREY)

    # ---- 5. Timeline strip (y=111..129) ----
    oy = 111
    d.rectangle([M, oy, R, oy + 17], fill=INK)
    order = ("TIMELINE  ·  SAT 21 NOV Serang fire  ·  SUN 22 NOV Kyiv strike, COP31 ends  ·  "
             "MON 23 NOV Huang returns, FIFA hosts, ICJ backed  ·  TUE 24 NOV rest of day's news")
    draw_centered_text(d, W / 2, oy + 8.5, order, F_BOLD(11), LIGHT)

    # ---- 6. IN NUMBERS strip (y=131..167) ----
    ny0, ny1 = 131, 167
    nums = [
        ("+31.48%", "NVDA in a day", GREEN),
        ("$952B", "market value gained", INK),
        ("$41B", "Sanofi-Insmed deal", INK),
        ("186", "drones launched", INK),
        ("161", "intercepted", INK),
        ("800+", "scam suspects charged", INK),
        ("24", "dead in Serang fire", RED),
    ]
    d.text((M, ny0 + 4), "THE DAY", font=F_BOLD(11), fill=RED)
    d.text((M, ny0 + 18), "IN NUMBERS", font=F_BOLD(11), fill=RED)
    cell_x0 = M + 84
    cell_w = (R - cell_x0) / len(nums)
    for i, (num, label, color) in enumerate(nums):
        cx = cell_x0 + cell_w * i
        draw_centered_text(d, cx + cell_w / 2, ny0 + 12, num, F_COND_BLACK(22), color)
        draw_centered_text(d, cx + cell_w / 2, ny0 + 29, label, F_BOLD(10), BODY_INK)
        if i:
            d.line([(cx, ny0 + 4), (cx, ny1 - 3)], fill=GRID, width=1)
    rule(d, M, ny1 + 1, R, 2, INK)

    # ---- 7. Section 1: The 4 Original Leads (y=172..354, height 182px) ----
    LY = 172
    LH = 182
    # Left: HUANG IS BACK (462px wide: x=20..482)
    # Text left subcol: 256px (x=20..276), Chart right subcol: 198px (x=282..480)
    d.rectangle([M, LY, M + 76, LY + 16], fill=RED)
    draw_centered_text(d, M + 38, LY + 8, "1 · LEAD", F_BOLD(10), LIGHT)
    d.text((M + 82, LY + 1), "N. AMERICA · MON 23", font=F_BOLD(10), fill=RED)
    badge(d, M + 196, LY + 1, "CONFIRMED", GREEN, fnt=F_BOLD(9), h=14, pad=8)

    hf = F_BLACK(36)
    d.text((M, LY + 17), "HUANG", font=hf, fill=INK)
    d.text((M, LY + 51), "IS BACK", font=hf, fill=INK)

    sy = LY + 92
    sy = draw_text_block(
        d, M, sy,
        "Nvidia reinstates founder Jensen Huang as CEO.",
        F_BOLD(13), INK, 254, 14, max_lines=2
    )
    sy += 2
    sy = draw_text_block(
        d, M, sy,
        "Shares +31.48% in a day, best day since 2003, +$952B market value.",
        F_MED(11), BODY_INK, 254, 13, max_lines=2
    )
    d.text((M, LY + 148), "Reuters · CNN · USA Today · Zacks · Investopedia",
           font=F_MED(9), fill=GREY)
    iy = LY + 162
    for idx_x, box_w, idx_txt in ((M, 130, "NASDAQ  +6.5%"), (M + 136, 114, "S&P  +4.7%")):
        d.rectangle([idx_x, iy, idx_x + box_w, iy + 19], fill=LIGHT, outline=INK, width=2)
        draw_centered_text(d, idx_x + box_w / 2, iy + 9.5, idx_txt, F_BLACK(12), INK)

    # Lead chart panel (x=282..480, y=LY..LY+180)
    cx0, cy0, cx1, cy1 = 282, LY, 480, LY + LH - 2
    d.rectangle([cx0 + 3, cy0 + 3, cx1 + 3, cy1 + 3], fill=INK)
    d.rectangle([cx0, cy0, cx1, cy1], fill=LIGHT, outline=INK, width=2)
    d.text((cx0 + 10, cy0 + 2), "+31.48%", font=F_COND_BLACK(40), fill=GREEN)
    d.text((cx0 + 11, cy0 + 46), "NVDA · BEST DAY SINCE 2003", font=F_BLACK(11), fill=INK)
    d.text((cx0 + 11, cy0 + 60), "+$952B market value", font=F_SEMI(11), fill=BODY_INK)

    px0, py0, px1, py1 = cx0 + 12, cy0 + 78, cx1 - 12, cy1 - 17
    base_y = py1 - 14
    pts = [
        (px0 + 2, base_y - 2),
        (px0 + 28, base_y - 5),
        (px0 + 54, base_y + 1),
        (px0 + 80, base_y - 9),
        (px0 + 100, base_y - 6),
        (px0 + 120, py0 + 44),
        (px0 + 144, py0 + 14),
        (px1 - 6, py0 + 5),
    ]
    poly_pts = [(pts[0][0], base_y)] + pts + [(pts[-1][0], base_y)]
    d.polygon(poly_pts, fill=GREEN_FILL)
    for gy in (py0 + 6, py0 + 29, py0 + 52):
        d.line([(px0, gy), (px1, gy)], fill=GRID, width=1)
    draw_dashed_line(d, px0, base_y, px1, GREY, dash=5, gap=4, width=1)
    d.text((px0, base_y + 4), "PREV. CLOSE", font=F_BOLD(8), fill=GREY)
    d.line(pts, fill=GREEN, width=4, joint="curve")
    pkx, pky = pts[-1]
    d.ellipse([pkx - 5, pky - 5, pkx + 5, pky + 5], fill=GREEN, outline=LIGHT, width=2)
    d.line([(px0, py1), (px1, py1)], fill=INK, width=1)
    axf = F_BOLD(9)
    d.text((px0, py1 + 2), "OPEN", font=axf, fill=BODY_INK)
    d.text((px1 - d.textlength("CLOSE", font=axf), py1 + 2), "CLOSE", font=axf, fill=GREEN)

    # Right 3 Big Cards: COP31, KYIV, SERANG (x=490..1004 -> 514px, 3 cards x 166px + 2x8px gap)
    CX_START = 490
    PW, GAP = 166, 8
    BH = 50
    panels = [
        ("EUROPE · CLIMATE", "COP31 COLLAPSES",
         "Antalya talks ended Sun 22 Nov with no deal. \"Antalya Pact\" rejected for never naming fossil fuels.",
         "globe", "2+ wks · 1st breakdown since '09",
         "CNN · WRI · Le Monde"),
        ("EUROPE · UKRAINE", "14 MISSING IN KYIV",
         "Russian drone strike Sun 22 Nov left a five-storey block in Dymer partly collapsed.",
         "kyiv", "186 drones · 161 intercepted",
         "111next · EUobserver"),
        ("ASIA · INDONESIA", "24 DEAD IN FIRE",
         "Fire at PT Fonusa Agung Mulia (Milkita) candy factory in Serang, Banten, Sat 21 Nov.",
         "factory", "~30 missing · ~300 inside",
         "AP · Reuters"),
    ]

    for i, (kicker, head, fact, pic, stat, srcs) in enumerate(panels):
        x0 = CX_START + i * (PW + GAP)
        x1 = x0 + PW
        d.rectangle([x0, LY, x1, LY + LH], fill=LIGHT, outline=INK, width=2)
        d.rectangle([x0 + 2, LY + 2, x1 - 2, LY + BH], fill=BAND_BG)
        d.line([(x0, LY + BH), (x1, LY + BH)], fill=INK, width=1)

        if pic == "globe":
            draw_globe_band(d, x0, LY, PW, BH)
        elif pic == "kyiv":
            draw_kyiv_band(d, x0, LY, PW, BH)
        else:
            draw_factory_band(d, x0, LY, PW, BH)

        ix = x0 + 8
        iw = PW - 16
        ky = LY + BH + 4
        d.text((ix, ky), kicker, font=F_BOLD(10), fill=RED)
        _bf = F_BOLD(8)
        _bw = d.textlength("CONFIRMED", font=_bf) + 8
        badge_outline(d, x1 - 7 - _bw, ky - 1, "CONFIRMED", GREEN, _bf, h=13, pad=8)

        hy = ky + 14
        hy = draw_text_block(d, ix, hy, head, F_COND_BLACK(18), INK, iw, 18, max_lines=2)
        fy = hy + 2
        fy = draw_text_block(d, ix, fy, fact, F_MED(10), BODY_INK, iw, 11.5, max_lines=4)

        sy2 = LY + LH - 30
        d.line([(ix, sy2), (x1 - 8, sy2)], fill=INK, width=1)
        draw_text_block(d, ix, sy2 + 2, stat, F_COND_BOLD(11), INK, iw, 12, max_lines=1)
        d.text((ix, LY + LH - 14), srcs, font=F_MED(9), fill=GREY)

    rule(d, M, LY + LH + 4, R, 3, INK)

    # ---- 8. Section 2: 10 Small Illustrated Stories (#5-#14) (y=361..571) ----
    SY = LY + LH + 8  # 362
    d.text((M, SY), "WORLD DISPATCHES  ·  10 ILLUSTRATED STORIES (#5–#14 ON MAP)",
           font=F_BOLD(11), fill=RED)
    GY = SY + 15
    COLS, ROWS = 5, 2
    CGAP, RGAP = 8, 5
    CW = (R - M - (COLS - 1) * CGAP) // COLS  # 190px
    CH = 93  # 2 * 93 + 5 = 191px (GY..568)

    for idx, (num, pic, kicker, btype, head, summary, srcs) in enumerate(SMALL_CARDS):
        col = idx % COLS
        row = idx // COLS
        x0 = M + col * (CW + CGAP)
        y0 = GY + row * (CH + RGAP)
        x1 = x0 + CW
        y1 = y0 + CH

        d.rectangle([x0, y0, x1, y1], fill=LIGHT, outline=INK, width=1)
        # Top area: 44x32 mini pic + pin + kicker + badge + 2-line headline
        draw_mini_pic(d, pic, x0 + 5, y0 + 5, 44, 31)
        pin_num(d, x0 + 9, y0 + 9, num, r=6)

        tx = x0 + 54
        tw = CW - 59
        d.text((tx, y0 + 4), kicker, font=F_BOLD(8), fill=RED)
        bf = F_BOLD(8)
        bw = d.textlength(btype, font=bf) + 7
        badge(d, x1 - 4 - bw, y0 + 3, btype, BADGE_COLORS[btype], fnt=bf, h=11, pad=7)

        draw_text_block(d, tx, y0 + 15, head, F_COND_BLACK(12), INK, tw, 11.5, max_lines=2)

        # Summary (3 lines max at 11.5px leading)
        draw_text_block(d, x0 + 6, y0 + 39, summary, F_MED(10), BODY_INK, CW - 12, 11.5, max_lines=3)

        # Bottom source bar
        d.line([(x0 + 6, y1 - 14), (x1 - 6, y1 - 14)], fill=GRID, width=1)
        d.text((x0 + 6, y1 - 12), srcs, font=F_MED(9), fill=GREY)

    rule(d, M, GY + 2 * CH + RGAP + 4, R, 3, INK)

    # ---- 9. Section 3: ALSO ON numbered list (#15-#36 = 22 stories) (y=577..886) ----
    AY = GY + 2 * CH + RGAP + 8  # 576
    d.text((M, AY), "ALSO ON TUESDAY 24 NOVEMBER  ·  22 MORE VERIFIED STORIES (#15–#36)",
           font=F_BOLD(11), fill=RED)
    LY2 = AY + 16  # 592
    COL_GAP = 14
    COL_W = (R - M - COL_GAP) // 2  # 485px
    ROW_H = 27  # 11 * 27 = 297px -> ends at 889; summary descenders clear the next rule by 2px

    for idx, (num, reg, btype, head, summary, srcs) in enumerate(ALSO_ON):
        col = idx // 11
        row = idx % 11
        x0 = M + col * (COL_W + COL_GAP)
        y0 = LY2 + row * ROW_H

        if row > 0:
            d.line([(x0, y0), (x0 + COL_W, y0)], fill=GRID, width=1)

        # Number pill
        d.rounded_rectangle([x0, y0 + 4, x0 + 20, y0 + 19], radius=3, fill=INK)
        draw_centered_text(d, x0 + 10, y0 + 11.5, str(num), F_BOLD(10), LIGHT)

        hx = x0 + 24
        d.text((hx, y0 + 2), head, font=F_COND_BOLD(12), fill=INK)
        hw = d.textlength(head, font=F_COND_BOLD(12))

        # Region + badge inline after headline
        rx = hx + hw + 5
        rf = F_BOLD(8)
        d.text((rx, y0 + 4), reg, font=rf, fill=GREY)
        rw = d.textlength(reg, font=rf)
        bx = rx + rw + 4
        badge_outline(d, bx, y0 + 3, btype, BADGE_COLORS[btype], fnt=F_BOLD(8), h=11, pad=6)

        # Right-aligned source on line 1
        sf = F_MED(9)
        sw = d.textlength(srcs, font=sf)
        sx = x0 + COL_W - sw
        bw_used = d.textlength(btype, font=F_BOLD(8)) + 6
        if bx + bw_used + 4 > sx:
            raise ValueError(f"Line 1 collision on #{num}: {head}")
        d.text((sx, y0 + 3), srcs, font=sf, fill=GREY)

        # Line 2: 1-line summary (9.5px font with clean descender clearance)
        sum_w = d.textlength(summary, font=F_MED(9))
        # Use 10px if it fits cleanly, else 9.5px — actually let's test 10px at y0+14!
        sum_fnt = F_MED(10)
        sum_w = d.textlength(summary, font=sum_fnt)
        if sum_w > COL_W - 24:
            raise ValueError(f"Summary too wide ({sum_w:.0f} > {COL_W - 24}) on #{num}: {summary}")
        d.text((hx, y0 + 14), summary, font=sum_fnt, fill=BODY_INK)

    # ---- 10. Bottom row: World Map + HOW SURE + DATE CHECK (y=891..990) ----
    MY = LY2 + 11 * ROW_H + 2  # 891
    rule(d, M, MY, R, 2, INK)

    d.text((M, MY + 4), "WHERE IT HAPPENED  ·  14 ILLUSTRATED STORIES ON MAP",
           font=F_BOLD(10), fill=RED)
    draw_world_map(d, M, MY + 17, 468, 62)
    d.text((M, MY + 82),
           "1 NVDA · 2 Antalya · 3 Kyiv · 4 Serang · 5 Hormuz · 6 Libya · 7 China · 8 N.Am · 9 Senegal · 10,12 NYC · 11 Paris · 13 Hanoi · 14 ESA",
           font=F_MED(8), fill=BODY_INK)

    mx = 508
    d.text((mx, MY + 4), "HOW SURE", font=F_BOLD(10), fill=RED)
    legend = [
        (GREEN, "CONFIRMED", "reported by 2+ outlets"),
        (BLUE, "OFFICIAL", "announced on the record"),
        (RED, "REPORTED", "carried by the day's wires, single source or claim"),
    ]
    ly = MY + 19
    for color, name, desc in legend:
        badge(d, mx, ly, name, color, fnt=F_BOLD(9), h=14, pad=8)
        d.text((mx + 74, ly + 1), desc, font=F_MED(10), fill=BODY_INK)
        ly += 17

    d.text((mx, ly + 4), "DATE CHECK:", font=F_BOLD(10), fill=RED)
    d.text((mx + 68, ly + 4), "Every story happened or was first reported 21–24 Nov 2026;",
           font=F_MED(10), fill=BODY_INK)
    d.text((mx, ly + 17), "nothing from 25 Nov included. Original drawings, no photographs.",
           font=F_ITALIC(10), fill=GREY)

    # ---- 11. Footer (y=990..1020) ----
    rule(d, M, 990, R, 2, INK)
    ff = F_MED(9)
    foot1 = ("Sources: Reuters, AP, CNN, BBC, Al Jazeera, CNBC, Investopedia, The Guardian, Le Monde, "
             "PBS, Sky News, The Straits Times, ABC News AU, Daily Maverick, Sportsnet, Motley Fool,")
    foot2 = ("USA Today, NY Post, Fox News, WRI, EUobserver, 111next, ESA, Sky & Telescope, Popular Science, "
             "PTI, Nature World News, Jagran Josh, FIFA, US DOJ, Zacks, Horizon, GeoQuest, JAWS/Medium, Newsquawk, NXplace")
    d.text(((W - d.textlength(foot1, font=ff)) / 2, 995), foot1, font=ff, fill=BODY_INK)
    d.text(((W - d.textlength(foot2, font=ff)) / 2, 1007), foot2, font=ff, fill=BODY_INK)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
