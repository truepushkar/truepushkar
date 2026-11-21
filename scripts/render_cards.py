#!/usr/bin/env python3
"""Render the pixel-themed animated SVG cards for the truepushkar GitHub profile README
(headline + inline tech chips, profile.yaml, Technology, GitHub Activity, compact socials at the bottom).

Place this repo layout at github.com/truepushkar/truepushkar:
    README.md        <- generated
    cards/*.svg      <- generated
    scripts/render_cards.py

Run from the repo root:    python scripts/render_cards.py
STATIC=1 python ...        renders final frames (no animation) for screenshots.

SIZING RULE
  GitHub's README column is fluid: ~428px wide at a 780px viewport, ~592px at 1000px.
  An <img> shown narrower than its authored width is scaled DOWN and the type gets
  illegible, so every card is authored at the exact pixel width it renders at in the
  narrow case:
        FULL = 428   (legacy)
        WIDE = 880   (headings, technology, activity, divider)  -> width=WIDE_W (880px, fixed)
        BTN  = 84    (social buttons, five per row)          -> width="19.6%"
  Wider columns scale cards UP slightly, which stays sharp. The five buttons are written
  back-to-back with no whitespace between the tags so 5 x 19.6% never wraps.

Everything works inside <img> on GitHub: inline <style>, CSS keyframes,
prefers-color-scheme and prefers-reduced-motion. No scripts, no external requests,
no web fonts (the pixel lettering is drawn from rects).
"""
import html
import math
import os
import textwrap

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CARDS = os.path.join(ROOT, "cards")
STATIC = os.environ.get("STATIC") == "1"

FULL, WIDE, BTN, SHADOW = 428, 880, 84, 4
RAW = "https://raw.githubusercontent.com/truepushkar/truepushkar/main/cards"
PROFILE = "https://github.com/truepushkar"

SERIF = "Georgia,'Iowan Old Style','Times New Roman',serif"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace"

# ---- content (copied from the previous README) ---------------------------------------
ROLE = "Backend & Web Developer"
STACK = "Python \u00b7 Flask \u00b7 Jinja"
TAGLINE = "Building software that is simple, useful, and actually gets used."

# label, url, accent, sprite
SOCIALS = [
    ("GITHUB", "https://github.com/truepushkar", "blue", "github"),
    ("YOUTUBE", "https://www.youtube.com/@truepushkar", "red", "youtube"),
    ("X", "https://x.com/TruePushkar", "teal", "x"),
    ("DISCORD", "https://discord.com/users/1141179236309287082", "blue", "discord"),
    ("EMAIL", "mailto:truepushkar@gmail.com", "amber", "email"),
]

SPRITES = {
    "github": ["10000001", "11000011", "11111111", "10111101", "11111111", "01111110", "01011010", "11000011"],
    "youtube": ["11111111", "10111111", "10011111", "10001111", "10011111", "10111111", "11111111", "00000000"],
    "x": ["10000001", "01000010", "00100100", "00011000", "00011000", "00100100", "01000010", "10000001"],
    "discord": ["01111110", "11111111", "11011011", "11011011", "11111111", "11111111", "01100110", "00000000"],
    "email": ["11111111", "11000011", "10100101", "10011001", "10000001", "10000001", "11111111", "00000000"],
}

# the profile.yaml card (same six lines as before; values re-checked against ALL-REPOS.md)
YAML = [
    ("focus:", "Backend & Web Development"),
    ("stack:", "Python \u00b7 Flask \u00b7 Jinja"),
    ("also:", "TypeScript \u00b7 React \u00b7 Workers"),
    ("org:", "@nullstacks \u00b7 since 2022"),
    ("building:", "Small, sharp, composable tools"),
]

# technology chips; group decides the accent. Updated to what the 29 public repos actually use.
TECH = [
    ("Python", "backend"), ("Flask", "backend"), ("FastAPI", "backend"), ("MongoDB", "backend"),
    ("MySQL", "backend"), ("SQLite", "backend"),
    ("HTML", "frontend"), ("CSS", "frontend"), ("JavaScript", "frontend"), ("TypeScript", "frontend"),
    ("React", "frontend"), ("Tailwind", "frontend"),
    ("Cloudflare Workers", "infra"), ("Docker", "infra"), ("Git", "infra"), ("GitHub Actions", "infra"),
    ("Vercel", "infra"), ("PowerShell", "infra"),
]
GROUPS = {"backend": ("BACKEND", "blue"), "frontend": ("FRONTEND", "amber"), "infra": ("INFRA & TOOLS", "teal")}

