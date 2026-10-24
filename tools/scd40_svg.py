#!/usr/bin/env python3
"""Draw doc/scd40.svg: the SCD40 CO2 sensor module (the small blue board), dimensioned.

Usage: python tools/scd40_svg.py   (run from the window-vent folder)
Top view, sensor side up, pins at the bottom (as in the seller's picture); side view from the pin edge.
Board size, thickness, height and pin positions are measured; the sensor's place on the board and the corner hole
are estimates (the sensor's size is Sensirion's, 10.1 x 10.1 mm).
"""
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "scd40.svg")

# measured
BW, BL, BT = 13.70, 21.70, 1.62     # board width, length, thickness
TOP = 7.85                          # board underside to the sensor's top
EDGE_X, EDGE_Y = 2.63, 1.00         # board edge to pin 1's hole edge: from the left edge, from the bottom edge
PIN_D = 1.0                         # the pin holes: standard for 2.54 mm headers
PIN1_X, PIN_Y = EDGE_X + PIN_D / 2, EDGE_Y + PIN_D / 2   # pin 1's centre
PITCH = 2.54
PINS = ["GND", "VDD", "SCL", "SDA"]
# estimates
SENS = 10.1                         # SCD40 package (Sensirion), centred across the board
SENS_TOP = 1.5                      # its distance from the top edge
HOLE = (0.9, 0.9, 1.1)              # corner hole: centre x, y from the top-left corner, diameter

K = 22                              # px per mm
OX, OY = 190, 140                   # canvas position of the board's top-left corner
W, H = 1200, 850
C_DIM, C_EST = "#b3261e", "#7a7a7a"
out = []


def px(x, y):
    return OX + x * K, OY + y * K


def text(x, y, s, size=15, anchor="middle", color="#111", weight="normal", rotate=None, italic=False):
    tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
    st = ' font-style="italic"' if italic else ""
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}"{tr}{st}>{s}</text>')


def line(x1, y1, x2, y2, color="#111", width=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d}/>')


def arrow(x, y, dx, dy, color):
    n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
    a, b = 10, 4
    p1 = (x - ux * a - uy * b, y - uy * a + ux * b)
    p2 = (x - ux * a + uy * b, y - uy * a - ux * b)
    out.append(f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def hdim(x1, x2, y, ext_y, label, color=C_DIM, below=False):
    """horizontal dimension between board x1 and x2 (mm), drawn at canvas y; extension lines from board y = ext_y"""
    (a, ey), (b, _) = px(x1, ext_y), px(x2, ext_y)
    s = 6 if y > ey else -6
    line(a, ey, a, y + s, color, 1, "3,3"); line(b, ey, b, y + s, color, 1, "3,3")
    line(a, y, b, y, color, 1.5); arrow(a, y, -1, 0, color); arrow(b, y, 1, 0, color)
    text((a + b) / 2, y + (20 if below else -7), label, 15, color=color, italic=(color == C_EST))


def vdim(y1, y2, x, ext_x, label, color=C_DIM, left=False):
    """vertical dimension between board y1 and y2 (mm), drawn at canvas x; extension lines from board x = ext_x"""
    (ex, a), (_, b) = px(ext_x, y1), px(ext_x, y2)
    s = 6 if x > ex else -6
    line(ex, a, x + s, a, color, 1, "3,3"); line(ex, b, x + s, b, color, 1, "3,3")
    line(x, a, x, b, color, 1.5); arrow(x, a, 0, -1, color); arrow(x, b, 0, 1, color)
    text(x + (-10 if left else 10), (a + b) / 2 + 5, label, 15, "end" if left else "start", color, italic=(color == C_EST))


# --- top view ----------------------------------------------------------------------------------------------------
x0, y0 = px(0, 0)
out.append(f'<rect x="{x0}" y="{y0}" width="{BW * K}" height="{BL * K}" rx="5" fill="#1f49a8" stroke="#0f2a66" stroke-width="2"/>')
hx, hy = px(HOLE[0], HOLE[1])
out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{HOLE[2] / 2 * K:.1f}" fill="#d9d9d9" stroke="#888"/>')
sx = (BW - SENS) / 2
a, b = px(sx - 0.4, SENS_TOP - 0.4)
out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{(SENS + 0.8) * K:.1f}" height="{(SENS + 0.8) * K:.1f}" fill="#1b6e4a" stroke="#0e4a30"/>')
a, b = px(sx, SENS_TOP)
out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{SENS * K:.1f}" height="{SENS * K:.1f}" rx="8" fill="#c8c8c8" stroke="#666" stroke-width="2"/>')
a, b = px(sx + 2.2, SENS_TOP + 2.2)
out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{(SENS - 4.4) * K:.1f}" height="{(SENS - 4.4) * K:.1f}" rx="6" fill="#f4f4f4" stroke="#999"/>')
cx, cy = px(BW / 2, SENS_TOP + SENS / 2)
text(cx, cy - 12, "SCD40", 17, weight="bold", color="#333")
text(cx, cy + 8, "membrane:", 12, color="#555")
text(cx, cy + 23, "keep it open", 12, color="#555")
for i, (name, ref) in enumerate((("C1", "C1"), ("R2", "R2"), ("R1", "R1"))):     # the parts row, as on the board
    a, b = px(2.2 + i * 3.6, 14.4)
    out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{2.4 * K:.1f}" height="{1.3 * K:.1f}" rx="2" '
               f'fill="{"#c9a46a" if ref == "C1" else "#222"}" stroke="#bbb"/>')
    text(a + 1.2 * K, b - 6, ref, 13, color="#ffffff")
