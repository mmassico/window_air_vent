// =====================================================================
//  Air conditioner window insert: hollow printed boxes
// =====================================================================
//  Boxes stacked between the top and bottom caps, held by the caps. Each
//  box is a thin shell with inner walls
//  parallel to its faces: the air gaps between them insulate in series,
//  like the panes of a triple-glazed window. A copy of the vent insert's
//  insert_boxes.scad (../../cad/), with the air conditioner's
//  hose hole in place of the vent's two holes.
//
//  Every box prints standing: its faces and inner walls are plain
//  vertical walls, and each cell's roof is a 45 deg gable (as is the end
//  of each socket's solid block), so nothing needs supports and there is
//  no flat ceiling to bridge. The box at the window latch
//  is notched around it.
//
//  The AC box has the hose's hole (ac_hole.scad) in a panel_t thick
//  panel on its room face: the hose's end clips onto it there, as on the
//  air conditioner's own panel. Behind the panel, a tunnel runs out
//  through the box, the hole's outline (its hull) grown by tun_clr, with
//  room for the clips. The box is as tall as the hole and its tunnel;
//  at the floor (ac_box = 0, the hole as low as it goes), taller at its
//  bottom, so the hole clears the bottom cap's room-side lip by ac_face
//  (the hose's minimum, plus a margin).
//
//  A hole through a standing box would have a flat overhang at its top,
//  so the AC box is cut into three pieces: through the upper notches'
//  bottom edge and the lower notches' top edge. The top piece prints
//  upside down: both arcs, of the hole and of the tunnel, then print as
//  bowls, and no notch has an overhanging edge. The middle piece is two
//  pillars; a snap joiner in each pillar at each joint (the side cap's)
//  holds the three pieces together.
//
//  Coordinates as in window_caps.scad, which this file includes: x across
//  the window from the side frame's face, u (y) across the thickness from
//  the insert's centre (outdoor negative), z up from the floor.
// =====================================================================

include <window_caps.scad>
include <ac_hole.scad>

/* [Part to show or export] */
part = "box_view";   // [box_0a, box_0b, box_0c, ac_joiners, box_1, box_2, box_3, box_4, box_5, box_6, box_7, box_view]

/* [Boxes] */
n_box    = 8;       // boxes in the stack, numbered from 0 at the floor: the AC box and 7 others, 114.3 tall (shorter
                    //   boxes print better). Keep the joints between boxes out of the latch zone: with 8, it is all
                    //   in box 3 (6, 7 or 9 boxes put a joint through it; see the warning below)
n_in     = 2;       // inner walls, parallel to the faces: n_in + 1 air gaps across the thickness
w_face   = 1.2;     // faces and edges (3 lines with a 0.4 nozzle)
w_in     = 0.8;     // inner walls (2 lines)
w_end    = 1.2;     // end plates
corbel   = 99;      // 45 deg corbels in each cell's top corners (as printed), at most gap / 2: the roof bridges gap - 2
                    //   corbel. 99: a full gable, no ceiling at all (its triangles print as infill); 0: a flat bridge
box_t    = ins_t;   // thickness: the insert's, so the boxes slide between the caps' lips
box_xclr = 0.5;     // the boxes are this much narrower than the gap (ins_w): rigid, they must still let the sash close
top_tape = 2.5;     // foam tape in the top channel, above the stack
box_tag  = [6, 0.4]; // each box's label (0a, 0b, 0c, 1, 2...) on its side-frame end: letter height, engraving depth
                     //   (the end wall is w_face thick)

/* [Air conditioner box] */
ac_box   = 0;       // the box with the hose's hole, cut into pieces a to c (box_0a to box_0c when it is 0): at the
                    //   floor, the hole as low as it goes. It must stay clear of the latch zone (box 2)
tun_clr  = 5;       // the tunnel behind the panel: the hole's outline (its hull) grown by this, room for the hose
                    //   end's clips
ac_face  = [12.85, 2];   // free room face the hose's end needs below the hole: the least it takes (measured), and a
                         //   margin. At the floor, the hole stays their sum above the bottom cap's lip. The end's top
                         //   and bottom lips are wider than its side ones: across the window it needs 115 between
                         //   the caps' lips, and has 120
ac_cap   = 10;      // material above the tunnel's top: box_0c stands on that face, printed upside down (the tunnel's
                    //   45 deg V under the bed makes it solid over the arc)

/* [Air conditioner box: joints] */
ac_joints = true;   // snap joiners between the AC box's pieces, one in each pillar at each joint: window_caps.scad's
                    //   socket, snap tab and joiner, as in the side cap. The tab is on the box's end face
j_sw     = 14;      // the socket's width across the thickness (u), centred: the sash cap's 14.0, with the same tab.
                    //   With its walls (j_wall) it fills the middle air gap only, between the inner walls: the outer
                    //   gaps stay whole, and no solid plastic crosses the box from face to face

