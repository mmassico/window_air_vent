// =====================================================================
//  Window vent: the audio mode's microphone, listening outdoors through
//  the foam insert
//  Parametric OpenSCAD model (tested with OpenSCAD 2021.01).
//
//  * The MAX9814 module is not weatherproof, so it stays on the room
//    side and only the sound goes through the foam, along an L: the
//    module lies at the top, its capsule pointing down into the tube, so
//    neither rain nor dust settles on it.
//  * Three parts: a straight tube pressed into a 10 mm hole drilled
//    through the foam, standing out of its outdoor face and cut there at
//    45 degrees, its top the longer side: a roof over the opening, which
//    faces down and outward; an elbow on its room end, screwed to the
//    foam, turning up to a tray for the module (the capsule a light press
//    fit in its bore); a lid on the tray, with a notch for the cable to
//    J7.
//  * The elbow prints in two parts, split level with its flange's top
//    and joined by four M2 screws: the lower one lies on its flange, so
//    the tube's socket is a vertical hole; the upper one stands as
//    installed, so the capsule's bore comes out round.
//  * A flat on the tube's room end keys it in the elbow's socket, so the
//    elbow's two screws keep the roof on top. In the foam the tube is
//    round, so it seals all around. Its end bears on the socket's 45
//    degree bottom, and an M2 from the elbow's side, tapped into the
//    tube's wall, holds it there: the tube can't slide away into the
//    foam.
//  * The lid's rim clips into a groove in the tray's walls.
//
//  Installed coordinates: x across the window (along the foam's face),
//  y toward the room (y = 0 on the foam's room face, its outdoor face at
//  y = -foam_t), z up (z = 0 on the tube's axis).
// =====================================================================

/* [Part to show or export] */
part = "mic_view";   // [mic_tube, mic_elbow_lower, mic_elbow_upper, mic_lid, mic_parts, mic_bore_test, mic_view]

/* [Foam] */
foam_t   = 50.8;    // foam thickness (2 in), as in window_caps.scad

/* [Tube] */
tube_od  = 10.4;    // pressed into a 10 mm hole (the XPS gives a little)
tube_id  = 7.0;     // the sound path's bore, from the tube's outdoor end to the capsule
tube_fl  = 0.5;     // the key: a flat on top of the tube's room end (in the socket only), this deep into its circle
tube_out = 12;      // the roof's tip past the foam's outdoor face (the 45 degree cut's bottom edge is tube_od closer)
sock_d   = 9;       // socket depth in the elbow, to its bottom: a 45 degree cone down to the bore, the tube's stop
sock_clr = 0.1;     // clearance per side in the socket: a snug slide
pin      = [6, 1.0];   // the M2 holding the tube in its socket, from the elbow's +x side, tapped into the tube's
                       //   wall: its y, and its head's top this far inside the elbow's side (an M2 x 6 then takes
                       //   the wall's whole 1.7 and ends 0.15 inside the bore)

/* [Microphone module] */
mod_l    = 25.6;    // MAX9814 module (measured, doc/max9814.svg in the main folder): PCB length
mod_w    = 14.3;    //   width
mod_t    = 1.62;    //   thickness
mod_h    = 3.0;     //   tallest part on its back (the chip, the capsule's pins); nothing but the capsule on its front
cap_d    = 9.70;    // capsule: diameter (9.65 to 9.70, depending where it's measured)
cap_h    = 7.38;    //   height above the PCB (9 overall, with the PCB)
cap_e    = 2.10;    //   from its wall to the PCB's near end; centred across the PCB's width
hdr_e    = 1.5;     // the 5-pin header's holes (about 1 across): their centres from the PCB's far end
cap_fit  = 0.3;     // the capsule's bore: this much over its diameter, a light press fit (mic_bore_test tries 0.2 to 0.4;
                    //   0.2 printed tight: it held, but the capsule was hard to take out)
mod_clr  = 0.5;     // at the PCB's ends in the tray (y), per side: the capsule's bore sets its position
mod_side = 1.5;     // beside the PCB in the tray (x), per side: room for tweezers to lift it out

/* [Elbow and lid] */
wall     = 1.6;     // tray walls, lid
fl_t     = 3;       // flange on the foam's face (it is also the tray's back wall)
fl_w     = 43;      // flange width (x), with the screws
floor_z  = 16;      // the tray's floor (the PCB's front face) above the tube's axis: the capsule's bore stays above
                    //   the split
