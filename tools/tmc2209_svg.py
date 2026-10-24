#!/usr/bin/env python3
"""Draw doc/tmc2209.svg: the TMC2209 stepper driver module (StepStick format, V985 board), dimensioned.

Usage: python tools/tmc2209_svg.py   (run from the window-vent folder)
Top view, heatsink side up, VM/EN end at the top (as on the seller's pinout); side view from the DIR/GND end.
PCB and heatsink sizes are the seller's; the row spacing and pin span are the StepStick standard; the side-view
heights are assumed equal to the ESP32-S3 board's. All to verify on the part.
"""
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "tmc2209.svg")

PW, PL = 15.08, 20.81                # PCB width (across the rows), length (along the rows), measured
SINK = (14.4, 15.0, 13.08)           # heatsink: across the rows, along the rows (its fins), height on the PCB; measured
ROW_SPACING = 12.7                   # StepStick: 0.5 in, 5 perfboard holes
PITCH = 2.54
PCB_T, SPACER, PIN_BELOW = 1.62, 2.62, 5.8    # measured
BASE, FLAT = 2.25, 10.0                       # heatsink: PCB to the fin valleys, flat contact width (measured)
RELIEF = BASE                                 # the edge reliefs rise to the valleys
OUTER_VALLEY = 3.5                            # PCB to the two outer valleys, next to the edge fins (measured)
FINS, FIN_T = 7, 1.0                          # fins (counted), their thickness (estimated)
LEFT = ["EN", "MS1", "MS2", "PDN", "UART", "CLK", "STEP", "DIR"]
RIGHT = ["VM", "GND", "M1B", "M1A", "M2A", "M2B", "VIO", "GND"]

K = 20                               # px per mm
OX, OY = 300, 200                    # canvas position of the PCB's top-left corner
W, H = 1420, 900
C_DIM = "#b3261e"

out = []


def px(x, y):
    return OX + x * K, OY + y * K


def text(x, y, s, size=15, anchor="middle", color="#111", weight="normal", rotate=None):
    tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}"{tr}>{s}</text>')


def line(x1, y1, x2, y2, color="#111", width=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d}/>')


def arrow(x, y, dx, dy, color):
    n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
    a, b = 10, 4
    p1 = (x - ux * a - uy * b, y - uy * a + ux * b)
    p2 = (x - ux * a + uy * b, y - uy * a - ux * b)
    out.append(f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def hdim(x1, x2, y, ext_y, label, color=C_DIM):
    """horizontal dimension between x1 and x2 (mm) at canvas y; extension lines from board y = ext_y (mm)"""
    (a, ey), (b, _) = px(x1, ext_y), px(x2, ext_y)
    line(a, ey, a, y + (6 if y > ey else -6), color, 1, "3,3"); line(b, ey, b, y + (6 if y > ey else -6), color, 1, "3,3")
    line(a, y, b, y, color, 1.5); arrow(a, y, -1, 0, color); arrow(b, y, 1, 0, color)
    text((a + b) / 2, y - 7, label, 15, color=color)


def vdim(y1, y2, x, ext_x, label, color=C_DIM):
    """vertical dimension between y1 and y2 (mm) at canvas x; extension lines from board x = ext_x (mm)"""
    (ex, a), (_, b) = px(ext_x, y1), px(ext_x, y2)
    line(ex, a, x + (6 if x > ex else -6), a, color, 1, "3,3"); line(ex, b, x + (6 if x > ex else -6), b, color, 1, "3,3")
    line(x, a, x, b, color, 1.5); arrow(x, a, 0, -1, color); arrow(x, b, 0, 1, color)
    text(x - 8, (a + b) / 2, label, 15, color=color, rotate=-90)


# --- top view: PCB, pads, potentiometer, heatsink outline -------------------------------------------
x0, y0 = px(0, 0)
out.append(f'<rect x="{x0}" y="{y0}" width="{PW * K}" height="{PL * K}" rx="4" fill="#1e1e1e" stroke="#000" stroke-width="2"/>')
a, b = px(PW / 2 - 4.25, PL / 2 - 3.5)                         # thermal pad (approximate)
out.append(f'<rect x="{a}" y="{b}" width="{8.5 * K}" height="{9.5 * K}" fill="#c9a55a" stroke="#8a6d2a"/>')
for x, y in ((3.6, 1.3), (5.6, 1.3), (4.6, 3.0)):               # EN jumper pads (approximate)
    cx, cy = px(x, y)
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.75 * K}" fill="#d9a520" stroke="#7a5c00" stroke-width="1.5"/>')
text(*px(3.0, 4.6), "EN", 12, color="#ffffff")
a, b = px(9.3, 0.6)                                             # potentiometer (approximate)
out.append(f'<rect x="{a}" y="{b}" width="{2.8 * K}" height="{3 * K}" rx="3" fill="#bbbbbb" stroke="#555"/>')
cx, cy = px(10.7, 2.1)
out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.9 * K}" fill="#888" stroke="#333"/>')
sx0 = (PW - SINK[0]) / 2                                        # heatsink footprint: the same gap at the sides
sy0 = PL - SINK[1] - sx0                                        #   and at the DIR/GND end, clear of the potentiometer
a, b = px(sx0, sy0)
out.append(f'<rect x="{a}" y="{b}" width="{SINK[0] * K}" height="{SINK[1] * K}" fill="#2f5fd0" fill-opacity="0.18" '
           f'stroke="#2f5fd0" stroke-width="2" stroke-dasharray="8,5"/>')
