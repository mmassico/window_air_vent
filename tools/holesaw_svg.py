#!/usr/bin/env python3
"""Draw doc/holesaw_83.svg: the 3-1/4 in (83 mm) bi-metal hole saw, and how it cuts the 51 mm foam from both faces.

Usage: python tools/holesaw_svg.py   (run from the window-vent folder)
Listed values: 83 mm cut, 32 mm cutting depth, 98 mm arbor with its pilot drill, 68 mm pilot drill. Values marked
"about" are read from the product photos or typical for this size: measure them on the saw.
"""
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "holesaw_83.svg")

CUT_D = 83.0          # listed: hole diameter (3-1/4 in)
TEETH_D = 83.3        # measured: widest sweep across the teeth (one tooth at 83.57, to bend back in)
BODY_D = 82.6         # measured: the cup body, without the teeth's set
DEPTH = 32.0          # listed: cutting depth
ARBOR = 98.0          # listed: arbor, shank end to the pilot drill's tip
DRILL_L = 68.0        # listed: pilot drill length
FOAM = 51.0           # 2 in XPS
# about (from the photos, or typical): to measure
CUP_H = 38.0          # cup, back plate to tooth tips
LEAD = 15.0           # pilot drill tip ahead of the teeth
DRILL_D = 6.35        # pilot drill (1/4 in)
SHANK_D, SHANK_L = 9.5, 30.0   # 3-flat shank (3/8 in), length

K = 5.2               # px per mm
W, H = 1500, 900
C_DIM, C_EST = "#b3261e", "#7a7a7a"

out = []


def text(x, y, s, size=15, anchor="middle", color="#111", weight="normal", rotate=None, italic=False):
    tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
    st = ' font-style="italic"' if italic else ""
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}"{tr}{st}>{s}</text>')


def line(x1, y1, x2, y2, color=C_DIM, width=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d}/>')