# dynamic stat services from the old README (recoloured to the pixel palette)
PAL = "bg_color=12171e&title_color=6ea0ff&text_color=ecebe6&icon_color=6ea0ff&hide_border=true&border_radius=0"

# ---- 5x7 bitmap font (drawn from rects, so no font file is needed) ------------------
FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000", "-": "00000 00000 00000 11111 00000 00000 00000",
    "_": "00000 00000 00000 00000 00000 00000 11111", "&": "01100 10010 10100 01000 10101 10010 01101",
    ",": "00000 00000 00000 00000 00110 00100 01000", "'": "00100 00100 01000 00000 00000 00000 00000",
    ".": "00000 00000 00000 00000 00000 01100 01100",
}


CSS = """
:root{--bg:#fbfaf6;--card:#ffffff;--ink:#17171a;--mute:#6b6b73;--line:#d9d5c8;
--blue:#2f6fed;--red:#e5484d;--amber:#c98100;--teal:#12a37f}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--card:#12171e;--ink:#ecebe6;--mute:#8b949e;--line:#2b323d;
--blue:#6ea0ff;--red:#ff7b7f;--amber:#f5b942;--teal:#3ddbb0}}
path,rect,line{shape-rendering:crispEdges}
text{font-family:%(sans)s;fill:var(--ink)}
.serif{font-family:%(serif)s}.mono{font-family:%(mono)s}.mute{fill:var(--mute)}
.ink{fill:var(--ink)}
.rise{animation:rise .7s cubic-bezier(.2,.8,.2,1) var(--d,0s) backwards}
.pop{transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.2,1.4,.4,1) var(--d,0s) backwards}
.tick{opacity:0;animation:tick .13s linear var(--d,0s) both}
.final{animation:fade .3s ease-out var(--d,0s) backwards}
.blink{animation:blink 1.1s steps(1) infinite}
.pulse{animation:pulse 2s steps(2) infinite}
.twinkle{animation:twinkle 3s steps(1) var(--d,0s) infinite}
.march{animation:march 1s steps(2) infinite}
.flick{animation:flick .7s steps(1) var(--d,0s) backwards}
.title{animation:flick .7s steps(1) var(--d,0s) backwards,glint 6s linear var(--g,0s) infinite}
.orbit{opacity:.4;transform-box:fill-box;transform-origin:center;animation:orbit 3.6s linear var(--d,0s) infinite}
.zip{opacity:.4;transform-box:fill-box;transform-origin:center;animation:zip 4.2s linear var(--d,0s) infinite}
.wave{opacity:.35;animation:wave 3.2s linear var(--d,0s) infinite}
.sweep{transform-box:fill-box;transform-origin:center;animation:sweep 7s linear var(--d,0s) infinite}
.cell{transform-box:fill-box;transform-origin:center;animation:cellin .5s cubic-bezier(.2,1.5,.4,1) var(--d,0s) backwards,scan 9s linear var(--s,0s) infinite}
.cellbg{transform-box:fill-box;transform-origin:center;animation:cellin .5s cubic-bezier(.2,1.5,.4,1) var(--d,0s) backwards,scanbg 9s linear var(--s,0s) infinite}
.ping{opacity:0;transform-box:fill-box;transform-origin:center;animation:ping 3.6s linear var(--d,0s) infinite}
@keyframes cellin{from{opacity:0;transform:scale(0)}}
@keyframes scan{0%%,6%%,100%%{transform:scale(1);fill:var(--teal)}1.5%%{transform:scale(1.55);fill:var(--ink)}3%%{transform:scale(1.15);fill:var(--teal)}}
@keyframes scanbg{0%%,6%%,100%%{fill:var(--line)}1.5%%{fill:var(--mute)}}
@keyframes ping{0%%{opacity:.9;transform:scale(1)}60%%,100%%{opacity:0;transform:scale(2.4)}}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@keyframes fade{from{opacity:0}}
@keyframes tick{0%%,99%%{opacity:1}100%%{opacity:0}}
@keyframes blink{50%%{opacity:0}}
@keyframes pulse{50%%{opacity:.3}}
@keyframes twinkle{0%%,100%%{opacity:.15}50%%{opacity:.9}}
@keyframes march{to{stroke-dashoffset:-8}}
@keyframes flick{0%%{opacity:0}20%%{opacity:1}35%%{opacity:0}55%%{opacity:1}70%%{opacity:0}100%%{opacity:1}}
@keyframes glint{0%%{fill:var(--blue)}9%%{fill:var(--ink)}100%%{fill:var(--ink)}}
@keyframes orbit{0%%{opacity:1;transform:scale(1.18)}22%%{opacity:.4;transform:scale(1)}100%%{opacity:.4}}
@keyframes zip{0%%{opacity:1;transform:scale(1.3)}14%%{opacity:.4;transform:scale(1)}100%%{opacity:.4}}
@keyframes wave{0%%{opacity:1}20%%{opacity:.35}100%%{opacity:.35}}
@keyframes sweep{0%%{transform:scale(1.8)}3%%{transform:scale(1)}100%%{transform:scale(1)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.tick{opacity:0}.orbit,.zip,.wave{opacity:1}}
""" % dict(sans=SANS, serif=SERIF, mono=MONO)

