#!/usr/bin/env python3
"""Write the controller PCB's KiCad project and schematic: pcb/window_vent_ctrl.kicad_pro and .kicad_sch, plus the
project's own symbol library (pcb/window_vent.kicad_sym) and library tables.

Usage: python tools/pcb_schematic.py   (run from the window-vent folder; KiCad 10 installed)
Parts and nets come from tools/pcb_parts.py. Every pin gets a short wire to a net label (power nets included), so the
schematic reads as a list of blocks; tools/pcb_layout.py builds the board from the same data.
Then: kicad-cli sch erc, and kicad-cli sch export pdf for the review copy.
"""
import os, re, sys, uuid, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcb_parts import PARTS, POWER_NETS, ESP_L, ESP_R, TMC_S, TMC_P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(ROOT, "pcb")
NAME = "window_vent_ctrl"
KICAD = r"C:\Program Files\KiCad\10.0\share\kicad"
NS = uuid.UUID("6f1d2c4e-8a3b-4c5d-9e7f-102030405060")
ROOT_UUID = str(uuid.uuid5(NS, "root sheet"))


def uid(key):
    return str(uuid.uuid5(NS, key))


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def fnum(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


# --- tiny s-expression reader: enough to pull symbols and their pins out of KiCad libraries ----------------------
def tokens(text):
    for m in re.finditer(r'"(?:\\.|[^"\\])*"|[()]|[^\s()"]+', text):
        yield m.group(0)


def parse(text):
    stack, cur = [], []
    for t in tokens(text):
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return cur[0]


def block(text, start):
    """the balanced (...) block starting at index start"""
    depth, i = 0, start
    while i < len(text):
        c = text[i]
        if c == '"':                                  # skip a quoted string (it may hold parentheses)
            i += 1
            while text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    raise ValueError("unbalanced")


def lib_symbol(lib_id):
    """(raw text with the symbol renamed to lib_id, list of pins: (number, x, y, angle, length))"""
    lib, name = lib_id.split(":")
    if lib == "window_vent":
        raw = CUSTOM[name]
    else:
        text = LIBS.setdefault(lib, open(os.path.join(KICAD, "symbols", lib + ".kicad_sym"), encoding="utf-8").read())
        m = re.search(r'\n\t\(symbol "' + re.escape(name) + r'"\n', text)
        raw = block(text, m.start() + 2)
    raw = raw.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)
    pins = []

    def walk(node):
        if isinstance(node, list):
            if node and node[0] == "pin":
                at = next(x for x in node if isinstance(x, list) and x[0] == "at")
                ln = next(x for x in node if isinstance(x, list) and x[0] == "length")
                num = next(x for x in node if isinstance(x, list) and x[0] == "number")
                pins.append((num[1], float(at[1]), float(at[2]), int(float(at[3])), float(ln[1])))
            for c in node:
                walk(c)
    walk(parse(raw))
    return raw, pins


LIBS = {}


