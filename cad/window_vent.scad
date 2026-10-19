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
part  = "assembly"; // [assembly, body, disc, motor_plate, magnet_cap, ebox, fittest, oring_test, assembly_nofan]
angle = 30;         // [0:5:90] damper opening in the assembly preview (0 = closed)

/* [Ducts and foam] */
duct_id   = 74;     // duct bore (80 mm fans have about a 76 mm blade circle)
wall      = 2.4;    // duct wall (6 perimeters at 0.4 mm)
pitch     = 96;     // vertical distance between the two duct centres
sp_len    = 25;     // spigot length inside the foam hole
sp_od     = 82;     // spigot OD = foam hole diameter
oring_cs  = 3;      // O-ring cross-section (default: 74 x 3 mm O-rings, stretched about 4.7%)
oring_dep = 0.75;   // groove depth as a fraction of cs (about 24% squeeze in the foam hole); width is 1.4 x cs
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
grub_n   = 2;       // [1:1:3] M3 grub screws per disc (2 = no rocking on the shaft)
grub_sp  = 24;      // spacing between them along the shaft
gasket   = 1;       // foam tape thickness on the lips
lip_ovl  = 2;       // lips overlap the disc edge by this much
lip_t    = 2;       // lip thickness (along the flow)
lip_gap  = 7;       // no lip within this distance of the shaft (clears the hub and the edge-on disc)
dam_h    = 3;       // drip dam near the fan end, on the lower part of each bore (sizes the disc; its inner face follows the disc sweep)
dam_ang  = 60;      // the dam covers +/- this angle from the bottom of the bore
sboss_d  = 16;      // bosses around both shaft holes inside each duct: at the bottom, water flows around it
                    // instead of down the shaft; at both ends, they close the gap the lips leave around the shaft
sboss_clr = 0.3;    // their inner face is curved, coaxial with the bore, this far outside the disc's sweep

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
cap_h     = 12;     // magnet cap on the shaft end
cap_d     = 14;     // wide enough for a radial M3 grub screw
cap_grub_z = 2;     // grub screw height above the cap's shaft end (the shaft reaches about 4.6 mm in)
cap_slide = 1;      // the cap can slide this much up or down before its grub screw is tightened
magnet    = "diametric"; // [diametric:diametric disc lying flat (as sold with AS5600 boards), sideways:2 x 2 mm axial cylinder lying across the shaft]
magnet_d  = 6;      // diametric magnet diameter (AS5600 kits: usually 6 x 2.5 mm, some 6 x 3 mm)
magnet_h  = 2.5;    // diametric magnet thickness
enc_gap   = 1.5;    // nominal magnet face to AS5600 chip top (datasheet: 0.5-3); set on assembly with a shim
enc_chip  = 1.5;    // AS5600 package height (SOIC-8)
enc_board = 1.6;    // board thickness
enc_standoff = 2;   // pads lift the board over its solder joints
enc_holes = [15, 17];  // board hole squares supported by the diagonal slots (20 x 20 and 23 x 23 boards)
enc_win   = [18, 9];   // window under the board for header pins pointing down (x, y)

/* [Electronics box and cables] */
ebox_w    = 80;     // box width (= fan width); the encoder plate widens to match and becomes its lid
ebox_h    = 32;     // inside height under the encoder plate (TMC2209 with heatsink in female headers: about 28)
ebox_t    = 2.4;    // walls and floor
pb_size   = [70, 50];  // perfboard carrier (5 x 7 cm protoboard)
pb_holes  = [66, 46];  // its corner hole spacing (M2)
pb_y      = 56;     // perfboard centre (y)
pb_stand  = 5;      // standoff height
usb_slot  = [0, 10];   // optional slot in the left wall for the ESP32's USB-C (length along y, height); 0 = none (flash once on the bench, then OTA)
usb_z     = 18;     // slot centre above the box floor
cable_in  = [16, 10];  // cable entries at the top of both side walls, toward the front (length along y, depth)

