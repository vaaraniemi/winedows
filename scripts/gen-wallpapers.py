#!/usr/bin/env python3
"""Generate the Winedows wallpaper set (rotating slideshow).

Writes 1920x1080 SVGs to build/config/includes.chroot/usr/share/winedows/wallpapers/.
Pure stdlib, deterministic (fixed seeds), so re-running gives identical files.
Everything is drawn here: the logo mark is redrawn from docs/logo-mark.svg, no outside artwork.
Linux Torvalds (see docs/wiki/joke-design.md) hides in 04, 07 and 10. Keep him small.

Usage: python3 scripts/gen-wallpapers.py [outdir]
"""
import math
import os
import random
import sys

W, H = 1920, 1080
FONT = "Liberation Sans, DejaVu Sans, Arial, sans-serif"
MONO = "Liberation Mono, DejaVu Sans Mono, monospace"

NAVY = "#06173f"
NAVY2 = "#0a2a6b"
BLUE = "#0a4fd6"
SKY = "#2aa3ff"
WINE = "#9c1d3f"
WINE2 = "#5e0f27"
ROSE = "#c42a55"

# Logo mark (docs/logo-mark.svg) as a reusable symbol. Gradient ids are prefixed to avoid clashes.
MARK = """
<linearGradient id="mkR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9c1d3f"/><stop offset="1" stop-color="#5e0f27"/></linearGradient>
<linearGradient id="mkB" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2aa3ff"/><stop offset="1" stop-color="#0a4fd6"/></linearGradient>
<symbol id="mark" viewBox="0 0 64 64">
  <g stroke-linejoin="round" stroke-width="2.5">
    <polygon points="4,10 30,8 30,30 4,30" fill="url(#mkR)" stroke="url(#mkR)"/>
    <polygon points="4,34 30,34 30,58 4,57" fill="url(#mkR)" stroke="url(#mkR)"/>
    <polygon points="34,7 60,3 60,30 34,30" fill="url(#mkB)" stroke="url(#mkB)"/>
    <polygon points="34,34 60,34 60,61 34,58" fill="url(#mkB)" stroke="url(#mkB)"/>
  </g>
  <path d="M9.5 12.5 H24.5 C24.5 21.5 21 25.5 17 25.5 C13 25.5 9.5 21.5 9.5 12.5 Z" fill="#fff"/>
  <path d="M11.2 16.5 C14 15.6 20 17.4 22.8 16.5 C22.3 21.6 20 23.8 17 23.8 C14 23.8 11.7 21.6 11.2 16.5 Z" fill="#c42a55"/>
  <path d="M17 25 V28.5" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>
  <g fill="#fff">
    <circle cx="11" cy="42" r="3.3"/><circle cx="17" cy="42" r="3.3"/><circle cx="23" cy="42" r="3.3"/>
    <circle cx="14" cy="47.6" r="3.3"/><circle cx="20" cy="47.6" r="3.3"/>
    <circle cx="17" cy="53.1" r="3.3"/>
  </g>
  <path d="M37 55.5 C48 55.5 56 49 59.3 39 C55 48 47.5 52.6 37 53.2 Z" fill="#fff" opacity=".9"/>
</symbol>
"""

# Outline-only version of the mark (blueprint).
MARK_LINE = """
<symbol id="markline" viewBox="0 0 64 64">
  <g fill="none" stroke="#fff" stroke-width="0.35" stroke-linejoin="round">
    <polygon points="4,10 30,8 30,30 4,30"/><polygon points="4,34 30,34 30,58 4,57"/>
    <polygon points="34,7 60,3 60,30 34,30"/><polygon points="34,34 60,34 60,61 34,58"/>
    <path d="M9.5 12.5 H24.5 C24.5 21.5 21 25.5 17 25.5 C13 25.5 9.5 21.5 9.5 12.5 Z"/>
    <path d="M11.2 16.5 C14 15.6 20 17.4 22.8 16.5"/>
    <path d="M17 25.5 V28.5"/>
    <circle cx="11" cy="42" r="3.3"/><circle cx="17" cy="42" r="3.3"/><circle cx="23" cy="42" r="3.3"/>
    <circle cx="14" cy="47.6" r="3.3"/><circle cx="20" cy="47.6" r="3.3"/><circle cx="17" cy="53.1" r="3.3"/>
    <path d="M37 55.5 C48 55.5 56 49 59.3 39 C55 48 47.5 52.6 37 53.2 Z"/>
  </g>
</symbol>
"""

# Linux Torvalds: the project's penguin with a face (docs/linux-torvalds.png), redrawn as a tiny vector.
LINUS = """
<symbol id="linus" viewBox="0 0 40 52">
  <ellipse cx="20" cy="32" rx="15" ry="17" fill="#111"/>
  <circle cx="20" cy="13" r="11" fill="#111"/>
  <ellipse cx="20" cy="34" rx="10" ry="13" fill="#f2f2f2"/>
  <ellipse cx="20" cy="14.5" rx="7.2" ry="6.8" fill="#8d7f74"/>
  <rect x="12.6" y="11.4" width="14.8" height="3.4" rx="1.6" fill="#050505"/>
  <path d="M16.2 18.4 Q20 20.4 23.8 17.6" fill="none" stroke="#1a1a1a" stroke-width="1"/>
  <path d="M5 33 Q2 41 8 46 Z M35 33 Q38 41 32 46 Z" fill="#111"/>
  <ellipse cx="12" cy="49" rx="7" ry="3" fill="#f2b705"/>
  <ellipse cx="28" cy="49" rx="7" ry="3" fill="#f2b705"/>
</symbol>
"""


