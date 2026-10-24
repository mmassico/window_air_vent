#!/usr/bin/env python3
"""Draw doc/perfboard.svg and doc/perfboard.pdf: a proposed build plan for the 5 x 7 cm perfboard in the electronics box.

Usage: python tools/perfboard_svg.py   (run from the window-vent folder)
The SVG (for the README) holds everything on one sheet; the PDF has three landscape Letter pages for the bench: the
component side, the solder side and the wire list.
Top panel: the component side, seen from above as in doc/ebox_layout.svg (the window side at the top, the room at the
bottom, the right wall on the right). Bottom panel: the solder side, the board turned over left to right, with the
numbered wires of the table.
Grid: 24 columns, A at the right wall's side, and 18 rows, 18 at the back (the model's pb_col(0) and pb_row(0)), as
printed on the board.
Pins as in firmware/baremetal/Pins.h; connections as in firmware/images/wiring.svg.
"""
import os, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "perfboard.svg")
PDF = os.path.join(ROOT, "doc", "perfboard.pdf")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

NX, NY = 24, 18
PITCH = 2.54
K = 14                              # px per mm
P = PITCH * K                       # px per hole
LET = "ABCDEFGHIJKLMNOPQRSTUVWX"

NET = {"GND": "#222222", "3V3": "#e08a00", "12V": "#d32f2f", "SENSE": "#8e44ad",
       "EN": "#1565c0", "STEP": "#0d47a1", "DIR": "#1e88e5", "TX": "#3949ab", "UART": "#5c6bc0",
       "PWM0": "#00897b", "TACH0": "#26a69a", "PWM1": "#00695c", "TACH1": "#4db6ac",
       "SDA0": "#2e7d32", "SCL0": "#66bb6a", "SDA1": "#558b2f", "SCL1": "#9ccc65",
       "DQo": "#795548", "DQi": "#a1887f", "M1A": "#616161", "M1B": "#757575", "M2A": "#9e9e9e", "M2B": "#bdbdbd"}

