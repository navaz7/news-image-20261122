#!/usr/bin/env python3
"""Compose entry.png — a newspaper front page summing up 22 November 2026.

Layout: masthead + date line, a hero story with a hand-drawn graphic,
two rows of two story panels (each with its own drawn graphic strip) and
a navy ticker band along the bottom. Every graphic is drawn with Pillow
shapes — no external images. All text is shrink-to-fit wrapped so that
nothing overflows its box.

Stories (reported 22 Nov 2026): COP31 climate talks in Antalya collapse
with no deal after the draft omitted fossil fuels; a suspected Ukrainian
drone hits a Russian warship at Benghazi, Libya, and a second ship is
reported hit; Democrats secure at least 258 US House seats, their
largest majority since 1992; global stocks fall as the AI sell-off
deepens (S&P 500 -3.7%, Nikkei -5.06%); BepiColombo enters orbit around
Mercury; plus ticker briefs on El Chapo Isidro's capture, the Indonesia
candy-factory fire, tankers hit near Hormuz, the Dymer apartment strike
and Poland confirming the missiles on its soil were Russian Kh-101s.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"

W = H = 1024
MARGIN = 36
CW = W - 2 * MARGIN  # content width = 952

CREAM = (244, 236, 216)
NAVY = (20, 33, 61)
NAVY_LIGHT = (38, 58, 99)
CRIMSON = (179, 32, 44)
GOLD = (216, 164, 65)
PAPER_PANEL = (250, 246, 235)
SKY = (198, 219, 226)
TEAL = (23, 107, 122)
WHITE = (245, 245, 240)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_BLACK = [FONT_DIR / "DejaVuSerif-Bold.ttf"]
SERIF = [FONT_DIR / "DejaVuSerif.ttf"]
SANS_BLACK = [FONT_DIR / "DejaVuSans-Bold.ttf"]
SANS_BOLD = [FONT_DIR / "DejaVuSans-Bold.ttf"]
SANS = [FONT_DIR / "DejaVuSans.ttf"]


def font(candidates, size):
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise FileNotFoundError(candidates)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def fit_one_line(draw, s, candidates, max_w, start, minimum=12):
    """Largest font (<= start) whose single line fits max_w."""
    size = start
    while size > minimum:
        f = font(candidates, size)
        if text_w(draw, s, f) <= max_w:
            return f
        size -= 1
    return font(candidates, minimum)


def wrap(draw, s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_wrapped(draw, s, candidates, max_w, max_lines, start, minimum=11):
    """Largest font whose wrapped text fits within max_lines lines."""
    size = start
    while size > minimum:
        f = font(candidates, size)
        lines = wrap(draw, s, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = font(candidates, minimum)
    return f, wrap(draw, s, f, max_w)[:max_lines]


def line_h(f, ratio=1.22):
    return int(f.size * ratio)


def draw_lines(draw, lines, f, x, y, fill, lh=None, anchor_center_x=None):
    lh = lh or line_h(f)
    for ln in lines:
        if anchor_center_x is not None:
            draw.text((anchor_center_x - text_w(draw, ln, f) / 2, y), ln, font=f, fill=fill)
        else:
            draw.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def draw_tracked(draw, s, f, cx, y, fill, tracking=4):
    """Draw text centered at cx with extra letter tracking."""
    widths = [text_w(draw, ch, f) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, wch in zip(s, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += wch + tracking
    return y + line_h(f)


def star(draw, cx, cy, r_outer, r_inner, fill, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


def burst(draw, cx, cy, r, fill):
    """Jagged explosion burst."""
    pts = []
    n = 12
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(i * 180 / n + 8)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill)


# ---------------------------------------------------------------- graphics

def hero_globe(draw, box):
    """Cracked globe over Antalya: COP31 ends with no deal."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    cx, cy = x + w * 0.30, y + h / 2
    r = int(h * 0.44)
    # Globe: teal disc, cream land blobs
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TEAL)
    draw.ellipse([cx - r * 0.55, cy - r * 0.72, cx + r * 0.15, cy - r * 0.10], fill=(214, 196, 150))
    draw.ellipse([cx - r * 0.10, cy + r * 0.05, cx + r * 0.62, cy + r * 0.66], fill=(214, 196, 150))
    draw.ellipse([cx + r * 0.28, cy - r * 0.80, cx + r * 0.80, cy - r * 0.30], fill=(214, 196, 150))
    # Meridian arcs
    draw.arc([cx - r, cy - r, cx + r, cy + r], start=250, end=470, fill=NAVY_LIGHT, width=2)
    draw.arc([cx - int(r * 0.55), cy - r, cx + int(r * 0.55), cy + r], start=270, end=450, fill=NAVY_LIGHT, width=2)
    # Jagged crack across the globe
    crack = [(cx - r * 0.72, cy - r * 0.55), (cx - r * 0.38, cy - r * 0.18),
             (cx - r * 0.55, cy + r * 0.12), (cx - r * 0.12, cy + r * 0.42),
             (cx - r * 0.30, cy + r * 0.72), (cx + r * 0.05, cy + r * 0.95)]
    draw.line(crack, fill=CRIMSON, width=6)
    draw.line(crack, fill=GOLD, width=2)
    # Right side: big NO DEAL stamp
    tx = x + w * 0.58
    tf = font(SANS_BLACK, 46)
    draw.text((tx, y + 22), "NO", font=tf, fill=CRIMSON)
    draw.text((tx, y + 74), "DEAL", font=tf, fill=CRIMSON)
    draw.line([(tx, y + 128), (x + w - 24, y + 128)], fill=GOLD, width=3)
    sf = font(SANS_BOLD, 20)
    draw.text((tx, y + 140), "COP31 · ANTALYA", font=sf, fill=WHITE)
    lf = font(SANS_BOLD, 15)
    draw.text((x + 18, y + h - 30), "LONGEST COP ON RECORD", font=lf, fill=GOLD)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


