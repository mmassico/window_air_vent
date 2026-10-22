#!/usr/bin/env python3
"""Regenerate the README images from the OpenSCAD models.

Requires: openscad (2021.01+) on PATH, python3 with Pillow.
Usage:    python tools/render_images.py [name ...]   (run from the window-vent folder; no name = all)

Each image is an OpenSCAD preview (Tomorrow colour scheme), trimmed to its content.
Section views use small wrapper files written to a temporary folder.
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENT = os.path.join(ROOT, "cad", "window_vent.scad")
LOUV = os.path.join(ROOT, "cad", "louvers.scad")
IMG = os.path.join(ROOT, "images")
tmp = tempfile.mkdtemp(prefix="wv_img_")


def inc(scad):
    return f'include <{scad.replace(os.sep, "/")}>\npart = "none";\n'


# Wrappers for the section views (installed coordinates of window_vent.scad).
CUT = inc(VENT) + """intersection() {   // top-down cut through the upper duct, disc at angle a
    union() { color([0.8, 0.8, 0.85]) body(); color([0.95, 0.55, 0.2]) disc_installed(zc[0], a); }
    translate([-60, -40, zc[0] - 60]) cube([120, 140, 60 + 12]);
}
"""
SIDE = inc(VENT) + """intersection() {   // vertical cut through the shaft plane (x = 0), lower duct
    union() { color([0.8, 0.8, 0.85]) body(); color([0.95, 0.55, 0.2]) disc_installed(zc[1], 0); }
    translate([0, -30, -160]) cube([60, 140, 160]);
}
"""
LIPS = inc(VENT) + """z = zc[0];   // lower half of the upper duct around the damper: housing grey, lips red, closed disc orange
intersection() {
    union() {
        color([0.82, 0.82, 0.86]) difference() { body(); lips(z); }
        color([0.85, 0.15, 0.15]) lips(z);
        color([0.95, 0.6, 0.2]) disc_installed(z, 0);
    }
    translate([-45, 18, z - 45]) cube([90, 52, 45.5]);
}
"""
XSEC = inc(VENT) + """z = zc[0];   // cut across the upper duct just on the room side of the closed disc, seen from the room
intersection() {
    union() {
        color([0.82, 0.82, 0.86]) difference() { body(); lips(z); }
        color([0.85, 0.15, 0.15]) lips(z);
        color([0.95, 0.6, 0.2]) disc_installed(z, 0);
    }
    translate([-50, -30, z - 50]) cube([100, 30 + ys - 1.5, 100]);
}
"""


def render(out, src, camera, size, defs=(), ortho=False, viewall=False, text=None):
    """Render src (a .scad path, or wrapper text) to out; returns the trimmed image."""
    if text is not None:
        src = os.path.join(tmp, os.path.basename(out) + ".scad")
        with open(src, "w") as fh:
            fh.write(text)
    cmd = ["openscad", "-o", out, f"--imgsize={size[0]},{size[1]}", "--colorscheme=Tomorrow", f"--camera={camera}"]
    cmd += sum([["-D", d] for d in defs], [])
    if ortho:
        cmd.append("--projection=o")
    if viewall:
        cmd += ["--viewall", "--autocenter"]
    subprocess.run(cmd + [src], capture_output=True, text=True, check=True)
    return trim(Image.open(out))


def trim(im, pad=20):
    im = im.convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((2, 2)))
    b = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
    return im.crop((max(b[0] - pad, 0), max(b[1] - pad, 0), min(b[2] + pad, im.width), min(b[3] + pad, im.height)))


def font():
    try:
        return ImageFont.truetype("arial.ttf", 22)
    except OSError:
        return ImageFont.load_default()


def save(im, name):
    im.save(os.path.join(IMG, name))
    print(f"  {name} {im.size[0]} x {im.size[1]}")


def t(name):
    return os.path.join(tmp, name)


# name -> function producing images/<name>
def assembly():
    save(render(t("a.png"), VENT, "0,0,0,68,0,198,0", (1000, 1100), ['angle=30'], viewall=True), "assembly.png")

def damper_section():
    ims = [render(t(f"cut{a}.png"), None, "0,40,200,0,0,0,330", (700, 600), ortho=True, text=f"a = {a};\n" + CUT)
           for a in (0, 45, 90)]
    w = sum(i.width for i in ims) + 40
    h = max(i.height for i in ims) + 50
    g = Image.new("RGB", (w, h), "white"); d = ImageDraw.Draw(g); x = 0; f = font()
    for im, cap in zip(ims, ("closed", "45 deg", "open")):
        g.paste(im, (x, 45)); d.text((x + im.width // 2 - 30, 10), cap, fill="black", font=f); x += im.width + 20
    save(g, "damper_section.png")

def side_section():
    im = render(t("side.png"), None, "0,40,-70,90,0,270,460", (900, 900), ortho=True, text=SIDE)
    g = Image.new("RGB", (im.width, im.height + 45), "white"); g.paste(im, (0, 45))
    ImageDraw.Draw(g).text((10, 10), "Side section (shaft plane): fan end left, foam right", fill="black", font=font())
    save(g, "side_section.png")

def damper_cutaway():
    save(render(t("lips.png"), None, "0,44,28,48,0,210,300", (1100, 850), text=LIPS), "damper_cutaway.png")

def damper_closed_view():
    save(render(t("xsec.png"), None, "0,40,48,90,0,180,260", (900, 900), ortho=True, text=XSEC), "damper_closed_view.png")

def parts():
    for name, camera, size, viewall in [
            ("body", "0,0,0,60,0,30,0", (900, 1100), True),
            ("disc", "0,0,4,55,0,30,190", (1100, 900), False),
            ("motor_plate", "0,-3,6,55,0,25,240", (1100, 1000), False),
            ("magnet_cap", "0,0,0,55,0,30,0", (700, 800), True),
            ("ebox", "0,0,0,50,0,20,0", (900, 800), True),
            ("fittest", "28.03,16.58,-2.18,52.9,0,305.3,250", (1200, 1100), False),
            ("oring_test", "0,0,0,55,0,25,0", (1000, 800), True),
            ("body_top", "0,63,40,55,0,25,560", (1300, 1300), False),
            ("body_bottom", "0,-58,40,55,0,25,560", (1300, 1300), False),
            ("splice", "0,0,3,50,0,20,150", (1000, 800), False)]:
        save(render(t(f"p_{name}.png"), VENT, camera, size, [f'part="{name}"'], viewall=viewall), f"part_{name}.png")

def split_view():
    save(render(t("split.png"), VENT, "0,30,0,70,0,235,820", (1100, 1300), ['part="split_view"']), "split_view.png")

def louvers():
    save(render(t("louv.png"), LOUV, "0,0,0,48,0,200,300", (1300, 1300), ['angle=25']), "louvers.png")
    for name, camera, size, viewall in [
            ("chassis", "0,0,0,55,0,25,200", (1200, 1000), True),
            ("blade", "41,0,1,50,0,20,140", (1400, 700), False),
            ("link", "0,0,0,55,0,25,200", (1200, 1000), True),
            ("retainer", "0,0,0,55,0,25,200", (1200, 1000), True)]:
        save(render(t(f"l_{name}.png"), LOUV, camera, size, [f'part="{name}"'], viewall=viewall), f"part_louver_{name}.png")


JOBS = {f.__name__: f for f in (assembly, damper_section, side_section, damper_cutaway, damper_closed_view,
                                parts, split_view, louvers)}

if __name__ == "__main__":
    names = sys.argv[1:] or list(JOBS)
    for n in names:
        print(n)
        JOBS[n]()
