#!/usr/bin/env python3
"""Draw doc/lip_templates.svg and doc/lip_templates.pdf: full-size cutting templates for the foam on the damper lips.

Usage: python tools/lip_templates_svg.py   (run from the window-vent folder)
The page is US Letter, drawn in millimetres, with everything inside 205 x 270 mm so it also prints on A4. Print it at
100 % ("Actual size", not "Fit to page") and check the 100 mm and 50 mm bars with a ruler. The PDF and the README
preview (images/lip_templates.png, needs Pillow) are made by headless Chrome when it is installed.

Lip A is flat: a half-ring. Lip B is a 45 deg cone: its template is the cone unrolled (radii x sqrt 2, angles / sqrt 2).
Both stop lip_gap from the shaft axis. Values follow the defaults in cad/window_vent.scad; keep them in step.
"""
import math, os, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "lip_templates.svg")
PDF = os.path.join(ROOT, "doc", "lip_templates.pdf")
PNG = os.path.join(ROOT, "images", "lip_templates.png")   # small preview for the README
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

R_OUT = 37.0                 # bore radius (duct_id / 2): the lips' outer edge
LIP_W = 5.6                  # lip width, (duct_id - disc_d) / 2 + lip_ovl
R_IN = R_OUT - LIP_W         # 31.4
GAP = 7.0                    # lip_gap: no lip within this distance of the shaft axis
PAGE = (215.9, 279.4)        # US Letter, mm
C_CUT, C_DIM, C_TXT = "#111111", "#b3261e", "#333333"

out = []


def text(x, y, s, size=3.5, anchor="start", color=C_TXT, weight="normal"):
    out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}">{s}</text>')


def line(x1, y1, x2, y2, color=C_DIM, width=0.25, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"{d}/>')


def cross(x, y, label):
    line(x - 2.5, y, x + 2.5, y); line(x, y - 2.5, x, y + 2.5)
    text(x + 1.5, y + 4.5, label, 2.6, color=C_DIM)


def shape(pts):
    p = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
    out.append(f'<polygon points="{p}" fill="#f1e3c4" stroke="{C_CUT}" stroke-width="0.3"/>')


def lip_a(cx, cy, n=120):
    """flat half-ring around the axis (cx, cy), the part farther than GAP from the shaft, which runs vertically"""
    a_out, a_in = math.acos(GAP / R_OUT), math.acos(GAP / R_IN)
    pts = [(cx + R_OUT * math.cos(t), cy - R_OUT * math.sin(t))
           for t in (-a_out + 2 * a_out * i / n for i in range(n + 1))]
    pts += [(cx + R_IN * math.cos(t), cy - R_IN * math.sin(t))
            for t in (a_in - 2 * a_in * i / n for i in range(n + 1))]
    shape(pts)


def lip_b(ax, ay, n=120):
    """the conical lip unrolled about its apex (ax, ay), bisector pointing up: a point at radius rho and angle t from
    the lip's middle lies at slant distance rho * sqrt 2, angle t / sqrt 2; the ends follow rho * cos t = GAP"""
    k = math.sqrt(2)

    def p(rho, t):
        s, f = rho * k, t / k
        return ax + s * math.sin(f), ay - s * math.cos(f)

    a_out, a_in = math.acos(GAP / R_OUT), math.acos(GAP / R_IN)
    pts = [p(R_OUT, -a_out + 2 * a_out * i / n) for i in range(n + 1)]
    pts += [p(rho, math.acos(GAP / rho)) for rho in (R_OUT - LIP_W * i / 40 for i in range(1, 40))]
    pts += [p(R_IN, a_in - 2 * a_in * i / n) for i in range(n + 1)]
    pts += [p(rho, -math.acos(GAP / rho)) for rho in (R_IN + LIP_W * i / 40 for i in range(1, 40))]
    shape(pts)


# --- title and instructions ---------------------------------------------------------------------------
text(12, 17, "Damper lip foam: cutting templates, full size (mm)", 6, weight="bold")
for i, s in enumerate([
        "Print at 100 % (Actual size, not Fit to page); the bars at the bottom must measure 100 and 50 mm.",
        "Foam: closed-cell neoprene sheet, 1/16 in (1.6 mm), self-adhesive. Cut 2 of each lip, one per duct.",
        "Both shapes are symmetrical, so they can be traced on the backing paper. Cut on the solid outline.",
        "Straight-ish ends: toward the shaft. Long outer arc: against the bore wall."]):
    text(12, 25 + i * 5, s, 3.4)

# --- lip A: two flat half-rings -----------------------------------------------------------------------
cy = 98
for cx in (12, 56):
    lip_a(cx, cy)
    cross(cx, cy, "shaft axis")
text(12 + GAP + 2, cy + R_OUT + 8, "Lip A (flat): cut 2", 3.8, weight="bold")
text(12 + GAP + 2, cy + R_OUT + 13, f"R {R_IN:g} to R {R_OUT:g}, ends {GAP:g} from the shaft axis", 3, color=C_DIM)

# --- lip B: two unrolled cones ------------------------------------------------------------------------
k = math.sqrt(2)
bx = 150
for ay in (128, 166):
    lip_b(bx, ay)
cross(bx, 166, "apex of the unrolled cone")
line(bx, 166, bx, 166 - R_OUT * k, dash="1,1")
text(bx - 44, 178, "Lip B (45° cone, unrolled): cut 2", 3.8, weight="bold")
text(bx - 44, 183, f"R {R_IN * k:.2f} to R {R_OUT * k:.2f} about the apex (= {R_IN:g} and {R_OUT:g} x 1.414)", 3, color=C_DIM)
text(bx - 44, 188, "Short arc: inner edge of the cone. Long arc: against the bore wall.", 3, color=C_DIM)

# --- scale check bars -----------------------------------------------------------------------------------
x0, y0 = 24, 232                       # horizontal bar from x0, vertical bar at the left margin, both ending at y0
out.append(f'<rect x="{x0}" y="{y0}" width="100" height="3" fill="#111"/>')
for i in range(11):
    line(x0 + i * 10, y0 - (3 if i % 5 == 0 else 1.5), x0 + i * 10, y0, C_CUT, 0.3)
text(x0 + 50, y0 + 8, "100 mm", 3.4, "middle", C_CUT, "bold")
out.append(f'<rect x="12" y="{y0 + 3 - 50}" width="3" height="50" fill="#111"/>')
for i in range(6):
    line(15, y0 + 3 - i * 10, 15 + (3 if i % 5 == 0 else 1.5), y0 + 3 - i * 10, C_CUT, 0.3)
text(19, y0 - 22, "50 mm", 3.4, "start", C_CUT, "bold")
text(12, 255, "If a bar is off, the printer scaled the page: reprint at 100 % (in some PDF viewers: Page Sizing, Actual size).", 3.2)
text(12, 261, "Generated by tools/lip_templates_svg.py from the window_vent.scad defaults (duct 74, lip width 5.6, gap 7).", 2.8)

W, H = PAGE
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)

