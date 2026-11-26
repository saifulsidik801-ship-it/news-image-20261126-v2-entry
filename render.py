#!/usr/bin/env python3
"""news-image-20261126 v2 — one-day front page, drawn in code (PIL only, no photos).
36 stories: 3 heroes + 10 mids + 23 list. All Nov 26 2026 only."""
from PIL import Image, ImageDraw, ImageFont
import textwrap, math

W, H = 1024, 1024
FD = "/usr/share/fonts/truetype/dejavu/"
def F(name, s): return ImageFont.truetype(FD + name, s)
SERIF_B = lambda s: F("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: F("DejaVuSerif.ttf", s)
SANS_B = lambda s: F("DejaVuSans-Bold.ttf", s)
SANS = lambda s: F("DejaVuSans.ttf", s)

NAVY = (15, 42, 74); PAPER = (247, 243, 232); RED = (185, 28, 28)
INK = (20, 20, 20); GREY = (90, 90, 90); GOLD = (200, 160, 40)
CREAM = (250, 246, 236)

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

def badge(x, y, label, fill):
    f = SANS_B(11)
    w = d.textlength(label, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 16], 3, fill=fill)
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w

def skyline(dr, x0, y0, x1, y1, night=True, lit=True):
    bg = (18, 30, 58) if night else (150, 200, 230)
    dr.rectangle([x0, y0, x1, y1], fill=bg)
    import random
    rnd = random.Random(7)
    x = x0 + 4
    while x < x1 - 14:
        bw = rnd.randint(14, 30); bh = rnd.randint(8, max(9, int((y1 - y0) * 3 // 4)))
        dr.rectangle([x, y1 - bh, x + bw, y1], fill=(40, 55, 90) if night else (90, 120, 150))
        if lit:
            for wy in range(y1 - bh + 5, y1 - 4, 10):
                for wx in range(x + 3, x + bw - 3, 8):
                    if rnd.random() < 0.5:
                        dr.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 210, 90))
        x += bw + 3

def scene(dr, kind, x0, y0, x1, y1):
    """Draw a scene illustration inside box. Each kind is a distinct flat scene."""
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if kind == "parade":  # Macy's: storm sky, balloon, buildings
        dr.rectangle([x0, y0, x1, y1], fill=(38, 52, 86))
        skyline(dr, x0, y1 - h * 0.45, x1, y1)
        dr.ellipse([cx - 52, y0 + 8, cx + 52, y0 + 52], fill=(220, 60, 60))
        dr.ellipse([cx - 30, y0 + 44, cx - 8, y0 + 58], fill=(220, 60, 60))
        dr.ellipse([cx + 8, y0 + 44, cx + 30, y0 + 58], fill=(220, 60, 60))
        for i, (rx, ry) in enumerate([(x0 + 20, y0 + 14), (x0 + 60, y0 + 30), (x1 - 40, y0 + 18)]):
            dr.line([rx, ry, rx + 14, ry + 22], fill=(180, 200, 230), width=2)
        dr.rectangle([x0, y1 - 22, x1, y1 - 14], fill=(200, 40, 40))
        txt(cx, y1 - 20, "POSTPONED TO SATURDAY", SANS_B(13), (255, 255, 255), "ma")
    elif kind == "riyadh":  # night skyline, missile arcs, intercept bursts
        dr.rectangle([x0, y0, x1, y1], fill=(12, 22, 48))
        skyline(dr, x0, y1 - h * 0.5, x1, y1)
        dr.arc([x0 + 10, y0 + 6, x1 - 60, y0 + h * 0.75], 200, 330, fill=(255, 200, 60), width=3)
        dr.arc([x0 + 60, y0 + 20, x1 - 10, y0 + h * 0.9], 210, 320, fill=(255, 120, 60), width=3)
        for bx, by in [(x1 - 70, y0 + 26), (x0 + 60, y0 + 40)]:
            for ang in range(0, 360, 45):
                dx, dy = int(14 * math.cos(math.radians(ang))), int(14 * math.sin(math.radians(ang)))
                dr.line([bx, by, bx + dx, by + dy], fill=(255, 220, 80), width=2)
            dr.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(255, 240, 150))
        txt(x0 + 8, y0 + 6, "2 MISSILES DOWN", SANS_B(13), (255, 220, 80), "la")
    elif kind == "mumbai":  # candles / diyas row, Gateway-ish arch
        dr.rectangle([x0, y0, x1, y1], fill=(245, 222, 170))
        dr.rectangle([cx - 46, y0 + 10, cx + 46, y1 - 34], fill=(190, 120, 60))
        dr.arc([cx - 30, y0 + 22, cx + 30, y0 + 82], 180, 360, fill=(245, 222, 170), width=6)
        for i in range(7):
            fx = x0 + 14 + i * ((w - 28) // 6)
            dr.ellipse([fx - 8, y1 - 30, fx + 8, y1 - 18], fill=(230, 140, 40))
            dr.ellipse([fx - 3, y1 - 40, fx + 3, y1 - 30], fill=(255, 200, 60))
        txt(cx, y0 + 4, "18 YEARS", SANS_B(13), (140, 40, 20), "ma")
    elif kind == "eu":  # EU circle of stars + building
        dr.rectangle([x0, y0, x1, y1], fill=(30, 60, 140))
        for i in range(12):
            a = math.radians(i * 30 - 90)
            sx, sy = cx + int(w * 0.32 * math.cos(a)), cy + int(h * 0.30 * math.sin(a))
            dr.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 215, 0))
        dr.ellipse([cx - 26, cy - 18, cx + 26, cy + 18], fill=(20, 40, 100))
        txt(cx, cy - 8, "EU 27", SANS_B(16), (255, 255, 255), "ma")
    elif kind == "chess":  # board + clocks
        dr.rectangle([x0, y0, x1, y1], fill=(60, 50, 40))
        bs = min(w, h) - 16; bx, by = cx - bs // 2, y0 + 8
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 0:
                    dr.rectangle([bx + c * bs // 8, by + r * bs // 8, bx + (c + 1) * bs // 8, by + (r + 1) * bs // 8], fill=(240, 230, 210))
        dr.ellipse([bx + bs // 8 * 3, by + bs // 8 * 3, bx + bs // 8 * 4.4, by + bs // 8 * 4.4], fill=(20, 20, 20))
        dr.ellipse([bx + bs // 8 * 5, by + bs // 8 * 5, bx + bs // 8 * 6.4, by + bs // 8 * 6.4], fill=(255, 255, 255))
        txt(cx, y1 - 16, "GAME 3 · 1–1", SANS_B(13), (255, 255, 255), "ma")
    elif kind == "bok":  # bank building + rising arrow
        dr.rectangle([x0, y0, x1, y1], fill=(220, 235, 245))
        dr.rectangle([cx - 40, y0 + 26, cx + 40, y1 - 8], fill=(200, 210, 220))
        dr.polygon([(cx - 48, y0 + 26), (cx + 48, y0 + 26), (cx, y0 + 8)], fill=(40, 70, 110))
        for i in range(4):
            dr.rectangle([cx - 34 + i * 18, y0 + 34, cx - 22 + i * 18, y1 - 8], fill=(255, 255, 255))
        dr.line([x0 + 10, y1 - 20, cx, y0 + 34, x1 - 12, y0 + 16], fill=(20, 140, 60), width=4)
        dr.polygon([(x1 - 12, y0 + 16), (x1 - 26, y0 + 14), (x1 - 14, y0 + 28)], fill=(20, 140, 60))
        txt(x1 - 8, y0 + 4, "3.25%", SANS_B(16), (20, 140, 60), "ra")
    elif kind == "kyiv":  # night city, fire, smoke
        dr.rectangle([x0, y0, x1, y1], fill=(16, 26, 52))
        skyline(dr, x0, y1 - h * 0.45, x1, y1)
        fx, fy = cx + 20, y1 - h * 0.45
        for r, col in [(26, (255, 120, 30)), (18, (255, 180, 40)), (10, (255, 240, 120))]:
            dr.ellipse([fx - r, fy - r, fx + r, fy + r], fill=col)
        dr.ellipse([x0 + 16, y0 + 8, x0 + 34, y0 + 26], fill=(120, 120, 120))
        dr.ellipse([x0 + 30, y0 + 4, x0 + 52, y0 + 22], fill=(90, 90, 90))
        txt(x0 + 8, y1 - 18, "4 HURT", SANS_B(13), (255, 255, 255), "la")
    elif kind == "kim":  # atom orbits + red star
        dr.rectangle([x0, y0, x1, y1], fill=(20, 20, 30))
        for a in (0, 60, 120):
            dr.arc([cx - 40, cy - 16, cx + 40, cy + 16], 0, 360, fill=(200, 60, 60), width=2)
        dr.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 220, 60))
        for dx, dy in [(-38, -14), (38, 14), (0, 18)]:
            dr.ellipse([cx + dx - 4, cy + dy - 4, cx + dx + 4, cy + dy + 4], fill=(240, 240, 240))
        txt(x0 + 8, y0 + 4, "KCNA", SANS_B(12), (255, 255, 255), "la")
    elif kind == "school":  # green field, figures, schoolhouse
        dr.rectangle([x0, y0, x1, y1], fill=(140, 200, 140))
        dr.rectangle([x0 + 8, y0 + 8, x0 + 44, y0 + 34], fill=(200, 90, 60))
        dr.polygon([(x0 + 4, y0 + 10), (x0 + 48, y0 + 10), (x0 + 26, y0 - 2)], fill=(120, 50, 40))
        for i in range(4):
            fx = cx - 30 + i * 20
            dr.ellipse([fx - 5, cy - 6, fx + 5, cy + 4], fill=(60, 40, 30))
            dr.rectangle([fx - 5, cy + 4, fx + 5, cy + 18], fill=(255, 255, 255))
        txt(cx, y1 - 16, "24 FREED", SANS_B(13), (20, 80, 20), "ma")
    elif kind == "tube":  # roundel + train
        dr.rectangle([x0, y0, x1, y1], fill=(230, 235, 240))
        dr.rectangle([x0, y1 - 30, x1, y1 - 12], fill=(40, 80, 160))
        for wx in range(x0 + 10, x1 - 10, 22):
            dr.rectangle([wx, y1 - 28, wx + 12, y1 - 18], fill=(255, 255, 255))
        dr.ellipse([cx - 26, y0 + 6, cx + 26, y0 + 38], outline=(200, 0, 0), width=6)
        dr.rectangle([cx - 34, y0 + 18, cx + 34, y0 + 26], fill=(0, 40, 120))
        txt(cx, y0 + 42, "8 STRIKES", SANS_B(13), (200, 0, 0), "ma")
    elif kind == "stocks":  # rebound chart
        dr.rectangle([x0, y0, x1, y1], fill=(235, 245, 235))
        pts = [(x0 + 8, y0 + h * 0.75), (x0 + w * 0.3, y0 + h * 0.8), (x0 + w * 0.55, y0 + h * 0.55), (x0 + w * 0.8, y0 + h * 0.35), (x1 - 8, y0 + h * 0.2)]
        dr.line(pts, fill=(20, 140, 60), width=4)
        dr.polygon([(x1 - 8, y0 + h * 0.2), (x1 - 22, y0 + h * 0.2), (x1 - 10, y0 + h * 0.08)], fill=(20, 140, 60))
        txt(x0 + 8, y0 + 4, "KOSPI +2%", SANS_B(14), (20, 140, 60), "la")
    elif kind == "taiwan":  # flag bars + tariff table
        dr.rectangle([x0, y0, x1, y1], fill=(240, 240, 245))
        for i, col in enumerate([(200, 40, 40), (255, 200, 60), (40, 120, 60), (40, 80, 180)]):
            dr.rectangle([x0 + 8 + i * (w // 4), y0 + 8, x0 + 8 + (i + 1) * (w // 4) - 4, y0 + h // 2], fill=col)
        dr.rectangle([x0 + 8, y0 + h // 2 + 6, x1 - 8, y1 - 8], fill=(255, 255, 255), outline=(150, 150, 150))
        txt(cx, y0 + h // 2 + 10, "TOP RATE 15%", SANS_B(14), (20, 20, 20), "ma")
    elif kind == "taipo":  # memorial candles + flowers
        dr.rectangle([x0, y0, x1, y1], fill=(40, 40, 55))
        for i in range(5):
            fx = x0 + 16 + i * ((w - 32) // 4)
            dr.rectangle([fx - 4, y1 - 26, fx + 4, y1 - 10], fill=(240, 230, 200))
            dr.ellipse([fx - 3, y1 - 36, fx + 3, y1 - 26], fill=(255, 200, 60))
        for i in range(4):
            dr.ellipse([x0 + 22 + i * 24, y0 + 10, x0 + 34 + i * 24, y0 + 22], fill=(220, 80, 120))
        txt(cx, y0 + 30, "168", SANS_B(16), (255, 255, 255), "ma")

# ---------- header ----------
d.rectangle([0, 0, W, 24], fill=NAVY)
txt(512, 4, "THE WORLD IN ONE DAY  ·  36 STORIES  ·  10 REGIONS  ·  18 FIELDS  ·  ALL FIRST REPORTED ON THURSDAY 26 NOVEMBER 2026",
    SANS_B(12), (255, 255, 255), "ma")
masthead = "Thursday 26 November 2026"
mh_size = 64
while mh_size > 30 and d.textlength(masthead, font=SERIF_B(mh_size)) > 980:
    mh_size -= 1
txt(512, 30, masthead, SERIF_B(mh_size), NAVY, "ma")
lede = "Nor'easter grounds Macy's 100th parade  ·  Missiles over Riyadh  ·  India marks 18 years since 26/11"
lede_size = 20
while lede_size > 12 and d.textlength(lede, font=SERIF(lede_size)) > 1000:
    lede_size -= 1
txt(512, 102, lede, SERIF(lede_size), RED, "ma")
# region strip
regs = [("Europe", 8), ("East Asia", 6), ("N. America", 6), ("South Asia", 5), ("Oceania", 4),
        ("Middle East", 2), ("Africa", 2), ("SE Asia", 1), ("Latin Am", 1), ("World", 1)]
x = 12
for name, n in regs:
    lab = f"{name} {n}"
    wdt = d.textlength(lab, font=SANS_B(12)) + 14
    d.rounded_rectangle([x, 132, x + wdt, 152], 4, fill=REGION[name])
    d.text((x + 7, 136), lab, font=SANS_B(12), fill=(255, 255, 255))
    x += wdt + 5
# number strip
nums = [("100", "100th Macy's parade,\nfirst weather delay"), ("2", "missiles downed\nover Riyadh"),
        ("18", "years since\nthe 26/11 attacks"), ("3.25%", "Bank of Korea\nkey rate"),
        ("4", "hurt in Kyiv\nmall strike"), ("24", "schoolgirls freed\nin Nigeria")]
cw = (W - 24) // 6
for i, (num, lab) in enumerate(nums):
    x0 = 12 + i * cw
    d.rectangle([x0, 158, x0 + cw - 4, 204], fill=(255, 255, 255), outline=(200, 190, 170))
    txt(x0 + (cw - 4) // 2, 160, num, SERIF_B(24), NAVY, "ma")
    ll = lab.split("\n")
    txt(x0 + (cw - 4) // 2, 186, ll[0], SANS(9), GREY, "ma")
    txt(x0 + (cw - 4) // 2, 195, ll[1], SANS(9), GREY, "ma")
# timeline
d.rectangle([0, 210, W, 232], fill=NAVY)
tl = "THE DAY IN UTC   00:50  Bank of Korea hikes   ·   09:00  EU summit opens   ·   14:00  Chess Game 3   ·   15:00  NYC wind alert   ·   18:00  NFL games"
txt(12, 215, tl, SANS_B(11), (255, 255, 255), "la")

# ---------- heroes ----------
HEROES = [
    dict(n=1, kind="parade", region="N. America", field="CULTURE", head="Nor'easter grounds Macy's 100th parade",
         body="The 100th parade moves to Saturday — the first weather delay in a century. Gusts to 60 mph.",
         why="WHY: a century-old ritual stopped by weather.", src="Reuters · AP", badge="CONFIRMED"),
    dict(n=2, kind="riyadh", region="Middle East", field="WAR", head="Saudi defences down two missiles over Riyadh",
         body="Two ballistic missiles aimed at the capital are destroyed early Thursday; a drone is downed near Jeddah.",
         why="WHY: a second straight day of strikes on Riyadh.", src="Reuters · Al Jazeera", badge="OFFICIAL"),
    dict(n=3, kind="mumbai", region="South Asia", field="REMEMBRANCE", head="India marks 18 years since 26/11",
         body="Tributes for the 166 killed in the 2008 Mumbai attacks, as the nation marks 77 years of its Constitution.",
         why="WHY: the date itself is the anniversary.", src="PTI · PIB", badge="OFFICIAL"),
]
hy, hh = 238, 208
for i, h in enumerate(HEROES):
    x0 = 12 + i * 336; x1 = x0 + 328
    d.rectangle([x0, hy, x1, hy + hh], fill=(255, 255, 255), outline=(190, 180, 160))
    scene(d, h["kind"], x0 + 4, hy + 4, x1 - 4, hy + 100)
    d.ellipse([x0 + 8, hy + 104, x0 + 30, hy + 126], fill=RED)
    txt(x0 + 19, hy + 106, str(h["n"]), SANS_B(13), (255, 255, 255), "ma")
    txt(x0 + 36, hy + 108, f"{h['region'].upper()} — {h['field']}", SANS_B(10), RED, "la")
    for j, ln in enumerate(wrap(h["head"], SERIF_B(15), 306)):
        txt(x0 + 8, hy + 128 + j * 17, ln, SERIF_B(15), INK, "la")
    bl = wrap(h["body"], SANS(10), 312)
    for j, ln in enumerate(bl[:2]):
        txt(x0 + 8, hy + 164 + j * 11, ln, SANS(10), INK, "la")
    txt(x0 + 8, hy + hh - 20, h["why"], SANS(9), GREY, "la")
    txt(x0 + 8, hy + hh - 10, "SOURCE: " + h["src"], SANS(9), GREY, "la")
    badge(x1 - 92, hy + hh - 12, h["badge"], (0, 110, 60) if h["badge"] != "OFFICIAL" else NAVY)

# ---------- mids ----------
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
mw, mh = 196, 134
for r in range(2):
    for c in range(5):
        m = MIDS[r * 5 + c]
        x0 = 12 + c * 202; y0 = 452 + r * (mh + 6); x1 = x0 + mw
        d.rectangle([x0, y0, x1, y0 + mh], fill=(255, 255, 255), outline=(190, 180, 160))
        scene(d, m["kind"], x0 + 3, y0 + 3, x1 - 3, y0 + 50)
        d.ellipse([x0 + 5, y0 + 53, x0 + 23, y0 + 71], fill=RED)
        txt(x0 + 14, y0 + 55, str(m["n"]), SANS_B(11), (255, 255, 255), "ma")
        txt(x0 + 27, y0 + 56, f"{m['region'].upper()} — {m['field']}", SANS_B(9), RED, "la")
        for j, ln in enumerate(wrap(m["head"], SERIF_B(13), 182)):
            txt(x0 + 5, y0 + 73 + j * 14, ln, SERIF_B(13), INK, "la")
        bl = wrap(m["body"], SANS(10), 186)
        for j, ln in enumerate(bl[:2]):
            txt(x0 + 5, y0 + 99 + j * 10, ln, SANS(10), INK, "la")
        txt(x0 + 5, y0 + mh - 10, "SOURCE: " + m["src"], SANS(8), GREY, "la")
        badge(x1 - 78, y0 + mh - 12, m["badge"], (0, 110, 60) if m["badge"] != "OFFICIAL" else NAVY)

# ---------- map + list ----------
my = 732
d.rectangle([12, my, 308, my + 154], fill=(225, 235, 240), outline=(190, 180, 160))
txt(16, my + 4, "WHERE IT HAPPENED — PINS 1–13", SANS_B(11), NAVY, "la")
# simple world map: rough continent blobs
land = (190, 185, 160)
d.ellipse([30, my + 40, 90, my + 90], fill=land)          # N America
d.ellipse([95, my + 95, 130, my + 135], fill=land)        # S America
d.ellipse([140, my + 35, 180, my + 75], fill=land)        # Europe
d.ellipse([175, my + 70, 225, my + 125], fill=land)       # Africa
d.ellipse([205, my + 30, 290, my + 85], fill=land)        # Asia
d.ellipse([255, my + 115, 295, my + 145], fill=land)      # Oceania
pins = [(1, 55, 60), (2, 196, 56), (3, 228, 74), (4, 148, 46), (5, 164, 64), (6, 238, 48),
        (7, 144, 64), (8, 252, 60), (9, 198, 96), (10, 172, 46), (11, 232, 64), (12, 244, 72), (13, 264, 56)]
pin_regions = {1: "N. America", 2: "Middle East", 3: "South Asia", 4: "Europe", 5: "Europe",
               6: "East Asia", 7: "Europe", 8: "East Asia", 9: "Africa", 10: "Europe",
               11: "East Asia", 12: "East Asia", 13: "East Asia"}
for n, px, py in pins:
    col = REGION[pin_regions[n]]
    ay = my + py
    d.ellipse([px - 8, ay - 8, px + 8, ay + 8], fill=col, outline=(255, 255, 255))
    txt(px, ay - 7, str(n), SANS_B(9), (255, 255, 255), "ma")
txt(16, my + 138, "Pins = story numbers 1–13 · colours = regions", SANS(9), GREY, "la")

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
lx = 318
txt(lx, my + 4, "ALSO ON THURSDAY 26 NOVEMBER — 23 MORE STORIES", SANS_B(12), NAVY, "la")
d.line([lx, my + 20, W - 12, my + 20], fill=NAVY, width=2)
for i, (n, head, src, b, reg) in enumerate(LIST):
    col = i % 2; row = i // 2
    x0 = lx + col * 348; y0 = my + 26 + row * 11
    colr = REGION[reg]
    d.rectangle([x0, y0, x0 + 16, y0 + 11], fill=colr)
    txt(x0 + 8, y0, str(n), SANS_B(8), (255, 255, 255), "ma")
    s = f"{head} [{b}] — {src}"
    txt(x0 + 20, y0, s, SANS(9), INK, "la")

# ---------- DATE CHECK ----------
dy = 892
d.rectangle([12, dy, W - 12, dy + 86], fill=(255, 245, 245), outline=RED, width=2)
txt(20, dy + 4, "DATE CHECK — THESE ARE NOT 26 NOVEMBER", SANS_B(12), RED, "la")
txt(20, dy + 20, "Every story above happened or was first reported on Thursday 26 November 2026.", SANS_B(11), INK, "la")
ex = ("Left out as earlier news:  Cairo tanker fire (Wed 25)  ·  Solomon Islands treaty (Wed 25)  ·  Shenzhou-24 docking (Wed 25)  ·  "
      "US tariff announcement (Wed 25)  ·  Bangladesh wage rise (Wed 25)  ·  Ras Tanura claim (Wed 25)  ·  "
      "Gaza security chief killed (Wed 25)  ·  US GDP +4.3% (Wed 25)  ·  N. Korea expels Swiss envoy (Wed 25)  ·  "
      "Nvidia reinstates Huang (Mon 23)  ·  Real Madrid 5–1 PSV (Tue 24)  ·  COP31 collapse (Sun 22).")
for j, ln in enumerate(wrap(ex, SANS(10), 980)):
    txt(20, dy + 36 + j * 12, ln, SANS(10), INK, "la")
txt(20, dy + 72, "Not yet:  Chess Game 3 result  ·  EU budget deal (Fri 27 Nov)  ·  Taiwan vote (Sat 28 Nov).", SANS_B(10), RED, "la")

# ---------- footer ----------
txt(12, 984, "OFFICIAL = an authority's own word  ·  CONFIRMED = 2+ major outlets  ·  REPORTED = press report  ·  CLAIM = one side's say, unverified",
    SANS(10), GREY, "la")
txt(12, 996, "Sources: Reuters, AP, AFP, BBC, Al Jazeera, Yonhap, FIDE, Bank of Korea, EU Council, PTI — all reported 26 November 2026.  Every drawing original — drawn in code, not photos.",
    SANS(10), GREY, "la")
txt(512, 1008, "THE WORLD IN ONE DAY  ·  26 NOV 2026  ·  36 STORIES  ·  10 REGIONS", SANS_B(9), NAVY, "ma")

img.save("entry.png")
print("saved entry.png", img.size)
