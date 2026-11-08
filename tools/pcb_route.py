#!/usr/bin/env python3
"""Route the controller PCB with Freerouting, then pour the ground planes.

Usage: "C:/Program Files/KiCad/10.0/bin/python.exe" tools/pcb_route.py   (after tools/pcb_layout.py)
Steps: net classes and design rules into the project file; the board out to Specctra DSN; Freerouting (headless) back
to a session file; the session into the board; a cleanup (narrowed tracks back to their class width, small jogs
straightened); GND pours on both layers; zone fill; save.
"""
import fnmatch, json, math, os, subprocess, sys
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
    ("Supply", 0.20, 0.50, 0.80, 0.40, ["/+3V3"]),        # the 3.3 V rail: wider, for C2's bulk current
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

# --- cleanup: Freerouting leaves tracks necked down where they once squeezed past something, and small jogs ------
# Each change is kept only if it clears every other net's copper by the larger of the two class clearances, the
# 0.5 mm edge strip and the rule areas that forbid tracks (antenna keep-out); tools/pcb_finish.py's DRC checks again.
SHIFTS = [0.0] + [s * k * 0.05 for k in range(1, 7) for s in (1, -1)]   # sideways, up to 0.3 mm
JOG = mm(0.3)                                   # a joint this close to its neighbours' straight line is a jog


def key(it):
    return int(it.this)                         # the C++ object: Python wrappers differ on each access


def net_rule(net):
    for _, clr, trk, _, _, pats in CLASSES[1:]:
        if any(fnmatch.fnmatchcase(net, p) for p in pats):
            return mm(clr), mm(trk)
    return mm(CLASSES[0][1]), mm(CLASSES[0][2])


no_tracks = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowTracks()]
EX0, EY0, EX1, EY1 = mm(100.5), mm(100.5), mm(169.5), mm(149.5)


def copper(layer):
    """the other copper on a layer: (net, clearance, bounding box, shape) per pad, via and track"""
    items = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(layer):
                items.append((p, p.GetNetname(), net_rule(p.GetNetname())[0], p.GetBoundingBox(), p.GetEffectiveShape(layer)))
    for t in board.GetTracks():
        if t.IsOnLayer(layer):
            items.append((t, t.GetNetname(), net_rule(t.GetNetname())[0], t.GetBoundingBox(), t.GetEffectiveShape(layer)))
    return items


def clear(a, b, w, layer, net, clr, items, skip):
    """a segment a-b, w wide, on net: clear of everything not on its net (skip: keys of tracks being replaced)?"""
    r = w // 2
    if min(a.x, b.x) - r < EX0 or max(a.x, b.x) + r > EX1 or min(a.y, b.y) - r < EY0 or max(a.y, b.y) + r > EY1:
        return False
    seg = pcbnew.SHAPE_SEGMENT(a, b, w)
    for z in no_tracks:
        if z.IsOnLayer(layer) and z.Outline().Collide(seg, 0):
            return False
    x0, x1, y0, y1 = min(a.x, b.x) - r, max(a.x, b.x) + r, min(a.y, b.y) - r, max(a.y, b.y) + r
    for it, n, c, bb, shape in items:
        if n == net or key(it) in skip:
            continue
        m = max(clr, c)
        if bb.GetLeft() > x1 + m or bb.GetRight() < x0 - m or bb.GetTop() > y1 + m or bb.GetBottom() < y0 - m:
            continue
        if shape.Collide(seg, m - 1000):         # 1 um under the rule: a track exactly at it is fine
            return False
    return True


def fixed(pt, net, layer):
    """a pad or a via of this net at this point: the track's end can't move"""
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA" and t.GetNetname() == net and t.GetPosition() == pt:
            return True
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == net and p.IsOnLayer(layer) and p.HitTest(pt):
                return True
    return False


gone = set()                                    # tracks merged away, removed at the end of each pass
removed, trash = [], []                         # ... and kept referenced, so Python doesn't free them


def ends_at(pt, t0):
    k0 = key(t0)
    return [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK" and key(t) != k0 and key(t) not in gone
            and t.GetNetname() == t0.GetNetname()
            and t.GetLayer() == t0.GetLayer() and (t.GetStart() == pt or t.GetEnd() == pt)]


def teed(t):
    """another track of the net ends on t between its ends, or a via sits there (a T): t must keep its line"""
    a, b, k0 = t.GetStart(), t.GetEnd(), key(t)
    for o in board.GetTracks():
        if key(o) == k0 or key(o) in gone or o.GetNetname() != t.GetNetname():
            continue
        pts = [o.GetPosition()] if o.GetClass() == "PCB_VIA" else [o.GetStart(), o.GetEnd()] if o.GetLayer() == t.GetLayer() else []
        for pt in pts:
            if pt != a and pt != b and t.HitTest(pt, 0):
                return True
    return False