# --- PDF, through headless Chrome ---------------------------------------------------------------------
if os.path.exists(CHROME):
    tmp = tempfile.mkdtemp(prefix="wv_lips_")
    html = os.path.join(tmp, "page.html")
    with open(html, "w", encoding="utf-8") as fh:
        fh.write(f'<!doctype html><html><head><meta charset="utf-8"><style>@page {{ size: {W}mm {H}mm; margin: 0 }} '
                 f'html, body {{ margin: 0 }} img {{ display: block; width: {W}mm; height: {H}mm }}</style></head>'
                 f'<body><img src="file:///{OUT.replace(os.sep, "/")}"></body></html>')
    subprocess.run([CHROME, "--headless=new", f"--user-data-dir={os.path.join(tmp, 'prof')}", "--no-pdf-header-footer",
                    f"--print-to-pdf={PDF}", "file:///" + html.replace(os.sep, "/")], capture_output=True)
    print("wrote", PDF if os.path.exists(PDF) else "(no PDF: Chrome failed)")
    shot = os.path.join(tmp, "page.png")                 # preview: the whole page at 96 dpi, scaled down
    subprocess.run([CHROME, "--headless=new", f"--user-data-dir={os.path.join(tmp, 'prof')}", "--hide-scrollbars",
                    f"--window-size={round(W / 25.4 * 96)},{round(H / 25.4 * 96)}", f"--screenshot={shot}",
                    "file:///" + OUT.replace(os.sep, "/")], capture_output=True)
    from PIL import Image, ImageOps
    im = Image.open(shot).convert("RGB")
    im = ImageOps.expand(im.resize((400, round(400 * im.height / im.width)), Image.LANCZOS), 1, "#999999")
    im.save(PNG, optimize=True)
    print("wrote", PNG)
else:
    print("Chrome not found: no PDF (print the SVG from a browser at 100 %)")