def svg(title, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
        f"<title>Winedows wallpaper: {title}</title>\n"
        f"<defs>{MARK}{MARK_LINE}{LINUS}{defs}</defs>\n{body}\n</svg>\n"
    )


def use(sym, x, y, size, extra=""):
    return f'<use xlink:href="#{sym}" href="#{sym}" x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" {extra}/>'


def linus(x, y, h, extra=""):
    w = h * 40 / 52
    return f'<use xlink:href="#linus" href="#linus" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {extra}/>'


def brand(dark_bg=True):
    """Bottom-right brand chip, same on every wallpaper. Sits above a 44px bottom panel."""
    fg = "#ffffff" if dark_bg else "#14213d"
    sub = "#ffffff" if dark_bg else "#14213d"
    return (
        f'<g font-family="{FONT}">'
        + use("mark", 1832, 944, 48)
        + f'<text x="1816" y="966" fill="{fg}" font-size="22" font-weight="bold" text-anchor="end">GigaHard Winedows</text>'
        f'<text x="1816" y="989" fill="{sub}" fill-opacity="0.72" font-size="16" text-anchor="end">Linux, but it works.</text>'
        "</g>"
    )


def stars(rng, n, y_max=H, r_max=1.6, opacity=0.9):
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, y_max)
        r = rng.choice([0.6, 0.8, 1.0, 1.2, r_max])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" opacity="{rng.uniform(0.3, opacity):.2f}"/>')
    return "".join(out)


# 01 Hero: the mark floating in the dark, lit from behind, beams fanning out.
def hero():
    defs = f"""
<radialGradient id="bg" cx="0.6" cy="0.45" r="0.8"><stop offset="0" stop-color="{NAVY2}"/><stop offset="0.6" stop-color="{NAVY}"/><stop offset="1" stop-color="#020817"/></radialGradient>
<linearGradient id="beam" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#7cc4ff" stop-opacity="0.5"/><stop offset="1" stop-color="#7cc4ff" stop-opacity="0"/></linearGradient>
<linearGradient id="beamR" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="{ROSE}" stop-opacity="0.45"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{SKY}" stop-opacity="0.55"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></radialGradient>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
"""
    # Logo panel, slightly in perspective. Beams leave its left edge.
    lx, ly, s = 1040, 250, 560
    beams = []
    for i, (y0, y1, ty0, ty1, grad) in enumerate([
        (ly + 40, ly + 250, -200, 300, "beamR"),
        (ly + 290, ly + 520, 520, 1180, "beamR"),
        (ly + 20, ly + 260, 120, 470, "beam"),
        (ly + 300, ly + 540, 640, 900, "beam"),
    ]):
        beams.append(f'<polygon points="{lx + 120},{y0} {lx + 120},{y1} -100,{ty1} -100,{ty0}" fill="url(#{grad})" opacity="0.55" filter="url(#soft)"/>')
    body = (
        '<rect width="1920" height="1080" fill="url(#bg)"/>'
        + "".join(beams)
        + f'<ellipse cx="{lx + s / 2}" cy="{ly + s / 2}" rx="520" ry="420" fill="url(#glow)"/>'
        + f'<g transform="translate({lx} {ly}) matrix(1 -0.06 0 1 0 0)">' + use("mark", 0, 0, s) + "</g>"
        + brand()
    )
    return svg("Hero", body, defs)


# 02 Panes: the four panes, enormous, edge to edge.
def panes():
    defs = f"""
<linearGradient id="r1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#b8264d"/><stop offset="1" stop-color="{WINE2}"/></linearGradient>
<linearGradient id="r2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{WINE}"/><stop offset="1" stop-color="#3d0919"/></linearGradient>
<linearGradient id="b1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{SKY}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
<linearGradient id="b2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1673ea"/><stop offset="1" stop-color="#062f8a"/></linearGradient>
<linearGradient id="gap" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#cfe6ff"/></linearGradient>
"""
    g = 22  # gap between panes
    cx, cy = 900, 560
    body = (
        '<rect width="1920" height="1080" fill="url(#gap)"/>'
        f'<polygon points="-20,-20 {cx - g},-60 {cx - g},{cy - g} -20,{cy - g + 10}" fill="url(#r1)"/>'
        f'<polygon points="-20,{cy + g + 10} {cx - g},{cy + g} {cx - g},1100 -20,1100" fill="url(#r2)"/>'
        f'<polygon points="{cx + g},-60 1940,-120 1940,{cy - g - 20} {cx + g},{cy - g}" fill="url(#b1)"/>'
        f'<polygon points="{cx + g},{cy + g} 1940,{cy + g - 20} 1940,1100 {cx + g},1100" fill="url(#b2)"/>'
        # Pane emblems, huge and white: glass, grapes, swoosh.
        '<g transform="translate(150 40) scale(16)" opacity="0.95">'
        '<path d="M9.5 12.5 H24.5 C24.5 21.5 21 25.5 17 25.5 C13 25.5 9.5 21.5 9.5 12.5 Z" fill="none" stroke="#fff" stroke-width="0.9" transform="translate(-9 -11)"/>'
        '<path d="M11.2 16.5 C14 15.6 20 17.4 22.8 16.5 C22.3 21.6 20 23.8 17 23.8 C14 23.8 11.7 21.6 11.2 16.5 Z" fill="#fff" fill-opacity="0.25" transform="translate(-9 -11)"/>'
        '<path d="M8 14 V18 M3 18 H13" stroke="#fff" stroke-width="0.9" stroke-linecap="round" fill="none"/>'
        "</g>"
        '<g fill="#fff" fill-opacity="0.18">'
        + "".join(f'<circle cx="{x}" cy="{y}" r="62"/>' for x, y in [(260, 700), (400, 700), (540, 700), (330, 822), (470, 822), (400, 944)])
        + "</g>"
        '<path d="M960 1010 C1380 1010 1700 860 1880 600 C1680 900 1380 980 960 975 Z" fill="#fff" opacity="0.85"/>'
        + brand()
    )
    return svg("Panes", body, defs)


