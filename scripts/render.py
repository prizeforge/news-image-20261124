#!/usr/bin/env python3
"""Render the 24 November 2026 front page (1024x1024) with Pillow.

Deterministic: fixed palette, fixed fonts, fixed geometry, no timestamps.
Run:  python3 scripts/render.py   -> writes assets/entry.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "entry.png")

W, H = 1024, 1024
PAPER = (247, 243, 234)   # cream
INK = (26, 34, 56)        # navy ink
RED = (192, 57, 43)       # brick red
GREEN = (30, 122, 70)     # market green
GREY = (90, 100, 114)     # secondary text
LIGHT = (255, 255, 255)   # panel white
GRID = (210, 205, 192)    # light grid

FONT_DIR = "/usr/share/fonts/truetype/noto"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_BLACK = lambda s: font("NotoSansDisplay-Black.ttf", s)
F_BOLD = lambda s: font("NotoSansDisplay-Bold.ttf", s)
F_MED = lambda s: font("NotoSansDisplay-Medium.ttf", s)
F_REG = lambda s: font("NotoSansDisplay-Regular.ttf", s)


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


def draw_text_block(draw, x, y, text, fnt, fill, max_w, leading):
    lines = wrap(draw, text, fnt, max_w)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, y, x1, wdt, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=wdt)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 36            # margin
    R = 988           # right edge (1024-36)

    # ---- masthead ----
    rule(d, M, 40, R, 3)
    title = "THE WORLD IN ONE PAGE"
    tf = F_BLACK(56)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 52), title, font=tf, fill=INK)
    rule(d, M, 126, R, 4, RED)
    df = F_BOLD(23)
    d.text((M, 138), "TUESDAY, 24 NOVEMBER 2026", font=df, fill=RED)
    right = "FOUR STORIES THAT MADE THE DAY"
    d.text((R - d.textlength(right, font=df), 138), right, font=df, fill=INK)
    rule(d, M, 172, R, 6)

    # ---- lead story: NVIDIA ----
    LY = 196
    # kicker
    kf = F_BOLD(22)
    d.text((M, LY), "MARKETS  ·  LEAD STORY", font=kf, fill=RED)
    # headline, two lines
    hf = F_BLACK(104)
    d.text((M, LY + 34), "HUANG", font=hf, fill=INK)
    d.text((M, LY + 138), "IS BACK", font=hf, fill=INK)
    # subhead
    sy = LY + 258
    sy = draw_text_block(d, M, sy,
                         "Nvidia reinstates its founder as chief executive.",
                         F_BOLD(29), INK, 580, 36)
    # fact line
    sy += 8
    sy = draw_text_block(d, M, sy,
                         "Shares +31% in a day — a $952 billion gain.",
                         F_REG(24), GREY, 580, 31)

    # chart panel (right)
    cx0, cy0, cx1, cy1 = 648, 196, R, 548
    d.rectangle([cx0, cy0, cx1, cy1], fill=LIGHT, outline=INK, width=2)
    # gridlines
    for gy in (cy0 + 80, cy0 + 160, cy0 + 240):
        d.line([(cx0 + 14, gy), (cx1 - 14, gy)], fill=GRID, width=1)
    # chart polyline: flat, dip, then a steep spike
    pts = [(cx0 + 20, cy0 + 290), (cx0 + 80, cy0 + 280), (cx0 + 130, cy0 + 300),
           (cx0 + 180, cy0 + 250), (cx0 + 220, cy0 + 262), (cx0 + 260, cy0 + 150),
           (cx0 + 300, cy0 + 60), (cx1 - 24, cy0 + 42)]
    d.line(pts, fill=GREEN, width=6, joint="curve")
    d.ellipse([pts[-1][0] - 7, pts[-1][1] - 7, pts[-1][0] + 7, pts[-1][1] + 7],
              fill=GREEN)
    # +31% label
    pf = F_BLACK(58)
    d.text((cx0 + 20, cy0 + 18), "+31%", font=pf, fill=GREEN)
    lf = F_BOLD(20)
    d.text((cx0 + 20, cy0 + 82), "NVDA  ·  MONDAY'S CLOSE", font=lf, fill=INK)
    d.text((cx0 + 20, cy1 - 34), "Best day since 2003", font=F_REG(19), fill=GREY)

    # ---- divider ----
    rule(d, M, 572, R, 3)

    # ---- bottom row: three panels ----
    PY, PH = 592, 378
    PW, GAP = 301, 24
    panels = [
        ("CLIMATE", "COP31 COLLAPSES",
         "Antalya talks end with no deal. The pact never named fossil fuels.",
         "globe", "194 nations · no deal"),
        ("UKRAINE", "14 MISSING IN KYIV",
         "A Russian drone hit a five-storey block in Dymer. Rescuers search "
         "the rubble.", "building", "186 drones, one night"),
        ("INDONESIA", "24 DEAD IN FACTORY FIRE",
         "Blaze at a candy factory in Serang, Banten. About 30 still missing.",
         "factory", "300 workers on site"),
    ]
    for i, (kicker, head, fact, pic, stat) in enumerate(panels):
        x0 = M + i * (PW + GAP)
        x1 = x0 + PW
        d.rectangle([x0, PY, x1, PY + PH], fill=LIGHT, outline=INK, width=2)
        ix = x0 + 22
        iw = PW - 44
        # pictogram band
        pic_y = PY + 22
        if pic == "globe":
            cx, cy, r = x0 + PW // 2, pic_y + 52, 48
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
            d.ellipse([cx - 20, cy - r, cx + 20, cy + r], outline=INK, width=2)
            d.line([(cx - r, cy), (cx + r, cy)], fill=INK, width=2)
            # red crack across the globe
            d.line([(cx - 34, cy - 30), (cx - 8, cy - 4), (cx - 18, cy + 18),
                    (cx + 12, cy + 34)], fill=RED, width=5, joint="curve")
        elif pic == "building":
            # three blocks, middle one broken
            d.rectangle([x0 + 62, pic_y + 42, x0 + 118, pic_y + 108], fill=INK)
            d.rectangle([x0 + 128, pic_y + 18, x0 + 184, pic_y + 108], fill=INK)
            d.rectangle([x0 + 194, pic_y + 58, x0 + 238, pic_y + 108], fill=INK)
            # broken top on the middle block
            d.polygon([(x0 + 128, pic_y + 18), (x0 + 146, pic_y + 2),
                       (x0 + 162, pic_y + 16), (x0 + 184, pic_y + 18)],
                      fill=PAPER)
            # windows
            for wx in (x0 + 72, x0 + 92):
                for wy in (pic_y + 56, pic_y + 78):
                    d.rectangle([wx, wy, wx + 10, wy + 10], fill=PAPER)
            for wx in (x0 + 138, x0 + 160):
                for wy in (pic_y + 40, pic_y + 62, pic_y + 84):
                    d.rectangle([wx, wy, wx + 10, wy + 10], fill=PAPER)
            # smoke
            d.ellipse([x0 + 138, pic_y - 6, x0 + 158, pic_y + 14], fill=GREY)
            d.ellipse([x0 + 158, pic_y - 12, x0 + 172, pic_y + 2], fill=GREY)
        else:  # factory
            # sawtooth roof + chimney + flame
            d.rectangle([x0 + 56, pic_y + 52, x0 + 240, pic_y + 108], fill=INK)
            d.polygon([(x0 + 56, pic_y + 52), (x0 + 102, pic_y + 22),
                       (x0 + 148, pic_y + 52), (x0 + 194, pic_y + 22),
                       (x0 + 240, pic_y + 52)], fill=INK)
            d.rectangle([x0 + 212, pic_y + 2, x0 + 230, pic_y + 52], fill=INK)
            # flame
            d.polygon([(x0 + 148, pic_y + 26), (x0 + 162, pic_y + 2),
                       (x0 + 172, pic_y + 22), (x0 + 186, pic_y + 6),
                       (x0 + 188, pic_y + 30), (x0 + 168, pic_y + 40)],
                      fill=RED)
            # windows
            for wx in (x0 + 72, x0 + 104, x0 + 136, x0 + 168, x0 + 200):
                d.rectangle([wx, pic_y + 68, wx + 14, pic_y + 88], fill=PAPER)
        # kicker
        ky = pic_y + 122
        d.text((ix, ky), kicker, font=F_BOLD(19), fill=RED)
        # headline
        hy = ky + 26
        hy = draw_text_block(d, ix, hy, head, F_BLACK(30), INK, iw, 32)
        # fact
        draw_text_block(d, ix, hy + 10, fact, F_REG(20), GREY, iw, 25)
        # bottom stat line
        sy2 = PY + PH - 44
        d.line([(ix, sy2), (x1 - 22, sy2)], fill=GRID, width=2)
        d.text((ix, sy2 + 12), stat, font=F_BOLD(19), fill=INK)

    # ---- footer ----
    rule(d, M, 988, R, 2)
    ff = F_REG(14)
    foot = "Sources: Reuters · CNN · AP · WRI · Le Monde — 24 November 2026"
    d.text(((W - d.textlength(foot, font=ff)) / 2, 996), foot, font=ff, fill=GREY)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
