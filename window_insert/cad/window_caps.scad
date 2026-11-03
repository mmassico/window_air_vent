// =====================================================================
//  Window vent: printed edge caps around the foam insert (fit tests)
//  Parametric OpenSCAD model (tested with OpenSCAD 2021.01).
//
//  * The foam insert (XPS, 2 in thick, 100 mm wide) fills the gap
//    between the sliding sash and the window's side frame. Printed caps
//    on its four edges fit the window's profiles, so the foam itself
//    stays a plain rectangle:
//      - top:    over the top frame's two ribs;
//      - bottom: over the bottom track's two rails;
//      - side:   a tongue into the side frame's sash channel;
//      - sash:   a channel that takes the sash's end, as the side frame
//                does, with a tongue in the sash's end groove.
//  * Fit tests first: a thin slice of each profile, to check the
//    profiles and the clearance; then the cap ends that meet in the four
//    corners; then a joint between two segments of the side and sash
//    caps.
//  * The side and sash caps are too long for the printer: they print in
//    segments, joined by separate joiners that snap into a socket in
//    each segment's end (a bump on the joiner clicks into a window in a
//    tab of the socket's wall). The top and bottom caps print in one
//    piece each.
//  * Installation, like a drawer: open the sash wide; push the side cap
//    into the side frame's channel; set the bottom and top caps on their
//    rails and ribs a little away from the side frame and slide them
//    against it; slide the foam in sideways, between their lips, into
//    the side cap; put the sash cap on the foam's other edge; close the
//    sash against it. Nothing is glued: reverse it in spring.
//  * The top and bottom caps run the whole width, from the side frame's
//    face to the sash's end. The side and sash caps fit between them,
//    and the top and bottom caps' lips straddle their ends. The side
//    cap's tongue goes on into the channel up to the ceiling and down to
//    the floor, notched for the centre rib and rail (they run through
//    the channel to its back wall) and for the soft foam strip there.
//
//  Slices: x across the foam's thickness (u, from its centre, outdoor
//  negative), y from the window's reference surface toward the foam
//  (the ceiling, the track floor, the side frame's face or the sash's
//  end face), z through the slice. The window's features are at y < 0
//  for the side and the sash, and cut into the slice from y = 0 for the
//  top and the bottom.
//
//  Caps, installed: x across the window (x = 0 on the side frame's face,
//  toward the sash), y = u, z up (z = 0 on the track's floor).
//
//  Each slice ends in a tab exactly as wide as the foam: its edges show
//  where the foam's faces are, and the engraved line across it shows
//  where the foam starts. The tabs carry a cross-lap key: in a corner, a
//  top or bottom slice and a side or sash slice slot together (sliding
//  along u until both slots bottom out), so their u positions must
//  match for the pair to sit in the corner.
// =====================================================================

/* [Part to show or export] */
part = "joint_tests";   // [cap_top, cap_bottom, side_0a, side_0b, side_1a, side_1b, side_2a, side_2b, side_3a, side_3b, side_4a, side_4b, sash_0a, sash_0b, sash_1a, sash_1b, sash_2a, sash_2b, sash_3a, sash_3b, sash_4a, sash_4b, joiner_side, joiner_sash, joiners, joint_tests, snap_test, joint_side_lower, joint_side_upper, joint_sash_lower, joint_sash_upper, joint_view, assembly_view, corners, corner_top, corner_bottom, corner_side_top, corner_side_bottom, corner_sash_top, corner_sash_bottom, latch_slice, corners_view, slices, slice_top, slice_bottom, slice_side, slice_sash, slice_pair_view, latch_cover, latch_cover_view]

/* [Fit] */
clr      = 0.3;     // clearance per side on the window's ribs, channel and sash
clr_d    = 0.5;     // clearance at the bottom of a slot or channel (depth)
slice_t  = 5;       // slice thickness
base     = 3;       // cap material between the deepest window feature and the foam

cap_gap  = 0.5;     // between a cap's end and the cap it butts against (foam tape)
foam_clr = 0.2;     // per side, between the foam and the lips (it slides in)

/* [Foam] */
foam_t   = 50.8;    // foam thickness (2 in)
foam_w   = 112;     // foam width, side frame to sash: 96 uncovered between the side and sash caps' lips, for
                    //   the vent's chassis (at least 90 wide); the sash stays open 118 (security)

/* [Caps] */
lip_d    = 8;       // how far the lips reach onto the foam's faces
lip_t    = 4.8;     // lip thickness
corner_l = 40;      // corner test pieces: length past the cap they butt against
latch_t  = 3;       // latch test slice: thickness

/* [Joints] */
splits   = [216, 432, 648, 864];  // heights of the joints between the side and sash caps' segments: 5 segments,
                                  //   numbered 0 to 4 from the floor, each under 256 mm in its print orientation
halves   = true;    // print each segment in two halves, a and b from the floor, joined at its middle: a 215 mm
                    //   segment standing on its end can be knocked off the bed near its top. The halves keep the
                    //   whole segments' joints, so they mix with whole segments already printed (halves = false)
j_d      = [15, 25]; // socket depth into each segment's end (to the eaves of its roof, see socket()): side cap, sash
                     //   cap. The sash cap's tab is its socket's whole outer wall but for 2 mm a side, so its joiner
                     //   goes deeper, to bear on a rigid wall well past the tab: the joint then won't rock
j_wall   = 1.6;     // socket wall on the snap tab's face: the tab's thickness
j_clr    = 0.1;     // clearance per side around the joiner
j_tab    = [11.6, 13]; // snap tab: width (the sash cap's 14.0 socket, less the slits, allows 12.4), length from
                       //   the segment's end. Wider than the first joint test's 8 x 12, for more material beside the
                       //   window; longer, for about the same flex (0.88 to 1.10 times, wherever the bump pushes) and
                       //   less strain at its root (0.73 to 0.85 times), where it bends across the layers