tray_h   = 6;       // tray walls above the floor: the lid's rim stays above the module's parts
screw    = [4.25, 8, 3.5];   // screws into the foam, as the latch cover's: hole, head diameter, head height
csk      = 0.8;     // the countersink's diameter at the flange's face, past the head's (as the latch cover's)
screw_x  = 15.5;    // the screws' x, either side of the tube's axis (at z = 0), their heads clear of the body
notch_w  = 8;       // cable notch in the tray's room-end wall
lid_clr  = 0.1;     // the lid's rim inside the tray's walls, per side
lid_rim  = [0.8, 2.0];   // the lid's rim: width, depth
lid_clip = 0.3;     // a 45 degree ridge on the rim's long sides, this far out, into a groove in the tray's walls: the
                    //   lid clips on (lid_clip - lid_clr of interference per side)

/* [The elbow's joint] */
m2       = [1.6, 2.2, 4.0];   // M2 screws joining the elbow's two parts: tapping hole (lower part), clearance hole
                              //   and head pocket (upper part)
m2_csk   = 2.0;     // the countersink's top (the head's top) above the split: 6 mm screws reach 4 mm into the lower part
m2_tap   = 4.5;     // the tapping holes' depth below the split
m2_at    = [[-6.5, 5.2], [6.5, 5.2], [-6.5, 17], [6.5, 17]];   // the screws: [x, y], clear of the socket, the sound path
                                                           //   and the capsule's bore, the pockets inside the tray

eps = 0.01;
sock_r  = tube_od / 2 + sock_clr;
blk     = sock_r + 2;                           // the elbow's flat bottom at z = -blk; its flange's top, and the
                                                //   split between its two parts, at z = blk
tube_end = sock_d + sock_clr;                   // the tube's room end, where its edge meets the socket's cone
tw      = mod_w + 2 * mod_side;                 // the tray's inside: width (x)
tl      = mod_l + 2 * mod_clr;                  //   and length (y), from the flange
cap_y   = fl_t + mod_clr + cap_e + cap_d / 2;   // the capsule's axis (x = 0)
tray_y  = fl_t + tl + wall;                     // the tray's room end, outside
top_z   = floor_z + tray_h;
clip_z  = top_z - lid_rim[1] / 2;               // the clip's ridge and groove

// a 2D shape (X = x, Y = z) run along y from y0 to y1
module along_y(y0, y1) translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) children();

// a hole along +x from x = 0 to x = l, at y, z = 0 (small enough to print round, lying)
module hole_x(y, d, l) translate([0, y, 0]) rotate([0, 90, 0]) cylinder(d = d, h = l, $fn = 24);

// the clip's 45 degree profile on the face at |x| = x0, on side s: out to x0 + out, h above and below clip_z there
module clip_profile(s, x0, out, h)
    polygon([[s * (x0 - h), clip_z - 2 * h], [s * (x0 + out), clip_z - h + out], [s * (x0 + out), clip_z + h - out],
             [s * (x0 - h), clip_z + 2 * h]]);

// the tube's end in the socket, a D, grown by c: its flat on top
module d_profile(c = 0) intersection() {
    circle(tube_od / 2 + c, $fn = 72);
    translate([-tube_od, -tube_od]) square([2 * tube_od, tube_od + tube_od / 2 - tube_fl + c]);
}

// --- the tube, through the foam ----------------------------------------------------------------------------------
// round in the foam; its room end flat on top, in the socket (the flat starts at 45 degrees, at the foam's face:
// no overhang as printed), with the pin's tapping hole on its +x side; its outdoor end cut at 45 degrees, the top the longer
// side (the plane through the roof's tip, its normal along +y and +z). render(): the preview shows the cuts right
module tube() render() difference() {
    along_y(-foam_t - tube_out, tube_end) difference() { circle(d = tube_od, $fn = 72); circle(d = tube_id, $fn = 48); }
    rotate([90, 0, 90]) linear_extrude(2 * tube_od, center = true)   // 2D: X = y, Y = z
        polygon([[tube_end + 1, tube_od / 2 - tube_fl], [0, tube_od / 2 - tube_fl], [-tube_fl - 1, tube_od / 2 + 1],
                 [tube_end + 1, tube_od / 2 + 1]]);
    hole_x(pin[0], m2[0], tube_od);
    translate([0, -foam_t - tube_out, tube_od / 2]) rotate([45, 0, 0]) translate([-50, -100, -50]) cube(100);
}