# --- placement ----------------------------------------------------------------------------------
# ESP32-S3 (Freenove Lite), soldered: its left header in row 1, its right header in row 11, columns D to W; the USB end
# at column W (toward the left wall), the antenna beyond column D.
ESP_L = ["3V3", "EN", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46", "9", "10", "11", "12", "13", "14", "5V"]
ESP_R = ["TX", "RX", "1", "2", "42", "41", "40", "39", "38", "37", "36", "35", "0", "45", "48", "47", "21", "20", "19", "GND"]
# TMC2209, soldered, heatsink up: signal row 13 (EN in column E ... DIR in L), power row 18 (VM ... GND)
TMC_S = ["EN", "MS1", "MS2", "PDN", "UART", "CLK", "STEP", "DIR"]
TMC_P = ["VM", "GND", "M1B", "M1A", "M2A", "M2B", "VIO", "GND"]

HEADERS = [   # name, title, [(c, r, pin label)]
    ("J2", "FAN 0 (intake)", [(13, 17, "GND"), (14, 17, "12V"), (15, 17, "TACH"), (16, 17, "PWM")]),
    ("J3", "FAN 1 (exhaust)", [(17, 17, "GND"), (18, 17, "12V"), (19, 17, "TACH"), (20, 17, "PWM")]),
    ("J4", "MOTOR", [(13, 13, "1A"), (14, 13, "1B"), (15, 13, "2A"), (16, 13, "2B")]),
    ("J5", "SCD40", [(17, 13, "3V3"), (18, 13, "GND"), (19, 13, "SDA"), (20, 13, "SCL")]),
    ("J6", "AS5600", [(13, 12, "3V3"), (14, 12, "GND"), (15, 12, "SDA"), (16, 12, "SCL")]),
    ("J7", "DS18B20 in", [(23, 12, "3V3"), (23, 13, "DQ"), (23, 14, "GND")]),
    ("J8", "DS18B20 out", [(23, 15, "GND"), (23, 16, "DQ"), (23, 17, "3V3")]),
]
TERM = [(0, 12, "+12V"), (0, 14, "GND")]   # J1: 2-pin screw terminal, 5.08 mm, wire entry toward the right wall
RES = [   # name, value, hole a, hole b, mount ("up": standing, body over hole a; "flat": lying, 10.16 between holes)
    ("R1", "10k", (14, 15), (15, 15), "up"),
    ("R2", "10k", (16, 15), (17, 15), "up"),
    ("R3", "10k", (18, 15), (19, 15), "up"),
    ("R4", "10k", (20, 15), (21, 15), "up"),
    ("R5", "10k", (18, 11), (22, 11), "flat"),
    ("R6", "1k", (13, 11), (17, 11), "flat"),
    ("R7", "100k", (3, 11), (7, 11), "flat"),
    ("R8", "22k", (8, 11), (12, 11), "flat"),
    ("R9", "4.7k", (22, 12), (22, 13), "up"),
    ("R10", "4.7k", (22, 17), (22, 16), "up"),
]
CAP = ((2, 17), (2, 16))          # C1, 100 uF 25 V: + and - holes

# Underside wires: net, then the holes and bends along it (first and last: soldered holes; bends between holes).
# Neighbouring holes: a solder bridge or a bent lead.
WIRES = [
    ("12V", [(0, 12), (3, 11)]), ("12V", [(0, 12), (1, 13), (1, 16.5), (2, 17)]), ("12V", [(2, 17), (4, 17)]),
    ("12V", [(2, 17), (2.5, 17.6), (13.5, 17.6), (14, 17)]), ("12V", [(14, 17), (14.5, 17.6), (17.5, 17.6), (18, 17)]),
    ("GND", [(0, 14), (2, 16)]), ("GND", [(2, 16), (5, 15)]), ("GND", [(5, 17), (5, 15)]), ("GND", [(5, 15), (5, 12)]),
    ("GND", [(5, 12), (6, 12)]), ("GND", [(5, 17), (5.5, 16.5), (10.5, 16.5), (11, 17)]), ("GND", [(11, 17), (13, 17)]),
    ("GND", [(13, 17), (13.5, 16.5), (16.5, 16.5), (17, 17)]), ("GND", [(17, 17), (17, 15)]), ("GND", [(17, 15), (18, 13)]),
    ("GND", [(17, 17), (21, 15)]), ("GND", [(21, 15), (23, 15)]), ("GND", [(23, 15), (23, 14)]),
    ("GND", [(22, 10), (22.5, 10.5), (22.5, 13.5), (23, 14)]), ("GND", [(12, 11), (11, 17)]), ("GND", [(14, 12), (12, 11)]),
    ("3V3", [(3, 0), (3.5, 0.5), (23.6, 0.5), (23.6, 10.5), (23, 11)]), ("3V3", [(23, 11), (22, 11)]),
    ("3V3", [(23, 11), (23, 12)]), ("3V3", [(23, 12), (22, 12)]), ("3V3", [(22, 12), (17.5, 12.5), (17, 13)]),
    ("3V3", [(17, 13), (18, 15)]), ("3V3", [(18, 15), (22, 17)]), ("3V3", [(22, 17), (23, 17)]),
    ("3V3", [(17, 13), (14, 15)]), ("3V3", [(14, 15), (12.5, 14.5), (12.5, 12.5), (13, 12)]), ("3V3", [(13, 12), (10, 17)]),
    ("SENSE", [(7, 11), (8, 11)]), ("SENSE", [(7, 11), (5, 10)]),
    ("EN", [(17, 0), (17.5, 10.5), (18, 11)]), ("EN", [(18, 11), (17.5, 11.65), (4.5, 11.65), (4, 12)]),
    ("TX", [(11, 0), (12.5, 10.5), (13, 11)]), ("UART", [(12, 0), (8.5, 10.5), (8, 12)]),
    ("UART", [(17, 11), (16.5, 11.35), (8.5, 11.35), (8, 12)]),
    ("STEP", [(18, 0), (10.5, 10.5), (10, 12)]), ("DIR", [(19, 0), (11.5, 10.5), (11, 12)]),
    ("PWM0", [(5, 0), (15.5, 10.5), (15.5, 14.5), (16, 15)]), ("PWM0", [(16, 15), (16, 17)]),
    ("TACH0", [(9, 0), (14.5, 10.5), (14.5, 14.5), (15, 15)]), ("TACH0", [(15, 15), (15, 17)]),
    ("PWM1", [(6, 0), (19.5, 10.5), (19.5, 14.5), (20, 15)]), ("PWM1", [(20, 15), (20, 17)]),
    ("TACH1", [(10, 0), (18.5, 10.5), (18.5, 14.5), (19, 15)]), ("TACH1", [(19, 15), (19, 17)]),
    ("SDA1", [(7, 0), (13.5, 10.5), (13.5, 11.5), (15, 12)]), ("SCL1", [(8, 0), (16.5, 10.5), (16, 12)]),
    ("SDA0", [(13, 0), (20.5, 10.5), (19.6, 12.5), (19, 13)]), ("SCL0", [(16, 0), (21.5, 10.5), (20.6, 12.4), (20, 13)]),
    ("DQi", [(19, 10), (21.5, 11.5), (22, 13)]), ("DQi", [(22, 13), (23, 13)]),
    ("DQo", [(21, 0), (22.6, 9.5), (23.8, 11.5), (23.8, 16), (23, 16)]), ("DQo", [(23, 16), (22, 16)]),
    ("M1A", [(7, 17), (13, 13)]), ("M1B", [(6, 17), (14, 13)]), ("M2A", [(8, 17), (15, 13)]), ("M2B", [(9, 17), (16, 13)]),
]

# Wires leaving the ESP32's back row cross its front row between two pins: drop straight down for the last rows.
WIRES = [(n, [q[0], (q[1][0], 8.6)] + q[1:] if q[0][1] == 0 and len(q) > 2 and q[1][1] == 10.5 else q) for n, q in WIRES]

# What sits in each hole, for the table
WHAT = {}
for i in range(20):
    WHAT[(3 + i, 0)] = "ESP " + ("GPIO " + ESP_L[i] if ESP_L[i].isdigit() else ESP_L[i])
    WHAT[(3 + i, 10)] = "ESP " + ("GPIO " + ESP_R[i] if ESP_R[i].isdigit() else ESP_R[i])
for i in range(8):
    WHAT[(4 + i, 12)] = "TMC " + TMC_S[i]
    WHAT[(4 + i, 17)] = "TMC " + TMC_P[i]
for hn, title, hp in HEADERS:
    for c, r, lab in hp:
        WHAT[(c, r)] = f"{hn} {lab}"
for c, r, lab in TERM:
    WHAT[(c, r)] = f"J1 {lab}"
for rn, val, a, b, mount in RES:
    WHAT[a] = rn; WHAT[b] = rn
WHAT[CAP[0]] = "C1 +"; WHAT[CAP[1]] = "C1 -"
WHAT.setdefault((5, 15), "tie point")
WHAT.setdefault((23, 11), "tie point")

out = []


def text(x, y, s, size=13, anchor="middle", color="#111", weight="normal", halo=0):
    """halo: opacity of a white outline behind the letters (0: none)"""
    h = (f' stroke="#ffffff" stroke-opacity="{halo}" stroke-width="3" stroke-linejoin="round" paint-order="stroke"'
         if halo else "")
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}"{h}>{s}</text>')


