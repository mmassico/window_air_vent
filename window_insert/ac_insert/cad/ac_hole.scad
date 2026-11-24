// =====================================================================
//  Air conditioner exhaust: the hose's hole, and a flat test plate
// =====================================================================
//  The hole in the air conditioner's own window panel, where the exhaust
//  hose's end clips in. Traced in pen on 1 mm paper, redrawn in Visio
//  just outside the pen line; the values below are the drawing's,
//  converted from points (1 pt = 25.4 / 72 mm). The drawing and the
//  scan stay out of the repository.
//
//  The hole is a slot with semicircular ends. On each long side it has
//  two rectangular notches (for the hose end's lugs) and, a little below
//  each one, a small round bump. It is not symmetric top to bottom: the
//  notches are nearer the top. "Top" is the drawing's top.
//
//  hole_test: a plate panel_t thick, the drawing's 116 x 224 rectangle,
//  with the hole in it. Its outline was checked on the original panel
//  (2 mm plate, 2026-11): it matches. At panel_t, the hose's end clips
//  into it.
//
//  ac_hole() is the hole alone, in 2D, for the AC box's panel
//  (insert_boxes.scad): x = 0 on its centre line, y = 0 on the plate's
//  top edge, downward negative (distances "below the top" below are
//  positive).
// =====================================================================

/* [Part to show or export] */
part = "hole_test";   // [hole_test]

/* [Hole (from the Visio drawing, mm)] */
hole_w   = 92.96;     // width: the semicircles' diameter
hole_top = 6.02;      // the hole's top, below the plate's top edge
hole_h   = 211.28;    // height, top of the upper arc to bottom of the lower one
notch_w  = 107.10;    // across both notches of a pair (7.07 past each side; the drawing has 7.05 and 7.11)
notches  = [[53.34, 11.0], [149.10, 11.0]];   // [top, below the plate's top edge; height]: upper and lower pair
bumps    = [67.98, 163.83];   // the round bumps' centres, below the plate's top edge (one pair under each notch)
bump     = [2.96, 1.54];      // a bump's length along the side and its depth past it (an arc through those points)

/* [Panel] */
panel_t  = 2.83;      // the panel's thickness at the hole: the hose's end clips onto this (measured on the hose)

/* [Test plate] */
plate_w  = 116;       // the drawing's rectangle
plate_h  = 224;
plate_tag = [6, 0.6]; // "UP": letter height, engraving depth

// the hole, 2D: x = 0 on its centre line, y = 0 on the plate's top edge, downward negative
module ac_hole() {
    r  = hole_w / 2;
    br = (pow(bump[0] / 2, 2) + pow(bump[1], 2)) / (2 * bump[1]);   // the bump's arc: its radius
    hull() for (y = [hole_top + r, hole_top + hole_h - r]) translate([0, -y]) circle(r, $fn = 192);
    for (n = notches) translate([-notch_w / 2, -(n[0] + n[1])]) square([notch_w, n[1]]);
    for (z = bumps, s = [-1, 1]) translate([s * (r + bump[1] - br), -z]) circle(br, $fn = 64);
}

// the test plate, flat on the bed, engraved face up; its top edge at y = plate_h
module hole_test() {
    difference() {
        translate([-plate_w / 2, 0, 0]) cube([plate_w, plate_h, panel_t]);
        translate([0, plate_h, -1]) linear_extrude(panel_t + 2) ac_hole();
        // "UP" and an arrow in the upper left corner, beside the upper arc
        translate([-plate_w / 2 + 11, plate_h - 22, panel_t - plate_tag[1]]) linear_extrude(1) {
            text("UP", size = plate_tag[0], font = "Liberation Sans:style=Bold", halign = "center", valign = "center");
            translate([0, plate_tag[0] / 2 + 2]) polygon([[-3, 0], [3, 0], [0, 4]]);
        }
    }
}

if (part == "hole_test") hole_test();

if (part == "hole_test") echo(hole_w = hole_w, hole_h = hole_h, notch_w = notch_w, straight_sides = hole_h - hole_w,
     hole_bottom_margin = plate_h - hole_top - hole_h);
