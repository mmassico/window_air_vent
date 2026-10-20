#!/usr/bin/env python3
"""Draw doc/ebox_layout.svg: the electronics box seen from above, to scale, with a proposed perfboard layout.

Usage: python tools/ebox_layout_svg.py   (run from the window-vent folder)
Box dimensions follow the defaults in cad/window_vent.scad; keep them in step. Model coordinates: x across the
window (+x = left seen from the room), y toward the room. The drawing has the room at the bottom.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "ebox_layout.svg")

# Box (from window_vent.scad): ebox_w = 80, ebox_t = 2.4, y from y_br = 15 to duct_len + ebox_t = 91.4
BOX_W, T = 80.0, 2.4
Y0, Y1 = 15.0, 91.4
PB = (70.0, 50.0)            # perfboard
PB_Y = 56.0                  # its centre (y)
PB_HOLES = (66.0, 46.0)
PILLAR = (34.0, 21.0)        # back fixing pillars: x = +/- 34, y = 21 (8 x 8 around)
CABLE_IN = (72.5, 88.5)      # cable entries at the top of both side walls (y range)
ESP = (57.0, 28.5)           # Freenove ESP32-S3 Lite: overall length (with the antenna), width
ESP_PCB = 50.0               # its PCB; the module's antenna sticks out 7 mm beyond it, over the middle 18.5 mm
TMC = (21.0, 15.0)           # TMC2209 module (heatsink 15 x 14.5 on top, fins along the pin rows)
PLUG = 20.0                  # USB-C plug housing, outside the wall
PITCH = 2.54

K = 8                        # px per mm
CX, CY = 640, 120            # canvas position of x = 0, y = Y0
W, H = 1180, 1120

out = []


def P(x, y):
    """model (x, y) -> canvas; +x to the left, room (large y) at the bottom"""
    return CX - x * K, CY + (y - Y0) * K


def rect(x0, y0, x1, y1, fill, stroke="#222", sw=1.5, rx=0, op=1.0):
    a, b = P(max(x0, x1), min(y0, y1))
    out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{abs(x1 - x0) * K:.1f}" height="{abs(y1 - y0) * K:.1f}" rx="{rx}" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" fill-opacity="{op}"/>')


def text(x, y, s, size=14, anchor="middle", color="#111", weight="normal"):
    a, b = P(x, y)
    out.append(f'<text x="{a:.1f}" y="{b:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}">{s}</text>')


def ctext(cx, cy, s, size=14, color="#111", weight="normal"):
    out.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-size="{size}" text-anchor="middle" fill="{color}" font-weight="{weight}">{s}</text>')


# --- box ---------------------------------------------------------------------------------------
xo = BOX_W / 2
rect(-xo, Y0, xo, Y1, "#d9dde3", sw=2)                                   # walls
rect(-xo + T, Y0 + T, xo - T, Y1 - T, "#f7f8fa", sw=1)                   # inside
for sx in (-1, 1):                                                       # back pillars
    rect(sx * PILLAR[0] - 4, Y0 + T, sx * PILLAR[0] + 4, PILLAR[1] + 4, "#c4c9d1", sw=1)
    cx, cy = P(sx * PILLAR[0], PILLAR[1])
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{1.25 * K}" fill="#ffffff" stroke="#222"/>')
    rect(sx * (xo - T / 2) - T / 2, CABLE_IN[0], sx * (xo - T / 2) + T / 2, CABLE_IN[1], "#ffffff", "#b3261e", 2)  # cable entries

# --- perfboard ----------------------------------------------------------------------------------
py0, py1 = PB_Y - PB[1] / 2, PB_Y + PB[1] / 2
rect(-PB[0] / 2, py0, PB[0] / 2, py1, "#e8d6a8", "#8a6d2a", 1.5)
nx, ny = int(PB[0] / PITCH), int(PB[1] / PITCH)
gx0 = -(nx - 1) * PITCH / 2
gy0 = PB_Y - (ny - 1) * PITCH / 2
for i in range(nx):
    for j in range(ny):
        cx, cy = P(gx0 + i * PITCH, gy0 + j * PITCH)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.2" fill="#c9a95a"/>')
for dx in (-1, 1):
    for dy in (-1, 1):
        cx, cy = P(dx * PB_HOLES[0] / 2, PB_Y + dy * PB_HOLES[1] / 2)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{1.0 * K}" fill="#ffffff" stroke="#222" stroke-width="1.5"/>')

# --- ESP32-S3: across the back half, USB end toward the left wall (+x) -------------------------
ex1 = xo - T - 0.5 - 7.62              # USB end, esp_dx = 3 holes in from the wall: the pins clear the corner standoff
ex0 = ex1 - ESP[0]
ey0 = py0 + 0.5                        # esp_dy
ey1 = ey0 + ESP[1]
ax0 = ex1 - ESP_PCB                    # antenna end of the PCB
rect(ax0, ey0, ex1, ey1, "#3b6fb6", "#183a6b", 2, rx=4, op=0.85)
am = (ESP[1] - 18.5) / 2               # antenna tab, 7 x 18.5, beyond the PCB
rect(ex0, ey0 + am, ax0, ey1 - am, "#2a2a2a", "#111", 1.5, rx=1, op=0.9)
rect(ex0 - 4, ey0 + am - 3, ax0 + 6, ey1 - am + 3, "none", "#b3261e", 1.5)   # keep-out
text(ex0 - 4, py0 - 1.5, "antenna: no wires or copper nearby", 11, "end", "#b3261e")
for e in (ey0 + 1.6, ey1 - 1.6):       # its two header rows (20 pins each, 25.3 apart, centred on the PCB)
    for i in range(20):
        cx, cy = P(ex1 - (ESP_PCB - 19 * PITCH) / 2 - i * PITCH, e)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.4" fill="#f4d35e"/>')
cx, cy = P((ax0 + ex1) / 2, (ey0 + ey1) / 2)
ctext(cx, cy - 4, "ESP32-S3", 18, "#ffffff", "bold")
ctext(cx, cy + 16, "PCB 50 x 28.5 (+ 7 mm antenna)", 13, "#ffffff")
# the board's two USB-C connectors at its left end (measured): USB-OTG 5.5 toward the back, USB-UART 6.0 toward the room
for dy, lab in ((-5.5, "OTG"), (6.0, "UART")):
    rect(ex1 - 7.5, (ey0 + ey1) / 2 + dy - 4.5, ex1, (ey0 + ey1) / 2 + dy + 4.5, "#c0c0c0", "#555", 1.2, rx=2)
    text(ex1 - 3.75, (ey0 + ey1) / 2 + dy + 1.3, lab, 10)
# USB-C plug through the left wall, into USB-UART (it reaches 7.6 mm into the box)
uy = (ey0 + ey1) / 2 + 6.0
rect(ex1 - 1, uy - 5.5, xo + PLUG, uy + 5.5, "#6b6b6b", "#333", 1.5, rx=3)
text(xo + PLUG / 2, uy + 10, "USB-C plug", 13)
text(xo + PLUG + 2, uy - 7.5, "power + console", 12, "start", "#444")
# diamond openings in both side walls, seen edge-on: mark their extent. The right-hand one serves the alternative
# layout (view ebox_elec_alt): the ESP32 turned 180 deg in the same place, so its USB-UART lands 6.0 toward the window
uy_alt = (ey0 + ey1) / 2 - 6.0
for sx, y in ((1, uy), (-1, uy_alt)):
    a, b = P(sx * xo, y - 9); c, d = P(sx * xo, y + 9)
    out.append(f'<line x1="{a + sx * 4:.1f}" y1="{b:.1f}" x2="{c + sx * 4:.1f}" y2="{d:.1f}" stroke="#b3261e" stroke-width="4"/>')
text(xo + 2, uy + 16, "18 mm diamond in the wall", 12, "end", "#b3261e")
for i, t in enumerate(("18 mm diamond for the", "alternative layout: ESP32", "turned 180 deg, USB here")):
    text(-xo - 2, uy_alt - 1.5 + i * 2.2, t, 12, "start", "#b3261e")

# --- TMC2209: front right, near the cable entry --------------------------------------------------
tx0, tx1 = -PB[0] / 2 + 12.5, -PB[0] / 2 + 12.5 + TMC[0]   # 12 V terminal and capacitor to its right
ty0 = ey1 + 1
ty1 = ty0 + TMC[1]
rect(tx0, ty0, tx1, ty1, "#222222", "#000", 2, rx=2)
rect((tx0 + tx1) / 2 - 7.5, (ty0 + ty1) / 2 - 7.25, (tx0 + tx1) / 2 + 7.5, (ty0 + ty1) / 2 + 7.25, "#2f5fd0", "#1b3a8a", 1, op=0.6)
for e in (ty0 + 1.3, ty1 - 1.3):
    for i in range(8):
        cx, cy = P(tx1 - 1.6 - i * PITCH, e)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.4" fill="#f4d35e"/>')
cx, cy = P((tx0 + tx1) / 2, (ty0 + ty1) / 2)
ctext(cx, cy + 5, "TMC2209", 14, "#ffffff", "bold")

# --- other items ---------------------------------------------------------------------------------
def block(x0, y0, w, h, label, fill="#7a9e7e"):
    rect(x0, y0, x0 + w, y0 + h, fill, "#333", 1.2, rx=2)
    cx, cy = P(x0 + w / 2, y0 + h / 2)
    ctext(cx, cy + 4, label, 11, "#ffffff", "bold")

block(-PB[0] / 2 + 1, ty0, 10.2, 7.6, "12 V")                                  # screw terminal, 2 x 5.08, by the cable entry
block(-PB[0] / 2 + 1, ty0 + 8.4, 10.2, 6, "100uF", "#8a6d9e")                # TMC VM capacitor
block(tx1 + 3, ty0 + 0.5, 10.2, 2.6, "FAN 0", "#c25e00")
block(tx1 + 3, ty0 + 5, 10.2, 2.6, "FAN 1", "#c25e00")
block(tx1 + 3, ty0 + 9.5, 10.2, 2.6, "MOTOR", "#6a3fb5")
block(tx1 + 16, ty0 + 0.5, 10.2, 2.6, "SCD40", "#1b7f3b")
block(tx1 + 16, ty0 + 5, 20, 7, "resistors", "#9e8a6a")

# --- perfboard size: this one (70 x 50) and the largest that fits ----------------------------------
C_DIM, C_MAX = "#b3261e", "#1f7a3a"
MAX_X = 74.0                           # inside width 75.2, 0.6 clear each side
MAX_Y = (PILLAR[1] + 4 + 0.5, Y1 - T - 0.5)   # from just in front of the back pillars to the front wall: 63
rect(-MAX_X / 2, MAX_Y[0], MAX_X / 2, MAX_Y[1], "none", C_MAX, 2)
out[-1] = out[-1].replace("/>", ' stroke-dasharray="10,6"/>')


def arrowhead(x, y, dx, dy, color):
    out.append(f'<polygon points="{x:.1f},{y:.1f} {x - dx * 10 - dy * 4:.1f},{y - dy * 10 + dx * 4:.1f} '
               f'{x - dx * 10 + dy * 4:.1f},{y - dy * 10 - dx * 4:.1f}" fill="{color}"/>')


def hdim(xa, xb, ext_y, cy, label, color):
    """horizontal dimension between model x = xa and xb, drawn at canvas y = cy, extension lines from model y = ext_y"""
    (a, ey), (b, _) = P(xa, ext_y), P(xb, ext_y)
    for x in (a, b):
        out.append(f'<line x1="{x:.1f}" y1="{ey:.1f}" x2="{x:.1f}" y2="{cy + 6:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="3,3"/>')
    out.append(f'<line x1="{a:.1f}" y1="{cy:.1f}" x2="{b:.1f}" y2="{cy:.1f}" stroke="{color}" stroke-width="1.5"/>')
    arrowhead(min(a, b), cy, -1, 0, color); arrowhead(max(a, b), cy, 1, 0, color)
    ctext((a + b) / 2, cy - 7, label, 14, color, "bold")


def vdim(ya, yb, ext_x, cx, label, color):
    """vertical dimension between model y = ya and yb, drawn at canvas x = cx, extension lines from model x = ext_x"""
    (ex, a), (_, b) = P(ext_x, ya), P(ext_x, yb)
    for y in (a, b):
        out.append(f'<line x1="{ex:.1f}" y1="{y:.1f}" x2="{cx - 6:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="3,3"/>')
    out.append(f'<line x1="{cx:.1f}" y1="{a:.1f}" x2="{cx:.1f}" y2="{b:.1f}" stroke="{color}" stroke-width="1.5"/>')
    arrowhead(cx, a, 0, -1, color); arrowhead(cx, b, 0, 1, color)
    out.append(f'<text x="{cx - 8:.1f}" y="{(a + b) / 2:.1f}" font-size="14" text-anchor="middle" fill="{color}" '
               f'font-weight="bold" transform="rotate(-90 {cx - 8:.1f} {(a + b) / 2:.1f})">{label}</text>')


bx = CY + (Y1 - Y0) * K                # canvas y of the box's front face
hdim(PB[0] / 2, -PB[0] / 2, py1, bx + 85, f"{PB[0]:g}: this perfboard (5 x 7 cm)", C_DIM)
hdim(MAX_X / 2, -MAX_X / 2, MAX_Y[1], bx + 125, f"{MAX_X:g} max", C_MAX)
vdim(py0, py1, PB[0] / 2, 110, f"{PB[1]:g}: this perfboard", C_DIM)
vdim(MAX_Y[0], MAX_Y[1], MAX_X / 2, 60, f"{MAX_Y[1] - MAX_Y[0]:g} max", C_MAX)
text(MAX_X / 2 - 1, MAX_Y[0] + 2.3, "largest board that fits", 12, "start", C_MAX)
# standoffs (6 mm, under the board's corner holes) and their spacing
C_STAND = "#1b5fa8"
for dx in (-1, 1):
    for dy in (-1, 1):
        cx, cy = P(dx * PB_HOLES[0] / 2, PB_Y + dy * PB_HOLES[1] / 2)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{3.0 * K}" fill="none" stroke="{C_STAND}" stroke-width="2" stroke-dasharray="4,3"/>')
hdim(PB_HOLES[0] / 2, -PB_HOLES[0] / 2, PB_Y + PB_HOLES[1] / 2 + 3, bx + 165, f"{PB_HOLES[0]:g}: standoffs (6 mm, M2)", C_STAND)
vdim(PB_Y - PB_HOLES[1] / 2, PB_Y + PB_HOLES[1] / 2, -PB_HOLES[0] / 2 - 3, W - 30, f"{PB_HOLES[1]:g}: standoffs", C_STAND)

# --- labels and dimensions -----------------------------------------------------------------------
ctext(CX, CY - 40, "back wall (window side)", 14, "#444")
ctext(CX, CY + (Y1 - Y0) * K + 50, "front cover (room side)", 14, "#444")
text(xo, Y0 - 2, "left wall", 14, "middle", "#444")
text(-xo, Y0 - 2, "right wall", 14, "middle", "#444")
text(-xo - 2, (CABLE_IN[0] + CABLE_IN[1]) / 2 + 1, "cables in: 12 V, fans, motor", 13, "start", "#b3261e")
text(xo + 2, (CABLE_IN[0] + CABLE_IN[1]) / 2 + 4.5, "(mirror entry, unused)", 13, "end", "#b3261e")
# AS5600 wires come down through the diamond window under the chip (x = 0, y = 43)
cx, cy = P(0, 43)
out.append(f'<polygon points="{cx},{cy - 6.75 * K} {cx + 6.75 * K},{cy} {cx},{cy + 6.75 * K} {cx - 6.75 * K},{cy}" '
           f'fill="none" stroke="#1f5fbf" stroke-width="2" stroke-dasharray="6,4"/>')
ctext(cx, cy + 6.75 * K + 16, "AS5600 wires come down here", 12, "#1f5fbf")

text(0, Y0 - 9, "Electronics box, top view, to scale (mm)", 22, "middle", "#111", "bold")
notes = [
    "Inside: 75.2 x 71.6 mm, 34 mm high under the encoder plate. Perfboard 70 x 50 on 5 mm standoffs, holes 66 x 46 (grid 2.54 mm).",
    "Any board from 70 x 50 up to 74 x 63 (dashed green) fits: set pb_size, pb_holes and pb_y (its centre) in the model to match it.",
    "The ESP32's USB end sits 3 holes (7.6 mm) in from the left wall, clear of the corner standoff; its USB-C cable (5 V adapter) passes",
    "through the diamond opening. Or turn the ESP32 180 deg in the same place, USB end to the right: the right-hand diamond (ebox_elec_alt).",
    "12 V from an external power brick comes in through the right-hand cable entry, with the fan and motor cables.",
    "Join the 12 V brick's GND and the ESP32's GND on the perfboard. The ESP32 lies components up, its 3V3/5V header row toward the window.",
]
for i, n in enumerate(notes):
    out.append(f'<text x="30" y="{H - 148 + i * 22}" font-size="14" fill="#333">{n}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