def poly(pts, fill, stroke="#222", sw=1.5):
    out.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
               f'" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def arrow(x, y, dx, dy, color):
    n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
    p1 = (x - ux * 10 - uy * 4, y - uy * 10 + ux * 4)
    p2 = (x - ux * 10 + uy * 4, y - uy * 10 - ux * 4)
    out.append(f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def vdim(ya, yb, x, ex, label, color=C_DIM, right=True):
    s = 6 if x > ex else -6
    line(ex, ya, x + s, ya, color, 1, "3,3"); line(ex, yb, x + s, yb, color, 1, "3,3")
    line(x, ya, x, yb, color, 1.5); arrow(x, min(ya, yb), 0, -1, color); arrow(x, max(ya, yb), 0, 1, color)
    text(x + (10 if right else -10), (ya + yb) / 2 + 5, label, 15, "start" if right else "end", color,
         italic=(color == C_EST))


def hdim(xa, xb, y, ey, label, color=C_DIM, lx=0.5):
    s = -6 if y < ey else 6
    line(xa, ey, xa, y + s, color, 1, "3,3"); line(xb, ey, xb, y + s, color, 1, "3,3")
    line(xa, y, xb, y, color, 1.5); arrow(xa, y, -1, 0, color); arrow(xb, y, 1, 0, color)
    text(xa + (xb - xa) * lx, y - 8, label, 15, color=color, italic=(color == C_EST))


# --- the saw, side view: teeth up, shank down --------------------------------------------------------
AX = 470                                # axis x
Y_TEETH = 270                           # canvas y of the tooth tips
def Y(mm):                              # distance below the tooth tips -> canvas y
    return Y_TEETH + mm * K
cut_r, body_r = TEETH_D / 2 * K, BODY_D / 2 * K
y_back = Y(CUP_H)
d = DRILL_D / 2 * K                                                        # pilot drill, tip ahead of the teeth
poly([(AX - d, y_back), (AX - d, Y(-LEAD) + d), (AX, Y(-LEAD)), (AX + d, Y(-LEAD) + d), (AX + d, y_back)], "#b08a3c")
out.append(f'<rect x="{AX - body_r:.1f}" y="{Y(5):.1f}" width="{2 * body_r:.1f}" height="{y_back - Y(5):.1f}" '
           f'fill="#d8312b" stroke="#222" stroke-width="1.5"/>')           # cup below the tooth gullets
teeth = []                                                                 # tooth row, set alternately out and in
n = 14
for i in range(n + 1):
    x = AX - body_r + 2 * body_r * i / n
    teeth.append((x, Y(5)))
    if i < n:
        xm = x + body_r / n * 0.7
        teeth.append((xm, Y(0)))
poly([(AX - body_r, Y(6))] + teeth + [(AX + body_r, Y(6))], "#d8312b")
for sx in (-1, 1):                                                         # the cut is wider than the body
    line(AX + sx * cut_r, Y(-2), AX + sx * cut_r, Y(DEPTH + 2), C_DIM, 1, "4,3")
for sx in (-1, 1):                                                         # chip slots
    x = AX + sx * body_r * 0.55
    out.append(f'<rect x="{x - 9:.1f}" y="{Y(12):.1f}" width="18" height="{12 * K:.1f}" rx="9" fill="#7a1612"/>')
y_shank_end = Y(-LEAD) + ARBOR * K
out.append(f'<rect x="{AX - 11 * K / 2:.1f}" y="{y_back:.1f}" width="{11 * K:.1f}" height="{14 * K:.1f}" fill="#2b2b2b" stroke="#111"/>')
out.append(f'<rect x="{AX - SHANK_D / 2 * K:.1f}" y="{y_back + 14 * K:.1f}" width="{SHANK_D * K:.1f}" '
           f'height="{y_shank_end - y_back - 14 * K:.1f}" fill="#3a3a3a" stroke="#111"/>')

hdim(AX - cut_r, AX + cut_r, Y(-LEAD) - 40, Y(-2), f"Ø {TEETH_D:g} across the teeth (sold as {CUT_D:g}, 3-1/4 in)")
hdim(AX - body_r, AX + body_r, y_back + 50, y_back, f"body Ø {BODY_D:g}", C_DIM, lx=0.22)
vdim(Y(0), Y(DEPTH), AX + cut_r + 50, AX + cut_r, f"{DEPTH:g} cutting depth")
vdim(Y(-LEAD), y_shank_end, AX - cut_r - 60, AX - d, f"{ARBOR:g} arbor + pilot drill", right=False)
vdim(Y(-LEAD), Y(0), AX + cut_r + 50, AX + d, f"pilot leads about {LEAD:g}", C_EST)
text(AX, Y(-LEAD) - 80, "Hole saw, side view", 17, weight="bold")
text(AX + SHANK_D * K, y_shank_end - 20, f"3-flat shank, about {SHANK_D:g}", 14, "start", C_EST, italic=True)
text(AX + d + 14, Y(-LEAD) + 30, f"pilot drill {DRILL_L:g} long,", 14, "start", "#333")
text(AX + d + 14, Y(-LEAD) + 48, f"about Ø {DRILL_D:g}", 14, "start", C_EST, italic=True)

# --- the foam, cut from both faces --------------------------------------------------------------------
FX, FY = 1000, 560                       # canvas position of the foam's top-left corner
KF = 3.4
STRIP = 100                              # the insert's width (the window gap)
fw = STRIP * KF
out.append(f'<rect x="{FX}" y="{FY}" width="{fw:.1f}" height="{FOAM * KF:.1f}" fill="#f2b8c6" stroke="#222" stroke-width="1.5"/>')
hx0, hx1 = FX + (STRIP - CUT_D) / 2 * KF, FX + (STRIP + CUT_D) / 2 * KF
for x in (hx0, hx1):                     # the two kerfs meet: 32 from the top, 32 from the bottom
    out.append(f'<rect x="{x - 4:.1f}" y="{FY:.1f}" width="8" height="{DEPTH * KF:.1f}" fill="#ffffff" stroke="#b3261e" stroke-width="1.2"/>')
    out.append(f'<rect x="{x - 4:.1f}" y="{FY + (FOAM - DEPTH) * KF:.1f}" width="8" height="{DEPTH * KF:.1f}" '
               f'fill="#ffffff" stroke="#1f5fbf" stroke-width="1.2" fill-opacity="0.6"/>')
line(FX + STRIP / 2 * KF, FY - 20, FX + STRIP / 2 * KF, FY + FOAM * KF + 20, "#777", 1, "10,4,2,4")   # pilot hole axis
text(FX + STRIP / 2 * KF, FY - 28, "pilot hole, right through", 13, color="#555")
vdim(FY, FY + FOAM * KF, FX - 160, FX, f"{FOAM:g} foam", "#111", right=False)
vdim(FY, FY + DEPTH * KF, FX - 40, hx0 - 4, f"{DEPTH:g} from face 1", C_DIM, right=False)
vdim(FY + (FOAM - DEPTH) * KF, FY + FOAM * KF, FX + fw + 20, hx1 + 4, f"{DEPTH:g} from face 2", "#1f5fbf")
yo0, yo1 = FY + (FOAM - DEPTH) * KF, FY + DEPTH * KF
out.append(f'<rect x="{hx0 - 4:.1f}" y="{yo0:.1f}" width="8" height="{yo1 - yo0:.1f}" fill="#6a3fb5" opacity="0.5"/>')
out.append(f'<rect x="{hx1 - 4:.1f}" y="{yo0:.1f}" width="8" height="{yo1 - yo0:.1f}" fill="#6a3fb5" opacity="0.5"/>')
text(hx0 + 12, (yo0 + yo1) / 2 + 5, f"{2 * DEPTH - FOAM:g} overlap", 14, "start", "#6a3fb5", "bold")
text(FX + fw / 2 - 40, FY - 70, "Cutting the 51 mm foam (section)", 17, weight="bold")

text(40, 50, "3-1/4 in (83 mm) bi-metal hole saw (mm)", 22, "start", weight="bold")
notes = [
    f"Listed: Ø {CUT_D:g} cut, {DEPTH:g} cutting depth, {ARBOR:g} arbor with its pilot drill, {DRILL_L:g} pilot drill. "
    f"Measured: Ø {TEETH_D:g} across the teeth, body Ø {BODY_D:g}. Grey italic values are estimates.",
    f"The cut ({DEPTH:g} deep) is shorter than the foam ({FOAM:g}): cut from both faces, on one pilot hole, so the kerfs meet with "
    f"{2 * DEPTH - FOAM:g} mm of overlap.",
    "The pilot drill may not reach through 51 mm: push a skewer or a long nail through the centre mark to find it on the other face.",
    f"The teeth are set alternately in and out, so the hole follows the teeth ({TEETH_D:g}), not the body: cut a test hole and try oring_test in it.",
]
for i, s in enumerate(notes):
    out.append(f'<text x="40" y="{H - 110 + i * 24}" font-size="14" fill="#333">{s}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
