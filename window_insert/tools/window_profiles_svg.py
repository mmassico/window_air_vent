#!/usr/bin/env python3
"""Draw doc/window_top_view.svg and doc/window_side_view.svg: the window's profiles around the foam insert, to scale.

Usage: python tools/window_profiles_svg.py   (run from the window_insert folder)
All dimensions in mm, measured on the window (the same values as cad/window_caps.scad). u runs across the foam's
thickness from its centre (the centre of the 25.90 sash channel), outdoor negative. Both views keep one scale in x
and y; the side view breaks the foam's height twice to fit the page, and its z labels give the true heights.
"""
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_TOP = os.path.join(ROOT, "doc", "window_top_view.svg")
OUT_SIDE = os.path.join(ROOT, "doc", "window_side_view.svg")
OUT_WIDTH = os.path.join(ROOT, "doc", "insert_width.svg")

# Measurements
FOAM_T, FOAM_W = 50.8, 112.0
LIP_D, LIP_T, FOAM_CLR = 8.0, 4.8, 0.2       # the caps' lips: reach onto the foam, thickness; clearance to the foam
CHASSIS_W = 90.0                            # the vent's chassis, on the foam's room face (at least)
BASE = 3.0                                  # cap base at each edge of the foam (side frame and sash)
SASH_T, SASH_THIN = 25.80, 17.10            # sash thickness at its end, and how far from its end it stays that thin
GROOVE = (7.90, 7.50, 7.50)                 # sash end groove: width at the mouth, at the bottom, depth
CH_W, CH_D = 25.90, 10.70                   # side frame's sash channel
STRIP = (-4.20, 2.80, 19.0, 4.0)            # soft foam strip at the back of the channel: u from, u to, height, depth
FLOOR_STRIP = 1.7                           # another soft strip on the channel's floor, across it, 4.0 deep from the
                                            #   back wall (as STRIP): its thickness
SCREW = (3.70, 12.0)                        # screw heads in the sash's groove, near its top and bottom ends only:
                                            #   height above the groove's bottom, extent from the end
TOP_RIBS = [(-39.85, -34.55, 8.50), (-3.55, 2.15, 8.50), (14.45, 18.20, 7.40)]     # u from, u to, depth
BOT_RIBS = [(-39.50, -33.80, 18.40), (-3.55, 2.15, 11.00), (12.95, 19.85, 11.00)]  # u from, u to, height
TIP = 1060.0                                # centre rib tip to centre rail tip
H = TIP + 8.50 + 11.00                      # ceiling to floor
LATCH_U0 = 18.20                            # latch zone: from the top room-side rib's room edge ...
LATCH_W, LATCH_H, LATCH_D = 40.0, 80.0, 40.0   # ... 40 toward the room, 80 high, 40 into the opening
LATCH_Z0 = 11.00 + 495.0                    # its bottom: 495 above the rail tips
CAP_TOP, CAP_BOT = 12.0, 14.5               # where the caps put the foam's top and bottom edges