# 03 Tiles: a field of marks, lit from the middle and fading into the dark.
def tiles():
    defs = f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY2}"/><stop offset="1" stop-color="#020817"/></linearGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{SKY}" stop-opacity="0.45"/><stop offset="0.5" stop-color="{ROSE}" stop-opacity="0.12"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></radialGradient>
<radialGradient id="fade" cx="0.5" cy="0.5" r="0.62"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="0.55" stop-color="#fff" stop-opacity="0.35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080"><rect width="1920" height="1080" fill="url(#fade)"/></mask>
<pattern id="tiles" width="132" height="132" patternUnits="userSpaceOnUse" patternTransform="rotate(-12 960 540)">
  <use xlink:href="#mark" href="#mark" x="30" y="30" width="72" height="72"/>
</pattern>
"""
    body = (
        '<rect width="1920" height="1080" fill="url(#bg)"/>'
        '<ellipse cx="960" cy="540" rx="900" ry="560" fill="url(#glow)"/>'
        '<rect width="1920" height="1080" fill="url(#tiles)" mask="url(#m)" opacity="0.55"/>'
        + brand()
    )
    return svg("Tiles", body, defs)


# 04 Vineyard: dusk over the rows, the mark rising as the sun. Linus works the third row.
def vineyard():
    rng = random.Random(4)
    defs = f"""
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="0.45" stop-color="#1d3f9e"/><stop offset="0.75" stop-color="#b8264d"/><stop offset="1" stop-color="#ff9a6b"/></linearGradient>
<radialGradient id="sun"><stop offset="0" stop-color="#ffd7b0" stop-opacity="0.9"/><stop offset="1" stop-color="#ff9a6b" stop-opacity="0"/></radialGradient>
<linearGradient id="h1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a1030"/><stop offset="1" stop-color="#2a0a22"/></linearGradient>
<linearGradient id="h2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1d4f"/><stop offset="1" stop-color="#0c1033"/></linearGradient>
<linearGradient id="h3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0e1640"/><stop offset="1" stop-color="#050a22"/></linearGradient>
"""
    rows = []
    # Front hill vine rows: curved lines converging to a vanishing point.
    vx, vy = 1300, 700
    for i in range(-12, 22):
        x_end = vx + i * 150
        rows.append(f'<path d="M{vx + i * 6} {vy + 10} Q{vx + i * 40} {vy + 140} {x_end} 1100" stroke="#2c4bb0" stroke-opacity="0.55" stroke-width="{3 + abs(i) * 0.4:.1f}" fill="none"/>')
    # Vine bushes along rows (dots).
    for i in range(-12, 22):
        for t in [0.25, 0.4, 0.55, 0.7, 0.85]:
            x0, y0 = vx + i * 6, vy + 10
            x1, y1 = vx + i * 40, vy + 140
            x2, y2 = vx + i * 150, 1100
            bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t ** 2 * x2
            by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t ** 2 * y2
            r = 2 + t * 14
            col = rng.choice(["#3b1a5e", "#5e0f27", "#2a2f7a"])
            rows.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r:.1f}" fill="{col}"/>')
    # Linus stands in a row on the left, about one vine tall.
    t = 0.7
    i = -5
    lx = (1 - t) ** 2 * (vx + i * 6) + 2 * (1 - t) * t * (vx + i * 40) + t ** 2 * (vx + i * 150)
    ly = (1 - t) ** 2 * (vy + 10) + 2 * (1 - t) * t * (vy + 140) + t ** 2 * 1100
    body = (
        '<rect width="1920" height="1080" fill="url(#sky)"/>'
        + stars(rng, 120, y_max=380, opacity=0.8)
        + '<circle cx="760" cy="640" r="340" fill="url(#sun)"/>'
        + use("mark", 640, 500, 240)
        + '<path d="M0 640 C300 590 520 610 760 650 C1000 690 1400 600 1920 640 V1080 H0 Z" fill="url(#h1)"/>'
        + '<path d="M0 700 C400 660 800 720 1200 700 C1500 685 1700 690 1920 705 V1080 H0 Z" fill="url(#h2)"/>'
        + '<path d="M0 740 C500 720 900 712 1300 710 C1600 712 1800 730 1920 745 V1080 H0 Z" fill="url(#h3)"/>'
        + "".join(rows)
        + linus(lx - 12, ly - 38, 34)
        + brand()
    )
    return svg("Vineyard", body, defs)


# 05 Vintage: a glass of Win32, still fizzing.
def vintage():
    rng = random.Random(5)
    defs = f"""
