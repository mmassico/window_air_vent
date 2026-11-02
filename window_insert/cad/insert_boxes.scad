// =====================================================================
//  Window insert: hollow printed boxes in place of the foam (evaluation)
// =====================================================================
//  Five boxes stacked between the top and bottom caps, where the XPS foam
//  would go, held by the same caps. Each box is a thin shell with inner
//  walls parallel to its faces: the air gaps between them insulate in
//  series, like the panes of a triple-glazed window.
//
//  Every box prints standing: its faces and inner walls are plain vertical
//  walls, and each cell's roof is a short bridge between two 45 deg
//  corbels, so nothing needs supports. The box at the window latch is
//  notched around it, like the foam.
//
//  The vent box takes the vent's two holes (and the outdoor probe's), as
//  sleeves through all its walls. A hole through a standing box would have
//  a flat overhang at its top, so the vent box is cut into four pieces,
//  through each hole's centre and midway between them: every half hole
//  then prints as a bowl, open side up, the pieces with a hole's top half
//  upside down.
//
//  Coordinates as in window_caps.scad, which this file includes: x across
//  the window from the side frame's face, u (y) across the thickness from
//  the foam's centre (outdoor negative), z up from the floor.
// =====================================================================

include <window_caps.scad>

/* [Part to show or export] */
part = "box_view";   // [box_0, box_1a, box_1b, box_1c, box_1d, box_2, box_3, box_4, bore_test, box_view]

/* [Boxes] */
n_box    = 5;       // boxes in the stack, numbered from 0 at the floor
n_in     = 2;       // inner walls, parallel to the faces: n_in + 1 air gaps across the thickness
w_face   = 1.2;     // faces and edges (3 lines with a 0.4 nozzle)
w_in     = 0.8;     // inner walls (2 lines)
w_end    = 1.2;     // end plates
corbel   = 3;       // 45 deg corbels in each cell's top corners (as printed): the roof bridges gap - 2 corbel (0: a
                    //   flat bridge across the gap; gap / 2: a full gable, but its solid triangle costs 20 cm3 a box)
box_t    = foam_t;  // thickness: the foam's, so the boxes slide between the caps' lips
box_xclr = 0.5;     // the boxes are this much narrower than the foam: rigid, they must still let the sash close
top_tape = 2.5;     // foam tape in the top channel, above the stack

/* [Vent box] */
vent_box = 1;       // the box with the vent's holes, cut into pieces a to d (box_1a to box_1d when it is 1); the
                    //   housing must stay clear of the latch zone (box 2)
v_pitch  = 96;      // between the two holes' centres (window_vent.scad: pitch)
v_bore   = 84.1;    // hole for the housing's 83.7 spigots, 0.2 per side: rigid, unlike foam, so it can't squeeze
probe    = true;    // the outdoor temperature probe's hole, above the intake
probe_d  = 6.5;     // for the 6 mm DS18B20 probe
probe_up = 102;     // above the vent's centre, as on the drilling template (pitch / 2 + 45 + 9)

hb  = (zt - zb - top_tape) / n_box;     // box height
bw  = foam_w - box_xclr;                // box width
bx0 = base + box_xclr / 2;              // its side-frame end
gap = (box_t - 2 * w_face - n_in * w_in) / (n_in + 1);   // each air gap
vx  = base + foam_w / 2;                // the vent's centre across the window

function bz(i) = zb + i * hb;           // box i's bottom
function cell_u(k) = -box_t / 2 + w_face + k * (gap + w_in);   // cell k's outdoor side

// the vent's centre height: holes and probe centred in the box
v_lo = v_pitch / 2 + v_bore / 2 + w_face;
v_hi = probe ? probe_up + probe_d / 2 + w_face : v_lo;
vz   = bz(vent_box) + (hb + v_lo - v_hi) / 2;
holes = concat([[vz + v_pitch / 2, v_bore / 2], [vz - v_pitch / 2, v_bore / 2]],
               probe ? [[vz + probe_up, probe_d / 2]] : []);   // [z, radius]

// the vent box's pieces: [bottom, top, upside down (a hole's top half at its bottom)]
v_cuts = [bz(vent_box), vz - v_pitch / 2, vz, vz + v_pitch / 2, bz(vent_box) + hb];
v_pieces = [for (k = [0 : 3]) [v_cuts[k], v_cuts[k + 1], k % 2 == 1]];

// a 2D shape in the x-z plane at (x, z), run through the box's thickness along u
module along_u(x, z) translate([x, box_t / 2 + 1, z]) rotate([90, 0, 0]) linear_extrude(box_t + 2) children();