def hole_name(h):
    return f"{LET[h[0]]}{NY - h[1]}"


def panel(ox, oy, under):
    """Draw one view of the board; (ox, oy): canvas position of the top-left grid hole. Returns the grid mapper."""
    def G(c, r):
        cc = c if under else NX - 1 - c                 # from above, A is on the right; from below, on the left
        return ox + cc * P, oy + r * P

    def rect_g(c0, r0, c1, r1, fill, stroke="#222", sw=1.5, rx=3, op=1.0, dash=None):
        (xa, ya), (xb, yb) = G(c0, r0), G(c1, r1)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<rect x="{min(xa, xb):.1f}" y="{min(ya, yb):.1f}" width="{abs(xb - xa):.1f}" height="{abs(yb - ya):.1f}" '
                   f'rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    # board and grid labels
    mx, my = (70 - (NX - 1) * PITCH) / 2 * K, (50 - (NY - 1) * PITCH) / 2 * K
    xl, yt = ox - mx, oy - my
    out.append(f'<rect x="{xl:.1f}" y="{yt:.1f}" width="{70 * K:.1f}" height="{50 * K:.1f}" rx="6" '
               f'fill="{"#d8c79c" if under else "#e8d6a8"}" stroke="#8a6d2a" stroke-width="2"/>')
    for c in range(NX):
        x, _ = G(c, 0)
        text(x, yt - 7, LET[c], 12, color="#8a6d2a", weight="bold")
        text(x, yt + 50 * K + 17, LET[c], 12, color="#8a6d2a", weight="bold")
    for r in range(NY):
        _, y = G(0, r)
        text(xl - 8, y + 4, str(NY - r), 12, "end", "#8a6d2a", "bold")
        text(xl + 70 * K + 8, y + 4, str(NY - r), 12, "start", "#8a6d2a", "bold")
    for c in range(NX):
        for r in range(NY):
            x, y = G(c, r)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#b8975a"/>')

    # board outlines (solid from above, dashed from below)
    pe = (50 - 19 * PITCH) / 2 / PITCH
    pw = 28.5 / 2 / PITCH
    pt, tw = (20.81 - 7 * PITCH) / 2 / PITCH, 15.08 / 2 / PITCH
    if under:
        rect_g(3 - pe, 5 - pw, 22 + pe, 5 + pw, "none", "#183a6b", 1.5, 6, 1, "8,5")
        rect_g(4 - pt, 14.5 - tw, 11 + pt, 14.5 + tw, "none", "#333", 1.5, 4, 1, "8,5")
        rect_g(3 - pe - 7 / PITCH - 1.6, 5 - 9.25 / PITCH - 1.2, 3 - pe + 1, 5 + 9.25 / PITCH + 1.2, "#b3261e", "#b3261e", 1.5, 2, 0.08, "6,4")
        x, y = G(1, 5.5)
        text(x, y + 4, "no wires", 12, color="#b3261e", weight="bold")
        x, y = G(5.5, 8.5)
        text(x, y + 5, "ESP32-S3 above", 14, color="#183a6b", weight="bold")
        x, y = G(7.5, 14.5)
        text(x, y + 4, "TMC2209 above", 13, color="#333", weight="bold")
    else:
        rect_g(3 - pe, 5 - pw, 22 + pe, 5 + pw, "#3b6fb6", "#183a6b", 2, 6, 0.3)
        rect_g(3 - pe - 7 / PITCH, 5 - 9.25 / PITCH, 3 - pe, 5 + 9.25 / PITCH, "#2a2a2a", "#111", 1.5, 2, 0.4)
        rect_g(3 - pe - 7 / PITCH - 1.6, 5 - 9.25 / PITCH - 1.2, 3 - pe + 1, 5 + 9.25 / PITCH + 1.2, "none", "#b3261e", 1.5, 2, 1, "6,4")
        x, y = G(1.2, 5)
        text(x, y - 6, "antenna:", 12, color="#b3261e", weight="bold", halo=0.6)
        text(x, y + 10, "keep clear", 12, color="#b3261e", weight="bold", halo=0.6)
        x, y = G(12.5, 4.6)
        text(x, y, "ESP32-S3, soldered", 17, color="#183a6b", weight="bold")
        text(x, y + 19, "USB end toward the left wall", 13, color="#183a6b")
        rect_g(4 - pt, 14.5 - tw, 11 + pt, 14.5 + tw, "#222", "#000", 2, 4, 0.22)
        rect_g(11 + pt - 15 / PITCH - 0.134, 14.5 - 7.2 / PITCH, 11 + pt - 0.134, 14.5 + 7.2 / PITCH, "#2f5fd0", "#1b3a8a", 1.5, 2, 0.25)
        x, y = G(7.5, 14.5)
        text(x, y - 2, "TMC2209, soldered", 14, color="#111", weight="bold")
        text(x, y + 14, "heatsink up", 12, color="#333")

    # module pins with their names
    for i in range(20):
        for r, labs in ((0, ESP_L), (10, ESP_R)):
            x, y = G(3 + i, r)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="#f4d35e" stroke="#7a5c00" stroke-width="1.2"/>')
            text(x, y + (-10 if r == 0 else 19), labs[i], 9.5, color="#183a6b", weight="bold", halo=0.3)
    for i in range(8):
        for r, labs in ((12, TMC_S), (17, TMC_P)):
            x, y = G(4 + i, r)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="#f4d35e" stroke="#7a5c00" stroke-width="1.2"/>')
            text(x, y + (-10 if r == 12 else 19), labs[i], 9.5, color="#111", weight="bold", halo=0.6)

    if not under:
        # J1 screw terminal, C1, resistors, headers (top side only)
        rect_g(-0.6, 11.05, 2.4, 14.95, "#2e8b57", "#1b5e20", 2, 3, 0.85)
        for c, r, lab in TERM:
            x, y = G(c, r)
            out.append(f'<rect x="{x - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" fill="#e0b84a" stroke="#000"/>')
            text(x - 12, y + 4, lab, 11, "end", "#ffffff", "bold")
        x, y = G(1, 13)
        text(x, y + 5, "J1", 13, color="#ffffff", weight="bold")
        (xp, yp), (xm, ym) = G(*CAP[0]), G(*CAP[1])
        out.append(f'<circle cx="{xp:.1f}" cy="{(yp + ym) / 2:.1f}" r="{3.15 * K:.1f}" fill="#6a4c93" fill-opacity="0.8" '
                   f'stroke="#3d2a5c" stroke-width="2"/>')
        text(xp, (yp + ym) / 2 + 4, "C1", 12, color="#fff", weight="bold")
        text(xp + 15, yp + 5, "+", 14, color="#fff", weight="bold")
        for rn, val, a, b, mount in RES:
            (xa, ya), (xb, yb) = G(*a), G(*b)
            out.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="#666" stroke-width="2"/>')
            if mount == "flat":
                xm_, ym_ = (xa + xb) / 2, (ya + yb) / 2
                out.append(f'<rect x="{xm_ - 3.15 * K:.1f}" y="{ym_ - 8:.1f}" width="{6.3 * K:.1f}" height="16" rx="7" '
                           f'fill="#d9c6a0" stroke="#7a5c2a" stroke-width="1.5"/>')
                text(xm_, ym_ + 4.5, f"{rn} {val}", 11, weight="bold")
            else:
                out.append(f'<circle cx="{xa:.1f}" cy="{ya:.1f}" r="{1.15 * K:.1f}" fill="#d9c6a0" stroke="#7a5c2a" stroke-width="1.5"/>')
                text(xa, ya + 4, rn, 10, weight="bold")
                text((xa + xb) / 2, ya + 30, val, 10.5, color="#333")
            x, y = G(*b)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#888"/>')
        for hn, title, hp in HEADERS:
            cs, rs = [p[0] for p in hp], [p[1] for p in hp]
            rect_g(min(cs) - 0.45, min(rs) - 0.45, max(cs) + 0.45, max(rs) + 0.45, "#1a1a1a", "#000", 1.5, 2, 0.88)
            vertical = len(set(cs)) == 1
            for c, r, lab in hp:
                x, y = G(c, r)
                out.append(f'<rect x="{x - 4.5:.1f}" y="{y - 4.5:.1f}" width="9" height="9" fill="#e0b84a" stroke="#000"/>')
                if vertical:
                    text(x - 18, y + 4, lab, 9.5, "end", "#111", "bold", 0.6)
                else:
                    text(x, y + (21 if r in (13, 17) else -11), lab, 9.5, color="#111", weight="bold", halo=0.6)
            xa, ya = G((min(cs) + max(cs)) / 2, max(rs))
            if vertical:
                xa, ya = G(cs[0], (min(rs) + max(rs)) / 2)
                text(xa - 47, ya - 4, hn, 11.5, "end", weight="bold")
                text(xa - 47, ya + 11, title.replace("DS18B20 ", "DS "), 10.5, "end", weight="bold")
            elif rs[0] == 12:
                xe, _ = G(max(cs) + 0.5, rs[0])
                text(xe - 6, ya + 4, f"{hn} {title}", 11.5, "end", weight="bold")
            else:
                text(xa, ya + 36, f"{hn} {title}", 11.5, weight="bold")
    return G


