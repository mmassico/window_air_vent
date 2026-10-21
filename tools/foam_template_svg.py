#!/usr/bin/env python3
"""Draw doc/foam_template.svg and doc/foam_template.pdf: a full-size drilling template for the foam insert.

Usage: python tools/foam_template_svg.py   (run from the window-vent folder)
US Letter page, drawn in millimetres, everything inside 205 x 270 mm so it also prints on A4. Print at 100 % and check
the two 100 mm bars. The PDF and the README preview (images/foam_template.png, needs Pillow) are made by headless Chrome.

Spacing follows cad/window_vent.scad (pitch, stop_od); the hole is the saw size, sp_od a bit more; keep them in step.
"""
import os, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "foam_template.svg")
PDF = os.path.join(ROOT, "doc", "foam_template.pdf")
PNG = os.path.join(ROOT, "images", "foam_template.png")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

HOLE = 83.0                  # foam hole: 3-1/4 in (83 mm) hole saw; the spigots (sp_od 83.4) fit it snugly
PITCH = 96.0                 # pitch: duct centres, vertically
STOP = 90.0                  # stop_od: the stop ring resting on the room face
GAP = 100.0                  # largest window gap the insert fills
PROBE = 6.5                  # hole for a 6 mm waterproof DS18B20 probe
PAGE = (215.9, 279.4)        # US Letter, mm
CX, CY = PAGE[0] / 2, 152.0  # centre between the two holes
C_CUT, C_DIM, C_TXT, C_OPT = "#111111", "#b3261e", "#333333", "#0b7a75"

out = []


def text(x, y, s, size=3.5, anchor="middle", color=C_TXT, weight="normal", rotate=None):
    tr = f' transform="rotate({rotate} {x:.2f} {y:.2f})"' if rotate is not None else ""
    out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}"{tr}>{s}</text>')