// a sleeve's outside: the hole grown by the wall, with a 45 deg V on the side that faces the bed (dn = -1: down as
// installed, 1: up), so the cell beside it there has a self-supporting roof
module sleeve2d(r, dn) hull() {
    circle(r + w_face, $fn = 96);
    translate([0, dn * (r + w_face) * sqrt(2)]) square(eps, center = true);
}

// the latch zone's notch (the foam's 37 x 7.2 x 80), its top and bottom sloped 45 deg toward the room face, grown
// by g: g = 0 cuts the notch, g = w_face keeps the cells away from it
module notch(g = 0) {
    lz = bot_ribs[0][2] + latch[1];
    u0 = latch[0] - clr - g;
    u1 = box_t / 2 + 1;
    z0 = lz - clr - g;
    z1 = lz + latch[2] + clr + g;
    x1 = latch[3] + clr + g;
    hull() {
        bx(bx0 - 1, x1, u0, u0 + eps, z0, z1);
        bx(bx0 - 1, x1, u1 - eps, u1, z0 - (u1 - u0), z1 + (u1 - u0));
    }
}

// cell k of a piece from z0 to z1, its corbels under the roof as printed: at the top, or at z0 when upside down
module cell(k, z0, z1, flip) {
    a  = cell_u(k);
    c  = min(corbel, gap / 2 - eps);
    xa = bx0 + w_face;
    xb = bx0 + bw - w_face;
    za = z0 + w_end;
    zb_ = z1 - w_end;
    hull() {
        bx(xa, xb, a, a + gap, flip ? za + c : za, flip ? zb_ : zb_ - c);
        bx(xa, xb, a + c, a + gap - c, za, zb_);
    }
}

// a closed piece of the stack from z0 to z1, in its place in the window (a whole box, or a piece of the vent box)
module piece(z0, z1, flip = false) {
    vent = z0 < v_cuts[4] - eps && z1 > v_cuts[0] + eps;
    difference() {
        bx(bx0, bx0 + bw, -box_t / 2, box_t / 2, z0, z1);
        difference() {
            for (k = [0 : n_in]) cell(k, z0, z1, flip);
            notch(w_face);
            if (vent) for (h = holes) along_u(vx, h[0]) sleeve2d(h[1], flip ? 1 : -1);
        }
        notch();
        if (vent) for (h = holes) along_u(vx, h[0]) circle(h[1], $fn = 192);
    }
}

// in its print orientation, standing, its side-frame end at x = 0: as installed, or upside down
module piece_print(z0, z1, flip = false)
    if (flip) translate([-bx0, 0, z1]) rotate([180, 0, 0]) piece(z0, z1, true);
    else      translate([-bx0, 0, -z0]) piece(z0, z1, false);

// one half of a vent hole's sleeve, on its own: print two and put them together to try the spigot's fit (the vent
// box's pieces have the same bowl, printed open side up)
module bore_test() {
    r = v_bore / 2;
    R = r + w_face;
    translate([0, 0, R + 1]) difference() {
        intersection() {
            along_u(0, 0) sleeve2d(r, -1);
            bx(-100, 100, -100, 100, -(R + 1), 0);
        }
        along_u(0, 0) circle(r, $fn = 192);
    }
}

// the stack in the window, with the caps (no joints or labels: the full caps, as one piece each)
module box_view() {
    color([0.9, 0.75, 0.3]) bottom_cap();
    color([0.95, 0.6, 0.25]) top_cap();
    color([0.4, 0.6, 0.9]) side_cap();
    color([0.5, 0.8, 0.6]) sash_cap();
    // every piece of the stack from the floor up, the vent box's included, alternating between a lighter and a
    // darker violet
    stack = [for (i = [0 : n_box - 1]) each (i == vent_box ? v_pieces : [[bz(i), bz(i) + hb, false]])];
    for (k = [0 : len(stack) - 1])
        color(k % 2 == 0 ? [0.72, 0.58, 0.88] : [0.47, 0.33, 0.68]) render() piece(stack[k][0], stack[k][1], stack[k][2]);
    %window_ghost();
}

for (i = [0 : n_box - 1])
    if (i == vent_box) for (k = [0 : 3]) {
        if (part == str("box_", i, chr(97 + k))) piece_print(v_pieces[k][0], v_pieces[k][1], v_pieces[k][2]);
    }
    else if (part == str("box_", i)) piece_print(bz(i), bz(i) + hb);
if (part == "bore_test") bore_test();
if (part == "box_view")  box_view();
echo(box_h = hb, box_w = bw, air_gap = gap, vent_cuts = [for (c = v_cuts) c - bz(vent_box)]);