hx, hy = px(PW / 2, PL / 2 + 1.25)                              # centre of the thermal pad, level with UART and M2A
text(hx, hy + 5, "heatsink", 14, color="#1b3a8a", weight="bold")
text(*px(PW / 2, PL - 1.2), "TMC2209", 14, color="#e8c34a", weight="bold")

r1 = (PW - ROW_SPACING) / 2
first = (PL - 7 * PITCH) / 2
for col, labels, side in ((r1, LEFT, -1), (PW - r1, RIGHT, 1)):
    for i, lab in enumerate(labels):
        cx, cy = px(col, first + i * PITCH)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.8 * K}" fill="#f4d35e" stroke="#7a5c00"/>')
        lx = cx + side * (r1 * K + 12)
        text(lx, cy + 5, lab, 14, "start" if side > 0 else "end", "#1b5fa8", "bold")

# --- dimensions -------------------------------------------------------------------------------------
hdim(0, PW, OY - 70, 0, f"{PW:g}")
hdim(sx0, sx0 + SINK[0], OY - 30, sy0, f"{SINK[0]} heatsink")
vdim(0, PL, OX - 150, 0, f"{PL:g}")
vdim(sy0, sy0 + SINK[1], OX - 110, sx0, f"{SINK[1]:g} heatsink")
vdim(0, sy0, OX - 110, sx0, f"{sy0:.2f}")
bot = OY + PL * K + 60
hdim(r1, PW - r1, bot, PL - first, f"{ROW_SPACING}")
text(OX + PW * K / 2, bot + 28, "between the rows: 5 hole pitches (6 holes, both rows counted)", 15, color=C_DIM)
vdim(first, first + 7 * PITCH, OX + PW * K + 160, PW + 2.2, f"7 x {PITCH} = {7 * PITCH:.2f}")
vdim(first + 7 * PITCH, PL, OX + PW * K + 200, PW + 2.2, f"{first:.2f}")

text(40, 50, "TMC2209 stepper driver module (StepStick format): top view, heatsink side up, and side view (mm)", 22, "start", weight="bold")

# --- side view (from the DIR/GND end), to the right -----------------------------------------------
SX, SY, SK = 1010, 560, 16      # left end of the PCB's underside on the canvas, scale
def sp(x, z):                  # side-view mm -> canvas (z up, 0 = PCB underside)
    return SX + x * SK, SY - z * SK