def is_short(path):
    a, b = path[0], path[-1]
    return len(path) == 2 and abs(a[0] - b[0]) + abs(a[1] - b[1]) <= 1


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px_, py_ = p
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px_ - ax) * dx + (py_ - ay) * dy) / (dx * dx + dy * dy)))
    return ((ax + t * dx - px_) ** 2 + (ay + t * dy - py_) ** 2) ** 0.5


# clearance check: no wire may pass close to a used hole that is not its own end (or of the same net)
hole_net = {}
for net, path in WIRES:
    for h in (path[0], path[-1]):
        hole_net.setdefault(h, set()).add(net)
used = set(WHAT) | set(hole_net)
bad = 0
for i, (net, path) in enumerate(WIRES, 1):
    for h in used:
        if h in (path[0], path[-1]) or net in hole_net.get(h, ()):
            continue
        d = min(seg_dist(h, path[k], path[k + 1]) for k in range(len(path) - 1))
        if d < 0.3:
            print(f"  wire {i} ({net}) passes {d:.2f} from {hole_name(h)} {WHAT.get(h, '')}")
            bad += 1
print("clearance problems:", bad)


def wires(G):
    """The numbered wires on a solder-side panel."""
    for i, (net, path) in enumerate(WIRES, 1):
        pts = " ".join(f"{G(*q)[0]:.1f},{G(*q)[1]:.1f}" for q in path)
        sh = is_short(path)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{NET[net]}" stroke-width="{7 if sh else 2.6}" '
                   f'stroke-opacity="{0.95 if sh else 0.85}" stroke-linecap="round" stroke-linejoin="round"/>')
    for h in sorted(used):
        x, y = G(*h)
        if h in hole_net:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fff" stroke="#000" stroke-width="1.5"/>')
    mid_used = []
    for i, (net, path) in enumerate(WIRES, 1):
        if is_short(path):
            continue
        k = max(range(len(path) - 1), key=lambda j: (path[j + 1][0] - path[j][0]) ** 2 + (path[j + 1][1] - path[j][1]) ** 2)
        (xa, ya), (xb, yb) = G(*path[k]), G(*path[k + 1])
        for t in (0.5, 0.4, 0.6, 0.3, 0.7, 0.45, 0.55, 0.35, 0.65, 0.25, 0.75, 0.2, 0.8):   # number tag at a free spot
            xm, ym = xa + (xb - xa) * t, ya + (yb - ya) * t
            if all((xm - u) ** 2 + (ym - v) ** 2 > 22 ** 2 for u, v in mid_used):
                break
        mid_used.append((xm, ym))
        out.append(f'<circle cx="{xm:.1f}" cy="{ym:.1f}" r="10" fill="#ffffff" stroke="{NET[net]}" stroke-width="2"/>')
        text(xm, ym + 4, str(i), 10, color="#000", weight="bold")


