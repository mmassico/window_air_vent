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
//  * This first step prints a thin slice of each profile, to check the
//    profiles and the clearance before printing whole caps. The second
//    prints the cap ends that meet in the four corners.
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
part = "corners";   // [corners, corner_top, corner_bottom, corner_side_top, corner_side_bottom, corner_sash_top, corner_sash_bottom, corners_view, slices, slice_top, slice_bottom, slice_side, slice_sash, slice_pair_view]

/* [Fit] */
clr      = 0.3;     // clearance per side on the window's ribs, channel and sash
clr_d    = 0.5;     // clearance at the bottom of a slot or channel (depth)
slice_t  = 5;       // slice thickness
base     = 3;       // cap material between the deepest window feature and the foam

cap_gap  = 0.5;     // between a cap's end and the cap it butts against (foam tape)
foam_clr = 0.2;     // per side, between the foam and the lips (it slides in)

/* [Foam] */
foam_t   = 50.8;    // foam thickness (2 in)
foam_w   = 100;     // foam width, side frame to sash

/* [Caps] */
lip_d    = 10;      // how far the lips reach onto the foam's faces
lip_t    = 2.4;     // lip thickness
corner_l = 40;      // corner test pieces: length past the cap they butt against

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
sash_t   = 25.80;   // sash thickness at its end (centred)
sash_in  = 10.70;   // how far the sash goes into its cap (17.10 max: there the sash widens)
groove   = [7.90, 7.50, 7.50];   // sash end groove: width at the mouth, width at the bottom, depth
groove_key = true;  // tongue in the sash's end groove (one more seal line)

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
    upright_body(0, base);
    tw = side_ch[0] / 2 - clr;
    td = side_ch[1] - clr_d;
    difference() {   // tongue, floor to ceiling in the channel
        translate([-td, -tw, clr_d]) cube([td + eps, 2 * tw, H - 2 * clr_d]);
        r = top_ribs[0];
        translate([-td - 1, r[0] - clr, H - r[2] - clr_d]) cube([td + 2, r[1] - r[0] + 2 * clr, r[2] + clr_d + 1]);
        b = bot_ribs[0];
        translate([-td - 1, b[0] - clr, -1]) cube([td + 2, b[1] - b[0] + 2 * clr, b[2] + clr_d + 1]);
        translate([-side_ch[1] - 1, strip[0] - clr, -1]) cube([strip[3] + clr + 1, strip[1] - strip[0] + 2 * clr, strip[2] + clr_d + 1]);
    }
}

module sash_cap() {
    upright_body(xs - base, xs - base - lip_d);
    z0 = zb + cap_gap;
    h  = zt - zb - 2 * cap_gap;
    for (s = [-1, 1])   // the channel's walls, along the sash's faces
        translate([xs - eps, s < 0 ? -ow : sash_t / 2 + clr, z0]) cube([sash_in + eps, ow - sash_t / 2 - clr, h]);
    if (groove_key) {   // tongue in the groove, tapered like it
        m = groove[0] / 2 - clr;
        b = groove[1] / 2 - clr;
        d = groove[2] - clr_d;
        translate([xs, 0, z0]) linear_extrude(h) polygon([[-eps, -m], [-eps, m], [d, b], [d, -b]]);
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
