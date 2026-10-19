# Pre-print checklist

Every place where a printed part meets a bought part, with the value in the model, the hardware it must fit, and what is left to check. Go through it before the first print.

**Status:** ✅ checked against the spec · 📏 measure the real part · 🔧 model needs a change · ❓ open question

All dimensions in mm. Values come from `cad/window_vent.scad` (default parameters).

## Print tolerances in general

PETG holes usually come out 0.1–0.2 mm smaller than drawn, and holes printed **horizontally** (axis parallel to the bed) also come out slightly oval, lower at the top. The housing prints standing on its fan plate, so its shaft holes are horizontal; so is the shaft hole in each disc.

- 📏 After printing, run a **5.5 mm drill by hand** through the four shaft holes of the housing, and a **5 mm drill** through each disc hub. The shaft should turn freely in the housing and slide snugly through the hubs.
- ✅ Test prints (optional, before the 10-hour housing): first the small real parts (discs, motor plate, magnet cap), then `fittest` (the housing's printer-sensitive features in its print orientation, engraved A to F; the README lists what each one tests and when it passes) and `oring_test` (a spigot section with one O-ring groove, for the foam hole and the O-ring fit).

## Fans: Noctua NF-A8 PWM (80 × 80 × 25)

| Item | Model | Hardware | Status |
|---|---|---|---|
| Hole spacing | 71.5 square | 71.5 (standard 80 mm fan) | ✅ |
| Screw holes in the fan plate | Ø 3.4 | M3 clearance | ✅ |
| Fan plate thickness | 6 | | |
| Nut pockets (back of the fan plate) | hex 5.8 across flats, 2.6 deep | M3 nut: 5.5 AF, 2.4 thick | ✅ |
| Screws | | M3 × 35: 25 (fan) + 6 (plate), nut in the last 2.6 mm | ✅ |
| Bore | Ø 74 | NF-A8 blade circle about 76 | ✅ |

## Shaft: 5 mm steel rod, 200 mm (HSS)

| Item | Model | Hardware | Status |
|---|---|---|---|
| Bearing holes in the housing (4) | Ø 5.4 (0.4 clearance) | Ø 5.0 rod | ✅ ream if tight (see above) |
| Bore in each disc hub | Ø 5.2 | | ✅ ream if tight |
| Length needed | 200: from 4.6 inside the magnet cap to about 10 into the coupler (8 minimum) | 200 | ✅ fits uncut |
| Grip | grub screws on a round rod | HSS is very hard | 📏 grind small flats where the discs, the coupler and the magnet cap clamp |
| Real diameter | | | 📏 measure with a caliper (HSS bar stock is often 4.98–5.00) |

## Discs: grub screws

| Item | Model | Hardware | Status |
|---|---|---|---|
| Screws per disc | 2, 24 apart | M3 grub screws | ✅ |
| Pilot hole | Ø 2.5, self-tapping | M3 thread | ✅ (or cut a thread with an M3 tap) |
| Depth from hub top to shaft | 6 | | ✅ M3 × 6 sits flush; M3 × 8 sticks out 2 mm, still clear of everything |

## Coupler: uxcell 5–5 mm, Ø 19 × 25

| Item | Model | Hardware | Status |
|---|---|---|---|
| Space between the upper shaft boss and the frame | 28 | 25 long | ✅ 3 mm of play |
| Space between the bracket walls | 50 | Ø 19 | ✅ |
| Access to its set screws | diamond windows in both bracket walls | | ✅ |

## Motor: StepperOnline 17HS08-1004S (NEMA 17 pancake)

| Item | Model | Hardware | Status |
|---|---|---|---|
| Screw spacing | 31 square | 31 (NEMA 17) | ✅ |
| Screw holes in the motor plate | Ø 3.4 | M3 | ✅ |
| Centring boss hole | Ø 22.5 | boss Ø 22 × 2 | ✅ |
| Motor plate thickness | 4 | M3 × 8: 4 mm into the motor | 📏 check the motor's thread depth (usually 4.5); never use longer than 8 |
| Shaft length | assumed 24 from the face | | 📏 measure; the coupler can slide up or down to suit |
| Motor plate to frame | 4 holes, 48 square, M3 × 10 | nuts slide into side slots (6.1 × 2.8) | ✅ |

## Encoder: AS5600 board and magnet

Two common boards are supported. The chip is centred on both.

| Board | Size | Hole square | Holes |
|---|---|---|---|
| A | 20 × 20 | 15 × 15 | not stated |
| B (the usual kit, sold with magnet and header) | 23 × 23 | 17 × 17 | about Ø 3.5 (M3) |

| Item | Model | Hardware | Status |
|---|---|---|---|
| Board mounting | 4 diagonal slots from the 15 × 15 to the 17 × 17 position, 3.2 wide, on 2 mm standoff pads | both boards above, M3 or smaller screws | ✅ |
| Screws | through board, pad and 4 mm plate | M3 × 12 + nut, or smaller screws with nylon washers if the holes are small | ✅ adapt to the board |
| Wiring | window 18 × 9 under the board | wires soldered straight into the board's holes (no header) | ✅ the window lets the wires out below |
| Magnet to chip | 1.5 nominal (`enc_gap`), set exactly on assembly: rest the magnet on a 1 mm shim laid on the chip, then tighten the cap's grub screw | AS5600: 0.5–3 recommended | ✅ the cap slides ±1, which covers a 2.5 or 3 mm magnet and washers under the board |
| Magnet pocket | Ø 6.2 × 2.7 | 6 × 2.5 (kit, per listings) | 📏 confirm when it arrives; a 3 mm magnet just sticks out 0.3, which the shim setting absorbs |

## Magnet cap on the shaft

| Item | Model | Hardware | Status |
|---|---|---|---|
| Cap | Ø 14 × 12, printed bore down | | ✅ |
| Bore | Ø 5.2 × 8.3 deep; the shaft reaches 4.6 in | Ø 5 rod | ✅ |
| Fixing | one radial M3 grub screw, 2 above the shaft end, self-tapping | M3 grub screw, 6 or 8 long | ✅ the cap must never turn on the shaft, or the firmware loses its "closed" reference |
| Height | slides ±1 before tightening; 1 mm below the bearing boss at its highest | | ✅ |

## O-rings and the foam insert

| Item | Model | Hardware | Status |
|---|---|---|---|
| Spigot | Ø 82 | foam hole Ø 82 | 📏 a 3-1/4 in hole saw cuts 82.6; test on a scrap |
| Groove bottom / width | Ø 77.5 / 4.2, two per spigot | O-ring 74 × 3, nitrile 70A | ✅ stretched 4.7% (≤ 5% for a static seal) |
| Wall under the groove | 1.75 | | ✅ no load on the spigot |
| Squeeze in the hole | about 23% in an 82.0 hole | | 📏 less in an 82.6 hole; test the fit |
| Cold | nitrile is rated to −20 °C | | ✅ the grooves are in the room-side half of the foam, well above that |
| Hole spacing in the foam | 96 vertically, centred in the gap | | ✅ |

## Electronics box (`ebox`) and cables

| Item | Model | Hardware | Status |
|---|---|---|---|
| Inside | 75.2 × 71.6, 32 high under the encoder plate | perfboard 70 × 50; TMC2209 with heatsink in female headers about 28 high | ✅ |
| Perfboard standoffs | 4, 5 high, 66 × 46 apart, Ø 1.8 pilot | 5 × 7 cm protoboard, M2 holes about 2 from the corners | 📏 check your perfboard's hole spacing; set `pb_holes` |
| USB-C | no slot by default (`usb_slot` length 0) | Freenove ESP32-S3 | ✅ flash once over USB on the bench, then update over Wi-Fi (OTA); a slot can be re-enabled |
| Cable entries | notch at the top of each side wall, toward the front, 16 × 10 | 12 V, two fan cables, motor cable | ✅ use the one on the cable side |
| Fixing | 2 × M3 × 12 through the front cover into bosses (Ø 2.5 pilot) at the bay walls; 2 × M3 × 12 from above through the plate into back tabs | | ✅ |
| Contact with the housing | zero overlap (checked by `tools/check.py`) | | ✅ |
| Tie-wrap anchors | 3 on each side, on the back of the fan plate; top and bottom touch the outer fan nut pockets; slot 4.5 × 2 | tie wraps up to 3.6 wide | ✅ |
| SCD40 | not on the unit: on a free cable, out through a cable entry | I²C, about 1–2 m | ✅ place it in the room (near head height), away from the fresh-air jet, the electronics box and the sun; run the bus at 100 kHz or slower, pair SDA and SCL with GND and VCC |

## Open questions

1. Confirm the kit magnet's size when it arrives (6 × 2.5 expected). Nothing needs to change unless it is not 6 mm across.
