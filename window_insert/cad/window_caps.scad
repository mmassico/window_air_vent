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
part = "joint_tests";   // [cap_top, cap_bottom, side_0, side_1, side_2, side_3, side_4, sash_0, sash_1, sash_2, sash_3, sash_4, joiner_side, joiner_sash, joiners, joint_tests, joint_side_lower, joint_side_upper, joint_sash_lower, joint_sash_upper, joint_view, assembly_view, corners, corner_top, corner_bottom, corner_side_top, corner_side_bottom, corner_sash_top, corner_sash_bottom, corners_view, slices, slice_top, slice_bottom, slice_side, slice_sash, slice_pair_view]

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

/* [Joints] */
splits   = [216, 432, 648, 864];  // heights of the joints between the side and sash caps' segments: 5 segments,
                                  //   numbered 0 to 4 from the floor, each under 256 mm in its print orientation
j_d      = 15;      // socket depth into each segment's end (to the eaves of its roof, see socket())
j_wall   = 1.6;     // socket wall on the snap tab's face: the tab's thickness
j_clr    = 0.1;     // clearance per side around the joiner
j_tab    = [8, 12]; // snap tab: width, length from the segment's end
j_slit   = 0.8;     // slit on each side of the tab
j_win    = [6, 4];  // window in the tab, a diamond (45 degree edges: no bridge when printed standing): width and
                    //   height, distance of its near corner from the segment's end
j_bump   = 1.0;     // bump on the joiner (the tab flexes j_bump - j_clr as it snaps over)
j_catch  = 0.2;     // axial play between the bump's catch and the window's: how far each side of a joint opens when
                    //   pulled
j_end    = 0.1;     // play between each end of the joiner and its socket's roof (keep it under j_catch: a joiner
                    //   pushed to the bottom of one socket must still let the other one's tab snap in)
j_ch     = 0.6;     // chamfer at the socket's mouth (lead-in, and room for the elephant's foot)
joint_l  = 24;      // joint test pieces: length of each segment end (past the deepest socket's roof)
explode  = 0;       // assembly_view: gap between the pieces along the height (0: assembled)

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
        linear_extrude(slice_t) profile(kind);
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

module top_cap(x0 = 0, x1 = xs) {
    multmatrix([[0, 0, 1, x0], [1, 0, 0, 0], [0, -1, 0, H], [0, 0, 0, 1]]) linear_extrude(x1 - x0) cap_section("top");
}

module bottom_cap(x0 = 0, x1 = xs) {
    multmatrix([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]) linear_extrude(x1 - x0) cap_section("bottom");
}

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
        // the latch zone: the room-side lip and that part of the base stop around it (the tongue is clear of it)
        translate([-1, latch[0] - clr, lz - clr]) cube([latch[3] + 1, ow, latch[2] + 2 * clr]);
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
// The top and bottom caps, whole, standing on their end at the side frame
module cap_top()    linear_extrude(xs) cap_section("top");
module cap_bottom() linear_extrude(xs) cap_section("bottom");

module bx(x0, x1, y0, y1, z0, z1) translate([min(x0, x1), min(y0, y1), min(z0, z1)]) cube([abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)]);

// sockets of an upright cap: [x from, x to, u from, u to, the snap tab's face (-1: toward -x, 1: toward +x)]. The
// side cap's is in its tongue, its tab on the tongue's back face; the sash cap has one in each wall, its tab on the
// wall's free end.
function socks(kind) = kind == "side"
    ? [let(tw = side_ch[0] / 2 - clr, td = side_ch[1] - clr_d) [-td + j_wall, -1, -tw + j_wall, tw - j_wall, -1]]
    : [for (s = [-1, 1]) let(a = sash_t / 2 + clr + j_wall, b = ow - j_wall)
        [xs - 1, xs + sash_in - j_wall, s < 0 ? -b : a, s < 0 ? -a : b, 1]];