def ship_graphic(draw, box):
    """Warship at Benghazi harbour, drone burst overhead."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=SKY)
    # Harbour skyline (low, left)
    draw.rectangle([x, y + h - 42, x + 90, y + h - 1], fill=(120, 110, 92))
    draw.rectangle([x + 100, y + h - 30, x + 150, y + h - 1], fill=(120, 110, 92))
    # Sea band
    draw.rectangle([x, y + h * 0.52, x + w - 1, y + h - 1], fill=NAVY)
    for i in range(5):
        wy = y + h * 0.58 + i * 14
        if wy >= y + h - 2:
            break
        draw.line([(x + 10 + (i % 2) * 40, wy), (x + w - 10 - (i % 2) * 30, wy)],
                  fill=NAVY_LIGHT, width=2)
    # Ship hull + superstructure
    hx0, hx1 = x + w * 0.30, x + w * 0.82
    hy = y + h * 0.52
    draw.polygon([(hx0, hy), (hx1, hy), (hx1 - 26, hy + 26), (hx0 + 14, hy + 26)], fill=(52, 58, 66))
    draw.rectangle([hx0 + 60, hy - 26, hx0 + 150, hy], fill=(52, 58, 66))
    draw.rectangle([hx0 + 84, hy - 44, hx0 + 104, hy - 26], fill=(52, 58, 66))
    # Explosion burst above the ship, inside the sky
    bx, by = hx0 + 105, y + 20
    burst(draw, bx, by, 16, CRIMSON)
    burst(draw, bx, by, 10, GOLD)
    star(draw, bx, by, 6, 3, WHITE)
    # Drone dot with dotted trail
    dx, dy = x + w - 60, y + 12
    draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=CRIMSON)
    draw.line([(dx, dy + 8), (bx + 12, by - 8)], fill=CRIMSON, width=2)
    tf = font(SANS_BLACK, 16)
    draw.text((x + 12, y + 10), "BENGHAZI · LIBYA", font=tf, fill=NAVY)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


def capitol_graphic(draw, box):
    """US Capitol dome with a big 258 and stars (fits a 68px strip)."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=PAPER_PANEL)
    cx = x + w / 2
    # Dome
    draw.pieslice([cx - 40, y + 2, cx + 40, y + 46], start=180, end=360, fill=NAVY)
    draw.rectangle([cx - 40, y + 24, cx + 40, y + 30], fill=NAVY)
    draw.rectangle([cx - 2, y, cx + 2, y + 6], fill=NAVY)
    # Columns
    for i in range(5):
        colx = cx - 46 + i * 21
        draw.rectangle([colx, y + 32, colx + 9, y + h - 10], fill=NAVY)
    draw.rectangle([cx - 52, y + h - 10, cx + 52, y + h - 4], fill=CRIMSON)
    # 258 badge on the right
    bf = font(SANS_BLACK, 30)
    draw.text((x + w - 96, y + 6), "258", font=bf, fill=CRIMSON)
    sf = font(SANS_BLACK, 12)
    draw.text((x + w - 96, y + 42), "SEATS", font=sf, fill=NAVY)
    # Stars
    star(draw, x + 20, y + 16, 7, 3, GOLD)
    star(draw, x + w - 20, y + h - 14, 7, 3, GOLD)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


