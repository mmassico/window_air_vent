#!/usr/bin/env python3
"""Export every printable part from cad/window_vent.scad and run the geometry checks.

Requires: openscad (2021.01+) on PATH, python3 with trimesh and scipy.
Usage:    python tools/check.py   (run from the window-vent folder)

Checks
  1. Each part: one closed (watertight) solid, fits a 256 x 256 x 256 mm bed.
  2. The disc swings freely: no overlap with the housing from closed (0 deg) to open (90 deg).
  3. The lips stop the disc: turning it 3 deg past closed must hit them.
  4. The disc can be fitted: slid in edge-on from the fan end, it touches nothing.
  5. The electronics box only touches the housing (zero-volume contact), and the boards fit inside it in
     both ESP32 layouts (its USB plug through the left or the right opening, the TMC2209's heatsink under the lid).
  6. Split housing (for 180 mm beds): the two halves are exactly the housing minus the four joint
     screw holes, they don't overlap, and the splice plate only touches them.
  7. The motor plate only touches the housing (its back tabs pass through the frame's slots).
  8. Optional louvers: each part is one closed solid that fits a 180 mm bed, and from -45 to 45 deg
     the frame, blades, link and combs never collide.
"""
import os, subprocess, tempfile, warnings
import trimesh
warnings.filterwarnings('ignore')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = os.path.join(ROOT, "cad", "window_vent.scad")
PARTS = ["body", "disc", "motor_plate", "magnet_cap", "ebox", "fittest", "oring_test",
         "body_top", "body_bottom", "splice"]
BED = 256.0                                      # Bambu Lab P1/X1/A1
SMALL_BED = 180.0                                # Bambu Lab A1 mini
SPLIT = ["body_top", "body_bottom", "splice"]    # must fit the small bed; they replace "body" there
tmp = tempfile.mkdtemp(prefix="wv_check_")
ok = True

def openscad(out, defs=None, src=SCAD):
    cmd = ["openscad", "-o", out] + sum([["-D", d] for d in (defs or [])], []) + [src]
    r = subprocess.run(cmd, capture_output=True, text=True)
    empty = "empty" in (r.stderr or "").lower()
    if r.returncode and not empty:
        print(r.stderr); raise SystemExit("openscad failed: " + " ".join(cmd))
    return None if empty or not os.path.exists(out) else out

def report(name, good, detail=""):
    global ok
    ok &= good
    print(f"  [{'OK ' if good else 'BAD'}] {name} {detail}")

print("1. Parts")
for p in PARTS:
    m = trimesh.load(openscad(os.path.join(tmp, p + ".stl"), [f'part="{p}"']))
    size = [round(float(v), 1) for v in m.extents]
    bed = SMALL_BED if p in SPLIT else BED
    small = "fits 180" if max(size) <= SMALL_BED else "needs > 180"
    report(p, m.is_watertight and len(m.split(only_watertight=False)) == 1 and max(size) <= bed,
           f"size {size} mm, {m.volume/1000:.0f} cm3, {small}")

# wrapper: overlap of the upper disc at angle a with the housing
wrap = os.path.join(tmp, "wrap.scad")
with open(wrap, "w") as fh:
    fh.write(f'include <{SCAD.replace(os.sep, "/")}>\npart = "none";\na = 0;\ndy = 0;\n'
             'intersection() { body(); translate([0, dy, 0]) disc_installed(zc[0], a); }\n')

def overlap(a, dy=0):
    f = openscad(os.path.join(tmp, f"ov_{a}_{dy}.stl"), [f"a={a}", f"dy={dy}"], wrap)
    return 0.0 if f is None else abs(trimesh.load(f).volume)

print("2. Disc swings freely (overlap volume must be 0)")
for a in range(0, 91, 10):
    v = overlap(a)
    report(f"disc at {a:2d} deg", v < 1e-6, f"{v:.3f} mm3")

print("3. Lips stop the disc")
v = overlap(-3)
report("disc 3 deg past closed hits the lips", v > 1.0, f"{v:.1f} mm3")

print("4. Disc can be fitted (edge-on, slid in from the fan end; overlap must be 0)")
for dy in range(60, 0, -10):
    v = overlap(90, dy)
    report(f"disc {dy} mm short of its place", v < 1e-6, f"{v:.3f} mm3")

