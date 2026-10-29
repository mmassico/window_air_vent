#!/usr/bin/env python3
"""Draw firmware/images/wiring.svg: how the peripherals connect to the ESP32-S3 board.

Usage: python tools/wiring_svg.py [out.svg]   (run from the window-vent folder)
Pins follow firmware/baremetal/Pins.h; keep both in step.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "firmware", "images", "wiring.svg")
W, H = 1640, 1480

C_I2C = "#1b7f3b"
C_MOT = "#6a3fb5"
C_FAN = "#c25e00"
C_SNS = "#b3261e"
C_PWR = "#1f5fbf"
C_TMP = "#0b7a75"
C_AUD = "#a0287a"
NET = {"12V": "#b3261e", "3V3": "#d17a00", "5V": "#1f5fbf", "GND": "#333333"}

out = []


def text(x, y, s, size=15, anchor="start", weight="normal", color="#111", italic=False):
    style = ' font-style="italic"' if italic else ""
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
               f'font-weight="{weight}" fill="{color}"{style}>{s}</text>')


def line(pts, color="#111", width=2.5):
    p = " ".join(f"{x},{y}" for x, y in pts)
    out.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{width}" '
               f'stroke-linejoin="round" stroke-linecap="round"/>')


def dot(x, y, color="#111"):
    out.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{color}"/>')


def box(x0, y0, x1, y1, title, sub=None, fill="#f4f6f8"):
    out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="8" '
               f'fill="{fill}" stroke="#222" stroke-width="2"/>')
    text((x0 + x1) / 2, y0 + 22, title, 16, "middle", "bold")
    if sub:
        text((x0 + x1) / 2, y0 + 40, sub, 12.5, "middle", color="#444")


def tag(x, y, net, side):
    """Net label at the end of a lead. side: direction the lead points (left, right, up, down)."""
    c = NET[net]
    w, h = 12 + 9 * len(net), 22
    if side == "left":
        x0, y0 = x - w, y - h / 2
    elif side == "right":
        x0, y0 = x, y - h / 2
    elif side == "up":
        x0, y0 = x - w / 2, y - h
    else:
        x0, y0 = x - w / 2, y
    out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="11" fill="{c}"/>')
    text(x0 + w / 2, y0 + 16, net, 13, "middle", "bold", "#fff")


def lead_tag(x, y, net, side, length=30):
    dx = {"left": -length, "right": length, "up": 0, "down": 0}[side]
    dy = {"left": 0, "right": 0, "up": -length, "down": length}[side]
    line([(x, y), (x + dx, y + dy)], NET[net], 2)
    tag(x + dx, y + dy, net, side)


def resistor(x, y, orient, label, color="#111", length=44):
    """Zigzag resistor starting at (x, y), going right ('h') or down ('v') for 'length' px."""
    n, amp = 6, 7
    pts = [(x, y)]
    for i in range(n):
        t = (i + 0.5) / n * length
        s = amp if i % 2 == 0 else -amp
        pts.append((x + t, y + s) if orient == "h" else (x + s, y + t))
    pts.append((x + length, y) if orient == "h" else (x, y + length))
    line(pts, color, 2)
    if orient == "h":
        text(x + length / 2, y - 12, label, 13, "middle", color="#222")
    else:
        text(x + 12, y + length / 2 + 5, label, 13, color="#222")


def capacitor(x, y, label, length=40):
    """Vertical polarized capacitor from (x, y) downward."""
    mid = y + length / 2
    line([(x, y), (x, mid - 5)], "#111", 2)
    line([(x - 14, mid - 5), (x + 14, mid - 5)], "#111", 3)
    line([(x - 14, mid + 5), (x + 14, mid + 5)], "#111", 3)
    line([(x, mid + 5), (x, y + length)], "#111", 2)
    text(x - 22, mid - 8, "+", 13, "middle")
    text(x + 20, mid + 5, label, 13)


def pull(x, y, net, label, up, color):
    """Pull resistor from a wire at (x, y) to a net, going up or down."""
    dot(x, y, color)
    if up:
        line([(x, y), (x, y - 12)], color, 2)
        resistor(x, y - 56, "v", label, length=44)
        tag(x, y - 56, net, "up")
    else:
        line([(x, y), (x, y + 12)], color, 2)
        resistor(x, y + 12, "v", label, length=44)
        tag(x, y + 56, net, "down")


# ---------------------------------------------------------------------------------------------
# ESP32 board
# ---------------------------------------------------------------------------------------------
EX0, EX1, EY0, EY1 = 640, 900, 150, 1200
box(EX0, EY0, EX1, EY1, "ESP32-S3", "Freenove WROOM Lite (FNK0099)", "#e8eef7")
text((EX0 + EX1) / 2, 705, "USB-UART connector", 13, "middle", "bold")
text((EX0 + EX1) / 2, 723, "to the PC: flashing + console", 12.5, "middle", color="#444")


def esp_left(y, label, color):
    text(EX0 + 10, y + 5, label, 14)
    return (EX0, y)


def esp_right(y, label, color):
    text(EX1 - 10, y + 5, label, 14, "end")
    return (EX1, y)


# Power pins on top of the board.
for x, lab in ((770, "3V3"), (840, "GND")):
    text(x, EY0 + 62, lab, 13, "middle", "bold")
lead_tag(770, EY0, "3V3", "up", 26)
lead_tag(840, EY0, "GND", "up", 26)

# ---------------------------------------------------------------------------------------------
# Left side: sensors, 12 V sense, fans
# ---------------------------------------------------------------------------------------------
PX0, PX1 = 150, 330


def periph_pin_r(y, label):
    text(PX1 - 10, y + 5, label, 14, "end")


def periph_pin_l(y, label, net):
    text(PX0 + 10, y + 5, label, 14)
    lead_tag(PX0, y, net, "left", 26)


# SCD40
box(PX0, 200, PX1, 330, "SCD40", "CO2 sensor, I2C 0x62")
periph_pin_l(260, "VDD", "3V3")
periph_pin_l(300, "GND", "GND")
periph_pin_r(260, "SDA")
periph_pin_r(300, "SCL")
line([(PX1, 260), esp_left(260, "GPIO 8  SDA0", C_I2C)], C_I2C)
line([(PX1, 300), esp_left(300, "GPIO 9  SCL0", C_I2C)], C_I2C)
text(485, 330, "1-2 m cable, 100 kHz", 12.5, "middle", color=C_I2C, italic=True)

# AS5600
box(PX0, 370, PX1, 520, "AS5600", "encoder, I2C 0x36")
periph_pin_l(425, "VCC", "3V3")
periph_pin_l(460, "GND", "GND")
periph_pin_l(495, "DIR", "GND")
periph_pin_r(425, "SDA")
periph_pin_r(460, "SCL")
line([(PX1, 425), esp_left(425, "GPIO 6  SDA1", C_I2C)], C_I2C)
line([(PX1, 460), esp_left(460, "GPIO 7  SCL1", C_I2C)], C_I2C)
text(485, 490, "local, 400 kHz", 12.5, "middle", color=C_I2C, italic=True)

# 12 V sense divider
y = 630
line([(430, y), esp_left(y, "GPIO 1  12 V sense", C_SNS)], C_SNS)
dot(430, y, C_SNS)
line([(430, y), (430, y - 12)], C_SNS, 2)
resistor(430, y - 56, "v", "100 k")
tag(430, y - 56, "12V", "up")
line([(430, y), (430, y + 12)], C_SNS, 2)
resistor(430, y + 12, "v", "22 k")
tag(430, y + 56, "GND", "down")
text(330, y + 5, "12 V sense", 14, "end", "bold", C_SNS)
text(330, y + 24, "12 V reads 2.2 V", 12.5, "end", color="#444")


def fan(y0, idx, name, ytach, ypwm, xpu, xpd):
    box(PX0, y0, PX1, y0 + 130, f"Fan {idx} ({name})", "Noctua NF-A8 PWM")
    periph_pin_l(ytach, "12 V", "12V")
    periph_pin_l(ypwm, "GND", "GND")
    periph_pin_r(ytach, "tach (green)")
    periph_pin_r(ypwm, "PWM (blue)")
    t = 15 if idx == 0 else 16
    p = 4 if idx == 0 else 5
    line([(PX1, ytach), esp_left(ytach, f"GPIO {t}  FAN{idx} tach", C_FAN)], C_FAN)
    line([(PX1, ypwm), esp_left(ypwm, f"GPIO {p}  FAN{idx} PWM", C_FAN)], C_FAN)
    pull(xpu, ytach, "3V3", "10 k", True, C_FAN)
    pull(xpd, ypwm, "GND", "10 k", False, C_FAN)


fan(730, 0, "intake", 800, 840, 520, 400)
fan(900, 1, "exhaust", 970, 1010, 560, 440)

# ---------------------------------------------------------------------------------------------
# Right side: TMC2209 and motor
# ---------------------------------------------------------------------------------------------
TX0, TX1 = 1150, 1350
box(TX0, 200, TX1, 640, "TMC2209", "stepper driver module")
rows = [(300, "EN", "GPIO 10  EN"), (360, "STEP", "GPIO 11  STEP"), (400, "DIR", "GPIO 12  DIR"),
        (440, "DIAG", "GPIO 13  DIAG")]
for y, pin, lab in rows:
    text(TX0 + 10, y + 5, pin, 14)
    line([esp_right(y, lab, C_MOT), (TX0, y)], C_MOT)
pull(990, 300, "3V3", "10 k", True, C_MOT)

# Single-wire UART: TX through 1 k, RX direct, both onto PDN_UART.
y_tx, y_rx = 520, 580
line([esp_right(y_tx, "GPIO 17  UART TX", C_MOT), (980, y_tx)], C_MOT)
resistor(980, y_tx, "h", "1 k")
line([(1024, y_tx), (1080, y_tx), (1080, y_rx)], C_MOT)
line([esp_right(y_rx, "GPIO 18  UART RX", C_MOT), (TX0, y_rx)], C_MOT)
dot(1080, y_rx, C_MOT)
text(TX0 + 10, y_rx + 5, "PDN_UART", 14)

# Top: logic supply.
for x, pin, net in ((1200, "VIO", "3V3"), (1300, "GND", "GND")):
    text(x, 268, pin, 14, "middle")
    lead_tag(x, 200, net, "up", 26)

# Right edge: motor supply and address pins.
for y, pin, net in ((300, "VM", None), (360, "GND", "GND"), (400, "MS1", "GND"), (440, "MS2", "GND")):
    text(TX1 - 10, y + 5, pin, 14, "end")
    if net:
        lead_tag(TX1, y, net, "right", 30)
line([(TX1, 300), (1560, 300)], NET["12V"], 2)
tag(1560, 300, "12V", "right")
dot(1510, 300)
capacitor(1510, 300, "")
tag(1510, 340, "GND", "down")
text(1510, 385, "100 uF, 25 V,", 12.5, "middle", color="#444")
text(1510, 402, "close to the module", 12.5, "middle", color="#444", italic=True)

# Bottom: motor coils.
coil = [(1180, "A1"), (1220, "A2"), (1280, "B1"), (1320, "B2")]
for x, pin in coil:
    text(x, 630, pin, 13, "middle")
    line([(x, 640), (x, 700 if pin[0] == "A" else 700)], "#111", 2)
line([(1180, 700), (1180, 720), (1225, 745)], "#111", 2)
line([(1220, 700), (1220, 715), (1240, 735)], "#111", 2)
line([(1280, 700), (1280, 715), (1265, 735)], "#111", 2)
line([(1320, 700), (1320, 720), (1280, 745)], "#111", 2)
out.append('<circle cx="1250" cy="800" r="62" fill="#f4f6f8" stroke="#222" stroke-width="2.5"/>')
text(1250, 812, "M", 34, "middle", "bold")
text(1250, 890, "NEMA 17 pancake stepper", 14, "middle", "bold")
text(1250, 908, "coil A: A1-A2, coil B: B1-B2", 12.5, "middle", color="#444")
text(1250, 926, "never plug or unplug it with 12 V on", 12.5, "middle", color=C_SNS, italic=True)

# Below the motor: the two DS18B20 temperature sensors (1-Wire), one pin each.
def ds18b20(y0, where, sub, gpio, xpu, optional=False):
    start = len(out)
    box(TX0, y0, TX1, y0 + 90, f"DS18B20 ({where})", sub)
    ydq, yv, yg = y0 + 66, y0 + 54, y0 + 78
    text(TX0 + 10, ydq + 5, "DQ", 14)
    line([esp_right(ydq, f"GPIO {gpio}  1-Wire {where}", C_TMP), (TX0, ydq)], C_TMP)
    pull(xpu, ydq, "3V3", "4.7 k", True, C_TMP)
    for y, pin, net in ((yv, "VDD", "3V3"), (yg, "GND", "GND")):
        text(TX1 - 10, y + 5, pin, 14, "end")
        lead_tag(TX1, y, net, "right", 30)
    if optional:   # dashed outline for its box
        out[start] = out[start].replace('stroke-width="2"/>', 'stroke-width="2" stroke-dasharray="8,5"/>')


ds18b20(990, "outdoor", "waterproof probe", 14, 1000)
ds18b20(1100, "indoor", "optional (SCD40 reads it too)", 21, 1020, optional=True)
text(1020, 1190, "left out in audio mode", 11.5, "middle", color=C_AUD, italic=True)

# Audio mode (optional): a MAX9814 microphone on the indoor probe's header instead of the probe. GPIO 21 has no
# ADC, so a wire joins it to GPIO 3 (ADC1), under the board here.
MY0 = 1225
box(TX0, MY0, TX1, MY0 + 90, "MAX9814 (audio mode)", "microphone, optional")
out[-3] = out[-3].replace('stroke-width="2"/>', 'stroke-width="2" stroke-dasharray="8,5"/>')
text((TX0 + TX1) / 2, (1190 + MY0) / 2 + 5, "or", 13, "middle", "bold", "#444", italic=True)
yo, yv, yg = MY0 + 66, MY0 + 54, MY0 + 78
text(TX0 + 10, yo + 5, "OUT", 14)
line([(TX0, yo), (1120, yo), (1120, 1166)], C_AUD)
dot(1120, 1166, C_AUD)
for y, pin, net in ((yv, "VDD", "3V3"), (yg, "GND", "GND")):
    text(TX1 - 10, y + 5, pin, 14, "end")
    lead_tag(TX1, y, net, "right", 30)
text(TX0 + 10, MY0 + 108, "GAIN and A/R open (60 dB)", 12.5, color="#444")

y3, yl = 1100, 1232
text(EX0 + 10, y3 + 5, "GPIO 3  mic (audio)", 14)
dot(920, 1166, C_AUD)
line([(920, 1166), (920, yl), (615, yl), (615, y3), (EX0, y3)], C_AUD)
out[-1] = out[-1].replace('stroke-linecap="round"/>', 'stroke-linecap="round" stroke-dasharray="9,6"/>')
text(770, yl + 20, "audio mode only: a wire from GPIO 21 to GPIO 3", 12.5, "middle", color=C_AUD, italic=True)
text(770, yl + 37, "(GPIO 21 has no ADC)", 12.5, "middle", color=C_AUD, italic=True)

# ---------------------------------------------------------------------------------------------
# Top: the two power adapters (12 V brick, 5 V USB-C)
# ---------------------------------------------------------------------------------------------
box(1150, 10, 1350, 120, "12 V power brick", "fans and motor")
for y, pin, net in ((70, "+", "12V"), (100, "-", "GND")):
    text(1340, y + 5, pin, 16, "end", "bold")
    lead_tag(1350, y, net, "right", 30)

box(930, 10, 1090, 120, "USB-C adapter", "5 V, 1 A or more")
line([(930, 70), (700, 70), (700, EY0)], NET["5V"], 4)
text(815, 62, "USB-C cable to the USB-UART connector", 12.5, "middle", color=NET["5V"])

# ---------------------------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------------------------
notes = [
    "Coloured tags with the same name are the same net: every GND is common, and 3V3 comes from the board's 3V3 pin.",
    "Two adapters: 12 V for the fans and motor, 5 V over USB-C for the ESP32 (which makes the 3V3). Join their GNDs on the perfboard.",
    "SCD40 and AS5600 modules usually carry their own I2C pull-ups; on a long SCD40 cable, 4.7 k to 3V3 at the ESP32 end helps.",
    "DS18B20: three wires each (no parasite power), one 4.7 k pull-up per sensor at the ESP32 end. The indoor one (dashed) is optional.",
    "Audio mode (dashed, AUDIO_MODE 1 in Pins.h): the MAX9814 takes the indoor probe's header, without its 4.7 k pull-up,"
    " and a wire joins GPIO 21 to GPIO 3.",
]
for i, n in enumerate(notes):
    text(60, 1355 + i * 24, n, 14, color="#333")

text(60, 34, "Window vent: wiring", 24, weight="bold")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>\n' + "\n".join(out) + "\n</svg>\n")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(svg)
print("wrote", OUT)