j_slit   = 0.8;     // slit on each side of the tab
j_win    = [6, 4];  // window in the tab, a diamond (45 degree edges: no bridge when printed standing): width and
                    //   height, distance of its near corner from the segment's end
j_bump   = 1.0;     // bump on the joiner (the tab flexes j_bump - j_clr as it snaps over)
j_catch  = 0.2;     // axial play between the bump's catch and the window's: how far each side of a joint opens when
                    //   pulled
j_end    = 0.1;     // play between each end of the joiner and its socket's roof (keep it under j_catch: a joiner
                    //   pushed to the bottom of one socket must still let the other one's tab snap in)
j_ch     = 0.6;     // chamfer at the socket's mouth (lead-in, and room for the elephant's foot)
joint_l  = [24, 35]; // joint test pieces: length of each segment end (past the socket's roof): side cap, sash cap
explode  = 0;       // assembly_view: gap between the pieces along the height (0: assembled)

/* [Latch cover] */
// a liner for the foam's notch at the window latch, behind the latch: a flat floor just outdoor of the latch zone,
// 45 degree risers out to the foam's room face (they carry on the side cap's relief across the foam), and a border
// on that face, screwed into the foam. Its end against the side cap is open and straight, the cap's lip notched out
// of the border's corners there. The foam's notch is carved to its outside
lc_w     = 2;       // floor and risers
lc_t     = 3;       // border thickness
lc_b     = 12;      // border width, past the risers' foot
lc_r     = 12;      // the border's two corners toward the sash: radius
lc_screw = [4.25, 8, 3.5];   // screws into the foam: hole, head diameter, head height. The countersink has the
                             //   head's own taper, so the head bears on its whole cone; it stands proud by what
                             //   the head is taller than the border (0.5 with a 3 mm border)
lc_holes = 6;       // screws: 4 (2 on the top border, 2 on the bottom one) or 6 (2 more on the sash end's)

/* [Labels] */
// each full cap is engraved on its back (the face against the window): T and B for the top and bottom caps, F0 to
// F4 for the side cap's segments (the side frame), W0 to W4 for the sash cap's (the window's sash); F0a, F0b and so
// on for halves
tag_h    = 6;       // letter height
tag_d    = 0.6;     // depth

/* [Window (measured)] */
H        = 1079.5;  // ceiling to floor: 1060.0 from the centre rib's tip to the centre rail's tip, + 8.50 + 11.00
// u positions are measured from the foam's centre: the centre of the 25.90 sash channel. The first rib of each
// list is the centre one (the sash rides it; it runs through the side frame's channel to its back wall)
top_ribs = [[-3.55, 2.15, 8.50], [14.45, 18.20, 7.40]];    // [u from, u to, depth below the ceiling]; the third rib
                                                           //   (-39.85 to -34.55) is outside the foam. The room-side
                                                           //   rib is 1.5 mm further toward the room than the bottom
                                                           //   track's (measured twice)
bot_ribs = [[-3.55, 2.15, 11.00], [12.95, 19.85, 11.00]];  // [u from, u to, height above the floor]; the tall
                                                           //   outdoor lip (-39.50 to -33.80) is outside the foam
side_ch  = [25.90, 10.70];  // side frame's sash channel: width (centred), depth
strip    = [-4.20, 2.80, 19.0, 4.0];   // soft foam strip around the centre rail's end, at the back of the channel:
                    //   u from, u to, height, depth from the back wall
floor_strip = 2.5;  // the tongue stops this much higher, over another soft strip on the channel's floor
                    //   (1.7 thick, 4.0 deep from the back wall, across the channel)
sash_t   = 25.80;   // sash thickness at its end (centred)
sash_in  = 10.70;   // how far the sash goes into its cap (17.10 max: there the sash widens)
groove   = [7.90, 7.50, 7.50];   // sash end groove: width at the mouth, width at the bottom, depth
groove_key = true;  // tongue in the sash's end groove (one more seal line)
latch    = [18.20, 495, 80, 40];  // window latch zone on the side frame: u of its outdoor edge, its bottom above the
                                  //   rail tips, its height, its reach into the opening
screw    = [3.70, 12];   // screw heads in the groove at the sash's top and bottom: height above the groove's bottom,
                         //   length of the tongue's relief from each of its ends

/* [Key] */
key_at   = 25;      // key position from the window's reference surface (clear of the deepest cap)
key_clr  = 0.15;    // clearance per side in the key slots
key_tail = 4;       // tab material past the key slot

eps   = 0.01;
key_w = slice_t + 2 * key_clr;
tab_y = key_at + key_w / 2 + key_tail;   // tab end

// foam line: cap thickness from the reference surface to the foam
function deepest(r) = max([for (i = r) i[2]]);
function cap_t(kind) =
    kind == "top"    ? deepest(top_ribs) + clr_d + base :
    kind == "bottom" ? deepest(bot_ribs) + clr_d + base : base;

// the slice's outline, 2D
module profile(kind) {
    w = foam_t;
    if (kind == "top" || kind == "bottom")
        difference() {
            translate([-w / 2, 0]) square([w, tab_y]);
            for (r = kind == "top" ? top_ribs : bot_ribs)
                translate([r[0] - clr, -1]) square([r[1] - r[0] + 2 * clr, r[2] + clr_d + 1]);
        }
    if (kind == "side")
        union() {
            translate([-w / 2, 0]) square([w, tab_y]);
            translate([-side_ch[0] / 2 + clr, -(side_ch[1] - clr_d)]) square([side_ch[0] - 2 * clr, side_ch[1] - clr_d + eps]);
        }
    if (kind == "sash")
        union() {
            translate([-w / 2, 0]) square([w, tab_y]);
            for (s = [-1, 1])   // the channel's walls, along the sash's faces
                translate([s < 0 ? -w / 2 : sash_t / 2 + clr, -sash_in]) square([w / 2 - sash_t / 2 - clr, sash_in + eps]);
            if (groove_key) {   // tongue in the groove, tapered like it
                m = groove[0] / 2 - clr;
                b = groove[1] / 2 - clr;
                d = groove[2] - clr_d;
                polygon([[-m, eps], [m, eps], [b, -d], [-b, -d]]);
            }
        }
}

