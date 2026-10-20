#!/usr/bin/env python3
"""Draw doc/motor_17hs08.svg: the StepperOnline 17HS08-1004S NEMA 17 pancake stepper, dimensioned.

Usage: python tools/motor_svg.py   (run from the window-vent folder)
Front view (shaft end) and side view, after the maker's dimension sheet (in the box), checked with a caliper.
The corner chamfers are not on the sheet: drawn about 5 mm, approximate.
"""
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "motor_17hs08.svg")

BODY, BODY_L = 42.3, 20.5    # square frame (max), length
CHAMF = 5.0                  # corner chamfer (approximate, not on the sheet)
HOLES = 31.0                 # M3 screw spacing
HOLE_DEPTH = 2.5             # M3 thread depth (min on the sheet; measured 2.5)
BOSS_D, BOSS_H = 22.0, 2.0   # centring boss
SHAFT_D, SHAFT_L = 5.0, 20.0 # shaft, its length from the frame's face
FLAT_L, FLAT_W = 16.5, 4.5   # D-flat: length from the tip, size across the flat
WIRE_L = 400                 # leads, UL1007 AWG24
LEAD_COLOURS = ["#1565c0", "#2e7d32", "#d32f2f", "#111"]   # blue, green, red, black, left to right in the front view

K = 9                        # px per mm
W, H = 1410, 900
C_DIM = "#b3261e"
C_BODY, C_DARK = "#c9ccd1", "#2a2a2a"

out = []


def text(x, y, s, size=15, anchor="middle", color="#111", weight="normal", rotate=None):
    tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}"{tr}>{s}</text>')


def line(x1, y1, x2, y2, color="#111", width=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d}/>')


