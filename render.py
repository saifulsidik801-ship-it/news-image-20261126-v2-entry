#!/usr/bin/env python3
"""news-image-20261126 v6 — one-day front page, drawn in code (PIL only, no photos).
36 stories: 3 heroes + 10 mids + 23 list. All happened / first reported Thu 26 Nov 2026.
v6 vs v5: bigger full-width story-locator map (taller, re-spaced labels); hero 2
redrawn as a concrete Riyadh night scene (Kingdom Centre + Faisaliah globe towers,
street level with cars, two interceptor streaks, no abstract beam); mid art taller
(70 -> 81px) and scene-led; denser detail in hero 1/3; body wording tightened on
#7 (attribution disputed), #10 and #13 (unverified claims dropped). Same 36-story set,
#22 keeps the fixed "UK writes to ~100,000 strategic reservists" wording."""
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
BCOL = {"OFFICIAL": NAVY, "CONFIRMED": (0, 110, 60), "REPORTED": (170, 115, 0), "CLAIM": (160, 30, 90)}

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
    if kind == "bangchak":
        # Bangchak refinery, Bangkok, Thu afternoon: dusk sky, distillation
        # towers, storage tanks, fireball + black smoke, fire crews.
        vgrad(dr, x0, y0, x1, y1, (70, 60, 90), (235, 150, 80))
        dr.ellipse([x1 - 40, y0 + 6, x1 - 12, y0 + 34], fill=(255, 220, 140))
        # distant city skyline
        buildings(dr, x0, y0 + 44, x1, y1 - 26, 31, (52, 48, 70), (255, 200, 110), 0.4)
        # refinery: storage tanks (left) + distillation towers (centre-right)
        for tx in (x0 + 14, x0 + 52):
            dr.ellipse([tx, y1 - 52, tx + 34, y1 - 40], fill=(190, 190, 195))
            dr.rectangle([tx, y1 - 46, tx + 34, y1 - 26], fill=(200, 200, 205))
            dr.line([tx + 4, y1 - 46, tx + 30, y1 - 46], fill=(150, 150, 155), width=1)
        for tx, th in ((x0 + 108, 58), (x0 + 132, 72), (x0 + 158, 52)):
            dr.rectangle([tx, y1 - 26 - th, tx + 14, y1 - 26], fill=(120, 120, 128))
            dr.rectangle([tx - 3, y1 - 26 - th - 6, tx + 17, y1 - 26 - th], fill=(100, 100, 108))
            for py in range(y1 - 26 - th + 6, y1 - 28, 10):
                dr.rectangle([tx + 2, py, tx + 12, py + 3], fill=(255, 190, 90))
        # connecting pipes
        dr.line([x0 + 48, y1 - 34, x0 + 108, y1 - 34], fill=(140, 140, 148), width=3)
        dr.line([x0 + 172, y1 - 40, x1 - 30, y1 - 40], fill=(140, 140, 148), width=3)
        # fireball at the hydrocracking tower + embers
        fx, fy = x0 + 139, y1 - 62
        dr.polygon([(fx - 16, fy + 8), (fx - 11, fy - 12), (fx - 4, fy - 2), (fx, fy - 18),
                    (fx + 5, fy - 3), (fx + 12, fy - 13), (fx + 16, fy + 8), (fx, fy + 14)],
                   fill=(255, 110, 25))
        for r, col in [(11, (255, 170, 40)), (7, (255, 215, 90)), (3, (255, 245, 170))]:
            dr.ellipse([fx - r, fy - r, fx + r, fy + r], fill=col)
        rnd = random.Random(7)
        for _ in range(10):
            ex = fx + rnd.randint(-24, 24); ey = fy + rnd.randint(-26, 4)
            dr.ellipse([ex - 1, ey - 1, ex + 1, ey + 1], fill=(255, 180, 60))
        # thick black smoke plume, drifting right, capped below the top edge
        for sx, sy, sr in [(fx + 6, y0 + 14, 12), (fx + 22, y0 + 10, 10), (fx + 38, y0 + 14, 9),
                           (fx + 52, y0 + 20, 8), (fx + 64, y0 + 28, 7)]:
            dr.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(45, 42, 48))
        # ground + fire truck with water arc (left) + crew
        dr.rectangle([x0, y1 - 26, x1, y1], fill=(60, 58, 64))
        dr.rectangle([x0 + 8, y1 - 22, x0 + 52, y1 - 8], fill=(200, 40, 40))
        dr.rectangle([x0 + 38, y1 - 22, x0 + 52, y1 - 14], fill=(200, 40, 40))
        dr.rectangle([x0 + 40, y1 - 19, x0 + 49, y1 - 15], fill=(170, 220, 240))
        dr.ellipse([x0 + 12, y1 - 10, x0 + 20, y1 - 2], fill=(25, 25, 25))
        dr.ellipse([x0 + 38, y1 - 10, x0 + 46, y1 - 2], fill=(25, 25, 25))
        dr.arc([x0 + 52, y1 - 34, x0 + 96, y1 - 6], 300, 20, fill=(170, 220, 245), width=2)
        for i, px in enumerate((x0 + 66, x0 + 80, x0 + 94)):
            person(dr, px, y1 - 8, 15, (240, 200, 40) if i % 2 else (30, 90, 160), (40, 40, 40))
        # second fire truck (right) + extra storage tank + crane silhouette
        dr.rectangle([x1 - 92, y1 - 22, x1 - 52, y1 - 8], fill=(200, 40, 40))
        dr.rectangle([x1 - 66, y1 - 22, x1 - 52, y1 - 14], fill=(200, 40, 40))
        dr.rectangle([x1 - 64, y1 - 19, x1 - 55, y1 - 15], fill=(170, 220, 240))
        dr.ellipse([x1 - 88, y1 - 10, x1 - 80, y1 - 2], fill=(25, 25, 25))
        dr.ellipse([x1 - 62, y1 - 10, x1 - 54, y1 - 2], fill=(25, 25, 25))
        dr.arc([x1 - 52, y1 - 34, x1 - 8, y1 - 6], 320, 40, fill=(170, 220, 245), width=2)
        dr.ellipse([x0 + 200, y1 - 52, x0 + 234, y1 - 40], fill=(190, 190, 195))
        dr.rectangle([x0 + 200, y1 - 46, x0 + 234, y1 - 26], fill=(200, 200, 205))
        dr.line([x0 + 204, y1 - 46, x0 + 230, y1 - 46], fill=(150, 150, 155), width=1)
        dr.line([x0 + 250, y0 + 30, x0 + 250, y1 - 26], fill=(90, 90, 100), width=2)
        dr.line([x0 + 250, y0 + 30, x0 + 286, y0 + 38], fill=(90, 90, 100), width=2)
        dr.line([x0 + 286, y0 + 38, x0 + 286, y0 + 52], fill=(90, 90, 100), width=1)
        pill(dr, x1 - 62, y0 + 4, x1 - 4, y0 + 18, (200, 40, 40), "9 HURT", 10)
    elif kind == "riyadh":
        # Night interception over Riyadh, concrete scene: Kingdom Centre tower
        # (arch cut-out) + Al Faisaliah globe tower, lit skyline, street level
        # with cars, two interceptor streaks rising from ground launchers to
        # two bursts. No abstract beam — every element is a real object.
        vgrad(dr, x0, y0, x1, y1, (8, 16, 40), (30, 46, 82))
        rnd = random.Random(5)
        for _ in range(34):
            sx = rnd.randint(x0 + 2, x1 - 2); sy = rnd.randint(y0 + 2, y0 + 34)
            dr.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        # crescent moon, top right
        dr.ellipse([x1 - 34, y0 + 6, x1 - 14, y0 + 26], fill=(250, 240, 200))
        dr.ellipse([x1 - 30, y0 + 4, x1 - 10, y0 + 24], fill=(12, 20, 46))
        # skyline: mid towers with lit windows, left and centre
        buildings(dr, x0, y0 + 48, x1 - 90, y1 - 14, 17, (30, 45, 80), (255, 210, 90), 0.6)
        # Kingdom Centre tower (right): tall slab + inverted-arch cut-out
        tx = x1 - 82
        dr.rectangle([tx, y0 + 26, tx + 28, y1 - 14], fill=(42, 60, 100))
        dr.polygon([(tx, y0 + 26), (tx + 28, y0 + 26), (tx + 14, y0 + 44)], fill=(42, 60, 100))
        dr.ellipse([tx + 7, y0 + 34, tx + 21, y0 + 54], fill=(10, 18, 42))
        for wy in range(y0 + 58, y1 - 18, 9):
            dr.rectangle([tx + 4, wy, tx + 8, wy + 4], fill=(255, 210, 90))
            dr.rectangle([tx + 20, wy, tx + 24, wy + 4], fill=(255, 210, 90))
        # Al Faisaliah globe tower (centre-right): shaft + glass globe
        gx = x0 + 196
        dr.rectangle([gx, y0 + 44, gx + 16, y1 - 14], fill=(36, 52, 88))
        dr.ellipse([gx - 2, y0 + 28, gx + 18, y0 + 46], fill=(150, 200, 235), outline=(220, 235, 245))
        dr.line([gx + 8, y0 + 28, gx + 8, y0 + 46], fill=(220, 235, 245), width=1)
        for wy in range(y0 + 50, y1 - 18, 10):
            dr.rectangle([gx + 3, wy, gx + 7, wy + 4], fill=(255, 210, 90))
            dr.rectangle([gx + 10, wy, gx + 14, wy + 4], fill=(255, 210, 90))
        # incoming missile streak (top-left): bright head + dotted trail
        dr.line([x0 + 14, y0 + 8, x0 + 58, y0 + 30], fill=(255, 240, 200), width=2)
        for i in range(5):
            ix = x0 + 16 + i * 9; iy = y0 + 9 + i * 4
            dr.ellipse([ix, iy, ix + 2, iy + 2], fill=(255, 220, 150))
        dr.ellipse([x0 + 56, y0 + 27, x0 + 64, y0 + 35], fill=(255, 200, 80))
        # interceptor 1: ground launcher (left) fires a steep rising streak
        lx0, ly = x0 + 30, y1 - 14
        dr.rectangle([lx0, ly - 10, lx0 + 40, ly], fill=(60, 80, 60))
        for wx in (lx0 + 5, lx0 + 18, lx0 + 29):
            dr.ellipse([wx, ly - 2, wx + 8, ly + 4], fill=(20, 20, 20))
        dr.line([lx0 + 20, ly - 10, x0 + 92, y0 + 42], fill=(255, 230, 160), width=2)
        dr.line([lx0 + 20, ly - 10, x0 + 92, y0 + 42], fill=(255, 255, 255), width=1)
        # interceptor 2: second launcher (centre) fires a shallower streak
        lx2 = x0 + 130
        dr.rectangle([lx2, ly - 10, lx2 + 36, ly], fill=(60, 80, 60))
        for wx in (lx2 + 5, lx2 + 17, lx2 + 27):
            dr.ellipse([wx, ly - 2, wx + 8, ly + 4], fill=(20, 20, 20))
        dr.line([lx2 + 18, ly - 10, x1 - 52, y0 + 30], fill=(255, 200, 110), width=2)
        # two interception bursts where streaks meet the incoming missiles
        burst(dr, x0 + 92, y0 + 42, 12, (255, 200, 80))
        burst(dr, x1 - 52, y0 + 30, 14, (255, 200, 80))
        for (bx, by) in ((x0 + 92, y0 + 42), (x1 - 52, y0 + 30)):
            for r, col in [(8, (255, 150, 40)), (4, (255, 215, 90))]:
                dr.ellipse([bx - r, by - r, bx + r, by + r], fill=col)
        # falling debris dots under the bursts
        for dx, dy in [(x0 + 84, y0 + 56), (x0 + 100, y0 + 60), (x1 - 60, y0 + 46), (x1 - 44, y0 + 50)]:
            dr.ellipse([dx, dy, dx + 2, dy + 2], fill=(255, 180, 80))
        # street level: road, cars with headlights, street lamps
        dr.rectangle([x0, y1 - 14, x1, y1], fill=(24, 28, 40))
        dr.line([x0 + 4, y1 - 7, x1 - 4, y1 - 7], fill=(240, 220, 60), width=1)
        for cxp, col in ((x0 + 90, (200, 40, 40)), (x0 + 160, (40, 120, 200)), (x1 - 120, (220, 220, 220))):
            dr.rectangle([cxp, y1 - 13, cxp + 18, y1 - 8], fill=col)
            dr.ellipse([cxp + 15, y1 - 11, cxp + 18, y1 - 8], fill=(255, 240, 150))
        for lx in (x0 + 12, x0 + 120, x1 - 100):
            dr.line([lx, y1 - 14, lx, y1 - 26], fill=(120, 120, 130), width=1)
            dr.ellipse([lx - 2, y1 - 28, lx + 2, y1 - 24], fill=(255, 220, 120))
        dr.rounded_rectangle([x0 + 44, y0 + 4, x0 + 172, y0 + 20], 3, fill=(10, 18, 42))
        txt(x0 + 48, y0 + 7, "2 MISSILES DOWN", SANS_B(12), (255, 220, 80), "la")
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
        # mourners standing at the sides, heads bowed
        for px, shirt in ((x0 + 22, (40, 60, 110)), (x0 + 44, (110, 40, 60)), (x1 - 44, (40, 90, 60)), (x1 - 22, (90, 70, 30))):
            person(dr, px, y1 - 40, 17, shirt, (35, 35, 35))
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
    elif kind == "kuwait":
        # Night air-defence site in Kuwait: radar dome, interceptor launch,
        # explosion burst, facility buildings, desert ground. All inside frame.
        vgrad(dr, x0, y0, x1, y1, (10, 18, 44), (34, 48, 84))
        rnd = random.Random(6)
        for _ in range(14):
            sx = rnd.randint(x0 + 2, x1 - 2); sy = rnd.randint(y0 + 2, y0 + 20)
            dr.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        # desert ground
        dr.rectangle([x0, y1 - 16, x1, y1], fill=(72, 62, 48))
        # facility buildings with lit windows
        dr.rectangle([x0 + 8, y0 + 34, x0 + 46, y1 - 16], fill=(70, 70, 85))
        for wy in range(y0 + 38, y1 - 18, 8):
            dr.rectangle([x0 + 12, wy, x0 + 16, wy + 4], fill=(255, 210, 90))
            dr.rectangle([x0 + 24, wy, x0 + 28, wy + 4], fill=(255, 210, 90))
        # radar dome + dish on a mast
        dr.rectangle([x0 + 52, y0 + 40, x0 + 66, y1 - 16], fill=(90, 90, 100))
        dr.ellipse([x0 + 50, y0 + 30, x0 + 68, y0 + 42], fill=(220, 220, 225))
        dr.line([x0 + 76, y0 + 44, x0 + 76, y0 + 26], fill=(180, 180, 190), width=2)
        dr.ellipse([x0 + 70, y0 + 20, x0 + 82, y0 + 30], outline=(220, 220, 225), width=2)
        # interceptor streak + burst in the sky (right)
        dr.line([x1 - 70, y1 - 16, x1 - 44, y0 + 26], fill=(255, 240, 200), width=2)
        burst(dr, x1 - 40, y0 + 22, 10, (255, 200, 80))
        for r, col in [(7, (255, 150, 40)), (4, (255, 215, 90))]:
            dr.ellipse([x1 - 40 - r, y0 + 22 - r, x1 - 40 + r, y0 + 22 + r], fill=col)
        # smoke plume under the burst
        for sx, sy, sr in [(x1 - 52, y0 + 30, 4), (x1 - 58, y0 + 36, 5), (x1 - 64, y0 + 42, 4)]:
            dr.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(110, 110, 116))
        # launcher truck, foreground centre-right
        lx0, ly = x1 - 96, y1 - 16
        dr.rectangle([lx0, ly - 10, lx0 + 40, ly], fill=(60, 90, 60))
        for wx in (lx0 + 5, lx0 + 19, lx0 + 30):
            dr.ellipse([wx, ly - 2, wx + 8, ly + 5], fill=(20, 20, 20))
        pill(dr, x1 - 56, y0 + 4, x1 - 4, y0 + 18, (200, 40, 40), "2 KILLED", 10)
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
    elif kind == "garment":
        # Gazipur street: garment factory, marching workers with a placard,
        # tear-gas smoke, police line with shields. All inside the frame.
        vgrad(dr, x0, y0, x1, y1, (200, 220, 235), (240, 235, 215))
        # factory with sawtooth roof
        dr.rectangle([x0 + 6, y0 + 16, x0 + 78, y1 - 16], fill=(190, 120, 70))
        for i in range(3):
            dr.polygon([(x0 + 6 + i * 24, y0 + 16), (x0 + 18 + i * 24, y0 + 6),
                        (x0 + 30 + i * 24, y0 + 16)], fill=(150, 90, 50))
        for wx in range(x0 + 12, x0 + 74, 14):
            dr.rectangle([wx, y0 + 24, wx + 8, y0 + 32], fill=(255, 240, 180))
        dr.rectangle([x0 + 34, y1 - 28, x0 + 46, y1 - 16], fill=(120, 80, 50))
        # road
        dr.rectangle([x0, y1 - 16, x1, y1], fill=(90, 88, 84))
        dr.line([x0 + 6, y1 - 8, x1 - 6, y1 - 8], fill=(240, 220, 60), width=1)
        # tear-gas smoke puffs
        for sx, sy, sr in [(x0 + 104, y0 + 22, 8), (x0 + 120, y0 + 14, 6),
                           (x0 + 150, y0 + 24, 7), (x0 + 164, y0 + 16, 5)]:
            dr.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(225, 225, 220))
        # marching workers with a placard
        for i, px in enumerate((x0 + 96, x0 + 110, x0 + 124, x0 + 138)):
            person(dr, px, y1 - 16, 15, (30, 90, 160) if i % 2 else (200, 60, 40), (40, 40, 40))
        dr.line([x0 + 104, y1 - 31, x0 + 104, y1 - 48], fill=(90, 60, 30), width=2)
        dr.rectangle([x0 + 106, y1 - 48, x0 + 140, y1 - 36], fill=(255, 255, 255), outline=(200, 0, 0))
        txt(x0 + 123, y1 - 46, "PAY UP", SANS_B(8), (200, 0, 0), "ma")
        # police line with shields (right edge, inside frame)
        for i, px in enumerate((x1 - 34, x1 - 20)):
            person(dr, px, y1 - 16, 16, (30, 30, 40), (30, 30, 40))
            dr.rectangle([px - 7, y1 - 30, px + 7, y1 - 16], fill=(60, 60, 80), outline=(200, 200, 200))
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
d.rectangle([0, 0, W, 22], fill=NAVY)
txt(512, 4, "THE WORLD IN ONE DAY  ·  36 STORIES  ·  9 REGIONS  ·  21 FIELDS  ·  ALL FIRST REPORTED ON THURSDAY 26 NOVEMBER 2026",
    SANS_B(12), (255, 255, 255), "ma")
