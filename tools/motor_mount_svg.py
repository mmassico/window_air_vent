#!/usr/bin/env python3
"""Draw doc/motor_mount.svg: a section through one motor screw (motor, motor plate with its boss, frame, M3 x 8).

Usage: python tools/motor_mount_svg.py   (run from the window-vent folder)
Values follow cad/window_vent.scad (mplate_t, mp_boss, mp_t, mp_pocket) and the 17HS08-1004S motor; keep them in step.
The section is taken across the flats of the frame's diamond pocket.
"""
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "motor_mount.svg")

PLATE_T = 4.0                # mplate_t
BOSS_D, BOSS_H = 6.0, 2.0    # mp_boss
FRAME_T = 3.0                # mp_t
POCKET = 8.0                 # mp_pocket, across the flats
HOLE_D = 3.4                 # clearance hole in the plate and boss
SCREW_L = 8.0                # M3 x 8, length under the head
HEAD_D, HEAD_H = 5.7, 1.65   # ISO 7380 button head
THREAD_DEPTH = 2.5           # motor's M3 holes
FREE_BELOW = 38              # empty tower under the frame at the screw positions, down to the upper duct

K = 34                       # px per mm
W, H = 1300, 860
OX, OY = 690, 470            # canvas position of the screw axis at the plate's underside (z = 0)
C_DIM = "#b3261e"

out = []


def P(x, z):
    return OX + x * K, OY - z * K


def rect(x0, z0, x1, z1, fill, stroke="#222", sw=1.5, dash=None):
    a, b = P(min(x0, x1), max(z0, z1))
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{abs(x1 - x0) * K:.1f}" height="{abs(z1 - z0) * K:.1f}" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def text(x, y, s, size=15, anchor="middle", color="#111", weight="normal", rotate=None):
    tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
               f'font-weight="{weight}"{tr}>{s}</text>')


def line(x1, y1, x2, y2, color=C_DIM, width=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d}/>')


