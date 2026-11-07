#!/usr/bin/env python3
"""Draw doc/max9814.svg: the MAX9814 microphone module (the small purple board), dimensioned.

Usage: python tools/max9814_svg.py   (run from the window-vent folder)
Top view, capsule side up, header holes on the right (as in the seller's picture); side view from a long edge, capsule
up. Board size, thickness, heights, holes and the capsule are measured; the parts' place on the back is an estimate.
"""
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "max9814.svg")

# measured
BL, BW, BT = 25.6, 14.3, 1.62       # board length (x), width (y), thickness
OVER = 9.0                          # board underside to the capsule's top
BACK = 3.0                          # tallest part on the back, about
CAP_D = 9.70                        # capsule diameter (9.65 to 9.70, depending where it's measured)
CAP_E = 2.10                        # capsule wall to the board's near end
HDR_E = 1.0                         # header hole's edge to the board's far end
MH_LONG, MH_SHORT = 1.5, 1.0        # mounting hole's edge to the long edge, to the short edge
MH_D = 2.30                         # mounting holes' diameter
PIN_D = 1.0                         # header holes: standard for 2.54 mm headers
PITCH = 2.54
PINS = ["GND", "Vdd", "Gain", "Out", "AR"]     # top to bottom, capsule side up, header on the right
# derived
CAP_X, CAP_Y = CAP_E + CAP_D / 2, BW / 2       # capsule's centre (centred across the width)
CAP_H = OVER - BT                   # capsule above the board
HDR_X = BL - HDR_E - PIN_D / 2      # header holes' centres
MH = [(MH_SHORT + MH_D / 2, MH_LONG + MH_D / 2), (MH_SHORT + MH_D / 2, BW - MH_LONG - MH_D / 2)]

K = 24                              # px per mm
OX, OY = 150, 150                   # canvas position of the board's top-left corner
W, H = 1240, 1090
C_DIM, C_EST = "#b3261e", "#7a7a7a"
PCB, PCB_EDGE = "#6a2c8c", "#3e1554"
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
out.append(f'<rect x="{x0}" y="{y0}" width="{BL * K}" height="{BW * K}" rx="6" fill="{PCB}" stroke="{PCB_EDGE}" stroke-width="2"/>')
for mx, my in MH:
    cx, cy = px(mx, my)
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{(MH_D / 2 + 0.4) * K:.1f}" fill="#e8e8e8" stroke="#888" stroke-width="2"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{MH_D / 2 * K:.1f}" fill="#ffffff" stroke="#888"/>')
cx, cy = px(CAP_X, CAP_Y)
out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{CAP_D / 2 * K:.1f}" fill="#c8c8c8" stroke="#666" stroke-width="2"/>')
out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{(CAP_D / 2 - 0.7) * K:.1f}" fill="#2b2b2b" stroke="#555"/>')
text(cx, cy - 4, "capsule", 15, color="#ffffff", weight="bold")
text(cx, cy + 15, "felt up", 12, color="#dddddd")
lx, ly = px(15.2, 2.2)
for i, s in enumerate(["Gain: open 60 dB,", "GND 50 dB, Vdd 40 dB", "Out: 2 Vpp max,", "1.25 V DC"]):
    text(lx, ly + 18 + i * 19, s, 13, "start", color="#f0e6f6")
for i, name in enumerate(PINS):
    hx, hy = px(HDR_X, BW / 2 + (i - 2) * PITCH)
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{0.85 * K:.1f}" fill="#e8e8e8" stroke="#888" stroke-width="2"/>')
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{PIN_D / 2 * K:.1f}" fill="{PCB}"/>')
    text(hx - 0.85 * K - 6, hy + 5, name, 14, "end", color="#ffffff", weight="bold")