// --- the elbow, on the foam's room face --------------------------------------------------------------------------
module elbow() {
    hole = screw[0]; hd = screw[1] + csk; hh = screw[2];
    taper = (screw[1] - hole) / 2 / hh;   // the head's taper: radius per mm of height
    difference() {
        union() {
            // the flange, its bottom flush with the body's (on the bed when printed); round top corners
            along_y(0, fl_t) hull() {
                translate([-fl_w / 2, -blk]) square([fl_w, eps]);
                for (s = [-1, 1]) translate([s * (fl_w / 2 - 3), blk - 3]) circle(3, $fn = 32);
            }
            // the body: the tray's floor and the block around the socket and the riser, hulled (its underside 45
            // degrees or steeper)
            hull() {
                translate([-tw / 2 - wall, 0, floor_z - 2]) cube([tw + 2 * wall, tray_y, 2]);
                translate([-tw / 2 - wall, 0, -blk]) cube([tw + 2 * wall, 20, eps]);
            }
            translate([-tw / 2 - wall, 0, floor_z]) cube([tw + 2 * wall, tray_y, tray_h]);   // the tray's walls
        }
        translate([-tw / 2, fl_t, floor_z]) cube([tw, tl, tray_h + 1]);                     // the tray's inside
        // the socket, and the sound path: along y, then up to the capsule. Below the split, the riser is a teardrop
        // pointing toward the room: the lower part prints lying on its flange, and the teardrop's point is then up
        along_y(-1, sock_d) d_profile(sock_clr);
        translate([0, sock_d - 0.2, 0]) rotate([-90, 0, 0])   // the socket's bottom, 45 degrees: the tube's stop
            cylinder(r1 = sock_r + 0.2, r2 = tube_id / 2 - 0.2, h = sock_r - tube_id / 2 + 0.4, $fn = 72);
        along_y(sock_d - 1, cap_y) circle(d = tube_id, $fn = 48);
        translate([0, cap_y, -tube_id / 2]) linear_extrude(blk + tube_id / 2 + eps) hull() {
            circle(d = tube_id, $fn = 48);
            translate([0, tube_id / 2 * sqrt(2)]) square(eps, center = true);
        }
        translate([0, cap_y, blk]) cylinder(d = tube_id, h = floor_z - blk, $fn = 48);
        // the capsule's bore, 0.3 deeper than the capsule: the PCB bears on the floor
        translate([0, cap_y, floor_z - cap_h - 0.3]) cylinder(d = cap_d + cap_fit, h = cap_h + 1, $fn = 96);
        // a relief under the header's holes, for the solder on the PCB's front
        translate([-6.5, fl_t + mod_clr + mod_l - hdr_e - 1.5, floor_z - 1]) cube([13, 3, 2]);
        // the cable's notch, down to the PCB's back
        translate([-notch_w / 2, tray_y - wall - 1, floor_z + mod_t]) cube([notch_w, wall + 2, tray_h]);
        // the pin: a clearance hole from the +x side into the socket, a countersink and a head pocket
        hole_x(pin[0], m2[1], tw / 2 + wall + 1);
        translate([tw / 2 + wall - pin[1] - (m2[2] - m2[1]) / 2 - 0.2, pin[0], 0]) rotate([0, 90, 0]) {
            cylinder(d1 = m2[1] - 0.4, d2 = m2[2], h = (m2[2] - m2[1]) / 2 + 0.2 + eps, $fn = 32);
            translate([0, 0, (m2[2] - m2[1]) / 2 + 0.2]) cylinder(d = m2[2], h = pin[1] + 2, $fn = 32);
        }
        // the clip's groove, in the tray's long walls
        for (s = [-1, 1]) along_y(fl_t, fl_t + tl) clip_profile(s, tw / 2, lid_clip, 0.45);
        // the screws: a hole, and a countersink with the head's taper, hd wide at the flange's face
        for (s = [-1, 1]) translate([s * screw_x, 0, 0]) rotate([-90, 0, 0]) {
            translate([0, 0, -1]) cylinder(d = hole, h = fl_t + 2, $fn = 32);
            translate([0, 0, fl_t + eps]) mirror([0, 0, 1])
                cylinder(d1 = hd, d2 = hd - 2 * taper * (fl_t + 1), h = fl_t + 1 + eps, $fn = 48);
        }
    }
}

// the two parts, split level with the flange's top: the lower one with the tapping holes, the upper one with the
// clearance holes, countersinks and head pockets (from the tray's floor, under the PCB). render(): the preview
// shows the split right
module elbow_lower() render() difference() {
    intersection() { elbow(); translate([-50, -1, -50]) cube([100, 100, 50 + blk]); }
    for (p = m2_at) translate([p[0], p[1], blk - m2_tap]) cylinder(d = m2[0], h = m2_tap + 1, $fn = 24);
}
module elbow_upper() render() difference() {
    intersection() { elbow(); translate([-50, -1, blk]) cube([100, 100, 50]); }
    for (p = m2_at) translate([p[0], p[1], 0]) {
        translate([0, 0, blk - 1]) cylinder(d = m2[1], h = m2_csk + 1, $fn = 24);
        translate([0, 0, blk + m2_csk - (m2[2] - m2[1]) / 2])
            cylinder(d1 = m2[1], d2 = m2[2], h = (m2[2] - m2[1]) / 2 + eps, $fn = 32);
        translate([0, 0, blk + m2_csk]) cylinder(d = m2[2], h = floor_z, $fn = 32);
    }
}