// a diamond across x from xa to xb: half-diagonal a, centred on u = uc and at distance dc from the joint at zs
module diamond(xa, xb, uc, dc, a, zs, h)
    hull() for (v = [[a, 0], [-a, 0], [0, a], [0, -a]])
        bx(xa, xb, uc + v[0] - eps, uc + v[0] + eps, zs + h * (dc + v[1] - eps), zs + h * (dc + v[1] + eps));

wa = j_win[0] / 2;      // the window's half-diagonal
wc = j_win[1] + wa;     // its centre's distance from the segment's end
ba = wa - 0.15;         // the bump's half-diagonal: 0.1 mm inside the window's side edges
bc = j_win[1] + j_catch + ba;   // the bump's centre: its catch (the V toward the joint) j_catch from the window's
jc = 1;                 // the joiner's end chamfer, 45 degrees
j_stop = j_d + j_clr + jc;      // how deep the joiner's end can go: its chamfers bear on a gable's slopes there, and
                                //   a flat-bottomed socket ends there

// a socket, cut into a segment from its end at height zs (h = 1: upward into it, -1: downward), with the snap tab
// (two slits through the wall) and the window in the tab. flat: it prints opening up, so its closed end is flat (a
// firmer stop for the joiner); otherwise a gable
module socket(r, zs, h, flat = false) {
    x0 = r[0]; x1 = r[1]; u0 = r[2]; u1 = r[3];
    uc = (u0 + u1) / 2;
    xo = r[4] < 0 ? [x0 - j_wall - 1, x0 + eps] : [x1 - eps, x1 + j_wall + 1];   // through the tab's wall
    bx(x0, x1, u0, u1, zs - h, zs + h * (flat ? j_stop : j_d));
    // the gable: 45 degrees across its narrower side, no bridge when it prints opening down
    xr = x1 - x0 <= u1 - u0;   // the ridge runs along u
    rise = (xr ? x1 - x0 : u1 - u0) / 2;
    if (!flat) hull() {
        bx(x0, x1, u0, u1, zs + h * (j_d - eps), zs + h * j_d);
        if (xr) bx((x0 + x1) / 2 - eps, (x0 + x1) / 2 + eps, u0, u1, zs + h * j_d, zs + h * (j_d + rise));
        else    bx(x0, x1, (u0 + u1) / 2 - eps, (u0 + u1) / 2 + eps, zs + h * j_d, zs + h * (j_d + rise));
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
    L  = j_stop - j_end;
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

// segment i of an upright cap (0 at the floor), with a socket in each end that meets another segment
function seg_lo(i) = i == 0 ? -1 : splits[i - 1];
function seg_hi(i) = i == len(splits) ? H + 1 : splits[i];
module segment(kind, i) {
    difference() {
        intersection() { upright_cap(kind); bx(-50, xs + 50, -50, 50, seg_lo(i), seg_hi(i)); }
        for (r = socks(kind)) {
            if (i > 0) socket(r, seg_lo(i), 1);
            if (i < len(splits)) socket(r, seg_hi(i), -1, i > 0);   // on top as it prints, except segment 0's
        }
    }
}

// print orientation: segment 0 is turned over onto its upper end (its base and lips start above its foot, like the
// corner pieces); the others stand on their lower end
module segment_print(kind, i) translate([kind == "sash" ? -xs : 0, 0, 0])
    if (i == 0) translate([0, 0, seg_hi(0)]) rotate([180, 0, 0]) segment(kind, 0);
    else translate([0, 0, -seg_lo(i)]) segment(kind, i);

// joint test: the two segment ends at the second joint, joint_l long; the upper one stands on its socket end, the
// lower one has it on top (the real segments have both)
module joint_piece(kind, upper) {
    zs = splits[1];
    translate([kind == "sash" ? -xs : 0, 0, upper ? -zs : -(zs - joint_l)]) difference() {
        intersection() { upright_cap(kind); bx(-50, xs + 50, -50, 50, upper ? zs : zs - joint_l, upper ? zs + joint_l : zs); }
        for (r = socks(kind)) socket(r, zs, upper ? 1 : -1, !upper);
    }
}

module joint_tests() {
    translate([0, 0, 0])   joint_piece("side", false);
    translate([30, 0, 0])  joint_piece("side", true);
    translate([66, 0, 0])  joint_piece("sash", false);
    translate([96, 0, 0])  joint_piece("sash", true);
    translate([130, -16, 0]) joiner_print("side");
    for (k = [0, 1]) translate([130, 8 + k * 16, 0]) joiner_print("sash");
}

// all the joiners for both caps: one per joint in the side cap, two in the sash cap
module joiners() {
    n = len(splits);
    for (i = [0 : n - 1]) translate([i * 34, 0, 0]) joiner_print("side");
    for (i = [0 : 2 * n - 1]) translate([(i % n) * 34, 22 + floor(i / n) * 16, 0]) joiner_print("sash");
}

// a joint, opened up: the lower end, the joiners, the upper end lifted (installed orientation)
module joint_view() {
    zs = splits[1];
    for (kind = ["side", "sash"]) {
        color(kind == "side" ? [0.4, 0.6, 0.9] : [0.5, 0.8, 0.6]) {
            difference() {
                intersection() { upright_cap(kind); bx(-50, xs + 50, -50, 50, zs - joint_l, zs); }
                for (r = socks(kind)) socket(r, zs, -1, true);
            }
            translate([0, 0, 2 * j_d + 10]) difference() {
                intersection() { upright_cap(kind); bx(-50, xs + 50, -50, 50, zs, zs + joint_l); }
                for (r = socks(kind)) socket(r, zs, 1);
            }
        }
        color([0.95, 0.6, 0.25]) for (r = socks(kind)) translate([0, 0, j_d + 5]) joiner(r, zs);
    }
}

// every part in its place in the window, the foam and the window as ghosts; explode > 0 spreads the pieces apart
// along the height (then the ghosts are left out)
module assembly_view() {
    n = len(splits);
    e = explode;
    color([0.9, 0.75, 0.3]) bottom_cap();
    color([0.95, 0.6, 0.25]) translate([0, 0, (n + 2) * e]) top_cap();
    // segments alternate between a lighter and a darker shade (render(): a clean preview of their sockets)
    for (i = [0 : n]) translate([0, 0, (i + 1) * e]) {
        color(i % 2 == 0 ? [0.4, 0.6, 0.9] : [0.22, 0.38, 0.7]) render() segment("side", i);
        color(i % 2 == 0 ? [0.5, 0.8, 0.6] : [0.27, 0.58, 0.38]) render() segment("sash", i);
    }
    for (i = [0 : n - 1]) translate([0, 0, (i + 1.5) * e]) color([0.85, 0.3, 0.3])
        for (kind = ["side", "sash"], r = socks(kind)) joiner(r, splits[i]);
    if (e == 0) {
        %translate([base, -foam_t / 2, zb]) cube([foam_w, foam_t, zt - zb]);
        %window_ghost();
    }
}

/* =================== CORNER TEST PIECES =================== */
// The real cap ends, in their print orientation (all print standing, cross-section on the bed). One top piece and
// one bottom piece serve both corners: turn them end for end for the sash corners.
module corner_top()    linear_extrude(corner_l) cap_section("top");
module corner_bottom() linear_extrude(corner_l) cap_section("bottom");

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
for (i = [0 : len(splits)]) {
    if (part == str("side_", i))  segment_print("side", i);
    if (part == str("sash_", i))  segment_print("sash", i);
}
if (part == "joiner_side")        joiner_print("side");
if (part == "joiner_sash")        joiner_print("sash");
if (part == "joiners")            joiners();
if (part == "joint_tests")        joint_tests();
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
if (part == "corners_view")       corners_view();
if (part == "slices")             slices();
if (part == "slice_top")          slice("top");
if (part == "slice_bottom")       slice("bottom");
if (part == "slice_side")         slice("side");
if (part == "slice_sash")         slice("sash");
if (part == "slice_pair_view")    slice_pair_view();
