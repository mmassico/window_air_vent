// =====================================================================
//  Window vent: dual butterfly damper with two 80 mm fans (prototype)
//  Parametric OpenSCAD model (tested with OpenSCAD 2021.01).
//
//  * A foam insert fills the window gap (about 100 mm wide). Two 82 mm
//    holes, stacked vertically, go through it: intake on top, exhaust
//    below.
//  * This housing sits on the ROOM face of the foam (warm side, so no
//    ice on the moving parts). Its spigots slide into the foam holes and
//    seal with two O-rings each.
//  * One vertical 5 mm shaft runs through both ducts and carries a
//    butterfly disc in each, so a quarter turn opens or closes both.
//    A NEMA 17 pancake stepper drives it from the top; an AS5600 magnetic
//    encoder reads the shaft angle at the bottom.
//  * Each disc closes against two half-ring lips (lined with thin foam
//    tape), one on each side of the shaft: the classic butterfly seat.
//  * Two 80 mm fans screw onto the room end.
//
//  Coordinates (installed): x across the window, y toward the room
//  (y = 0 on the room face of the foam), z up.
// =====================================================================

/* [Part to show or export] */
part  = "assembly"; // [assembly, body, disc, motor_plate, magnet_cap]
angle = 30;         // [0:5:90] damper opening in the assembly preview (0 = closed)

/* [Ducts and foam] */
duct_id   = 74;     // duct bore (80 mm fans have about a 76 mm blade circle)
wall      = 2.4;    // duct wall (6 perimeters at 0.4 mm)
pitch     = 96;     // vertical distance between the two duct centres
sp_len    = 25;     // spigot length inside the foam hole
sp_od     = 82;     // spigot OD = foam hole diameter
oring_cs  = 2.5;    // O-ring cross-section; grooves are 0.8 x cs deep, 1.4 x cs wide
oring_pos = [6, 16];// groove starts, measured from the foam face into the foam
stop_od   = 90;     // stop ring that rests on the room face of the foam
stop_t    = 3;

/* [Damper] */
ys       = 43;      // shaft position, from the foam face
duct_len = 89;      // foam face to the fan face of the housing
disc_t   = 3;       // disc plate thickness
hc       = 5.5;     // shaft axis above the disc plate bottom (the disc prints flat, hub up)
hub_w    = 10;      // hub width
hub_l    = 40;      // hub length along the shaft
hub_h    = 14;      // hub height above the plate bottom
gasket   = 1;       // foam tape thickness on the lips
lip_ovl  = 2;       // lips overlap the disc edge by this much
lip_t    = 2;       // lip thickness (along the flow)
lip_gap  = 7;       // no lip within this distance of the shaft (clears the hub and the edge-on disc)
dam_h    = 3;       // drip dam near the fan end, on the lower part of each bore
dam_ang  = 60;      // the dam covers +/- this angle from the bottom of the bore
sboss_d  = 16;      // bosses around both shaft holes inside each duct: at the bottom, water flows
sboss_h  = 3;       // around it instead of down the shaft; at both ends, they close the gap the lips leave around the shaft

/* [Fans] */
fan       = 80;     // fan frame size
fan_t     = 25;
fan_hole  = 71.5;   // fan screw spacing (80 mm fans)
fan_plate = 6;      // fan plate thickness; M3 nuts sit in pockets on its back

/* [Shaft, motor and encoder] */
shaft_d   = 5;      // steel rod, same as the NEMA 17 shaft
shaft_clr = 0.4;    // clearance in the bearing holes
boss_h    = 4;      // bearing bosses on the duct walls
nema      = 42.3;   // NEMA 17 frame
nema_hole = 31;     // NEMA 17 screw spacing (M3)
nema_boss = 22;     // NEMA 17 centring boss
coupler_room = 28;  // space for a 5-5 mm flexible coupler (19 x 25 mm)
mp_t      = 6;      // motor frame thickness (on top of the housing)
mplate    = 56;     // motor plate: the motor screws to it on the bench,
mplate_t  = 4;      //   then it screws to the frame from above (4 x M3)
mplate_hole = 48;   // corner screw spacing
tower_t   = 3;      // motor and encoder bracket walls
cap_h     = 7;      // magnet cap on the shaft end
magnet    = "diametric"; // [diametric:diametric disc lying flat (as sold with AS5600 boards), sideways:2 x 2 mm axial cylinder lying across the shaft]
magnet_d  = 6;      // diametric magnet diameter (AS5600 kits: usually 6 x 2.5 mm, some 6 x 3 mm)
magnet_h  = 2.5;    // diametric magnet thickness
enc_gap   = 1.5;    // magnet to encoder chip
enc_stack = 2.6;    // AS5600 board + chip height

