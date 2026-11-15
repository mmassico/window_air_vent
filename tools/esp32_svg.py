#!/usr/bin/env python3
"""Draw the ESP32-S3 boards, dimensioned from measurements:
doc/esp32_s3.svg (the Freenove ESP32-S3-WROOM Lite, FNK0099) and doc/esp32_s3_n16r8.svg (the ESP32-S3-N16R8
board in the DevKitC-1 layout, with a U.FL socket for an external antenna).

Usage: python tools/esp32_svg.py   (run from the window-vent folder)
Top view, components up, USB end at the bottom (as on the silkscreen); dimensions in mm.
"""
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PITCH = 2.54
K = 13                       # px per mm
OX, OY = 300, 260            # canvas position of the PCB's top-left corner
C_DIM = "#b3261e"

FREENOVE = dict(
    out="esp32_s3.svg", W=1640, H=1200,
    title="Freenove ESP32-S3-WROOM Lite (FNK0099): top view, components up, and side view (mm)",
    PW=28.5, PL=50.0,            # PCB width, length
    ANT_W=18.5, ANT_L=7.0,       # module antenna beyond the PCB (5 mm from each side edge)
    MOD_L=25.5,                  # ESP32-S3-WROOM-1 module length (datasheet), so 18.5 of it on the PCB
    module="ESP32-S3-WROOM-1", ufl=False,
    pcb="#d8453a", pcb_stroke="#222", ant="#2a2a2a",
    OTG_X=4.25, UART_X=3.75, USB_W=9.0,   # USB-C: OTG from the left edge, UART from the right edge, width
    ROW=25.3,                    # header rows, centre to centre (measured 25.25-25.3: 10 holes on a 2.54 perfboard)
    row_label="25.3 between the pin rows: 10 perfboard holes",
    LEFT=["3V3", "EN", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46", "9", "10", "11", "12", "13", "14", "5V"],
    RIGHT=["TX", "RX", "1", "2", "42", "41", "40", "39", "38", "37", "36", "35", "0", "45", "48", "47", "21", "20", "19",
           "GND"],
    side=dict(PCB_T=1.62, SPACER=2.78, PIN_BELOW=5.54,   # side view (measured)
              TOP_H=4.85, USB_H=3.25),   # tallest part above the PCB's underside; USB-C socket height above the PCB
    notes=["Measured on the board. 2 x 20 pins, 2.54 pitch; the rows land 10 holes apart on a perfboard (25.4, within 0.1).",
           "Side view: 5.54 pins below a 2.78 spacer, 1.62 PCB; the tallest part is 4.85 above the PCB's underside, the USB-C sockets 3.25 above its top.",
           "In the electronics box, the USB end faces the left wall (or the right one, board turned 180 deg); plug the USB-UART connector (power and console)."],
)

N16R8 = dict(
    out="esp32_s3_n16r8.svg", W=1180, H=1300,
    title="ESP32-S3-N16R8 board (DevKitC-1 layout, U.FL antenna): top view, components up (mm)",
    PW=28.5, PL=56.9,
    ANT_W=18.0, ANT_L=6.5,
    MOD_L=25.5,
    module="ESP32-S3-N16R8", ufl=True, halo=True,   # halo: pin labels readable over the USB-C sockets
    usb_alias=("USB", "COM"),    # the board's own silkscreen names for USB-OTG and USB-UART
    pcb="#1c1c1e", pcb_stroke="#000", ant="#3a3a3c",
    OTG_X=4.25, UART_X=3.75, USB_W=9.0,   # measured: at the same places as on the Freenove board
    ROW=25.35,                   # measured about 25.35, as the Freenove's: on the 25.4 grid on the v2.0 PCB
    row_label="25.35 between the pin rows (25.4 on the PCB)",
    LEFT=["3V3", "3V3", "RST", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46", "9", "10", "11", "12", "13",
          "14", "5V", "GND"],
    RIGHT=["GND", "TX", "RX", "1", "2", "42", "41", "40", "39", "38", "37", "36", "35", "0", "45", "48", "47", "21",
           "20", "19", "GND", "GND"],
    side=None,
    notes=["Measured on the board. 2 x 22 pins, 2.54 pitch; the 20 inner pins of each row are the Freenove's (the v2.0 PCB takes both boards).",
           "U.FL socket on the module, for the external antenna's pigtail (15 cm, to the SMA jack in the electronics box's wall).",
           "The USB-C sockets are at the same places as on the Freenove board and are the tallest parts; nothing on the underside.",
           "In the electronics box, plug the USB-UART connector, marked COM on this board (power and console)."],
)


def draw(b):
    PW, PL, ANT_W, ANT_L, MOD_L = b["PW"], b["PL"], b["ANT_W"], b["ANT_L"], b["MOD_L"]
    OTG_X, UART_X, USB_W = b["OTG_X"], b["UART_X"], b["USB_W"]
    LEFT, RIGHT, W, H = b["LEFT"], b["RIGHT"], b["W"], b["H"]
    n = len(LEFT)
    out = []

    def px(x, y):
        return OX + x * K, OY + y * K

    def text(x, y, s, size=15, anchor="middle", color="#111", weight="normal", rotate=None, halo=False):
        tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
        hl = ' stroke="#ffffff" stroke-width="3" paint-order="stroke"' if halo else ""
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
                   f'font-weight="{weight}"{hl}{tr}>{s}</text>')

    def line(x1, y1, x2, y2, color="#111", width=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d}/>')

    def arrow(x, y, dx, dy, color):
        n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
        a, c = 10, 4
        p1 = (x - ux * a - uy * c, y - uy * a + ux * c)
        p2 = (x - ux * a + uy * c, y - uy * a - ux * c)
        out.append(f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')

    def hdim(x1, x2, y, ext_y, label, color=C_DIM):
        """horizontal dimension between x1 and x2 (mm) at canvas y; extension lines from board y = ext_y (mm)"""
        (a, ey), (c, _) = px(x1, ext_y), px(x2, ext_y)
        line(a, ey, a, y + (6 if y > ey else -6), color, 1, "3,3"); line(c, ey, c, y + (6 if y > ey else -6), color, 1, "3,3")
        line(a, y, c, y, color, 1.5); arrow(a, y, -1, 0, color); arrow(c, y, 1, 0, color)
        text((a + c) / 2, y - 7, label, 15, color=color)

    def vdim(y1, y2, x, ext_x, label, color=C_DIM):
        """vertical dimension between y1 and y2 (mm) at canvas x; extension lines from board x = ext_x (mm)"""
        (ex, a), (_, c) = px(ext_x, y1), px(ext_x, y2)
        line(ex, a, x + (6 if x > ex else -6), a, color, 1, "3,3"); line(ex, c, x + (6 if x > ex else -6), c, color, 1, "3,3")
        line(x, a, x, c, color, 1.5); arrow(x, a, 0, -1, color); arrow(x, c, 0, 1, color)
        text(x - 8, (a + c) / 2, label, 15, color=color, rotate=-90)

    # --- PCB, module, antenna ----------------------------------------------------------------------
    x0, y0 = px(0, 0)
    out.append(f'<rect x="{x0}" y="{y0}" width="{PW * K}" height="{PL * K}" rx="6" fill="{b["pcb"]}" '
               f'stroke="{b["pcb_stroke"]}" stroke-width="2"/>')
    am = (PW - ANT_W) / 2
    a, c = px(am, -ANT_L)
    out.append(f'<rect x="{a}" y="{c}" width="{ANT_W * K}" height="{MOD_L * K}" rx="3" fill="{b["ant"]}" stroke="#111" stroke-width="1.5"/>')
    a, c = px(am + 1, MOD_L - ANT_L - 18)
    out.append(f'<rect x="{a}" y="{c}" width="{(ANT_W - 2) * K}" height="{17 * K}" rx="3" fill="#c9cbcf" stroke="#888"/>')
    text(*px(PW / 2, MOD_L - ANT_L - 9), b["module"], 15, color="#333", weight="bold")
    text(*px(PW / 2, -ANT_L / 2 + 0.6), "antenna", 14, color="#ffffff")
    if b["ufl"]:                     # U.FL socket, on the module's antenna end, right side (as on the board)
        ux, uy = PW / 2 + ANT_W / 2 - 4.2, MOD_L - ANT_L - 18 - 0.2
        a, c = px(ux, uy - 1.6)
        out.append(f'<rect x="{a:.1f}" y="{c:.1f}" width="{3 * K}" height="{3 * K}" rx="2" fill="#e8c766" stroke="#7a5c00" stroke-width="1.2"/>')
        cx, cy = px(ux + 1.5, uy - 0.1)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.9 * K:.1f}" fill="#d9d9d9" stroke="#7a5c00"/>')
        text(*px(ux - 0.6, uy - 0.2), "U.FL (IPEX)", 14, "end", "#ffffff", "bold")

    # USB-C connectors
    for x, lab in ((OTG_X, "USB-OTG"), (PW - UART_X - USB_W, "USB-UART")):
        a, c = px(x, PL - 7.5)
        out.append(f'<rect x="{a}" y="{c}" width="{USB_W * K}" height="{7.5 * K}" rx="5" fill="#c0c0c0" stroke="#555" stroke-width="1.5"/>')
        text(*px(x + USB_W / 2, PL + 3.2), lab, 15, weight="bold")
    for x, lab in zip((OTG_X, PW - UART_X - USB_W), b.get("usb_alias", ())):
        text(*px(x + USB_W / 2, PL + 4.6), f"({lab})", 14, color="#444")

    # header pins and labels
    r1 = (PW - b["ROW"]) / 2
    first = (PL - (n - 1) * PITCH) / 2
    for col, labels, side in ((r1, LEFT, -1), (PW - r1, RIGHT, 1)):
        for i, lab in enumerate(labels):
            cx, cy = px(col, first + i * PITCH)
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.75 * K}" fill="#f4d35e" stroke="#7a5c00"/>')
            over_usb = first + i * PITCH > PL - 7.5           # labels over a USB-C connector: dark text
            text(cx - side * 1.2 * K, cy + 5, lab, 12, "end" if side > 0 else "start", "#111" if over_usb else "#ffffff", "bold",
                 halo=over_usb and b.get("halo", False))

    # --- dimensions ---------------------------------------------------------------------------------
    top = OY - ANT_L * K
    hdim(0, PW, top - 70, 0, f"{PW}")
    hdim(0, am, top - 25, 0, f"{am:g}")
    hdim(PW - am, PW, top - 25, 0, f"{am:g}")
    vdim(-ANT_L, PL, OX - 60, 0, f"{PL + ANT_L:g}")
    vdim(0, PL, OX + PW * K + 110, PW, f"{PL:g} (PCB)")
    vdim(-ANT_L, 0, OX + PW * K + 60, PW / 2 + ANT_W / 2, f"{ANT_L:g}")
    if not b["side"]:               # end pins to the PCB's ends (the Freenove's are in its notes)
        vdim(PL - first, PL, OX + PW * K + 60, PW - r1, f"{first:.2f}")
    bot = OY + PL * K + 70
    hdim(0, OTG_X, bot, PL, f"{OTG_X}")
    hdim(OTG_X, OTG_X + USB_W, bot + 40, PL, f"{USB_W:g}")
    hdim(PW - UART_X - USB_W, PW - UART_X, bot + 40, PL, f"{USB_W:g}")
    hdim(PW - UART_X, PW, bot, PL, f"{UART_X}")
    hdim(r1, PW - r1, bot + 90, PL - first, b["row_label"])

    text(40, 50, b["title"], 22, "start", weight="bold")

    # --- side view (seen from the USB end), to the right ------------------------------------------
    s = b["side"]
    if s:
        PCB_T, SPACER, PIN_BELOW, TOP_H, USB_H = s["PCB_T"], s["SPACER"], s["PIN_BELOW"], s["TOP_H"], s["USB_H"]
        SX, SY, SK = 960, 640, 16      # left end of the PCB's underside on the canvas, scale

        def sp(x, z):                  # side-view mm -> canvas (z up, 0 = PCB underside)
            return SX + x * SK, SY - z * SK

        def srect(x0, z0, x1, z1, fill, stroke="#222"):
            a, c = sp(x0, z1)
            out.append(f'<rect x="{a:.1f}" y="{c:.1f}" width="{(x1 - x0) * SK:.1f}" height="{(z1 - z0) * SK:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        srect(0, 0, PW, PCB_T, b["pcb"])                                              # PCB
        for col in (r1, PW - r1):
            srect(col - 1.25, -SPACER, col + 1.25, 0, "#555")                        # plastic spacer
            srect(col - 0.32, -SPACER - PIN_BELOW, col + 0.32, -SPACER, "#f4d35e")  # pin
            srect(col - 0.32, PCB_T, col + 0.32, PCB_T + 1.0, "#f4d35e")           # pin tip above
        for x in (OTG_X, PW - UART_X - USB_W):
            srect(x, PCB_T, x + USB_W, PCB_T + USB_H, "#c0c0c0")                     # USB-C sockets
        srect(PW / 2 - 3, PCB_T, PW / 2 + 3, TOP_H, "#33c8d8")                       # tallest part

        def sdim(z0, z1, x, label, ext_x, left=False):
            a, c = sp(x, z0); _, d2 = sp(x, z1); ex, _ = sp(ext_x, 0)
            d = -6 if left else 6
            line(ex, c, a + d, c, C_DIM, 1, "3,3"); line(ex, d2, a + d, d2, C_DIM, 1, "3,3")
            line(a, c, a, d2, C_DIM, 1.5); arrow(a, c, 0, 1, C_DIM); arrow(a, d2, 0, -1, C_DIM)
            text(a - 10 if left else a + 10, (c + d2) / 2 + 5, label, 14, "end" if left else "start", C_DIM)
        sdim(0, PCB_T, PW + 4, f"{PCB_T} PCB", PW)
        sdim(-SPACER, 0, PW + 4, f"{SPACER} spacer", PW)
        sdim(-SPACER - PIN_BELOW, -SPACER, PW + 4, f"{PIN_BELOW} pins", PW)
        sdim(0, TOP_H, -4, f"{TOP_H} to the top", PW / 2 - 3, left=True)
        text(SX, SY - 8 * SK, "Side view, from the USB end", 15, "start", weight="bold")

    notes = b["notes"]
    for i, t in enumerate(notes):
        out.append(f'<text x="40" y="{H - 80 - (len(notes) - 3) * 24 + i * 24}" font-size="14" fill="#333">{t}</text>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
           + "\n".join(out) + "\n</svg>\n")
    path = os.path.join(ROOT, "doc", b["out"])
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("wrote", path)


for board in (FREENOVE, N16R8):
    draw(board)
