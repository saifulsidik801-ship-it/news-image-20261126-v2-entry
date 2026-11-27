#!/usr/bin/env python3
"""news-image-20261126 v4 — one-day front page, drawn in code (PIL only, no photos).
36 stories: 3 heroes + 10 mids + 23 list. All Nov 26 2026 only.
v4: every card carries a REAL drawn scene (sky/ground/foreground, 3-5 elements);
text renders after art; map is bigger with numbered pins + place labels."""
from PIL import Image, ImageDraw, ImageFont
import math, random

W, H = 1024, 1024
FD = "/usr/share/fonts/truetype/dejavu/"
def F(name, s): return ImageFont.truetype(FD + name, s)
SERIF_B = lambda s: F("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: F("DejaVuSerif.ttf", s)
SANS_B = lambda s: F("DejaVuSans-Bold.ttf", s)
SANS = lambda s: F("DejaVuSans.ttf", s)

NAVY = (15, 42, 74); PAPER = (247, 243, 232); RED = (185, 28, 28)
INK = (20, 20, 20); GREY = (90, 90, 90); GOLD = (200, 160, 40)

REGION = {"Europe": (30, 80, 160), "East Asia": (180, 40, 40), "N. America": (0, 110, 90),
          "South Asia": (200, 120, 0), "Oceania": (0, 130, 160), "Middle East": (120, 60, 140),
          "Africa": (160, 90, 20), "SE Asia": (60, 140, 60), "Latin Am": (200, 60, 120),
          "World": (100, 100, 100)}

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def wrap(txt, font, maxw):
    words = txt.split(); lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def txt(x, y, s, font, fill=INK, anchor="la"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)

def fit_font(s, maxw, size, bold=True):
    f = SANS_B(size) if bold else SANS(size)
    while size > 7 and d.textlength(s, font=f) > maxw:
        size -= 1
        f = SANS_B(size) if bold else SANS(size)
    return f

def badge(x, y, label, fill):
    f = SANS_B(11)
    w = d.textlength(label, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 16], 3, fill=fill)
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w

def vgrad(dr, x0, y0, x1, y1, top, bot):
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / (h - 1)
        col = tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3))
        dr.line([x0, y0 + i, x1, y0 + i], fill=col)