<radialGradient id="bg" cx="0.5" cy="0.4" r="0.8"><stop offset="0" stop-color="#7a1838"/><stop offset="0.6" stop-color="#3d0b24"/><stop offset="1" stop-color="#14051a"/></radialGradient>
<linearGradient id="wine" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ROSE}"/><stop offset="0.55" stop-color="#6b2a9e"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
<clipPath id="bowl"><path d="M760 230 H1160 C1160 520 1070 640 960 640 C850 640 760 520 760 230 Z"/></clipPath>
<radialGradient id="shine"><stop offset="0" stop-color="#fff" stop-opacity="0.35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
"""
    bubbles = "".join(
        f'<circle cx="{rng.uniform(800, 1120):.1f}" cy="{rng.uniform(380, 620):.1f}" r="{rng.uniform(2, 7):.1f}" fill="none" stroke="#fff" stroke-opacity="{rng.uniform(0.3, 0.8):.2f}" stroke-width="1.5"/>'
        for _ in range(40)
    )
    body = (
        '<rect width="1920" height="1080" fill="url(#bg)"/>'
        '<ellipse cx="960" cy="860" rx="300" ry="26" fill="#000" opacity="0.35"/>'
        '<g clip-path="url(#bowl)">'
        '<path d="M700 360 C820 330 900 390 960 370 C1030 345 1100 380 1220 350 V700 H700 Z" fill="url(#wine)"/>'
        + bubbles
        + "</g>"
        '<path d="M760 230 H1160 C1160 520 1070 640 960 640 C850 640 760 520 760 230 Z" fill="none" stroke="#fff" stroke-width="8" stroke-linejoin="round"/>'
        '<path d="M960 640 V840 M840 846 H1080" stroke="#fff" stroke-width="8" stroke-linecap="round"/>'
        '<ellipse cx="840" cy="330" rx="40" ry="90" fill="url(#shine)"/>'
        + use("mark", 924, 420, 72, 'opacity="0.95"')
        + f'<text x="960" y="944" text-anchor="middle" font-family="{FONT}" font-size="30" fill="#fff" fill-opacity="0.85" letter-spacing="6">WIN32 · AGED SINCE 1993</text>'
        + brand()
    )
    return svg("Vintage", body, defs)


# 06 Bedrock: geological survey. Library versions erode; Win32 is the bedrock.
def bedrock():
    layers = [
        ("#6b8f3a", "topsoil: whatever you installed this morning", 30),
        ("#a87b55", "libssl3 (current, for now)", 70),
        ("#946a48", "libssl1.1 deposit (extinct)", 60),
        ("#82603f", "libssl1.0 fossil bed", 50),
        ("#7a5a54", "glibc symbol version strata, GLIBC_2.2.5 to GLIBC_2.40", 90),
        ("#6a4f60", "GTK2 sediment (compressed)", 55),
        ("#5a4568", "Python 2 deposits (do not disturb)", 60),
        ("#4a3d6e", "libpng12 fossils, well preserved", 50),
        ("#3d3870", "Flatpak runtime layers (several, overlapping)", 70),
    ]
    out = []
    y = 300
    rng = random.Random(6)
    for i, (col, label, th) in enumerate(layers):
        # Wavy top edge per layer.
        pts = []
        for x in range(0, W + 1, 120):
            pts.append(f"{x},{y + rng.uniform(-8, 8):.1f}")
        out.append(f'<polygon points="{" ".join(pts)} {W},{H} 0,{H}" fill="{col}"/>')
        out.append(f'<text x="1660" y="{y + th / 2 + 8:.0f}" text-anchor="end" font-family="{MONO}" font-size="17" fill="#fff" fill-opacity="0.82">{label}</text>')
        out.append(f'<line x1="1676" y1="{y + th / 2 + 2:.0f}" x2="1720" y2="{y + th / 2 + 2:.0f}" stroke="#fff" stroke-opacity="0.6"/>')
        y += th
    # Bedrock: Win32. Thick, blue, unbothered.
    bedrock_y = y
    pts = " ".join(f"{x},{bedrock_y + rng.uniform(-6, 6):.1f}" for x in range(0, W + 1, 160))
    out.append(f'<polygon points="{pts} {W},{H} 0,{H}" fill="url(#rock)"/>')
    out.append(
        f'<text x="960" y="{bedrock_y + 120}" text-anchor="middle" font-family="{FONT}" font-size="64" font-weight="bold" fill="#fff" letter-spacing="10">WIN32</text>'
        f'<text x="960" y="{bedrock_y + 162}" text-anchor="middle" font-family="{FONT}" font-size="22" fill="#cfe6ff">bedrock · stable since 1993 · your .exe still runs</text>'
    )
    # Fossils: little embedded shapes in the strata.
    for _ in range(26):
        fx, fy = rng.uniform(120, 1500), rng.uniform(330, bedrock_y - 20)
        out.append(f'<ellipse cx="{fx:.0f}" cy="{fy:.0f}" rx="{rng.uniform(6, 16):.0f}" ry="{rng.uniform(3, 6):.0f}" fill="#fff" fill-opacity="0.08"/>')
    defs = f"""
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{SKY}"/></linearGradient>
<linearGradient id="rock" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{NAVY}"/></linearGradient>
"""
    body = (
        '<rect width="1920" height="1080" fill="url(#sky)"/>'
        + "".join(out)
        # A flag on the surface.
        + '<path d="M420 300 V200" stroke="#fff" stroke-width="4"/>'
        + use("mark", 422, 196, 56)
        + f'<text x="960" y="150" text-anchor="middle" font-family="{FONT}" font-size="40" fill="#fff" font-weight="300">Geological survey of a Linux desktop</text>'
        f'<text x="960" y="192" text-anchor="middle" font-family="{FONT}" font-size="20" fill="#fff" fill-opacity="0.75">cross-section, not to scale, layers subject to change without notice</text>'
        + brand()
    )
    return svg("Bedrock", body, defs)


# 07 No problems: a full-screen notice that nothing is wrong. Linus is the middle of the code square.
def noproblems():
    rng = random.Random(7)
    n, cell = 25, 6
    qx, qy = 260, 640
    q = [f'<rect x="{qx - 8}" y="{qy - 8}" width="{n * cell + 16}" height="{n * cell + 16}" fill="#fff"/>']
    hole = range(9, 16)
    for r in range(n):
        for c in range(n):
            finder = (r < 7 and c < 7) or (r < 7 and c >= n - 7) or (r >= n - 7 and c < 7)
            if finder or (r in hole and c in hole):
                continue
            if rng.random() < 0.5:
                q.append(f'<rect x="{qx + c * cell}" y="{qy + r * cell}" width="{cell}" height="{cell}" fill="{BLUE}"/>')
    for fr, fc in [(0, 0), (0, n - 7), (n - 7, 0)]:
        fx, fy = qx + fc * cell, qy + fr * cell
        q.append(f'<rect x="{fx + 3}" y="{fy + 3}" width="{7 * cell - 6}" height="{7 * cell - 6}" fill="none" stroke="{BLUE}" stroke-width="6"/>')
        q.append(f'<rect x="{fx + 2 * cell}" y="{fy + 2 * cell}" width="{3 * cell}" height="{3 * cell}" fill="{BLUE}"/>')
    q.append(linus(qx + 9 * cell + 4, qy + 9 * cell + 2, 7 * cell - 4))
    t = f'font-family="{FONT}" fill="#fff"'
    body = (
        f'<rect width="1920" height="1080" fill="{BLUE}"/>'
        f'<text x="250" y="380" {t} font-size="200">:)</text>'
        f'<text x="260" y="470" {t} font-size="40">Your PC ran into no problems and doesn\'t need to restart.</text>'
        f'<text x="260" y="522" {t} font-size="40">We\'re just collecting some compliments, then we\'ll keep going.</text>'
        f'<text x="260" y="600" {t} font-size="40">100% complete</text>'
        + "".join(q)
        + f'<text x="460" y="672" {t} font-size="20">For more information about this non-issue, there is none.</text>'
        f'<text x="460" y="708" {t} font-size="20">If you call a support person, give them this info:</text>'
        f'<text x="460" y="740" {t} font-size="20">Stop code: EVERYTHING_WORKS</text>'
        f'<text x="460" y="772" {t} font-size="20">What succeeded: setup.exe (via Wine)</text>'
        + brand()
    )
    return svg("No problems", body)


# 08 Aurora: night lake under wine-and-blue northern lights.
def aurora():
    rng = random.Random(8)
    defs = f"""
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#020617"/><stop offset="0.7" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient>
<linearGradient id="a1" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{SKY}" stop-opacity="0"/><stop offset="0.3" stop-color="{SKY}" stop-opacity="0.8"/><stop offset="0.7" stop-color="{ROSE}" stop-opacity="0.8"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></linearGradient>
<linearGradient id="a2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ROSE}" stop-opacity="0"/><stop offset="0.4" stop-color="#7a3cc8" stop-opacity="0.7"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient>
<filter id="blur" filterUnits="userSpaceOnUse" x="-300" y="-300" width="2520" height="1200"><feGaussianBlur stdDeviation="28"/></filter>
<filter id="blur2" filterUnits="userSpaceOnUse" x="-300" y="-300" width="2520" height="1200"><feGaussianBlur stdDeviation="10"/></filter>
<radialGradient id="moon"><stop offset="0" stop-color="#cfe6ff" stop-opacity="0.6"/><stop offset="1" stop-color="#cfe6ff" stop-opacity="0"/></radialGradient>
<clipPath id="lake"><rect y="640" width="1920" height="440"/></clipPath>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#071a4a"/><stop offset="1" stop-color="#020617"/></linearGradient>
"""
    sky = (
        '<rect width="1920" height="1080" fill="url(#sky)"/>'
        + stars(rng, 260, y_max=640)
        + '<path d="M-100 380 C300 200 600 420 960 260 C1300 110 1600 300 2020 160" stroke="url(#a1)" stroke-width="150" fill="none" filter="url(#blur)"/>'
        + '<path d="M-100 300 C400 380 700 180 1100 320 C1400 420 1700 240 2020 330" stroke="url(#a2)" stroke-width="80" fill="none" filter="url(#blur)"/>'
        + '<path d="M200 330 C500 250 800 360 1100 270" stroke="#9fd6ff" stroke-opacity="0.35" stroke-width="10" fill="none" filter="url(#blur2)"/>'
        + '<circle cx="1480" cy="200" r="120" fill="url(#moon)"/>'
        + '<path d="M0 640 L180 520 L300 590 L470 430 L640 600 L760 540 L900 640 Z" fill="#040b24"/>'
        + '<path d="M820 640 L1010 480 L1120 560 L1260 410 L1420 580 L1560 500 L1760 640 Z" fill="#030921"/>'
        + '<path d="M1500 640 L1700 540 L1820 590 L1920 520 V640 Z" fill="#040b24"/>'
    )
    body = (
        sky
        + '<rect y="640" width="1920" height="440" fill="url(#water)"/>'
        # Reflection: the sky mirrored, dimmed.
        + f'<g clip-path="url(#lake)"><g transform="translate(0 1280) scale(1 -1)" opacity="0.35">{sky}</g></g>'
        + '<rect y="640" width="1920" height="440" fill="url(#water)" opacity="0.55"/>'
        + "".join(
            f'<rect x="{rng.uniform(0, 1880):.0f}" y="{rng.uniform(660, 1040):.0f}" width="{rng.uniform(30, 160):.0f}" height="1.5" fill="#cfe6ff" opacity="{rng.uniform(0.08, 0.25):.2f}"/>'
            for _ in range(60)
        )
        + use("mark", 1450, 170, 60)
        + brand()
    )
    return svg("Aurora", body, defs)


# 09 Blueprint: engineering drawing of the mark.
def blueprint():
    defs = """