module label(t, size = 4) text(t, size = size, font = "Liberation Sans:style=Bold", halign = "center", valign = "center");

// one slice, on the bed
module slice(kind) {
    w  = foam_t;
    t  = cap_t(kind);
    tb = kind == "top" || kind == "bottom";
    name = kind == "top" ? "TOP" : kind == "bottom" ? "BOT" : kind == "side" ? "SIDE" : "SASH";
    difference() {
        linear_extrude(slice_t, convexity = 10) profile(kind);
        // key slot: from the outdoor edge on the top and bottom slices, from the room edge on the side and sash ones
        translate([tb ? -w / 2 - 1 : 0, key_at - key_w / 2, -1]) cube([w / 2 + 1, key_w, slice_t + 2]);
        // foam line: an engraved line across, and a notch in each edge
        translate([-w / 2 - 1, t - 0.3, slice_t - 0.4]) cube([w + 2, 0.6, 1]);
        for (s = [-1, 1]) translate([s * w / 2, t, -1]) rotate(45) translate([-0.8, -0.8, 0]) cube([1.6, 1.6, slice_t + 2]);
        // foam centre line, on the tab
        translate([-0.3, t, slice_t - 0.4]) cube([0.6, tab_y - t + 1, 1]);
        // labels, between the foam line and the key slot
        ly = (t + key_at - key_w / 2) / 2;
        translate([-w / 4 - 2, ly, slice_t - 0.6]) linear_extrude(1) label("OUT");
        translate([w / 4 + 1, ly, slice_t - 0.6]) linear_extrude(1) label(name);
    }
}

// all four slices, laid out for one print
module slices() {
    for (k = [["top", 0, 0], ["bottom", 1, 0], ["side", 0, 1], ["sash", 1, 1]])
        translate([k[1] * (foam_t + 8), k[2] * (tab_y + sash_in + 8) + (k[0] == "side" || k[0] == "sash" ? sash_in : 0), 0])
            slice(k[0]);
}

// a keyed pair in its corner: top slice and side slice, installed coordinates (x across the window toward the foam,
// y = u toward the room, z up; the ceiling at z = 0, the side frame's face at x = 0). The window is a rough ghost.
module slice_pair_view() {
    color([0.95, 0.6, 0.25])   // slice u -> y, depth below the ceiling -> -z, thickness -> -x
        multmatrix([[0, 0, -1, key_at + slice_t / 2], [1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 0, 1]]) slice("top");
    color([0.4, 0.6, 0.9])     // slice u -> y, distance from the frame's face -> x, thickness -> -z
        multmatrix([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, -1, -key_at + slice_t / 2], [0, 0, 0, 1]]) slice("side");
    %union() {
        translate([-side_ch[1] - 8, -45, 0]) cube([side_ch[1] + 8 + 70, 90, 6]);   // top frame
        for (r = top_ribs) translate([0, r[0], -r[2]]) cube([70, r[1] - r[0], r[2] + eps]);
        difference() {   // side frame, with its sash channel
            translate([-side_ch[1] - 8, -45, -70]) cube([side_ch[1] + 8, 90, 70]);
            translate([-side_ch[1], -side_ch[0] / 2, -71]) cube([side_ch[1] + 1, side_ch[0], 72]);
        }
    }
}

/* =================== CAPS (installed coordinates) =================== */
fw = foam_t / 2 + foam_clr;     // half width inside the lips
ow = fw + lip_t;                // half width over the lips
xs = base + foam_w + base;      // the sash's end face
zt = H - cap_t("top");          // underside of the top cap's body
zb = cap_t("bottom");           // top of the bottom cap's body

// top or bottom cap's cross-section: X = u, Y = from the ceiling or floor toward the foam
module cap_section(kind) {
    t = cap_t(kind);
    difference() {
        translate([-ow, 0]) square([2 * ow, t]);
        for (r = kind == "top" ? top_ribs : bot_ribs)
            translate([r[0] - clr, -1]) square([r[1] - r[0] + 2 * clr, r[2] + clr_d + 1]);
    }
    for (s = [-1, 1]) translate([s < 0 ? -ow : fw, t - eps]) square([lip_t, lip_d + eps]);
}

// a top or bottom cap's own coordinates (its section extruded along z from x0) placed in the window
module at_top(x0 = 0)    multmatrix([[0, 0, 1, x0], [1, 0, 0, 0], [0, -1, 0, H], [0, 0, 0, 1]]) children();
module at_bottom(x0 = 0) multmatrix([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]) children();

module top_cap(x0 = 0, x1 = xs)    at_top(x0) linear_extrude(x1 - x0, convexity = 10) cap_section("top");
module bottom_cap(x0 = 0, x1 = xs) at_bottom(x0) linear_extrude(x1 - x0, convexity = 10) cap_section("bottom");

// the side and sash caps' bodies and lips, between the top and bottom caps (and under their lips)
// (the base is the foam's width at its ends, where those lips straddle it, and the lips' width between them)
module upright_body(xb0, xl0) {
    translate([xb0, -fw + clr, zb + cap_gap]) cube([base, 2 * (fw - clr), zt - zb - 2 * cap_gap]);
    z0 = zb + lip_d + cap_gap;
    h  = zt - zb - 2 * (lip_d + cap_gap);
    translate([xb0, -ow, z0]) cube([base, 2 * ow, h]);
    for (s = [-1, 1])
        translate([xl0, s < 0 ? -ow : fw, z0]) cube([lip_d, lip_t, h]);
}