def widen(t):
    net, layer = t.GetNetname(), t.GetLayer()
    clr, want = net_rule(net)
    if t.GetWidth() >= want:
        return False
    a, b = t.GetStart(), t.GetEnd()
    L = math.hypot(b.x - a.x, b.y - a.y)
    if L == 0:
        return False
    nx, ny = -(b.y - a.y) / L, (b.x - a.x) / L
    na, nb = ends_at(a, t), ends_at(b, t)
    fa, fb = fixed(a, net, layer), fixed(b, net, layer)
    fa = fa or teed(t)                          # a T on it: widen in place only
    items = copper(layer)
    for s in SHIFTS:
        if s and (fa or fb):
            break
        d = pcbnew.VECTOR2I(int(round(nx * mm(s))), int(round(ny * mm(s))))
        a2, b2 = a + d, b + d
        skip = {key(x) for x in [t] + na + nb}
        if not clear(a2, b2, want, layer, net, clr, items, skip):
            continue
        moved = []                              # the neighbours' ends follow the shifted segment
        ok = True
        for nbrs, old, new in ((na, a, a2), (nb, b, b2)):
            for o in nbrs:
                p, q = (new, o.GetEnd()) if o.GetStart() == old else (o.GetStart(), new)
                if s and not clear(p, q, o.GetWidth(), layer, net, clr, items, skip):
                    ok = False
                moved.append((o, p, q))
        if not ok:
            continue
        t.SetStart(a2); t.SetEnd(b2); t.SetWidth(want)
        for o, p, q in moved:
            o.SetStart(p); o.SetEnd(q)
        return True
    return False


def straighten(t):
    """merge t with the next segment at a free joint that sits within JOG of their straight line"""
    net, layer = t.GetNetname(), t.GetLayer()
    for joint in (t.GetStart(), t.GetEnd()):
        other = ends_at(joint, t)
        if len(other) != 1 or other[0].GetWidth() != t.GetWidth() or fixed(joint, net, layer):
            continue
        o = other[0]
        if teed(t) or teed(o):
            continue
        p = t.GetEnd() if t.GetStart() == joint else t.GetStart()
        q = o.GetEnd() if o.GetStart() == joint else o.GetStart()
        L = math.hypot(q.x - p.x, q.y - p.y)
        if L == 0 or abs((q.x - p.x) * (joint.y - p.y) - (q.y - p.y) * (joint.x - p.x)) / L > JOG:
            continue
        if not clear(p, q, t.GetWidth(), layer, net, net_rule(net)[0], copper(layer), {key(t), key(o)}):
            continue
        t.SetStart(p); t.SetEnd(q)
        gone.add(key(o))
        removed.append(o)
        return True
    return False


def unconnected():
    board.BuildConnectivity()
    return board.GetConnectivity().GetUnconnectedCount(True)


before = unconnected()
widened = merged = 0
for _ in range(6):
    changed = False
    for t in [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"]:
        if widen(t):
            widened += 1; changed = True
    for t in [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"]:
        if key(t) not in gone and straighten(t):
            merged += 1; changed = True
    for o in removed:
        board.Remove(o)
    trash.extend(removed)
    removed.clear()
    gone.clear()
    if not changed:
        break
after = unconnected()
print("cleanup:", widened, "segments back to their class width,", merged, "joints straightened; unconnected",
      before, "->", after)
if after > before:
    print("WARNING: the cleanup disconnected something; DRC will list it")

# --- ground pours on both layers, then fill ----------------------------------------------------------------------
# no top-layer pour along the top edge, above the ESP32's top pin row: it would only leave a sliver between the edge
# and the +3V3 track there (the bottom layer's plane stays whole)
nf = pcbnew.ZONE(board)
nf.SetIsRuleArea(True)
nf.SetDoNotAllowTracks(False); nf.SetDoNotAllowVias(False); nf.SetDoNotAllowPads(False)
nf.SetDoNotAllowZoneFills(True); nf.SetDoNotAllowFootprints(False)
nf.SetLayer(pcbnew.F_Cu)
nf.SetZoneName("no fill, top edge")
o = nf.Outline(); o.NewOutline()
for x, y in ((100, 100), (158.06, 100), (158.06, 102.3), (100, 102.3)):
    o.Append(mm(x), mm(y))
board.Add(nf)
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
# C2's GND pad joins the pours solidly (no thermal spokes): the bulk capacitor's return path
board.FindFootprintByReference("C2").FindPadByNumber("2").SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
board.GetDesignSettings().m_MinResolvedSpokes = 1     # a pad tucked between tracks may get one spoke only
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(BOARD, board)
os.makedirs(os.path.join(PCB, "build"), exist_ok=True)
pcbnew.SaveBoard(os.path.join(PCB, "build", NAME + "_routed.kicad_pcb"), board)   # tools/pcb_finish.py starts here
print("wrote", BOARD, len(board.GetTracks()), "tracks and vias")