<pattern id="minor" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0 H0 V24" fill="none" stroke="#fff" stroke-opacity="0.08"/></pattern>
<pattern id="major" width="120" height="120" patternUnits="userSpaceOnUse"><path d="M120 0 H0 V120" fill="none" stroke="#fff" stroke-opacity="0.18"/></pattern>
<marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#fff"/></marker>
"""
    x0, y0, s = 700, 170, 560  # 1 unit = 8.75 px
    u = s / 64
    t = f'font-family="{MONO}" fill="#fff"'
    def P(px, py):
        return x0 + px * u, y0 + py * u
    callouts = [
        ((17, 18), (1360, 230), "A  GLASS, WINE-FILLED, QTY 1"),
        ((20, 47.6), (1360, 330), "B  GRAPES, ROUND, QTY 6"),
        ((48, 52), (1360, 430), "C  SWOOSH, FITS ALL APPS"),
        ((47, 18), (1360, 530), "D  BLANK PANE, RESERVED FOR ABI BREAKS"),
        ((47, 18), (1360, 560), "   (NONE PLANNED)"),
    ]
    cl = []
    for (px, py), (tx, ty), label in callouts:
        if not label.startswith("   "):
            ax, ay = P(px, py)
            cl.append(f'<path d="M{ax:.0f} {ay:.0f} L{tx - 20} {ty - 6}" stroke="#fff" stroke-width="1.2" fill="none" marker-start="url(#arr)"/>')
            cl.append(f'<circle cx="{ax:.0f}" cy="{ay:.0f}" r="3" fill="#fff"/>')
        cl.append(f'<text x="{tx}" y="{ty}" {t} font-size="18">{label}</text>')
    ax0, _ = P(4, 0)
    ax1, _ = P(60, 0)
    _, ay0 = P(0, 3)
    _, ay1 = P(0, 61)
    dims = (
        f'<path d="M{ax0:.0f} {y0 + s + 40} H{ax1:.0f}" stroke="#fff" marker-start="url(#arr)" marker-end="url(#arr)"/>'
        f'<path d="M{ax0:.0f} {y0 + s + 10} V{y0 + s + 52} M{ax1:.0f} {y0 + s + 10} V{y0 + s + 52}" stroke="#fff" stroke-opacity="0.6"/>'
        f'<text x="{(ax0 + ax1) / 2:.0f}" y="{y0 + s + 32}" text-anchor="middle" {t} font-size="16">56 UNITS (ONE WIN32)</text>'
        f'<path d="M{x0 - 40} {ay0:.0f} V{ay1:.0f}" stroke="#fff" marker-start="url(#arr)" marker-end="url(#arr)"/>'
        f'<text x="{x0 - 52}" y="{(ay0 + ay1) / 2:.0f}" text-anchor="middle" {t} font-size="16" transform="rotate(-90 {x0 - 52} {(ay0 + ay1) / 2:.0f})">58 UNITS</text>'
    )
    tb_x, tb_y, tb_w = 240, 820, 760
    rows = [
        "GIGAHARD WINEDOWS · GENERAL ARRANGEMENT",
        "DWG NO. WD-0001   REV 32 (Win32)   SHEET 1 OF 1",
        "SCALE 1:1   TOLERANCE ±0 ABI BREAKS",
        "DRAWN: L.T.   CHECKED: WINE   APPROVED: IT WORKS",
    ]
    tb = [f'<rect x="{tb_x}" y="{tb_y}" width="{tb_w}" height="{len(rows) * 34 + 8}" fill="none" stroke="#fff" stroke-width="2"/>']
    for i, r in enumerate(rows):
        yy = tb_y + 28 + i * 34
        tb.append(f'<text x="{tb_x + 16}" y="{yy}" {t} font-size="{20 if i == 0 else 17}"{" font-weight=" + chr(34) + "bold" + chr(34) if i == 0 else ""}>{r}</text>')
        if i:
            tb.append(f'<line x1="{tb_x}" y1="{yy - 24}" x2="{tb_x + tb_w}" y2="{yy - 24}" stroke="#fff" stroke-opacity="0.6"/>')
    body = (
        '<rect width="1920" height="1080" fill="#0b3a8f"/>'
        '<rect width="1920" height="1080" fill="url(#minor)"/>'
        '<rect width="1920" height="1080" fill="url(#major)"/>'
        '<rect x="200" y="40" width="1680" height="1000" fill="none" stroke="#fff" stroke-opacity="0.5" stroke-width="2"/>'
        + use("markline", x0, y0, s)
        + f'<g transform="translate({x0} {y0}) scale({u})"><path d="M34 30 L60 3 M34 7 L60 30" stroke="#fff" stroke-opacity="0.35" stroke-width="0.2" stroke-dasharray="1 1"/></g>'
        + "".join(cl)
        + dims
        + "".join(tb)
        + brand()
    )
    return svg("Blueprint", body, defs)


# 10 Constellation: the mark in the stars. A smaller constellation nearby is Linux Torvalds Minor.
def constellation():
    rng = random.Random(10)
    defs = f"""
