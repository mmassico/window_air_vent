# Pre-print checklist

Every place where a printed part meets a bought part, with the value in the model, the hardware it must fit, and what is left to check. Go through it before the first print.

**Status:** ✅ checked against the spec · 📏 measure the real part · 🔧 model needs a change · ❓ open question

All dimensions in mm. Values come from `cad/window_vent.scad` (default parameters).

## Print tolerances in general

PETG holes usually come out 0.1–0.2 mm smaller than drawn, and holes printed **horizontally** (axis parallel to the bed) also come out slightly oval, lower at the top. The housing prints standing on its fan plate, so its shaft holes are horizontal; so is the shaft hole in each disc.

- 📏 After printing, run a **5.5 mm drill by hand** through the four shaft holes of the housing, and a **5 mm drill** through each disc hub. The shaft should turn freely in the housing and slide snugly through the hubs.
- ✅ Test prints (optional, before the 10-hour housing): first the small real parts (discs, motor plate, magnet cap), then `fittest` (the housing's printer-sensitive features in its print orientation, engraved A to G; the README lists what each one tests and when it passes) and `oring_test` (a spigot section with one O-ring groove, for the foam hole and the O-ring fit).

## Fans: Noctua NF-A8 PWM (80 × 80 × 25)

| Item | Model | Hardware | Status |
|---|---|---|---|
| Hole spacing | 71.5 square | 71.5 (standard 80 mm fan, Noctua spec); about 71.8 measured edge to edge, within caliper error | ✅ |
| Screw holes in the fan plate | Ø 3.4 | M3 clearance; the fan's own holes are Ø 4.3 (measured) | ✅ |
| Fan plate thickness | 6 | | |
| Nut pockets (back of the fan plate) | hex 5.8 across flats, 2.6 deep | M3 nut: 5.5 AF, 2.4 thick | ✅ |
| Screws | | M3 × 35: 27 (fan with its rubber pads, measured) + 6 (plate), nut in the last 2.6 mm; the tip ends 2 mm past the nut | ✅ |
| Bore | Ø 74 | NF-A8 blade circle about 76 | ✅ |

## Shaft: 5 mm steel rod, 200 mm (HSS)

| Item | Model | Hardware | Status |
|---|---|---|---|
| Bearing holes in the housing (4) | Ø 5.4 (0.4 clearance) | Ø 5.0 rod | ✅ ream if tight (see above) |
| Bearing bosses outside the ducts (4) | 45° cones, Ø 10 flat top around the shaft hole | | ✅ they stick out sideways when printing; the 45° sides leave no overhang |
| Shaft bosses inside the ducts (4) | Ø 16, 45° plane cut on the fan-plate side only | | ✅ only that side faces the bed when printing; the footprint is unchanged, so water flows around them and the air sees them as before |
| Water past lip B | the floor boss is cut back within 3 mm of lip B's end (x = −7 to −4), up to 3 mm past the lip on the fan side | | ✅ the conical lip reaches the boss along the floor; this keeps a 2–3 mm drain channel along the floor, and a 1.3 mm rim around the shaft hole |
| Bore in each disc hub | Ø 5.2, teardrop: 45° point up, toward the grub screws | | ✅ prints without support; the grub screws press the shaft into the round lower half; ream if tight |
| Length needed | 200: from 4.6 inside the magnet cap to about 10 into the coupler (8 minimum) | 200 | ✅ fits uncut |
| Grip | grub screws on a round rod | HSS is very hard | 📏 grind small flats where the discs, the coupler and the magnet cap clamp |
| Real diameter | | 4.99 measured, 200 long | ✅ |

## Discs: grub screws

| Item | Model | Hardware | Status |
|---|---|---|---|
| Screws per disc | 2, 24 apart | M3 grub screws | ✅ |
| Pilot hole | Ø 2.5, self-tapping | M3 thread | ✅ (or cut a thread with an M3 tap) |
| Depth from hub top to shaft | 6 | | ✅ M3 × 6 sits flush; M3 × 8 sticks out 2 mm, still clear of everything |
| Bevel on half B | 45°, 2 mm, on the bed-side rim, engraved B on the top face | | ✅ seats on the conical lip B with one foam-tape thickness (1 mm, square to the slope); prints as a 45° chamfer |
| Orientation | half B on the conical-lip side (right side, seen from the room) | | 📏 check before tightening the grub screws: turned the wrong way, the disc stops short of closed |

## Coupler: uxcell 5–5 mm, Ø 19 × 25 (measured Ø 18.8 × 24.64)

| Item | Model | Hardware | Status |
|---|---|---|---|
| Space between the upper shaft boss and the frame | 31 | 24.64 long | ✅ the coupler hangs on the motor shaft as before; 3 mm more room under the thinner roof |
| Space between the bracket walls | 50 | Ø 18.8 | ✅ |
| Passing through the motor frame (it goes on with the motor) | centre diamond, 23.1 across its flats (a little more than the motor plate's Ø 22.5 hole) | Ø 18.8 | ✅ 2.1 mm per side |
| Bore | | Ø 5 rod: snug, slides in | ✅ the set screws clamp it |
| Access to its set screws | diamond windows in both bracket walls | | ✅ |

## Motor: StepperOnline 17HS08-1004S (NEMA 17 pancake)

| Item | Model | Hardware | Status |
|---|---|---|---|
| Screw spacing | 31 square | 31 (NEMA 17) | ✅ |
| Screw holes in the motor plate | Ø 3.4 | M3 | ✅ |
| Centring boss hole | Ø 22.5 | boss Ø 22 × 2 | ✅ |
| Motor plate thickness | 4, plus a Ø 6 × 2 boss under each motor screw hole (`mp_boss`) | M3 × 8: 2 mm into the motor | ✅ the 17HS08-1004S's holes are 2.5 deep (sheet: 2.5 min; measured 2.5; [drawing](doc/motor_17hs08.svg)), so 0.5 mm spare ([section](doc/motor_mount.svg)). The bosses print upward (plate top face on the bed) |
| Frame pockets for the bosses and screw heads | 4 diamonds, 8 across the flats (`mp_pocket`) | boss Ø 6; button head Ø 5.7 | ✅ 1 mm clear around each boss; the heads end 0.65 below the 3 mm frame, in about 38 mm of empty tower |
| Shaft length | assumed 24 from the face | | 📏 measure; the coupler can slide up or down to suit |
| Motor plate to frame | front: 2 holes at ±20, 27 in front of the motor axis, through the 3 mm frame; back: 2 tabs (3 × 10, 8 below the frame), flush with the back edge, through notches, against the tower walls, Ø 3.4 holes through tab and wall | M3 × 10 + nut, all four | ✅ the front heads clear the motor body by 3 mm; the front nuts are reached from the tower's open front, the back ones from its open back; no nut pockets; `check.py` check 7 |

## Encoder: AS5600 board and magnet

Two common boards are supported. The chip is centred on both. Board B is the one in the kit, measured.

<p align="center"><img src="doc/as5600.svg" alt="AS5600 kit board, dimensioned: 23.3 x 22.8 mm, holes 3.6 mm at 3.3 mm from the edges, pin rows 5.2 mm from the sides" width="520"></p>

| Board | Size | Holes (centres) | Holes | Headers |
|---|---|---|---|---|
| A | 20 × 20 | 15 × 15 | not stated | 4-pin connector |
| B (the kit, sold with the magnet) | 23.3 × 22.8 × 1.6 thick; 3.22 over the chip | 16.7 × 16.2 (3.3 from each edge) | Ø 3.6 (M3) | 3 pins and 4 pins, 12.9 apart, along the 22.8 side |

| Item | Model | Hardware | Status |
|---|---|---|---|
| Board mounting | 4 diagonal slots from the 15 × 15 to the 17 × 17 position, 3.5 wide, on 2 mm standoff pads (Ø 5.5, a 1 mm wall around the slot; the lower 1 mm flares at 45° to Ø 7.5, clear of the solder joints under the board) | both boards above, M3 or smaller screws | ✅ board B's holes form a rectangle, 0.18 off the slot axis; the 3.5 width lets an M3 through |
| Screws | through board, pad and 4 mm plate | M3 × 12 + nut, or smaller screws with nylon washers if the holes are small | ✅ adapt to the board |
| Wiring | one diamond window, 13.5 point to point, under the chip | wires soldered straight to the board (no headers) | ✅ the wires run inward under the board (2 mm standoff gap) and down through the window |
| Magnet to chip | 1.5 nominal (`enc_gap`), set exactly on assembly: rest the magnet on a 1 mm shim laid on the chip, then tighten the cap's grub screw | AS5600: 0.5–3 recommended | ✅ the cap slides ±1, which also covers washers under the board |
| Magnet pocket | Ø 4.2 × 2.2 | 3.95 × 2 (kit, measured) | ✅ |

## Magnet cap on the shaft

| Item | Model | Hardware | Status |
|---|---|---|---|
| Cap | Ø 14 × 12, printed bore down | | ✅ |
| Bore | Ø 5.2 × 8.8 deep; the shaft reaches 4.6 in | Ø 5 rod | ✅ |
| Fixing | one radial M3 grub screw, 2 above the shaft end, self-tapping | M3 grub screw, 6 or 8 long | ✅ the cap must never turn on the shaft, or the firmware loses its "closed" reference |
| Height | slides ±1 before tightening; 1 mm below the bearing boss at its highest | | ✅ |

## O-rings and the foam insert

| Item | Model | Hardware | Status |
|---|---|---|---|
| Spigot | Ø 82 | foam hole Ø 82 | 📏 a 3-1/4 in hole saw cuts 82.6; test on a scrap |
| Groove bottom / width | Ø 77.5 / 4.2, two per spigot | O-ring 74 × 3, nitrile 70A | ✅ stretched 4.7% (≤ 5% for a static seal) |
| Wall under the groove | 1.75 | | ✅ no load on the spigot |
| Groove profile | flat floor, straight wall on the stop-ring side, 45° wall on the tip side (`oring_slope`) | | ✅ the spigots print tip up, so no wall is a flat overhang; the O-ring bears on the floor and the straight wall when pushed in |
| Squeeze in the hole | about 23% in an 82.0 hole | | 📏 less in an 82.6 hole; test the fit |
| Cold | nitrile is rated to −20 °C | | ✅ the grooves are in the room-side half of the foam, well above that |
| Hole spacing in the foam | 96 vertically, centred in the gap | | ✅ |

## Electronics box (`ebox`) and cables

| Item | Model | Hardware | Status |
|---|---|---|---|
| Inside | 75.2 × 71.6, 34 high under the encoder plate | perfboard 70 × 50; TMC2209 with its heatsink, soldered: 24.0 above the floor; in female headers: 32.5 ([drawing](doc/tmc2209.svg); spacer and PCB heights assumed, to measure) | ✅ 10 under the plate (1.5 in headers) |
| Perfboard standoffs | 4, 5 high, 66 × 46 apart, Ø 1.8 pilot | 5 × 7 cm protoboard, M2 holes about 2 from the corners | 📏 check your perfboard's hole spacing; set `pb_holes` |
| Layout | ESP32 across the back half, USB end 7.6 mm (3 holes) in from the left wall (`esp_dx`), or turned 180° toward the right wall (`ebox_elec_alt`); TMC2209 front right, by the cable entry ([drawing](doc/ebox_layout.svg)) | | ✅ |
| USB-C (power and console) | 18 mm diamond in each side wall (`usb_side`, `usb_port`; `"mark"` engraves a cross to drill a 12 mm hole instead), centre 18.2 above the inner floor | plug 11 × 6.25, 20 long, through the wall and 7.6 into the box; 5 V USB-C adapter | ✅ centred on the USB-UART connector (`usb_dy = 6`, measured: 8.25 from the board's TX/GND edge); the ESP32 lies components up, its 3V3/5V header row toward the window (toward the room when turned; the right-hand diamond is mirrored to match, 6 toward the window); both layouts checked clear of the standoffs |
| Power | no buck converter: 12 V brick for VM, fans and the 12 V sense; the ESP32 on USB | the brick's GND joined to the ESP32's GND on the perfboard | 📏 the board's 3.3 V regulator is a SOT-223 (usually an AMS1117-3.3, about 1 A); confirm its marking (about 600 mA peaks: Wi-Fi plus the SCD40) |
| Cable entries | notch at the top of each side wall, toward the front, 16 × 10 | 12 V brick wire, two fan cables, motor cable | ✅ use the one on the cable side |
| Fixing | 2 × M3 × 12 through the front cover into bosses (Ø 2.5 pilot) at the bay walls; 2 × M3 × 12 from above through the plate into back tabs | | ✅ |
| Contact with the housing | zero overlap (checked by `tools/check.py`) | | ✅ |
| Tie-wrap anchors | 3 on each side, 6 tall off the back of the fan plate (about 1.75–2 mm of material all around the slot), with a rounded back (radius 4) for the wires to rest on; top and bottom touch the outer fan nut pockets; house-shaped slot on the plate, 4.5 wide with 2 mm straight walls and a 45° roof (no flat ceiling when printing); same slot shape in both motor tower walls | tie wraps up to 3.6 wide | ✅ |
| SCD40 | not on the unit: on a free cable, out through a cable entry | I²C, about 1–2 m | ✅ place it in the room (near head height), away from the fresh-air jet, the electronics box and the sun; run the bus at 100 kHz or slower, pair SDA and SCL with GND and VCC |

## Split housing (`body_top`, `body_bottom`, `splice`): 180 mm printers only

| Item | Model | Hardware | Status |
|---|---|---|---|
| Part sizes | 90 × 130 × 114, 90 × 116 × 114, 60 × 32 × 6 | 180 × 180 × 180 bed (A1 mini) | ✅ |
| Halves = housing | identical except the four joint screw holes | | ✅ `check.py`, check 6 |
| Joint screws | Ø 3.4 holes through 6 (fan plate) + 6 (splice) | M3 × 12 countersunk (length includes the head): ends flush with the back of the splice, full nut engagement | ✅ |
| Nut pockets (back of the splice) | hex 5.8 across flats, 2.6 deep | M3 nut: 5.5 AF, 2.4 thick | ✅ |
| Screw heads on the fan face | 90° countersinks, Ø 7 at the face, at z = ±4.5 | flat head Ø 5.5–6.7 | ✅ flush or just below the fan face, so no contact with the fan frames (they start at ±8); 45° walls print from the bed without bridging |
| Splice to the ducts | 1 mm clearance all round | | ✅ |
| Middle tie-wrap anchors | whole, on `body_top`; the cut steps down 5 mm under them (1 mm below the anchor), so they print from the bed | | ✅ |
| Alignment | 0.2 mm radial play in the screw holes | shaft through all four bearing holes | ✅ tighten the screws after the shaft is in |
| Both halves from the same spool and profile | | | 📏 shrinkage must match for the shaft line |

## Open questions

None. The kit magnet (3.95 × 2) and the kit board are measured and in the model.
