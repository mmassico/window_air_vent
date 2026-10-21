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
part  = "assembly"; // [assembly, body, disc, motor_plate, magnet_cap, ebox, fittest, oring_test, assembly_nofan, body_top, body_bottom, splice, split_view, split_assembly, ebox_elec, ebox_elec_alt]
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
oring_slope = true; // 45 deg groove wall on the spigot-tip side: the spigots print tip up, so that wall would
                    // otherwise be a flat overhang; floor depth (squeeze) and the other wall are unchanged
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
disc_bev = 2;       // 45 deg bevel on the foam-side rim of the disc half that closes against lip B (engraved B);
                    // lip B is a matching 45 deg cone, so neither prints a flat overhang
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
coupler_room = 31;  // space under the frame for a 5-5 mm flexible coupler (19 x 25 mm)
mp_t      = 3;      // motor frame (the tower's roof) thickness, the same as the walls
mplate    = 56;     // motor plate width; it covers the top of the tower from its open back to just past the front screws. The motor screws to it
mplate_t  = 4;      //   on the bench, then it goes on the frame: two screws in front of the motor (M3 x 10 + nuts,
mp_front  = [20, 27];  //   from the tower's open front), at x = +/- [0], [1] in front of the shaft, and two tabs at the back
mp_tab    = [3, 10, 8];  // back tabs (thickness, width, depth below the frame), flush with the back edge: through notches in the frame, against the
                    //   inner faces of the tower walls, one M3 + nut each through the wall
mp_boss   = [6, 2]; // motor screw bosses under the plate (diameter, height): with the 4 mm plate, an M3 x 8 reaches 2 mm
                    //   into the motor, whose holes are 2.5 deep. They sit in the frame's small diamonds
mp_pocket = 8;      // those diamonds, across their flats: 1 mm clear around each boss
tower_t   = 3;      // motor and encoder bracket walls
cap_h     = 12;     // magnet cap on the shaft end
cap_d     = 14;     // wide enough for a radial M3 grub screw
cap_grub_z = 2;     // grub screw height above the cap's shaft end (the shaft reaches about 4.6 mm in)
cap_slide = 1;      // the cap can slide this much up or down before its grub screw is tightened
magnet    = "diametric"; // [diametric:diametric disc lying flat (as sold with AS5600 boards), sideways:2 x 2 mm axial cylinder lying across the shaft]
magnet_d  = 4;      // diametric magnet diameter (the kit magnet measures 3.95 x 2 mm; other kits: 6 x 2.5 or 6 x 3)
magnet_h  = 2;      // diametric magnet thickness
enc_gap   = 1.5;    // nominal magnet face to AS5600 chip top (datasheet: 0.5-3); set on assembly with a shim
enc_chip  = 1.62;   // AS5600 package height above the board (kit board measured: 3.22 with the 1.6 board)
enc_board = 1.6;    // board thickness (measured)
enc_standoff = 2;   // pads lift the board over its solder joints
enc_holes = [15, 17];  // board hole squares supported by the diagonal slots (20 x 20 boards: 15 x 15; the kit
                       // board, 23.3 x 22.8: 16.7 x 16.2, a rectangle, so its screws sit 0.18 off the slot axis)
enc_slot  = 3.5;    // slot width: an M3 screw (3.0) passes even 0.18 off the slot axis
enc_pad   = 5.5;    // standoff pads around the slots (a 1 mm wall around a 3.5 slot)
enc_pad_bev = 1;    // 45 deg flare at the pads' base (they stick out sideways when printing); more would reach the
                    // solder joints under the board's end pins
enc_win   = 13.5;   // wire window: a diamond (point to point) under the chip; the wires soldered to the board
                    // run inward under it (the standoffs leave 2 mm) and down through it

/* [Electronics box and cables] */
ebox_w    = 80;     // box width (= fan width); the encoder plate widens to match and becomes its lid
ebox_h    = 34;     // inside height under the encoder plate (soldered, the TMC2209's heatsink reaches 24.0; in female
                    // headers, 32.5)
ebox_t    = 2.4;    // walls and floor
pb_size   = [70, 50];  // perfboard carrier (5 x 7 cm protoboard)
pb_holes  = [66, 46];  // its corner hole spacing (M2)
pb_y      = 56;     // perfboard centre (y)
pb_stand  = 5;      // standoff height
usb_port  = "diamond"; // [none, mark, diamond] the ESP32's USB-C cable (5 V power and console) through a side wall:
                    // an 18 mm diamond opening, or only an engraved cross to drill a 12 mm hole later
usb_side  = "both"; // [left, right, both] which side wall gets it: both lets one box take either ESP32 layout
esp_usb   = "left"; // [left, right] the ESP32's USB end toward the left wall (view ebox_elec) or the right one
                    // (turned 180 deg, view ebox_elec_alt); shown in the assembly
