#!/usr/bin/env python3
"""Regenerate the README's part thumbnails from cad/window_caps.scad.

Requires: openscad (2021.01+) on PATH, python3 with Pillow.
Usage:    python tools/render_images.py   (run from the window_insert folder)

Each image is an OpenSCAD preview (Tomorrow colour scheme) of a part in its print orientation, trimmed to its content.
"""
import os, subprocess, tempfile
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPS = os.path.join(ROOT, "cad", "window_caps.scad")
IMG = os.path.join(ROOT, "images")
tmp = tempfile.mkdtemp(prefix="wi_img_")


def render(out, camera, size, defs=(), viewall=True):
    """viewall frames the part's bounding box; the upright corner pieces are cut from a cap by a large box, which
    viewall would frame instead, so they get an explicit camera."""
    cmd = ["openscad", "-o", out, f"--imgsize={size[0]},{size[1]}", "--colorscheme=Tomorrow", f"--camera={camera}"]
    if viewall:
        cmd += ["--viewall", "--autocenter"]
    cmd += sum([["-D", d] for d in defs], [])
    subprocess.run(cmd + [CAPS], capture_output=True, text=True, check=True)
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
    for name, camera, size, viewall in [
            ("slice_top", "0,0,0,40,0,0,0", (1000, 800), True),
            ("slice_bottom", "0,0,0,40,0,0,0", (1000, 800), True),
            ("slice_side", "0,0,0,40,0,0,0", (1000, 900), True),
            ("slice_sash", "0,0,0,40,0,0,0", (1000, 900), True),
            ("corner_top", "0,0,0,55,0,25,0", (1000, 1000), True),
            ("corner_bottom", "0,0,0,55,0,25,0", (1000, 1000), True),
            ("corner_side_top", "1.4,0,25,55,0,25,280", (1000, 1100), False),
            ("corner_side_bottom", "1.4,0,27,55,0,25,280", (1000, 1100), False),
            ("corner_sash_top", "-1.2,0,20,55,0,25,250", (1000, 1000), False),
            ("corner_sash_bottom", "-1.2,0,20,55,0,25,250", (1000, 1000), False)]:
        save(render(os.path.join(tmp, f"{name}.png"), camera, size, [f'part="{name}"'], viewall), f"part_{name}.png")
