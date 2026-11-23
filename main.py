#!/usr/bin/env python3
"""The World Today - 22 November 2026: a one-image newspaper front page.

Draws the day's world news with Pillow shapes and text only: a masthead,
one hero story, four panels and a news ticker. No network access, no
timestamps, no randomness, so running it twice writes identical bytes.

Layout (1024 x 1024):
  masthead band -> date strip -> hero headline + drawn art -> 2x2 panels
  -> ticker band -> footer line.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (22, 22, 22)
NAVY = (20, 33, 61)
RED = (158, 32, 32)
GREY = (96, 92, 82)
LIGHT_GREY = (200, 194, 178)
BLACK = (12, 12, 12)
WHITE = (255, 255, 255)
SUN = (233, 161, 59)
SKY_TOP = (245, 183, 110)
SKY_BOTTOM = (250, 226, 178)
GROUND = (61, 44, 30)
CLOUD = (128, 124, 112)

MARGIN = 32
CONTENT_W = W - 2 * MARGIN

FONT_DIRS = (
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/local/share/fonts",
)


def load_font(filename, size):
    """Try a named font file, fall back to Pillow's built-in bitmap font."""
    for folder in FONT_DIRS:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


SERIF_BOLD = lambda s: load_font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: load_font("DejaVuSerif.ttf", s)
SANS_BOLD = lambda s: load_font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: load_font("DejaVuSans.ttf", s)


