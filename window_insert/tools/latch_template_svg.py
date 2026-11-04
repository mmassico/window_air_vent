#!/usr/bin/env python3
"""Draw doc/latch_template.svg and doc/latch_template.pdf: a full-size template for the latch cover's notch in the foam.

Usage: python tools/latch_template_svg.py   (run from the window_insert folder)
US Letter page, drawn in millimetres, everything inside 205 x 270 mm so it also prints on A4. Print at 100 % and check
the two 100 mm bars. The PDF and the README preview (images/latch_template.png, needs Pillow) are made by headless
Chrome, as for the vent's drilling template.

The notch seen from the room, like the latch cover from above: the outer rectangle is its edge on the room face, the
inner one its floor, 9.5 mm down, joined by the 45 deg slopes. Print two copies: cut one to the outer rectangle, to
trace on the foam's face, and the other to the inner one, to check the floor. The values follow cad/window_caps.scad
(latch, clr, lc_w, base, zb, bot_ribs); keep them in step.
"""
import math
import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "latch_template.svg")
PDF = os.path.join(ROOT, "doc", "latch_template.pdf")
PNG = os.path.join(ROOT, "images", "latch_template.png")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# From cad/window_caps.scad
LATCH = (18.20, 495, 80, 40)  # latch zone: from the foam's centre (u), above the bottom rib, height, across (x)
CLR = 0.3                     # clr
LC_W = 2.0                    # lc_w: the latch cover's wall
BASE = 3.0                    # base: the side frame's face to the foam's end
FOAM_T = 50.8                 # foam_t
ZB = 14.5                     # zb: the foam's bottom edge
RIB_Z = 11.0                  # bot_ribs[0][2]: the bottom rib, where the latch zone's height starts

# The notch: the latch cover's outside, measured from the foam's end (x) and its bottom edge (z)
k = LC_W * (math.sqrt(2) - 1)                       # a 45 deg wall of thickness lc_w moves its corner by this much
DEPTH = FOAM_T / 2 - (LATCH[0] - CLR) + LC_W        # 9.5
IN_X = LATCH[3] + CLR + k - BASE                    # 38.1
IN_Z = (RIB_Z + LATCH[1] - CLR - k - ZB, RIB_Z + LATCH[1] + LATCH[2] + CLR + k - ZB)   # 490.4, 572.6
OUT_X = IN_X + DEPTH                                # 47.6
OUT_Z = (IN_Z[0] - DEPTH, IN_Z[1] + DEPTH)          # 480.9, 582.1

PAGE = (215.9, 279.4)        # US Letter, mm
X0, Y0 = 78.0, 92.0          # the outer rectangle's top-left corner on the page (the foam's end on the left)
C_CUT, C_DIM, C_TXT, C_IN = "#111111", "#b3261e", "#333333", "#0b7a75"

out = []


def text(x, y, s, size=3.5, anchor="middle", color=C_TXT, weight="normal", rotate=None):
    tr = f' transform="rotate({rotate} {x:.2f} {y:.2f})"' if rotate is not None else ""
    out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}"{tr}>{s}</text>')


def line(x1, y1, x2, y2, color=C_DIM, width=0.25, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"{d}/>')


def rect(x, y, w, h, color=C_CUT, width=0.4):
    out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="none" stroke="{color}" '
               f'stroke-width="{width}"/>')


def arrow(x, y, dx, dy, color=C_DIM):
    a, b = 2.2, 0.8
    out.append(f'<polygon points="{x:.2f},{y:.2f} {x - dx * a - dy * b:.2f},{y - dy * a + dx * b:.2f} '
               f'{x - dx * a + dy * b:.2f},{y - dy * a - dx * b:.2f}" fill="{color}"/>')


def dim_h(x1, x2, y, label, color=C_DIM, ext=None):
    """A horizontal dimension from x1 to x2 at y, its extension lines from ext (a y) when given."""
    if ext is not None:
        for x in (x1, x2):
            line(x, ext, x, y + (1.5 if y > ext else -1.5), color, 0.2, "1,1")
    line(x1, y, x2, y, color, 0.3)
    arrow(x1, y, -1, 0, color); arrow(x2, y, 1, 0, color)
    text((x1 + x2) / 2, y - 1.5, label, 3.2, "middle", color, "bold")