<radialGradient id="bg" cx="0.55" cy="0.4" r="0.9"><stop offset="0" stop-color="#14245e"/><stop offset="0.5" stop-color="{NAVY}"/><stop offset="1" stop-color="#01040f"/></radialGradient>
<radialGradient id="neb" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{ROSE}" stop-opacity="0.35"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></radialGradient>
<radialGradient id="neb2" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{SKY}" stop-opacity="0.3"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></radialGradient>
<radialGradient id="star"><stop offset="0" stop-color="#fff"/><stop offset="0.3" stop-color="#cfe6ff" stop-opacity="0.8"/><stop offset="1" stop-color="#cfe6ff" stop-opacity="0"/></radialGradient>
"""
    ox, oy, k = 780, 170, 9.5
    quads = [
        [(4, 10), (30, 8), (30, 30), (4, 30)],
        [(4, 34), (30, 34), (30, 58), (4, 57)],
        [(34, 7), (60, 3), (60, 30), (34, 30)],
        [(34, 34), (60, 34), (60, 61), (34, 58)],
    ]
    lines, nodes = [], []
    for qd in quads:
        pts = [(ox + x * k, oy + y * k) for x, y in qd]
        lines.append(f'<polygon points="{" ".join(f"{a:.0f},{b:.0f}" for a, b in pts)}" fill="none" stroke="#cfe6ff" stroke-opacity="0.45" stroke-width="1.5"/>')
        for a, b in pts:
            nodes.append(f'<circle cx="{a:.0f}" cy="{b:.0f}" r="14" fill="url(#star)"/><circle cx="{a:.0f}" cy="{b:.0f}" r="2.6" fill="#fff"/>')
    # Inner stars: glass, grapes, swoosh.
    for x, y in [(9.5, 12.5), (24.5, 12.5), (17, 25.5), (17, 28.5), (11, 42), (17, 42), (23, 42), (14, 47.6), (20, 47.6), (17, 53.1), (37, 55.5), (49, 52), (59.3, 39)]:
        a, b = ox + x * k, oy + y * k
        nodes.append(f'<circle cx="{a:.0f}" cy="{b:.0f}" r="8" fill="url(#star)"/><circle cx="{a:.0f}" cy="{b:.0f}" r="1.6" fill="#fff"/>')
    g = [(9.5, 12.5), (24.5, 12.5), (17, 25.5), (9.5, 12.5)]
    lines.append(f'<polyline points="{" ".join(f"{ox + x * k:.0f},{oy + y * k:.0f}" for x, y in g)}" fill="none" stroke="#cfe6ff" stroke-opacity="0.3"/>')
    lines.append(f'<polyline points="{" ".join(f"{ox + x * k:.0f},{oy + y * k:.0f}" for x, y in [(37, 55.5), (49, 52), (59.3, 39)])}" fill="none" stroke="#cfe6ff" stroke-opacity="0.3"/>')
    # Linux Torvalds Minor: faint penguin outline, lower left, with the little drawing under it at low opacity.
    lx, ly = 300, 640
    peng = [(0, 0), (-28, 30), (-40, 90), (-30, 140), (-50, 160), (0, 150), (50, 160), (30, 140), (40, 90), (28, 30), (0, 0)]
    lines.append(f'<polyline points="{" ".join(f"{lx + x},{ly + y}" for x, y in peng)}" fill="none" stroke="#cfe6ff" stroke-opacity="0.18"/>')
    for x, y in peng[:-1]:
        nodes.append(f'<circle cx="{lx + x}" cy="{ly + y}" r="1.4" fill="#fff" opacity="0.7"/>')
    hidden = linus(lx - 60, ly - 6, 172, 'opacity="0.07"')
    body = (
        '<rect width="1920" height="1080" fill="url(#bg)"/>'
        '<ellipse cx="1000" cy="420" rx="620" ry="300" fill="url(#neb)" transform="rotate(-20 1000 420)"/>'
        '<ellipse cx="1300" cy="640" rx="520" ry="240" fill="url(#neb2)" transform="rotate(15 1300 640)"/>'
        + stars(rng, 520)
        + hidden
        + "".join(lines)
        + "".join(nodes)
        + f'<text x="{ox + 64 * k + 30:.0f}" y="{oy + 20}" font-family="{FONT}" font-size="22" fill="#cfe6ff" fill-opacity="0.75" letter-spacing="4" font-style="italic">FENESTRA VINIFERA</text>'
        f'<text x="{ox + 64 * k + 30:.0f}" y="{oy + 48}" font-family="{FONT}" font-size="15" fill="#cfe6ff" fill-opacity="0.5">visible from every desktop, all year</text>'
        f'<text x="{lx + 60}" y="{ly + 170}" font-family="{FONT}" font-size="11" fill="#cfe6ff" fill-opacity="0.28" font-style="italic">Linux Torvalds Minor</text>'
        + brand()
    )
    return svg("Constellation", body, defs)


# 11 Daylight: the light one. Soft panes on white.
def daylight():
    defs = f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e3e9f3"/></linearGradient>
<filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="40"/></filter>
<linearGradient id="pr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f3b6c6"/><stop offset="1" stop-color="{ROSE}"/></linearGradient>
<linearGradient id="pb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#b9dcff"/><stop offset="1" stop-color="{SKY}"/></linearGradient>
"""
    body = (
        '<rect width="1920" height="1080" fill="url(#bg)"/>'
        '<g filter="url(#blur)" opacity="0.55">'
        '<polygon points="1050,160 1400,140 1400,460 1050,460" fill="url(#pr)"/>'
        '<polygon points="1050,500 1400,500 1400,840 1050,830" fill="url(#pr)"/>'
        '<polygon points="1440,130 1800,80 1800,460 1440,460" fill="url(#pb)"/>'
        '<polygon points="1440,500 1800,500 1800,880 1440,840" fill="url(#pb)"/>'
        "</g>"
        '<g stroke="#0a4fd6" stroke-opacity="0.07" stroke-width="2">'
        + "".join(f'<line x1="{-400 + i * 90}" y1="1080" x2="{400 + i * 90}" y2="0"/>' for i in range(30))
        + "</g>"
        + use("mark", 560, 330, 300)
        + f'<text x="710" y="720" text-anchor="middle" font-family="{FONT}" font-size="52" fill="#14213d" font-weight="300">GigaHard <tspan font-weight="bold">Winedows</tspan></text>'
        + brand(dark_bg=False)
    )
    return svg("Daylight", body, defs)