def wrap(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered_lines(draw, lines, font, cx, y, fill, leading):
    """Draw lines centred on cx, top to bottom; returns the next y."""
    for line in lines:
        width = draw.textlength(line, font=font)
        draw.text((cx - width / 2, y), line, font=font, fill=fill)
        y += leading
    return y


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_masthead(draw):
    """Dark navy band with the paper's name, then the date strip."""
    draw.rectangle([0, 0, W, 118], fill=NAVY)
    title_font = SERIF_BOLD(62)
    title = "THE WORLD TODAY"
    tw = draw.textlength(title, font=title_font)
    draw.text(((W - tw) / 2, 26), title, font=title_font, fill=WHITE)
    draw.rectangle([0, 118, W, 122], fill=RED)
    date_font = SANS_BOLD(26)
    date = "SUNDAY, 22 NOVEMBER 2026"
    dw = draw.textlength(date, font=date_font)
    draw.text(((W - dw) / 2, 136), date, font=date_font, fill=INK)
    draw.line([MARGIN, 176, W - MARGIN, 176], fill=INK, width=2)


def draw_hero(draw):
    """Hero headline, sub-headline and a drawn summit scene."""
    cx = W / 2
    head_font = SERIF_BOLD(44)
    lines = wrap(draw, "COP31 TALKS COLLAPSE WITH NO DEAL", head_font, CONTENT_W)
    y = draw_centered_lines(draw, lines, head_font, cx, 190, INK, 54)
    sub_font = SANS(21)
    sub = (
        "Antalya summit ends without agreement as fossil-fuel "
        "phase-out is left out of the final text"
    )
    sub_lines = wrap(draw, sub, sub_font, CONTENT_W - 40)
    y = draw_centered_lines(draw, sub_lines, sub_font, cx, y + 8, GREY, 28)

    # Drawn art panel: hazy sun over cracked ground. Its top follows the
    # sub-headline so no line is ever covered by the panel.
    ax0 = MARGIN
    ax1 = W - MARGIN
    ay0 = y + 10
    ay1 = ay0 + 104
    bands = 6
    for i in range(bands):
        colour = lerp(SKY_TOP, SKY_BOTTOM, i / (bands - 1))
        band_y0 = ay0 + (ay1 - ay0) * i // bands
        band_y1 = ay0 + (ay1 - ay0) * (i + 1) // bands
        draw.rectangle([ax0, band_y0, ax1, band_y1], fill=colour)
    # Sun with rays, kept inside the panel.
    import math

    sun_cx, sun_cy, sun_r = ax0 + 180, ay0 + 46, 36
    for k in range(12):
        angle = k * 30
        x0 = sun_cx + int(44 * math.cos(math.radians(angle)))
        y0 = sun_cy + int(44 * math.sin(math.radians(angle)))
        x1 = sun_cx + int(52 * math.cos(math.radians(angle)))
        y1 = sun_cy + int(52 * math.sin(math.radians(angle)))
        draw.line([x0, y0, x1, y1], fill=SUN, width=5)
    draw.ellipse(
        [sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
        fill=SUN,
    )
    # Clouds drifting across the sky.
    draw.ellipse([ax0 + 220, ay0 + 18, ax0 + 300, ay0 + 54], fill=CLOUD)
    draw.ellipse([ax0 + 270, ay0 + 32, ax0 + 360, ay0 + 64], fill=CLOUD)
    draw.ellipse([ax0 + 530, ay0 + 16, ax0 + 610, ay0 + 50], fill=CLOUD)
    # Cracked ground.
    draw.rectangle([ax0, ay1 - 30, ax1, ay1], fill=GROUND)
    crack = [
        (ax0 + 120, ay1 - 30),
        (ax0 + 180, ay1 - 18),
        (ax0 + 240, ay1 - 28),
        (ax0 + 320, ay1 - 12),
        (ax0 + 400, ay1 - 24),
        (ax0 + 470, ay1 - 10),
        (ax0 + 560, ay1 - 26),
        (ax0 + 650, ay1 - 14),
        (ax0 + 760, ay1 - 28),
        (ax0 + 860, ay1 - 16),
        (ax1, ay1 - 24),
    ]
    draw.line(crack, fill=PAPER, width=3)
    draw.rectangle([ax0, ay0, ax1, ay1], outline=INK, width=2)
    cap_font = SERIF(17)
    caption = "Climate talks in Antalya, Turkiye, broke down on Sunday."
    cw = draw.textlength(caption, font=cap_font)
    draw.text(((W - cw) / 2, ay1 + 6), caption, font=cap_font, fill=GREY)
    return ay1 + 30


def draw_icon(draw, kind, x, y):
    """Small line icon for a panel, drawn in a 56x56 box at (x, y)."""
    if kind == "ship":
        draw.polygon(
            [(x, y + 34), (x + 54, y + 34), (x + 46, y + 50), (x + 8, y + 50)],
            fill=NAVY,
        )
        draw.line([x + 27, y + 34, x + 27, y + 6], fill=NAVY, width=3)
        draw.polygon([(x + 27, y + 6), (x + 44, y + 12), (x + 27, y + 18)], fill=RED)
        draw.line([x, y + 54, x + 54, y + 54], fill=NAVY, width=2)
    elif kind == "dome":
        draw.arc([x + 10, y + 6, x + 44, y + 34], start=180, end=360, fill=NAVY, width=3)
        draw.line([x + 10, y + 34, x + 44, y + 34], fill=NAVY, width=3)
        draw.rectangle([x + 6, y + 34, x + 48, y + 40], fill=NAVY)
        for col in (x + 12, x + 24, x + 36):
            draw.line([col, y + 40, col, y + 50], fill=NAVY, width=3)
        draw.rectangle([x + 4, y + 50, x + 50, y + 54], fill=NAVY)
    elif kind == "chart":
        draw.line([x + 6, y + 6, x + 6, y + 50], fill=NAVY, width=3)
        draw.line([x + 6, y + 50, x + 52, y + 50], fill=NAVY, width=3)
        draw.line(
            [(x + 10, y + 14), (x + 22, y + 24), (x + 32, y + 20), (x + 48, y + 42)],
            fill=RED,
            width=3,
        )
        draw.polygon(
            [(x + 48, y + 42), (x + 40, y + 40), (x + 46, y + 48)], fill=RED
        )
    elif kind == "planet":
        draw.ellipse([x + 12, y + 12, x + 42, y + 42], fill=NAVY)
        draw.ellipse([x + 2, y + 20, x + 52, y + 36], outline=RED, width=3)
        draw.ellipse([x + 44, y + 4, x + 50, y + 10], fill=SUN)


def draw_panel(draw, box, colour, kicker, icon, headline, sub):
    """One news panel: coloured kicker bar, icon, headline and sub-line."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)
    draw.rectangle([x0, y0, x1, y0 + 32], fill=colour)
    kick_font = SANS_BOLD(19)
    draw.text((x0 + 12, y0 + 5), kicker, font=kick_font, fill=WHITE)
    draw_icon(draw, icon, x0 + 14, y0 + 48)
    tx = x0 + 84
    tw = x1 - tx - 12
    head_font = SANS_BOLD(24)
    lines = wrap(draw, headline, head_font, tw)[:3]
    y = y0 + 46
    for line in lines:
        draw.text((tx, y), line, font=head_font, fill=INK)
        y += 30
    sub_font = SANS(18)
    sub_lines = wrap(draw, sub, sub_font, tw)[:2]
    for line in sub_lines:
        draw.text((tx, y), line, font=sub_font, fill=GREY)
        y += 24


def draw_panels(draw, top):
    """2x2 grid of the day's other big stories."""
    gap = 16
    pw = (CONTENT_W - gap) // 2
    ph = 178
    panels = [
        (
            (158, 32, 32),
            "UKRAINE WAR",
            "ship",
            "Ukrainian drone hits Russian warship Merkury at Benghazi",
            "Second Russian ship hit in this campaign.",
        ),
        (
            NAVY,
            "US POLITICS",
            "dome",
            "Democrats take 258+ House seats",
            "Largest House majority since 1992.",
        ),
        (
            (138, 90, 0),
            "MARKETS",
            "chart",
            "AI sell-off deepens",
            "S&P 500 down 3.7%, Nikkei down 5.06%.",
        ),
        (
            (46, 74, 58),
            "SPACE",
            "planet",
            "BepiColombo enters orbit around Mercury",
            "European-Japanese probe begins its science orbit.",
        ),
    ]
    for i, (colour, kicker, icon, headline, sub) in enumerate(panels):
        col = i % 2
        row = i // 2
        x0 = MARGIN + col * (pw + gap)
        y0 = top + row * (ph + gap)
        draw_panel(draw, (x0, y0, x0 + pw, y0 + ph), colour, kicker, icon, headline, sub)
    return top + 2 * ph + gap


def draw_ticker(draw, top):
    """Black ticker band with the day's remaining headlines, three rows."""
    band_h = 90
    draw.rectangle([0, top, W, top + band_h], fill=BLACK)
    label_font = SANS_BOLD(20)
    draw.rectangle([MARGIN, top + 8, MARGIN + 92, top + 30], fill=RED)
    draw.text((MARGIN + 12, top + 10), "LATEST", font=label_font, fill=WHITE)
    tick_font = SANS_BOLD(19)
    rows = [
        "EL CHAPO ISIDRO CAPTURED IN SINALOA  |  INDONESIA CANDY-FACTORY FIRE",
        "TANKERS HIT NEAR HORMUZ  |  DYMER STRIKE: 14 MISSING",
        "POLAND CONFIRMS MISSILES WERE RUSSIAN KH-101S",
    ]
    for i, row in enumerate(rows):
        draw.text((MARGIN + 112, top + 8 + i * 26), row, font=tick_font, fill=WHITE)
    return top + band_h


def build():
    """Draw the whole front page and return the image."""
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, W - 9, H - 9], outline=INK, width=2)
    draw_masthead(draw)
    after_hero = draw_hero(draw)
    after_panels = draw_panels(draw, after_hero + 8)
    after_ticker = draw_ticker(draw, after_panels + 12)
    foot_font = SANS(16)
    footer = "THE WORLD TODAY - 22 NOVEMBER 2026"
    fw = draw.textlength(footer, font=foot_font)
    draw.text(((W - fw) / 2, after_ticker + 8), footer, font=foot_font, fill=GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    build().save(path, "PNG")
    print("wrote", path)


if __name__ == "__main__":
    main()
