#!/usr/bin/env python3
"""Export every printable part from cad/window_vent.scad and run the geometry checks.

Requires: openscad (2021.01+) on PATH, python3 with trimesh and scipy.
Usage:    python tools/check.py   (run from the window-vent folder)

Checks
  1. Each part: one closed (watertight) solid, fits a 256 x 256 x 256 mm bed.
  2. The disc swings freely: no overlap with the housing from closed (0 deg) to open (90 deg).
  3. The lips stop the disc: turning it 3 deg past closed must hit them.
  4. The disc can be fitted: slid in edge-on from the fan end, it touches nothing.
  5. The electronics box only touches the housing (zero-volume contact).
"""
import os, subprocess, tempfile, warnings
import trimesh
warnings.filterwarnings('ignore')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = os.path.join(ROOT, "cad", "window_vent.scad")
PARTS = ["body", "disc", "motor_plate", "magnet_cap", "ebox", "fittest", "oring_test"]
BED = 256.0
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
    report(p, m.is_watertight and len(m.split(only_watertight=False)) == 1 and max(size) <= BED,
           f"size {size} mm, {m.volume/1000:.0f} cm3")

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

print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
