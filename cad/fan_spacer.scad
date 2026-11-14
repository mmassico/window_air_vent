// =====================================================================
//  Window vent: spacer with straightening vanes between two stacked fans
//  (optional add-on). Parametric OpenSCAD model (tested with OpenSCAD 2021.01).
//
//  * Two 80 mm fans in series in the same duct (push-pull) give about twice
//    the pressure of one. The first fan's air leaves it spinning, which takes
//    away part of what the second fan can add: thin radial vanes in this
//    spacer straighten it, and the spacing keeps the two rotors apart (less
//    of the hum or beat of two rotors running close together).
//  * A square block the size of the fans, with their bore, a small hub ring
//    behind the motors, and radial vanes from the hub to the wall. Both faces
//    are flat, like the housing's fan plate.
//  * The fan bolts go through the whole stack: outer fan, shim, spacer, shim,
//    inner fan, into the fan plate's nuts, instead of the M3 x 35. With the
//    default 12 mm spacer and 1.35 mm shims: 2 x 25 + 12 + 2.7 + the 6 mm fan
//    plate = 70.7, so M3 x 75 (an M3 x 70 reaches only 1.9 mm into the nut);
//    with length = 10, M3 x 70.
//  * It prints as modelled, either face on the bed, no supports: every wall
//    and vane is vertical.
//  * The fans' corner rubber pads stand proud of their faces, so the spacer
//    would only bear on them. A thin cross-shaped shim on each face of the
//    spacer fills that gap beside the pads (its corners cut away around
//    them); four tabs on one side key it into the spacer's bore, between the
//    vanes. Two per spacer, printed flat, tabs up. With them, the stack is
//    2 x shim_t longer: see the README for the bolt length.
//
//  Coordinates: z along the airflow, z = 0 and z = length on the two faces.
// =====================================================================

/* [Part to show or export] */
part = "spacer";    // [spacer, shim, assembly]

/* [Spacer] */
length   = 12;      // along the airflow (the fans' spacing)
vanes    = 8;       // radial vanes; short vanes straighten less, so more of them
vane_t   = 1.2;     // vane thickness (three 0.4 mm lines)
vane_rot = 22.5;    // turns the set of vanes: none horizontal or vertical
hub_d    = 30;      // hub ring behind the fans' motors (their hubs block that area anyway)
hub_t    = 1.2;     // hub ring wall

/* [Shim (for the fans' corner rubber pads)] */
shim_t   = 1.35;    // the pads' height above the fan's face
shim_arm = 54.8;    // the cross's arms: this wide, centred (the corners, 12.6 mm square, clear the pads)
tabs     = 4;       // alignment tabs, between the vanes, against the spacer's bore
tab_h    = 2;       // how far they reach into the spacer
tab_t    = 1;       // radial thickness
tab_w    = 10;      // length along the bore
tab_clr  = 0.2;     // clearance to the bore (radial)
tab_rot  = 45;      // turns the tabs by whole vane pitches (45 deg: mid-sides, clear of the fan's frame at the diagonals)
gusset   = 4;       // right-angle triangles filling the cross's inner corners (legs this long): more plastic there

/* [Fan] */
fan      = 80;      // fan frame size
fan_t    = 25;      // fan frame depth (assembly view only)
fan_hole = 71.5;    // fan screw spacing
bore     = 76;      // the fans' blade circle (the housing's duct is 74)
hole_d   = 3.4;     // M3 clearance

eps = 0.01;

module spacer() {
    difference() {
        translate([-fan / 2, -fan / 2, 0]) cube([fan, fan, length]);
        translate([0, 0, -1]) cylinder(d = bore, h = length + 2, $fn = 180);
        for (dx = [-1, 1], dy = [-1, 1])
            translate([dx * fan_hole / 2, dy * fan_hole / 2, -1]) cylinder(d = hole_d, h = length + 2, $fn = 24);
    }
    difference() {                                   // hub ring, open at both ends
        cylinder(d = hub_d, h = length, $fn = 90);
        translate([0, 0, -1]) cylinder(d = hub_d - 2 * hub_t, h = length + 2, $fn = 90);
    }
    for (i = [0 : vanes - 1])                        // vanes: from inside the hub ring into the outer wall
        rotate(vane_rot + i * 360 / vanes)
            translate([hub_d / 2 - hub_t / 2, -vane_t / 2, 0]) cube([(bore - hub_d + hub_t) / 2 + 0.5, vane_t, length]);
}

// cross-shaped shim, tabs up (as printed); in the stack, the tabs go into the spacer
module shim() {
    difference() {
        union() {
            translate([-fan / 2, -shim_arm / 2, 0]) cube([fan, shim_arm, shim_t]);
            translate([-shim_arm / 2, -fan / 2, 0]) cube([shim_arm, fan, shim_t]);
            for (sx = [-1, 1], sy = [-1, 1]) scale([sx, sy, 1])      // gussets in the four inner corners
                translate([shim_arm / 2 - eps, shim_arm / 2 - eps, 0])
                    linear_extrude(shim_t) polygon([[0, 0], [gusset + eps, 0], [0, gusset + eps]]);
        }
        translate([0, 0, -1]) cylinder(d = bore, h = shim_t + 2, $fn = 180);
    }
    r1 = bore / 2 - tab_clr;                         // tab outer radius
    a  = tab_w / r1 * 180 / PI;                      // tab angle
    for (i = [0 : tabs - 1])                         // centred between two vanes
        rotate(vane_rot + 180 / vanes + tab_rot + i * 360 / tabs - a / 2)
            rotate_extrude(angle = a, $fn = 180) {
                translate([r1 - tab_t, shim_t - eps]) square([tab_t, tab_h + eps]);       // the tab
                translate([r1 - tab_t, 0]) square([bore / 2 + 0.5 - (r1 - tab_t), shim_t]);  // its foot, in the sheet
            }
}

// the stack: inner fan (on the housing's fan plate, below), shim, spacer, shim, outer fan, and the four bolts
module fan_dummy() {
    color([0.2, 0.2, 0.22]) difference() {
        translate([-fan / 2, -fan / 2, 0]) cube([fan, fan, fan_t]);
        translate([0, 0, -1]) cylinder(d = bore, h = fan_t + 2, $fn = 90);
        for (dx = [-1, 1], dy = [-1, 1])
            translate([dx * fan_hole / 2, dy * fan_hole / 2, -1]) cylinder(d = hole_d, h = fan_t + 2, $fn = 24);
    }
}

module assembly() {
    translate([0, 0, -shim_t - fan_t]) fan_dummy();
    color([0.3, 0.6, 0.9]) translate([0, 0, -shim_t]) shim();
    color([0.95, 0.6, 0.2]) spacer();
    color([0.3, 0.6, 0.9]) translate([0, 0, length + shim_t]) mirror([0, 0, 1]) shim();
    translate([0, 0, length + shim_t]) fan_dummy();
    top = length + shim_t + fan_t;
    bolt = 2 * fan_t + length + 2 * shim_t + 6;     // to the back of the 6 mm fan plate
    for (dx = [-1, 1], dy = [-1, 1]) color([0.7, 0.7, 0.72]) translate([dx * fan_hole / 2, dy * fan_hole / 2, 0]) {
        translate([0, 0, top]) cylinder(d = 5.5, h = 3, $fn = 24);          // socket head
        translate([0, 0, top - bolt]) cylinder(d = 3, h = bolt, $fn = 16);  // M3, to the fan plate's nuts
    }
}

if (part == "spacer")   spacer();
if (part == "shim")     shim();
if (part == "assembly") assembly();
