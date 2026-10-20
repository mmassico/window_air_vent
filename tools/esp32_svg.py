#!/usr/bin/env python3
"""Draw doc/esp32_s3.svg: the Freenove ESP32-S3-WROOM Lite board (FNK0099), dimensioned from measurements.

Usage: python tools/esp32_svg.py   (run from the window-vent folder)
Top view, components up, USB end at the bottom (as on the silkscreen); dimensions in mm.
"""
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "esp32_s3.svg")

# Measurements
PW, PL = 28.5, 50.0          # PCB width, length
ANT_W, ANT_L = 18.5, 7.0     # module antenna beyond the PCB (5 mm from each side edge)
MOD_L = 25.5                 # ESP32-S3-WROOM-1 module length (datasheet), so 18.5 of it on the PCB
OTG_X, UART_X, USB_W = 4.25, 3.75, 9.0   # USB-C: OTG from the left edge, UART from the right edge, width
PCB_T, SPACER, PIN_BELOW = 1.62, 2.78, 5.54   # side view (measured)
TOP_H, USB_H = 4.85, 3.25  # tallest part above the PCB's underside; USB-C socket height above the PCB
ROW_SPACING = 25.3           # header rows, centre to centre (measured 25.25-25.3: 10 holes on a 2.54 perfboard)
PITCH = 2.54
LEFT = ["3V3", "EN", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46", "9", "10", "11", "12", "13", "14", "5V"]
RIGHT = ["TX", "RX", "1", "2", "42", "41", "40", "39", "38", "37", "36", "35", "0", "45", "48", "47", "21", "20", "19", "GND"]

K = 13                       # px per mm
OX, OY = 300, 260            # canvas position of the PCB's top-left corner
W, H = 1640, 1200
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


# --- PCB, module, antenna --------------------------------------------------------------------------
x0, y0 = px(0, 0)
out.append(f'<rect x="{x0}" y="{y0}" width="{PW * K}" height="{PL * K}" rx="6" fill="#d8453a" stroke="#222" stroke-width="2"/>')
am = (PW - ANT_W) / 2
a, b = px(am, -ANT_L)
out.append(f'<rect x="{a}" y="{b}" width="{ANT_W * K}" height="{MOD_L * K}" rx="3" fill="#2a2a2a" stroke="#111" stroke-width="1.5"/>')
a, b = px(am + 1, MOD_L - ANT_L - 18)
out.append(f'<rect x="{a}" y="{b}" width="{(ANT_W - 2) * K}" height="{17 * K}" rx="3" fill="#c9cbcf" stroke="#888"/>')
text(*px(PW / 2, MOD_L - ANT_L - 9), "ESP32-S3-WROOM-1", 15, color="#333", weight="bold")
text(*px(PW / 2, -ANT_L / 2 + 0.6), "antenna", 14, color="#ffffff")

# USB-C connectors
for x, lab in ((OTG_X, "USB-OTG"), (PW - UART_X - USB_W, "USB-UART")):
    a, b = px(x, PL - 7.5)
    out.append(f'<rect x="{a}" y="{b}" width="{USB_W * K}" height="{7.5 * K}" rx="5" fill="#c0c0c0" stroke="#555" stroke-width="1.5"/>')
    text(*px(x + USB_W / 2, PL + 3.2), lab, 15, weight="bold")

# header pins and labels
r1 = (PW - ROW_SPACING) / 2
first = (PL - 19 * PITCH) / 2
for col, labels, side in ((r1, LEFT, -1), (PW - r1, RIGHT, 1)):
    for i, lab in enumerate(labels):
        cx, cy = px(col, first + i * PITCH)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.75 * K}" fill="#f4d35e" stroke="#7a5c00"/>')
        over_usb = first + i * PITCH > PL - 7.5           # labels over a USB-C connector: dark text
        text(cx - side * 1.2 * K, cy + 5, lab, 12, "end" if side > 0 else "start", "#111" if over_usb else "#ffffff", "bold")

