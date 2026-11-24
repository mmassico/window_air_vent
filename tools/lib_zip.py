#!/usr/bin/env python3
"""Zip the WindowVent library for the Arduino IDE's Sketch > Include Library > Add .ZIP Library.

Usage: python tools/lib_zip.py   (run from the window-vent folder; again after any change in firmware/libs/WindowVent)
Writes firmware/libs/WindowVent.zip, with WindowVent/ at its root as the IDE expects (library.properties and src/).
The zip is a copy of the sources, so it is not kept in git (.gitignore): the IDE copies it into the sketchbook, and
a library change needs a new zip, added again. A junction to firmware/libs/WindowVent avoids that (firmware/README.md).
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBS = os.path.join(ROOT, "firmware", "libs")
NAME = "WindowVent"
OUT = os.path.join(LIBS, NAME + ".zip")
SKIP_DIRS = {"__pycache__", ".git"}


def files(top):
    """The library's files, relative to LIBS, in a stable order."""
    for here, dirs, names in os.walk(top):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        for n in sorted(names):
            if not n.startswith("."):
                yield os.path.relpath(os.path.join(here, n), LIBS).replace(os.sep, "/")


def main():
    src = os.path.join(LIBS, NAME)
    if not os.path.isfile(os.path.join(src, "library.properties")):
        raise SystemExit(f"no library.properties in {src}")
    paths = list(files(src))
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in paths:
            z.write(os.path.join(LIBS, rel), rel)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(paths)} files, {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