esp_mount = "soldered"; // [soldered, headers] ESP32 soldered straight into the perfboard, or in female headers
tmc_mount = "soldered"; // [soldered, headers] TMC2209 likewise
header_h  = 8.5;    // female header height
esp_w     = 28.5;   // ESP32 board width; it lies across the back half of the perfboard, USB end toward a side wall
esp_l     = 50;     // ESP32 PCB length (the module's antenna sticks out 7 more, over the middle 18.5)
esp_dy    = 0.5;    // ESP32 edge from the perfboard's back edge
esp_dx    = 7.62;   // its USB end this far in from the side wall (3 perfboard holes): its pins clear the corner
                    // standoff and screw, and the free holes beyond its end are easy to solder. The plug enters the box
esp_pcb   = [1.62, 2.78, 5.54];  // ESP32 PCB thickness, pin spacer, pin length below the spacer (measured)
tmc_pcb   = [21, 15, 1.62];      // TMC2209 module (along x = along its pin rows, along y, thickness; see doc/tmc2209.svg)
tmc_spacer = 2.78;  // its pin spacer (assumed as on the ESP32; to measure)
tmc_pin   = 5.54;   // its pins below the spacer (likewise); 2 rows of 8, 12.7 apart
tmc_sink  = [15, 14.5, 13];     // its heatsink, on top, fins along the pin rows
usb_dy    = 6;      // the USB-UART connector's offset from the board's centre line, toward the room (measured: 8.25 from the
                    // board's TX/GND edge, which faces the room; the USB-OTG one is 5.5 off on the other side)
cable_in  = [16, 10];  // cable entries at the top of both side walls, toward the front (length along y, depth)
anchor_h  = 6;      // tie-wrap anchors: height off the back of the fan plate, to the top of their rounded back (the
                    // wires rest on it). Their slot is house-shaped (floor on the plate, 2 mm straight walls 4.5 apart,
                    // 45 deg roof), so it prints without a flat ceiling

/* [Split housing, for printers under 241 mm (e.g. 180 mm beds)] */
splice_t  = 6;      // splice plate behind the fan plate, in the gap between the ducts
splice_w  = 60;     // its width (x); stays inside the tie-wrap anchors
splice_h  = 32;     // its height (z), before the 1 mm clearance cuts around the ducts
split_sx  = 20;     // joint screws (4 x M3 x 12 countersunk) at x = +/- split_sx ...
split_sz  = 4.5;    //   ... and z = +/- split_sz: in the band between the fans
split_csk = 7;      // 90 deg countersinks for their heads, this wide at the fan face (M3 flat heads: 5.5-6.7); 45 deg walls print from the bed

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
y_sp0  = duct_len - fan_plate - splice_t;  // splice plate back face
ebox_top    = -pitch / 2 - fan / 2;         // the box cover rises to the bottom of the lower fan
ebox_back_x = ebox_w / 2 - 6;               // back fixing screws, outside the bay walls
ebox_back_y = y_br + 6;
ebox_screw_z = z_ep1 + 8;                   // front cover screws: in the bay, above the encoder plate
// electronics heights, above the box's inner floor
pb_top    = pb_stand + 1.6;                                                      // perfboard top
esp_z0    = pb_top + (esp_mount == "headers" ? header_h : 0) + esp_pcb[1];        // ESP32 PCB underside
usb_z     = esp_z0 + esp_pcb[0] + 3.25 / 2;                                     // USB-C socket centre (the diamond's)
tmc_z0    = pb_top + (tmc_mount == "headers" ? header_h : 0) + tmc_spacer;        // TMC2209 PCB underside
esp_yc    = pb_y - pb_size[1] / 2 + esp_dy + esp_w / 2;                           // ESP32 centre line (y)
// tie-wrap anchors on the back of the fan plate, right side: the top and bottom ones touch the
// outer fan nut pockets (hex flat at fan_hole / 2 - 2.9 from the fan centre), the middle one sits between the fans
anchor_zt = pitch / 2 + fan_hole / 2 - 5.8 / 2 - 4;
anchor_z  = [anchor_zt, 0, -anchor_zt];

assert(sqrt(pow(disc_d / 2, 2) + pow(hc, 2)) < r - 0.4, "disc too large to rotate in the bore");

// cylinder along +y, from y0 to y1, centred on (0, z)
module ycyl(y0, y1, d, z = 0, d2 = undef)
    translate([0, y0, z]) rotate([-90, 0, 0]) cylinder(d1 = d, d2 = (d2 == undef ? d : d2), h = y1 - y0);

/* =================== HOUSING =================== */
// O-ring groove cut, as one profile turned around the spigot axis (+z here, toward the spigot tip):
// flat floor from z = 0 to 1.4 cs, straight wall at z = 0, and with oring_slope a 45 deg wall at the tip end.
module oring_groove() {
    rf = sp_od / 2 - oring_dep * oring_cs;   // floor radius
    ro = sp_od / 2 + 1;                      // beyond the spigot surface
    w  = 1.4 * oring_cs;
    rotate_extrude($fn = 96) polygon(oring_slope
        ? [[rf, 0], [ro, 0], [ro, w + (ro - rf)], [rf, w]]
        : [[rf, 0], [ro, 0], [ro, w], [rf, w]]);
}

// AS5600 standoff pad post, along +z from its base: flares 45 deg over its lower enc_pad_bev
module enc_pad_post(extra = 0) {
    cylinder(d1 = enc_pad + 2 * enc_pad_bev, d2 = enc_pad, h = enc_pad_bev + extra, $fn = 32);
    cylinder(d = enc_pad, h = enc_standoff + extra, $fn = 32);
}

