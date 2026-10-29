#!/usr/bin/env python3
"""Route the controller PCB with Freerouting, then pour the ground planes.

Usage: "C:/Program Files/KiCad/10.0/bin/python.exe" tools/pcb_route.py   (after tools/pcb_layout.py)
Steps: net classes and design rules into the project file; the board out to Specctra DSN; Freerouting (headless) back
to a session file; the session into the board; GND pours on both layers; zone fill; save.
"""
import json, os, subprocess, sys
import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(ROOT, "pcb")
NAME = "window_vent_ctrl"
BOARD = os.path.join(PCB, NAME + ".kicad_pcb")
FREEROUTING = os.path.join(os.environ["LOCALAPPDATA"], "freerouting", "freerouting.exe")
mm = pcbnew.FromMM

# --- net classes and rules (PCBWay standard: 6/6 mil, 0.3 mm holes; we stay well above) ---------------------------
CLASSES = [  # name, clearance, track, via diameter, via drill, patterns
    ("Default", 0.20, 0.30, 0.80, 0.40, []),
    ("Power", 0.25, 0.80, 1.00, 0.50, ["/+12V", "/VIN", "/MOT_*"]),
    ("Ground", 0.25, 0.50, 0.80, 0.40, ["/GND"]),
]
pro_path = os.path.join(PCB, NAME + ".kicad_pro")
pro = json.load(open(pro_path, encoding="utf-8")) if os.path.exists(pro_path) else {}
classes = []
for name, clr, trk, vd, vh, _ in CLASSES:
    classes.append({"name": name, "clearance": clr, "track_width": trk, "via_diameter": vd, "via_drill": vh,
                    "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
                    "diff_pair_width": 0.2, "line_style": 0, "bus_width": 12, "wire_width": 6,
                    "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 2147483647 if name == "Default" else len(classes), "tuning_profile": ""})
pro["net_settings"] = {"classes": classes, "meta": {"version": 5}, "net_colors": None, "netclass_assignments": None,
                       "netclass_patterns": [{"netclass": n, "pattern": p} for n, *_, pats in CLASSES for p in pats]}
pro.setdefault("board", {}).setdefault("design_settings", {})["rules"] = {
    "min_clearance": 0.2, "min_track_width": 0.2, "min_copper_edge_clearance": 0.5, "min_hole_clearance": 0.25,
    "min_hole_to_hole": 0.25, "min_through_hole_diameter": 0.3, "min_via_diameter": 0.6, "min_via_annular_width": 0.15,
    "min_silk_clearance": 0.0, "min_text_height": 0.8, "min_text_thickness": 0.12, "max_error": 0.005,
    "min_connection": 0.0, "min_resolved_spokes": 1, "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1,
    "min_groove_width": 0.0, "solder_mask_to_copper_clearance": 0.0, "use_height_for_length_calcs": True}
pro.setdefault("meta", {"filename": NAME + ".kicad_pro", "version": 3})
with open(pro_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pro, fh, indent=2)

# --- out to Freerouting and back ----------------------------------------------------------------------------------
board = pcbnew.LoadBoard(BOARD)                 # loads the project file too, so the net classes apply
for t in list(board.GetTracks()):               # start from a clean board
    board.Remove(t)
for z in [z for z in board.Zones() if not z.GetIsRuleArea()]:
    board.Remove(z)
# keep tracks and vias 0.5 mm from the board edge (Freerouting has no edge clearance of its own): four thin keep-outs
for z in [z for z in board.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith("edge")]:
    board.Remove(z)
E = 0.5
for i, (x0, y0, x1, y1) in enumerate(((100, 100, 170, 100 + E), (100, 150 - E, 170, 150), (100, 100, 100 + E, 150),
                                      (170 - E, 100, 170, 150))):
    k = pcbnew.ZONE(board)
    k.SetIsRuleArea(True)
    k.SetDoNotAllowTracks(True); k.SetDoNotAllowVias(True); k.SetDoNotAllowPads(False)
    k.SetDoNotAllowZoneFills(False); k.SetDoNotAllowFootprints(False)
    k.SetLayerSet(pcbnew.LSET.AllCuMask())
    k.SetZoneName(f"edge {i + 1}")
    o = k.Outline(); o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(mm(x), mm(y))
    board.Add(k)
# no vias under the silkscreen labels: their boxes as tools/pcb_finish.py last placed them (it adds them after the
# routing, at fixed positions; after moving a label, run route and finish twice)
for z in [z for z in board.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith("silk")]:
    board.Remove(z)
silk = []
if os.path.exists(os.path.join(PCB, "build", NAME + "_finished.kicad_pcb")):
    done = pcbnew.LoadBoard(os.path.join(PCB, "build", NAME + "_finished.kicad_pcb"))
    for d in done.GetDrawings():
        if d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            bb = d.GetBoundingBox()
            silk.append(tuple(pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())))
print(len(silk), "silkscreen items kept clear of vias")
for i, (x0, y0, x1, y1) in enumerate(silk):
    x0, y0, x1, y1 = x0 - 0.1, y0 - 0.1, x1 + 0.1, y1 + 0.1
    k = pcbnew.ZONE(board)
    k.SetIsRuleArea(True)
    k.SetDoNotAllowTracks(False); k.SetDoNotAllowVias(True); k.SetDoNotAllowPads(False)
    k.SetDoNotAllowZoneFills(False); k.SetDoNotAllowFootprints(False)
    k.SetLayerSet(pcbnew.LSET.AllCuMask())
    k.SetZoneName(f"silk {i + 1}")
    o = k.Outline(); o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(mm(x), mm(y))
    board.Add(k)
dsn, ses = os.path.join(PCB, NAME + ".dsn"), os.path.join(PCB, NAME + ".ses")
if os.path.exists(ses):
    os.remove(ses)
assert pcbnew.ExportSpecctraDSN(board, dsn), "DSN export failed"
print("routing with Freerouting ...")
r = subprocess.run([FREEROUTING, "-de", dsn, "-do", ses, "-mp", "100", "--gui.enabled=false"],
                   capture_output=True, text=True, timeout=1200)
log = (r.stdout or "") + (r.stderr or "")
for line in log.splitlines():
    if any(k in line for k in ("unrouted", "completed", "Auto-routing", "ERROR", "WARN", "passes")):
        print("  ", line[-160:])
assert os.path.exists(ses), "no session file: Freerouting failed\n" + log[-2000:]
assert pcbnew.ImportSpecctraSES(board, ses), "SES import failed"
for t in board.GetTracks():                     # Freerouting necks tracks down between pads: not below 0.2 mm
    if t.GetClass() == "PCB_TRACK" and t.GetWidth() < mm(0.2):
        t.SetWidth(mm(0.2))

# --- ground pours on both layers, then fill ----------------------------------------------------------------------
gnd = board.FindNet("/GND")
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(gnd)
    z.SetZoneName("GND " + ("top" if layer == pcbnew.F_Cu else "bottom"))
    z.SetLocalClearance(mm(0.3))
    z.SetMinThickness(mm(0.25))
    z.SetThermalReliefGap(mm(0.4))
    z.SetThermalReliefSpokeWidth(mm(0.5))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    o = z.Outline(); o.NewOutline()
    for x, y in ((100, 100), (170, 100), (170, 150), (100, 150)):
        o.Append(mm(x), mm(y))
    board.Add(z)
board.GetDesignSettings().m_MinResolvedSpokes = 1     # a pad tucked between tracks may get one spoke only
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(BOARD, board)
os.makedirs(os.path.join(PCB, "build"), exist_ok=True)
pcbnew.SaveBoard(os.path.join(PCB, "build", NAME + "_routed.kicad_pcb"), board)   # tools/pcb_finish.py starts here
print("wrote", BOARD, len(board.GetTracks()), "tracks and vias")