K = 7                                       # px per mm, both views
C_DIM = "#b3261e"
C_FRAME, C_EDGE = "#c4c4c4", "#555555"
C_FOAM, C_LATCH, C_STRIP, C_BAND = "#ff9ccb", "#fff59a", "#f5b800", "#e9e9e9"


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.out = w, h, []

    def rect(self, x1, y1, x2, y2, fill, stroke=C_EDGE, width=1.5, dash=None, opacity=None):
        x, y = min(x1, x2), min(y1, y2)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{opacity}"' if opacity else ""
        self.out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{abs(x2 - x1):.1f}" height="{abs(y2 - y1):.1f}" '
                        f'fill="{fill}"{o} stroke="{stroke}" stroke-width="{width}"{d}/>')

    def poly(self, pts, fill, stroke=C_EDGE, width=1.5):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.out.append(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def line(self, x1, y1, x2, y2, color="#111", width=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                        f'stroke-width="{width}"{d}/>')

    def path(self, d, color="#111", width=1.5, fill="none"):
        self.out.append(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{width}"/>')

    def text(self, x, y, s, size=15, anchor="middle", color="#111", weight="normal", rotate=None):
        tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
        self.out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
                        f'font-weight="{weight}"{tr}>{s}</text>')

    def arrow(self, x, y, dx, dy, color=C_DIM):
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        a, b = 10, 3.5
        p1 = (x - ux * a - uy * b, y - uy * a + ux * b)
        p2 = (x - ux * a + uy * b, y - uy * a - ux * b)
        self.out.append(f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" '
                        f'fill="{color}"/>')

    def hdim(self, xa, xb, y, label, ext=(), color=C_DIM, text_side=0):
        """Horizontal dimension from canvas xa to xb at canvas y. ext: (x, y_from) extension lines to draw.
        A short span gets its arrows from outside and its label beside it (text_side -1: left, else right)."""
        for ex, ey in ext:
            self.line(ex, ey, ex, y + (6 if y > ey else -6), color, 1, "3,3")
        xa, xb = min(xa, xb), max(xa, xb)
        if xb - xa >= 46:
            self.line(xa, y, xb, y, color, 1.5)
            self.arrow(xa, y, -1, 0, color)
            self.arrow(xb, y, 1, 0, color)
            self.text((xa + xb) / 2, y - 6, label, 14, color=color)
        else:
            self.line(xa - 22, y, xb + 22, y, color, 1.5)
            self.arrow(xa, y, 1, 0, color)
            self.arrow(xb, y, -1, 0, color)
            if xb - xa >= 26:
                self.text((xa + xb) / 2, y - 6, label, 14, color=color)
            elif text_side < 0:
                self.text(xa - 26, y + 5, label, 14, "end", color=color)
            else:
                self.text(xb + 26, y + 5, label, 14, "start", color=color)

    def vdim(self, ya, yb, x, label, ext=(), color=C_DIM, text_side=1):
        """Vertical dimension from canvas ya to yb at canvas x; label beside it (text_side 1: right, -1: left)."""
        for ex, ey in ext:
            self.line(ex, ey, x + (6 if x > ex else -6), ey, color, 1, "3,3")
        ya, yb = min(ya, yb), max(ya, yb)
        if yb - ya >= 30:
            self.line(x, ya, x, yb, color, 1.5)
            self.arrow(x, ya, 0, -1, color)
            self.arrow(x, yb, 0, 1, color)
        else:
            self.line(x, ya - 20, x, yb + 20, color, 1.5)
            self.arrow(x, ya, 0, 1, color)
            self.arrow(x, yb, 0, -1, color)
        if text_side > 0:
            self.text(x + 7, (ya + yb) / 2 + 5, label, 14, "start", color=color)
        else:
            self.text(x - 7, (ya + yb) / 2 + 5, label, 14, "end", color=color)

    def zigzag_v(self, x, y1, y2, amp=7):
        """A vertical break line (a straight line with one Z in its middle)."""
        m = (y1 + y2) / 2
        self.path(f"M{x:.1f},{y1:.1f} L{x:.1f},{m - 10:.1f} L{x + amp:.1f},{m - 4:.1f} L{x - amp:.1f},{m + 4:.1f} "
                  f"L{x:.1f},{m + 10:.1f} L{x:.1f},{y2:.1f}", "#111", 1.5)

    def zigzag_h(self, x1, x2, y, amp=7):
        """A horizontal break line."""
        m = (x1 + x2) / 2
        self.path(f"M{x1:.1f},{y:.1f} L{m - 10:.1f},{y:.1f} L{m - 4:.1f},{y - amp:.1f} L{m + 4:.1f},{y + amp:.1f} "
                  f"L{m + 10:.1f},{y:.1f} L{x2:.1f},{y:.1f}", "#111", 1.5)

    def save(self, path):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" font-family="Segoe UI, Helvetica, Arial, sans-serif">\n'
               f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>\n' + "\n".join(self.out) + "\n</svg>\n")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(svg)
        print("wrote", path)


def fmt(v):
    return f"{v:.2f}"


# =================================== TOP VIEW ===================================
# x across the window: 0 on the side frame's face, positive toward the sash (drawn to the left); u downward (room)
def top_view():
    xs = BASE + FOAM_W + BASE                   # the sash's end face
    X0, Y0 = 1292, 470                          # canvas position of x = 0, u = 0
    s = Svg(1832, 1112)

    def P(x, u):
        return X0 - x * K, Y0 + u * K

    sl = xs + SASH_THIN + 14                    # where the sash is cut off
    fr = -32                                    # where the side frame is cut off
    s.line(*P(sl + 6, 0), *P(fr, 0), "#777", 1, "14,4,3,4")   # foam centre line, under everything

    # side frame, with its channel, cut off on the right
    a = [P(0, -42), P(0, -CH_W / 2), P(-CH_D, -CH_W / 2), P(-CH_D, CH_W / 2), P(0, CH_W / 2), P(0, 66),
         P(fr, 66), P(fr, -42)]
    s.poly(a, C_FRAME)
    s.zigzag_v(P(fr, 0)[0], P(0, -42)[1] - 12, P(0, 66)[1] + 12)
    s.rect(*P(-CH_D, STRIP[0]), *P(-CH_D + STRIP[3], STRIP[1]), C_STRIP)

    # foam, and the latch zone over it
    s.rect(*P(BASE, -FOAM_T / 2), *P(BASE + FOAM_W, FOAM_T / 2), C_FOAM)
    s.rect(*P(0, LATCH_U0), *P(LATCH_D, LATCH_U0 + LATCH_W), C_LATCH, "#9a8f00", 1.5, "6,3", 0.85)

    # the sash's end, with its groove, cut off on the left
    gm, gb, gd = GROOVE[0] / 2, GROOVE[1] / 2, GROOVE[2]
    st = SASH_T / 2
    s.poly([P(xs, -st), P(xs, -gm), P(xs + gd, -gb), P(xs + gd, gb), P(xs, gm), P(xs, st), P(sl, st), P(sl, -st)],
           C_FRAME)
    s.zigzag_v(P(sl, 0)[0], P(0, -st)[1] - 12, P(0, st)[1] + 12)
    for f in (-st, st):
        s.line(*P(xs + SASH_THIN, f - 2), *P(xs + SASH_THIN, f + 2), "#555", 1.5)
    s.rect(*P(xs + gd - SCREW[0], -gb), *P(xs + gd, gb), "none", "#555", 1.5, "4,3")   # screw head, not in this plane

    # labels
    s.text(*P(BASE + FOAM_W / 2, -15), "XPS foam", 17, weight="bold")
    s.text(P(sl, 0)[0] - 2, P(0, -st)[1] - 84, "Sliding sash (its end)", 16, "start", weight="bold")
    s.text(P(sl + 2, 0)[0], P(0, st)[1] + 44, "past 17.10 the sash widens (not drawn)", 13, "start", "#555")
    s.text(P(fr / 2, 0)[0], P(0, -42)[1] - 22, "Window side frame", 16, weight="bold")
    s.text(*P(LATCH_D / 2, LATCH_U0 + LATCH_W / 2 - 1), "Window latch", 14, weight="bold")
    s.text(*P(LATCH_D / 2, LATCH_U0 + LATCH_W / 2 + 2.2), "zone", 14, weight="bold")
    lx, ly = P(-CH_D + STRIP[3] / 2, STRIP[1])
    tx, ty = P(fr - 6, 40)
    s.line(lx, ly, tx - 4, ty - 4, "#8a6a00", 1)
    s.text(tx, ty, "Soft foam strip", 13, "start", "#8a6a00")
    s.text(tx, ty + 16, "(at the floor only)", 13, "start", "#8a6a00")
    s.text(*P(BASE + FOAM_W / 2, -50), "&#8593; Outdoor", 22, color="#d8312b", weight="bold")
    s.text(*P(BASE + FOAM_W / 2, 72), "&#8595; Room", 22, color="#1f5fbf", weight="bold")

    # dimensions: sash
    y = P(0, -st)[1]
    s.hdim(P(xs + SASH_THIN, 0)[0], P(xs, 0)[0], y - 60, fmt(SASH_THIN),
           [(P(xs + SASH_THIN, 0)[0], y - 3), (P(xs, 0)[0], y)])
    s.hdim(P(xs + gd, 0)[0], P(xs, 0)[0], P(0, st)[1] + 22, fmt(gd),
           [(P(xs + gd, 0)[0], P(0, gb)[1]), (P(xs, 0)[0], P(0, st)[1])], text_side=-1)
    x = P(xs + SASH_THIN + 24, 0)[0]
    s.vdim(P(0, -st)[1], P(0, st)[1], x, fmt(SASH_T), [(P(sl, 0)[0], P(0, -st)[1]), (P(sl, 0)[0], P(0, st)[1])],
           text_side=-1)
    x = P(xs + gd + 2.5, 0)[0]
    s.vdim(P(0, -gb)[1], P(0, gb)[1], x, f"{fmt(GROOVE[1])} at the bottom",
           [(P(xs + gd, 0)[0], P(0, -gb)[1]), (P(xs + gd, 0)[0], P(0, gb)[1])], text_side=-1)
    x = P(xs - 4, 0)[0]
    s.vdim(P(0, -gm)[1], P(0, gm)[1], x, f"{fmt(GROOVE[0])} at the mouth",
           [(P(xs, 0)[0], P(0, -gm)[1]), (P(xs, 0)[0], P(0, gm)[1])])

    # dimensions: foam, and the caps' bases on either side
    y = P(0, -FOAM_T / 2)[1]
    yd = P(0, -34)[1]
    s.hdim(P(BASE + FOAM_W, 0)[0], P(BASE, 0)[0], yd, f"{FOAM_W:.0f} foam",
           [(P(BASE + FOAM_W, 0)[0], y), (P(BASE, 0)[0], y)])
    s.hdim(P(xs, 0)[0], P(BASE + FOAM_W, 0)[0], yd, f"{BASE:.0f} cap", [(P(xs, 0)[0], P(0, -st)[1])],
           text_side=-1)
    s.hdim(P(BASE, 0)[0], P(0, 0)[0], yd, f"{BASE:.0f} cap", [(P(0, 0)[0], P(0, -42)[1])])
    x = P(BASE + FOAM_W / 2 + 14, 0)[0]
    s.vdim(P(0, -FOAM_T / 2)[1], P(0, FOAM_T / 2)[1], x, f"{FOAM_T} (2 in)")

    # dimensions: side frame
    x = P(fr - 10, 0)[0]
    s.vdim(P(0, 0)[1], P(0, CH_W / 2)[1], x, fmt(CH_W / 2), [(P(fr - 6, 0)[0], P(0, 0)[1])])
    x = P(fr - 32, 0)[0]
    s.vdim(P(0, -CH_W / 2)[1], P(0, CH_W / 2)[1], x, fmt(CH_W),
           [(P(-CH_D, 0)[0], P(0, -CH_W / 2)[1]), (P(-CH_D, 0)[0], P(0, CH_W / 2)[1])])
    s.hdim(P(-CH_D, 0)[0], P(0, 0)[0], P(0, 9)[1], fmt(CH_D))
    s.hdim(P(-CH_D, 0)[0], P(-CH_D + STRIP[3], 0)[0], P(0, -9)[1], f"{STRIP[3]:.1f}",
           [(P(-CH_D + STRIP[3], 0)[0], P(0, STRIP[0])[1])])
    x = P(-CH_D - 5, 0)[0]
    s.vdim(P(0, STRIP[0])[1], P(0, STRIP[1])[1], x, f"{STRIP[1] - STRIP[0]:.1f}",
           [(P(-CH_D, 0)[0], P(0, STRIP[0])[1]), (P(-CH_D, 0)[0], P(0, STRIP[1])[1])])

    # dimensions: latch zone
    x = P(LATCH_D + 8, 0)[0]
    s.vdim(P(0, CH_W / 2)[1], P(0, LATCH_U0)[1], x, fmt(LATCH_U0 - CH_W / 2),
           [(P(0, 0)[0], P(0, CH_W / 2)[1]), (P(LATCH_D, 0)[0], P(0, LATCH_U0)[1])], text_side=-1)
    s.vdim(P(0, LATCH_U0)[1], P(0, LATCH_U0 + LATCH_W)[1], x, f"{LATCH_W:.1f}",
           [(P(LATCH_D, 0)[0], P(0, LATCH_U0 + LATCH_W)[1])], text_side=-1)
    y = P(0, LATCH_U0 + LATCH_W)[1]
    s.hdim(P(LATCH_D, 0)[0], P(0, 0)[0], y + 22, f"{LATCH_D:.1f}", [(P(LATCH_D, 0)[0], y)])

    s.text(40, 44, "TOP VIEW: section through the window at mid-height, seen from above (mm)", 22, "start",
           weight="bold")
    s.text(40, s.h - 72, f"To scale: {K} px per mm in both directions. u = 0 on the foam's centre, the centre of "
           f"the side frame's 25.90 channel. The caps' 3 mm bases set the sash {xs:g} from the side frame.", 14,
           "start", "#333")
    s.text(40, s.h - 50, "The latch zone spans 80 mm of height (see the side view); the soft foam strip is only at "
           "the floor, 19 high; another, 1.7 thick, lies across the channel's floor, also 4.0 deep.", 14, "start", "#333")
    s.text(40, s.h - 28, f"Dashed in the sash's groove: the screw heads, {fmt(SCREW[0])} high, only within "
           f"{SCREW[1]:.0f} of the sash's top and bottom.", 14, "start", "#333")
    s.save(OUT_TOP)


# =================================== SIDE VIEW ===================================
# u across (outdoor on the left), z up; three height ranges shown, with breaks in between
def side_view():
    segs = [(H - 46, H + 10), (470, 618), (-10, 46)]   # top to bottom of the page
    GAP = 46
    X0, YT = 600, 150                                  # canvas x of u = 0; canvas y of the first range's top
    tops = []
    y = YT
    for lo, hi in segs:
        tops.append(y)
        y += (hi - lo) * K + GAP
    s = Svg(1340, int(y - GAP + 230))

    def Z(z):
        for (lo, hi), t in zip(segs, tops):
            if lo - 1e-6 <= z <= hi + 1e-6:
                return t + (hi - z) * K
        raise ValueError(z)

    def U(u):
        return X0 + u * K

    def box(u1, u2, z1, z2, *a, **k):
        s.rect(U(u1), Z(z1), U(u2), Z(z2), *a, **k)

    UL, UR = -50, 64
    # sash channel band (where the sash runs), then the frames
    box(-CH_W / 2, CH_W / 2, H - CAP_TOP, H, C_BAND, "none")
    box(-CH_W / 2, CH_W / 2, 0, CAP_BOT, C_BAND, "none")
    box(UL, UR, H, H + 10, C_FRAME)
    for a, b, d in TOP_RIBS:
        box(a, b, H - d, H + 0.1, C_FRAME)
    box(UL, UR, -10, 0, C_FRAME)
    box(-CH_W / 2, CH_W / 2, 0, FLOOR_STRIP, C_STRIP)   # on the channel's floor at its back, under the rails
    box(STRIP[0], STRIP[1], 0, STRIP[2], C_STRIP)
    for a, b, h in BOT_RIBS:
        box(a, b, -0.1, h, C_FRAME)
    for z1, z2 in ((H, H + 10), (-10, 0)):             # cut ends of the frames, across their slabs
        s.zigzag_v(U(UL), Z(z2) - 8, Z(z1) + 8)
        s.zigzag_v(U(UR), Z(z2) - 8, Z(z1) + 8)

    # foam, in its three ranges, with breaks
    f0, f1 = -FOAM_T / 2, FOAM_T / 2
    box(f0, f1, H - 46, H - CAP_TOP, C_FOAM)
    box(f0, f1, 470, 618, C_FOAM)
    box(f0, f1, CAP_BOT, 46, C_FOAM)
    for a, b in ((STRIP[0], STRIP[0]), (STRIP[1], STRIP[1]), (STRIP[0], STRIP[1])):   # the strip, hidden by the foam
        za = CAP_BOT if a == b else STRIP[2]
        s.line(U(a), Z(za), U(b), Z(STRIP[2]), "#8a6a00", 1.5, "4,3")
    box(LATCH_U0, LATCH_U0 + LATCH_W, LATCH_Z0, LATCH_Z0 + LATCH_H, C_LATCH, "#9a8f00", 1.5, "6,3", 0.85)
    for zz in (H - 46, 618, 470, 46):
        s.zigzag_h(U(f0) - 14, U(f1) + 14, Z(zz))

    # centre line
    for (lo, hi), t in zip(segs, tops):
        s.line(U(0), t - 6, U(0), t + (hi - lo) * K + 6, "#777", 1, "14,4,3,4")

    # labels
    s.text(U(UR) + 24, Z(H + 5) + 5, "Window top frame", 16, "start", weight="bold")
    s.text(U(UR) + 24, Z(-5) + 5, "Window bottom frame", 16, "start", weight="bold")
    s.text(U(0), Z(560), "XPS foam", 17, weight="bold")
    s.text(U(LATCH_U0 + LATCH_W / 2), Z(LATCH_Z0 + LATCH_H / 2) - 2, "Window latch", 14, weight="bold")
    s.text(U(LATCH_U0 + LATCH_W / 2), Z(LATCH_Z0 + LATCH_H / 2) + 16, "zone", 14, weight="bold")
    s.text(U(UL) - 10, Z(560), "&#8592; Outdoor", 22, "end", "#d8312b", "bold")
    s.text(U(UR) + 150, Z(560), "Room &#8594;", 22, "start", "#1f5fbf", "bold")
    s.text(U(0), Z(-10) + 84, "foam centre", 13, color="#555")
    lx, ly = U(-3.0), Z(CAP_BOT - 1.75)             # its visible part, under the foam and above the rail
    s.path(f"M{U(UL) - 8:.1f},{Z(36):.1f} L{lx:.1f},{Z(36):.1f} L{lx:.1f},{ly:.1f}", "#8a6a00", 1)
    s.text(U(UL) - 12, Z(36) - 4, "Soft foam strip around the rail", 13, "end", "#8a6a00")
    s.text(U(UL) - 12, Z(36) + 12, "(only at the side frame, 4 deep)", 13, "end", "#8a6a00")
    lx, ly = U(-9.0), Z(FLOOR_STRIP / 2)            # across the channel
    s.path(f"M{U(UL) - 8:.1f},{Z(36) + 40:.1f} L{lx:.1f},{Z(36) + 40:.1f} L{lx:.1f},{ly:.1f}", "#8a6a00", 1)
    s.text(U(UL) - 12, Z(36) + 44, "Soft foam strip on the channel's floor", 13, "end", "#8a6a00")
    s.text(U(UL) - 12, Z(36) + 60, f"({FLOOR_STRIP} thick, {STRIP[3]:.1f} deep, at the side frame)", 13, "end", "#8a6a00")

    # dimensions: top frame (chain above, depths beside)
    pts = [TOP_RIBS[0][0], TOP_RIBS[0][1], TOP_RIBS[1][0], TOP_RIBS[1][1], TOP_RIBS[2][0], TOP_RIBS[2][1]]
    yc = Z(H + 10) - 30
    for a, b in zip(pts, pts[1:]):
        s.hdim(U(a), U(b), yc, fmt(b - a), [(U(a), Z(H + 10)), (U(b), Z(H + 10))])
    for (a, b, d), (ux, side) in zip(TOP_RIBS, [(a - 3, -1) for a, _, _ in TOP_RIBS[:2]] + [(TOP_RIBS[2][1] + 3, 1)]):
        s.vdim(Z(H), Z(H - d), U(ux), fmt(d), [(U(b if side > 0 else a), Z(H - d))], text_side=side)
    yb = Z(H - CAP_TOP) + 26
    s.hdim(U(-CH_W / 2), U(CH_W / 2), yb, f"{fmt(CH_W)} sash channel", [(U(-CH_W / 2), Z(H - CAP_TOP))])
    s.hdim(U(0), U(CH_W / 2), yb + 32, fmt(CH_W / 2), [(U(CH_W / 2), Z(H - CAP_TOP))])
    s.hdim(U(CH_W / 2), U(TOP_RIBS[2][0]), yb + 64, fmt(TOP_RIBS[2][0] - CH_W / 2),
           [(U(TOP_RIBS[2][0]), Z(H - TOP_RIBS[2][2]))])

    # dimensions: bottom frame
    pts = [BOT_RIBS[0][0], BOT_RIBS[0][1], BOT_RIBS[1][0], BOT_RIBS[1][1], BOT_RIBS[2][0], BOT_RIBS[2][1]]
    yc = Z(-10) + 30
    for a, b in zip(pts, pts[1:]):
        s.hdim(U(a), U(b), yc, fmt(b - a), [(U(a), Z(-10)), (U(b), Z(-10))])
    s.vdim(Z(0), Z(BOT_RIBS[0][2]), U(BOT_RIBS[0][1] + 3), fmt(BOT_RIBS[0][2]), [(U(BOT_RIBS[0][1]), Z(BOT_RIBS[0][2]))])
    s.vdim(Z(0), Z(STRIP[2]), U(-CH_W / 2 - 3), f"{STRIP[2]:.1f}", [(U(STRIP[0]), Z(STRIP[2]))], text_side=-1)
    s.vdim(Z(0), Z(BOT_RIBS[1][2]), U(BOT_RIBS[1][1] + 3), fmt(BOT_RIBS[1][2]), [(U(STRIP[1]), Z(BOT_RIBS[1][2]))])
    s.vdim(Z(0), Z(BOT_RIBS[2][2]), U(BOT_RIBS[2][1] + 3), fmt(BOT_RIBS[2][2]), [(U(BOT_RIBS[2][1]), Z(BOT_RIBS[2][2]))])
    yb = Z(CAP_BOT) - 66
    s.hdim(U(-CH_W / 2), U(CH_W / 2), yb, f"{fmt(CH_W)} sash channel", [(U(-CH_W / 2), Z(CAP_BOT))])

    # dimensions: foam and latch (middle range)
    s.hdim(U(f0), U(f1), Z(480), f"{FOAM_T} (2 in)")
    s.hdim(U(f0), U(0), Z(493), f"{FOAM_T / 2}")
    s.hdim(U(LATCH_U0), U(LATCH_U0 + LATCH_W), Z(LATCH_Z0 + LATCH_H) - 22, f"{LATCH_W:.1f}",
           [(U(LATCH_U0), Z(LATCH_Z0 + LATCH_H)), (U(LATCH_U0 + LATCH_W), Z(LATCH_Z0 + LATCH_H))])
    xr = U(LATCH_U0 + LATCH_W) + 26
    s.vdim(Z(LATCH_Z0), Z(LATCH_Z0 + LATCH_H), xr, f"{LATCH_H:.1f}",
           [(U(LATCH_U0 + LATCH_W), Z(LATCH_Z0)), (U(LATCH_U0 + LATCH_W), Z(LATCH_Z0 + LATCH_H))])

    # long heights, across the breaks
    xr = U(UR) + 40
    tip_top, tip_bot = Z(H - TOP_RIBS[1][2]), Z(BOT_RIBS[1][2])
    s.line(U(TOP_RIBS[1][1]) + 4, tip_top, xr + 76, tip_top, C_DIM, 1, "3,3")
    s.line(U(BOT_RIBS[2][1]) + 4, tip_bot, xr + 76, tip_bot, C_DIM, 1, "3,3")
    s.vdim(Z(LATCH_Z0), tip_bot, xr, "495.0", [(U(LATCH_U0 + LATCH_W) + 30, Z(LATCH_Z0))])
    s.vdim(tip_top, tip_bot, xr + 70, f"{TIP:.1f} rib tip to rail tip")
    s.text(xr + 78, (tip_top + tip_bot) / 2 + 24, f"(ceiling to floor {H:.1f})", 13, "start", C_DIM)

    s.text(40, 44, "SIDE VIEW: section across the foam, at the side frame (mm)", 22, "start", weight="bold")
    s.text(40, 72, "Heights broken twice: the foam runs on between the breaks.", 14, "start", "#333")
    s.text(40, s.h - 72, f"To scale: {K} px per mm in both directions. u = 0 on the foam's centre, the centre of the "
           "side frame's 25.90 channel.", 14, "start", "#333")
    s.text(40, s.h - 50, "The top room-side rib sits 1.5 mm further toward the room than the bottom one (measured "
           "twice). The centre rib and rail", 14, "start", "#333")
    s.text(40, s.h - 28, f"run on through the side frame's channel to its back wall. The caps put the foam "
           f"{CAP_TOP:g} below the ceiling and {CAP_BOT:g} above the floor.", 14, "start", "#333")
    s.save(OUT_SIDE)



# ================================ INSERT WIDTH ================================
# the same top view, simplified: the caps' sections and the vent's chassis, with the chain of widths across
def width_view():
    xs = BASE + FOAM_W + BASE                   # the sash's end face
    X0, Y0 = 1290, 400                          # canvas position of x = 0, u = 0
    s = Svg(1560, 1010)
    C_SIDE, C_SASH, C_VENT = "#8fb3e8", "#9bd4a9", "#5b5b5b"

    def P(x, u):
        return X0 - x * K, Y0 + u * K

    def box(x1, u1, x2, u2, fill, **k):
        s.rect(*P(x1, u1), *P(x2, u2), fill, **k)

    fw, ow = FOAM_T / 2 + FOAM_CLR, FOAM_T / 2 + FOAM_CLR + LIP_T
    sl = xs + SASH_THIN + 14                    # where the sash is cut off
    fr = -30                                    # where the side frame is cut off
    st = SASH_T / 2
    tw, td = CH_W / 2 - 0.3, CH_D - 0.5         # the side cap's tongue

    # window: side frame with its channel (right), the sash's end (left)
    s.poly([P(0, -42), P(0, -CH_W / 2), P(-CH_D, -CH_W / 2), P(-CH_D, CH_W / 2), P(0, CH_W / 2), P(0, 42),
            P(fr, 42), P(fr, -42)], C_FRAME)
    s.zigzag_v(P(fr, 0)[0], P(0, -42)[1] - 12, P(0, 42)[1] + 12)
    s.poly([P(xs, -st), P(sl, -st), P(sl, st), P(xs, st)], C_FRAME)
    s.zigzag_v(P(sl, 0)[0], P(0, -st)[1] - 12, P(0, st)[1] + 12)

    # foam, then the caps: side cap (tongue, base, lips), sash cap (base, lips, walls along the sash)
    box(BASE, -FOAM_T / 2, BASE + FOAM_W, FOAM_T / 2, C_FOAM)
    box(-td, -tw, 0, tw, C_SIDE)
    box(0, -ow, BASE, ow, C_SIDE)
    box(xs - BASE, -ow, xs, ow, C_SASH)
    for a, b in ((-ow, -fw), (fw, ow)):
        box(BASE, a, BASE + LIP_D, b, C_SIDE)
        box(xs - BASE - LIP_D, a, xs - BASE, b, C_SASH)
    for a, b in ((-ow, -st - 0.3), (st + 0.3, ow)):
        box(xs, a, xs + 10.7, b, C_SASH)

    # the vent's chassis on the room face, centred between the lips
    xc = BASE + FOAM_W / 2
    v0, v1 = xc - CHASSIS_W / 2, xc + CHASSIS_W / 2
    box(v0, FOAM_T / 2, v1, FOAM_T / 2 + 22, "#f2f2f2", stroke=C_VENT, width=1.5, dash="7,4")

    # labels
    s.text(*P(xc, -6), "XPS foam", 17, weight="bold")
    s.text(*P(xc, FOAM_T / 2 + 14), f"Vent chassis (at least {CHASSIS_W:g} wide)", 15, color=C_VENT, weight="bold")
    s.text(*P(xc, -41), "&#8593; Outdoor", 20, color="#d8312b", weight="bold")
    s.text(P(sl, 0)[0] + 4, P(0, -st)[1] - 14, "Sash", 15, "start", weight="bold")
    s.text(P(fr / 2, 0)[0], P(0, -42)[1] - 14, "Side frame", 15, weight="bold")
    for x, name in ((BASE / 2, "Side cap"), (xs - BASE / 2, "Sash cap")):   # in their bases
        s.text(P(x, 0)[0] + 5, P(x, 0)[1], name, 14, weight="bold", rotate=-90)
    s.text(*P(xs + 22, FOAM_T / 2 + 14), "&#8595; Room", 20, color="#1f5fbf", weight="bold")

    # dimensions, room side: the chain across, the chassis' margins, the total
    yl = P(0, ow)[1]
    chain = [0, BASE, BASE + LIP_D, xs - BASE - LIP_D, xs - BASE, xs]
    names = [f"{BASE:g} base", f"{LIP_D:g} lip", f"{FOAM_W - 2 * LIP_D:g} uncovered foam", f"{LIP_D:g} lip",
             f"{BASE:g} base"]
    yc = P(0, FOAM_T / 2 + 36)[1]
    for (a, b), name, side in zip(zip(chain, chain[1:]), names, (1, 1, 1, -1, -1)):
        s.hdim(P(b, 0)[0], P(a, 0)[0], yc, name, [(P(a, 0)[0], yl), (P(b, 0)[0], yl)], text_side=side)
    ym = P(0, FOAM_T / 2 + 28)[1]
    s.hdim(P(v0, 0)[0], P(BASE + LIP_D, 0)[0], ym, fmt((FOAM_W - 2 * LIP_D - CHASSIS_W) / 2).rstrip("0").rstrip("."),
           [(P(v0, 0)[0], P(0, FOAM_T / 2 + 22)[1])], text_side=1)
    s.hdim(P(xs - BASE - LIP_D, 0)[0], P(v1, 0)[0], ym, fmt((FOAM_W - 2 * LIP_D - CHASSIS_W) / 2).rstrip("0").rstrip("."),
           [(P(v1, 0)[0], P(0, FOAM_T / 2 + 22)[1])], text_side=-1)
    yt = P(0, FOAM_T / 2 + 48)[1]
    s.hdim(P(xs, 0)[0], P(0, 0)[0], yt, f"{xs:g} side frame to sash (the top and bottom caps' length)",
           [(P(xs, 0)[0], yc + 6), (P(0, 0)[0], yc + 6)])

    # dimensions, outdoor side: the foam's width
    yf = P(0, -FOAM_T / 2 - 10)[1]
    s.hdim(P(BASE + FOAM_W, 0)[0], P(BASE, 0)[0], yf, f"{FOAM_W:g} foam",
           [(P(BASE + FOAM_W, 0)[0], P(0, -ow)[1]), (P(BASE, 0)[0], P(0, -ow)[1])])

    s.text(40, 40, "INSERT WIDTH: the foam and its caps across the window, seen from above (mm)", 22, "start",
           weight="bold")
    s.text(40, s.h - 50, f"To scale: {K} px per mm. Section at mid-height, room at the bottom. The lips are "
           f"{LIP_T:g} thick, with {FOAM_CLR:g} clearance to the foam; the top and bottom caps' lips reach", 14,
           "start", "#333")
    s.text(40, s.h - 28, f"{LIP_D:g} onto the foam the same way. The vent's chassis fits between the lips with "
           f"{(FOAM_W - 2 * LIP_D - CHASSIS_W) / 2:g} to spare on each side.", 14, "start", "#333")
    s.save(OUT_WIDTH)


top_view()
side_view()
width_view()