def dim_v(y1, y2, x, label, color=C_DIM, ext=None):
    if ext is not None:
        for y in (y1, y2):
            line(ext, y, x + (1.5 if x > ext else -1.5), y, color, 0.2, "1,1")
    line(x, y1, x, y2, color, 0.3)
    arrow(x, y1, 0, -1, color); arrow(x, y2, 0, 1, color)
    text(x + 2, (y1 + y2) / 2 + 1.2, label, 3.2, "start", color, "bold")


# --- title and instructions ---------------------------------------------------------------------------
text(12, 15, "Window insert: latch cover notch template, full size (mm)", 6, "start", weight="bold")
for i, s in enumerate([
        "Print two copies at 100 % (Actual size, not Fit to page); both bars must measure 100 mm.",
        "Copy 1: cut along the OUTER rectangle. Lay it on the foam's room face, its left edge on the foam's end",
        "(the side frame's end), and trace it: that is the top edge of the three 45&#176; slopes.",
        "Copy 2: cut along the INNER rectangle: the notch's floor, 9.5 mm deep. Lay it in the notch to check the floor.",
        "Line both up in height with the notch in the assembled side cap; carve a little small, then sand to the cover."]):
    text(12, 23 + i * 5, s, 3.4, "start")

# --- the notch, seen from the room ---------------------------------------------------------------------
ow, oh = OUT_X, OUT_Z[1] - OUT_Z[0]
iw, ih = IN_X, IN_Z[1] - IN_Z[0]
ix, iy = X0, Y0 + DEPTH                              # the inner rectangle shares the foam's end, 9.5 in from the rest
for (xa, ya), (xb, yb) in (((X0 + ow, Y0), (ix + iw, iy)), ((X0 + ow, Y0 + oh), (ix + iw, iy + ih)),
                           ((X0, Y0), (ix, iy)), ((X0, Y0 + oh), (ix, iy + ih))):
    line(xa, ya, xb, yb, "#888", 0.25)               # the slopes' corners (at the foam's end: the slopes' ends)
rect(X0, Y0, ow, oh, C_CUT, 0.5)
rect(ix, iy, iw, ih, C_IN, 0.5)
line(X0, Y0 - 8, X0, Y0 + oh + 8, C_CUT, 1.0)        # the foam's end, extended past the rectangles
text(X0 - 3, Y0 + oh / 2, "FOAM'S END (side frame)", 4.2, "middle", C_CUT, "bold", rotate=-90)
text(X0 + ow / 2 + 2, Y0 + 5.5, "slope", 2.8, "middle", "#777")
text(X0 + ow / 2 + 2, Y0 + oh - 3.3, "slope", 2.8, "middle", "#777")
text(X0 + ow - 3.3, Y0 + oh / 2, "slope", 2.8, "middle", "#777", rotate=-90)
text(ix + iw / 2, iy + ih / 2 - 3, "FLOOR", 4.2, "middle", C_IN, "bold")
text(ix + iw / 2, iy + ih / 2 + 2.5, f"{DEPTH:.1f} deep", 3.2, "middle", C_IN)
text(ix + iw / 2, iy + ih / 2 + 7, "(inner)", 3.0, "middle", C_IN)
text(X0 + ow / 2, Y0 - 11, "OUTER: on the room face", 3.4, "middle", C_CUT, "bold")

# dimensions: the outer ones above and right, the inner ones below and left of the floor
dim_h(X0, X0 + ow, Y0 - 4, f"{OUT_X:.1f}")
dim_v(Y0, Y0 + oh, X0 + ow + 9, f"{OUT_Z[1] - OUT_Z[0]:.1f}", ext=X0 + ow)
dim_h(ix, ix + iw, iy + ih - 6, f"{IN_X:.1f}", C_IN)   # inside the floor, clear of the slope
dim_v(iy, iy + ih, X0 + ow + 26, f"{IN_Z[1] - IN_Z[0]:.1f}", C_IN, ext=ix + iw)
text(X0 + ow + 4, Y0 + oh + 12, f"slopes: 45&#176;, {DEPTH:.1f} wide on the face and {DEPTH:.1f} deep", 3.0, "start",
     "#555")