# --- the two modules as symbols -------------------------------------------------------------------------------
def module_symbol(name, ref, value, left, right, types, half_w=10.16):
    """Box with pins 1..len(left) on the left (top to bottom) and the next ones on the right."""
    n = max(len(left), len(right))
    top = (n - 1) * 2.54 / 2
    out = [f'(symbol "{name}"', "(pin_names (offset 1.016))", "(exclude_from_sim no) (in_bom yes) (on_board yes)",
           f'(property "Reference" "{ref}" (at 0 {fnum(top + 3.81)} 0) (effects (font (size 1.27 1.27))))',
           f'(property "Value" {q(value)} (at 0 {fnum(-top - 3.81)} 0) (effects (font (size 1.27 1.27))))',
           '(property "Footprint" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           '(property "Datasheet" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           '(property "Description" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           f'(symbol "{name}_0_1" (rectangle (start {fnum(-half_w)} {fnum(top + 2.54)}) (end {fnum(half_w)} {fnum(-top - 2.54)}) '
           '(stroke (width 0.254) (type default)) (fill (type background))))',
           f'(symbol "{name}_1_1"']
    for side, names, x, ang in ((0, left, -half_w - 5.08, 0), (1, right, half_w + 5.08, 180)):
        for i, pn in enumerate(names):
            num = i + 1 + side * len(left)
            out.append(f'(pin {types.get(pn, "bidirectional")} line (at {fnum(x)} {fnum(top - i * 2.54)} {ang}) (length 5.08) '
                       f'(name {q(pn)} (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))')
    out.append(")")
    out.append(")")
    return "\n".join(out)


ESP_NAMES = [("GPIO" + p if p.isdigit() else p) for p in ESP_L + ESP_R]
CUSTOM = {
    "ESP32S3_Lite": module_symbol("ESP32S3_Lite", "U", "Freenove ESP32-S3 Lite", ESP_NAMES[:20], ESP_NAMES[20:],
                                  {"3V3": "power_out", "5V": "power_in", "GND": "power_in", "EN": "input"}),
    "TMC2209_Module": module_symbol("TMC2209_Module", "U", "TMC2209 module", TMC_S, TMC_P,
                                    {"VM": "power_in", "VIO": "power_in", "GND": "power_in", "EN": "input", "MS1": "input",
                                     "MS2": "input", "STEP": "input", "DIR": "input", "CLK": "input",
                                     "M1A": "output", "M1B": "output", "M2A": "output", "M2B": "output"}),
}

# --- placement on the sheet (A3, mm, y down): symbol origin and rotation (degrees, counter-clockwise) ----------------
PLACE = {
    "U1": (76.2, 116.84, 0), "U2": (190.5, 76.2, 0),
    "J1": (284.48, 50.8, 0), "D1": (320.04, 50.8, 180), "JP1": (320.04, 38.1, 0), "C1": (350.52, 53.34, 0),
    "TP3": (302.26, 33.02, 0), "TP4": (340.36, 33.02, 0),
    "J2": (300.99, 109.22, 0), "J3": (300.99, 132.08, 0), "J4": (300.99, 154.94, 0),
    "J5": (358.14, 109.22, 0), "J6": (358.14, 132.08, 0), "J7": (358.14, 154.94, 0), "J8": (358.14, 177.8, 0),
    "JP2": (300.99, 177.8, 0),
    "R1": (167.64, 132.08, 90), "R2": (167.64, 142.24, 90), "R3": (167.64, 152.4, 90), "R4": (167.64, 162.56, 90),
    "R9": (167.64, 172.72, 90), "R10": (167.64, 182.88, 90),
    "R5": (226.06, 132.08, 90), "R6": (226.06, 142.24, 90), "R7": (226.06, 162.56, 90), "R8": (226.06, 172.72, 90),
    "TP1": (165.1, 213.36, 0), "TP2": (185.42, 213.36, 0), "TP5": (205.74, 213.36, 0),
    "H1": (238.76, 210.82, 0), "H2": (251.46, 210.82, 0), "H3": (264.16, 210.82, 0), "H4": (276.86, 210.82, 0),
}
SECTIONS = [  # title, (x, y)
    ("ESP32-S3 (Freenove Lite, FNK0099), soldered: USB toward the box's left wall", (38.1, 76.2)),
    ("TMC2209 stepper driver (StepStick module), soldered", (157.48, 45.72)),
    ("12 V input: D1 against reverse polarity; a jumper on JP1 bypasses it", (271.78, 22.86)),
    ("Connectors (2.54 mm male headers)", (284.48, 93.98)),
    ("Fan, temperature-probe and driver resistors; 12 V sense divider", (149.86, 119.38)),
    ("Test pads", (157.48, 200.66)),
    ("Mounting holes (M2)", (233.68, 200.66)),
]
NOTES = [
    "Nets with the same label are connected. Pins as in firmware/libs/WindowVent/src/Pins.h.",
    "U1 pins 1-20 are its left header (3V3 ... 5V) and 21-40 its right header (TX ... GND), top to bottom as on the board.",
    "U2: MS1 = MS2 = GND (UART address 0); CLK and PDN free. DIAG is not on this module's pins: GPIO 13 goes to TP5.",
    "R6 1k: single-wire UART, TX through 1k and RX straight onto PDN_UART. R5 holds the driver off (EN high) while the ESP32 boots.",
    "R7/R8: 12 V reads 2.16 V on GPIO 1 (ADC1). R2/R4 keep the fans slow at boot; R1/R3 tach pull-ups; R9/R10 1-Wire pull-ups.",
    "GPIO 38, 39, 40 stay free for the INMP441 microphone reserved in Pins.h (no room for its header on this board).",
    "AS5600: tie its DIR pin to GND at the module. C1 sits next to U2's VM pin.",
    "JP2 (solder jumper on the back, open): bridge it for the audio mode, a microphone on J7 read on GPIO 3 (GPIO 21 has no ADC); leave R9 out then.",
]

out = []
PWR = []
# directions on the sheet: unit vectors (x right, y down)
VEC = {"R": (1, 0), "L": (-1, 0), "U": (0, -1), "D": (0, 1)}


def rot(vx, vy, deg):
    """rotate a sheet vector counter-clockwise as seen on the sheet (y down)"""
    c, s = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}[deg % 360]
    return vx * c + vy * s, -vx * s + vy * c


def direction(vx, vy):
    return {(1, 0): "R", (-1, 0): "L", (0, -1): "U", (0, 1): "D"}[(round(vx), round(vy))]


def props(ref, value, fp, x, y, ref_xy, val_xy, hide_ref=False, hide_val=False, ang=0, vjust="left"):
    def at(p):
        return f"(at {fnum(p[0])} {fnum(p[1])} {ang})"
    return (f' (property "Reference" {q(ref)} {at(ref_xy)}{" (hide yes)" if hide_ref else ""} (effects (font (size 1.27 1.27)) (justify left)))'
            f' (property "Value" {q(value)} {at(val_xy)}{" (hide yes)" if hide_val else ""} (effects (font (size 1.27 1.27)) (justify {vjust})))'
            f' (property "Footprint" {q(fp)} (at {fnum(x)} {fnum(y)} 0) (hide yes) (effects (font (size 1.27 1.27))))'
            f' (property "Datasheet" "" (at {fnum(x)} {fnum(y)} 0) (hide yes) (effects (font (size 1.27 1.27))))'
            f' (property "Description" "" (at {fnum(x)} {fnum(y)} 0) (hide yes) (effects (font (size 1.27 1.27))))')


def instance(ref):
    return f' (instances (project "{NAME}" (path "/{ROOT_UUID}" (reference {q(ref)}) (unit 1))))'


def power_symbol(net, x, y, d, key):
    """power symbol at the end of a stub that runs in direction d"""
    lib_id = POWER_NETS[net]
    r = ({"D": 0, "U": 180, "L": 270, "R": 90} if net == "GND" else {"U": 0, "D": 180, "L": 90, "R": 270})[d]
    ref = "#PWR" + f"{len(PWR) + 1:03d}"
    PWR.append(ref)
    vx, vy = VEC[d]
    out.append(f'(symbol (lib_id {q(lib_id)}) (at {fnum(x)} {fnum(y)} {r}) (unit 1) (exclude_from_sim no) (in_bom yes) '
               f'(on_board yes) (dnp no) (uuid {q(uid(key))})'
               + (props(ref, net, "", x, y, (x, y), (x + vx * 3.6, y + vy * 3.6), hide_ref=True, vjust="center")
                  if d in "UD" else
                  props(ref, net, "", x, y, (x, y), (x + vx * 3.3, y + 0.5), hide_ref=True, ang=90,
                        vjust="left" if d == "R" else "right"))
               + f' (pin "1" (uuid {q(uid(key + "/pin"))}))' + instance(ref) + ")")


def label(net, x, y, d, key):
    ang, just = {"R": (0, "left"), "L": (180, "right"), "U": (90, "left"), "D": (270, "right")}[d]
    out.append(f'(label {q(net)} (at {fnum(x)} {fnum(y)} {ang}) (effects (font (size 1.27 1.27)) (justify {just} bottom)) '
               f'(uuid {q(uid(key))}))')


def wire(x1, y1, x2, y2, key):
    out.append(f'(wire (pts (xy {fnum(x1)} {fnum(y1)}) (xy {fnum(x2)} {fnum(y2)})) (stroke (width 0) (type default)) '
               f'(uuid {q(uid(key))}))')


def connect(net, x, y, d, key, length=2.54):
    """a stub from the pin end (x, y) in direction d, ending in a label or a power symbol"""
    vx, vy = VEC[d]
    ex, ey = x + vx * length, y + vy * length
    wire(x, y, ex, ey, key + "/w")
    if net in POWER_NETS and POWER_SYMBOLS:
        power_symbol(net, ex, ey, d, key + "/pwr")
    else:                       # power nets too: KiCad can't turn a sideways power symbol's name horizontal
        label(net, ex, ey, d, key + "/lbl")


POWER_SYMBOLS = False


lib_defs = {}
for ref, lib_id, value, fp, nets, desc in PARTS:
    raw, pins = lib_symbol(lib_id)
    lib_defs[lib_id] = raw
    X, Y, R = PLACE[ref]
    sheet = []                                      # (number, x, y, direction of its stub)
    for num, px, py, ang, ln in pins:
        dx, dy = rot(px, -py, R)                    # library y is up, the sheet's is down
        ax, ay = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[ang]   # toward the body, on the sheet
        bx, by = rot(ax, ay, R)
        sheet.append((num, X + dx, Y + dy, direction(-bx, -by)))
    if R in (90, 270):                              # lying parts: name above, value below
        ref_xy, val_xy = (X - 1.9, Y - 2.2), (X - 1.6, Y + 3.4)
    elif ref.startswith("U"):                     # modules: name and value above the box
        top = min(p[2] for p in sheet)
        ref_xy, val_xy = (X - 10.16, top - 6.6), (X - 10.16, top - 4.4)
    elif sheet:
        top = min(p[2] for p in sheet)
        ref_xy, val_xy = (X + 2.54, top - 4.6), (X + 2.54, top - 2.7)
    else:
        ref_xy, val_xy = (X + 2.54, Y - 1.27), (X + 2.54, Y + 0.635)
    bom = "no" if ref.startswith(("TP", "H")) or "SolderJumper" in lib_id else "yes"   # pads and holes: nothing to buy
    out.append(f'(symbol (lib_id {q(lib_id)}) (at {fnum(X)} {fnum(Y)} {R}) (unit 1) (exclude_from_sim no) (in_bom {bom}) '
               f'(on_board yes) (dnp no) (uuid {q(uid(ref))})'
               + props(ref, value, fp, X, Y, ref_xy, val_xy, ang=0 if R in (0, 180) else 90)
               + "".join(f' (pin {q(p[0])} (uuid {q(uid(ref + "/" + p[0]))}))' for p in pins) + instance(ref) + ")")
    for num, x, y, d in sheet:
        key = f"{ref}/{num}"
        net = nets.get(num)
        if net is None:
            out.append(f'(no_connect (at {fnum(x)} {fnum(y)}) (uuid {q(uid(key + "/nc"))}))')
        else:
            connect(net, x, y, d, key)

# power flags on the nets with no driver of their own
lib_defs["power:PWR_FLAG"] = lib_symbol("power:PWR_FLAG")[0]
for i, (net, (x, y)) in enumerate((("GND", (271.78, 71.12)), ("+12V", (365.76, 45.72)), ("VIN", (271.78, 35.56)))):
    ref = f"#FLG{i + 1:02d}"
    out.append(f'(symbol (lib_id "power:PWR_FLAG") (at {fnum(x)} {fnum(y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) '
               f'(on_board yes) (dnp no) (uuid {q(uid(ref))})'
               + props(ref, "PWR_FLAG", "", x, y, (x, y), (x + 1.27, y - 3.4), hide_ref=True)
               + f' (pin "1" (uuid {q(uid(ref + "/pin"))}))' + instance(ref) + ")")
    connect(net, x, y, "D", ref)
if POWER_SYMBOLS:
    for p in ("power:GND", "power:+3V3", "power:+12V"):
        lib_defs[p] = lib_symbol(p)[0]

for title, (x, y) in SECTIONS:
    out.append(f'(text {q(title)} (exclude_from_sim no) (at {fnum(x)} {fnum(y)} 0) (effects (font (size 1.778 1.778) (bold yes)) '
               f'(justify left bottom)) (uuid {q(uid("text/" + title))}))')
for i, n in enumerate(NOTES):
    out.append(f'(text {q(n)} (exclude_from_sim no) (at 38.1 {fnum(233.68 + i * 3.81)} 0) (effects (font (size 1.524 1.524)) '
               f'(justify left bottom)) (uuid {q(uid("note/" + str(i)))}))')

today = datetime.date.today().isoformat()
sch = ["(kicad_sch", "(version 20250610)", '(generator "window_vent_tools")', '(generator_version "10.0")',
       f"(uuid {q(ROOT_UUID)})", '(paper "A3")',
       f'(title_block (title "Window vent controller") (date {q(today)}) (rev "1.1") '
       '(comment 1 "github.com/mmassico/window_air_vent") (comment 2 "Generated by tools/pcb_schematic.py from tools/pcb_parts.py"))',
       "(lib_symbols"] + [lib_defs[k] for k in sorted(lib_defs)] + [")"] + out + \
      [f'(sheet_instances (path "/" (page "1")))', ")"]
os.makedirs(PCB, exist_ok=True)
with open(os.path.join(PCB, NAME + ".kicad_sch"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(sch) + "\n")

# the project's symbol library and library tables
with open(os.path.join(PCB, "window_vent.kicad_sym"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write('(kicad_symbol_lib (version 20251024) (generator "window_vent_tools") (generator_version "10.0")\n'
             + "\n".join(CUSTOM.values()) + "\n)\n")
with open(os.path.join(PCB, "sym-lib-table"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write('(sym_lib_table (version 7)\n  (lib (name "window_vent")(type "KiCad")(uri "${KIPRJMOD}/window_vent.kicad_sym")'
             '(options "")(descr "Window vent controller: module symbols"))\n)\n')
with open(os.path.join(PCB, "fp-lib-table"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write('(fp_lib_table (version 7)\n  (lib (name "window_vent")(type "KiCad")(uri "${KIPRJMOD}/window_vent.pretty")'
             '(options "")(descr "Window vent controller: module footprints"))\n)\n')
pro = os.path.join(PCB, NAME + ".kicad_pro")
if not os.path.exists(pro):
    with open(pro, "w", encoding="utf-8", newline="\n") as fh:
        fh.write('{\n  "meta": {\n    "filename": "' + NAME + '.kicad_pro",\n    "version": 3\n  }\n}\n')
print("wrote", os.path.join(PCB, NAME + ".kicad_sch"), len(PARTS), "parts,", len(PWR), "power symbols")

# KiCad's own netlist of it: tools/pcb_layout.py takes the board's nets from there
import subprocess
CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", os.path.join(PCB, NAME + ".net"),
                os.path.join(PCB, NAME + ".kicad_sch")], check=True, capture_output=True)
print("wrote", os.path.join(PCB, NAME + ".net"))
# and the PDF for reading it without KiCad
subprocess.run([CLI, "sch", "export", "pdf", "-o", os.path.join(PCB, NAME + "_schematic.pdf"),
                os.path.join(PCB, NAME + ".kicad_sch")], check=True, capture_output=True)
print("wrote", os.path.join(PCB, NAME + "_schematic.pdf"))
