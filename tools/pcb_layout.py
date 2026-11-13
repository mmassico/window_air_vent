#!/usr/bin/env python3
"""Build the controller PCB (pcb/window_vent_ctrl.kicad_pcb): outline, mounting holes, footprints, nets, placement.

Usage: "C:/Program Files/KiCad/10.0/bin/python.exe" tools/pcb_layout.py   (KiCad's own Python: it has pcbnew)
Parts and nets come from tools/pcb_parts.py, as for the schematic (tools/pcb_schematic.py, run that first).
The board is the 5 x 7 cm protoboard's size and holes; the ESP32-S3 and the TMC2209 sit on the same pins as on the
protoboard (doc/perfboard.svg), so the box model stays valid. Coordinates: mm, seen from above, the window side at
the top (smaller y), the right wall on the right (larger x); grid hole (c, r) as in the protoboard plan.
"""
import os, sys, uuid
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcb_parts import PARTS, DNP, DEVKITC, NAME

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(ROOT, "pcb")
FPLIB = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
MYLIB = os.path.join(PCB, "window_vent.pretty")
NS = uuid.UUID("6f1d2c4e-8a3b-4c5d-9e7f-102030405060")     # as in pcb_schematic.py: the symbols' UUIDs
mm = pcbnew.FromMM

# board: 70 x 50 with its top-left corner at (100, 100); the protoboard's 24 x 18 grid centred on it
BX, BY, BW, BH = 100.0, 100.0, 70.0, 50.0
CX, CY = BX + BW / 2, BY + BH / 2
HOLES = (66.0, 46.26)                       # the protoboard's corner holes (measured), for the box's M2 standoffs


def hole(c, r):
    """protoboard grid: column c (0 = A, at the right wall), row r (0 = the back row, printed 18)"""
    return CX + (11.5 - c) * 2.54, CY + (r - 8.5) * 2.54