module side_cap() {
    tw = side_ch[0] / 2 - clr;
    td = side_ch[1] - clr_d;
    lz = bot_ribs[0][2] + latch[1];   // the latch zone's bottom
    difference() {
        union() {
            upright_body(0, base);
            difference() {   // tongue, floor to ceiling in the channel
                translate([-td, -tw, clr_d + floor_strip]) cube([td + eps, 2 * tw, H - 2 * clr_d - floor_strip]);
                r = top_ribs[0];
                translate([-td - 1, r[0] - clr, H - r[2] - clr_d]) cube([td + 2, r[1] - r[0] + 2 * clr, r[2] + clr_d + 1]);
                b = bot_ribs[0];
                translate([-td - 1, b[0] - clr, -1]) cube([td + 2, b[1] - b[0] + 2 * clr, b[2] + clr_d + 1]);
                translate([-side_ch[1] - 1, strip[0] - clr, -1]) cube([strip[3] + clr + 1, strip[1] - strip[0] + 2 * clr, strip[2] + clr_d + 1]);
            }
        }
        // the latch zone: the room-side lip and that part of the base stop around it (the tongue is clear of it). Its
        // top rises at 45 degrees toward the room, and over the lip toward the foam too, so the base and the lip
        // above it print standing without an overhang; its bottom mirrors it
        let(u0 = latch[0] - clr, u1 = ow + 1, z0 = lz - clr, z1 = lz + latch[2] + clr, xl = base + lip_d + 1) {
            translate([-1, u0, z0]) cube([latch[3] + 1, ow, latch[2] + 2 * clr]);
            hull() { bx(-1, base, u0, u0 + eps, z0, z1); bx(-1, base, u1 - eps, u1, z0 - (u1 - u0), z1 + u1 - u0); }
            hull() for (x = [base, xl], u = [u0, u1])
                let(d = (u - u0) + (x - base)) bx(x - eps, x + eps, u - eps, u + eps, z0 - d, z1 + d);
        }
    }
}

module sash_cap() {
    upright_body(xs - base, xs - base - lip_d);
    z0 = zb + cap_gap;
    h  = zt - zb - 2 * cap_gap;
    wi = sash_t / 2 + clr;   // the walls' inner face (|u|)
    for (s = [-1, 1]) {   // the channel's walls, along the sash's faces
        translate([xs - eps, s < 0 ? -ow : wi, z0]) cube([sash_in + eps, ow - wi, h]);
        // past the sash's end face they go on to the ceiling and the floor, notched for the ribs and rails beside
        // the sash (a notch runs to the sash's face when it would leave a sliver thinner than 1.5 mm)
        difference() {
            translate([xs, s < 0 ? -ow : wi, clr_d]) cube([sash_in, ow - wi, H - 2 * clr_d]);
            for (k = [[top_ribs, H, -1], [bot_ribs, 0, 1]], r = k[0])
                let(a = r[0] - clr, b = r[1] + clr)
                if (s * b > wi && s * a < ow)
                    let(lo = s > 0 && a - wi < 1.5 ? wi - 1 : a,
                        hi = s < 0 && -wi - b < 1.5 ? -wi + 1 : b,
                        d  = r[2] + clr_d)
                    translate([xs - 1, lo, k[2] > 0 ? -1 : H - d]) cube([sash_in + 2, hi - lo, d + 1]);
        }
    }
    if (groove_key) {   // tongue in the groove, tapered like it
        m = groove[0] / 2 - clr;
        b = groove[1] / 2 - clr;
        d = groove[2] - clr_d;
        difference() {
            translate([xs, 0, z0]) linear_extrude(h) polygon([[-eps, -m], [-eps, m], [d, b], [d, -b]]);
            for (zr = [z0 - 1, z0 + h - screw[1]])   // shallower over the screw heads near its ends
                translate([xs + groove[2] - screw[0] - clr_d, -groove[0], zr]) cube([screw[0] + 1, 2 * groove[0], screw[1] + 1]);
        }
    }
}

// the window around the caps, roughly (a ghost for the views)
module window_ghost() {
    x0 = -side_ch[1] - 8;
    x1 = xs + 40;
    translate([x0, -45, H]) cube([x1 - x0, 90, 6]);   // top frame and its ribs
    for (r = top_ribs) let(a = r == top_ribs[0] ? -side_ch[1] : 0) translate([a, r[0], H - r[2]]) cube([x1 - a, r[1] - r[0], r[2] + eps]);
    translate([x0, -45, -6]) cube([x1 - x0, 90, 6]);  // bottom frame and its rails
    for (r = bot_ribs) let(a = r == bot_ribs[0] ? -side_ch[1] : 0) translate([a, r[0], -eps]) cube([x1 - a, r[1] - r[0], r[2] + eps]);
    translate([-side_ch[1], strip[0], 0]) cube([strip[3], strip[1] - strip[0], strip[2]]);
    difference() {   // side frame, with its channel
        translate([x0, -45, 0]) cube([8 + side_ch[1], 90, H]);
        translate([-side_ch[1], -side_ch[0] / 2, -1]) cube([side_ch[1] + 1, side_ch[0], H + 2]);
    }
    difference() {   // the sash's end, with its groove
        translate([xs, -sash_t / 2, 0]) cube([40, sash_t, H]);
        translate([xs - 1, -groove[1] / 2, -1]) cube([groove[2] + 1, groove[1], H + 2]);
    }
}

/* =================== FULL CAPS AND JOINTS =================== */
// text s engraved into a face at p: reading along a, the letters' tops toward b (the face's outward normal is a x b)
module tag(s, p, a, b) let(n = cross(a, b))
    multmatrix([[a[0], b[0], n[0], p[0]], [a[1], b[1], n[1], p[1]], [a[2], b[2], n[2], p[2]], [0, 0, 0, 1]])
        translate([0, 0, -tag_d]) linear_extrude(tag_d + 1) label(s, tag_h);