/* [Hidden] */
$fn = 96;
eps = 0.01;
r      = duct_id / 2;
ro     = r + wall;
zc     = [pitch / 2, -pitch / 2];          // upper (intake), lower (exhaust)
z_top  = pitch / 2 + ro;                   // top of the upper duct
z_mp0  = z_top + boss_h + coupler_room;    // motor plate bottom
z_mp1  = z_mp0 + mp_t;
z_cap1 = -(z_top + boss_h + 1);            // magnet cap top
z_ep1  = z_cap1 - cap_h - enc_gap - enc_stack;  // encoder plate top
z_ep0  = z_ep1 - 4;
// The disc goes in edge-on, so it must clear the drip dam and the floor boss: that sets its size.
disc_d = duct_id - 2 * (max(dam_h, sboss_h) + 0.6);
lip_w  = (duct_id - disc_d) / 2 + lip_ovl;   // lips reach in far enough to overlap the disc
y_br   = ys - mplate / 2;                  // bracket walls start here (they run to the fan plate)
x_br   = mplate / 2;                       // bracket walls: x from x_br - tower_t to x_br, under the frame corners
y_dam  = ys + (r - 0.4) + 1;               // drip dam face, just outside the disc swing

assert(sqrt(pow(disc_d / 2, 2) + pow(hc, 2)) < r - 0.4, "disc too large to rotate in the bore");

// cylinder along +y, from y0 to y1, centred on (0, z)
module ycyl(y0, y1, d, z = 0, d2 = undef)
    translate([0, y0, z]) rotate([-90, 0, 0]) cylinder(d1 = d, d2 = (d2 == undef ? d : d2), h = y1 - y0);

/* =================== HOUSING =================== */
module duct_outer(z) {
    ycyl(-sp_len, 0, sp_od, z);                                   // spigot
    ycyl(0, stop_t, stop_od, z);                                  // stop ring
    ycyl(stop_t, stop_t + (stop_od / 2 - ro), stop_od, z, 2 * ro);// 45 deg underside (prints without support)
    ycyl(0, duct_len, 2 * ro, z);                                 // damper duct
    for (s = [-1, 1])                                             // shaft bearing bosses
        translate([0, ys, z + s * (r + (wall + boss_h) / 2)]) cylinder(d = 12, h = wall + boss_h + 0.5, center = true);
}

module lips(z) {
    // A: x > lip_gap, room side of the closed disc; B: x < -lip_gap, foam side
    ya = ys - hc + disc_t + gasket;
    yb = ys - hc - gasket;
    intersection() {
        translate([lip_gap, -sp_len, z - ro]) cube([ro, duct_len + sp_len, 2 * ro]);
        union() {
            difference() { ycyl(ya, ya + lip_t, duct_id + 1, z); ycyl(ya - 1, ya + lip_t + 1, duct_id - 2 * lip_w, z); }
            difference() {   // 45 deg chamfer on the room side of lip A
                ycyl(ya + lip_t, ya + lip_t + lip_w, duct_id + 1, z);
                ycyl(ya + lip_t - eps, ya + lip_t + lip_w + eps, duct_id - 2 * lip_w, z, duct_id + 2 * eps);
            }
        }
    }
    intersection() {
        translate([-lip_gap - ro, -sp_len, z - ro]) cube([ro, duct_len + sp_len, 2 * ro]);
        difference() { ycyl(yb - lip_t, yb, duct_id + 1, z); ycyl(yb - lip_t - 1, yb + 1, duct_id - 2 * lip_w, z); }
    }
}

// Two side walls from z0 to z1, running to the fan plate (they rest on the bed when printing),
// with a diamond access window (45 deg edges print without support) between wz0 and wz1.
module bracket(z0, z1, wz0, wz1) {
    s = (wz1 - wz0 - 4) / sqrt(2);
    for (sx = [-1, 1]) difference() {
        translate([sx > 0 ? x_br - tower_t : -x_br, y_br, z0]) cube([tower_t, duct_len - y_br, z1 - z0]);
        translate([sx * (x_br - tower_t / 2), ys, (wz0 + wz1) / 2]) rotate([45, 0, 0]) cube([tower_t + 2, s, s], center = true);
    }
}