# --- the two module footprints (pad 1 at the origin; same orientation as on the board) --------------------------
def module_fp(name, descr, pads, outline, rows, extra="", silk_x=0.0, crt_end=1.52):
    """rows: (x0, x1, y of each pin row): the courtyard covers the header strips only; the module stands 2.6 mm up
    on its pins, so parts lower than that (lying resistors) may go under its edges"""
    x0, y0, x1, y1 = outline
    lines = [f'(footprint "{name}" (version 20241229) (generator "window_vent_tools") (layer "F.Cu")',
             f'(descr "{descr}")',
             f'(property "Reference" "REF**" (at {x0 + 1:.2f} {y0 - 1.2:.2f} 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)) (justify left)))',
             f'(property "Value" "{name}" (at {(x0 + x1) / 2:.2f} {(y0 + y1) / 2:.2f} 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
             '(attr through_hole)',
             f'(fp_rect (start {x0 - silk_x:.2f} {y0:.2f}) (end {x1 + silk_x:.2f} {y1:.2f}) (stroke (width 0.12) (type solid)) (fill no) (layer "F.SilkS"))',
             f'(fp_rect (start {x0:.2f} {y0:.2f}) (end {x1:.2f} {y1:.2f}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
             extra]
    rx0, rx1, rys = rows
    for ry in rys:
        lines.append(f'(fp_rect (start {rx0 - crt_end:.2f} {ry - 1.27:.2f}) (end {rx1 + crt_end:.2f} {ry + 1.27:.2f}) '
                     '(stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))')
    for num, x, y in pads:
        shape = "rect" if num == "1" else "circle"
        lines.append(f'(pad "{num}" thru_hole {shape} (at {x:.3f} {y:.3f}) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask"))')
    lines.append(")")
    os.makedirs(MYLIB, exist_ok=True)
    with open(os.path.join(MYLIB, name + ".kicad_mod"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


P = 2.54
# ESP32-S3: pins 1-20 its left header (3V3 at the antenna end ... 5V at the USB end), on the protoboard's back row from
# column D to W; pins 21-40 its right header, 10 rows toward the room. PCB 50 x 28.5, antenna 7 x 18.5 beyond it.
esp_pads = [(str(i + 1), -i * P, 0.0) for i in range(20)] + [(str(21 + i), -i * P, 10 * P) for i in range(20)]
e_end = (50 - 19 * P) / 2
module_fp("Freenove_ESP32S3_Lite", "Freenove ESP32-S3-WROOM Lite (FNK0099), soldered on its pins; antenna to the right",
          esp_pads, (-19 * P - e_end, 5 * P - 14.25, e_end, 5 * P + 14.25), (-19 * P, 0, (0, 10 * P)),
          f'(fp_rect (start {e_end:.2f} {5 * P - 9.25:.2f}) (end {e_end + 7:.2f} {5 * P + 9.25:.2f}) (stroke (width 0.12) (type dash)) (fill no) (layer "F.SilkS"))\n'
          f'(fp_text user "ANTENNA" (at {e_end + 3.5:.2f} {5 * P:.2f} 90) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
          silk_x=0.3)   # silk clear of the end pins' pads; "USB-UART" is board text (tools/pcb_finish.py)
# ESP32-S3-N16R8, DevKitC-1 type (VENT_PCB=devkitc): 2 x 22 pins, the Freenove's 20 plus one at each end, so pad 1 is
# the extra 3V3 one pin beyond the Freenove's pin 1. Rows 25.4 mm apart (measure before ordering: from its photos);
# PCB about 56.3 x 28 (1.5 mm past the end pins), the module's antenna end 6.5 x 18 beyond it, with the U.FL socket.
DK_END, DK_HALF, DK_ANT = 1.5, 14.0, 6.5
dk_pads = [(str(i + 1), -i * P, 0.0) for i in range(22)] + [(str(23 + i), -i * P, 10 * P) for i in range(22)]
module_fp("ESP32S3_DevKitC_N16R8", "ESP32-S3-N16R8 board, DevKitC-1 type (2 x 22), soldered on its pins; antenna to the right",
          dk_pads, (-21 * P - DK_END, 5 * P - DK_HALF, DK_END, 5 * P + DK_HALF), (-21 * P, 0, (0, 10 * P)),
          f'(fp_rect (start {DK_END:.2f} {5 * P - 9:.2f}) (end {DK_END + DK_ANT:.2f} {5 * P + 9:.2f}) (stroke (width 0.12) (type dash)) (fill no) (layer "F.SilkS"))\n'
          f'(fp_text user "ANTENNA" (at {DK_END + DK_ANT / 2:.2f} {5 * P:.2f} 90) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
          silk_x=0.3, crt_end=1.25)    # the row ends' courtyard clear of H1's
# TMC2209: pins 1-8 EN ... DIR, pins 9-16 VM ... GND, 5 rows apart; EN/VM end on the right (toward the 12 V input)
tmc_pads = [(str(i + 1), -i * P, 0.0) for i in range(8)] + [(str(9 + i), -i * P, 5 * P) for i in range(8)]
t_end = (20.81 - 7 * P) / 2
t_side = (15.08 - 5 * P) / 2
module_fp("TMC2209_StepStick", "TMC2209 StepStick module (20.81 x 15.08), soldered on its pins, heatsink up",
          tmc_pads, (-7 * P - t_end, -t_side, t_end, 5 * P + t_side), (-7 * P, 0, (0, 5 * P)),
          f'(fp_rect (start {-7 * P - t_end + 0.34:.2f} {2.5 * P - 7.2:.2f}) (end {-7 * P - t_end + 15.34:.2f} {2.5 * P + 7.2:.2f}) (stroke (width 0.1) (type dash)) (fill no) (layer "F.Fab"))')

# lying 1/4 W resistor (DIN0207, 6.3 x 2.5) for the 2.54 mm strip between the two modules' header spacers: as the
# library's R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal, but its courtyard is the body itself (+-1.26)
os.makedirs(MYLIB, exist_ok=True)
with open(os.path.join(MYLIB, "R_DIN0207_P10.16mm_Flat_Tight.kicad_mod"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join([
        '(footprint "R_DIN0207_P10.16mm_Flat_Tight" (version 20241229) (generator "window_vent_tools") (layer "F.Cu")',
        '(descr "Resistor, axial DIN0207 (6.3 x 2.5 mm), lying, 10.16 mm; courtyard tight to the body")',
        '(property "Reference" "REF**" (at 5.08 -2.0 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '(property "Value" "R" (at 5.08 0 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '(attr through_hole)',
        '(fp_rect (start 1.93 -1.25) (end 8.23 1.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
        '(fp_rect (start -1.05 -1.26) (end 11.21 1.26) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
        '(pad "1" thru_hole rect (at 0 0) (size 1.6 1.6) (drill 0.8) (layers "*.Cu" "*.Mask"))',
        '(pad "2" thru_hole circle (at 10.16 0) (size 1.6 1.6) (drill 0.8) (layers "*.Cu" "*.Mask"))',
        ")"]) + "\n")

# the vertical DO-201AD diode (D1) with a tight courtyard: the library's is a rectangle over the body and the anode
# lead, but at pad 2 there is only the lead, a wire rising to the bend over the body. This one is the body circle
# (r 2.85, as the library's) joined by a band to a circle around pad 2 (r 1.85: its pad plus 0.25), so a part can stand
# next to the lead (devkitc: C2)
import math
lib_d = open(os.path.join(FPLIB, "Diode_THT.pretty", "D_DO-201AD_P5.08mm_Vertical_AnodeUp.kicad_mod"), encoding="utf-8").read()
RB, RL, D_P = 2.85, 1.85, 5.08
a0 = math.degrees(math.asin(RL / RB))                    # where the body circle meets the band
pts = [(RB * math.cos(math.radians(a0)), -RL), (D_P, -RL)]
pts += [(D_P + RL * math.cos(math.radians(a)), RL * math.sin(math.radians(a))) for a in range(-80, 90, 10)]
pts += [(D_P, RL), (RB * math.cos(math.radians(a0)), RL)]
pts += [(RB * math.cos(math.radians(a)), RB * math.sin(math.radians(a))) for a in range(int(a0) + 10, 360 - int(a0), 10)]
crt = ('(fp_poly (pts ' + " ".join(f"(xy {x:.3f} {y:.3f})" for x, y in pts) + ') (stroke (width 0.05) (type solid)) '
       '(fill no) (layer "F.CrtYd"))')
i0 = lib_d.index("\t(fp_rect")
i1 = lib_d.index("\t(fp_line", i0)
assert '"F.CrtYd"' in lib_d[i0:i1]
tight = lib_d[:i0] + "\t" + crt + "\n" + lib_d[i1:]
tight = tight.replace('(footprint "D_DO-201AD_P5.08mm_Vertical_AnodeUp"', '(footprint "D_DO-201AD_P5.08mm_Vertical_AnodeUp_Tight"', 1)
with open(os.path.join(MYLIB, "D_DO-201AD_P5.08mm_Vertical_AnodeUp_Tight.kicad_mod"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(tight)

# --- placement: reference -> (x, y, rotation); the position is pad 1's -----------------------------------------
ex, ey = hole(3, 0)
tx, ty = hole(4, 12)
BAND = 131.35                               # between the header spacers of the ESP32 (to 130.08) and the TMC2209 (from 132.62)
PLACE = {
    "U1": (ex, ey, 0), "U2": (tx, ty, 0),
    "H1": (CX - HOLES[0] / 2, CY - HOLES[1] / 2, 0), "H2": (CX + HOLES[0] / 2, CY - HOLES[1] / 2, 0),
    "H3": (CX - HOLES[0] / 2, CY + HOLES[1] / 2, 0), "H4": (CX + HOLES[0] / 2, CY + HOLES[1] / 2, 0),
    # lying resistors in the strip, under the two modules' edges (2.6 mm up on their pin spacers)
    "R5": (117.56, BAND, 180), "R6": (119.80, BAND, 0), "R8": (132.20, BAND, 0), "R7": (154.80, BAND, 180),
    # 12 V input, right of the TMC2209
    "J1": (168.2, 130.0, 0), "JP1": (160.4, 130.3, 90), "D1": (158.9, 135.2, 0), "C1": (158.7, 144.1, 0),
    "TP3": (168.3, 138.6, 0), "TP4": (168.3, 142.1, 0),
    # connectors, left of the TMC2209: three rows of headers, pins along x
    # J7 is 2 x 3, its first row (3V3, IN, GND) where the 3-pin header was; pin 1 (GND) at its right end
    "J6": (106.8, 135.3, 90), "J7": (118.6 + 2 * P, 135.3, 270), "J8": (127.4, 135.3, 90),
    "J3": (106.8, 140.7, 90),
    "J2": (106.8, 148.1, 90), "J5": (118.6, 148.1, 90),
    "J4": (131.4, 138.9, 0),                                   # the motor header, standing beside the driver's motor pins
    # standing resistors: fan pull-ups and pull-downs, R1/R2 between the fan headers, R3/R4 under J7
    "R1": (107.0, 144.0, 0), "R2": (112.6, 144.0, 0), "R3": (118.8, 142.0, 0), "R4": (124.4, 142.0, 0),
    # 1-Wire pull-ups beside the ESP32's USB end, lying on the back: the USB-C plugs pass over the top there (their
    # undersides 2.6 mm up, too low for a resistor), and the 5 mm standoffs leave room under the board
    "R9": (101.9, 112.2, 270), "R10": (105.6, 112.2, 270),
    # +3V3 bulk capacitor in the top-left corner, as high as it goes: its courtyard (r 3.4) touches H1's (r 2.45), and
    # its silk circle stays clear of the ESP32's outline (x 107.16). Pad 1 (+3V3) on the right, GND on the left, as the test pads it replaces. Clear of
    # the USB-UART cable's path (y 116.6 to 127.6 beside the ESP32), so its pads can be probed with the cable on.
    "C2": (104.95, 107.5, 180), "TP5": (102.6, 130.6, 0),
    # audio-mode jumper (GPIO 21 to GPIO 3), on the back under the ESP32, between its two pins
    "JP2": (117.0, 124.0, 0),
    # PDN_UART jumpers on the back, just under the TMC2209's pins 4 (PDN) and 5 (UART), pad 2 toward the pin
    "JP3": (tx - 3 * P, ty + 2.7, 90), "JP4": (tx - 4 * P, ty + 2.7, 90),
}
if DEVKITC:
    # the module's extra pins take JP1's place (antenna end) and C2's (USB end; C2 would stand under the module):
    # C2 goes below the antenna end, to the right, clear of the module's corner and next to D1's anode lead (D1's
    # tight courtyard); D1 a little lower, J1 below C2, as low as C1 lets it (no TP3/TP4: probe J1 or a fan header)
    PLACE.update({
        "U1": (ex + P, ey, 0),
        "C2": (165.25, 132.6, 0),          # can centre (166.5, 132.6), its courtyard at the edge; "+12V" fits under it
        "D1": (158.8, 133.0, 315),         # turned 45 deg clockwise: its lead toward C1, its body under the module's
                                           # corner (clear of it), so C2 can come down past it
        "J1": (168.5, 139.2, 0),           # right a little, its courtyard clear of C1's: room for "+12V" above
    })
BOTTOM = {"JP2", "JP3", "JP4", "R9", "R10"}              # parts on the back (B.Cu)

board = pcbnew.BOARD()
board.SetCopperLayerCount(2)
edge = pcbnew.PCB_SHAPE(board)
edge.SetShape(pcbnew.SHAPE_T_RECT)
edge.SetStart(pcbnew.VECTOR2I(mm(BX), mm(BY)))
edge.SetEnd(pcbnew.VECTOR2I(mm(BX + BW), mm(BY + BH)))
edge.SetLayer(pcbnew.Edge_Cuts)
edge.SetWidth(mm(0.1))
board.Add(edge)

def read_netlist(path):
    """{(ref, pin): net name} from a KiCad netlist (kicad-cli sch export netlist --format kicadsexpr)"""
    import re
    toks = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()"]+', open(path, encoding="utf-8").read())
    stack, cur = [], []
    for t in toks:
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(t[1:-1] if t.startswith('"') else t)
    tree = cur[0]
    pad_net = {}
    for n in next(x for x in tree if isinstance(x, list) and x[0] == "nets")[1:]:
        name = next(x for x in n if isinstance(x, list) and x[0] == "name")[1]
        for node in n:
            if isinstance(node, list) and node[0] == "node":
                ref = next(x for x in node if isinstance(x, list) and x[0] == "ref")[1]
                pin = next(x for x in node if isinstance(x, list) and x[0] == "pin")[1]
                pad_net[(ref, pin)] = name
    return pad_net


PAD_NET = read_netlist(os.path.join(PCB, NAME + ".net"))
nets = {}
for name in sorted(set(PAD_NET.values())):
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    nets[name] = ni

for ref, lib_id, value, fp_id, pins, desc in PARTS:
    lib, name = fp_id.split(":")
    path = MYLIB if lib == "window_vent" else os.path.join(FPLIB, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPath(pcbnew.KIID_PATH("/" + str(uuid.uuid5(NS, ref))))
    x, y, rot = PLACE[ref]
    fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    fp.SetOrientationDegrees(rot)
    fp.SetDNP(ref in DNP)
    board.Add(fp)
    if ref in BOTTOM:
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    fp.Reference().SetTextAngleDegrees(0)     # references read left to right; the values stay on the fab layer
    fp.Value().SetVisible(False)
    for pad in fp.Pads():
        net = PAD_NET.get((ref, pad.GetNumber()))
        if net:
            pad.SetNet(nets[net])
        assert (net or "").lstrip("/") == pins.get(pad.GetNumber(), (net or "").lstrip("/")), (ref, pad.GetNumber())

# antenna keep-out: no copper on either layer around the ESP32's antenna
ka = pcbnew.ZONE(board)
ka.SetIsRuleArea(True)
ka.SetDoNotAllowTracks(True); ka.SetDoNotAllowVias(True); ka.SetDoNotAllowPads(True); ka.SetDoNotAllowZoneFills(True)
ka.SetDoNotAllowFootprints(False)
ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu)
ka.SetLayerSet(ls)
ka.SetZoneName("antenna keep-out")
o = ka.Outline(); o.NewOutline()
# from the Freenove's module end, so it suits both boards on the devkitc PCB (the Freenove fits its inner pins);
# there 11.6 mm either side of the antenna's centre line, not 12, to leave the devkitc's last pins out of it
k_x, k_h = ex + e_end + 0.6, (11.6 if DEVKITC else 12.0)
for px, py in ((k_x, ey + 5 * P - k_h), (BX + BW, ey + 5 * P - k_h), (BX + BW, ey + 5 * P + k_h),
               (k_x, ey + 5 * P + k_h)):
    o.Append(mm(px), mm(py))
board.Add(ka)

pcbnew.SaveBoard(os.path.join(PCB, NAME + ".kicad_pcb"), board)
print("wrote", os.path.join(PCB, NAME + ".kicad_pcb"), len(PARTS), "footprints,", len(nets), "nets")