def table(x, y, first, last, size=11.5, rowh=18.5):
    """Rows first..last (numbered from 1) of the wire list, from (x, y)."""
    k = size / 11.5
    for i in range(first, last + 1):
        net, path = WIRES[i - 1]
        a, b = path[0], path[-1]
        out.append(f'<rect x="{x:.1f}" y="{y - 12 * k:.1f}" width="{12 * k:.1f}" height="{12 * k:.1f}" rx="2" fill="{NET[net]}"/>')
        text(x + 34 * k, y - 1, str(i), size, "end", weight="bold")
        text(x + 42 * k, y - 1, net, size, "start", NET[net] if net not in ("M2B", "M2A") else "#666", "bold")
        text(x + 100 * k, y - 1, f"{hole_name(a)}  {WHAT.get(a, '')}", size, "start")
        text(x + 245 * k, y - 1, "to", size, "start", "#888")
        text(x + 265 * k, y - 1, f"{hole_name(b)}  {WHAT.get(b, '')}" + ("  (bridge)" if is_short(path) else ""), size, "start")
        y += rowh


TITLE = "Perfboard build plan (5 x 7 cm protoboard, 24 x 18 holes)"
GRID = "Columns A to X from the right wall, rows 18 (back) to 1 (front), as printed on the board (A18 is its back right corner, seen from above)."
TOP = "Component side, seen from above: window (outdoor) side at the top, room (indoor) side at the bottom"
BOT = "Solder side, turned over left to right: A on the left, window side still at the top"
WIRE_NOTE = ["Thin insulated wire (wire-wrap or 26-30 AWG), except 22-24 AWG",
             "for the 12 V and GND around the driver (1-14) and the motor (58-61)."]