def arrow(x, y, dx, dy):
    n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
    p1 = (x - ux * 9 - uy * 3.5, y - uy * 9 + ux * 3.5)
    p2 = (x - ux * 9 + uy * 3.5, y - uy * 9 - ux * 3.5)
    out.append(f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{C_DIM}"/>')


def zdim(z0, z1, x, ext_x, label, right=True):
    """vertical dimension from z0 to z1 (mm) at model x; extension lines from model x = ext_x"""
    (cx, a), (_, b) = P(x, z0), P(x, z1)
    ex, _ = P(ext_x, 0)
    s = 6 if cx > ex else -6
    line(ex, a, cx + s, a, dash="3,3"); line(ex, b, cx + s, b, dash="3,3")
    line(cx, a, cx, b, width=1.5); arrow(cx, a, 0, 1 if a > b else -1); arrow(cx, b, 0, -1 if a > b else 1)
    text(cx + (10 if right else -10), (a + b) / 2 + 5, label, 15, "start" if right else "end", C_DIM)


def xdim(x0, x1, z, ext_z, label, above=True):
    (a, cz), (b, _) = P(x0, z), P(x1, z)
    _, ez = P(0, ext_z)
    s = -6 if cz < ez else 6
    line(a, ez, a, cz + s, dash="3,3"); line(b, ez, b, cz + s, dash="3,3")
    line(a, cz, b, cz, width=1.5); arrow(a, cz, -1, 0); arrow(b, cz, 1, 0)
    text((a + b) / 2, cz - 8 if above else cz + 20, label, 15, color=C_DIM)


# --- parts (section) ---------------------------------------------------------------------------------
X = 9.5                                                   # half-width of the section shown
rect(-X, PLATE_T, X, PLATE_T + 6, "#c9ccd1")              # motor end cap (cut off above)
rect(-1.25, PLATE_T, 1.25, PLATE_T + THREAD_DEPTH, "#ffffff", "#222", 1.2)   # its M3 hole (tap drill 2.5)
for xs in (-X, POCKET / 2):                               # frame, either side of the pocket
    rect(xs, -FRAME_T, xs + (X - POCKET / 2), 0, "#9fb3c8")
rect(-X, 0, -HOLE_D / 2, PLATE_T, "#e9a15a")              # plate, either side of the hole
rect(HOLE_D / 2, 0, X, PLATE_T, "#e9a15a")
rect(-BOSS_D / 2, -BOSS_H, -HOLE_D / 2, 0, "#e9a15a")     # boss
rect(HOLE_D / 2, -BOSS_H, BOSS_D / 2, 0, "#e9a15a")
z_head = -BOSS_H                                          # screw: head under the boss, shank up into the motor
rect(-HEAD_D / 2, z_head - HEAD_H, HEAD_D / 2, z_head, "#5b6470")
rect(-1.5, z_head, 1.5, z_head + SCREW_L, "#7d8794")
for i in range(int((z_head + SCREW_L - PLATE_T) / 0.5)):  # thread lines where it engages the motor
    z = PLATE_T + 0.25 + i * 0.5
    a, b = P(-1.5, z); c, d = P(1.5, z)
    line(a, b, c, d, "#3a3f46", 1)
line(*P(0, -FRAME_T - 2.5), *P(0, PLATE_T + 6.5), "#777", 1, "10,4,2,4")   # screw axis

# labels on the parts
text(*P(-X + 0.3, PLATE_T + 4.6), "motor end cap", 15, "start", "#333", "bold")
text(*P(-X + 0.3, 1.6), "motor plate", 15, "start", "#5a2d00", "bold")
text(*P(-X + 0.3, -2.75), "frame", 15, "start", "#1d3557", "bold")
text(*P(-3.2, -4.15), "M3 x 8, button head", 15, "end", "#333", "bold")

# --- dimensions ---------------------------------------------------------------------------------------
zdim(0, PLATE_T, X + 1.2, X, f"{PLATE_T:g} plate")
zdim(-BOSS_H, 0, X + 1.2, BOSS_D / 2, f"{BOSS_H:g} boss")
zdim(-FRAME_T, 0, X + 4.6, X, f"{FRAME_T:g} frame")
zdim(PLATE_T, PLATE_T + THREAD_DEPTH, -X - 1.2, -1.25, f"{THREAD_DEPTH} hole depth", right=False)
zdim(PLATE_T, z_head + SCREW_L, -X - 4.8, -1.5, f"{z_head + SCREW_L - PLATE_T:g} in the motor", right=False)
zdim(z_head, z_head + SCREW_L, -X - 8.4, -1.5, f"{SCREW_L:g} screw", right=False)
zdim(-FRAME_T, z_head - HEAD_H, X + 4.6, HEAD_D / 2, f"{-(z_head - HEAD_H) - FRAME_T:.2f} below", right=True)
xdim(-POCKET / 2, POCKET / 2, -FRAME_T - 1.6, -FRAME_T, f"{POCKET:g} pocket (across the flats)", above=False)
xdim(-BOSS_D / 2, BOSS_D / 2, PLATE_T + 7.3, 0, f"Ø {BOSS_D:g} boss: {(POCKET - BOSS_D) / 2:g} clear each side")

text(40, 50, "Motor screw mount: section through one of the four screws (mm)", 22, "start", weight="bold")
notes = [
    f"The motor's M3 holes are {THREAD_DEPTH} deep: through the {PLATE_T:g} mm plate and its {BOSS_H:g} mm boss, an M3 x 8 reaches "
    f"{z_head + SCREW_L - PLATE_T:g} mm in (4 threads), {THREAD_DEPTH - (z_head + SCREW_L - PLATE_T):g} mm short of the bottom.",
    f"The bosses and heads go down through the frame's diamond pockets; below the frame there is about {FREE_BELOW} mm of empty tower.",
    "Screw the motor on at the bench (heads from below), then set the plate on the frame. A socket head (3 mm) would also fit.",
]
for i, n in enumerate(notes):
    out.append(f'<text x="40" y="{H - 90 + i * 24}" font-size="14" fill="#333">{n}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