# heights on the foam: above its bottom edge, the end the bottom cap holds
xh = 26
text(xh, Y0 - 9, "On the foam, above", 3.0, "start", "#555", "bold")
text(xh, Y0 - 5, "its bottom edge:", 3.0, "start", "#555", "bold")
for y, s, c in ((Y0, f"{OUT_Z[1]:.1f} outer", C_CUT), (iy, f"{IN_Z[1]:.1f} inner", C_IN),
                (iy + ih, f"{IN_Z[0]:.1f} inner", C_IN), (Y0 + oh, f"{OUT_Z[0]:.1f} outer", C_CUT)):
    line(xh + 24, y, X0 - 1.5, y, c, 0.2, "1,1")
    text(xh + 23, y + 1.1, s, 3.0, "end", c, "bold")
text(xh, Y0 + oh + 12, "The foam's bottom edge is", 2.8, "start", "#777")
text(xh, Y0 + oh + 15.5, "below this page: TOP is up.", 2.8, "start", "#777")
arrow(X0 + ow / 2, Y0 - 24, 0, -1, "#555"); line(X0 + ow / 2, Y0 - 24, X0 + ow / 2, Y0 - 18, "#555", 0.4)
text(X0 + ow / 2 + 3, Y0 - 20, "TOP", 3.2, "start", "#555", "bold")

# --- scale check bars ---------------------------------------------------------------------------------
y0 = 262                                                   # horizontal bar
x0 = PAGE[0] / 2 - 50
out.append(f'<rect x="{x0:.2f}" y="{y0}" width="100" height="2.5" fill="#111"/>')
for i in range(11):
    line(x0 + i * 10, y0 - (3 if i % 5 == 0 else 1.5), x0 + i * 10, y0, C_CUT, 0.3)
text(PAGE[0] / 2, y0 + 7, "100 mm", 3.4, "middle", C_CUT, "bold")
xb, yb0 = 12, 148                                          # vertical bar, left margin
out.append(f'<rect x="{xb}" y="{yb0:.2f}" width="2.5" height="100" fill="#111"/>')
for i in range(11):
    line(xb + 2.5, yb0 + i * 10, xb + 2.5 + (3 if i % 5 == 0 else 1.5), yb0 + i * 10, C_CUT, 0.3)
text(xb, yb0 + 106, "100 mm", 3.4, "start", C_CUT, "bold")
text(PAGE[0] - 12, 274, f"tools/latch_template_svg.py (outer {OUT_X:.1f} x {OUT_Z[1] - OUT_Z[0]:.1f}, inner "
     f"{IN_X:.1f} x {IN_Z[1] - IN_Z[0]:.1f}, {DEPTH:.1f} deep)", 2.6, "end", "#777")

W, H = PAGE
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)

# --- PDF and preview, through headless Chrome ---------------------------------------------------------
if os.path.exists(CHROME):
    tmp = tempfile.mkdtemp(prefix="wi_latch_")
    html = os.path.join(tmp, "page.html")
    with open(html, "w", encoding="utf-8") as fh:
        fh.write(f'<!doctype html><html><head><meta charset="utf-8"><style>@page {{ size: {W}mm {H}mm; margin: 0 }} '
                 f'html, body {{ margin: 0 }} img {{ display: block; width: {W}mm; height: {H}mm }}</style></head>'
                 f'<body><img src="file:///{OUT.replace(os.sep, "/")}"></body></html>')
    prof = f"--user-data-dir={os.path.join(tmp, 'prof')}"
    subprocess.run([CHROME, "--headless=new", prof, "--no-pdf-header-footer", f"--print-to-pdf={PDF}",
                    "file:///" + html.replace(os.sep, "/")], capture_output=True)
    print("wrote", PDF if os.path.exists(PDF) else "(no PDF: Chrome failed)")
    shot = os.path.join(tmp, "page.png")
    subprocess.run([CHROME, "--headless=new", prof, "--hide-scrollbars",
                    f"--window-size={round(W / 25.4 * 96)},{round(H / 25.4 * 96)}", f"--screenshot={shot}",
                    "file:///" + OUT.replace(os.sep, "/")], capture_output=True)
    from PIL import Image, ImageOps
    im = Image.open(shot).convert("RGB")
    im = ImageOps.expand(im.resize((400, round(400 * im.height / im.width)), Image.LANCZOS), 1, "#999999")
    im.save(PNG, optimize=True)
    print("wrote", PNG)
else:
    print("Chrome not found: no PDF (print the SVG from a browser at 100 %)")