module drip_dam(z) {   // lower part of the bore, flat face toward the foam, 45 deg chamfer on the room side
    intersection() {
        translate([-ro, y_dam - 1, z - ro]) cube([2 * ro, duct_len, ro - r * cos(dam_ang)]);
        union() {
            difference() { ycyl(y_dam, y_dam + 2, duct_id + 1, z); ycyl(y_dam - 1, y_dam + 3, duct_id - 2 * dam_h, z); }
            difference() {
                ycyl(y_dam + 2, y_dam + 2 + dam_h, duct_id + 1, z);
                ycyl(y_dam + 2 - eps, y_dam + 2 + dam_h + eps, duct_id - 2 * dam_h, z, duct_id + 2 * eps);
            }
        }
    }
}

// Square frame on top of the bracket. M3 nuts slide into side slots in the middle of
// its thickness (the bracket walls run under the corners, so pockets from below would be blocked).
module motor_frame() {
    difference() {
        // runs to the fan plate, so it rests on the bed when printing (no bridge)
        translate([-mplate / 2, ys - mplate / 2, z_mp0]) cube([mplate, duct_len - (ys - mplate / 2), mp_t]);
        translate([-(mplate_hole / 2 - 4), ys - (mplate_hole / 2 - 4), z_mp0 - 1]) cube([mplate_hole - 8, mplate_hole - 8, mp_t + 2]);
        for (dx = [-1, 1], dy = [-1, 1]) {
            translate([dx * mplate_hole / 2, ys + dy * mplate_hole / 2, z_mp0 - 1]) cylinder(d = 3.4, h = mp_t + 2, $fn = 24);
            // nut slot from the outer x face, 2.8 mm thick, centred in the frame thickness
            translate([dx > 0 ? mplate_hole / 2 - 3.4 : -mplate / 2 - 1, ys + dy * mplate_hole / 2 - 3.05, z_mp0 + (mp_t - 2.8) / 2])
                cube([mplate / 2 - mplate_hole / 2 + 4.4, 6.1, 2.8]);
        }
    }
}

module motor_plate() {   // prints flat; the motor screws to it from below (4 x M3 x 8), heads in the frame opening
    difference() {
        translate([-mplate / 2, -mplate / 2, 0]) cube([mplate, mplate, mplate_t]);
        translate([0, 0, -1]) cylinder(d = nema_boss + 0.5, h = mplate_t + 2);
        for (dx = [-1, 1], dy = [-1, 1]) {
            translate([dx * nema_hole / 2, dy * nema_hole / 2, -1]) cylinder(d = 3.4, h = mplate_t + 2, $fn = 24);
            translate([dx * mplate_hole / 2, dy * mplate_hole / 2, -1]) cylinder(d = 3.4, h = mplate_t + 2, $fn = 24);
        }
    }
}

module body() {
    difference() {
        union() {
            difference() {
                union() {
                    for (z = zc) duct_outer(z);
                    translate([-fan / 2, duct_len - fan_plate, -pitch / 2 - fan / 2]) cube([fan, fan_plate, pitch + fan]);
                    // motor bracket and frame
                    bracket(pitch / 2 + 25, z_mp0 + eps, z_top + boss_h, z_mp0);   // starts inside the bore (cut away below)
                    motor_frame();
                    // encoder bracket and plate
                    bracket(z_ep1 - eps, -pitch / 2 - 25, z_ep1, -(z_top + boss_h));
                    translate([-x_br, y_br, z_ep0]) cube([2 * x_br, duct_len - y_br, z_ep1 - z_ep0]);
                }
                for (z = zc) {
                    ycyl(-sp_len - 1, duct_len + 1, duct_id, z);                     // bore
                    for (p = oring_pos)                                               // O-ring grooves
                        difference() {
                            ycyl(-p - 1.4 * oring_cs, -p, sp_od + 2, z);
                            ycyl(-p - 1.4 * oring_cs - 1, -p + 1, sp_od - 2 * 0.8 * oring_cs, z);
                        }
                    for (dx = [-1, 1], dz = [-1, 1]) {                                 // fan screws + M3 nut pockets
                        translate([dx * fan_hole / 2, duct_len - fan_plate - 1, z + dz * fan_hole / 2]) rotate([-90, 0, 0]) cylinder(d = 3.4, h = fan_plate + 2, $fn = 24);
                        translate([dx * fan_hole / 2, duct_len - fan_plate - eps, z + dz * fan_hole / 2]) rotate([-90, 0, 0]) cylinder(r = 5.8 / sqrt(3), h = 2.6, $fn = 6);
                    }
                }
                // encoder plate: two slots to screw or zip-tie the AS5600 board
                for (dy = [-1, 1]) hull() for (dx = [-1, 1])
                    translate([dx * 12, ys + dy * 9, z_ep0 - 1]) cylinder(d = 3.2, h = 6, $fn = 24);
            }
            // inside the bores
            for (z = zc) {
                lips(z);
                drip_dam(z);
                translate([0, ys, z - r - 1]) cylinder(d = sboss_d, h = 1 + sboss_h, $fn = 48);   // shaft boss on the floor
                translate([0, ys, z + r - sboss_h]) cylinder(d = sboss_d, h = 1 + sboss_h, $fn = 48);   // and on the ceiling
            }
        }
        // shaft
        translate([0, ys, -(z_top + boss_h) - 1]) cylinder(d = shaft_d + shaft_clr, h = z_mp0 + z_top + boss_h + 2, $fn = 32);
    }
}