masthead = "Thursday 26 November 2026"
mh_size = 56
while mh_size > 30 and d.textlength(masthead, font=SERIF_B(mh_size)) > 980:
    mh_size -= 1
txt(512, 24, masthead, SERIF_B(mh_size), NAVY, "ma")
lede = "Refinery blast in Bangkok  ·  Missiles over Riyadh  ·  India marks 18 years since 26/11"
lede_size = 19
while lede_size > 12 and d.textlength(lede, font=SERIF(lede_size)) > 1000:
    lede_size -= 1
txt(512, 84, lede, SERIF(lede_size), RED, "ma")
# region strip
regs = [("Europe", 10), ("East Asia", 7), ("N. America", 5), ("Middle East", 3), ("Africa", 3),
        ("Oceania", 3), ("South Asia", 2), ("World", 2), ("SE Asia", 1)]
x = 12
for name, n in regs:
    lab = f"{name} {n}"
    wdt = d.textlength(lab, font=SANS_B(12)) + 14
    d.rounded_rectangle([x, 108, x + wdt, 126], 4, fill=REGION[name])
    d.text((x + 7, 112), lab, font=SANS_B(12), fill=(255, 255, 255))
    x += wdt + 5
# number strip
nums = [("9", "hurt in Bangkok\nrefinery blast"), ("2", "missiles downed\nover Riyadh"),
        ("18", "years since\nthe 26/11 attacks"), ("3.25%", "Bank of Korea\nkey rate"),
        ("77,000", "UK net migration,\nlowest since 1997"), ("12,021", "Congo Ebola cases,\nsecond-largest ever")]