// --- the lid, on the tray ----------------------------------------------------------------------------------------
module lid() render() union() {
    translate([-tw / 2 - wall, 0, top_z]) cube([tw + 2 * wall, tray_y, wall]);
    difference() {   // a rim inside the walls, open at the cable's notch
        translate([-tw / 2 + lid_clr, fl_t + lid_clr, top_z - lid_rim[1]])
            cube([tw - 2 * lid_clr, tl - 2 * lid_clr, lid_rim[1] + eps]);
        translate([-tw / 2 + lid_clr + lid_rim[0], fl_t + lid_clr + lid_rim[0], top_z - lid_rim[1] - 1])
            cube([tw - 2 * (lid_clr + lid_rim[0]), tl - 2 * (lid_clr + lid_rim[0]), lid_rim[1] + 2]);
        translate([-notch_w / 2, tray_y - wall - 2, top_z - lid_rim[1] - 1]) cube([notch_w, wall + 3, lid_rim[1] + 2]);
    }
    // the clip's ridges, on the rim's long sides, short of its ends so the rim flexes
    for (s = [-1, 1]) intersection() {
        along_y(fl_t + 4, fl_t + tl - 4) clip_profile(s, tw / 2 - lid_clr, lid_clip, 0.45);
        translate([-tw / 2 - 1, 0, top_z - lid_rim[1]]) cube([tw + 2, tray_y, lid_rim[1]]);
    }
}

// --- prints ------------------------------------------------------------------------------------------------------
// the tube stands on its room end, the cut on top; the elbow's lower part lies on its flange (the socket a vertical
// hole), its upper part stands as installed, on the split (the capsule's bore comes out round); the lid lies on its
// top
module tube_print()  translate([0, 0, tube_end]) rotate([-90, 0, 0]) tube();
module elbow_lower_print() rotate([90, 0, 0]) elbow_lower();
module elbow_upper_print() translate([0, 0, -blk]) elbow_upper();
module lid_print()   translate([0, tray_y, top_z + wall]) rotate([180, 0, 0]) lid();

module mic_parts() {
    translate([0, 25, 0]) elbow_lower_print();
    translate([0, 35, 0]) elbow_upper_print();
    translate([fl_w / 2 + tw / 2 + wall + 5, 35, 0]) lid_print();
    translate([fl_w / 2 + tw + 2 * wall + blk + 14, 50, 0]) tube_print();
}

// three bores 0.2, 0.3 and 0.4 over the capsule's diameter, as deep as the elbow's, with a hole below each to push
// the capsule out; the number of notches on the edge beside each tells which
module bore_test() {
    fits = [0.2, 0.3, 0.4];
    p = cap_d + 5;
    difference() {
        cube([3 * p, p, cap_h + 0.3 + 1.5]);
        for (i = [0 : 2]) {
            translate([(i + 0.5) * p, p / 2, 1.5]) cylinder(d = cap_d + fits[i], h = cap_h + 1, $fn = 96);
            translate([(i + 0.5) * p, p / 2, -1]) cylinder(d = 5, h = 5, $fn = 32);
            for (k = [0 : i]) translate([(i + 0.5) * p + (k - i / 2) * 2 - 0.4, -1, 2]) cube([0.8, 1.6, cap_h + 2]);
        }
    }
}

// --- installed, in a piece of the foam (a ghost), with the module -------------------------------------------------
module mic_view() {
    color([0.4, 0.6, 0.9])   elbow_lower();
    color([0.95, 0.6, 0.25]) elbow_upper();
    color([0.9, 0.75, 0.3])  lid();
    color([0.85, 0.85, 0.85]) tube();
    color([0.2, 0.5, 0.3]) translate([-mod_w / 2, fl_t + mod_clr, floor_z]) cube([mod_w, mod_l, mod_t]);
    color([0.3, 0.3, 0.3]) translate([0, cap_y, floor_z - cap_h]) cylinder(d = cap_d, h = cap_h, $fn = 48);
    %difference() {
        translate([-40, -foam_t, -50]) cube([80, foam_t, 100]);
        along_y(-foam_t - 1, 1) circle(d = 10, $fn = 48);
    }
}

if (part == "mic_tube")      tube_print();
if (part == "mic_elbow_lower") elbow_lower_print();
if (part == "mic_elbow_upper") elbow_upper_print();
if (part == "mic_lid")       lid_print();
if (part == "mic_parts")     mic_parts();
if (part == "mic_bore_test") bore_test();
if (part == "mic_view")      mic_view();