hdim(0, BL, OY - 50, 0, f"{BL:.1f}")
vdim(0, BW, OX + BL * K + 95, BL, f"{BW:.1f}")
# as measured: from the board's edges to the holes' and the capsule's edges
hdim(0, CAP_E, OY + BW * K + 40, CAP_Y, f"{CAP_E:.2f}", below=True)
hdim(CAP_E, CAP_E + CAP_D, OY + BW * K + 40, CAP_Y, f"Ø {CAP_D:.2f}", below=True)
top_pin = BW / 2 - 2 * PITCH
hdim(BL - HDR_E, BL, OY - 14, top_pin, f"{HDR_E:.1f}")
vdim(top_pin, top_pin + 4 * PITCH, OX + BL * K + 30, HDR_X + PIN_D / 2 + 0.85, f"4 x {PITCH}")
text(OX + BL * K + 30, OY + BW * K + 26, f"holes Ø {PIN_D:g} (standard)", 13, "start", C_EST, italic=True)
mx, my = MH[0]
vdim(0, MH_LONG, OX - 30, mx - MH_D / 2, f"{MH_LONG:.1f}", left=True)
hdim(0, MH_SHORT, OY - 14, my - MH_D / 2, f"{MH_SHORT:.1f}")
text(OX - 14, OY + MH[1][1] * K + 5, f"holes Ø {MH_D:.2f}", 15, "end", C_DIM)
text(OX + BL * K / 2, OY + BW * K + 100, "Top view, capsule side up", 15, weight="bold")

# --- side view, from a long edge ------------------------------------------------------------------------------------
SX, SY, SK = 330, 830, 24          # left end of the board's underside, scale


def sp(x, z):
    return SX + x * SK, SY - z * SK


def srect(x0_, z0, x1, z1, fill, stroke="#222", dash=None):
    a_, b_ = sp(x0_, z1)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<rect x="{a_:.1f}" y="{b_:.1f}" width="{(x1 - x0_) * SK:.1f}" height="{(z1 - z0) * SK:.1f}" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{d}/>')


srect(0, 0, BL, BT, PCB, PCB_EDGE)
srect(CAP_E, BT, CAP_E + CAP_D, OVER, "#c8c8c8", "#666")
srect(CAP_E + 0.4, OVER - 0.5, CAP_E + CAP_D - 0.4, OVER, "#2b2b2b", "#555")
srect(3.5, -BACK, 21.5, 0, "#f3eef6", C_EST, "5,4")
a_, b_ = sp(12.5, -BACK / 2)
text(a_, b_ + 5, "parts on the back (chip, capsule's pins), up to about 3", 13, color=C_EST, italic=True)


def sdim(z0, z1, x, label, ext_x, left=False, color=C_DIM):
    a_, b_ = sp(x, z0); _, c_ = sp(x, z1); ex_, _ = sp(ext_x, 0)
    d = -6 if left else 6
    line(ex_, b_, a_ + d, b_, color, 1, "3,3"); line(ex_, c_, a_ + d, c_, color, 1, "3,3")
    line(a_, b_, a_, c_, color, 1.5); arrow(a_, b_, 0, 1, color); arrow(a_, c_, 0, -1, color)
    text(a_ - 10 if left else a_ + 10, (b_ + c_) / 2 + 5, label, 15, "end" if left else "start", color,
         italic=(color == C_EST))


sdim(0, BT, BL + 1.2, f"{BT} board", BL)
sdim(0, OVER, -1.5, f"{OVER} overall", CAP_E, left=True)
sdim(BT, OVER, CAP_E + CAP_D + 1.2, f"{CAP_H:.2f}", CAP_E + CAP_D, color=C_EST)
sdim(-BACK, 0, BL + 1.2, f"about {BACK:g}", 21.5)
text(SX + BL * SK / 2, SY + BACK * SK + 40, "Side view, from a long edge", 15, weight="bold")

text(40, 50, "MAX9814 microphone module (AGC amplifier and electret capsule on a 14.3 x 25.6 mm board), mm", 22, "start",
     weight="bold")
notes = ["Measured: board 25.6 x 14.3 x 1.62; 9 from its underside to the capsule's top; parts on the back up to about 3;",
         "capsule 2.10 from the near end; header holes 1.0 and mounting holes (Ø 2.30) 1.0 and 1.5 from the edges (edge to hole edge).",
         "Grey italic values are estimates or derived. Header pins 2.54 apart, centred; their order reads the other way on the back.",
         "Wired here: Vdd and GND to 3V3 and GND, Out to GPIO 21 (joined to GPIO 3), Gain to Vdd (40 dB), AR open."]
for i, n in enumerate(notes):
    text(40, H - 95 + i * 22, n, 14, "start", color="#333")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
