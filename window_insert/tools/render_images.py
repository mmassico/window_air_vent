#!/usr/bin/env python3
"""Regenerate the README's part thumbnails from cad/window_caps.scad.

Requires: openscad (2021.01+) on PATH, python3 with Pillow.
Usage:    python tools/render_images.py   (run from the window_insert folder)

Each image is an OpenSCAD preview (Tomorrow colour scheme) of a part in its print orientation, or of the assembly,
trimmed to its content.
"""
import os, subprocess, tempfile
from PIL import Image, ImageChops, ImageDraw, ImageFont

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


def compose(views, gap=24, right_w=600):
    """The first view on the left, the others stacked on its right and numbered from 1, all as tall as each other."""
    side = [v.resize((right_w, round(v.height * right_w / v.width)), Image.LANCZOS) for v in views[1:]]
    h = sum(v.height for v in side) + gap * (len(side) - 1)
    main = views[0].resize((round(views[0].width * h / views[0].height), h), Image.LANCZOS)
    out = Image.new("RGB", (main.width + gap + right_w, h), views[0].getpixel((2, 2)))
    out.paste(main, (0, 0))
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("arialbd.ttf", 30)
    except OSError:
        font = ImageFont.load_default(size=30)
    x, y = main.width + gap, 0
    for i, v in enumerate(side, 1):
        out.paste(v, (x, y))
        draw.ellipse((x + 10, y + 10, x + 56, y + 56), fill="#333333")
        draw.text((x + 33, y + 33), str(i), fill="white", font=font, anchor="mm")
        y += v.height + gap
    return out


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
            ("corner_sash_bottom", "-1.2,0,20,55,0,25,250", (1000, 1000), False),
            ("latch_slice", "0.4,-6.3,1.5,40,0,0,110", (1000, 900), False),
            ("latch_cover", "0,0,0,55,0,210,0", (1000, 900), True),
            ("snap_test", "32.5,21.8,8,55,0,25,230", (1000, 800), False),
            ("joint_side_lower", "1.4,0,10,55,0,25,200", (1000, 900), False),
            ("joint_side_upper", "1.4,0,10,235,0,205,200", (1000, 900), False),
            ("joint_sash_lower", "-1.2,0,10,55,0,155,200", (1000, 900), False),
            ("joint_sash_upper", "-1.2,0,10,235,0,25,200", (1000, 900), False),
            ("joiner_side", "0,0,0,45,0,30,0", (1000, 800), True),
            ("joiner_sash", "0,0,0,45,0,30,0", (1000, 800), True),
            ("cap_top", "0,0,0,55,0,25,0", (800, 1100), True),
            ("cap_bottom", "0,0,0,55,0,25,0", (800, 1100), True),
            ("side_0a", "0,0,53,65,0,25,480", (700, 1000), False),
            ("sash_0a", "0,0,54,65,0,25,480", (700, 1000), False),
            ("joiners", "0,0,0,45,0,30,0", (1000, 800), True)]:
        save(render(os.path.join(tmp, f"{name}.png"), camera, size, [f'part="{name}"'], viewall), f"part_{name}.png")

    # the assembly in the window (the window and the foam as ghosts): all of it, seen from the room, then three corners,
    # composed into one image (a README table would stripe its rows)
    views = [render(os.path.join(tmp, f"{name}.png"), camera, size, ['part="assembly_view"'], False)
             for name, camera, size in [
                 ("assembly", "59,0,540,72,0,205,3000", (600, 1500)),
                 ("assembly_side_top", "0,0,1058,108,0,250,265", (900, 800)),
                 ("assembly_side_bottom", "0,0,22,68,0,250,265", (900, 800)),
                 ("assembly_sash_bottom", "118,0,30,68,0,70,320", (900, 800))]]
    save(compose(views), "assembly.png")