def buildings(dr, x0, y0, x1, y1, seed, base, wincol, lit=0.5, winw=3, winh=4):
    rnd = random.Random(seed)
    x = x0
    while x < x1 - 8:
        bw = rnd.randint(16, 34); bh = rnd.randint(max(10, (y1 - y0) // 3), max(11, (y1 - y0) - 4))
        dr.rectangle([x, y1 - bh, x + bw, y1], fill=base)
        for wy in range(y1 - bh + 5, y1 - 4, 9):
            for wx in range(x + 3, x + bw - 3, 7):
                if rnd.random() < lit:
                    dr.rectangle([wx, wy, wx + winw, wy + winh], fill=wincol)
        x += bw + 2

def flame(dr, x, y, s=1.0):
    w = int(5 * s); h = int(9 * s)
    dr.polygon([(x, y - h), (x + w, y), (x, y + 2), (x - w, y)], fill=(255, 120, 20))
    dr.ellipse([x - int(2 * s), y - int(3 * s), x + int(2 * s), y + int(3 * s)], fill=(255, 210, 80))

def candle(dr, x, y, s=1.0):
    dr.ellipse([x - int(6 * s), y - int(4 * s), x + int(6 * s), y + int(2 * s)], fill=(200, 120, 50))
    flame(dr, x, y - int(5 * s), s)

def burst(dr, x, y, r, col):
    for ang in range(0, 360, 30):
        dx, dy = int(r * math.cos(math.radians(ang))), int(r * math.sin(math.radians(ang)))
        dr.line([x, y, x + dx, y + dy], fill=col, width=2)
    dr.ellipse([x - r // 3, y - r // 3, x + r // 3, y + r // 3], fill=(255, 240, 150))

def person(dr, x, y, h, shirt, pants, skin=(220, 180, 140)):
    dr.ellipse([x - 4, y - h - 6, x + 4, y - h + 2], fill=skin)
    dr.rectangle([x - 4, y - h + 2, x + 4, y - h // 2], fill=shirt)
    dr.rectangle([x - 4, y - h // 2, x + 4, y], fill=pants)

def pill(dr, x0, y0, x1, y1, fill, label, size=11, fg=(255, 255, 255)):
    dr.rounded_rectangle([x0, y0, x1, y1], 4, fill=fill)
    f = SANS_B(size)
    tw = d.textlength(label, font=f)
    d.text(((x0 + x1 - tw) / 2, y0 + (y1 - y0 - size) / 2 - 1), label, font=f, fill=fg)

def num_badge(dr, x, y, n, size=24):
    dr.rounded_rectangle([x, y, x + size, y + size], 4, fill=(255, 255, 255), outline=RED, width=2)
    f = SANS_B(size - 9)
    tw = d.textlength(str(n), font=f)
    d.text((x + (size - tw) / 2, y + (size - (size - 9)) / 2 - 1), str(n), font=f, fill=RED)

# ---------------------------------------------------------------- scenes
def scene(dr, kind, x0, y0, x1, y1):
    """Draw a REAL scene inside box: sky, ground, foreground, 3-5 elements."""
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if kind == "parade":
        # Storm sky over a NYC avenue; deflated balloon lowered by crane truck.
        vgrad(dr, x0, y0, x1, y1, (42, 58, 92), (110, 132, 165))
        rnd = random.Random(11)
        for _ in range(6):  # storm clouds
            ccx = rnd.randint(x0, x1 - 60); ccy = rnd.randint(y0, y0 + 22)
            dr.ellipse([ccx, ccy, ccx + 70, ccy + 16], fill=(60, 72, 100))
        for _ in range(26):  # rain streaks
            rx = rnd.randint(x0, x1); ry = rnd.randint(y0, y0 + h - 30)
            dr.line([rx, ry, rx - 6, ry + 14], fill=(190, 205, 225), width=2)
        buildings(dr, x0, y0 + 34, x0 + 62, y1 - 34, 21, (32, 46, 78), (255, 210, 90), 0.55)
        buildings(dr, x1 - 62, y0 + 30, x1, y1 - 34, 33, (28, 42, 72), (255, 210, 90), 0.55)
        # street in perspective
        dr.polygon([(x0 + 62, y0 + 62), (x1 - 62, y0 + 62), (x1 - 30, y1 - 34), (x0 + 30, y1 - 34)],
                   fill=(52, 56, 66))
        for i in range(4):
            yy = y0 + 70 + i * 14
            ww = 4 + i * 3
            dr.rectangle([cx - ww // 2, yy, cx + ww // 2, yy + 5], fill=(230, 200, 60))
        # deflated balloon: sagging red shape with wrinkles + big 100
        dr.ellipse([cx - 58, y0 + 6, cx + 58, y0 + 46], fill=(215, 45, 45))
        dr.ellipse([cx - 40, y0 + 32, cx + 40, y0 + 60], fill=(200, 35, 35))
        dr.ellipse([cx - 58, y0 + 38, cx - 30, y0 + 58], fill=(200, 35, 35))
        dr.ellipse([cx + 30, y0 + 38, cx + 58, y0 + 58], fill=(200, 35, 35))
        dr.arc([cx - 44, y0 + 12, cx + 44, y0 + 42], 20, 160, fill=(160, 25, 25), width=2)
        dr.arc([cx - 28, y0 + 18, cx + 28, y0 + 48], 20, 160, fill=(160, 25, 25), width=2)
        txt(cx, y0 + 12, "100", SERIF_B(22), (255, 255, 255), "ma")
        # ropes from balloon to crane + handlers
        dr.line([cx - 40, y0 + 54, cx - 78, y1 - 52], fill=(240, 240, 240), width=2)
        dr.line([cx + 40, y0 + 54, cx + 78, y1 - 52], fill=(240, 240, 240), width=2)
        dr.line([cx - 16, y0 + 58, cx - 30, y1 - 52], fill=(240, 240, 240), width=2)
        dr.line([cx + 16, y0 + 58, cx + 30, y1 - 52], fill=(240, 240, 240), width=2)
        # crane truck (right) + handler crew (left)
        dr.rectangle([x1 - 108, y1 - 58, x1 - 34, y1 - 36], fill=(240, 190, 40))
        dr.rectangle([x1 - 108, y1 - 72, x1 - 84, y1 - 58], fill=(240, 190, 40))
        dr.rectangle([x1 - 104, y1 - 68, x1 - 88, y1 - 60], fill=(180, 230, 240))
        dr.line([x1 - 96, y1 - 70, cx + 56, y0 + 44], fill=(220, 170, 30), width=4)
        for wx in (x1 - 100, x1 - 76, x1 - 52):
            dr.ellipse([wx, y1 - 36, wx + 12, y1 - 24], fill=(25, 25, 25))
        for i, px in enumerate((x0 + 44, x0 + 58, x0 + 72)):
            person(dr, px, y1 - 36, 16, (30, 90, 160) if i % 2 else (200, 60, 40), (40, 40, 40))
        # crowd barriers along the bottom, above the banner
        for bx in range(x0 + 6, x1 - 6, 34):
            dr.rectangle([bx, y1 - 34, bx + 28, y1 - 22], fill=(200, 200, 200), outline=(120, 120, 120))
            dr.rectangle([bx, y1 - 34, bx + 9, y1 - 22], fill=(240, 120, 30))
        dr.rectangle([x0, y1 - 20, x1, y1], fill=(200, 40, 40))
        txt(cx, y1 - 17, "POSTPONED TO SATURDAY", SANS_B(13), (255, 255, 255), "ma")
    elif kind == "riyadh":
        # Night skyline, two interceptor arcs, explosion bursts, searchlights.
        vgrad(dr, x0, y0, x1, y1, (8, 16, 40), (28, 44, 80))
        rnd = random.Random(5)
        for _ in range(30):
            sx = rnd.randint(x0 + 2, x1 - 2); sy = rnd.randint(y0 + 2, y0 + 40)
            dr.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        buildings(dr, x0, y0 + 52, x1, y1, 17, (30, 45, 80), (255, 210, 90), 0.6)
        # Kingdom Centre tower with arch
        tx = x1 - 78
        dr.rectangle([tx, y0 + 34, tx + 26, y1], fill=(38, 55, 95))
        dr.polygon([(tx, y0 + 34), (tx + 26, y0 + 34), (tx + 13, y0 + 20)], fill=(38, 55, 95))
        dr.ellipse([tx + 6, y0 + 40, tx + 20, y0 + 58], fill=(10, 18, 42))
        for wy in range(y0 + 62, y1 - 4, 10):
            dr.rectangle([tx + 4, wy, tx + 8, wy + 4], fill=(255, 210, 90))
            dr.rectangle([tx + 18, wy, tx + 22, wy + 4], fill=(255, 210, 90))
        # searchlight beams
        for bx in (x0 + 40, x0 + 120):
            dr.polygon([(bx, y1), (bx + 8, y1), (bx + 34, y0 + 6), (bx + 22, y0 + 6)], fill=(200, 210, 140))
        # interceptor arcs + bursts
        dr.arc([x0 + 8, y0 + 2, x1 - 40, y0 + 78], 200, 335, fill=(255, 200, 60), width=3)
        dr.arc([x0 + 46, y0 + 14, x1 - 8, y0 + 92], 205, 325, fill=(255, 130, 60), width=3)
        burst(dr, x1 - 52, y0 + 24, 16, (255, 200, 80))
        burst(dr, x0 + 62, y0 + 36, 13, (255, 220, 100))
        for r, col in [(22, (255, 120, 30)), (13, (255, 180, 60)), (6, (255, 240, 150))]:
            dr.ellipse([x1 - 52 - r, y0 + 24 - r, x1 - 52 + r, y0 + 24 + r], fill=col)
        # alert lights on rooftops
        for ax in (x0 + 30, x0 + 150, x1 - 110):
            dr.ellipse([ax, y0 + 48, ax + 5, y0 + 53], fill=(255, 60, 60))
        dr.rounded_rectangle([x0 + 34, y0 + 5, x0 + 162, y0 + 23], 3, fill=(10, 18, 42))
        txt(x0 + 38, y0 + 8, "2 MISSILES DOWN", SANS_B(12), (255, 220, 80), "la")
    elif kind == "mumbai":
        # Gateway of India at dusk, rows of lit candles, marigolds, flags.
        vgrad(dr, x0, y0, x1, y1, (235, 165, 85), (252, 222, 165))
        dr.ellipse([x1 - 46, y0 + 8, x1 - 14, y0 + 40], fill=(255, 225, 140))
        # Gateway arch monument
        dr.rectangle([cx - 74, y0 + 30, cx + 74, y1 - 40], fill=(188, 138, 88))
        dr.rectangle([cx - 84, y0 + 24, cx + 84, y0 + 32], fill=(170, 118, 70))
        dr.ellipse([cx - 34, y0 + 8, cx + 34, y0 + 44], fill=(170, 118, 70))
        dr.ellipse([cx - 52, y0 + 18, cx - 40, y0 + 32], fill=(170, 118, 70))
        dr.ellipse([cx + 40, y0 + 18, cx + 52, y0 + 32], fill=(170, 118, 70))
        dr.polygon([(cx - 30, y1 - 40), (cx - 30, y0 + 52), (cx, y0 + 34), (cx + 30, y0 + 52), (cx + 30, y1 - 40)],
                   fill=(250, 222, 165))
        dr.ellipse([cx - 30, y0 + 34, cx + 30, y0 + 70], fill=(250, 222, 165))
        for px in (cx - 66, cx - 52, cx + 52, cx + 66):
            dr.rectangle([px, y0 + 44, px + 8, y1 - 40], fill=(160, 108, 62))
        txt(cx, y0 + 38, "26/11", SANS_B(11), (140, 70, 20), "ma")
        # tricolour flags flanking
        for fx in (x0 + 26, x1 - 26):
            dr.line([fx, y0 + 34, fx, y0 + 66], fill=(90, 60, 30), width=2)
            dr.rectangle([fx, y0 + 34, fx + 18, y0 + 40], fill=(255, 140, 40))
            dr.rectangle([fx, y0 + 40, fx + 18, y0 + 46], fill=(255, 255, 255))
            dr.rectangle([fx, y0 + 46, fx + 18, y0 + 52], fill=(20, 140, 60))
        # ground + marigolds + two rows of candles
        dr.rectangle([x0, y1 - 40, x1, y1], fill=(120, 82, 52))
        rnd = random.Random(9)
        for _ in range(14):
            mx = rnd.randint(x0 + 6, x1 - 6)
            dr.ellipse([mx, y1 - 38, mx + 5, y1 - 33], fill=(255, 160, 30))
            dr.ellipse([mx + 3, y1 - 36, mx + 8, y1 - 31], fill=(255, 210, 60))
        for i in range(9):
            candle(dr, x0 + 18 + i * 34, y1 - 22, 1.0)
        for i in range(8):
            candle(dr, x0 + 34 + i * 34, y1 - 8, 0.85)
    elif kind == "eu":
        vgrad(dr, x0, y0, x1, y1, (190, 215, 238), (228, 236, 244))
        # Berlaymont building
        dr.rectangle([x0 + 52, y0 + 14, x1 - 52, y1 - 16], fill=(120, 140, 168))
        dr.rectangle([x0 + 52, y0 + 14, x1 - 52, y0 + 20], fill=(90, 112, 142))
        for ry in range(y0 + 24, y1 - 18, 8):
            for wx in range(x0 + 58, x1 - 58, 10):
                dr.rectangle([wx, ry, wx + 6, ry + 4], fill=(220, 232, 244))
        # EU flag on the roof
        dr.line([cx, y0 + 2, cx, y0 + 14], fill=(60, 60, 60), width=2)
        dr.rectangle([cx, y0 + 2, cx + 20, y0 + 12], fill=(30, 60, 140))
        for i in range(6):
            a = math.radians(i * 60)
            dr.ellipse([cx + 10 + int(6 * math.cos(a)) - 1, y0 + 7 + int(4 * math.sin(a)) - 1,
                        cx + 10 + int(6 * math.cos(a)) + 1, y0 + 7 + int(4 * math.sin(a)) + 1], fill=(255, 215, 0))
        # round table with mini flags
        dr.ellipse([cx - 40, y1 - 18, cx + 40, y1 - 6], fill=(140, 95, 55))
        dr.rectangle([cx - 40, y1 - 12, cx + 40, y1 - 6], fill=(120, 80, 45))
        for i, col in enumerate([(30, 60, 140), (200, 40, 40), (255, 210, 60), (20, 140, 60), (200, 60, 120)]):
            fx = cx - 36 + i * 18
            dr.line([fx, y1 - 32, fx, y1 - 18], fill=(60, 60, 60), width=1)
            dr.rectangle([fx, y1 - 32, fx + 13, y1 - 25], fill=col)
        pill(dr, x1 - 52, y0 + 4, x1 - 4, y0 + 18, (30, 60, 140), "EU 27", 10)
    elif kind == "chess":
        dr.rectangle([x0, y0, x1, y1], fill=(148, 112, 72))
        for wx in (x0 + 4, x1 - 18):
            dr.rectangle([wx, y0 + 4, wx + 14, y0 + 30], fill=(240, 225, 180))
            dr.line([wx + 7, y0 + 4, wx + 7, y0 + 30], fill=(180, 150, 100), width=1)
        # board
        bs = 44; bx, by = x0 + 62, y0 + 6
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 0:
                    dr.rectangle([bx + c * bs // 8, by + r * bs // 8, bx + (c + 1) * bs // 8, by + (r + 1) * bs // 8],
                                 fill=(240, 230, 210))
                else:
                    dr.rectangle([bx + c * bs // 8, by + r * bs // 8, bx + (c + 1) * bs // 8, by + (r + 1) * bs // 8],
                                 fill=(90, 60, 40))
        dr.rectangle([bx, by, bx + bs, by + bs], outline=(60, 40, 25), width=2)
        # black king + white queen
        kx, ky = bx + 3 * bs // 8 + 3, by + 3 * bs // 8 + 3
        dr.ellipse([kx - 4, ky - 4, kx + 4, ky + 4], fill=(20, 20, 20))
        dr.rectangle([kx - 2, ky + 3, kx + 2, ky + 6], fill=(20, 20, 20))
        qx, qy = bx + 5 * bs // 8 + 3, by + 5 * bs // 8 + 3
        dr.ellipse([qx - 4, qy - 4, qx + 4, qy + 4], fill=(255, 255, 255), outline=(120, 120, 120))
        dr.rectangle([qx - 2, qy + 3, qx + 2, qy + 6], fill=(255, 255, 255), outline=(120, 120, 120))
        # chess clock (two dials)
        for dx in (x1 - 46, x1 - 26):
            dr.ellipse([dx, y0 + 12, dx + 16, y0 + 28], fill=(245, 240, 225), outline=(60, 40, 25))
            dr.line([dx + 8, y0 + 20, dx + 8, y0 + 14], fill=(20, 20, 20), width=1)
            dr.line([dx + 8, y0 + 20, dx + 12, y0 + 22], fill=(20, 20, 20), width=1)
        dr.rectangle([x0, y1 - 14, x1, y1], fill=(60, 40, 25))
        txt(cx, y1 - 12, "GAME 3 · 1–1", SANS_B(11), (255, 255, 255), "ma")
    elif kind == "bok":
        vgrad(dr, x0, y0, x1, y1, (215, 232, 244), (240, 244, 248))
        # bank building, left
        bx0, bx1 = x0 + 8, x0 + 88
        dr.polygon([(bx0 - 4, y0 + 22), (bx1 + 4, y0 + 22), ((bx0 + bx1) // 2, y0 + 8)], fill=(50, 80, 120))
        txt((bx0 + bx1) // 2, y0 + 11, "₩", SANS_B(10), (255, 255, 255), "ma")
        dr.rectangle([bx0, y0 + 22, bx1, y1 - 10], fill=(200, 210, 222))
        for i in range(4):
            dr.rectangle([bx0 + 6 + i * 20, y0 + 28, bx0 + 16 + i * 20, y1 - 10], fill=(255, 255, 255))
        dr.rectangle([bx0 - 4, y1 - 10, bx1 + 4, y1 - 6], fill=(160, 170, 185))
        dr.rectangle([bx0 - 8, y1 - 6, bx1 + 8, y1 - 2], fill=(140, 150, 165))
        # rising chart, right
        pts = [(x0 + 92, y1 - 16), (x0 + 116, y1 - 22), (x0 + 134, y1 - 30), (x0 + 156, y1 - 26),
               (x0 + 172, y1 - 40), (x1 - 10, y1 - 48)]
        dr.line(pts, fill=(20, 140, 60), width=3)
        dr.polygon([(x1 - 10, y1 - 48), (x1 - 22, y1 - 48), (x1 - 12, y1 - 56)], fill=(20, 140, 60))
        for px, py in pts[1:-1]:
            dr.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(20, 140, 60))
        pill(dr, x1 - 52, y0 + 4, x1 - 4, y0 + 18, (20, 140, 60), "3.25%", 10)
    elif kind == "kyiv":
        # ALL elements stay inside the card box with a margin — nothing may
        # touch or cross the frame (Sidik: "keluar kotak").
        vgrad(dr, x0, y0, x1, y1, (14, 22, 48), (30, 42, 75))
        rnd = random.Random(3)
        for _ in range(12):
            sx = rnd.randint(x0 + 6, x1 - 6); sy = rnd.randint(y0 + 6, y0 + 14)
            dr.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        # mall facade: sign band + glass front + entrance, all inside the box
        dr.rectangle([x0 + 8, y0 + 20, x1 - 8, y1 - 18], fill=(70, 60, 80))
        dr.rectangle([x0 + 8, y0 + 20, x1 - 8, y0 + 28], fill=(40, 36, 52))
        txt(cx, y0 + 21, "MALL", SANS_B(9), (255, 220, 90), "ma")
        for wx in range(x0 + 14, x1 - 14, 15):
            dr.rectangle([wx, y0 + 32, wx + 9, y0 + 41], fill=(255, 210, 90))
        for wx in range(x0 + 14, x1 - 14, 15):
            if (wx // 15) % 3 != 2:
                dr.rectangle([wx, y0 + 44, wx + 9, y0 + 52], fill=(255, 210, 90))
            else:
                dr.rectangle([wx, y0 + 44, wx + 9, y0 + 52], fill=(35, 30, 45))
        # entrance, centre
        dr.rectangle([cx - 11, y0 + 44, cx + 11, y1 - 18], fill=(200, 180, 140))
        dr.line([cx, y0 + 44, cx, y1 - 18], fill=(120, 100, 70), width=1)
        # fireball on the roof, right side — jagged flames, not a disc
        fx, fy = x1 - 36, y0 + 30
        dr.polygon([(fx - 12, fy + 4), (fx - 8, fy - 10), (fx - 3, fy - 2), (fx, fy - 14),
                    (fx + 4, fy - 3), (fx + 9, fy - 11), (fx + 12, fy + 4), (fx, fy + 10)],
                   fill=(255, 110, 25))
        for r, col in [(8, (255, 170, 40)), (5, (255, 215, 90)), (2, (255, 245, 170))]:
            dr.ellipse([fx - r, fy - r + 2, fx + r, fy + r + 2], fill=col)
        # embers + smoke plume, capped below the top edge
        for ex, ey in [(fx - 16, fy - 12), (fx + 14, fy - 14), (fx - 6, fy - 18), (fx + 8, fy - 20)]:
            dr.ellipse([ex - 1, ey - 1, ex + 1, ey + 1], fill=(255, 180, 60))
        for sx, sy, sr in [(x1 - 50, y0 + 12, 5), (x1 - 60, y0 + 9, 4), (x1 - 68, y0 + 12, 4)]:
            dr.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(115, 115, 120))
        # ground line
        dr.rectangle([x0 + 4, y1 - 18, x1 - 4, y1 - 16], fill=(25, 22, 38))
        # ambulance, foreground left — FULL body inside the frame
        ax = x0 + 10
        dr.rectangle([ax, y1 - 15, ax + 28, y1 - 5], fill=(245, 245, 245))
        dr.rectangle([ax + 28, y1 - 12, ax + 40, y1 - 5], fill=(245, 245, 245))
        dr.rectangle([ax + 30, y1 - 10, ax + 37, y1 - 7], fill=(170, 220, 240))
        dr.rectangle([ax + 8, y1 - 13, ax + 15, y1 - 6], fill=(220, 40, 40))
        dr.rectangle([ax + 11, y1 - 11, ax + 12, y1 - 8], fill=(255, 255, 255))
        dr.ellipse([ax + 4, y1 - 7, ax + 10, y1 - 1], fill=(25, 25, 25))
        dr.ellipse([ax + 30, y1 - 7, ax + 36, y1 - 1], fill=(25, 25, 25))
        dr.ellipse([ax + 13, y1 - 19, ax + 17, y1 - 15], fill=(255, 60, 60))
        dr.ellipse([ax + 19, y1 - 19, ax + 23, y1 - 15], fill=(60, 120, 255))
        pill(dr, x1 - 52, y1 - 17, x1 - 4, y1 - 3, (200, 40, 40), "4 HURT", 10)
    elif kind == "kim":
        vgrad(dr, x0, y0, x1, y1, (18, 18, 34), (40, 34, 60))
        rnd = random.Random(8)
        for _ in range(16):
            sx = rnd.randint(x0 + 2, x1 - 2); sy = rnd.randint(y0 + 2, y0 + 22)
            dr.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        # mountains
        dr.polygon([(x0, y1 - 22), (x0 + 40, y0 + 26), (x0 + 80, y1 - 22)], fill=(30, 34, 58))
        dr.polygon([(x0 + 60, y1 - 22), (x0 + 110, y0 + 18), (x0 + 160, y1 - 22)], fill=(24, 28, 50))
        # site buildings with lit windows
        dr.rectangle([x0 + 6, y0 + 34, x0 + 34, y1 - 22], fill=(70, 70, 85))
        for wy in range(y0 + 38, y1 - 24, 8):
            dr.rectangle([x0 + 10, wy, x0 + 14, wy + 4], fill=(255, 210, 90))
            dr.rectangle([x0 + 22, wy, x0 + 26, wy + 4], fill=(255, 210, 90))
        # launcher truck + missile
        lx0, ly = x1 - 92, y1 - 22
        dr.rectangle([lx0, ly - 12, lx0 + 62, ly], fill=(50, 90, 50))
        dr.rectangle([lx0 + 44, ly - 20, lx0 + 62, ly - 12], fill=(60, 100, 60))
        for wx in (lx0 + 8, lx0 + 26, lx0 + 44):
            dr.ellipse([wx, ly - 2, wx + 10, ly + 6], fill=(20, 20, 20))
        mx = lx0 + 22
        dr.polygon([(mx - 7, ly - 12), (mx - 7, y0 + 14), (mx, y0 + 4), (mx + 7, y0 + 14), (mx + 7, ly - 12)],
                   fill=(225, 225, 225))
        dr.rectangle([mx - 7, y0 + 22, mx + 7, y0 + 28], fill=(200, 40, 40))
        dr.rectangle([mx - 7, ly - 16, mx + 7, ly - 12], fill=(120, 120, 120))
        # red star
        sx, sy = x1 - 14, y0 + 12
        dr.polygon([(sx, sy - 6), (sx + 2, sy - 1), (sx + 6, sy), (sx + 2, sy + 2), (sx + 3, sy + 6),
                    (sx, sy + 3), (sx - 3, sy + 6), (sx - 2, sy + 2), (sx - 6, sy), (sx - 2, sy - 1)],
                   fill=(255, 220, 60))
        txt(x0 + 6, y0 + 4, "KCNA", SANS_B(10), (255, 255, 255), "la")
    elif kind == "school":
        vgrad(dr, x0, y0, x1, y1, (250, 235, 200), (235, 245, 210))
        dr.rectangle([x0, y1 - 16, x1, y1], fill=(120, 190, 110))
        # school building
        dr.rectangle([x0 + 8, y0 + 18, x0 + 74, y1 - 16], fill=(245, 235, 210))
        dr.polygon([(x0 + 4, y0 + 20), (x0 + 78, y0 + 20), (x0 + 41, y0 + 6)], fill=(200, 80, 60))
        dr.rectangle([x0 + 36, y1 - 30, x0 + 46, y1 - 16], fill=(120, 80, 50))
        for wx in (x0 + 14, x0 + 56):
            dr.rectangle([wx, y0 + 26, wx + 12, y0 + 36], fill=(170, 210, 235))
        # flag pole
        dr.line([x0 + 74, y0 + 6, x0 + 74, y0 + 20], fill=(90, 60, 30), width=2)
        dr.rectangle([x0 + 74, y0 + 6, x0 + 88, y0 + 11], fill=(20, 140, 60))
        dr.rectangle([x0 + 74, y0 + 11, x0 + 88, y0 + 16], fill=(255, 255, 255))
        # yellow school bus
        bx0, by = x0 + 92, y1 - 16
        dr.rectangle([bx0, by - 18, bx0 + 62, by], fill=(250, 200, 30))
        dr.rectangle([bx0 + 44, by - 18, bx0 + 62, by - 10], fill=(250, 200, 30))
        for wx in range(bx0 + 5, bx0 + 42, 12):
            dr.rectangle([wx, by - 15, wx + 8, by - 7], fill=(170, 220, 240))
        dr.ellipse([bx0 + 8, by - 2, bx0 + 16, by + 6], fill=(25, 25, 25))
        dr.ellipse([bx0 + 44, by - 2, bx0 + 52, by + 6], fill=(25, 25, 25))
        # figures + FREED placard
        pill(dr, x0 + 96, y0 + 4, x0 + 152, y0 + 18, (20, 120, 50), "FREED", 10)
        for i, px in enumerate((x0 + 108, x0 + 126, x0 + 144)):
            person(dr, px, y1 - 16, 14, (200, 60, 40) if i % 2 else (30, 90, 160), (40, 40, 40))
    elif kind == "tube":
        # ALL elements stay inside the card box with a margin — nothing may
        # touch or cross the frame (Sidik: "keluar kotak").
        dr.rectangle([x0, y0, x1, y1], fill=(38, 48, 66))
        # tunnel mouth, TOP THIRD only, fully inside the frame
        dr.ellipse([cx - 36, y0 + 4, cx + 36, y0 + 26], fill=(24, 32, 48))
        dr.ellipse([cx - 36, y0 + 4, cx + 36, y0 + 26], outline=(95, 105, 125), width=2)
        dr.ellipse([cx - 22, y0 + 10, cx + 22, y0 + 26], fill=(16, 22, 36))
        # platform
        dr.rectangle([x0 + 2, y1 - 15, x1 - 2, y1 - 2], fill=(120, 115, 105))
        dr.rectangle([x0 + 2, y1 - 17, x1 - 2, y1 - 15], fill=(240, 200, 60))
        # red Tube train, BIG and fully in frame
        tx0, tx1, ty = x0 + 82, x1 - 8, y1 - 17
        dr.rounded_rectangle([tx0, ty - 29, tx1, ty], 6, fill=(200, 30, 40))
        dr.rectangle([tx0, ty - 29, tx1, ty - 22], fill=(40, 80, 160))
        for i in range(4):
            wx = tx0 + 8 + i * 24
            dr.rectangle([wx, ty - 19, wx + 15, ty - 9], fill=(190, 225, 245))
        dr.ellipse([tx0 + 8, ty - 6, tx0 + 14, ty], fill=(255, 240, 150))
        dr.ellipse([tx1 - 14, ty - 6, tx1 - 8, ty], fill=(255, 240, 150))
        # roundel, top-right, fully inside the frame
        rx, ry = x1 - 24, y0 + 13
        dr.ellipse([rx - 8, ry - 8, rx + 8, ry + 8], outline=(220, 30, 30), width=3)
        dr.rectangle([rx - 11, ry - 3, rx + 11, ry + 3], fill=(20, 60, 160))
        # protester + placard, left, fully inside the frame
        person(dr, x0 + 18, y1 - 17, 14, (220, 220, 220), (40, 40, 40))
        dr.line([x0 + 26, y1 - 31, x0 + 26, y1 - 46], fill=(90, 60, 30), width=2)
        dr.rectangle([x0 + 28, y1 - 46, x0 + 78, y1 - 33], fill=(255, 255, 255), outline=(200, 0, 0))
        txt(x0 + 53, y1 - 44, "ON STRIKE", SANS_B(8), (200, 0, 0), "ma")
    elif kind == "stocks":
        dr.rectangle([x0, y0, x1, y1], fill=(18, 28, 44))
        # trading screens
        dr.rectangle([x0 + 6, y0 + 6, x0 + 78, y0 + 26], fill=(35, 50, 70), outline=(90, 110, 130))
        dr.line([(x0 + 10, y0 + 22), (x0 + 26, y0 + 18), (x0 + 40, y0 + 20), (x0 + 56, y0 + 12), (x0 + 74, y0 + 10)],
                fill=(40, 220, 110), width=2)
        dr.rectangle([x0 + 84, y0 + 6, x1 - 6, y0 + 26], fill=(35, 50, 70), outline=(90, 110, 130))
        txt(x0 + 88, y0 + 11, "+2.0%", SANS_B(12), (40, 220, 110), "la")
        # big rising chart
        pts = [(x0 + 6, y1 - 12), (x0 + 40, y1 - 16), (x0 + 70, y1 - 26), (x0 + 110, y1 - 22),
               (x0 + 140, y1 - 34), (x1 - 8, y1 - 44)]
        dr.line(pts, fill=(40, 220, 110), width=3)
        dr.polygon([(x1 - 8, y1 - 44), (x1 - 20, y1 - 44), (x1 - 10, y1 - 52)], fill=(40, 220, 110))
        for px, py in pts[1:-1]:
            dr.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(40, 220, 110))
        txt(x0 + 6, y0 + 30, "KOSPI +2%", SANS_B(12), (40, 220, 110), "la")
        txt(x1 - 6, y0 + 30, "NIKKEI +1.8%", SANS_B(10), (220, 220, 220), "ra")
    elif kind == "taiwan":
        vgrad(dr, x0, y0, x1, y1, (200, 225, 240), (235, 242, 248))
        dr.rectangle([x0, y1 - 18, x1, y1], fill=(60, 130, 190))
        # gantry crane
        dr.line([x0 + 18, y0 + 8, x0 + 18, y1 - 18], fill=(60, 60, 70), width=3)
        dr.line([x0 + 44, y0 + 8, x0 + 44, y1 - 18], fill=(60, 60, 70), width=3)
        dr.line([x0 + 10, y0 + 8, x0 + 120, y0 + 8], fill=(60, 60, 70), width=3)
        dr.line([x0 + 60, y0 + 8, x0 + 60, y0 + 20], fill=(60, 60, 70), width=2)
        # dock containers
        for i, col in enumerate([(200, 60, 50), (40, 110, 180), (240, 180, 40)]):
            dr.rectangle([x0 + 52 + i * 22, y1 - 34, x0 + 72 + i * 22, y1 - 18], fill=col, outline=(255, 255, 255))
        # container ship
        sx0, sy = x0 + 118, y1 - 18
        dr.polygon([(sx0, sy - 10), (sx0 + 64, sy - 10), (sx0 + 58, sy), (sx0 + 4, sy)], fill=(40, 50, 70))
        for i, col in enumerate([(200, 60, 50), (40, 110, 180), (240, 180, 40), (30, 160, 90)]):
            dr.rectangle([sx0 + 6 + i * 15, sy - 24, sx0 + 20 + i * 15, sy - 12], fill=col, outline=(255, 255, 255))
        dr.rectangle([sx0 + 52, sy - 34, sx0 + 64, sy - 24], fill=(240, 240, 240))
        # tariff stamp, top-right
        pill(dr, x1 - 92, y0 + 4, x1 - 4, y0 + 20, (200, 40, 40), "TOP RATE 15%", 10)
    elif kind == "taipo":
        vgrad(dr, x0, y0, x1, y1, (95, 82, 125), (55, 50, 85))
        # housing-block silhouettes with lit windows
        rnd = random.Random(4)
        for bx0, bw, bh in [(x0 + 8, 30, 34), (x0 + 44, 36, 44), (x0 + 86, 30, 38), (x0 + 122, 34, 30), (x0 + 160, 24, 40)]:
            dr.rectangle([bx0, y1 - 20 - bh, bx0 + bw, y1 - 20], fill=(35, 32, 48))
            for wy in range(y1 - 20 - bh + 4, y1 - 22, 8):
                for wx in range(bx0 + 4, bx0 + bw - 4, 8):
                    if rnd.random() < 0.45:
                        dr.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 210, 90))
        # memorial ground: candles + flowers
        dr.rectangle([x0, y1 - 20, x1, y1], fill=(45, 40, 60))
        for i in range(6):
            candle(dr, x0 + 16 + i * 28, y1 - 6, 0.8)
        for i in range(5):
            fx = x0 + 30 + i * 28
            dr.ellipse([fx, y1 - 18, fx + 6, y1 - 12], fill=(230, 100, 140))
            dr.ellipse([fx + 3, y1 - 16, fx + 9, y1 - 10], fill=(255, 160, 60))
        txt(x1 - 6, y0 + 4, "168", SERIF_B(16), (255, 255, 255), "ra")
        txt(x1 - 6, y0 + 22, "REMEMBERED", SANS_B(8), (220, 210, 200), "ra")

# ---------------------------------------------------------------- header
d.rectangle([0, 0, W, 24], fill=NAVY)
txt(512, 4, "THE WORLD IN ONE DAY  ·  36 STORIES  ·  10 REGIONS  ·  18 FIELDS  ·  ALL FIRST REPORTED ON THURSDAY 26 NOVEMBER 2026",
    SANS_B(12), (255, 255, 255), "ma")
masthead = "Thursday 26 November 2026"
mh_size = 62
while mh_size > 30 and d.textlength(masthead, font=SERIF_B(mh_size)) > 980:
    mh_size -= 1
txt(512, 28, masthead, SERIF_B(mh_size), NAVY, "ma")
lede = "Nor'easter grounds Macy's 100th parade  ·  Missiles over Riyadh  ·  India marks 18 years since 26/11"
lede_size = 20
while lede_size > 12 and d.textlength(lede, font=SERIF(lede_size)) > 1000:
    lede_size -= 1
txt(512, 98, lede, SERIF(lede_size), RED, "ma")
# region strip
regs = [("Europe", 8), ("East Asia", 6), ("N. America", 6), ("South Asia", 5), ("Oceania", 4),
        ("Middle East", 2), ("Africa", 2), ("SE Asia", 1), ("Latin Am", 1), ("World", 1)]
x = 12
for name, n in regs:
    lab = f"{name} {n}"
    wdt = d.textlength(lab, font=SANS_B(12)) + 14
    d.rounded_rectangle([x, 124, x + wdt, 144], 4, fill=REGION[name])
    d.text((x + 7, 128), lab, font=SANS_B(12), fill=(255, 255, 255))
    x += wdt + 5
# number strip
nums = [("100", "100th Macy's parade,\nfirst weather delay"), ("2", "missiles downed\nover Riyadh"),
        ("18", "years since\nthe 26/11 attacks"), ("3.25%", "Bank of Korea\nkey rate"),
        ("4", "hurt in Kyiv\nmall strike"), ("24", "schoolgirls freed\nin Nigeria")]
cw = (W - 24) // 6
for i, (num, lab) in enumerate(nums):
    x0 = 12 + i * cw
    d.rectangle([x0, 148, x0 + cw - 4, 192], fill=(255, 255, 255), outline=(200, 190, 170))
    txt(x0 + (cw - 4) // 2, 150, num, SERIF_B(24), NAVY, "ma")
    ll = lab.split("\n")
    txt(x0 + (cw - 4) // 2, 176, ll[0], SANS(9), GREY, "ma")
    txt(x0 + (cw - 4) // 2, 185, ll[1], SANS(9), GREY, "ma")
# timeline
d.rectangle([0, 196, W, 216], fill=NAVY)
tl = "THE DAY IN UTC   00:50  Bank of Korea hikes   ·   09:00  EU summit opens   ·   14:00  Chess Game 3   ·   15:00  NYC wind alert   ·   18:00  NFL games"
txt(12, 200, tl, SANS_B(11), (255, 255, 255), "la")

# ---------------------------------------------------------------- heroes
HEROES = [
    dict(n=1, kind="parade", region="N. America", field="CULTURE", head="Nor'easter grounds Macy's 100th parade",
         body="The 100th parade moves to Saturday — the first weather delay in a century. Gusts to 60 mph.",
         why="WHY: a century-old ritual stopped by weather. — Reuters · AP", badge="CONFIRMED"),
    dict(n=2, kind="riyadh", region="Middle East", field="WAR", head="Saudi defences down two missiles over Riyadh",
         body="Two ballistic missiles aimed at the capital are destroyed early Thursday; a drone is downed near Jeddah.",
         why="WHY: a second straight day of strikes. — Reuters · Al Jazeera", badge="OFFICIAL"),
    dict(n=3, kind="mumbai", region="South Asia", field="REMEMBRANCE", head="India marks 18 years since 26/11",
         body="Tributes for the 166 killed in the 2008 Mumbai attacks, as the nation marks 77 years of its Constitution.",
         why="WHY: the date itself is the anniversary. — PTI · PIB", badge="OFFICIAL"),
]
hy, hh = 222, 232
for i, h in enumerate(HEROES):
    x0 = 12 + i * 336; x1 = x0 + 328
    d.rectangle([x0, hy, x1, hy + hh], fill=(255, 255, 255), outline=(190, 180, 160))
    scene(d, h["kind"], x0 + 4, hy + 4, x1 - 4, hy + 132)
    num_badge(d, x0 + 10, hy + 10, h["n"], 24)
    txt(x0 + 8, hy + 138, f"{h['region'].upper()} — {h['field']}", SANS_B(10), RED, "la")
    badge(x1 - 92, hy + 136, h["badge"], (0, 110, 60) if h["badge"] != "OFFICIAL" else NAVY)
    hl = wrap(h["head"], SERIF_B(15), 306)
    for j, ln in enumerate(hl[:2]):
        txt(x0 + 8, hy + 152 + j * 17, ln, SERIF_B(15), INK, "la")
    bl = wrap(h["body"], SANS(10), 312)
    by = hy + 152 + len(hl[:2]) * 17 + 4
    for j, ln in enumerate(bl[:2]):
        txt(x0 + 8, by + j * 11, ln, SANS(10), INK, "la")
    wf = fit_font(h["why"], 312, 9, bold=False)
    txt(x0 + 8, hy + hh - 12, h["why"], wf, GREY, "la")

# ---------------------------------------------------------------- mids
MIDS = [
    dict(n=4, kind="eu", region="Europe", field="POLITICS", head="EU leaders meet on budget and Ukraine aid",
         body="Two-day summit opens on the 2028–34 budget and Kyiv's 2027 funding.", src="EU Council", badge="OFFICIAL"),
    dict(n=5, kind="chess", region="Europe", field="SPORT", head="Gukesh meets Sindarov in Game 3",
         body="World title match level 1–1 after two draws; Game 3 in Geneva, 14:00 UTC.", src="FIDE", badge="CONFIRMED"),
    dict(n=6, kind="bok", region="East Asia", field="ECONOMY", head="Bank of Korea lifts key rate to 3.25%",
         body="First above 3% since 2024; two of seven dissent.", src="Bank of Korea", badge="OFFICIAL"),
    dict(n=7, kind="kyiv", region="Europe", field="WAR", head="Russian missiles hit Kyiv mall, 4 hurt",
         body="Overnight missiles; two in serious condition; power cuts round the clock.", src="Reuters", badge="REPORTED"),
    dict(n=8, kind="kim", region="East Asia", field="SECURITY", head="Kim calls for more tactical nuclear arms",
         body="KCNA shows Kim touring three nuclear sites; media urges a wider push.", src="KCNA · Yonhap", badge="OFFICIAL"),
    dict(n=9, kind="school", region="Africa", field="JUSTICE", head="Nigeria says 24 schoolgirls freed",
         body="Officials say the girls are safe after the latest school abduction.", src="TRT Afrika", badge="REPORTED"),
    dict(n=10, kind="tube", region="Europe", field="TRANSPORT", head="London Tube drivers begin eight-strike campaign",
         body="No Piccadilly or Circle line all day; first of eight strikes to February.", src="RMT", badge="REPORTED"),
    dict(n=11, kind="stocks", region="East Asia", field="MARKETS", head="Asian stocks bounce back",
         body="Kospi +2%, Nikkei +1.8% early on, a day after the AI-doubts rout.", src="Yonhap", badge="REPORTED"),
    dict(n=12, kind="taiwan", region="East Asia", field="TRADE", head="Taiwan answers US tariff plan",
         body="Top rate 15%, Taiwan says — Thursday's reply to the US announcement.", src="CNA", badge="OFFICIAL"),
    dict(n=13, kind="taipo", region="East Asia", field="MEMORY", head="Hong Kong marks a year since the Tai Po fire",
         body="Residents lay flowers for the 168 dead; no state memorial is held.", src="The Standard", badge="CONFIRMED"),
]
mw, mh = 196, 140
for r in range(2):
    for c in range(5):
        m = MIDS[r * 5 + c]
        x0 = 12 + c * 202; y0 = 460 + r * (mh + 6); x1 = x0 + mw
        d.rectangle([x0, y0, x1, y0 + mh], fill=(255, 255, 255), outline=(190, 180, 160))
        scene(d, m["kind"], x0 + 3, y0 + 3, x1 - 3, y0 + 66)
        num_badge(d, x0 + 7, y0 + 7, m["n"], 18)
        txt(x0 + 5, y0 + 69, f"{m['region'].upper()} — {m['field']}", SANS_B(9), RED, "la")
        badge(x1 - 78, y0 + 67, m["badge"], (0, 110, 60) if m["badge"] != "OFFICIAL" else NAVY)
        hl = wrap(m["head"], SERIF_B(13), 182)
        for j, ln in enumerate(hl[:2]):
            txt(x0 + 5, y0 + 82 + j * 14, ln, SERIF_B(13), INK, "la")
        bl = wrap(m["body"], SANS(9), 186)
        by = y0 + 82 + len(hl[:2]) * 14 + 2
        for j, ln in enumerate(bl[:2]):
            txt(x0 + 5, by + j * 9, ln, SANS(9), INK, "la")
        txt(x0 + 5, y0 + mh - 9, "SOURCE: " + m["src"], SANS(8), GREY, "la")

# ---------------------------------------------------------------- map + list
my = 752
d.rectangle([12, my, 340, my + 130], fill=(215, 228, 235), outline=(190, 180, 160))
txt(16, my + 4, "WHERE IT HAPPENED — PINS 1–13", SANS_B(11), NAVY, "la")
# world map: lon/lat polygons -> map box
MX0, MY0, MW, MH = 16, 772, 320, 96
def mxy(lon, lat):
    return (MX0 + (lon + 170) / 360.0 * MW, MY0 + (75 - lat) / 130.0 * MH)
LAND = (205, 198, 170)
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60), (-55, 47), (-70, 42), (-75, 35),
     (-80, 26), (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-155, 58)],
    [(-45, 60), (-30, 68), (-20, 70), (-25, 76), (-55, 76), (-58, 70)],
    [(-80, 10), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-70, -52), (-73, -40),
     (-70, -20), (-80, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (18, 56), (21, 55), (28, 59), (30, 60),
     (25, 65), (18, 69), (12, 71), (5, 60), (-5, 58), (-10, 50)],
    [(-5, 50), (-3, 53), (-5, 58), (-2, 57), (0, 53)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12), (51, 11), (48, 0),
     (40, -10), (35, -20), (32, -28), (25, -34), (18, -32), (12, -18), (9, -1), (9, 4), (-8, 4), (-13, 8)],
    [(30, 60), (40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72), (160, 70), (178, 66), (170, 60),
     (160, 55), (142, 50), (140, 40), (135, 35), (130, 33), (127, 35), (122, 30), (120, 22), (110, 20),
     (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 15), (77, 8), (73, 20), (66, 25), (60, 25),
     (57, 27), (52, 26), (48, 30), (44, 29), (40, 31), (36, 36), (30, 36), (30, 42), (28, 45)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (129, -32), (137, -35), (140, -38), (145, -38), (150, -37),
     (153, -27), (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
]
for poly in CONTINENTS:
    d.polygon([mxy(lon, lat) for lon, lat in poly], fill=LAND, outline=(170, 163, 135))
# Indonesia + Japan + NZ islands
for lon, lat, rx, ry in [(100, -2, 7, 3), (112, -7, 8, 3), (125, -3, 6, 3), (138, -4, 7, 3),
                         (140, 38, 3, 6), (142, 43, 3, 5), (167, -41, 3, 5), (174, -41, 3, 4)]:
    cxp, cyp = mxy(lon, lat)
    d.ellipse([cxp - rx, cyp - ry, cxp + rx, cyp + ry], fill=LAND)
# grid
for gx in range(MX0 + 40, MX0 + MW, 40):
    d.line([gx, MY0, gx, MY0 + MH], fill=(235, 240, 243), width=1)
for gy in range(MY0 + 24, MY0 + MH, 24):
    d.line([MX0, gy, MX0 + MW, gy], fill=(235, 240, 243), width=1)
# pins: (story, lon, lat, nudge_x, nudge_y)
PINS = [(1, -74, 40.7, 0, 0), (2, 46.7, 24.6, 0, 0), (3, 72.8, 19.1, 0, 0),
        (4, 4.35, 50.85, 9, 7), (5, 6.14, 46.2, -3, 12), (6, 127, 37.5, 0, 0),
        (7, 30.5, 50.45, 2, 0), (8, 125.75, 39.03, -8, 9), (9, 3.4, 6.45, 0, 0),
        (10, -0.1, 51.5, -1, -1), (11, 139.7, 35.7, 4, -2), (12, 121.56, 25.03, 0, 0),
        (13, 114.16, 22.32, 0, 0)]
PIN_REG = {1: "N. America", 2: "Middle East", 3: "South Asia", 4: "Europe", 5: "Europe",
           6: "East Asia", 7: "Europe", 8: "East Asia", 9: "Africa", 10: "Europe",
           11: "East Asia", 12: "East Asia", 13: "East Asia"}
pin_pos = {}
for n, lon, lat, dx, dy in PINS:
    px, py = mxy(lon, lat)
    px, py = px + dx, py + dy
    pin_pos[n] = (px, py)
    col = REGION[PIN_REG[n]]
    d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col, outline=(255, 255, 255), width=2)
    f = SANS_B(9)
    tw = d.textlength(str(n), font=f)
    d.text((px - tw / 2, py - 5), str(n), font=f, fill=(255, 255, 255))
def map_label(x, y, s, anchor="la"):
    f = SANS_B(8)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((x + ox, y + oy), s, font=f, fill=(255, 255, 255), anchor=anchor)
    d.text((x, y), s, font=f, fill=NAVY, anchor=anchor)
map_label(93, 793, "New York", "ra")
map_label(209, 796, "Riyadh", "ma")
map_label(240, 803, "Mumbai", "la")
map_label(180, 812, "Brussels", "ma")
map_label(158, 806, "Geneva", "ra")
map_label(289, 793, "Seoul", "la")
map_label(205, 786, "Kyiv", "la")
map_label(178, 824, "Lagos", "la")
map_label(156, 784, "London", "ra")
map_label(300, 803, "Tokyo", "la")
map_label(284, 815, "Taipei", "la")
map_label(256, 817, "Hong Kong", "ra")
txt(16, my + 116, "Pins = story numbers 1–13 · colours = regions", SANS(9), GREY, "la")

LIST = [
    (14, "Virgin Australia staff strike at 4 airports", "ABC", "C", "Oceania"),
    (15, "US markets shut for Thanksgiving", "NYSE", "O", "N. America"),
    (16, "India: ₹15,000 crore aid for Nepal", "PTI", "R", "South Asia"),
    (17, "Norway court voids oil licences", "Reuters", "R", "Europe"),
    (18, "Zambia bans protest over term limits", "Al Jazeera", "R", "Africa"),
    (19, "Liberal senator defects to One Nation", "ABC", "R", "Oceania"),
    (20, "India rejects US case for 25% tariff", "Commerce min.", "O", "South Asia"),
    (21, "Winter rains threaten Gaza shelter sites", "BBC", "R", "Middle East"),
    (22, "Six days in a row above 2°C", "Copernicus", "O", "World"),
    (23, "Korea's rail slows as Korail staff act", "Yonhap", "R", "East Asia"),
    (24, "M4.0 quake off Labuan, Indonesia", "USGS", "O", "SE Asia"),
    (25, "Europa League: 17 ties on matchday 5", "UEFA", "C", "Europe"),
    (26, "US jobless claims fall to 189,000", "Reuters", "R", "N. America"),
    (27, "Nvidia sell-off drags S&P and Nasdaq down", "Reuters", "R", "N. America"),
    (28, "EU moves on Chinese car quotas", "Reuters", "R", "Europe"),
    (29, "Brazil: mosquitoes cut viral infections 68%", "Study", "R", "Latin Am"),
    (30, "Palm Beach ferries stop as workers walk out", "Medianet", "R", "N. America"),
    (31, "Small-business complaints jump 21% to 5,644", "AFCA", "R", "Oceania"),
    (32, "M4.8 quake off Hicks Bay", "USGS", "R", "Oceania"),
    (33, "Hasina seeks return on 16 Dec", "Dhaka Tribune", "R", "South Asia"),
    (34, "Davis Cup: Britain v Germany", "Davis Cup", "R", "Europe"),
    (35, "Sooryavanshi, 15, smashes record 204 off 53", "BCCI", "R", "South Asia"),
    (36, "NFL Thanksgiving games kick off", "NFL", "C", "N. America"),
]
lx = 350
txt(lx, my + 4, "ALSO ON THURSDAY 26 NOVEMBER — 23 MORE STORIES", SANS_B(12), NAVY, "la")
d.line([lx, my + 20, W - 12, my + 20], fill=NAVY, width=2)
for i, (n, head, src, b, reg) in enumerate(LIST):
    col = i % 2; row = i // 2
    x0 = lx + col * 332; y0 = my + 26 + row * 9
    colr = REGION[reg]
    d.rectangle([x0, y0, x0 + 16, y0 + 11], fill=colr)
    txt(x0 + 8, y0, str(n), SANS_B(8), (255, 255, 255), "ma")
    s = f"{head} [{b}] — {src}"
    txt(x0 + 20, y0, s, SANS(9), INK, "la")

# ---------------------------------------------------------------- DATE CHECK
dy = 888
d.rectangle([12, dy, W - 12, dy + 82], fill=(255, 245, 245), outline=RED, width=2)
txt(20, dy + 4, "DATE CHECK — THESE ARE NOT 26 NOVEMBER", SANS_B(12), RED, "la")
txt(20, dy + 20, "Every story above happened or was first reported on Thursday 26 November 2026.", SANS_B(11), INK, "la")
ex = ("Left out as earlier news:  Cairo tanker fire (Wed 25)  ·  Solomon Islands treaty (Wed 25)  ·  Shenzhou-24 docking (Wed 25)  ·  "
      "US tariff announcement (Wed 25)  ·  Bangladesh wage rise (Wed 25)  ·  Ras Tanura claim (Wed 25)  ·  "
      "Gaza security chief killed (Wed 25)  ·  US GDP +4.3% (Wed 25)  ·  N. Korea expels Swiss envoy (Wed 25)  ·  "
      "Nvidia reinstates Huang (Mon 23)  ·  Real Madrid 5–1 PSV (Tue 24)  ·  COP31 collapse (Sun 22).")
for j, ln in enumerate(wrap(ex, SANS(10), 980)):
    txt(20, dy + 36 + j * 12, ln, SANS(10), INK, "la")
txt(20, dy + 68, "Not yet:  Chess Game 3 result  ·  EU budget deal (Fri 27 Nov)  ·  Taiwan vote (Sat 28 Nov).", SANS_B(10), RED, "la")

# ---------------------------------------------------------------- footer
txt(12, 976, "OFFICIAL = an authority's own word  ·  CONFIRMED = 2+ major outlets  ·  REPORTED = press report  ·  CLAIM = one side's say, unverified",
    SANS(10), GREY, "la")
txt(12, 988, "Sources: Reuters, AP, AFP, BBC, Al Jazeera, Yonhap, FIDE, Bank of Korea, EU Council, PTI — all reported 26 November 2026.  Every drawing original — drawn in code, not photos.",
    SANS(10), GREY, "la")
txt(512, 1000, "THE WORLD IN ONE DAY  ·  26 NOV 2026  ·  36 STORIES  ·  10 REGIONS", SANS_B(9), NAVY, "ma")

img.save("entry.png")
print("saved entry.png", img.size)