print("5. Electronics box on the housing (overlap volume must be 0)")
boxw = os.path.join(tmp, "box.scad")
with open(boxw, "w") as fh:
    fh.write(f'include <{SCAD.replace(os.sep, "/")}>\npart = "none";\nintersection() {{ body(); ebox(); }}\n')
f = openscad(os.path.join(tmp, "box_ov.stl"), None, boxw)
v = 0.0 if f is None else abs(trimesh.load(f).volume)
report("box on housing", v < 1e-6, f"{v:.3f} mm3")
for usb in ["left", "right"]:
    elw = os.path.join(tmp, f"elec_{usb}.scad")
    with open(elw, "w") as fh:
        fh.write(f'include <{SCAD.replace(os.sep, "/")}>\npart = "none";\n'
                 f'intersection() {{ union() {{ body(); ebox(); }} electronics("{usb}"); }}\n')
    f = openscad(os.path.join(tmp, f"elec_ov_{usb}.stl"), None, elw)
    v = 0.0 if f is None else abs(trimesh.load(f).volume)
    report(f"boards in the box, USB to the {usb} (perfboard, ESP32 and its USB plug, TMC2209)", v < 1e-6, f"{v:.3f} mm3")

print("6. Split housing (leftover / overlap volumes must be 0)")
def volume(name, expr):
    w = os.path.join(tmp, name + ".scad")
    with open(w, "w") as fh:
        fh.write(f'include <{SCAD.replace(os.sep, "/")}>\npart = "none";\n{expr}\n')
    f = openscad(os.path.join(tmp, name + ".stl"), None, w)
    return 0.0 if f is None else abs(trimesh.load(f).volume)

for label, name, expr in [
        ("nothing of the housing lost (except the screw holes)", "sp_lost",
         "difference() { body(); body_half(true); body_half(false); split_screws(); }"),
        ("nothing added to the housing", "sp_added",
         "difference() { union() { body_half(true); body_half(false); } body(); }"),
        ("halves don't overlap", "sp_halves", "intersection() { body_half(true); body_half(false); }"),
        ("splice only touches the housing", "sp_splice", "intersection() { body(); splice(); }")]:
    v = volume(name, expr)
    report(label, v < 1e-6, f"{v:.3f} mm3")

print("7. Motor plate on the housing, tabs in their slots (overlap volume must be 0)")
v = volume("plate_ov", "intersection() { body(); translate([0, ys, z_mp1]) motor_plate(); }")
report("motor plate on housing", v < 1e-6, f"{v:.3f} mm3")

print("8. Optional louvers (cad/louvers.scad): parts, and no collisions from -45 to 45 deg")
LOUV = os.path.join(ROOT, "cad", "louvers.scad")
for p in ["chassis", "blade", "link", "retainer"]:
    m = trimesh.load(openscad(os.path.join(tmp, f"louver_{p}.stl"), [f'part="{p}"'], LOUV))
    size = [round(float(v), 1) for v in m.extents]
    report(f"louver_{p}", m.is_watertight and len(m.split(only_watertight=False)) == 1 and max(size) <= SMALL_BED,
           f"size {size} mm, {m.volume/1000:.1f} cm3")
for a in [-45, 0, 45]:
    w = os.path.join(tmp, f"louv_{a}.scad")
    with open(w, "w") as fh:
        fh.write(f'include <{LOUV.replace(os.sep, "/")}>\npart = "none";\na = {a};\n'
                 "module link_at(a) translate([0, -arm * cos(a) + arm, -arm * sin(a)]) link();\n"
                 "module blades(a) for (z = zs) blade_at(z, a);\n"
                 "module combs() for (sx = [0, 1]) mirror([sx, 0, 0]) retainer();\n"
                 "union() {\n"
                 "  intersection() { chassis(); blades(a); }\n"
                 "  intersection() { chassis(); link_at(a); }\n"
                 "  intersection() { link_at(a); blades(a); }\n"
                 "  intersection() { combs(); blades(a); }\n"
                 "  intersection() { combs(); link_at(a); }\n"
                 "  intersection() { chassis(); combs(); }\n"
                 "  for (i = [0 : n_blades - 2]) intersection() { blade_at(zs[i], a); blade_at(zs[i + 1], a); }\n"
                 "}\n")
    f = openscad(os.path.join(tmp, f"louv_{a}.stl"), None, w)
    v = 0.0 if f is None else abs(trimesh.load(f).volume)
    report(f"louvers at {a:3d} deg (frame, blades, link, combs)", v < 1e-6, f"{v:.3f} mm3")

print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