# 12 Horizon: flat sunrise over the sea, the sun cut into four panes.
def horizon():
    defs = f"""
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="0.6" stop-color="#3a1f7a"/><stop offset="1" stop-color="{ROSE}"/></linearGradient>
<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2a7a"/><stop offset="1" stop-color="#030a26"/></linearGradient>
<linearGradient id="sunr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff7aa0"/><stop offset="1" stop-color="{WINE}"/></linearGradient>
<linearGradient id="sunb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fd0ff"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
<clipPath id="sun"><circle cx="960" cy="640" r="300"/></clipPath>
<radialGradient id="halo"><stop offset="0" stop-color="#ffb0c8" stop-opacity="0.45"/><stop offset="1" stop-color="#ffb0c8" stop-opacity="0"/></radialGradient>
"""
    gap = 14
    slits = "".join(
        f'<rect x="600" y="{640 - 30 * i - i * i * 1.2:.0f}" width="720" height="{3 + i * 1.6:.1f}" fill="url(#sky)"/>'
        for i in range(1, 7)
    )
    refl = "".join(
        f'<rect x="{960 - (300 - j * 30)}" y="{660 + j * 26}" width="{2 * (300 - j * 30)}" height="{10 - j * 0.6:.1f}" fill="{"url(#sunr)" if j % 2 else "url(#sunb)"}" opacity="{0.6 - j * 0.05:.2f}"/>'
        for j in range(10)
    )
    body = (
        '<rect width="1920" height="1080" fill="url(#sky)"/>'
        '<circle cx="960" cy="640" r="560" fill="url(#halo)"/>'
        '<g clip-path="url(#sun)">'
        f'<rect x="660" y="340" width="{300 - gap / 2}" height="{300 - gap / 2}" fill="url(#sunr)"/>'
        f'<rect x="{960 + gap / 2}" y="340" width="300" height="{300 - gap / 2}" fill="url(#sunb)"/>'
        + slits
        + "</g>"
        + f'<rect x="{960 - gap / 2}" y="330" width="{gap}" height="310" fill="url(#sky)"/>'
        + '<rect y="640" width="1920" height="440" fill="url(#sea)"/>'
        + refl
        + brand()
    )
    return svg("Horizon", body, defs)


WALLPAPERS = [
    ("01-hero", hero),
    ("02-panes", panes),
    ("03-tiles", tiles),
    ("04-vineyard", vineyard),
    ("05-vintage", vintage),
    ("06-bedrock", bedrock),
    ("07-no-problems", noproblems),
    ("08-aurora", aurora),
    ("09-blueprint", blueprint),
    ("10-constellation", constellation),
    ("11-daylight", daylight),
    ("12-horizon", horizon),
]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "build/config/includes.chroot/usr/share/winedows/wallpapers")
    os.makedirs(out, exist_ok=True)
    for name, fn in WALLPAPERS:
        path = os.path.join(out, name + ".svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(fn())
        print(path)


if __name__ == "__main__":
    main()