/* [Hidden] */
$fn = 96;
eps = 0.01;
r      = duct_id / 2;
ro     = r + wall;
zc     = [pitch / 2, -pitch / 2];          // upper (intake), lower (exhaust)
z_top  = pitch / 2 + ro;                   // top of the upper duct
z_mp0  = z_top + boss_h + coupler_room;    // motor plate bottom
z_mp1  = z_mp0 + mp_t;
z_cap1 = -(z_top + boss_h + 1 + cap_slide);   // magnet cap top (nominal; it can rise cap_slide)
z_mag  = z_cap1 - cap_h + 0.2;             // magnet face (the magnet sits 0.2 deep in its pocket)
z_ep1  = z_mag - enc_gap - enc_chip - enc_board - enc_standoff;  // encoder plate top
z_ep0  = z_ep1 - 4;
// The disc goes in edge-on, so it must clear the drip dam: that sets its size.
disc_d = duct_id - 2 * (dam_h + 0.6);
lip_w  = (duct_id - disc_d) / 2 + lip_ovl;   // lips reach in far enough to overlap the disc
// The plate is hc off the shaft, so while it turns its edge reaches this far from the bore axis.
r_sweep = sqrt(pow(disc_d / 2, 2) + pow(hc, 2));
boss_rc = r_sweep + sboss_clr;               // curved inner face of the shaft bosses
y_br   = ys - mplate / 2;                  // bracket walls start here (they run to the fan plate)
x_br   = mplate / 2;                       // bracket walls: x from x_br - tower_t to x_br, under the frame corners
y_dam  = ys + (r - 0.4) + 1;               // drip dam face, just outside the disc swing
ebox_top    = -pitch / 2 - fan / 2;         // the box cover rises to the bottom of the lower fan
ebox_back_x = ebox_w / 2 - 6;               // back fixing screws, outside the bay walls
ebox_back_y = y_br + 6;
ebox_screw_z = z_ep1 + 8;                   // front cover screws: in the bay, above the encoder plate
// tie-wrap anchors on the back of the fan plate, right side: the top and bottom ones touch the
// outer fan nut pockets (hex flat at fan_hole / 2 - 2.9 from the fan centre), the middle one sits between the fans
anchor_zt = pitch / 2 + fan_hole / 2 - 5.8 / 2 - 4;
anchor_z  = [anchor_zt, 0, -anchor_zt];

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

// Airflow arrow engraved in the outer face of both bracket walls: dir = +1 toward the room
// (intake, upper duct), -1 toward the foam (exhaust, lower duct). Same direction seen from either side.
module flow_arrows(zm, dir, len = 36, shaft = 3, head = 9, depth = 0.8) {
    yc = ys + 7;
    pts = [[-len / 2, -shaft / 2], [len / 2 - 8, -shaft / 2], [len / 2 - 8, -head / 2], [len / 2, 0],
           [len / 2 - 8, head / 2], [len / 2 - 8, shaft / 2], [-len / 2, shaft / 2]];
    for (sx = [-1, 1])
        translate([sx > 0 ? x_br - depth : -x_br - eps, yc, zm]) rotate([90, 0, 90])
            linear_extrude(depth + eps) scale([dir, 1]) polygon(pts);
}