def chart_graphic(draw, box):
    """Falling market line on a navy field."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    for gy in range(1, 4):
        yy = y + h * gy / 4
        draw.line([(x + 8, yy), (x + w - 8, yy)], fill=NAVY_LIGHT, width=1)
    pts = [(x + 14, y + 12), (x + w * 0.28, y + 18), (x + w * 0.48, y + h * 0.42),
           (x + w * 0.66, y + h * 0.52), (x + w * 0.86, y + h - 14)]
    draw.line(pts, fill=CRIMSON, width=5)
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=GOLD)
    # Down arrow head at the end
    ex, ey = pts[-1]
    draw.polygon([(ex + 2, ey - 12), (ex + 16, ey + 2), (ex - 10, ey + 6)], fill=CRIMSON)
    tf = font(SANS_BLACK, 20)
    draw.text((x + 16, y + h - 32), "S&P 500  -3.7%", font=tf, fill=GOLD)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


def mercury_graphic(draw, box):
    """BepiColombo probe in orbit around Mercury, Sun blazing."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    # Stars (kept clear of the Sun at top left)
    for sx, sy, sr in [(90, 40, 2), (150, 14, 3), (210, 48, 2),
                       (280, 22, 2), (340, 44, 3), (400, 16, 2), (120, 60, 2)]:
        draw.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=WHITE)
    # Sun, top left
    sx, sy = x + 36, y + 28
    burst(draw, sx, sy, 24, GOLD)
    draw.ellipse([sx - 13, sy - 13, sx + 13, sy + 13], fill=GOLD)
    # Mercury: cratered disc, lower left
    mx, my = x + 84, y + h - 34
    draw.ellipse([mx - 26, my - 26, mx + 26, my + 26], fill=(176, 160, 140))
    draw.ellipse([mx - 12, my - 16, mx - 2, my - 6], fill=(140, 126, 110))
    draw.ellipse([mx + 4, my + 4, mx + 16, my + 16], fill=(140, 126, 110))
    draw.ellipse([mx + 8, my - 18, mx + 16, my - 10], fill=(140, 126, 110))
    # Orbit arc (kept inside the box)
    draw.arc([mx - 30, my - 30, mx + 30, my + 30], start=200, end=60, fill=GOLD, width=2)
    # Probe: body + solar panels on the arc, inside the box
    px, py = mx + 27, my - 13
    draw.rectangle([px - 8, py - 6, px + 8, py + 6], fill=WHITE)
    draw.rectangle([px - 30, py - 4, px - 10, py + 4], fill=(120, 140, 170))
    draw.rectangle([px + 10, py - 4, px + 30, py + 4], fill=(120, 140, 170))
    tf = font(SANS_BLACK, 15)
    draw.text((x + w - 132, y + h - 30), "MERCURY", font=tf, fill=GOLD)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


# ------------------------------------------------------------------- panels

def panel(draw, x, y, w, row_h, graphic, headline, sub):
    """Graphic strip on top, then headline, then a 2-line summary."""
    art_h = 68
    graphic(draw, (x, y, w, art_h))
    cy = y + art_h + 7
    hf, hlines = fit_wrapped(draw, headline, SERIF_BLACK, w, 2, 25, 17)
    cy = draw_lines(draw, hlines, hf, x, cy, NAVY, lh=line_h(hf, 1.2))
    sf, slines = fit_wrapped(draw, sub, SANS, w, 3, 16, 12)
    draw_lines(draw, slines, sf, x, cy + 2, NAVY, lh=line_h(sf, 1.18))
    return y + row_h