# --- dimensions -------------------------------------------------------------------------------------
top = OY - ANT_L * K
hdim(0, PW, top - 70, 0, f"{PW}")
hdim(0, am, top - 25, 0, f"{am:g}")
hdim(PW - am, PW, top - 25, 0, f"{am:g}")
vdim(-ANT_L, PL, OX - 60, 0, "57")
vdim(0, PL, OX + PW * K + 110, PW, f"{PL:g} (PCB)")
vdim(-ANT_L, 0, OX + PW * K + 60, PW / 2 + ANT_W / 2, f"{ANT_L:g}")
bot = OY + PL * K + 70
hdim(0, OTG_X, bot, PL, f"{OTG_X}")
hdim(OTG_X, OTG_X + USB_W, bot + 40, PL, f"{USB_W:g}")
hdim(PW - UART_X - USB_W, PW - UART_X, bot + 40, PL, f"{USB_W:g}")
hdim(PW - UART_X, PW, bot, PL, f"{UART_X}")
hdim(r1, PW - r1, bot + 90, PL - first, f"{ROW_SPACING} between the pin rows: 10 perfboard holes")

text(40, 50, "Freenove ESP32-S3-WROOM Lite (FNK0099): top view, components up, and side view (mm)", 22, "start", weight="bold")

# --- side view (seen from the USB end), to the right ----------------------------------------------
SX, SY, SK = 960, 640, 16      # left end of the PCB's underside on the canvas, scale
def sp(x, z):                  # side-view mm -> canvas (z up, 0 = PCB underside)
    return SX + x * SK, SY - z * SK
def srect(x0, z0, x1, z1, fill, stroke="#222"):
    a, b = sp(x0, z1)
    out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{(x1 - x0) * SK:.1f}" height="{(z1 - z0) * SK:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
srect(0, 0, PW, PCB_T, "#d8453a")                                             # PCB
for col in (r1, PW - r1):
    srect(col - 1.25, -SPACER, col + 1.25, 0, "#555")                        # plastic spacer
    srect(col - 0.32, -SPACER - PIN_BELOW, col + 0.32, -SPACER, "#f4d35e")  # pin
    srect(col - 0.32, PCB_T, col + 0.32, PCB_T + 1.0, "#f4d35e")           # pin tip above
for x in (OTG_X, PW - UART_X - USB_W):
    srect(x, PCB_T, x + USB_W, PCB_T + USB_H, "#c0c0c0")                     # USB-C sockets
srect(PW / 2 - 3, PCB_T, PW / 2 + 3, TOP_H, "#33c8d8")                       # tallest part
def sdim(z0, z1, x, label, ext_x, left=False):
    a, b = sp(x, z0); _, c = sp(x, z1); ex, _ = sp(ext_x, 0)
    d = -6 if left else 6
    line(ex, b, a + d, b, C_DIM, 1, "3,3"); line(ex, c, a + d, c, C_DIM, 1, "3,3")
    line(a, b, a, c, C_DIM, 1.5); arrow(a, b, 0, 1, C_DIM); arrow(a, c, 0, -1, C_DIM)
    text(a - 10 if left else a + 10, (b + c) / 2 + 5, label, 14, "end" if left else "start", C_DIM)
sdim(0, PCB_T, PW + 4, f"{PCB_T} PCB", PW)
sdim(-SPACER, 0, PW + 4, f"{SPACER} spacer", PW)
sdim(-SPACER - PIN_BELOW, -SPACER, PW + 4, f"{PIN_BELOW} pins", PW)
sdim(0, TOP_H, -4, f"{TOP_H} to the top", PW / 2 - 3, left=True)
text(SX, SY - 8 * SK, "Side view, from the USB end", 15, "start", weight="bold")
notes = ["Measured on the board. 2 x 20 pins, 2.54 pitch; the rows land 10 holes apart on a perfboard (25.4, within 0.1).",
         "Side view: 5.54 pins below a 2.78 spacer, 1.62 PCB; the tallest part is 4.85 above the PCB's underside, the USB-C sockets 3.25 above its top.",
         "In the electronics box, the USB end faces the left wall (or the right one, board turned 180 deg); plug the USB-UART connector (power and console)."]
for i, n in enumerate(notes):
    out.append(f'<text x="40" y="{H - 80 + i * 24}" font-size="14" fill="#333">{n}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