def arrow(x, y, dx, dy, color=C_DIM):
    n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
    p1 = (x - ux * 10 - uy * 4, y - uy * 10 + ux * 4)
    p2 = (x - ux * 10 + uy * 4, y - uy * 10 - ux * 4)
    out.append(f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def hdim(a, b, y, ey, label):
    """horizontal dimension between canvas x = a and b at canvas y; extension lines from canvas y = ey"""
    s = 6 if y > ey else -6
    line(a, ey, a, y + s, C_DIM, 1, "3,3"); line(b, ey, b, y + s, C_DIM, 1, "3,3")
    line(a, y, b, y, C_DIM, 1.5); arrow(a, y, -1, 0); arrow(b, y, 1, 0)
    text((a + b) / 2, y - 7, label, 15, color=C_DIM)


def vdim(a, b, x, ex, label, side=-1):
    """vertical dimension between canvas y = a and b at canvas x; extension lines from canvas x = ex"""
    s = 6 if x > ex else -6
    line(ex, a, x + s, a, C_DIM, 1, "3,3"); line(ex, b, x + s, b, C_DIM, 1, "3,3")
    line(x, a, x, b, C_DIM, 1.5); arrow(x, a, 0, -1); arrow(x, b, 0, 1)
    tx = x - 8 if side < 0 else x + 18
    text(tx, (a + b) / 2, label, 15, color=C_DIM, rotate=-90)


# --- front view, shaft end -------------------------------------------------------------------------
FX, FY = 420, 440                       # canvas centre of the shaft
h, c = BODY / 2 * K, CHAMF * K
pts = [(-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c)]
out.append('<polygon points="' + " ".join(f"{FX + x:.1f},{FY + y:.1f}" for x, y in pts) +
           f'" fill="{C_BODY}" stroke="#222" stroke-width="2"/>')
out.append(f'<circle cx="{FX}" cy="{FY}" r="{BOSS_D / 2 * K}" fill="#dfe2e6" stroke="#222" stroke-width="1.5"/>')
out.append(f'<circle cx="{FX}" cy="{FY}" r="{BOSS_D / 2 * K - 18}" fill="none" stroke="#777" stroke-width="1"/>')
r = SHAFT_D / 2 * K                     # shaft with its D-flat on the right
fx = (FLAT_W - SHAFT_D / 2) * K
a = math.acos(fx / r)
out.append(f'<path d="M {FX + fx:.1f},{FY - r * math.sin(a):.1f} A {r:.1f} {r:.1f} 0 1 0 {FX + fx:.1f},{FY + r * math.sin(a):.1f} Z" '
           f'fill="#9aa0a8" stroke="#222" stroke-width="1.5"/>')
for sx in (-1, 1):
    for sy in (-1, 1):
        out.append(f'<circle cx="{FX + sx * HOLES / 2 * K:.1f}" cy="{FY + sy * HOLES / 2 * K:.1f}" r="{1.5 * K}" '
                   f'fill="#ffffff" stroke="#222" stroke-width="1.5"/>')
for i in range(4):                      # leads, out of the bottom face
    x = FX + (i - 1.5) * 9
    line(x, FY + h, x, FY + h + 70, LEAD_COLOURS[i], 3)
line(FX - 25, FY + h + 70, FX + 25, FY + h + 70, "#777", 1, "4,3")
text(FX + 32, FY + h + 60, f"leads {WIRE_L} ± 10 (UL1007 AWG24)", 14, "start", "#333")

top = FY - h
hdim(FX - h, FX + h, top - 70, top, f"{BODY} max")
hdim(FX - HOLES / 2 * K, FX + HOLES / 2 * K, top - 30, FY - HOLES / 2 * K, f"{HOLES:g} ± 0.2")
vdim(FY - h, FY + h, FX + h + 75, FX + h, f"{BODY} max", side=1)
vdim(FY - HOLES / 2 * K, FY + HOLES / 2 * K, FX + h + 35, FX + HOLES / 2 * K, f"{HOLES:g} ± 0.2", side=1)
lx, ly = FX - HOLES / 2 * K, FY + HOLES / 2 * K   # hole callout
line(lx - 10, ly + 10, lx - 70, ly + 70, C_DIM, 1.2); line(lx - 70, ly + 70, lx - 240, ly + 70, C_DIM, 1.2)
text(lx - 240, ly + 64, f"4 x M3, {HOLE_DEPTH} deep min", 14, "start", C_DIM, "bold")
text(lx - 240, ly + 88, "(measured 2.5)", 13, "start", C_DIM)
text(FX, FY - h - 110, "Front view (shaft end)", 17, weight="bold")

# --- side view: shaft tip on the left, as on the sheet --------------------------------------------
SX, SY = 960, 440                       # canvas position of the shaft tip, on the axis
def sx(mm):                             # distance from the shaft tip (mm) -> canvas x
    return SX + mm * K
face = SHAFT_L                          # frame's front face
out.append(f'<rect x="{sx(face):.1f}" y="{SY - h:.1f}" width="{BODY_L * K:.1f}" height="{2 * h:.1f}" fill="{C_BODY}" stroke="#222" stroke-width="2"/>')
for z in (0.3, 0.7):                    # the end caps' seams (approximate)
    x = sx(face + BODY_L * z)
    line(x, SY - h, x, SY + h, "#888", 1)
out.append(f'<rect x="{sx(face - BOSS_H):.1f}" y="{SY - BOSS_D / 2 * K:.1f}" width="{BOSS_H * K:.1f}" height="{BOSS_D * K:.1f}" fill="#dfe2e6" stroke="#222" stroke-width="1.5"/>')
out.append(f'<rect x="{sx(0):.1f}" y="{SY - r:.1f}" width="{(face - BOSS_H) * K:.1f}" height="{2 * r:.1f}" fill="#9aa0a8" stroke="#222" stroke-width="1.5"/>')
line(sx(FLAT_L), SY - r, sx(FLAT_L), SY - r + (SHAFT_D - FLAT_W) * K, "#222", 1.5)   # end of the D-flat
line(sx(0), SY - r + (SHAFT_D - FLAT_W) * K, sx(FLAT_L), SY - r + (SHAFT_D - FLAT_W) * K, "#222", 1.5)
line(sx(-3), SY, sx(face + BODY_L + 3), SY, "#777", 1, "10,4,2,4")                    # axis
for i in range(4):                      # leads, at the back end of the bottom face
    x = sx(face + BODY_L - 2.5) + (i - 1.5) * 4
    line(x, SY + h, x, SY + h + 70, LEAD_COLOURS[i], 3)

top = SY - h
hdim(sx(0), sx(face), top - 70, SY - r, f"{SHAFT_L:g} ± 1")
hdim(sx(face), sx(face + BODY_L), top - 70, top, f"{BODY_L} ± 1")
hdim(sx(0), sx(FLAT_L), top - 30, SY - r, f"{FLAT_L} ± 0.25 flat")
hdim(sx(face - BOSS_H), sx(face), SY + h + 40, SY + BOSS_D / 2 * K, f"{BOSS_H:g} ± 0.25")
vdim(SY - BOSS_D / 2 * K, SY + BOSS_D / 2 * K, sx(-15), sx(face - BOSS_H), f"Ø {BOSS_D:g} (0 / -0.05)")
vdim(SY - r, SY + r, sx(-9), sx(0), f"Ø {SHAFT_D:g} (0 / -0.012)")
vdim(SY - r + (SHAFT_D - FLAT_W) * K, SY + r, sx(-3.5), sx(0), f"{FLAT_W} ± 0.1")
text((sx(0) + sx(face + BODY_L)) / 2, SY - h - 110, "Side view", 17, weight="bold")

text(40, 50, "StepperOnline 17HS08-1004S, NEMA 17 pancake stepper (mm)", 22, "start", weight="bold")
notes = ["After the maker's dimension sheet, checked with a caliper. Corner chamfers and end-cap seams are approximate.",
         "The M3 holes are only 2.5 mm deep: a screw may reach at most 2.5 mm past the motor plate's top face.",
         "Shaft Ø 5 with a D-flat (4.5 across) along its last 16.5 mm; it carries the flexible coupler."]
for i, n in enumerate(notes):
    out.append(f'<text x="40" y="{H - 80 + i * 24}" font-size="14" fill="#333">{n}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