// The top and bottom caps, whole, standing on their end at the side frame; the label is on the back's outdoor half,
// between the lips' edge and the centre rib
module cap_tb(kind, s) difference() {
    linear_extrude(xs, convexity = 10) cap_section(kind);
    tag(s, [-(ow + 3.55 + clr) / 2, 0, xs / 2], [0, 0, 1], [-1, 0, 0]);
}
module cap_top()    cap_tb("top", "T");
module cap_bottom() cap_tb("bottom", "B");

module bx(x0, x1, y0, y1, z0, z1) translate([min(x0, x1), min(y0, y1), min(z0, z1)]) cube([abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)]);

// sockets of an upright cap: [x from, x to, u from, u to, the snap tab's face (-1: toward -x, 1: toward +x), depth]. The
// side cap's is in its tongue, its tab on the tongue's back face; the sash cap has one in each wall, its tab on the
// wall's free end.
function socks(kind) = kind == "side"
    ? [let(tw = side_ch[0] / 2 - clr, td = side_ch[1] - clr_d) [-td + j_wall, -1, -tw + j_wall, tw - j_wall, -1, j_d[0]]]
    : [for (s = [-1, 1]) let(a = sash_t / 2 + clr + j_wall, b = ow - j_wall)
        [xs - 1, xs + sash_in - j_wall, s < 0 ? -b : a, s < 0 ? -a : b, 1, j_d[1]]];

// a diamond across x from xa to xb: half-diagonal a, centred on u = uc and at distance dc from the joint at zs
module diamond(xa, xb, uc, dc, a, zs, h)
    hull() for (v = [[a, 0], [-a, 0], [0, a], [0, -a]])
        bx(xa, xb, uc + v[0] - eps, uc + v[0] + eps, zs + h * (dc + v[1] - eps), zs + h * (dc + v[1] + eps));

wa = j_win[0] / 2;      // the window's half-diagonal
wc = j_win[1] + wa;     // its centre's distance from the segment's end
ba = wa - 0.15;         // the bump's half-diagonal: 0.1 mm inside the window's side edges
bc = j_win[1] + j_catch + ba;   // the bump's centre: its catch (the V toward the joint) j_catch from the window's
jc = 1;                 // the joiner's end chamfer, 45 degrees
function j_stop(r) = r[5] + j_clr + jc;   // how deep the joiner's end can go: its chamfers bear on a gable's slopes there, and
                                          //   a flat-bottomed socket ends there

// a socket, cut into a segment from its end at height zs (h = 1: upward into it, -1: downward), with the snap tab
// (two slits through the wall) and the window in the tab. flat: it prints opening up, so its closed end is flat (a
// firmer stop for the joiner); otherwise a gable
module socket(r, zs, h, flat = false) {
    x0 = r[0]; x1 = r[1]; u0 = r[2]; u1 = r[3]; d = r[5];
    uc = (u0 + u1) / 2;
    xo = r[4] < 0 ? [x0 - j_wall - 1, x0 + eps] : [x1 - eps, x1 + j_wall + 1];   // through the tab's wall
    bx(x0, x1, u0, u1, zs - h, zs + h * (flat ? j_stop(r) : d));
    // the gable: 45 degrees across its narrower side, no bridge when it prints opening down
    xr = x1 - x0 <= u1 - u0;   // the ridge runs along u
    rise = (xr ? x1 - x0 : u1 - u0) / 2;
    if (!flat) hull() {
        bx(x0, x1, u0, u1, zs + h * (d - eps), zs + h * d);
        if (xr) bx((x0 + x1) / 2 - eps, (x0 + x1) / 2 + eps, u0, u1, zs + h * d, zs + h * (d + rise));
        else    bx(x0, x1, (u0 + u1) / 2 - eps, (u0 + u1) / 2 + eps, zs + h * d, zs + h * (d + rise));
    }
    hull() { bx(x0 - j_ch, x1 + j_ch, u0 - j_ch, u1 + j_ch, zs - h, zs); bx(x0, x1, u0, u1, zs, zs + h * j_ch); }
    for (s = [-1, 1]) bx(xo[0], xo[1], uc + s * j_tab[0] / 2, uc + s * (j_tab[0] / 2 + j_slit), zs - h, zs + h * j_tab[1]);
    diamond(xo[0], xo[1], uc, wc, wa, zs, h);
}

// the joiner in its sockets, centred on the joint at height zs: a diamond bump near each end, full height on its
// half toward the joint (its catch: the two edges of the V) and ramped down on the other half. Its ends' 45 degree
// chamfers bear on the sockets' gables (or its ends on a flat bottom), j_end short of them: that sets how deep it can
// go. The long edges of its back, on the bed, are chamfered too (elephant's foot).
module joiner(r, zs) {
    x0 = r[0] + j_clr; x1 = r[1] - j_clr; u0 = r[2] + j_clr; u1 = r[3] - j_clr; f = r[4];
    c  = jc;
    k  = 0.4;   // the back's chamfer
    L  = j_stop(r) - j_end;
    uc = (u0 + u1) / 2;
    xf = f < 0 ? x0 : x1;   // the tab's face, bumps out
    xb = f < 0 ? x1 : x0;   // the back
    hull() {
        bx(xf, xb + f * k, u0, u1, zs - L + c, zs + L - c);
        bx(xf, xb, u0 + k, u1 - k, zs - L + c, zs + L - c);
        bx(x0 + c, x1 - c, u0 + c, u1 - c, zs - L, zs + L);
    }
    for (h = [-1, 1]) intersection() {
        diamond(xf - f * 0.5, xf + f * j_bump, uc, bc, ba, zs, h);
        hull() {
            bx(xf - f * 0.5, xf + f * j_bump, uc - wa, uc + wa, zs + h * (bc - wa), zs + h * bc);
            bx(xf - f * 0.5, xf, uc - wa, uc + wa, zs + h * (bc + ba - eps), zs + h * (bc + ba));
        }
    }
}