NOTES = [   # paragraphs, wrapped to each page's width
    "Values: R1-R5 10k, R6 1k, R7 100k, R8 22k, R9 R10 4.7k (1/4 W); C1 100 uF 25 V. R1-R4, R9, R10 stand up; R5-R8 lie flat "
    "in row 7, so they pass under the edges of the ESP32 and the TMC2209 (2.6 mm up on their pin spacers).",
    "Headers: 1 x 4 and 1 x 3 male, 2.54 mm. The fan plugs (J2, J3) go on with their latch toward row 2; keep row 2 clear there.",
    "AS5600: tie its DIR pin to GND at the module. TMC2209: CLK and PDN stay free (wires 38-39 go to its UART pin; check with a "
    "meter that UART is PDN_UART on your module); DIAG (GPIO 13) is not on its pins, so it stays free too.",
    "Solder the parts first, then the ESP32 and the TMC2209: the wires under them must be in place before. "
    "Check each net with a meter before power; 12 V on J1 only with the motor plugged in.",
]


def notes(x, y, size=12.5, step=19, width=128):
    """The notes from (x, y), wrapped at width characters; returns the last baseline."""
    import textwrap
    for par in NOTES:
        for line in textwrap.wrap(par, width):
            text(x, y, line, size, "start", color="#333")
            y += step
    return y - step


