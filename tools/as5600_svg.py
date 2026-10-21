#!/usr/bin/env python3
"""Draw doc/as5600.svg: the AS5600 kit board, dimensioned from measurements.

Usage: python tools/as5600_svg.py   (run from the window-vent folder)
All dimensions in mm, top view with the chip facing the viewer; origin at the board's top-left corner.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "as5600.svg")

# Measurements (kit board, the one sold with the 3.95 x 2 mm magnet)
BW, BH = 23.3, 22.8          # board width, height
HOLE_E, HOLE_D = 3.3, 3.6    # hole centres from the edges, hole diameter
ROW_E = 5.2                  # pin rows from the side edges
PITCH = 2.54
OUT_Y = BH / 2              # the 3-pin row's middle pin (OUT): centred, like the 4-pin row
LEFT = ["VCC", "OUT", "GND"]
RIGHT = ["DIR", "SCL", "SDA", "GPO"]
T_BOARD, T_CHIP = 1.6, 3.22  # board thickness, board + chip
MAG_D, MAG_H, MAG_GAP = 3.95, 2.0, 1.0   # the kit's diametric magnet (measured), and its gap over the chip (1 mm shim)

K = 20                       # px per mm
OX, OY = 170, 175            # board origin on the canvas
W, H = 900, 1100
C_DIM = "#b3261e"
C_BLUE = "#1f5fbf"

out = []


def px(x, y):
    return OX + x * K, OY + y * K


def text(x, y, s, size=15, anchor="middle", color="#111", weight="normal", rotate=None):
    tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}"{tr}>{s}</text>')


def line(x1, y1, x2, y2, color="#111", width=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d}/>')


def arrow(x, y, dx, dy, color):
    # small filled arrowhead at (x, y) pointing along (dx, dy)
    import math
    n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
    a, b = 10, 4
    p1 = (x - ux * a - uy * b, y - uy * a + ux * b)
    p2 = (x - ux * a + uy * b, y - uy * a - ux * b)
    out.append(f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def hdim(x1, x2, y, ext_from, label, color=C_DIM):
    """Horizontal dimension between board x1 and x2 (mm), drawn at canvas height y, extension lines from ext_from (mm)."""
    (a, _), (b, _) = px(x1, 0), px(x2, 0)
    ey = OY + ext_from * K
    line(a, ey, a, y + (6 if y > ey else -6), color, 1, "3,3")
    line(b, ey, b, y + (6 if y > ey else -6), color, 1, "3,3")
    line(a, y, b, y, color, 1.5)
    arrow(a, y, -1, 0, color); arrow(b, y, 1, 0, color)
    text((a + b) / 2, y - 7, label, 15, color=color)


def vdim(y1, y2, x, ext_from, label, color=C_DIM):
    """Vertical dimension between board y1 and y2 (mm), drawn at canvas x, extension lines from ext_from (mm)."""
    (_, a), (_, b) = px(0, y1), px(0, y2)
    ex = OX + ext_from * K
    line(ex, a, x + (6 if x > ex else -6), a, color, 1, "3,3")
    line(ex, b, x + (6 if x > ex else -6), b, color, 1, "3,3")
    line(x, a, x, b, color, 1.5)
    arrow(x, a, 0, -1, color); arrow(x, b, 0, 1, color)
    text(x - 8, (a + b) / 2, label, 15, color=color, rotate=-90)


# --- board, top view -------------------------------------------------------------------------
x0, y0 = px(0, 0)
out.append(f'<rect x="{x0}" y="{y0}" width="{BW * K}" height="{BH * K}" rx="{1.2 * K}" fill="#f2f2ee" stroke="#222" stroke-width="2"/>')
holes = [(HOLE_E, HOLE_E), (BW - HOLE_E, HOLE_E), (HOLE_E, BH - HOLE_E), (BW - HOLE_E, BH - HOLE_E)]
for hx, hy in holes:
    cx, cy = px(hx, hy)
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{HOLE_D / 2 * K}" fill="#ffffff" stroke="#222" stroke-width="2"/>')
    line(cx - 8, cy, cx + 8, cy, "#888", 1); line(cx, cy - 8, cx, cy + 8, "#888", 1)

# chip (SOIC-8, leads left and right), centred on the board
cw, ch = 3.9, 4.9
cx, cy = px(BW / 2 - cw / 2, BH / 2 - ch / 2)
out.append(f'<rect x="{cx}" y="{cy}" width="{cw * K}" height="{ch * K}" rx="3" fill="#2b2b2b"/>')
for i in range(4):
    ly = BH / 2 - 1.905 + i * 1.27
    for side in (-1, 1):
        lx = BW / 2 + side * (cw / 2 + 0.5)
        a, b = px(lx - 0.5, ly - 0.2)
        out.append(f'<rect x="{a}" y="{b}" width="{1.0 * K}" height="{0.4 * K}" fill="#9a9a9a"/>')
text(*px(BW / 2, BH / 2 + 0.3), "AS5600", 13, color="#ffffff", weight="bold")


def pins(xmm, ys, labels, anchor_side):
    for y, lab in zip(ys, labels):
        cx, cy = px(xmm, y)
        out.append(f'<rect x="{cx - 0.8 * K}" y="{cy - 0.8 * K}" width="{1.6 * K}" height="{1.6 * K}" fill="none" stroke="#b07a00" stroke-width="2"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{0.5 * K}" fill="#ffffff" stroke="#b07a00" stroke-width="2"/>')
        if anchor_side < 0:
            text(cx - 0.95 * K, cy + 5, lab, 14, "end", weight="bold")
        else:
            text(cx + 0.95 * K, cy + 5, lab, 14, "start", weight="bold")


left_y = [OUT_Y + (i - 1) * PITCH for i in range(3)]
right_y = [BH / 2 + (i - 1.5) * PITCH for i in range(4)]
pins(ROW_E, left_y, LEFT, -1)
pins(BW - ROW_E, right_y, RIGHT, +1)

# --- dimensions ------------------------------------------------------------------------------
top = OY - 30
hdim(0, BW, top - 60, 0, f"{BW}")
hdim(0, HOLE_E, top - 20, 0, f"{HOLE_E}")
hdim(BW - ROW_E, BW, top - 20, right_y[0] - 0.8, f"{ROW_E}")
bot = OY + BH * K + 30
hdim(0, ROW_E, bot + 20, left_y[-1] + 0.8, f"{ROW_E}")
hdim(HOLE_E, BW - HOLE_E, bot + 60, BH - HOLE_E, f"{BW - 2 * HOLE_E:.1f} (hole centres)")
lx = OX - 30
vdim(0, OUT_Y, lx - 20, 0, f"{OUT_Y:.1f} (OUT)")
vdim(0, HOLE_E, lx - 60, 0, f"{HOLE_E}")
rx = OX + BW * K + 110
vdim(0, BH, rx + 50, BW, f"{BH}")
vdim(HOLE_E, BH - HOLE_E, rx + 10, BW - HOLE_E, f"{BH - 2 * HOLE_E:.1f} (hole centres)")

# hole diameter callout
hx, hy = px(HOLE_E, BH - HOLE_E)
line(hx + 0.9 * K, hy + 0.9 * K, hx + 3.2 * K, hy + 3.6 * K, C_DIM, 1.2)
text(hx + 3.3 * K, hy + 3.6 * K + 16, f"&#216; {HOLE_D} (M3)", 15, "start", color=C_DIM)
# pin pitch callout
px1, py1 = px(BW - ROW_E, right_y[2])
text(px1 - 1.2 * K, py1 + 0.9 * K + 18, f"pitch {PITCH}", 13, "end", color=C_DIM)

# --- side view ------------------------------------------------------------------------------
sy = OY + BH * K + 270
sx = OX
out.append(f'<rect x="{sx}" y="{sy + (T_CHIP - T_BOARD) * K}" width="{BW * K}" height="{T_BOARD * K}" fill="#f2f2ee" stroke="#222" stroke-width="2"/>')
cx0 = sx + (BW / 2 - cw / 2) * K
out.append(f'<rect x="{cx0}" y="{sy}" width="{cw * K}" height="{(T_CHIP - T_BOARD) * K}" fill="#2b2b2b"/>')
# thickness dims, on the right
bx = sx + BW * K
for (ya, yb, lab, xo) in [(sy + (T_CHIP - T_BOARD) * K, sy + T_CHIP * K, f"{T_BOARD}", 40),
                          (sy, sy + T_CHIP * K, f"{T_CHIP} over the chip", 110)]:
    line(bx + 6, ya, bx + xo + 6, ya, C_DIM, 1, "3,3"); line(bx + 6, yb, bx + xo + 6, yb, C_DIM, 1, "3,3")
    line(bx + xo, ya, bx + xo, yb, C_DIM, 1.5)
    arrow(bx + xo, ya, 0, -1, C_DIM); arrow(bx + xo, yb, 0, 1, C_DIM)
    text(bx + xo + 8, (ya + yb) / 2 + 5, lab, 15, "start", color=C_DIM)
line(cx0 + cw * K, sy, bx + 116, sy, C_DIM, 1, "3,3")
text(sx, sy - (MAG_GAP + MAG_H) * K - 50, "Side view, with the magnet over the chip", 15, "start", weight="bold")

# the magnet, centred over the chip at its working gap; diametric: N and S side by side, across the diameter
mx0 = sx + (BW / 2 - MAG_D / 2) * K
my0 = sy - (MAG_GAP + MAG_H) * K
mw, mh = MAG_D * K, MAG_H * K
out.append(f'<rect x="{mx0:.1f}" y="{my0:.1f}" width="{mw / 2:.1f}" height="{mh:.1f}" fill="#d64541" stroke="#222" stroke-width="1.5"/>')
out.append(f'<rect x="{mx0 + mw / 2:.1f}" y="{my0:.1f}" width="{mw / 2:.1f}" height="{mh:.1f}" fill="#3b6fb6" stroke="#222" stroke-width="1.5"/>')
text(mx0 + mw / 4, my0 + mh / 2 + 6, "N", 15, color="#ffffff", weight="bold")
text(mx0 + 3 * mw / 4, my0 + mh / 2 + 6, "S", 15, color="#ffffff", weight="bold")
# its diameter, above it
ya = my0 - 22
line(mx0, my0 - 4, mx0, ya - 6, C_DIM, 1, "3,3"); line(mx0 + mw, my0 - 4, mx0 + mw, ya - 6, C_DIM, 1, "3,3")
line(mx0 - 40, ya, mx0, ya, C_DIM, 1.5); arrow(mx0, ya, 1, 0, C_DIM)         # arrows from outside: too narrow inside
line(mx0 + mw, ya, mx0 + mw + 40, ya, C_DIM, 1.5); arrow(mx0 + mw, ya, -1, 0, C_DIM)
text(mx0 + mw + 46, ya + 5, f"&#216; {MAG_D} magnet, diametric (N and S across the diameter)", 15, "start", color=C_DIM)
# its thickness and the gap, on the left
for (y1, y2, lab, xo) in [(my0, my0 + mh, f"{MAG_H:g} thick", 30), (my0 + mh, sy, f"{MAG_GAP:g} gap (shim)", 30)]:
    xl = mx0 - xo
    line(mx0 - 4, y1, xl - 6, y1, C_DIM, 1, "3,3"); line(mx0 - 4, y2, xl - 6, y2, C_DIM, 1, "3,3")
    line(xl, y1, xl, y2, C_DIM, 1.5)
    arrow(xl, y1, 0, -1, C_DIM); arrow(xl, y2, 0, 1, C_DIM)
    text(xl - 8, (y1 + y2) / 2 + 5, lab, 15, "end", color=C_DIM)
line(mx0 - 4, sy, cx0, sy, C_DIM, 1, "3,3")

text(40, 40, "AS5600 kit board: top view, chip side (mm)", 22, "start", weight="bold")
text(40, H - 54, "Measured on the kit board sold with the 3.95 &#215; 2 mm diametric magnet. "
     "Holes form a 16.7 &#215; 16.2 rectangle, not a square.", 14, "start", color="#333")
text(40, H - 30, "The magnet's poles must lie across the shaft (diametric): an ordinary axial magnet, poles on its flat faces, "
     "would not work lying flat.", 14, "start", color="#333")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