/* =================== DISC (print frame: plate on the bed, hub up, shaft along y) =================== */
module disc() {
    difference() {
        intersection() {
            union() {
                cylinder(d = disc_d, h = disc_t);
                translate([-hub_w / 2, -hub_l / 2, 0]) cube([hub_w, hub_l, hub_h]);
            }
            translate([0, 0, hc]) sphere(r = r - 0.4);   // stays inside the bore at every angle
        }
        translate([0, -50, hc]) rotate([-90, 0, 0]) cylinder(d = shaft_d + 0.2, h = 100, $fn = 32);
        translate([0, 0, hc]) cylinder(d = 2.5, h = hub_h, $fn = 24);   // M3 grub screw (self-tapping)
    }
}

// disc in the installed position, opened by a degrees (x > 0 half swings toward the foam)
module disc_installed(z, a)
    translate([0, ys, z]) rotate([0, 0, -a]) translate([0, -hc, 0]) rotate([0, 0, 180]) rotate([90, 0, 0]) disc();

/* =================== MAGNET CAP =================== */
// Printed bore down; the magnet is glued into the pocket on top (it faces the AS5600 once
// installed). The AS5600 reads the field direction across the shaft, so the magnet's
// north-south axis must lie ACROSS the shaft: a diametric disc lies flat, an ordinary
// axial cylinder lies on its side.
module magnet_cap() {
    difference() {
        cylinder(d = 10, h = cap_h);
        translate([0, 0, -1]) cylinder(d = shaft_d + 0.2, h = 1 + cap_h - 3.7, $fn = 32);
        if (magnet == "diametric")
            translate([0, 0, cap_h - magnet_h - 0.2]) cylinder(d = magnet_d + 0.2, h = magnet_h + 1, $fn = 32);
        else   // 2 x 2 mm cylinder lying across the shaft, centred on it
            translate([0, 0, cap_h - 1.1]) rotate([0, 90, 0]) {
                cylinder(d = 2.15, h = 2.15, center = true, $fn = 24);
                translate([-2, -1.075, -1.075]) cube([2, 2.15, 2.15]);  // open to the top face (local -x = up here)
            }
    }
}

/* =================== PREVIEW =================== */
module assembly() {
    color([0.85, 0.85, 0.88]) body();
    for (z = zc) color([0.95, 0.6, 0.25]) disc_installed(z, angle);
    color([0.6, 0.6, 0.62]) translate([0, ys, z_cap1 - 3.3]) cylinder(d = shaft_d, h = z_mp1 - 12 - z_cap1 + 3.3);
    color([0.3, 0.5, 0.9]) translate([0, ys, z_cap1]) rotate([180, 0, 0]) magnet_cap();
    color([0.55, 0.75, 0.95]) translate([0, ys, z_mp1]) motor_plate();
    color([0.15, 0.15, 0.17]) translate([-nema / 2, ys - nema / 2, z_mp1 + mplate_t]) cube([nema, nema, 20]);
    color([0.75, 0.75, 0.3]) translate([0, ys, z_mp0 - 25]) cylinder(d = 19, h = 25);
    color([0.2, 0.55, 0.3]) translate([-11, ys - 11, z_ep1]) cube([22, 22, 1.6]);
    for (z = zc) color([0.2, 0.2, 0.22]) translate([-fan / 2, duct_len, z - fan / 2])
        difference() { cube([fan, fan_t, fan]); translate([fan / 2, -1, fan / 2]) rotate([-90, 0, 0]) cylinder(d = 76, h = fan_t + 2); }
    %translate([-50, -50, -pitch / 2 - 90]) cube([100, 50, pitch + 180]);   // foam insert (ghost)
}

if (part == "assembly")   assembly();
if (part == "body")       translate([0, 0, duct_len]) rotate([-90, 0, 0]) body();   // fan plate on the bed
if (part == "disc")       disc();
if (part == "motor_plate") motor_plate();
if (part == "magnet_cap") magnet_cap();