def save(path, w, h):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
           + "\n".join(out) + "\n</svg>\n")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    out.clear()


# --- the README sheet: both sides and the list --------------------------------------------------------
TX0 = 1175
text(40, 42, TITLE, 24, "start", weight="bold")
text(40, 70, GRID, 14, "start", color="#333")
text(150, 120, TOP, 17, "start", weight="bold")
panel(150, 205, False)
text(150, 920, BOT, 17, "start", weight="bold")
wires(panel(150, 1000, True))
notes(150, 1712)
text(TX0, 130, "Wires (solder side)", 17, "start", weight="bold")
for i, n in enumerate(WIRE_NOTE):
    text(TX0, 150 + i * 16, n, 12, "start", color="#333")
table(TX0, 196, 1, len(WIRES))
save(OUT, 1650, 1850)
print("wrote", OUT, len(WIRES), "wires")

# --- the PDF: three landscape Letter pages ------------------------------------------------------------
PW, PH = 1400, 1082                       # 279.4 x 215.9 mm
OXP = (PW - 23 * P) / 2                   # board centred across the page
pages = []
tmp = tempfile.mkdtemp(prefix="wv_perf_")

text(60, 58, TITLE, 26, "start", weight="bold")
text(60, 88, GRID, 14.5, "start", color="#333")
text(60, 128, "Page 1 of 3. " + TOP, 18, "start", weight="bold")
panel(OXP, 205, False)
last = notes(60, 922, 13.5, 20, 210)
assert last <= PH - 40, f"page 1 notes run to {last}: past the printable area"
pages.append(os.path.join(tmp, "p1.svg")); save(pages[-1], PW, PH)

text(60, 58, TITLE, 26, "start", weight="bold")
text(60, 128, "Page 2 of 3. " + BOT, 18, "start", weight="bold")
wires(panel(OXP, 225, True))
text(60, 945, "Lines are the wires on the underside, coloured by net; the numbers match the list on page 3. Thick short bars are",
     13.5, "start", color="#333")
text(60, 965, "solder bridges between neighbouring holes. Dashed outlines: the ESP32 and the TMC2209, on the other side.",
     13.5, "start", color="#333")
pages.append(os.path.join(tmp, "p2.svg")); save(pages[-1], PW, PH)

text(60, 58, TITLE, 26, "start", weight="bold")
text(60, 100, "Page 3 of 3. Wires (solder side), with the numbers of page 2", 18, "start", weight="bold")
text(60, 124, " ".join(WIRE_NOTE), 13.5, "start", color="#333")
half = (len(WIRES) + 1) // 2
table(60, 175, 1, half, 13, 26.5)
table(720, 175, half + 1, len(WIRES), 13, 26.5)
pages.append(os.path.join(tmp, "p3.svg")); save(pages[-1], PW, PH)

if os.path.exists(CHROME):
    html = os.path.join(tmp, "plan.html")
    body = "".join(f'<img src="file:///{q.replace(os.sep, "/")}">' for q in pages)
    with open(html, "w", encoding="utf-8") as fh:
        fh.write('<!doctype html><html><head><meta charset="utf-8"><style>@page { size: 279.4mm 215.9mm; margin: 0 } '
                 'html, body { margin: 0 } img { display: block; width: 279.4mm; height: 215.9mm; break-after: page }'
                 '</style></head><body>' + body + '</body></html>')
    subprocess.run([CHROME, "--headless=new", f"--user-data-dir={os.path.join(tmp, 'prof')}", "--no-pdf-header-footer",
                    f"--print-to-pdf={PDF}", "file:///" + html.replace(os.sep, "/")], capture_output=True)
    print("wrote", PDF if os.path.exists(PDF) else "(no PDF: Chrome failed)")
else:
    print("Chrome not found: no PDF")