def line(x1, y1, x2, y2, color=C_DIM, width=0.25, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"{d}/>')


def circle(x, y, d, color=C_CUT, width=0.4, dash=None, fill="none"):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{d / 2:.2f}" fill="{fill}" stroke="{color}" stroke-width="{width}"{ds}/>')


def cross(x, y, size=6, color=C_CUT):
    line(x - size, y, x + size, y, color, 0.3); line(x, y - size, x, y + size, color, 0.3)
    circle(x, y, 1.2, color, 0.3)


def arrow(x, y, dx, dy, color=C_DIM):
    a, b = 2.2, 0.8
    out.append(f'<polygon points="{x:.2f},{y:.2f} {x - dx * a - dy * b:.2f},{y - dy * a + dx * b:.2f} '
               f'{x - dx * a + dy * b:.2f},{y - dy * a - dx * b:.2f}" fill="{color}"/>')


# --- title and instructions ---------------------------------------------------------------------------
text(12, 15, "Foam insert: drilling template, full size (mm)", 6, "start", weight="bold")
for i, s in enumerate([
        "Print at 100 % (Actual size, not Fit to page); both bars must measure 100 mm.",
        "Tape it on the foam, centred across the insert's width, INTAKE on top (it works from either face).",
        "Mark each centre with an awl and drill a pilot hole right through.",
        "Cut with a 3-1/4 in (83 mm) hole saw, halfway from each face, centred on the pilot hole."]):
    text(12, 23 + i * 5, s, 3.4, "start")

# --- guides: centre line, the largest gap ----------------------------------------------------------------
y_top, y_bot = CY - PITCH / 2 - STOP / 2 - 15, CY + PITCH / 2 + STOP / 2 + 4
line(CX, y_top, CX, y_bot, "#777", 0.25, "6,2,1,2")
for sx in (-1, 1):
    line(CX + sx * GAP / 2, y_top + 2, CX + sx * GAP / 2, y_bot, "#777", 0.3, "3,2")
text(CX + GAP / 2 + 1.5, y_bot - 2, f"{GAP:g} max", 2.8, "start", "#555")
text(CX - GAP / 2 - 1.5, y_bot - 2, "insert width", 2.8, "end", "#555")

# --- the two holes -----------------------------------------------------------------------------------
for dy, name, flow in ((-1, "INTAKE", "top: outdoor air in"), (1, "EXHAUST", "bottom: room air out")):
    y = CY + dy * PITCH / 2
    circle(CX, y, STOP, "#888", 0.3, "1.5,1.5")          # the stop ring's footprint on the room face
    circle(CX, y, HOLE, C_CUT, 0.5)
    cross(CX, y)
    text(CX, y - 12, name, 6, weight="bold", color="#bbbbbb")
    text(CX, y + 16, f"Ø {HOLE:g} hole", 3.6, color=C_TXT, weight="bold")
    text(CX, y + 21, flow, 3, color="#666")
text(CX + GAP / 2 + 1.5, CY + PITCH / 2 + STOP / 2 * 0.71 + 4, "dashed circle: stop ring Ø 90", 2.8, "start", "#777")
text(CX + GAP / 2 + 1.5, CY + PITCH / 2 + STOP / 2 * 0.71 + 7.5, "(the housing on the room face)", 2.8, "start", "#777")

# 96 between the centres
x_d = CX + GAP / 2 + 12
for dy in (-1, 1):
    line(CX + 8, CY + dy * PITCH / 2, x_d + 2, CY + dy * PITCH / 2, C_DIM, 0.25, "1,1")
line(x_d, CY - PITCH / 2, x_d, CY + PITCH / 2, C_DIM, 0.35)
arrow(x_d, CY - PITCH / 2, 0, -1); arrow(x_d, CY + PITCH / 2, 0, 1)
text(x_d + 2, CY + 1.2, f"{PITCH:g} between centres", 3.4, "start", C_DIM, "bold")

# --- optional probe hole, above the intake ------------------------------------------------------------
yp = CY - PITCH / 2 - STOP / 2 - 9
circle(CX, yp, PROBE, C_OPT, 0.4, "1,0.8")
cross(CX, yp, 4.5, C_OPT)
text(CX + 6, yp - 1.6, "Optional: outdoor DS18B20", 3.0, "start", C_OPT, "bold")   # kept inside the width guides
text(CX + 6, yp + 2.2, f"probe, Ø {PROBE:g} hole", 3.0, "start", C_OPT, "bold")
text(CX + 6, yp + 5.8, "keep it in the shade", 2.7, "start", C_OPT)

# --- scale check bars ---------------------------------------------------------------------------------
y0 = 262                                                   # horizontal bar
x0 = CX - 50
out.append(f'<rect x="{x0:.2f}" y="{y0}" width="100" height="2.5" fill="#111"/>')
for i in range(11):
    line(x0 + i * 10, y0 - (3 if i % 5 == 0 else 1.5), x0 + i * 10, y0, C_CUT, 0.3)
text(CX, y0 + 7, "100 mm", 3.4, "middle", C_CUT, "bold")
xb, yb0 = 12, CY - 50                                      # vertical bar, left margin
out.append(f'<rect x="{xb}" y="{yb0:.2f}" width="2.5" height="100" fill="#111"/>')
for i in range(11):
    line(xb + 2.5, yb0 + i * 10, xb + 2.5 + (3 if i % 5 == 0 else 1.5), yb0 + i * 10, C_CUT, 0.3)
text(xb + 9, CY + 1.2, "100 mm", 3.4, "start", C_CUT, "bold")
text(PAGE[0] - 12, 274, "tools/foam_template_svg.py (hole 83, pitch 96, stop_od 90)", 2.6, "end", "#777")

W, H = PAGE
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)

# --- PDF and preview, through headless Chrome ---------------------------------------------------------
if os.path.exists(CHROME):
    tmp = tempfile.mkdtemp(prefix="wv_foam_")
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