def main():
    page = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(page)
    cx = W // 2

    # --- Masthead -------------------------------------------------------
    draw.line([(MARGIN, 26), (W - MARGIN, 26)], fill=NAVY, width=2)
    mf = fit_one_line(draw, "THE WORLD TODAY", SERIF_BLACK, CW, 104)
    y = 36
    draw.text((cx - text_w(draw, "THE WORLD TODAY", mf) / 2, y),
              "THE WORLD TODAY", font=mf, fill=NAVY)
    y += line_h(mf, 1.04)
    draw.rectangle([MARGIN, y + 2, W - MARGIN, y + 8], fill=CRIMSON)
    y += 16

    # --- Date line ------------------------------------------------------
    df = fit_one_line(draw, "SUNDAY · 22 NOVEMBER 2026", SANS_BLACK, CW - 40, 34)
    y = draw_tracked(draw, "SUNDAY · 22 NOVEMBER 2026", df, cx, y, NAVY, tracking=3)
    draw.line([(MARGIN, y + 2), (W - MARGIN, y + 2)], fill=NAVY, width=2)
    y += 14

    # --- Hero -----------------------------------------------------------
    hero_h = 186
    hero_globe(draw, (MARGIN, y, CW, hero_h))
    y += hero_h + 10
    hf = fit_one_line(draw, "COP31 COLLAPSES WITH NO DEAL", SERIF_BLACK, CW, 52)
    draw.text((cx - text_w(draw, "COP31 COLLAPSES WITH NO DEAL", hf) / 2, y),
              "COP31 COLLAPSES WITH NO DEAL", font=hf, fill=NAVY)
    y += line_h(hf, 1.06) + 2
    sf, slines = fit_wrapped(
        draw,
        "Antalya talks end after two days of overtime as the EU rejects a draft with no mention "
        "of fossil fuels — the longest climate summit on record closes with no agreement",
        SANS_BOLD, CW, 2, 23, 15)
    y = draw_lines(draw, slines, sf, 0, y, NAVY, lh=line_h(sf, 1.16), anchor_center_x=cx)
    y += 8
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=NAVY, width=2)
    y += 12

    # --- Story rows -----------------------------------------------------
    ticker_h = 106
    rows_top = y
    row_h = (H - ticker_h - rows_top - 14) // 2
    col_w = (CW - 48) // 2
    col2_x = MARGIN + col_w + 48
    div_x = MARGIN + col_w + 24

    panel(draw, MARGIN, rows_top, col_w, row_h, ship_graphic,
          "DRONE SINKS RUSSIAN WARSHIP OFF LIBYA",
          "Suspected Ukrainian sea drone hits the corvette Merkury at Benghazi; a second ship, Maltese-flagged, is also struck")
    panel(draw, col2_x, rows_top, col_w, row_h, capitol_graphic,
          "DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE 1992",
          "At least 258 seats after a North Carolina recount win — the largest majority in three decades")
    draw.line([(div_x, rows_top + 4), (div_x, rows_top + row_h - 6)], fill=NAVY, width=1)

    row2_y = rows_top + row_h + 14
    draw.line([(MARGIN, row2_y - 8), (W - MARGIN, row2_y - 8)], fill=NAVY, width=1)
    panel(draw, MARGIN, row2_y, col_w, row_h, chart_graphic,
          "AI SELL-OFF DEEPENS AS STOCKS SLIDE",
          "S&P 500 falls 3.7% into correction and Japan's Nikkei drops 5.06% as investors dump AI shares")
    panel(draw, col2_x, row2_y, col_w, row_h, mercury_graphic,
          "BEPICOLOMBO ENTERS ORBIT AROUND MERCURY",
          "European-Japanese probe becomes only the second spacecraft to orbit the planet closest to the Sun")
    draw.line([(div_x, row2_y + 4), (div_x, row2_y + row_h - 6)], fill=NAVY, width=1)

    # --- Ticker ---------------------------------------------------------
    ty = H - ticker_h
    draw.rectangle([0, ty, W, H], fill=NAVY)
    draw.rectangle([0, ty, W, ty + 5], fill=CRIMSON)
    ticker = ("IN BRIEF — Mexico captures cartel boss 'El Chapo Isidro' in a Sinaloa raid that leaves 11 dead · "
              "Candy factory fire in Indonesia kills 3, dozens missing · "
              "Two tankers hit near the Strait of Hormuz · "
              "Russian drone hits an apartment block in Dymer, 14 missing · "
              "Poland confirms the missiles that fell on its soil were Russian Kh-101s")
    tf, tlines = fit_wrapped(draw, ticker, SANS_BOLD, CW, 3, 20, 13)
    total_h = line_h(tf, 1.25) * len(tlines)
    draw_lines(draw, tlines, tf, MARGIN, ty + (ticker_h - total_h) // 2 + 2,
               CREAM, lh=line_h(tf, 1.25))

    page.save(OUT, optimize=True)
    size = OUT.stat().st_size
    print(f"saved {OUT} {page.size} {size} bytes")
    if size > 1024 * 1024:
        q = page.quantize(colors=256, method=Image.MEDIANCUT)
        q.save(OUT, optimize=True)
        print(f"quantized -> {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
