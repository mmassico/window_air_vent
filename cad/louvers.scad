// =====================================================================
//  Window vent: adjustable louvers for the intake fan (optional add-on)
//  Parametric OpenSCAD model (tested with OpenSCAD 2021.01).
//
//  * A frame clips onto the room face of the intake fan: four hooks reach
//    back over the fan's corner flanges and catch behind them. Recesses in
//    its corners fit over the fan's screw heads. A firm pull takes it off.
//  * Six horizontal blades pivot on pins at both ends, in U-slots that
//    open toward the fan: the blades drop in from behind, and the fan's
//    face closes the slots.
//  * A link bar joins an offset pin on each blade, so turning any blade
//    turns them all. The pins' snug fit in the slots holds the angle.
//  * Two retaining combs, one per side wall, plug the slots behind the
//    pins, so the blades can't come out.
//  * A strip of 1 mm felt or foam tape on the link bar's outer face rubs
//    on the side wall: it damps vibration and adds friction. On the other
//    side, a collar on each blade's pivot bears on the wall.
//
//  Coordinates: x across (blade span), z up, y along the airflow
//  (y = 0 on the fan face, y = depth on the room side).
// =====================================================================

/* [Part to show or export] */
part  = "assembly"; // [assembly, chassis, blade, link, retainer]
angle = 30;         // [-45:5:45] blade angle in the assembly preview (positive: air deflected upward)

/* [Frame] */
fan      = 80;      // fan size (the frame matches it)
fan_hole = 71.5;    // fan screw spacing
depth    = 19;      // frame depth along the airflow (room for the link's swing)
wall     = 3;       // frame walls
tube_r   = 4;       // corner posts, over the fan's screw heads
head     = [6.2, 3.5];  // recess for the fan screw heads (diameter, depth from the back face)

/* [Clips] */
flange   = 7;       // fan corner flange, front face (with the rubber pad) to its back side
clip_w   = 8;       // clip width (along x)
clip_edge = 8;      // distance from the fan's side edge to the clip: 8+ keeps them clear of the corner screws
                    // (closer, the retainer must stay under 2.8); the fan's flange allows clips up to 16 mm from the edge
clip_lip = 5;       // how far the retainer reaches in behind the flange (the fan allows 5 for clips under 14 wide)
clip_t   = 2.4;     // arm thickness
clip_root = 6;      // the arms are joined to the frame only over its front clip_root mm, so they flex over a long length

/* [Blades] */
n_blades = 6;
pitch    = 9.5;     // blade spacing (z); the link bar's ends then clear the corner posts at 45 deg
chord    = 12;      // blade width (along the airflow when open)
thick    = 2;       // blade thickness
pin_d    = 3;       // pivot and link pins
slot_w   = 3.05;    // pivot slots: just over the pin, so the blades turn stiffly and hold their angle
pin_in   = 2.5;     // how far the pivot pins reach into the walls
arm      = 6.5;     // link pin offset from the pivot, toward the fan (the bar clears the pivot pins up to 45 deg)

/* [Retaining combs] */
comb_t   = 2;       // spine thickness (y), in a rebate at the back of each side wall
comb_clr = 0.3;     // pegs stop this far short of the pivot pins

/* [Link] */
link_t   = 2.4;     // link bar thickness (x)
link_w   = 5;       // link bar width (y)
link_hole = 1.6;    // blind holes for the link pins, from the blade side (the pad side stays solid)
gap      = 0.5;     // running clearance
pad_t    = 1;       // friction pad on the link bar's outer face (felt or foam tape)
pad_sq   = 0.2;     // how much the pad is squeezed against the wall
collar   = [5, 1];  // collar on each blade's pivot, plain side (diameter, thickness), 0.2 from the wall

/* [Hidden] */
$fn = 48;
eps = 0.01;
xi  = fan / 2 - wall;                         // inner face of the side walls
yp  = depth / 2;                              // pivot axis (y)
zs  = [for (i = [0 : n_blades - 1]) (i - (n_blades - 1) / 2) * pitch];   // pivot heights
x0  = -xi + 0.2 + collar[1];                  // blade end, plain side (the collar sits between it and the wall)
xl  = xi - pad_t + pad_sq - link_t;           // link bar, inner face (its pad touches the wall)
x1  = xl - gap;                               // blade end, link side