// at the floor, the AC box is taller at its bottom, so the hole clears the bottom cap's lip by ac_face
ac_lift = ac_box == 0 ? max(0, lip_d + ac_face[0] + ac_face[1] - (tun_clr + w_face)) : 0;
ac_h = hole_h + 2 * (tun_clr + w_face) + ac_lift + ac_cap;   // the AC box's height
hb   = (zt - zb - top_tape - ac_h) / (n_box - 1);      // the other boxes' height
bw   = ins_w - box_xclr;                              // box width
bx0  = base + box_xclr / 2;                            // its side-frame end
gap  = (box_t - 2 * w_face - n_in * w_in) / (n_in + 1);   // each air gap
vx   = base + ins_w / 2;                              // the hole's centre line across the window

function bz(i) = zb + i * hb + (i > ac_box ? ac_h - hb : 0);   // box i's bottom
function bh(i) = i == ac_box ? ac_h : hb;                     // its height
function cell_u(k) = -box_t / 2 + w_face + k * (gap + w_in);  // cell k's outdoor side

ac_top = bz(ac_box) + ac_h;
hz     = ac_top - ac_cap - tun_clr - w_face + hole_top;   // the drawing's top edge (y = 0 in ac_hole())

// the AC box's pieces: [bottom, top, upside down]. Cut through the upper notches' bottom edge and the lower notches'
// top edge
ac_cuts   = [bz(ac_box), hz - notches[1][0], hz - (notches[0][0] + notches[0][1]), ac_top];
ac_pieces = [for (k = [0 : 2]) [ac_cuts[k], ac_cuts[k + 1], k == 2]];
ac_joins  = [ac_cuts[1], ac_cuts[2]];   // the joints between them

// the sockets at those joints, as socks() in window_caps.scad: [x from, x to, u from, u to, the snap tab's face (-1:
// toward -x, 1: toward +x), depth]. One in each pillar, between the box's end face (the tab, j_wall thick) and the
// tunnel's wall
xt = notch_w / 2 + tun_clr + w_face;   // the tunnel's wall, outside, from the hole's centre line
ac_socks = [[bx0 + j_wall, vx - xt, -j_sw / 2, j_sw / 2, -1, j_d[0]],
            [vx + xt, bx0 + bw - j_wall, -j_sw / 2, j_sw / 2, 1, j_d[0]]];
ac_boss = j_stop(ac_socks[0]) + (ac_socks[0][1] - ac_socks[0][0]) / 2 + w_end;   // the pillar is solid this far
                                                                                 //   from a joint (the socket's gable,
                                                                                 //   and an end plate past it)

// a 2D shape in the x-z plane at (x, z), run along u from u0 to u1
module along_u(x, z, u0 = -box_t / 2 - 1, u1 = box_t / 2 + 1)
    translate([x, u1, z]) rotate([90, 0, 0]) linear_extrude(u1 - u0) children();

// the tunnel behind the panel, 2D, in ac_hole()'s coordinates
module tunnel2d() hull() offset(r = tun_clr, $fn = 48) ac_hole();

// the tunnel's wall, outside: the tunnel grown by the wall, with a 45 deg V on the side that faces the bed (dn = -1:
// down as installed, 1: up), so the cell beside it there has a self-supporting roof
module sleeve2d(dn) let(r = hole_w / 2, R = r + tun_clr + w_face,
                        yc = dn < 0 ? -(hole_top + hole_h - r) : -(hole_top + r))
    hull() {
        offset(r = w_face, $fn = 48) tunnel2d();
        translate([0, yc + dn * R * sqrt(2)]) square(eps, center = true);
    }

// the latch zone's notch (37 x 7.2 x 80 at its floor), its top and bottom sloped 45 deg toward the room face, grown
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

// a closed piece of the stack from z0 to z1, in its place in the window (a whole box, or a piece of the AC box)
module piece(z0, z1, flip = false) {
    ac = z0 < ac_top - eps && z1 > bz(ac_box) + eps;
    pj = ac_joints ? [for (c = ac_joins) if (abs(c - z0) < eps || abs(c - z1) < eps) c] : [];   // its joints
    difference() {
        bx(bx0, bx0 + bw, -box_t / 2, box_t / 2, z0, z1);
        difference() {
            for (k = [0 : n_in]) cell(k, z0, z1, flip);
            notch(w_face);
            if (ac) along_u(vx, hz) sleeve2d(flip ? 1 : -1);
            // the pillars, solid around the sockets, in the middle air gap. Past their end inside the piece, a 45 deg
            // corbel grows from each inner wall toward the middle and meets the other under the block: printed under
            // the middle cell, the block is a gable roof, no ceiling (and a floor with a groove when printed over it)
            for (c = pj, r = ac_socks) let(s = abs(c - z0) < eps ? 1 : -1, hw = j_sw / 2 + j_wall,
                                           zn = c + s * ac_boss, zf = zn + s * hw, xa = r[0] - j_wall, xb = r[1] + j_wall) {
                bx(xa, xb, -hw, hw, c - ac_boss, c + ac_boss);
                for (t = [-1, 1]) hull() {
                    bx(xa, xb, t * (hw - eps), t * hw, zn, zf);   // at the wall, from the block to the corbel's foot
                    bx(xa, xb, 0, t * hw, zn - s * eps, zn);      // under the block, to the middle
                }
            }
        }
        notch();
        if (ac) {
            along_u(vx, hz, u1 = box_t / 2 - panel_t) tunnel2d();   // from the outdoor face to the panel
            along_u(vx, hz) ac_hole();                              // through the panel
            // a notch whose edge is this piece's cut face, carried 1 mm past it: on the exact plane, rounding leaves
            // a skin of panel over the notch, a few microns thick (a thin overhang in the slicer)
            for (n = notches) let(n1 = hz - n[0], n0 = n1 - n[1]) {
                if (abs(n0 - z0) < eps) bx(vx - notch_w / 2, vx + notch_w / 2, -box_t / 2 - 1, box_t / 2 + 1, z0 - 1, n1);
                if (abs(n1 - z1) < eps) bx(vx - notch_w / 2, vx + notch_w / 2, -box_t / 2 - 1, box_t / 2 + 1, n0, z1 + 1);
            }
        }
        // a socket opening up as it prints has a flat bottom, one opening down a gable (as segment() does)
        for (c = pj, r = ac_socks) let(lo = abs(c - z0) < eps)
            socket(r, c, lo ? 1 : -1, lo ? flip : !flip);
    }
}

