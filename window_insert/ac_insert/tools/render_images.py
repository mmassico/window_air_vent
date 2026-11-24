#!/usr/bin/env python3
"""Regenerate the README's part thumbnails from cad/window_caps.scad, cad/insert_boxes.scad and cad/ac_hole.scad.

Requires: openscad (2021.01+) on PATH, python3 with Pillow.
Usage:    python tools/render_images.py   (run from the window_insert/ac_insert folder)

Each image is an OpenSCAD preview (Tomorrow colour scheme) of a part in its print orientation, or of the stack in the
window, trimmed to its content.
"""
import os, subprocess, tempfile
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPS = os.path.join(ROOT, "cad", "window_caps.scad")
BOXES = os.path.join(ROOT, "cad", "insert_boxes.scad")
HOLE = os.path.join(ROOT, "cad", "ac_hole.scad")
IMG = os.path.join(ROOT, "images")
tmp = tempfile.mkdtemp(prefix="wci_img_")


def render(out, camera, size, defs=(), viewall=True, src=CAPS, full=False):
    """viewall frames the part's bounding box; full renders it (CGAL) instead of previewing it."""
    cmd = ["openscad", "-o", out, f"--imgsize={size[0]},{size[1]}", "--colorscheme=Tomorrow", f"--camera={camera}"]
    if viewall:
        cmd += ["--viewall", "--autocenter"]
    if full:
        cmd += ["--render"]
    cmd += sum([["-D", d] for d in defs], [])
    subprocess.run(cmd + [src], capture_output=True, text=True, check=True)
    return trim(Image.open(out))


def trim(im, pad=20):
    im = im.convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((2, 2)))
    b = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
    return im.crop((max(b[0] - pad, 0), max(b[1] - pad, 0), min(b[2] + pad, im.width), min(b[3] + pad, im.height)))


def save(im, name):
    os.makedirs(IMG, exist_ok=True)
    im.save(os.path.join(IMG, name))
    print(f"  {name} {im.size[0]} x {im.size[1]}")


if __name__ == "__main__":
    for name, camera, size, src, full in [
            ("cap_top", "0,0,0,55,0,25,0", (800, 1100), CAPS, False),
            ("cap_bottom", "0,0,0,55,0,25,0", (800, 1100), CAPS, False),
            ("box_0a", "0,0,0,60,0,200,0", (1000, 800), BOXES, True),
            ("box_0b", "0,0,0,60,0,200,0", (1000, 800), BOXES, True),
            ("box_0c", "0,0,0,60,0,200,0", (1000, 800), BOXES, True),
            ("ac_joiners", "0,0,0,45,0,30,0", (1000, 800), BOXES, True),
            ("box_1", "0,0,0,60,0,200,0", (1000, 800), BOXES, True),
            ("box_3", "0,0,0,60,0,200,0", (1000, 800), BOXES, True),
            ("hole_test", "0,112,400,0,112,0", (600, 1100), HOLE, True)]:
        save(render(os.path.join(tmp, f"{name}.png"), camera, size, [f'part="{name}"'], True, src, full),
             f"part_{name}.png")

    # the stack in the window, seen from the room (the window as a ghost)
    save(render(os.path.join(tmp, "box_view.png"), "71,0,540,72,0,205,2600", (600, 1500), ['part="box_view"'],
                False, BOXES), "box_view.png")