// Tie-wrap slot cross-section, in (y, z) once extruded along x with rotate([90, 0, 90]): floor at y = +1 (toward the
// fan plate, i.e. the bed when printing), 2 mm straight walls 4.5 mm apart, and a 45 deg roof peaking at y = -3.25.
module house_slot() polygon([[1, -2.25], [1, 2.25], [-1, 2.25], [-3.25, 0], [-1, -2.25]]);

module duct_outer(z) {
    ycyl(-sp_len, 0, sp_od, z);                                   // spigot
    ycyl(0, stop_t, stop_od, z);                                  // stop ring
    ycyl(stop_t, stop_t + (stop_od / 2 - ro), stop_od, z, 2 * ro);// 45 deg underside (prints without support)
    ycyl(0, duct_len, 2 * ro, z);                                 // damper duct
    for (s = [-1, 1])                                             // shaft bearing bosses: 45 deg cones with a 10 mm flat top
        translate([0, ys, z + s * (r - 0.25)]) mirror([0, 0, s < 0 ? 1 : 0])   // (they stick out sideways when printing)
            cylinder(d1 = 10 + 2 * (wall + boss_h + 0.5), d2 = 10, h = wall + boss_h + 0.5, $fn = 64);
}

module lips(z) {
    // A: x > lip_gap, room side of the closed disc; B: x < -lip_gap, foam side
    ya = ys - hc + disc_t + gasket;
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
    // B: a 45 deg conical seat (it faces the fan plate, i.e. the bed when printing), one gasket thickness
    // (measured square to the slope) from the disc's bevelled rim; a flat land lip_t deep behind its inner edge
    r_in = r - lip_w;
    yc0  = ys - hc + r_in - (disc_d / 2 - disc_bev) - gasket * sqrt(2);   // the cone starts at r_in here
    yc1  = yc0 + (r + 1 - r_in);                                          // and passes the bore wall here
    intersection() {
        translate([-lip_gap - ro, -sp_len, z - ro]) cube([ro, duct_len + sp_len, 2 * ro]);
        difference() {
            ycyl(yc0 - lip_t, yc1, duct_id + 1, z);
            ycyl(yc0 - lip_t - 1, yc0 + eps, 2 * r_in, z);
            ycyl(yc0, yc1 + eps, 2 * r_in, z, 2 * (r + 1));
        }
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

// Square frame on top of the bracket. The motor plate's four screws pass inside the tower walls,
// so their nuts go on from below, in the space under the frame.
module motor_frame() {
    difference() {
        // runs to the fan plate, so it rests on the bed when printing (no bridge)
        translate([-mplate / 2, ys - mplate / 2, z_mp0]) cube([mplate, duct_len - (ys - mplate / 2), mp_t]);
        // diamond openings (pointed up and down when printing, so no bridges): a big one the coupler (19 mm) passes with 2 mm to spare
        // through when the motor goes on, and four small ones for the motor screw bosses and heads under the motor plate
        translate([0, ys, z_mp0 - 1]) linear_extrude(mp_t + 2) rotate(45) square(23.1, center = true);   // flats a little wider than the plate's 22.5 hole
        for (dx = [-1, 1], dy = [-1, 1])
            translate([dx * nema_hole / 2, ys + dy * nema_hole / 2, z_mp0 - 1]) linear_extrude(mp_t + 2) rotate(45) square(mp_pocket, center = true);
        for (sx = [-1, 1]) {
            // front: M3 holes for the plate's two front screws (nuts from the tower's open front, above the fan plate)
            translate([sx * mp_front[0], ys + mp_front[1], z_mp0 - 1]) cylinder(d = 3.4, h = mp_t + 2, $fn = 24);
            // back: notches for the plate's tabs, open at the back edge, against the inner faces of the tower walls
            translate([sx > 0 ? x_br - tower_t - mp_tab[0] - 0.4 : -(x_br - tower_t), y_br - 1, z_mp0 - 1])
                cube([mp_tab[0] + 0.4, mp_tab[1] + 1.4, mp_t + 2]);
        }
    }
}

// Modelled with the motor axis at the origin, the plate's underside at z = 0 (installed: on top of the frame).
// The motor screws to it from below (4 x M3 x 8 through bosses under the plate: the motor's holes are 2.5 deep; the
// bosses and heads go down through the frame's small diamonds); it covers the top of the
// tower from its open back to just past the front screws. Front: two M3 x 10 + nuts through the frame. Back: two tabs down through the frame, against the
// inner faces of the tower walls, each held by an M3 x 10 through the wall with a nut inside.
module motor_plate() {
    y0 = y_br - ys;                  // back edge (the tower's open back)
    y1 = mp_front[1] + 6;            // front edge: 6 mm past the front screws (the roof carries on to the fan plate)
    difference() {
        union() {
            translate([-mplate / 2, y0, 0]) cube([mplate, y1 - y0, mplate_t]);
            for (dx = [-1, 1], dy = [-1, 1])   // motor screw bosses (they print upward: the plate prints top face down)
                translate([dx * nema_hole / 2, dy * nema_hole / 2, -mp_boss[1]]) cylinder(d = mp_boss[0], h = mp_boss[1] + eps, $fn = 32);
            for (sx = [-1, 1])
                translate([sx > 0 ? x_br - tower_t - mp_tab[0] - 0.2 : -(x_br - tower_t - 0.2), y0, -(mp_t + mp_tab[2])])
                    cube([mp_tab[0], mp_tab[1], mp_t + mp_tab[2] + eps]);
        }
        translate([0, 0, -1]) cylinder(d = nema_boss + 0.5, h = mplate_t + 2);
        for (dx = [-1, 1], dy = [-1, 1])
            translate([dx * nema_hole / 2, dy * nema_hole / 2, -mp_boss[1] - 1]) cylinder(d = 3.4, h = mplate_t + mp_boss[1] + 2, $fn = 24);
        for (sx = [-1, 1]) {
            translate([sx * mp_front[0], mp_front[1], -1]) cylinder(d = 3.4, h = mplate_t + 2, $fn = 24);
            // tab screw, across the tab (along x), level with the wall hole
            translate([sx * (x_br - tower_t - mp_tab[0] / 2) - mp_tab[0], y0 + mp_tab[1] / 2, -(mp_t + mp_tab[2] / 2)])
                rotate([0, 90, 0]) cylinder(d = 3.4, h = 2 * mp_tab[0], $fn = 24);
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
                    for (sx = [-1, 1], z = anchor_z)   // tie-wrap anchors on both sides (cables on the right, -x, by default):
                                                       // 8 wide, walls up to anchor_h - 4, then a half-cylinder back
                        translate([sx < 0 ? -fan / 2 : fan / 2 - 7, duct_len - fan_plate, z]) rotate([90, 0, 90]) linear_extrude(7)
                            hull() {
                                translate([-(anchor_h - 4), 0]) circle(r = 4, $fn = 48);
                                translate([-(anchor_h - 4), -4]) square([anchor_h - 4 + eps, 8]);
                            }
                    for (dx = [-1, 1], dy = [-1, 1]) hull() for (h = enc_holes)   // standoff pads under the board corners
                        translate([dx * h / 2, ys + dy * h / 2, z_ep1 - eps]) enc_pad_post(eps);
                }
                for (z = zc) {
                    ycyl(-sp_len - 1, duct_len + 1, duct_id, z);                     // bore
                    for (p = oring_pos)                                               // O-ring grooves (spigot tip toward -y)
                        translate([0, -p, z]) rotate([90, 0, 0]) oring_groove();
                    for (dx = [-1, 1], dz = [-1, 1]) {                                 // fan screws + M3 nut pockets
                        translate([dx * fan_hole / 2, duct_len - fan_plate - 1, z + dz * fan_hole / 2]) rotate([-90, 0, 0]) cylinder(d = 3.4, h = fan_plate + 2, $fn = 24);
                        translate([dx * fan_hole / 2, duct_len - fan_plate - eps, z + dz * fan_hole / 2]) rotate([-90, 0, 0]) cylinder(r = 5.8 / sqrt(3), h = 2.6, $fn = 6);
                    }
                }
                // encoder plate: diagonal slots for both AS5600 board sizes (M3 or smaller screws)
                for (dx = [-1, 1], dy = [-1, 1]) hull() for (h = enc_holes)
                    translate([dx * h / 2, ys + dy * h / 2, z_ep0 - 1]) cylinder(d = enc_slot, h = z_ep1 - z_ep0 + enc_standoff + 2, $fn = 24);
                // wire window: a diamond under the chip (pointed up and down when printing)
                translate([0, ys, z_ep0 - 1]) linear_extrude(z_ep1 - z_ep0 + 2) rotate(45) square(enc_win / sqrt(2), center = true);
                // box fixing: cover screws into the front bosses (self-tapping M3), and two M3 from above at the back
                for (sx = [-1, 1]) {
                    translate([sx * (x_br - tower_t / 2), duct_len + 1, ebox_screw_z]) rotate([90, 0, 0]) cylinder(d = 2.5, h = 9, $fn = 24);
                    translate([sx * ebox_back_x, ebox_back_y, z_ep0 - 1]) cylinder(d = 3.4, h = z_ep1 - z_ep0 + 2, $fn = 24);
                }
                // airflow arrows: intake (upper duct) toward the room, exhaust (lower duct) toward the foam,
                // centred in the band between each diamond window and its duct
                flow_arrows((z_top + boss_h + pitch / 2 + sqrt(ro * ro - x_br * x_br)) / 2, 1);
                flow_arrows(-(z_top + boss_h + pitch / 2 + sqrt(ro * ro - x_br * x_br)) / 2, -1);
                for (sx = [-1, 1])   // M3 clearance holes for the motor plate's back tabs, through the tower walls
                    translate([sx * (x_br - tower_t / 2) - tower_t, y_br + mp_tab[1] / 2, z_mp0 - mp_tab[2] / 2])
                        rotate([0, 90, 0]) cylinder(d = 3.4, h = 2 * tower_t, $fn = 24);
                for (sx = [-1, 1])   // tie-wrap slot near the back edge of each motor tower wall, level with the bottom
                                     // tip of its diamond window; house-shaped, roof toward the back edge (up when printing),
                                     // leaving a 3 mm strip behind the peak for the tie to wrap around
                    translate([sx * (x_br - tower_t / 2) - (tower_t + 2) / 2, y_br + 3 + 3.25, z_top + boss_h + 2 + 2.25]) rotate([90, 0, 90])
                        linear_extrude(tower_t + 2) house_slot();
                for (sx = [-1, 1], z = anchor_z)   // tie-wrap slot through each anchor, across the cable run: house-shaped,
                                                   // its roof pointing away from the fan plate (up when printing)
                    translate([sx < 0 ? -fan / 2 - 1 : fan / 2 - 8, duct_len - fan_plate - 0.8, z]) rotate([90, 0, 90])
                        linear_extrude(9) house_slot();   // floor 0.2 mm into the plate, so no faces coincide
            }
            // inside the bores
            for (z = zc) {
                lips(z);
                drip_dam(z);
                for (s = [-1, 1]) intersection() {   // shaft bosses, floor and ceiling: a cylinder from the bore wall,
                                                     // cut by the bore-axis cylinder
                    difference() {
                        translate([0, ys, z + s * (r + 1)]) mirror([0, 0, s > 0 ? 1 : 0]) cylinder(d = sboss_d, h = r + 1, $fn = 48);
                        // 45 deg plane cut on the fan-plate side only: that side faces the bed when printing.
                        // The footprint on the bore wall stays sboss_d, so water and air see the same boss.
                        translate([0, ys + sboss_d / 2, z + s * r]) mirror([0, 0, s > 0 ? 1 : 0])
                            rotate([-45, 0, 0]) translate([-50, -50, 0]) cube([100, 100, 50]);
                        // floor only: a water channel past the end of lip B (x = -lip_gap). The conical lip reaches
                        // the boss along the floor, so the boss gives way within 3 mm of the lip end, up to 3 mm past
                        // the lip on the fan side; it keeps a 1.3 mm rim around the shaft hole
                        if (s < 0) translate([-(lip_gap + 3), ys - sboss_d, z - r - 1]) cube([6, sboss_d + 2, sboss_d / 2]);
                    }
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

/* =================== SPLIT HOUSING (printers under 241 mm) =================== */
// The housing cut at z = 0, midway between the ducts. In that band only the fan plate joins
// the two ducts, so a splice plate on its back, in the gap between the ducts, joins the halves
// again: 4 x M3 x 12 countersunk from the fan face (between the two fans, heads flush) into nuts in the splice.
// Each half prints like the full housing, fan plate on the bed.
module split_screws()
    for (sx = [-1, 1], sz = [-1, 1])
        translate([sx * split_sx, y_sp0 - 1, sz * split_sz]) rotate([-90, 0, 0]) {
            cylinder(d = 3.4, h = splice_t + fan_plate + 2, $fn = 24);
            translate([0, 0, splice_t + fan_plate + 1 - (split_csk - 3.4) / 2]) {   // 90 deg countersink, open at the fan face
                cylinder(d1 = 3.4, d2 = split_csk, h = (split_csk - 3.4) / 2, $fn = 32);
                translate([0, 0, (split_csk - 3.4) / 2 - eps]) cylinder(d = split_csk, h = 1, $fn = 32);
            }
        }

// The middle tie-wrap anchors (z = -4 to 4) stay whole on the upper half: under each one, the cut
// steps down to z = -5 (1 mm below the anchor, so no faces coincide), so the upper half keeps the fan
// plate under the anchor and it still prints from the bed.
module mid_anchor_zone()
    for (sx = [-1, 1])
        translate([sx < 0 ? -fan / 2 - 1 : fan / 2 - 8, duct_len - fan_plate - anchor_h - 1, -5]) cube([9, fan_plate + anchor_h + 2, 6]);   // to z = +1: no face in the cut plane

module body_half(upper) intersection() {
    difference() { body(); split_screws(); }
    if (upper) union() { translate([-100, -50, 0]) cube([200, 200, 300]); mid_anchor_zone(); }
    else difference() { translate([-100, -50, -300]) cube([200, 200, 300]); mid_anchor_zone(); }
}

module splice() {   // modelled in place (installed coordinates)
    difference() {
        translate([-splice_w / 2, y_sp0, -splice_h / 2]) cube([splice_w, splice_t, splice_h]);
        for (z = zc) ycyl(y_sp0 - 1, duct_len, 2 * (ro + 1), z);   // 1 mm clear of both ducts
        split_screws();
        for (sx = [-1, 1], sz = [-1, 1])   // M3 nut pockets on its back face
            translate([sx * split_sx, y_sp0 - eps, sz * split_sz]) rotate([-90, 0, 0]) cylinder(r = 5.8 / sqrt(3), h = 2.6, $fn = 6);
    }
}

// Exploded view: halves pulled apart, splice pulled back toward the foam, screws in front of the fan plate.
module split_view(gap = 36, back = 30) {
    color([0.85, 0.85, 0.88]) translate([0, 0, gap / 2]) body_half(true);
    color([0.75, 0.78, 0.85]) translate([0, 0, -gap / 2]) body_half(false);
    color([0.95, 0.6, 0.25]) translate([0, -back, 0]) splice();
    for (sx = [-1, 1], sz = [-1, 1]) color([0.25, 0.25, 0.27])
        translate([sx * split_sx, duct_len + 20, sz * (split_sz + gap / 2)]) rotate([-90, 0, 0]) {
            cylinder(d = 3, h = 10.3, $fn = 16);
            translate([0, 0, 10.3]) cylinder(d1 = 3, d2 = 6, h = 1.7, $fn = 24);   // flat (countersunk) head
        }
}

// The same parts assembled, with the four countersunk M3 x 12 (heads flush in the fan face, tips at the back of the
// splice) and their nuts in the splice's pockets.
module split_assembly() {
    color([0.85, 0.85, 0.88]) body_half(true);
    color([0.75, 0.78, 0.85]) body_half(false);
    color([0.95, 0.6, 0.25]) splice();
    for (sx = [-1, 1], sz = [-1, 1]) translate([sx * split_sx, 0, sz * split_sz]) {
        color([0.25, 0.25, 0.27]) translate([0, duct_len - 12, 0]) rotate([-90, 0, 0]) {
            cylinder(d = 3, h = 10.3, $fn = 16);
            translate([0, 0, 10.3]) cylinder(d1 = 3, d2 = 6, h = 1.7, $fn = 24);   // flat head
        }
        color([0.7, 0.7, 0.72]) translate([0, y_sp0, 0]) rotate([-90, 0, 0])   // M3 nut (5.5 across flats, 2.4 thick)
            difference() { cylinder(r = 5.5 / sqrt(3), h = 2.4, $fn = 6); translate([0, 0, -1]) cylinder(d = 3, h = 5, $fn = 16); }
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
        // shaft bore: a teardrop, 45 deg point up (toward the grub screws), so it prints without support; the
        // grub screws press the shaft into its round lower half
        translate([0, 50, hc]) rotate([90, 0, 0]) linear_extrude(100) hull() {
            circle(d = shaft_d + 0.2, $fn = 32);
            translate([0, (shaft_d + 0.2) / 2 * sqrt(2)]) square(0.01, center = true);
        }
        // half B (x > 0 here, the half that closes against the conical lip B): 45 deg bevel on the bed-side rim
        difference() {
            translate([0, -disc_d, -1]) cube([disc_d, 2 * disc_d, disc_bev + 1]);
            translate([0, 0, -1]) cylinder(r1 = disc_d / 2 - disc_bev - 1, r2 = disc_d / 2, h = disc_bev + 1);
        }
        translate([20, 0, disc_t - 0.6]) linear_extrude(1) rotate(90) fittest_letter_big("B");   // marks half B
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
// perfboard on four standoffs, carrying the ESP32 and the TMC2209 (soldered, or in female headers).
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
        // USB-C cable through the left wall (+x, seen from the room): a 45 deg diamond (points up and down when printing) that passes
        // an 11 x 6.25 mm plug, or an engraved cross marking where to drill
        // (left wall), or the right wall with the ESP32 turned 180 deg, so the connector lands on the other side
        // of the board's centre line
        for (sx = [-1, 1]) if (usb_side == "both" || (sx > 0) == (usb_side == "left")) {
            usb_y = esp_yc + sx * usb_dy;
            if (usb_port == "diamond")
                translate([sx > 0 ? ebox_w / 2 - ebox_t - 1 : x0 - 1, usb_y, zb + ebox_t + usb_z]) rotate([0, 90, 0])
                    linear_extrude(ebox_t + 2) rotate(45) square(18 / sqrt(2), center = true);
            if (usb_port == "mark")
                for (r = [0, 90]) translate([sx * ebox_w / 2, usb_y, zb + ebox_t + usb_z]) rotate([r, 0, 0])
                    cube([1.2, 8, 1], center = true);   // 0.6 deep into the outer face
        }
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
            translate([30, 2 + ebox_t - eps, 0]) rotate([90, 0, 90]) linear_extrude(28)   // ... with a 5.6 mm ledge,
                polygon([[0, 12 - lip_w], [lip_w, 12], [lip_w, 12 + lip_t], [0, 12 + lip_t]]);   // 45 deg underside like lip B
            translate([0, wy + eps, 0]) rotate([90, 0, 0])                    // AS5600 standoff pad on the wall
                hull() for (h = enc_holes) translate([28 + (h - 15) / 2, 12 + (h - 15) / 2, 0]) enc_pad_post(eps);
        }
        // fan plate: M3 clearance hole + nut pocket (pocket opens upward, as on the housing)
        translate([6, 6, -1]) cylinder(d = 3.4, h = fan_plate + 2, $fn = 24);
        translate([6, 6, fan_plate - 2.6]) cylinder(r = 5.8 / sqrt(3), h = 3, $fn = 6);
        // shaft bearing hole, horizontal
        translate([8, wy - 1, 12]) rotate([-90, 0, 0]) cylinder(d = shaft_d + shaft_clr, h = mp_t + 2, $fn = 32);
        // motor frame: M3 clearance hole, horizontal when printing
        translate([44, wy - 1, 12]) rotate([-90, 0, 0]) cylinder(d = 3.4, h = mp_t + 2, $fn = 24);
        // AS5600 diagonal slot, through pad and wall
        translate([0, wy + mp_t + 1, 0]) rotate([90, 0, 0])
            linear_extrude(mp_t + enc_standoff + 2) hull() for (h = enc_holes) translate([28 + (h - 15) / 2, 12 + (h - 15) / 2]) circle(d = enc_slot, $fn = 24);
        // self-tapping pilot (as in the box bosses and pillars)
        translate([20, 6, 3]) cylinder(d = 2.5, h = 10, $fn = 24);
        // split housing joint: M3 hole with a 90 deg countersink opening on the bed, as in the fan face
        translate([54, 29, -1]) cylinder(d = 3.4, h = 5, $fn = 24);
        translate([54, 29, -eps]) cylinder(d1 = split_csk, d2 = 3.4, h = (split_csk - 3.4) / 2, $fn = 32);
        // engraved references (see the table in the README): on the base behind the pad and the post for A and B,
        // on the front faces of the lip plate and the wall for C to F
        for (l = [["A", 6, 16], ["B", 20, 16], ["G", 54, 23]])
            translate([l[1], l[2], 3 - 0.6]) linear_extrude(1) fittest_letter(l[0]);
        translate([44, 2 + 0.6, 16]) rotate([90, 0, 0]) linear_extrude(1) fittest_letter("C");
        for (l = [["D", 8], ["E", 28.5], ["F", 44]])
            translate([l[1], wy + 0.6, 19]) rotate([90, 0, 0]) linear_extrude(1) fittest_letter(l[0]);
    }
}
module fittest_letter(t) text(t, size = 4, font = "Liberation Sans:style=Bold", halign = "center", valign = "center");
module fittest_letter_big(t) text(t, size = 8, font = "Liberation Sans:style=Bold", halign = "center", valign = "center");

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
        translate([0, 0, g0]) oring_groove();   // the same groove as on the housing (the tip is up here too)
    }
}

/* =================== PREVIEW =================== */
// Electronics in the box, for the preview and the clearance check (installed coordinates): perfboard, ESP32-S3
// (PCB, module and antenna, USB-C sockets, pins), its USB-C plug through the left wall, TMC2209 with its heatsink.
module electronics(usb = esp_usb) {
    fl  = z_ep0 - ebox_h;                                   // inner floor
    x1  = ebox_w / 2 - ebox_t - 0.5 - esp_dx;               // ESP32 USB end (left layout)
    yc  = esp_yc;
    zp  = fl + esp_z0;                                      // ESP32 PCB underside
    color([0.8, 0.68, 0.4]) translate([-pb_size[0] / 2, pb_y - pb_size[1] / 2, fl + pb_stand + 0.01]) cube([pb_size[0], pb_size[1], 1.6]);   // just clear of the standoffs
    // the ESP32 and its plug, drawn USB end left; the right layout turns them 180 deg about the board's centre line
    translate([0, yc, 0]) rotate(usb == "right" ? 180 : 0) translate([0, -yc, 0]) {
        color([0.85, 0.27, 0.23]) translate([x1 - esp_l, yc - esp_w / 2, zp]) cube([esp_l, esp_w, esp_pcb[0]]);
        color([0.17, 0.17, 0.17]) translate([x1 - esp_l - 7, yc - 9.25, zp + esp_pcb[0]]) cube([25.5, 18.5, 4.85 - esp_pcb[0]]);   // module + antenna
        for (dy = [-5.5, usb_dy]) color([0.75, 0.75, 0.75]) translate([x1 - 7.5, yc + dy - 4.5, zp + esp_pcb[0]]) cube([7.8, 9, 3.25]);
        for (sy = [-1, 1], i = [0 : 19])                    // pins (rows 25.3 apart)
            color([0.95, 0.8, 0.3]) translate([x1 - (esp_l - 19 * 2.54) / 2 - i * 2.54 - 0.32, yc + sy * 12.65 - 0.32, zp - esp_pcb[1] - esp_pcb[2]])
                cube([0.64, 0.64, esp_pcb[2] + esp_pcb[1] + esp_pcb[0] + 1]);
        for (sy = [-1, 1]) color([0.25, 0.25, 0.25]) translate([x1 - esp_l + 0.4, yc + sy * 12.65 - 1.25, zp - esp_pcb[1]]) cube([esp_l - 0.8, 2.5, esp_pcb[1]]);
        color([0.4, 0.4, 0.42]) translate([x1 + 0.3, yc + usb_dy - 5.5, fl + usb_z - 3.125]) cube([ebox_w / 2 - x1 + 20, 11, 6.25]);   // USB-C plug
        if (esp_mount == "headers")
            for (sy = [-1, 1]) color([0.1, 0.1, 0.1]) translate([x1 - esp_l + 0.4, yc + sy * 12.65 - 1.25, fl + pb_top]) cube([esp_l - 0.8, 2.5, header_h]);
    }
    tx0 = -pb_size[0] / 2 + 12.5;                           // TMC2209, front right (see doc/ebox_layout.svg)
    ty0 = yc + esp_w / 2 + 1;
    color([0.1, 0.1, 0.1]) translate([tx0, ty0, fl + tmc_z0]) cube(tmc_pcb);
    color([0.2, 0.35, 0.8]) translate([tx0 + (tmc_pcb[0] - tmc_sink[0]) / 2, ty0 + (tmc_pcb[1] - tmc_sink[1]) / 2, fl + tmc_z0 + tmc_pcb[2]]) cube(tmc_sink);
    for (sy = [-1, 1]) {                                    // its pin rows: spacer, pins (into the headers or the perfboard), headers
        ry = ty0 + tmc_pcb[1] / 2 + sy * 6.35;
        color([0.25, 0.25, 0.25]) translate([tx0 + 0.4, ry - 1.25, fl + tmc_z0 - tmc_spacer]) cube([tmc_pcb[0] - 0.8, 2.5, tmc_spacer]);
        for (i = [0 : 7])
            color([0.95, 0.8, 0.3]) translate([tx0 + (tmc_pcb[0] - 7 * 2.54) / 2 + i * 2.54 - 0.32, ry - 0.32, fl + tmc_z0 - tmc_spacer - tmc_pin])
                cube([0.64, 0.64, tmc_pin + tmc_spacer + tmc_pcb[2]]);
        if (tmc_mount == "headers")
            color([0.1, 0.1, 0.1]) difference() {             // female header, hollow so the pins show inside
                translate([tx0 + 0.4, ry - 1.25, fl + pb_top]) cube([tmc_pcb[0] - 0.8, 2.5, header_h]);
                for (i = [0 : 7]) translate([tx0 + (tmc_pcb[0] - 7 * 2.54) / 2 + i * 2.54 - 0.5, ry - 0.5, fl + pb_top + 1]) cube([1, 1, header_h]);
            }
    }
}

module assembly() {
    color([0.85, 0.85, 0.88]) body();
    for (z = zc) color([0.95, 0.6, 0.25]) disc_installed(z, angle);
    color([0.6, 0.6, 0.62]) translate([0, ys, z_cap1 - 4.6]) cylinder(d = shaft_d, h = 200);   // 200 mm rod, 4.6 mm into the cap
    color([0.3, 0.5, 0.9]) translate([0, ys, z_cap1]) rotate([180, 0, 0]) magnet_cap();
    color([0.55, 0.75, 0.95]) translate([0, ys, z_mp1]) motor_plate();
    color([0.35, 0.4, 0.5]) ebox();
    electronics();
    color([0.15, 0.15, 0.17]) translate([-nema / 2, ys - nema / 2, z_mp1 + mplate_t]) cube([nema, nema, 20]);
    color([0.75, 0.75, 0.3]) translate([0, ys, z_mp0 - 25]) cylinder(d = 19, h = 25);
    color([0.2, 0.55, 0.3]) translate([-11.65, ys - 11.4, z_ep1 + enc_standoff]) cube([23.3, 22.8, enc_board]);   // AS5600 kit board
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
    color([0.2, 0.55, 0.3]) translate([-11.65, ys - 11.4, z_ep1 + enc_standoff]) cube([23.3, 22.8, enc_board]);   // AS5600 kit board
    for (z = zc) color([0.2, 0.2, 0.22]) translate([-fan / 2, duct_len, z - fan / 2])
        difference() { cube([fan, fan_t, fan]); translate([fan / 2, -1, fan / 2]) rotate([-90, 0, 0]) cylinder(d = 76, h = fan_t + 2); }
    %translate([-50, -50, -pitch / 2 - 90]) cube([100, 50, pitch + 180]);   // foam insert (ghost)
    */
}


if (part == "assembly")       assembly();
if (part == "body")           translate([0, 0, duct_len]) rotate([-90, 0, 0]) body();   // fan plate on the bed
if (part == "disc")           disc();
if (part == "motor_plate")    translate([0, 0, mplate_t]) rotate([180, 0, 0]) motor_plate();   // top face on the bed, tabs up
if (part == "magnet_cap")     magnet_cap();
if (part == "ebox")           translate([0, 0, ebox_h + ebox_t - z_ep0]) ebox();   // floor on the bed
if (part == "fittest")        fittest();
if (part == "oring_test")     oring_test();
if (part == "assembly_nofan") assembly_nofan();
if (part == "body_top")       translate([0, 0, duct_len]) rotate([-90, 0, 0]) body_half(true);    // fan plate on the bed
if (part == "body_bottom")    translate([0, 0, duct_len]) rotate([-90, 0, 0]) body_half(false);   // fan plate on the bed
if (part == "splice")         translate([0, 0, duct_len - fan_plate]) rotate([-90, 0, 0]) splice();   // nut pockets up (no bridging)
if (part == "split_view")     split_view();
if (part == "split_assembly") split_assembly();
if (part == "ebox_elec")      { color([0.35, 0.4, 0.5]) ebox(); electronics("left"); }    // the box and its boards, installed coordinates
if (part == "ebox_elec_alt")  { color([0.35, 0.4, 0.5]) ebox(); electronics("right"); }   // the same, ESP32 USB end toward the right wall