cw = (W - 24) // 6
for i, (num, lab) in enumerate(nums):
    x0 = 12 + i * cw
    d.rectangle([x0, 128, x0 + cw - 4, 168], fill=(255, 255, 255), outline=(200, 190, 170))
    txt(x0 + (cw - 4) // 2, 130, num, SERIF_B(24), NAVY, "ma")
    ll = lab.split("\n")
    txt(x0 + (cw - 4) // 2, 153, ll[0], SANS(9), GREY, "ma")
    txt(x0 + (cw - 4) // 2, 162, ll[1], SANS(9), GREY, "ma")
# timeline
d.rectangle([0, 174, W, 194], fill=NAVY)
tl = "THE DAY IN UTC  00:50 Bank of Korea hikes · 08:00 Bangkok blast · 08:00 EU summit opens · 14:00 Chess Game 3 · 17:30 NFL kicks off · 19:55 DCA ground stop"
txt(12, 178, tl, SANS_B(11), (255, 255, 255), "la")

# ---------------------------------------------------------------- heroes
HEROES = [
    dict(n=1, kind="bangchak", region="SE Asia", field="DISASTER", head="Refinery blast rocks Bangkok",
         body="Nine hurt as a hydrocracking unit explodes at the Bangchak refinery; output halted.",
         why="WHY: the day's biggest industrial disaster. — CNN", badge="CONFIRMED"),
    dict(n=2, kind="riyadh", region="Middle East", field="WAR", head="Saudi defences down two missiles over Riyadh",
         body="Two ballistic missiles aimed at the capital are destroyed early Thursday; drones are downed in the Eastern Region.",
         why="WHY: a second straight day of strikes. — Reuters · Al Jazeera", badge="OFFICIAL"),
    dict(n=3, kind="mumbai", region="South Asia", field="REMEMBRANCE", head="India marks 18 years since 26/11",
         body="Tributes for the 166 killed in the 2008 Mumbai attacks, as the nation marks 77 years of its Constitution.",
         why="WHY: the date itself is the anniversary. — PTI · PIB", badge="OFFICIAL"),
]
hy, hh = 198, 216
for i, h in enumerate(HEROES):
    x0 = 12 + i * 336; x1 = x0 + 328
    d.rectangle([x0, hy, x1, hy + hh], fill=(255, 255, 255), outline=(190, 180, 160))
    scene(d, h["kind"], x0 + 4, hy + 4, x1 - 4, hy + 128)
    num_badge(d, x0 + 10, hy + 10, h["n"], 24)
    txt(x0 + 8, hy + 132, f"{h['region'].upper()} — {h['field']}", SANS_B(10), RED, "la")
    badge(x1 - 92, hy + 130, h["badge"], BCOL[h["badge"]])
    hl = wrap(h["head"], SERIF_B(15), 306)
    for j, ln in enumerate(hl[:2]):
        txt(x0 + 8, hy + 146 + j * 17, ln, SERIF_B(15), INK, "la")
    bl = wrap(h["body"], SANS(10), 312)
    by = hy + 146 + len(hl[:2]) * 17 + 4
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
    dict(n=7, kind="kuwait", region="Middle East", field="WAR", head="Drone strike in Kuwait kills two Italians",
         body="Drones hit an air-defence site; two Rheinmetall technicians die.", src="Reuters", badge="REPORTED"),
    dict(n=8, kind="kim", region="East Asia", field="SECURITY", head="Kim calls for more tactical nuclear arms",
         body="KCNA shows Kim touring three nuclear sites; media urges a wider push.", src="KCNA · Yonhap", badge="OFFICIAL"),
    dict(n=9, kind="garment", region="South Asia", field="LABOUR", head="Garment workers clash with police",
         body="Tear gas in Gazipur as workers reject a 36% pay rise; highways blocked.", src="Reuters", badge="REPORTED"),
    dict(n=10, kind="tube", region="Europe", field="TRANSPORT", head="London Tube drivers begin eight-strike campaign",
         body="No Piccadilly or Circle line all day; first of eight strikes.", src="RMT", badge="REPORTED"),
    dict(n=11, kind="stocks", region="East Asia", field="MARKETS", head="Asian stocks bounce back",
         body="Kospi +2%, Nikkei +1.8% early on, a day after the AI-doubts rout.", src="Yonhap", badge="REPORTED"),
    dict(n=12, kind="taiwan", region="East Asia", field="TRADE", head="Taiwan answers US tariff plan",
         body="Top rate 15%, Taiwan says — Thursday's reply to the US announcement.", src="CNA", badge="OFFICIAL"),
    dict(n=13, kind="taipo", region="East Asia", field="MEMORY", head="Hong Kong marks a year since the Tai Po fire",
         body="Residents lay flowers for the 168 dead; the city remembers.", src="The Standard", badge="CONFIRMED"),
]
mw, mh = 196, 150
for r in range(2):
    for c in range(5):
        m = MIDS[r * 5 + c]
        x0 = 12 + c * 202; y0 = 416 + r * (mh + 6); x1 = x0 + mw
        d.rectangle([x0, y0, x1, y0 + mh], fill=(255, 255, 255), outline=(190, 180, 160))
        scene(d, m["kind"], x0 + 3, y0 + 3, x1 - 3, y0 + 84)
        num_badge(d, x0 + 7, y0 + 7, m["n"], 18)
        txt(x0 + 5, y0 + 87, f"{m['region'].upper()} — {m['field']}", SANS_B(8), RED, "la")
        badge(x1 - 78, y0 + 85, m["badge"], BCOL[m["badge"]])
        hl = wrap(m["head"], SERIF_B(12), 182)
        for j, ln in enumerate(hl[:2]):
            txt(x0 + 5, y0 + 99 + j * 12, ln, SERIF_B(12), INK, "la")
        bl = wrap(m["body"], SANS(9), 186)
        by = y0 + 99 + len(hl[:2]) * 12 + 2
        for j, ln in enumerate(bl[:2]):
            txt(x0 + 5, by + j * 8, ln, SANS(9), INK, "la")
        txt(x0 + 5, y0 + 141, "SOURCE: " + m["src"], SANS(8), GREY, "la")

# ---------------------------------------------------------------- map (FULL-WIDTH story locator)
my = 722
d.rectangle([12, my, W - 12, 884], fill=(22, 48, 78), outline=(190, 180, 160))
# world map: lon/lat polygons -> full-width map box (lat -45..62)
MX0, MY0, MW, MH = 16, 742, 992, 132
def mxy(lon, lat):
    return (MX0 + (lon + 170) / 360.0 * MW, MY0 + (62 - lat) / 107.0 * MH)
LAND = (222, 210, 170)
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
for lon, lat, rx, ry in [(100, -2, 20, 4), (112, -7, 22, 4), (125, -3, 16, 4), (138, -4, 18, 4),
                         (140, 38, 7, 8), (142, 43, 7, 7), (167, -41, 7, 7), (174, -41, 7, 6)]:
    cxp, cyp = mxy(lon, lat)
    d.ellipse([cxp - rx, cyp - ry, cxp + rx, cyp + ry], fill=LAND)
# grid
for gx in range(MX0 + 82, MX0 + MW, 82):
    d.line([gx, MY0, gx, MY0 + MH], fill=(48, 78, 112), width=1)
for gy in range(MY0 + 31, MY0 + MH, 31):
    d.line([MX0, gy, MX0 + MW, gy], fill=(48, 78, 112), width=1)
# pins: (story, lon, lat, nudge_x, nudge_y)
PINS = [(1, 100.5, 13.75, 0, 0), (2, 46.7, 24.6, -14, 6), (3, 72.8, 19.1, 0, 0),
        (4, 4.35, 50.85, 12, -8), (5, 6.14, 46.2, 10, 12), (6, 127, 37.5, 14, 4),
        (7, 47.98, 29.38, 16, -10), (8, 125.75, 39.03, -12, -8), (9, 90.4, 24.0, 0, 0),
        (10, -0.1, 51.5, -16, -6), (11, 139.7, 35.7, 0, 0), (12, 121.56, 25.03, 6, 10),
        (13, 114.16, 22.32, -10, 8)]
PIN_REG = {1: "SE Asia", 2: "Middle East", 3: "South Asia", 4: "Europe", 5: "Europe",
           6: "East Asia", 7: "Middle East", 8: "East Asia", 9: "South Asia", 10: "Europe",
           11: "East Asia", 12: "East Asia", 13: "East Asia"}
for n, lon, lat, dx, dy in PINS:
    tx, ty = mxy(lon, lat)
    px, py = tx + dx, ty + dy
    if dx or dy:
        d.line([tx, ty, px, py], fill=(200, 210, 220), width=1)
    col = REGION[PIN_REG[n]]
    d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=col, outline=(255, 255, 255), width=2)
    f = SANS_B(10)
    tw = d.textlength(str(n), font=f)
    d.text((px - tw / 2, py - 6), str(n), font=f, fill=(255, 255, 255))
def map_label(x, y, s, anchor="la"):
    f = SANS_B(9)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((x + ox, y + oy), s, font=f, fill=NAVY, anchor=anchor)
    d.text((x, y), s, font=f, fill=(255, 255, 255), anchor=anchor)
map_label(745, 812, "Bangkok", "ma")
map_label(586, 800, "Riyadh", "ra")
map_label(672, 801, "Mumbai", "ra")
map_label(520, 736, "Brussels", "la")
map_label(498, 780, "Geneva", "ra")
map_label(852, 784, "Seoul", "la")
map_label(644, 760, "Kuwait", "la")
map_label(808, 748, "Pyongyang", "ra")
map_label(722, 796, "Gazipur", "ra")
map_label(456, 736, "London", "ra")
map_label(880, 760, "Tokyo", "la")
map_label(830, 808, "Taipei", "la")
map_label(789, 778, "Hong Kong", "ma")
txt(16, 874, "Pins = story numbers 1–13 · colours = regions", SANS(8), (200, 215, 230), "la")
d.rectangle([12, my, W - 12, 884], outline=(190, 180, 160))
# title band last so northern land never overdraws the title text
d.rectangle([12, my, W - 12, my + 18], fill=(22, 48, 78))
txt(16, my + 4, "WHERE IT HAPPENED — STORY LOCATOR · PINS 1–13", SANS_B(11), (255, 255, 255), "la")
txt(W - 16, my + 4, "DARK BLUE OCEAN · NUMBERED PINS · COLOURS = REGIONS", SANS_B(9), (180, 205, 230), "ra")
d.line([12, my + 18, W - 12, my + 18], fill=(90, 120, 150), width=1)

LIST = [
    (14, "Virgin Australia staff strike at 4 airports", "R", "Oceania"),
    (15, "US markets shut for Thanksgiving", "O", "N. America"),
    (16, "Trump tells Putin: pull back aggression", "R", "N. America"),
    (17, "N. Korea pauses missile shipments to Russia", "K", "East Asia"),
    (18, "Zambia bans protest over term limits", "R", "Africa"),
    (19, "Trump demands probe of GDP data", "R", "N. America"),
    (20, "IRGC: two tankers hit by mines in Hormuz", "K", "Middle East"),
    (21, "UNCTAD: sea trade flat in 2026", "O", "World"),
    (22, "UK writes to ~100,000 strategic reservists", "O", "Europe"),
    (23, "Korail work-to-rule slows trains", "R", "East Asia"),
    (24, "UK signs £8bn submarine deal with Babcock", "O", "Europe"),
    (25, "Europa League: 18 ties on matchday 5", "C", "Europe"),
    (26, "Cairo tanker driver held after fatal crash", "R", "Africa"),
    (27, "Norse Atlantic grounds all flights", "R", "Europe"),
    (28, "UK net migration 77,000, lowest since 1997", "O", "Europe"),
    (29, "INTERPOL: 65 held in Neptune VIII sweep", "O", "World"),
    (30, "Palm Beach ferries stop as workers walk out", "R", "Oceania"),
    (31, "Thanksgiving storm grounds DC flights", "R", "N. America"),
    (32, "M4.8 quake off Hicks Bay", "R", "Oceania"),
    (33, "Congo Ebola tops 12,000 cases", "R", "Africa"),
    (34, "Davis Cup: Britain v Germany", "R", "Europe"),
    (35, "ECB picks de Cos to succeed Lagarde", "O", "Europe"),
    (36, "NFL Thanksgiving games kick off", "C", "N. America"),
]
lx = 12
txt(lx, 888, "ALSO ON THURSDAY 26 NOVEMBER — 23 MORE STORIES", SANS_B(12), NAVY, "la")
d.line([lx, 904, W - 12, 904], fill=NAVY, width=2)
for i, (n, head, b, reg) in enumerate(LIST):
    col = i % 4; row = i // 4
    x0 = lx + col * 250; y0 = 908 + row * 9
    colr = REGION[reg]
    d.rectangle([x0, y0, x0 + 15, y0 + 11], fill=colr)
    txt(x0 + 7, y0, str(n), SANS_B(8), (255, 255, 255), "ma")
    s = f"{head} [{b}]"
    txt(x0 + 19, y0, s, SANS(8), INK, "la")

# ---------------------------------------------------------------- DATE CHECK
dy = 966
d.rectangle([12, dy, W - 12, dy + 40], fill=(255, 245, 245), outline=RED, width=2)
dc_title = "DATE CHECK — THESE ARE NOT 26 NOVEMBER · day shown = Nov"
txt(20, dy + 4, dc_title, SANS_B(11), RED, "la")
tw = d.textlength(dc_title, font=SANS_B(11))
txt(20 + tw + 12, dy + 5, "·  ALSO THU 26 NOV: Bangkok refinery blast · Chess Game 3 drawn in 60 moves, 1.5–1.5",
    SANS_B(9), NAVY, "la")
ex = ("Macy's 25 · Kyiv mall 25 · Nigeria girls 24 · India–Nepal aid 23 · Norway oil 13 · Blyth 25 · "
      "India tariff 25 · Gaza rain 25 · Copernicus 2°C 25 · Labuan quake 25 · US jobless 25 · Nvidia 25 · "
      "EU car quotas 24 · Brazil mosquitoes 21 · AFCA 25 · Hasina 24 · Sooryavanshi 204 24 · "
      "Mamdani freeze 25 · Iowa blast 25 · Pongkor flood 23")
for j, ln in enumerate(wrap(ex, SANS(9), 980)[:2]):
    txt(20, dy + 17 + j * 10, ln, SANS(9), INK, "la")

# ---------------------------------------------------------------- footer
txt(12, 1010, "OFFICIAL = authority's own word · CONFIRMED = 2+ outlets · REPORTED = press report · CLAIM = one side's say — Sources: Reuters, AP, BBC, Al Jazeera, Yonhap, FIDE, BoK, UN News, INTERPOL, ONS — drawn in code, not photos.",
    SANS(7), GREY, "la")

img.save("entry.png")
print("saved entry.png", img.size)