assert(max(zs) + chord / 2 < fan_hole / 2 - tube_r, "outer blades would hit the corner tubes when turned");
assert(arm * cos(45) > link_w / 2 + pin_d / 2 + 0.3, "at 45 deg the link bar would touch the pivot pins");
assert(yp - arm - link_w / 2 > 0.3, "the link bar would touch the fan");

/* =================== CHASSIS =================== */
// Prints front face down (y = depth on the bed): the slots open upward, nothing overhangs.
module chassis() {
    difference() {
        union() {
            difference() {
                translate([-fan / 2, 0, -fan / 2]) cube([fan, depth, fan]);
                translate([-xi, -1, -xi]) cube([2 * xi, depth + 2, 2 * xi]);
            }
            for (dx = [-1, 1], dz = [-1, 1])   // corner posts
                translate([dx * fan_hole / 2, 0, dz * fan_hole / 2]) rotate([-90, 0, 0]) cylinder(r = tube_r, h = depth);
            clips();
        }
        for (dx = [-1, 1], dz = [-1, 1])       // recesses over the fan's screw heads
            translate([dx * fan_hole / 2, -1, dz * fan_hole / 2]) rotate([-90, 0, 0]) cylinder(d = head[0], h = head[1] + 1, $fn = 32);
        for (sx = [-1, 1])                     // rebates for the retaining combs, at the back of the side walls
            translate([sx > 0 ? xi - eps : -fan / 2 - 1, -1, zs[0] - pitch / 2]) cube([wall + 1 + eps, comb_t + 1, (n_blades) * pitch]);
        for (z = zs, sx = [-1, 1])             // pivot slots, open toward the fan, through the side walls
            translate([sx > 0 ? xi - 1 : -fan / 2 - 1, 0, z]) rotate([0, 90, 0]) linear_extrude(wall + 2)
                hull() { translate([0, yp]) circle(d = slot_w); translate([0, -1]) circle(d = slot_w); }
    }
}

// Four snap hooks, top and bottom near the corners. Seen from the side, each arm lies just outside the frame
// (0.4 mm away, so it flexes freely) and is joined to it only at the front; behind the frame it runs over the fan's
// flange, then a triangular retainer with 45 deg faces reaches in behind it (both faces print without overhang).
module clips() {
    g  = 0.4;                        // arm to frame gap
    z0 = fan / 2 + g;                // arm inner face
    yc = -(flange + 0.2);            // where the retainer starts (0.2 mm clearance behind the flange)
    for (sx = [-1, 1], sz = [-1, 1])
        translate([sx * (fan / 2 - clip_edge - clip_w / 2) - clip_w / 2, 0, 0]) mirror([0, 0, sz < 0 ? 1 : 0])
            rotate([90, 0, 90]) linear_extrude(clip_w) polygon([
                [depth, fan / 2 - eps], [depth, z0 + clip_t], [yc - 2 * clip_lip, z0 + clip_t], [yc - 2 * clip_lip, z0],
                [yc - clip_lip, z0 - clip_lip], [yc, z0], [depth - clip_root, z0], [depth - clip_root, fan / 2 - eps]]);
}