// printed lying on its back, bumps up
module joiner_print(kind) {
    r = socks(kind)[kind == "side" ? 0 : 1];
    translate([0, -(r[2] + r[3]) / 2, r[4] < 0 ? r[1] - j_clr : -(r[0] + j_clr)])
        rotate([0, r[4] < 0 ? 90 : -90, 0]) joiner(r, 0);
}

module upright_cap(kind) if (kind == "side") side_cap(); else sash_cap();

// the pieces the upright caps print in: the segments, or their halves. cuts: the joints between them, from the floor
seg_ends = concat([0], splits, [H]);
cuts = halves ? [for (k = [1 : 2 * len(splits) + 1])
                    k % 2 == 0 ? seg_ends[k / 2] : (seg_ends[(k - 1) / 2] + seg_ends[(k + 1) / 2]) / 2]
              : splits;
function seg_name(i) = halves ? str(floor(i / 2), chr(97 + i % 2)) : str(i);   // 0a, 0b, 1a... or 0, 1, 2...

// the side cap's latch relief, from the bottom of its lower slopes to the top of its upper ones (see side_cap())
relief = let(lz = bot_ribs[0][2] + latch[1], d = (ow + 1 - latch[0] + clr) + lip_d + 1)
    [lz - clr - d, lz + latch[2] + clr + d];

// piece i turns over to print on its upper end: the lowest one (its base and lips start above its foot, like the
// corner pieces), and a side cap piece whose lower end is in the latch relief (its upper end has the full profile)
function seg_flip(kind, i) = i == 0 || (kind == "side" && seg_lo(i) > relief[0] && seg_lo(i) < relief[1]);

// piece i of an upright cap (0 at the floor), with a socket in each end that meets another piece, and its label at
// mid-height, reading upward, on the back's outdoor half: the side cap's beside the tongue, the sash cap's between
// the groove's tongue and the wall. A socket opening up as it prints has a flat bottom, one opening down a gable
function seg_lo(i) = i == 0 ? -1 : cuts[i - 1];
function seg_hi(i) = i == len(cuts) ? H + 1 : cuts[i];
module segment(kind, i) {
    zm = (max(seg_lo(i), 0) + min(seg_hi(i), H)) / 2;
    f  = seg_flip(kind, i);
    difference() {
        intersection() { upright_cap(kind); bx(-50, xs + 50, -50, 50, seg_lo(i), seg_hi(i)); }
        for (r = socks(kind)) {
            if (i > 0) socket(r, seg_lo(i), 1, f);
            if (i < len(cuts)) socket(r, seg_hi(i), -1, !f);
        }
        if (kind == "side") tag(str("F", seg_name(i)), [0, -(side_ch[0] / 2 - clr + ow) / 2, zm], [0, 0, 1], [0, 1, 0]);
        else tag(str("W", seg_name(i)), [xs, -(groove[0] / 2 - clr + sash_t / 2 + clr) / 2, zm], [0, 0, 1], [0, -1, 0]);
    }
}

// print orientation: standing on its lower end, or turned over onto its upper end (seg_flip())
module segment_print(kind, i) translate([kind == "sash" ? -xs : 0, 0, 0])
    if (seg_flip(kind, i)) translate([0, 0, seg_hi(i)]) rotate([180, 0, 0]) segment(kind, i);
    else translate([0, 0, -seg_lo(i)]) segment(kind, i);

// joint test: the two segment ends at the second joint, joint_l long; the upper one stands on its socket end, the
// lower one has it on top (the real segments have both)
module joint_piece(kind, upper) {
    zs = splits[1];
    l  = joint_l[kind == "side" ? 0 : 1];
    translate([kind == "sash" ? -xs : 0, 0, upper ? -zs : -(zs - l)]) difference() {
        intersection() { upright_cap(kind); bx(-50, xs + 50, -50, 50, upper ? zs : zs - l, upper ? zs + l : zs); }
        for (r = socks(kind)) socket(r, zs, upper ? 1 : -1, !upper);
    }
}

module joint_tests() {
    translate([0, 0, 0])   joint_piece("side", false);
    translate([30, 0, 0])  joint_piece("side", true);
    translate([66, 0, 0])  joint_piece("sash", false);
    translate([96, 0, 0])  joint_piece("sash", true);
    translate([140, -16, 0]) joiner_print("side");
    for (k = [0, 1]) translate([140, 8 + k * 16, 0]) joiner_print("sash");
}

// the smallest joint test: one wall of the sash cap's joint (room side), both ends, and one joiner
module snap_test() {
    for (k = [0, 1]) translate([k * 26, 0, 0]) intersection() {
        joint_piece("sash", k == 1);
        bx(-50, 50, sash_t / 2 + clr - eps, 50, -1, 100);
    }
    translate([7.5, -2, 0]) joiner_print("sash");
}

// all the joiners for both caps: one per joint in the side cap, two in the sash cap
module joiners() {
    n = len(cuts);
    for (i = [0 : n - 1]) translate([(i % 5) * 34, floor(i / 5) * 26, 0]) joiner_print("side");
    for (i = [0 : 2 * n - 1]) translate([(i % 3) * 56 + 11, 48 + floor(i / 3) * 16, 0]) joiner_print("sash");
}