def srect(x0, z0, x1, z1, fill, stroke="#222"):
    a, b = sp(x0, z1)
    out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{(x1 - x0) * SK:.1f}" height="{(z1 - z0) * SK:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
srect(0, 0, PW, PCB_T, "#1e1e1e")                                             # PCB
srect(PW / 2 - 2.5, -0.9, PW / 2 + 2.5, 0, "#444")                            # TMC2209 chip, on the underside
for col in (r1, PW - r1):
    srect(col - 1.25, -SPACER, col + 1.25, 0, "#555")                        # plastic spacer
    srect(col - 0.32, -SPACER - PIN_BELOW, col + 0.32, -SPACER, "#f4d35e")  # pin
for col in (r1, PW - r1):                                                    # pin tips and solder, above the PCB
    a, b = sp(col - 0.8, PCB_T); c, d = sp(col, PCB_T + 0.8); e, _ = sp(col + 0.8, PCB_T)
    out.append(f'<polygon points="{a:.1f},{b:.1f} {c:.1f},{d:.1f} {e:.1f},{b:.1f}" fill="#c8c8c8" stroke="#555"/>')
# heatsink, seen along its fins: base with a flat contact strip and a relief at each edge over the pin tips, then the fins
rw = (SINK[0] - FLAT) / 2
pts = [sp(sx0 + rw + FLAT, PCB_T)]
pts += [sp(sx0 + SINK[0] - rw * math.cos(t), PCB_T + RELIEF * math.sin(t)) for t in [i * math.pi / 2 / 12 for i in range(13)]]
gap = (SINK[0] - FINS * FIN_T) / (FINS - 1)
for i in reversed(range(FINS)):
    f0 = sx0 + i * (FIN_T + gap)
    pts += [sp(f0 + FIN_T, PCB_T + SINK[2]), sp(f0, PCB_T + SINK[2])]
    if i:
        v = OUTER_VALLEY if i in (1, FINS - 1) else BASE
        pts += [sp(f0, PCB_T + v), sp(f0 - gap, PCB_T + v)]
pts += [sp(sx0 + rw * math.cos(t), PCB_T + RELIEF * math.sin(t)) for t in [math.pi / 2 - i * math.pi / 2 / 12 for i in range(13)]]
out.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '" fill="#2f5fd0" stroke="#1b3a8a" stroke-width="1.5"/>')
def sdim(z0, z1, x, label, ext_x, left=False):
    a, b = sp(x, z0); _, c = sp(x, z1); ex, _ = sp(ext_x, 0)
    d = -6 if left else 6
    line(ex, b, a + d, b, C_DIM, 1, "3,3"); line(ex, c, a + d, c, C_DIM, 1, "3,3")
    line(a, b, a, c, C_DIM, 1.5); arrow(a, b, 0, 1, C_DIM); arrow(a, c, 0, -1, C_DIM)
    text(a - 10 if left else a + 10, (b + c) / 2 + 5, label, 14, "end" if left else "start", C_DIM)
sdim(0, PCB_T, PW + 3, f"{PCB_T} PCB", PW)
sdim(-SPACER, 0, PW + 3, f"{SPACER} spacer", PW)
sdim(-SPACER - PIN_BELOW, -SPACER, PW + 3, f"{PIN_BELOW} pins", PW)
sdim(PCB_T, PCB_T + SINK[2], -3, f"{SINK[2]:g} heatsink", sx0, left=True)
sdim(PCB_T, PCB_T + BASE, PW + 3, f"{BASE:g} base", PW)
zf = -SPACER - PIN_BELOW - 1.5                                                # flat contact strip, dimensioned below the pins
a, b = sp(sx0 + rw, zf); c, _ = sp(sx0 + rw + FLAT, zf); _, t = sp(0, PCB_T)
line(a, t, a, b + 6, C_DIM, 1, "3,3"); line(c, t, c, b + 6, C_DIM, 1, "3,3")
line(a, b, c, b, C_DIM, 1.5); arrow(a, b, -1, 0, C_DIM); arrow(c, b, 1, 0, C_DIM)
text((a + c) / 2, b + 20, f"{FLAT:g}: the heatsink's flat base on the PCB", 13, color=C_DIM)
text(SX, SY - 17 * SK, "Side view, from the DIR/GND end", 15, "start", weight="bold")
notes = ["Sizes and heights measured on the module; row spacing and pin span are the StepStick standard (0.5 in rows, 0.1 in pitch).",
         "Heatsink: 13.2 high with its thermal sticker, 14.70 from the PCB underside to its top once pressed on. It sits toward the DIR/GND end,",
         "clear of the potentiometer, with the same small gap there as at its sides; its base touches the PCB on a 10 mm strip, relieved over the pin tips.",
         "The chip is on the underside; its thermal pad, the heatsink side, faces up. The fins run along the pin rows.",
         "Thermal pad, EN pads and potentiometer positions are approximate."]
for i, n in enumerate(notes):
    out.append(f'<text x="40" y="{H - 110 + i * 24}" font-size="14" fill="#333">{n}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