/* =================== BLADE =================== */
// Modelled open (chord along y), pivot axis on the x axis. Prints flat: the pins are flattened on the bed side.
module blade() {
    intersection() {
        union() {
            translate([x0, 0, 0]) rotate([0, 90, 0]) linear_extrude(x1 - x0)   // rounded-edge slat
                hull() for (s = [-1, 1]) translate([0, s * (chord / 2 - thick / 2)]) circle(d = thick);
            translate([-xi - pin_in, 0, 0]) rotate([0, 90, 0]) cylinder(d = pin_d, h = x0 + xi + pin_in + eps);   // pivot, plain side
            translate([x0 - collar[1], 0, 0]) rotate([0, 90, 0]) cylinder(d = collar[0], h = collar[1] + eps);       // collar
            translate([x1 - eps, 0, 0]) rotate([0, 90, 0]) cylinder(d = pin_d, h = xi + pin_in - x1 + eps);       // pivot, link side
            translate([x1 - eps, -arm, 0]) rotate([0, 90, 0]) cylinder(d = pin_d, h = gap + link_hole - 0.2 + eps); // link pin
            hull() {   // arm carrying the link pin, inside the blade's end
                translate([x1 - 2, 0, 0]) rotate([0, 90, 0]) cylinder(d = thick, h = 2);
                translate([x1 - 2, -arm, 0]) rotate([0, 90, 0]) cylinder(d = pin_d, h = 2);
            }
        }
        translate([-fan, -fan, -thick / 2]) cube([2 * fan, 2 * fan, fan]);   // flat underside for printing
    }
}

/* =================== RETAINING COMB =================== */
// Modelled in place in the +x wall (mirror it for the other one). A spine in the wall's back rebate, and a peg
// in each slot up to just short of the pivot pin. Prints flat, spine down.
module retainer() {
    zr = [zs[0] - pitch / 2 + 0.2, zs[n_blades - 1] + pitch / 2 - 0.2];
    translate([xi + 0.1, 0, 0]) {
        translate([0, 0, zr[0]]) cube([wall - 0.1, comb_t, zr[1] - zr[0]]);
        for (z = zs) translate([0, 0, z - (slot_w - 0.05) / 2]) cube([wall - 0.1, yp - pin_d / 2 - comb_clr, slot_w - 0.05]);
    }
}

/* =================== LINK =================== */
// Prints flat. Modelled in place for the open position (blade angle 0).
module link() {
    difference() {
        hull() for (z = [zs[0], zs[n_blades - 1]]) translate([xl, yp - arm, z]) rotate([0, 90, 0]) cylinder(d = link_w, h = link_t);
        for (z = zs) translate([xl - 1, yp - arm, z]) rotate([0, 90, 0]) cylinder(d = pin_d + 0.25, h = 1 + link_hole, $fn = 24);
    }
}

// The friction pad (bought: felt or foam tape), on the link bar's outer face, for the preview only.
module pad() hull() for (z = [zs[0], zs[n_blades - 1]]) translate([xl + link_t, yp - arm, z]) rotate([0, 90, 0]) cylinder(d = link_w, h = pad_t - pad_sq);

/* =================== PREVIEW =================== */
module blade_at(z, a) translate([0, yp, z]) rotate([a, 0, 0]) blade();

module assembly(a = angle) {
    color([0.85, 0.85, 0.88]) chassis();
    for (z = zs) color([0.55, 0.75, 0.95]) blade_at(z, a);
    // the link follows the link pins: they move by the arm's rotation
    color([0.95, 0.6, 0.25]) translate([0, yp, 0]) translate([0, -arm * cos(a), -arm * sin(a)]) translate([0, arm, 0]) translate([0, -yp, 0]) link();
    for (sx = [0, 1]) color([0.4, 0.75, 0.4]) mirror([sx, 0, 0]) retainer();
    color([0.3, 0.3, 0.3]) translate([0, -arm * cos(a) + arm, -arm * sin(a)]) pad();
    %translate([-fan / 2, -25, -fan / 2]) cube([fan, 25, fan]);   // the fan (ghost)
}

if (part == "assembly") assembly();
if (part == "chassis")  translate([0, 0, depth]) rotate([-90, 0, 0]) chassis();              // front face on the bed
if (part == "blade")    translate([-x0 + pin_in + 3, 0, thick / 2]) blade();                  // flat, flattened pins down
if (part == "link")     rotate([0, 90, 0]) translate([-(xl + link_t), 0, 0]) link();   // flat, holes up
if (part == "retainer") rotate([90, 0, 0]) translate([-xi, 0, 0]) retainer();   // x2, spine down, pegs up