// a joint, opened up: the lower end, the joiners, the upper end lifted (installed orientation)
module joint_view() {
    zs = splits[1];
    for (kind = ["side", "sash"]) let(k = kind == "side" ? 0 : 1, l = joint_l[k], d = j_d[k]) {
        color(kind == "side" ? [0.4, 0.6, 0.9] : [0.5, 0.8, 0.6]) {
            difference() {
                intersection() { upright_cap(kind); bx(-50, xs + 50, -50, 50, zs - l, zs); }
                for (r = socks(kind)) socket(r, zs, -1, true);
            }
            translate([0, 0, 2 * d + 10]) difference() {
                intersection() { upright_cap(kind); bx(-50, xs + 50, -50, 50, zs, zs + l); }
                for (r = socks(kind)) socket(r, zs, 1);
            }
        }
        color([0.95, 0.6, 0.25]) for (r = socks(kind)) translate([0, 0, d + 5]) joiner(r, zs);
    }
}

// every part in its place in the window, the foam and the window as ghosts; explode > 0 spreads the pieces apart
// along the height (then the ghosts are left out)
module assembly_view() {
    n = len(cuts);
    e = explode;
    color([0.9, 0.75, 0.3]) render() at_bottom() cap_bottom();   // the printed caps, with their labels
    color([0.95, 0.6, 0.25]) translate([0, 0, (n + 2) * e]) render() at_top() cap_top();
    // segments alternate between a lighter and a darker shade (render(): a clean preview of their sockets)
    for (i = [0 : n]) translate([0, 0, (i + 1) * e]) {
        color(i % 2 == 0 ? [0.4, 0.6, 0.9] : [0.22, 0.38, 0.7]) render() segment("side", i);
        color(i % 2 == 0 ? [0.5, 0.8, 0.6] : [0.27, 0.58, 0.38]) render() segment("sash", i);
    }
    for (i = [0 : n - 1]) translate([0, 0, (i + 1.5) * e]) color([0.85, 0.3, 0.3])
        for (kind = ["side", "sash"], r = socks(kind)) joiner(r, cuts[i]);
    if (e == 0) {
        %translate([base, -foam_t / 2, zb]) cube([foam_w, foam_t, zt - zb]);
        %window_ghost();
    }
}

/* =================== CORNER TEST PIECES =================== */
// The real cap ends, in their print orientation (all print standing, cross-section on the bed). One top piece and
// one bottom piece serve both corners: turn them end for end for the sash corners.
module corner_top()    linear_extrude(corner_l, convexity = 10) cap_section("top");
module corner_bottom() linear_extrude(corner_l, convexity = 10) cap_section("bottom");

// upright ends: top ends stand on their cut face, bottom ends are turned over onto it
module upright_top(sash) {
    translate([0, 0, -(zt - corner_l)]) intersection() {
        if (sash) sash_cap(); else side_cap();
        translate([-50, -50, zt - corner_l]) cube([xs + 100, 100, H]);
    }
}
module upright_bottom(sash) {
    translate([0, 0, zb + corner_l]) rotate([180, 0, 0]) intersection() {
        if (sash) sash_cap(); else side_cap();
        translate([-50, -50, -1]) cube([xs + 100, 100, zb + corner_l + 1]);
    }
}
module corner_side_top()    upright_top(false);
module corner_side_bottom() upright_bottom(false);
module corner_sash_top()    translate([-xs, 0, 0]) upright_top(true);
module corner_sash_bottom() translate([-xs, 0, 0]) upright_bottom(true);

// latch test: a latch_t thick slice of the side cap at the latch zone's mid-height, flat on the bed (the room side
// of its base and its room-side lip stop there, to clear the latch)
module latch_slice() let(zm = bot_ribs[0][2] + latch[1] + latch[2] / 2)
    translate([0, 0, -zm]) intersection() { side_cap(); bx(-50, 50, -50, 50, zm, zm + latch_t); }

/* =================== LATCH COVER =================== */
lc_z  = [bot_ribs[0][2] + latch[1] - clr, bot_ribs[0][2] + latch[1] + latch[2] + clr];   // inside, at its floor
lc_zm = (lc_z[0] + lc_z[1]) / 2;
lc_x  = latch[3] + clr;                 // inside, at its floor
lc_x0 = base + clr;                     // its open end, against the side cap's base
lc_u0 = latch[0] - clr;                 // the floor's room face, as the side cap's relief
lc_uf = foam_t / 2;                     // the foam's room face
lc_h  = lc_uf - lc_u0;                  // the risers' height
// the risers' outer edge on the foam's face: x at the sash end, z at the bottom and top (the notch's outline there)
lc_fx = lc_x + lc_h + lc_w * sqrt(2);
lc_fz = [lc_z[0] - lc_h - lc_w * sqrt(2), lc_z[1] + lc_h + lc_w * sqrt(2)];

// a 2D shape in the x-z plane, run along u from u0 to u1
module xz_prism(u0, u1) translate([0, u1, 0]) rotate([90, 0, 0]) linear_extrude(u1 - u0) children();

// the liner's inside grown by g normal to its faces, from its floor out past the border, open at the side cap
module lc_solid(g) let(k = g * (sqrt(2) - 1), u1 = lc_uf + lc_t + 1, d = u1 - lc_u0 + g * sqrt(2)) hull() {
    bx(-1, lc_x + k, lc_u0 - g, lc_u0 - g + eps, lc_z[0] - k, lc_z[1] + k);
    bx(-1, lc_x + d, u1 - eps, u1, lc_z[0] - d, lc_z[1] + d);
}

// the screws' centres, in the border's middle: [x, z]. Along the top and bottom, the first one clears the side
// cap's lip
lc_bz = [lc_fz[0] - lc_b / 2, lc_fz[1] + lc_b / 2];
lc_screws = concat([for (x = [lc_x0 + lip_d + 7, lc_fx - 6], z = lc_bz) [x, z]],
                   lc_holes == 6 ? [for (s = [-1, 1]) [lc_fx + lc_b / 2, lc_zm + s * 35]] : []);