for i, name in enumerate(PINS):
    cx, cy = px(PIN1_X + i * PITCH, BL - PIN_Y)
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.85 * K:.1f}" fill="#e8e8e8" stroke="#888" stroke-width="2"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{PIN_D / 2 * K:.1f}" fill="#1f49a8"/>')
    text(cx, cy - 26, name, 15, color="#ffffff", weight="bold")

hdim(0, BW, OY - 48, 0, f"{BW:.2f}")
vdim(0, BL, OX + BW * K + 85, BW, f"{BL:.2f}")
# as measured: from the board's edges to the holes' edges
vdim(BL - EDGE_Y, BL, OX + BW * K + 25, PIN1_X + 3 * PITCH + PIN_D / 2, f"{EDGE_Y:.2f}")
hdim(0, EDGE_X, OY + BL * K + 40, BL - PIN_Y, f"{EDGE_X:.2f}", below=True)
hdim(PIN1_X, PIN1_X + 3 * PITCH, OY + BL * K + 40, BL - PIN_Y, f"3 x {PITCH} = {3 * PITCH:.2f}", below=True)
text(OX + BW * K + 25, OY + BL * K + 26, f"holes Ø {PIN_D:g} (standard)", 13, "start", C_EST, italic=True)
hdim(sx, sx + SENS, OY - 12, SENS_TOP, f"about {SENS:g} (datasheet)", C_EST)
text(OX - 14, hy + 5, f"hole, about Ø {HOLE[2]:g}", 13, "end", C_EST, italic=True)
text(OX + BW * K / 2, OY + BL * K + 95, "Top view, sensor side up", 15, weight="bold")

# --- side view, from the pin edge ----------------------------------------------------------------------------------
SX, SY, SK = 650, 540, 22          # left end of the board's underside, scale


def sp(x, z):
    return SX + x * SK, SY - z * SK


def srect(x0_, z0, x1, z1, fill, stroke="#222"):
    a_, b_ = sp(x0_, z1)
    out.append(f'<rect x="{a_:.1f}" y="{b_:.1f}" width="{(x1 - x0_) * SK:.1f}" height="{(z1 - z0) * SK:.1f}" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')


srect(0, 0, BW, BT, "#1f49a8")
srect(sx - 0.6, BT, sx + SENS + 0.6, BT + 0.6, "#1b6e4a")
srect(sx, BT + 0.6, sx + SENS, TOP, "#c8c8c8", "#666")


def sdim(z0, z1, x, label, ext_x, left=False):
    a_, b_ = sp(x, z0); _, c_ = sp(x, z1); ex_, _ = sp(ext_x, 0)
    d = -6 if left else 6
    line(ex_, b_, a_ + d, b_, C_DIM, 1, "3,3"); line(ex_, c_, a_ + d, c_, C_DIM, 1, "3,3")
    line(a_, b_, a_, c_, C_DIM, 1.5); arrow(a_, b_, 0, 1, C_DIM); arrow(a_, c_, 0, -1, C_DIM)
    text(a_ - 10 if left else a_ + 10, (b_ + c_) / 2 + 5, label, 15, "end" if left else "start", C_DIM)


sdim(0, BT, BW + 1.2, f"{BT} board", BW)
sdim(0, TOP, BW + 6.3, f"{TOP} overall", sx + SENS)
text(SX + BW * SK / 2, SY + 50, "Side view, from the pin edge", 15, weight="bold")
text(SX + BW * SK / 2, SY + 72, "(the pins are plain holes: header to solder)", 13, color="#555")

text(40, 50, "SCD40 CO2 sensor module (Sensirion SCD40 on a 13.7 x 21.7 mm board), mm", 22, "start", weight="bold")
notes = ["Measured: board 13.70 x 21.70 x 1.62; 7.85 from its underside to the sensor's top; pins 2.54 apart; pin 1 (GND)'s hole",
         f"2.63 from the left edge and 1.00 from the bottom edge (edge to hole edge: centres {PIN1_X:.2f} and {PIN_Y:.2f}). "
         "Grey italic values are estimates.",
         "On board: R1, R2 (10k, marked 103): the I2C pull-ups; C1: decoupling. It runs on 3.3 V here (VDD from the ESP32's 3V3).",
         "The controller PCB's J5 has the same order (GND, VDD, SCL, SDA): a straight 4-wire cable. Leave the membrane uncovered."]
for i, n in enumerate(notes):
    text(40, H - 100 + i * 22, n, 14, "start", color="#333")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
