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
//  * The fan bolts go through the whole stack: outer fan, spacer, inner fan,
//    into the fan plate's nuts. With the default 12 mm spacer: M3 x 70 (two
//    25 mm fans + 12 + the 6 mm fan plate = 68), instead of the M3 x 35.
//  * It prints as modelled, either face on the bed, no supports: every wall
//    and vane is vertical.
//
//  Coordinates: z along the airflow, z = 0 and z = length on the two faces.
// =====================================================================

/* [Part to show or export] */
part = "spacer";    // [spacer, assembly]

/* [Spacer] */
length   = 12;      // along the airflow (the fans' spacing)
vanes    = 8;       // radial vanes; short vanes straighten less, so more of them
vane_t   = 1.2;     // vane thickness (three 0.4 mm lines)
vane_rot = 22.5;    // turns the set of vanes: none horizontal or vertical
hub_d    = 30;      // hub ring behind the fans' motors (their hubs block that area anyway)
hub_t    = 1.2;     // hub ring wall

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

// the stack: inner fan (on the housing's fan plate, below), spacer, outer fan, and the four M3 x 70
module fan_dummy() {
    color([0.2, 0.2, 0.22]) difference() {
        translate([-fan / 2, -fan / 2, 0]) cube([fan, fan, fan_t]);
        translate([0, 0, -1]) cylinder(d = bore, h = fan_t + 2, $fn = 90);
        for (dx = [-1, 1], dy = [-1, 1])
            translate([dx * fan_hole / 2, dy * fan_hole / 2, -1]) cylinder(d = hole_d, h = fan_t + 2, $fn = 24);
    }
}

module assembly() {
    translate([0, 0, -fan_t]) fan_dummy();
    color([0.95, 0.6, 0.2]) spacer();
    translate([0, 0, length]) fan_dummy();
    top = length + fan_t;
    for (dx = [-1, 1], dy = [-1, 1]) color([0.7, 0.7, 0.72]) translate([dx * fan_hole / 2, dy * fan_hole / 2, 0]) {
        translate([0, 0, top]) cylinder(d = 5.5, h = 3, $fn = 24);          // socket head
        translate([0, 0, top - 70]) cylinder(d = 3, h = 70, $fn = 16);      // M3 x 70, to the fan plate's nuts
    }
}

if (part == "spacer")   spacer();
if (part == "assembly") assembly();