// the liner in its place in the foam
module latch_cover() {
    hole = lc_screw[0]; hd = lc_screw[1] + 0.4; hh = lc_screw[2];
    taper = (lc_screw[1] - hole) / 2 / hh;   // the head's taper: radius per mm of height
    difference() {
        union() {
            intersection() {   // the floor and the risers, in the foam
                difference() { lc_solid(lc_w); lc_solid(0); }
                bx(lc_x0, lc_fx + 1, lc_u0 - lc_w - 1, lc_uf, lc_fz[0] - 1, lc_fz[1] + 1);
            }
            difference() {   // the border, on the foam's face
                xz_prism(lc_uf, lc_uf + lc_t) hull() {
                    translate([lc_x0, lc_fz[0] - lc_b]) square([eps, lc_fz[1] - lc_fz[0] + 2 * lc_b]);
                    for (z = [lc_fz[0] - lc_b + lc_r, lc_fz[1] + lc_b - lc_r])
                        translate([lc_fx + lc_b - lc_r, z]) circle(lc_r, $fn = 96);
                }
                lc_solid(0);
            }
        }
        // the side cap grown by clr (by a cube): its lip, outside its relief, notches the border's corners at that
        // end (render(): computed once, which keeps the preview light)
        render() minkowski() {
            intersection() { side_cap(); bx(-20, base + lip_d + 1, 0, ow + 1, lc_fz[0] - lc_b - 5, lc_fz[1] + lc_b + 5); }
            cube(2 * clr, center = true);
        }
        // the screws: a hole, and a countersink with the head's taper, its top hh - lc_t above the border
        for (s = lc_screws) translate([s[0], 0, s[1]]) rotate([-90, 0, 0]) {
            translate([0, 0, lc_uf - 1]) cylinder(d = hole, h = lc_t + 2, $fn = 32);
            translate([0, 0, lc_uf + hh]) mirror([0, 0, 1])
                cylinder(d1 = hd, d2 = hd - 2 * taper * hh, h = hh, $fn = 48);
        }
    }
}

// print orientation: standing on its open end (the side cap's): the floor, the border and the top and bottom
// risers are walls, the sash end's riser a 45 degree overhang
module latch_cover_print() rotate([0, -90, 0]) translate([-lc_x0, 0, -lc_zm]) latch_cover();

// the liner in the notched foam, beside the side cap, the latch zone as a ghost
module latch_cover_view() {
    color([0.85, 0.5, 0.75]) latch_cover();
    color([0.4, 0.6, 0.9]) intersection() { side_cap(); bx(-50, 50, -50, 50, lc_fz[0] - 30, lc_fz[1] + 30); }
    color([0.85, 0.85, 0.8]) difference() {
        bx(base, base + foam_w, -foam_t / 2, foam_t / 2, lc_fz[0] - 30, lc_fz[1] + 30);
        lc_solid(lc_w);
    }
    %bx(0, latch[3], latch[0], latch[0] + 40, lc_z[0] + clr, lc_z[1] - clr);
}

// all six on one plate (print two top and two bottom pieces to try all four corners at once)
module corners() {
    translate([0, 0, 0])     corner_top();
    translate([0, 70, 0])    corner_bottom();
    translate([60, 0, 0])    corner_side_top();
    translate([60, 70, 0])   corner_side_bottom();
    translate([110, 0, 0])   corner_sash_top();
    translate([110, 70, 0])  corner_sash_bottom();
}

// the pieces in their corners, in the window (preview with a small H, for example -D H=200)
module corners_view() {
    color([0.95, 0.6, 0.25]) { top_cap(0, corner_l); top_cap(xs - corner_l, xs); }
    color([0.9, 0.75, 0.3])  { bottom_cap(0, corner_l); bottom_cap(xs - corner_l, xs); }
    color([0.4, 0.6, 0.9])   intersection() { side_cap(); union() { translate([-50, -50, zt - corner_l]) cube([100, 100, 100]); translate([-50, -50, -1]) cube([100, 100, zb + corner_l + 1]); } }
    color([0.5, 0.8, 0.6])   intersection() { sash_cap(); union() { translate([xs - 50, -50, zt - corner_l]) cube([100, 100, 100]); translate([xs - 50, -50, -1]) cube([100, 100, zb + corner_l + 1]); } }
    %window_ghost();
}

if (part == "cap_top")            cap_top();
if (part == "cap_bottom")         cap_bottom();
for (i = [0 : len(cuts)]) {
    if (part == str("side_", seg_name(i)))  segment_print("side", i);
    if (part == str("sash_", seg_name(i)))  segment_print("sash", i);
}
if (part == "joiner_side")        joiner_print("side");
if (part == "joiner_sash")        joiner_print("sash");
if (part == "joiners")            joiners();
if (part == "joint_tests")        joint_tests();
if (part == "snap_test")          snap_test();
if (part == "joint_side_lower")   joint_piece("side", false);
if (part == "joint_side_upper")   joint_piece("side", true);
if (part == "joint_sash_lower")   joint_piece("sash", false);
if (part == "joint_sash_upper")   joint_piece("sash", true);
if (part == "joint_view")         joint_view();
if (part == "assembly_view")      assembly_view();
if (part == "corners")            corners();
if (part == "corner_top")         corner_top();
if (part == "corner_bottom")      corner_bottom();
if (part == "corner_side_top")    corner_side_top();
if (part == "corner_side_bottom") corner_side_bottom();
if (part == "corner_sash_top")    corner_sash_top();
if (part == "corner_sash_bottom") corner_sash_bottom();
if (part == "latch_slice")        latch_slice();
if (part == "latch_cover")        latch_cover_print();
if (part == "latch_cover_view")   latch_cover_view();
if (part == "corners_view")       corners_view();
if (part == "slices")             slices();
if (part == "slice_top")          slice("top");
if (part == "slice_bottom")       slice("bottom");
if (part == "slice_side")         slice("side");
if (part == "slice_sash")         slice("sash");
if (part == "slice_pair_view")    slice_pair_view();