if STATIC:
    CSS += "*{animation:none!important}.tick{opacity:0}.orbit,.zip,.wave{opacity:1}"


# ---- helpers ------------------------------------------------------------------------
def esc(s):
    return html.escape(s, quote=False)


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title>'
        f"<style>{CSS}</style>{body}</svg>"
    )


def write(name, content):
    os.makedirs(CARDS, exist_ok=True)
    with open(os.path.join(CARDS, name), "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"wrote {name:28s} {len(content):6d} bytes")


def pixbox(x, y, w, h, n=4):
    """Rectangle with single-pixel stepped corners (retro 'rounded' look)."""
    return (f"M{x+n} {y}H{x+w-n}V{y+n}H{x+w}V{y+h-n}H{x+w-n}V{y+h}H{x+n}V{y+h-n}H{x}V{y+n}H{x+n}Z")


def frame(w, h, accent):
    """Card body (w-SHADOW x h-SHADOW) with a hard, offset accent shadow."""
    bw, bh = w - SHADOW, h - SHADOW
    return (
        f'<path d="{pixbox(SHADOW, SHADOW, bw, bh)}" style="fill:var(--{accent});opacity:.28"/>'
        f'<path d="{pixbox(1, 1, bw - 2, bh - 2)}" fill="var(--card)" stroke="var(--line)" stroke-width="2"/>'
    )


def glyph_d(ch, x, y, cell, pitch, bold=False):
    rows = FONT[ch].split()
    lit = set()
    for r, row in enumerate(rows):
        for c, bit in enumerate(row):
            if bit == "1":
                lit.add((r, c))
                if bold:  # thicken every stroke by one pixel to the right
                    lit.add((r, c + 1))
    # pixels advance by `cell` on both axes so the letterform is solid; `pitch`
    # (cell+gap) is the gap BETWEEN letters, applied by the callers.
    return "".join(f"M{x + c * cell} {y + r * cell}h{cell}v{cell}h-{cell}z" for r, c in sorted(lit))


def text_width(text, cell, gap, bold=False):
    adv = (6 if bold else 5) * cell + gap  # 5 glyph columns (6 when bold) + letter gap
    return len(text) * adv - gap


def pixel_text(text, x, y, cell, gap, attrs="", per_letter=None, bold=False):
    """One <path> per letter. per_letter(i) returns extra attributes for that letter."""
    adv = (6 if bold else 5) * cell + gap
    out = []
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        extra = per_letter(i) if per_letter else ""
        out.append(f'<path {attrs} {extra} d="{glyph_d(ch, x + i * adv, y, cell, cell + gap, bold)}"/>')
    return "".join(out)


def sprite(rows, x, y, cell, col, d0):
    d = []
    for r, row in enumerate(rows):
        for c, bit in enumerate(row):
            if bit == "1":
                d.append(f"M{x + c * cell} {y + r * cell}h{cell}v{cell}h-{cell}z")
    return f'<path class="pop" style="--d:{d0:.2f}s;fill:var(--{col})" d="{"".join(d)}"/>'


def chip(x, y, label, size=10):
    w = round(len(label) * 0.6 * size + 14)
    return w, (
        f'<rect x="{x}" y="{y}" width="{w}" height="20" fill="none" stroke="var(--line)" stroke-width="2"/>'
        f'<text class="mono mute" x="{x + 7}" y="{y + 14}" font-size="{size}">{esc(label)}</text>'
    )


# ---- headline (428 wide): big bold pixel title, white then grey, like a README hero line -----
HEADLINE = [  # (text, number of leading chars drawn in ink; the rest is muted)
    ("HI, I'M PUSHKAR", 15),
    ("- A BACKEND & WEB DEVELOPER.", 1),
]
HEADLINE_ALT = "Hi, I'm Pushkar \u2014 A Backend & Web Developer."


def headline_plain():
    W, cell, gap, lh = WIDE, 4, 1, 52
    pitch = cell + gap
    adv = 6 * cell + gap  # bold glyphs are 6 cells wide, plus the letter gap
    H = len(HEADLINE) * lh + 6
    out = []
    n = 0
    for li, (text, n_ink) in enumerate(HEADLINE):
        y = 4 + li * lh
        for i, ch in enumerate(text):
            if ch == " ":
                continue
            cls = "ink" if i < n_ink else "mute"
            out.append(f'<path class="{cls} flick" style="--d:{0.1 + n * 0.04:.2f}s" d="{glyph_d(ch, 2 + i * adv, y, cell, pitch, True)}"/>')
            n += 1
    last = HEADLINE[-1][0]
    out.append(f'<rect class="blink" x="{2 + len(last) * adv}" y="{4 + (len(HEADLINE) - 1) * lh}" width="{5 * cell + 1}" height="{7 * pitch - 1}" fill="var(--blue)"/>')
    return svg(W, H, "".join(out), HEADLINE_ALT)



# ---- hero banner: terminal window + starfield + pixel skyline ---------------------------------
def _rng(seed):
    while True:
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        yield seed / 0x7FFFFFFF


def headline():
    W, H, cell, gap = WIDE, 178, 4, 1
    pitch, adv = cell + gap, 6 * cell + gap
    out = [frame(W, H, "blue")]
    # window chrome (same language as the profile.yaml card)
    for i, col in enumerate(("red", "amber", "teal")):
        out.append(f'<rect x="{16 + i * 12}" y="10" width="7" height="7" fill="var(--{col})"/>')
    out.append('<text class="mono mute" x="64" y="17" font-size="10" letter-spacing="1">~/truepushkar/README.md</text>')
    out.append(f'<line x1="14" y1="24" x2="{W - SHADOW - 14}" y2="24" stroke="var(--line)" stroke-width="2"/>')
    # starfield (kept clear of the text block)
    r = _rng(7)
    stars = 0
    while stars < 46:
        x, y = int(next(r) * (W - 60)) + 28, int(next(r) * 110) + 32
        if (x < 760 and 58 < y < 160) or (x < 150 and y < 62):
            continue
        sz = 2 if next(r) < .7 else 4
        col = ("mute", "blue", "ink", "teal", "amber")[int(next(r) * 5)]
        out.append(f'<rect class="twinkle" style="--d:{next(r) * 3:.2f}s;fill:var(--{col})" x="{x - x % 2}" y="{y - y % 2}" width="{sz}" height="{sz}"/>')
        stars += 1
    # pixel skyline, two layers, right-hand side only so it never fights the headline
    import math
    for layer, (col, op, amp, ph) in enumerate((("line", .9, 44, 0.0), ("blue", .16, 34, 2.1))):
        base = H - SHADOW - 10
        for i in range(0, 11):
            x = 764 + i * 9
            if x + 9 > W - SHADOW - 8:
                break
            hgt = 8 + amp * (0.5 + 0.5 * math.sin(i * .42 + ph)) * (0.55 + 0.45 * math.sin(i * .13 + ph * 2))
            hgt = int(hgt // 4 * 4)
            out.append(f'<rect style="fill:var(--{col});opacity:{op}" x="{x}" y="{base - hgt}" width="9" height="{hgt}"/>')
    # prompt + title
    out.append('<text class="mono" x="24" y="52" font-size="12"><tspan style="fill:var(--teal)">$</tspan><tspan class="mute" dx="8">whoami</tspan></text>')
    lines = [("HI, I'M PUSHKAR", 15), ("- A BACKEND & WEB DEVELOPER.", 1)]
    n = 0
    for li, (text, n_ink) in enumerate(lines):
        y = 66 + li * 52
        for i, ch in enumerate(text):
            if ch == " ":
                continue
            cls = "ink" if i < n_ink else "mute"
            out.append(f'<path class="{cls} flick" style="--d:{0.1 + n * 0.04:.2f}s" d="{glyph_d(ch, 24 + i * adv, y, cell, pitch, True)}"/>')
            n += 1
    last = lines[-1][0]
    out.append(f'<rect class="blink" x="{24 + len(last) * adv}" y="{66 + 52}" width="{5 * cell + 1}" height="{7 * pitch - 1}" fill="var(--blue)"/>')
    return svg(W, H, "".join(out), HEADLINE_ALT)


# ---- inline technology chips (dashed, pixel corners, 8x8 pixel icon) ------------------------
CH = 24  # chip height, authored 1:1 so GitHub never scales the type

# icon palettes: letter -> css colour. '.' is empty.
PAL_ICON = {"b": "var(--blue)", "r": "var(--red)", "a": "var(--amber)", "t": "var(--teal)", "i": "var(--ink)", "m": "var(--mute)"}
ICONS = {
    "Python": ["..bbbb..", "..b.bb..", "..bbbb..", "bbbbbaaa", "aaabbbbb"[::1], "..aaaa..", "..a.aa..", "..aaaa.."],
    "Flask": ["..iiii..", "...ii...", "...ii...", "..iiii..", ".iiiiii.", "iiiiiiii", "iiiiiiii", ".iiiiii."],
    "Jinja": ["..bb.bb.", ".b.....b", ".b.....b", "b.......", ".b.....b", ".b.....b", "..bb.bb.", "........"],
    "MongoDB": ["...t....", "..tt....", ".tttt...", ".tttt...", ".tttt...", "..tt....", "..tt....", "...i...."],
    "MySQL": [".bbbbbb.", "bbbbbbbb", "........", ".bbbbbb.", "bbbbbbbb", "........", ".bbbbbb.", "bbbbbbbb"],
    "SQLite": [".tttttt.", "tttttttt", "........", ".tttttt.", "tttttttt", "........", ".tttttt.", "tttttttt"],
    "FastAPI": ["...ttt..", "..ttt...", ".ttt....", ".tttttt.", "...ttt..", "..ttt...", ".tt.....", "t......."],
    "HTML": ["aaaaaaaa", "aaaaaaaa", "aaiiiiaa", ".aaiiaa.", ".aaaaaa.", "..aaaa..", "...aa...", "........"],
    "CSS": ["bbbbbbbb", "bbbbbbbb", "bbiiiibb", ".bbiibb.", ".bbiibb.", "..bbbb..", "...bb...", "........"],
    "React": ["...bb...", ".bb..bb.", "b..bb..b", "b.bbbb.b", "b.bbbb.b", "b..bb..b", ".bb..bb.", "...bb..."],
    "Tailwind": ["........", "..bbb...", ".bbbbbb.", "bb..bbb.", "...bbb..", "..bbbbbb", ".bbbbbbb", "bb..bbb."],
    "Docker": ["........", ".b.b.b..", ".bbbbbb.", "bbbbbbbb", "bbbbbbb.", ".bbbbbb.", "..bbbb..", "........"],
    "Git": ["...rr...", "..rrrr..", ".rrirrr.", "rrriirrr", "rrrirrrr", ".rrrirr.", "..rrrr..", "...rr..."],
    "GitHub Actions": [".bbbbbb.", "bb.bbbbb", "bb..bbbb", "bb...bbb", "bb..bbbb", "bb.bbbbb", ".bbbbbb.", "........"],
    "Vercel": ["...ii...", "...ii...", "..iiii..", "..iiii..", ".iiiiii.", ".iiiiii.", "iiiiiiii", "iiiiiiii"],
    "PowerShell": ["bbbbbbbb", "biibbbbb", "bbiibbbb", "bbbiibbb", "bbiibbbb", "biibiiib", "bbbbbbbb", "bbbbbbbb"],
    "Cloudflare Workers": ["........", "...aa...", "..aaaa.a", ".aaaaaaa", "aaaaaaaa", "aaaaaaaa", ".aaaaaa.", "........"],
}
# two-letter monogram tiles, drawn with the same 5x7 pixel font (like the JS / TS badges)
TILES = {"TypeScript": ("TS", "blue", "card"), "JavaScript": ("JS", "amber", "card")}


def icon_svg(name, x, y):
    """16x16 icon at (x, y): an 8x8 sprite at 2px per cell, or a monogram tile."""
    if name in TILES:
        txt, col, ink = TILES[name]
        d = "".join(glyph_d(ch, x + 2 + i * 6 + (0 if ch != "S" else 0), y + 4, 1, 1, False) for i, ch in enumerate(txt))
        return (f'<rect x="{x}" y="{y}" width="16" height="16" fill="var(--{col})"/>'
                f'<path d="{d}" fill="var(--{ink})"/>')
    rows = ICONS[name]
    by_col = {}
    for r, row in enumerate(rows):
        for c, k in enumerate(row):
            if k != ".":
                by_col.setdefault(k, []).append(f"M{x + c * 2} {y + r * 2}h2v2h-2z")
    return "".join(f'<path d="{"".join(v)}" fill="{PAL_ICON[k]}"/>' for k, v in by_col.items())


def tech_chip(name):
    size = 11
    tw = round(len(name) * 0.6 * size)
    w = 8 + 16 + 7 + tw + 9
    out = [
        f'<path d="{pixbox(1, 1, w - 2, CH - 2, 3)}" fill="var(--card)" stroke="var(--mute)" stroke-opacity=".6" stroke-width="1.5" stroke-dasharray="3 3"/>',
        icon_svg(name, 8, (CH - 16) // 2),
        f'<text class="mono" x="{8 + 16 + 7}" y="{CH // 2 + 4}" font-size="{size}" font-weight="700" '
        f'textLength="{tw}" lengthAdjust="spacingAndGlyphs">{esc(name)}</text>',
    ]
    return w, svg(w, CH, "".join(out), name)


# ---- compact social chips (icon + label, one row at the bottom) ------------------------------
def social_chip(label, col, sprite_key):
    size = 9
    tw = round(len(label) * 0.6 * size + (len(label) - 1) * 0.5)
    w = 8 + 16 + 6 + tw + 8
    rows = SPRITES[sprite_key]
    d = "".join(f"M{8 + c * 2} {4 + r * 2}h2v2h-2z" for r, row in enumerate(rows) for c, bit in enumerate(row) if bit == "1")
    out = [
        f'<path d="{pixbox(SHADOW, SHADOW, w - SHADOW, CH - SHADOW, 3)}" style="fill:var(--{col});opacity:.28"/>',
        f'<path d="{pixbox(1, 1, w - SHADOW - 2, CH - SHADOW - 2, 3)}" fill="var(--card)" stroke="var(--line)" stroke-width="2"/>',
        f'<path d="{d}" style="fill:var(--{col})" transform="translate(0 -2)"/>',
        f'<text class="mono" x="{8 + 16 + 6}" y="{(CH - SHADOW) // 2 + 4}" font-size="{size}" font-weight="700" letter-spacing=".5" '
        f'textLength="{tw}" lengthAdjust="spacing">{esc(label)}</text>',
    ]
    return w, svg(w, CH, "".join(out), label.title())


# ---- profile.yaml card (428 wide) ---------------------------------------------------------
def about_card():
    W, LH = WIDE, 22
    ROWS = -(-len(YAML) // 2)  # two columns: left column fills first
    H = 40 + ROWS * LH + 12
    COLX = (18, W // 2 + 10)
    out = [frame(W, H, "blue")]
    for i, col in enumerate(("red", "amber", "teal")):
        out.append(f'<rect x="{16 + i * 12}" y="10" width="7" height="7" fill="var(--{col})"/>')
    out.append('<text class="mono mute" x="64" y="17" font-size="10" letter-spacing="1">profile.yaml</text>')
    out.append(f'<line x1="14" y1="24" x2="{W - SHADOW - 14}" y2="24" stroke="var(--line)" stroke-width="2"/>')
    for i, (k, v) in enumerate(YAML):
        c, r = divmod(i, ROWS)
        x, y = COLX[c], 48 + r * LH
        out.append(
            f'<g class="rise" style="--d:{0.3 + i * 0.12:.2f}s">'
            f'<text class="mono" x="{x}" y="{y}" font-size="13" style="fill:var(--blue)">{esc(k)}</text>'
            f'<text class="mono" x="{x + 88}" y="{y}" font-size="13">{esc(v)}</text></g>'
        )
    c, r = divmod(len(YAML) - 1, ROWS)
    cx = COLX[c] + 88 + round(len(YAML[-1][1]) * 7.8) + 6
    out.append(f'<rect class="blink" x="{cx}" y="{48 + r * LH - 11}" width="8" height="14" fill="var(--blue)"/>')
    alt = "profile.yaml: " + "; ".join(f"{k} {v}" for k, v in YAML)
    return svg(W, H, "".join(out), alt)


# ---- technology: logos only (428 wide, 9 per row) ----------------------------------------------
def logo_big(name, x, y):
    """24x24 logo at (x, y): an 8x8 sprite at 3px per cell, or a JS/TS monogram tile."""
    if name in TILES:
        txt, col, _ = TILES[name]
        fg = "#17171a" if txt == "JS" else "#ffffff"
        d = "".join(glyph_d(ch, x + 1 + i * 12, y + 9, 2, 2, False) for i, ch in enumerate(txt))
        return f'<rect x="{x}" y="{y}" width="24" height="24" fill="var(--{col})"/><path d="{d}" fill="{fg}"/>'
    by_col = {}
    for r, row in enumerate(ICONS[name]):
        for c, k in enumerate(row):
            if k != ".":
                by_col.setdefault(k, []).append(f"M{x + c * 3} {y + r * 3}h3v3h-3z")
    return "".join(f'<path d="{"".join(v)}" fill="{PAL_ICON[k]}"/>' for k, v in by_col.items())


SHORT = {"Cloudflare Workers": "Workers", "GitHub Actions": "Actions", "JavaScript": "JavaScript"}


def technology():
    """Three panels (backend / frontend / infra), each with 6 labelled tiles in a 3x2 grid."""
    W, T, GAP = WIDE, 40, 16
    PW = (W - 2 * GAP) // 3
    COLS, ROWP = 3, 70
    PH = 44 + 2 * ROWP + 4
    out, idx = [], 0
    for gi, (grp, (label, col)) in enumerate(GROUPS.items()):
        px = gi * (PW + GAP)
        g = [f'<g transform="translate({px} 0)">', frame(PW, PH, col)]
        g.append(f'<rect class="blink" x="16" y="14" width="8" height="8" fill="var(--{col})"/>')
        g.append(pixel_text(label, 32, 11, 2, 1, 'class="ink"', bold=True))
        tw = text_width(label, 2, 1, bold=True)
        g.append(f'<line class="march" x1="{32 + tw + 10}" y1="18" x2="{PW - SHADOW - 14}" y2="18" stroke="var(--line)" stroke-width="3" stroke-dasharray="3 3"/>')
        items = [n for n, gr in TECH if gr == grp]
        colw = (PW - SHADOW - 24) // COLS
        for k, name in enumerate(items):
            r, c = divmod(k, COLS)
            cx = 12 + c * colw + colw // 2
            x, y = cx - T // 2, 38 + r * ROWP
            g.append(
                f'<g class="rise" style="--d:{0.05 + idx * 0.05:.2f}s"><title>{esc(name)}</title>'
                f'<path d="{pixbox(SHADOW, SHADOW, T - SHADOW, T - SHADOW, 3)}" transform="translate({x} {y})" style="fill:var(--{col});opacity:.28"/>'
                f'<path d="{pixbox(1, 1, T - SHADOW - 2, T - SHADOW - 2, 3)}" transform="translate({x} {y})" fill="var(--card)" stroke="var(--line)" stroke-width="2"/>'
                f'{logo_big(name, x + 6, y + 6)}'
                f'<text class="mono mute" x="{cx - 2}" y="{y + T + 14}" font-size="9.5" text-anchor="middle">{esc(SHORT.get(name, name))}</text></g>'
            )
            idx += 1
        g.append("</g>")
        out.append("".join(g))
    return svg(W, PH, "".join(out), "Technology: " + ", ".join(n for n, _ in TECH))


# ---- section headings + divider (428 wide) ----------------------------------------------
def heading(label, accent, alt=None, idx=None):
    W, H = WIDE, 34
    cell, gap = 3, 1
    tw = text_width(label, cell, gap, bold=True)
    end = W - (52 if idx else 0)
    out = [
        f'<rect class="blink" x="0" y="8" width="10" height="10" fill="var(--{accent})"/>',
        pixel_text(label, 20, 4, cell, gap, 'class="ink"', bold=True),
        f'<line class="march" x1="{20 + tw + 14}" y1="10" x2="{end}" y2="10" stroke="var(--line)" stroke-width="4" stroke-dasharray="4 4"/>',
    ]
    if idx:
        out.append(f'<text class="mono mute" x="{W}" y="15" font-size="12" letter-spacing="1" text-anchor="end">// {idx:02d}</text>')
    return svg(W, H, "".join(out), alt or label.title())


def footer_strip():
    W, H, cell, gap = WIDE, 44, 3, 1
    text = "PRESS START TO CONNECT"
    tw = text_width(text, cell, gap, bold=True)
    x0 = (W - tw) // 2
    play = ["10000", "11000", "11100", "11110", "11100", "11000", "10000"]
    out = [sprite(play, x0 - 36, 8, 3, "teal", 0.2).replace('class="pop"', 'class="pulse"')]
    out.append(pixel_text(text, x0, 8, cell, gap, 'class="ink flick"', bold=True))
    out.append(f'<rect class="blink" x="{x0 + tw + 10}" y="8" width="16" height="20" fill="var(--blue)"/>')
    out.append(f'<line class="march" x1="0" y1="{H - 6}" x2="{W}" y2="{H - 6}" stroke="var(--line)" stroke-width="2" stroke-dasharray="4 4"/>')
    return svg(W, H, "".join(out), "Press start to connect")


def divider():
    W, H = WIDE, 12
    cols = ["blue", "red", "amber", "teal"]
    out = []
    for i in range(W // 8):
        out.append(f'<rect class="wave" style="--d:{i * .06:.2f}s;fill:var(--{cols[i % 4]})" x="{i * 8}" y="4" width="4" height="4"/>')
    return svg(W, H, "".join(out), "divider")


# Rendered widths (px) in the README. Fixed pixels instead of 100% so nothing is stretched on wide screens.
#   FULL_W: (unused now, kept for reference) compact 428px cards
#   WIDE_W: every full-width card (hero, profile.yaml, headings, technology, activity, divider) - authored AND shown at 880,
#           which is GitHub's max README column; GitHub shrinks them automatically on narrow screens.
FULL_W = 480
WIDE_W = 880


# ---- README ---------------------------------------------------------------------------------
# Original logos come from https://skillicons.dev (ids from its official icon list).
# A tool with no skillicons id (e.g. Jinja, YouTube) is shown without an icon / left out - never faked.
ICON_ID = {
    "Python": "py", "Flask": "flask", "FastAPI": "fastapi", "MongoDB": "mongodb", "MySQL": "mysql",
    "SQLite": "sqlite", "HTML": "html", "CSS": "css", "JavaScript": "js", "TypeScript": "ts",
    "React": "react", "Tailwind": "tailwind", "Cloudflare Workers": "workers", "Docker": "docker",
    "Git": "git", "GitHub Actions": "githubactions", "Vercel": "vercel", "PowerShell": "powershell",
}
SKILL = "https://skillicons.dev/icons?i="


def write_readme(socials):
    def img(name, alt, width):
        return f'<img src="{RAW}/{name}.svg" width="{width}" alt="{html.escape(alt)}" />'

    def c(name):  # inline tool: original logo + name (name only when skillicons has no icon)
        ic = ICON_ID.get(name)
        if not ic:
            return f"<kbd>{name}</kbd>"
        return f'<kbd><img src="{SKILL}{ic}" width="18" height="18" align="absmiddle" alt="" /> {name}</kbd>'

    tech_ids = ",".join(ICON_ID[n] for n, _ in TECH if n in ICON_ID)
    tech_alt = "Technology: " + ", ".join(n for n, _ in TECH if n in ICON_ID)
    soc = " ".join(
        f'<a href="{url}"><img src="{RAW}/social-{lab.lower()}.svg" width="{socials[lab]}" height="{CH}" align="absmiddle" alt="{lab.title()}" /></a>'
        for lab, url, _, _ in SOCIALS)

    parts = [
        f'<p>{img("headline", HEADLINE_ALT, WIDE_W)}</p>',
        "",
        f"I build web apps around problems that are easy to see but needlessly complicated to solve \u2014 attendance systems that replace paper registers, booking that lands the second a window opens, lightweight tools that need no account. Main stack: {c('Python')} + {c('Flask')} with hand-written {c('Jinja')} and whichever database fits \u2014 {c('MongoDB')}, {c('MySQL')} or {c('SQLite')}. Lately mostly {c('TypeScript')} and {c('Cloudflare Workers')}: gateways that let any harness talk to a provider it was never written for, plus small backend-free tools. **29 public repos, 13 of them live** across `truepushkar` and `nullstacks`. I care more about solving the right problem than collecting technologies.",
        "",
        f'<p align="center">{img("about", "profile.yaml: " + "; ".join(k + " " + v for k, v in YAML), WIDE_W)}</p>',
        "",
        f'<p>{img("heading-technology", "Technology", WIDE_W)}</p>',
        "",
        f'<p align="center"><img src="{SKILL}{tech_ids}&perline=18" width="{WIDE_W}" alt="{html.escape(tech_alt)}" /></p>',
        "",
        f'<p>{img("heading-activity", "GitHub Activity", WIDE_W)}</p>',
        "",
        f'<p align="center">{img("activity-overview", "GitHub statistics and top languages", WIDE_W)}</p>',
        "",
        f'<p align="center">{img("activity-streak", "GitHub contribution streak", WIDE_W)}</p>',
        "",
        f'<p align="center">{img("activity-graph", "GitHub contribution graph", WIDE_W)}</p>',
        "",
        f'<p>{img("divider", "", WIDE_W)}</p>',
        "",
        f'<p align="center">{soc}</p>',
        "",
    ]
    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    print("wrote README.md")


def slug(name):
    return name.lower().replace(" ", "-")


INLINE_CHIPS = ["Python", "Flask", "Jinja", "MongoDB", "MySQL", "SQLite", "Cloudflare Workers", "TypeScript"]


def main():
    if os.path.isdir(CARDS):
        for f in os.listdir(CARDS):
            if f.endswith(".svg") and not f.startswith("activity-"):  # activity cards come from render_activity.py
                os.remove(os.path.join(CARDS, f))
    write("headline.svg", headline())
    socials = {}
    for lab, _, col, sk in SOCIALS:
        w, content = social_chip(lab, col, sk)
        socials[lab] = w
        write(f"social-{lab.lower()}.svg", content)
    write("about.svg", about_card())
    write("heading-technology.svg", heading("TECHNOLOGY", "amber", "Technology", 1))
    write("heading-activity.svg", heading("ACTIVITY", "teal", "GitHub Activity", 2))
    write("divider.svg", divider())
    write_readme(socials)


if __name__ == "__main__":
    main()