// a piece with its label engraved on its side-frame end, at mid-height, centred across the thickness, reading
// upright as installed (clear of the snap tabs near the joints, and of the latch notch on the room side)
module labelled(s, z0, z1, flip) difference() {
    piece(z0, z1, flip);
    multmatrix([[0, 0, -1, bx0], [-1, 0, 0, 0], [0, 1, 0, (z0 + z1) / 2], [0, 0, 0, 1]])
        translate([0, 0, -box_tag[1]]) linear_extrude(box_tag[1] + 1) label(s, box_tag[0]);
}

// in its print orientation, standing, its side-frame end at x = 0: as installed, or upside down
module piece_print(s, z0, z1, flip = false)
    if (flip) translate([-bx0, 0, z1]) rotate([180, 0, 0]) labelled(s, z0, z1, true);
    else      translate([-bx0, 0, -z0]) labelled(s, z0, z1, false);

// a joiner for the AC box, printed lying on its back, bumps up (as joiner_print() in window_caps.scad)
module ac_joiner_print(r)
    translate([0, -(r[2] + r[3]) / 2, r[4] < 0 ? r[1] - j_clr : -(r[0] + j_clr)])
        rotate([0, r[4] < 0 ? 90 : -90, 0]) joiner(r, 0);

// all four: one in each pillar at each joint
module ac_joiners() for (k = [0 : 3]) translate([0, k * 28, 0]) ac_joiner_print(ac_socks[k % 2]);

// the stack in the window, with the caps (no joints or labels: the full caps, as one piece each)
module box_view() {
    color([0.9, 0.75, 0.3]) bottom_cap();
    color([0.95, 0.6, 0.25]) top_cap();
    color([0.4, 0.6, 0.9]) side_cap();
    color([0.5, 0.8, 0.6]) sash_cap();
    // every piece of the stack from the floor up, the AC box's included, alternating between a lighter and a darker
    // violet
    stack = [for (i = [0 : n_box - 1]) each (i == ac_box ? ac_pieces : [[bz(i), bz(i) + hb, false]])];
    for (k = [0 : len(stack) - 1])
        color(k % 2 == 0 ? [0.72, 0.58, 0.88] : [0.47, 0.33, 0.68]) render() piece(stack[k][0], stack[k][1], stack[k][2]);
    if (ac_joints) color([0.85, 0.3, 0.3]) for (c = ac_joins, r = ac_socks) joiner(r, c);
    %window_ghost();
}

for (i = [0 : n_box - 1])
    if (i == ac_box) for (k = [0 : 2]) {
        if (part == str("box_", i, chr(97 + k))) piece_print(str(i, chr(97 + k)), ac_pieces[k][0], ac_pieces[k][1], ac_pieces[k][2]);
    }
    else if (part == str("box_", i)) piece_print(str(i), bz(i), bz(i) + hb);
if (part == "ac_joiners") ac_joiners();
if (part == "box_view") box_view();

// the latch notch's extent on the room face, and a warning when a joint between boxes runs through it (or within an
// end plate of it)
lat_z = let(lz = bot_ribs[0][2] + latch[1], d = box_t / 2 - latch[0] + clr) [lz - clr - d, lz + latch[2] + clr + d];
lat_cut = [for (i = [1 : n_box - 1]) if (bz(i) > lat_z[0] - w_end && bz(i) < lat_z[1] + w_end) bz(i)];
if (len(lat_cut) > 0) echo(str("WARNING: a joint between boxes runs through the latch notch, at z = ", lat_cut));
echo(latch_notch = lat_z, latch_box = [for (i = [0 : n_box - 1]) if (bz(i) < lat_z[1] && bz(i) + bh(i) > lat_z[0]) i]);
echo(box_h = hb, ac_box_h = ac_h, ac_lift = ac_lift, hole_bottom = hz - hole_top - hole_h, box_w = bw, air_gap = gap, ac_box_z = [bz(ac_box), ac_top],
     ac_pieces_h = [for (p = ac_pieces) p[1] - p[0]]);