module drip_dam(z) {   // lower part of the bore, flat face toward the foam, 45 deg chamfer on the room side
    intersection() {
        translate([-ro, y_dam - 1, z - ro]) cube([2 * ro, duct_len, ro - r * cos(dam_ang)]);
        union() {
            difference() { ycyl(y_dam, y_dam + 2, duct_id + 1, z); ycyl(y_dam - 1, y_dam + 3, 2 * boss_rc, z); }
            difference() {
                ycyl(y_dam + 2, y_dam + 2 + dam_h, duct_id + 1, z);
                ycyl(y_dam + 2 - eps, y_dam + 2 + dam_h + eps, 2 * boss_rc, z, duct_id + 2 * eps);
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
                    translate([-ebox_w / 2, y_br, z_ep0]) cube([ebox_w, duct_len - y_br, z_ep1 - z_ep0]);   // encoder plate = box lid
                    for (sx = [-1, 1])   // bosses at the front of the bay walls for the box cover screws
                        translate([sx * (x_br - tower_t / 2) - 3.5, duct_len - 8, ebox_screw_z - 4]) cube([7, 8, 8]);
                    for (sx = [-1, 1], z = anchor_z)   // tie-wrap anchors on both sides (cables on the right, -x, by default)
                        translate([sx < 0 ? -fan / 2 : fan / 2 - 7, duct_len - fan_plate - 6, z - 4]) cube([7, 6 + eps, 8]);
                    for (dx = [-1, 1], dy = [-1, 1]) hull() for (h = enc_holes)   // standoff pads under the board corners
                        translate([dx * h / 2, ys + dy * h / 2, z_ep1 - eps]) cylinder(d = 6, h = enc_standoff + eps, $fn = 32);
                }
                for (z = zc) {
                    ycyl(-sp_len - 1, duct_len + 1, duct_id, z);                     // bore
                    for (p = oring_pos)                                               // O-ring grooves
                        difference() {
                            ycyl(-p - 1.4 * oring_cs, -p, sp_od + 2, z);
                            ycyl(-p - 1.4 * oring_cs - 1, -p + 1, sp_od - 2 * oring_dep * oring_cs, z);
                        }
                    for (dx = [-1, 1], dz = [-1, 1]) {                                 // fan screws + M3 nut pockets
                        translate([dx * fan_hole / 2, duct_len - fan_plate - 1, z + dz * fan_hole / 2]) rotate([-90, 0, 0]) cylinder(d = 3.4, h = fan_plate + 2, $fn = 24);
                        translate([dx * fan_hole / 2, duct_len - fan_plate - eps, z + dz * fan_hole / 2]) rotate([-90, 0, 0]) cylinder(r = 5.8 / sqrt(3), h = 2.6, $fn = 6);
                    }
                }
                // encoder plate: diagonal slots for both AS5600 board sizes (M3 or smaller screws), and a
                // window under the board so header pins can point down (rows parallel to y)
                for (dx = [-1, 1], dy = [-1, 1]) hull() for (h = enc_holes)
                    translate([dx * h / 2, ys + dy * h / 2, z_ep0 - 1]) cylinder(d = 3.2, h = z_ep1 - z_ep0 + enc_standoff + 2, $fn = 24);
                translate([-enc_win[0] / 2, ys - enc_win[1] / 2, z_ep0 - 1]) cube([enc_win[0], enc_win[1], z_ep1 - z_ep0 + 2]);
                // box fixing: cover screws into the front bosses (self-tapping M3), and two M3 from above at the back
                for (sx = [-1, 1]) {
                    translate([sx * (x_br - tower_t / 2), duct_len + 1, ebox_screw_z]) rotate([90, 0, 0]) cylinder(d = 2.5, h = 9, $fn = 24);
                    translate([sx * ebox_back_x, ebox_back_y, z_ep0 - 1]) cylinder(d = 3.4, h = z_ep1 - z_ep0 + 2, $fn = 24);
                }
                // airflow arrows: intake (upper duct) toward the room, exhaust (lower duct) toward the foam,
                // centred in the band between each diamond window and its duct
                flow_arrows((z_top + boss_h + pitch / 2 + sqrt(ro * ro - x_br * x_br)) / 2, 1);
                flow_arrows(-(z_top + boss_h + pitch / 2 + sqrt(ro * ro - x_br * x_br)) / 2, -1);
                for (sx = [-1, 1])   // tie-wrap slot near the back edge of each motor tower wall, level with the
                                     // bottom tip of its diamond window (the tie wraps around the 4 mm strip behind it)
                    translate([sx * (x_br - tower_t / 2) - (tower_t + 2) / 2, y_br + 4, z_top + boss_h + 2]) cube([tower_t + 2, 2, 4.5]);
                for (sx = [-1, 1], z = anchor_z)   // tie-wrap slot through each anchor, across the cable run
                    translate([sx < 0 ? -fan / 2 - 1 : fan / 2 - 8, duct_len - fan_plate - 4, z - 2.25]) cube([9, 2, 4.5]);
            }
            // inside the bores
            for (z = zc) {
                lips(z);
                drip_dam(z);
                intersection() {   // shaft bosses, floor and ceiling: a tall cylinder cut by the bore-axis cylinder
                    translate([0, ys, z - r - 1]) cylinder(d = sboss_d, h = 2 * r + 2, $fn = 48);
                    difference() {
                        ycyl(ys - sboss_d, ys + sboss_d, duct_id + 1, z);
                        ycyl(ys - sboss_d - 1, ys + sboss_d + 1, 2 * boss_rc, z, undef);
                    }
                }
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
        for (k = [0 : grub_n - 1])   // M3 grub screws (self-tapping), spread along the hub
            translate([0, (k - (grub_n - 1) / 2) * (grub_n > 1 ? grub_sp / (grub_n - 1) : 0), hc]) cylinder(d = 2.5, h = hub_h, $fn = 24);
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
// A radial M3 grub screw holds it on the shaft. Before tightening, the cap slides about
// +/- 1 mm along the shaft: rest the magnet on a 1 mm shim laid on the chip, then tighten,
// and the gap is exact whatever the magnet's real thickness or washers under the board.
module magnet_cap() {
    bore = cap_h - (magnet_h + 0.2) - 1;   // shaft bore from the bottom, 1 mm floor under the magnet
    difference() {
        cylinder(d = cap_d, h = cap_h);
        translate([0, 0, -1]) cylinder(d = shaft_d + 0.2, h = 1 + bore, $fn = 32);
        translate([0, 0, cap_grub_z]) rotate([-90, 0, 0]) cylinder(d = 2.5, h = cap_d, $fn = 24);   // M3 grub (self-tapping)
        if (magnet == "diametric")
            translate([0, 0, cap_h - magnet_h - 0.2]) cylinder(d = magnet_d + 0.2, h = magnet_h + 1, $fn = 32);
        else   // 2 x 2 mm cylinder lying across the shaft, centred on it
            translate([0, 0, cap_h - 1.1]) rotate([0, 90, 0]) {
                cylinder(d = 2.15, h = 2.15, center = true, $fn = 24);
                translate([-2, -1.075, -1.075]) cube([2, 2.15, 2.15]);  // open to the top face (local -x = up here)
            }
    }
}

/* =================== ELECTRONICS BOX =================== */
// Open-top tray under the housing; the encoder plate is its lid. Its front wall rises to
// the bottom of the lower fan and closes the front of the bottom bay. Inside: a 5 x 7 cm
// perfboard on four standoffs, carrying the ESP32 and the TMC2209 in female headers.
// Modelled in place (installed coordinates); printed floor down.
module ebox() {
    x0 = -ebox_w / 2;  y0 = y_br;  y1 = duct_len + ebox_t;   // the front wall sits in front of the plate's edge
    zb = z_ep0 - ebox_h - ebox_t;                            // underside of the floor
    difference() {
        union() {
            difference() {   // hollow shell first, so the pillars and standoffs below are not cut away
                union() {
                    translate([x0, y0, zb]) cube([ebox_w, y1 - y0, ebox_h + ebox_t]);
                    translate([x0, duct_len, zb]) cube([ebox_w, ebox_t, ebox_top - zb]);   // front cover
                }
                translate([x0 + ebox_t, y0 + ebox_t, zb + ebox_t]) cube([ebox_w - 2 * ebox_t, duct_len - y0 - ebox_t, ebox_h + 1]);
            }
            for (sx = [-1, 1])   // back corner pillars, floor to top, for the screws from above (no overhang when printing)
                translate([sx * ebox_back_x - 4, y0 + ebox_t - eps, zb + ebox_t - eps]) cube([8, ebox_back_y - y0 + 4 - ebox_t, ebox_h + eps]);   // top flush with the plate
            for (dx = [-1, 1], dy = [-1, 1])   // perfboard standoffs
                translate([dx * pb_holes[0] / 2, pb_y + dy * pb_holes[1] / 2, zb + ebox_t - eps]) cylinder(d = 6, h = pb_stand + eps, $fn = 32);
        }
        for (sx = [-1, 1]) {
            translate([sx * (x_br - tower_t / 2), duct_len - 1, ebox_screw_z]) rotate([-90, 0, 0]) cylinder(d = 3.4, h = ebox_t + 2, $fn = 24);
            translate([sx * ebox_back_x, ebox_back_y, z_ep0 - 9]) cylinder(d = 2.5, h = 10, $fn = 24);
        }
        for (dx = [-1, 1], dy = [-1, 1])
            translate([dx * pb_holes[0] / 2, pb_y + dy * pb_holes[1] / 2, zb + ebox_t]) cylinder(d = 1.8, h = pb_stand + 1, $fn = 16);
        // USB-C slot in the left wall (+x, seen from the room)
        if (usb_slot[0] > 0)
            translate([ebox_w / 2 - ebox_t - 1, pb_y - usb_slot[0] / 2, zb + usb_z - usb_slot[1] / 2]) cube([ebox_t + 2, usb_slot[0], usb_slot[1]]);
        for (sx = [-1, 1])   // cable entries (clear of the USB-C slot)
            translate([sx < 0 ? x0 - 1 : ebox_w / 2 - ebox_t - 1, duct_len - cable_in[0] - 0.5, z_ep0 - cable_in[1]]) cube([ebox_t + 2, cable_in[0], cable_in[1] + 1]);
    }
}

/* =================== TEST PRINTS (optional) =================== */
// fittest: the housing's printer-sensitive features, modelled in the housing's print
// orientation (fan plate down, so the shaft holes are horizontal). About 20-30 min.
module fittest() {
    wy = 20;   // wall: y from wy to wy + mp_t (same thickness as the motor frame)
    difference() {
        union() {
            cube([60, 34, 3]);                                                // base
            cube([12, 12, fan_plate]);                                        // fan plate pad
            translate([0, wy, 0]) cube([50, mp_t, 22]);                       // wall
            translate([16, 2, 0]) cube([8, 8, 12]);                           // post for the self-tapping pilot
            translate([30, 2, 0]) cube([28, ebox_t, 20]);                     // lip test: upright plate ...
            translate([30, 2 + ebox_t - eps, 12]) cube([28, lip_w, lip_t]);   // ... with a flat 5.6 mm ledge
            translate([0, wy + eps, 0]) rotate([90, 0, 0])                    // AS5600 standoff pad on the wall
                linear_extrude(enc_standoff) hull() for (h = enc_holes) translate([28 + (h - 15) / 2, 12 + (h - 15) / 2]) circle(d = 6, $fn = 32);
        }
        // fan plate: M3 clearance hole + nut pocket (pocket opens upward, as on the housing)
        translate([6, 6, -1]) cylinder(d = 3.4, h = fan_plate + 2, $fn = 24);
        translate([6, 6, fan_plate - 2.6]) cylinder(r = 5.8 / sqrt(3), h = 3, $fn = 6);
        // shaft bearing hole, horizontal
        translate([8, wy - 1, 12]) rotate([-90, 0, 0]) cylinder(d = shaft_d + shaft_clr, h = mp_t + 2, $fn = 32);
        // motor frame: M3 hole crossed by a side nut slot, centred in the wall thickness
        translate([44, wy - 1, 12]) rotate([-90, 0, 0]) cylinder(d = 3.4, h = mp_t + 2, $fn = 24);
        translate([44 - 3.4, wy + (mp_t - 2.8) / 2, 12 - 3.05]) cube([50 - 44 + 3.4 + 1, 2.8, 6.1]);
        // AS5600 diagonal slot, through pad and wall
        translate([0, wy + mp_t + 1, 0]) rotate([90, 0, 0])
            linear_extrude(mp_t + enc_standoff + 2) hull() for (h = enc_holes) translate([28 + (h - 15) / 2, 12 + (h - 15) / 2]) circle(d = 3.2, $fn = 24);
        // self-tapping pilot (as in the box bosses and pillars)
        translate([20, 6, 3]) cylinder(d = 2.5, h = 10, $fn = 24);
        // engraved references (see the table in the README): on the base behind the pad and the post for A and B,
        // on the front faces of the lip plate and the wall for C to F
        for (l = [["A", 6, 16], ["B", 20, 16]])
            translate([l[1], l[2], 3 - 0.6]) linear_extrude(1) fittest_letter(l[0]);
        translate([44, 2 + 0.6, 16]) rotate([90, 0, 0]) linear_extrude(1) fittest_letter("C");
        for (l = [["D", 8], ["E", 28.5], ["F", 44]])
            translate([l[1], wy + 0.6, 19]) rotate([90, 0, 0]) linear_extrude(1) fittest_letter(l[0]);
    }
}
module fittest_letter(t) text(t, size = 4, font = "Liberation Sans:style=Bold", halign = "center", valign = "center");

// oring_test: the stop flange (on the bed) and 15 mm of spigot with one O-ring groove,
// exactly as on the housing. Push it, with an O-ring, into a hole in a foam scrap.
module oring_test() {
    g0 = stop_t + 5;
    difference() {
        union() {
            cylinder(d = stop_od, h = stop_t);
            cylinder(d = sp_od, h = stop_t + 15);
        }
        translate([0, 0, -1]) cylinder(d = duct_id, h = stop_t + 17);
        translate([0, 0, g0]) difference() {
            cylinder(d = sp_od + 2, h = 1.4 * oring_cs);
            translate([0, 0, -1]) cylinder(d = sp_od - 2 * oring_dep * oring_cs, h = 1.4 * oring_cs + 2);
        }
    }
}

/* =================== PREVIEW =================== */
module assembly() {
    color([0.85, 0.85, 0.88]) body();
    for (z = zc) color([0.95, 0.6, 0.25]) disc_installed(z, angle);
    color([0.6, 0.6, 0.62]) translate([0, ys, z_cap1 - 4.6]) cylinder(d = shaft_d, h = 200);   // 200 mm rod, 4.6 mm into the cap
    color([0.3, 0.5, 0.9]) translate([0, ys, z_cap1]) rotate([180, 0, 0]) magnet_cap();
    color([0.55, 0.75, 0.95]) translate([0, ys, z_mp1]) motor_plate();
    color([0.35, 0.4, 0.5]) ebox();
    color([0.15, 0.15, 0.17]) translate([-nema / 2, ys - nema / 2, z_mp1 + mplate_t]) cube([nema, nema, 20]);
    color([0.75, 0.75, 0.3]) translate([0, ys, z_mp0 - 25]) cylinder(d = 19, h = 25);
    color([0.2, 0.55, 0.3]) translate([-11.5, ys - 11.5, z_ep1 + enc_standoff]) cube([23, 23, enc_board]);   // AS5600 board (23 x 23)
    for (z = zc) color([0.2, 0.2, 0.22]) translate([-fan / 2, duct_len, z - fan / 2])
        difference() { cube([fan, fan_t, fan]); translate([fan / 2, -1, fan / 2]) rotate([-90, 0, 0]) cylinder(d = 76, h = fan_t + 2); }
    %translate([-50, -50, -pitch / 2 - 90]) cube([100, 50, pitch + 180]);   // foam insert (ghost)
}

module assembly_nofan() {
    color([0.85, 0.85, 0.88]) body();
    for (z = zc) color([0.95, 0.6, 0.25]) disc_installed(z, angle);
    /*
    color([0.6, 0.6, 0.62]) translate([0, ys, z_cap1 - 4.6]) cylinder(d = shaft_d, h = 200);   // 200 mm rod, 4.6 mm into the cap
    */
    color([0.3, 0.5, 0.9]) translate([0, ys, z_cap1]) rotate([180, 0, 0]) magnet_cap();
    color([0.55, 0.75, 0.95]) translate([0, ys, z_mp1]) motor_plate();
    /*
    color([0.15, 0.15, 0.17]) translate([-nema / 2, ys - nema / 2, z_mp1 + mplate_t]) cube([nema, nema, 20]);
    color([0.75, 0.75, 0.3]) translate([0, ys, z_mp0 - 25]) cylinder(d = 19, h = 25);
    color([0.2, 0.55, 0.3]) translate([-11.5, ys - 11.5, z_ep1 + enc_standoff]) cube([23, 23, enc_board]);   // AS5600 board (23 x 23)
    for (z = zc) color([0.2, 0.2, 0.22]) translate([-fan / 2, duct_len, z - fan / 2])
        difference() { cube([fan, fan_t, fan]); translate([fan / 2, -1, fan / 2]) rotate([-90, 0, 0]) cylinder(d = 76, h = fan_t + 2); }
    %translate([-50, -50, -pitch / 2 - 90]) cube([100, 50, pitch + 180]);   // foam insert (ghost)
    */
}


if (part == "assembly")       assembly();
if (part == "body")           translate([0, 0, duct_len]) rotate([-90, 0, 0]) body();   // fan plate on the bed
if (part == "disc")           disc();
if (part == "motor_plate")    motor_plate();
if (part == "magnet_cap")     magnet_cap();
if (part == "ebox")           translate([0, 0, ebox_h + ebox_t - z_ep0]) ebox();   // floor on the bed
if (part == "fittest")        fittest();
if (part == "oring_test")     oring_test();
if (part == "assembly_nofan") assembly_nofan();
