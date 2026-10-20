# Window vent

A demand-controlled window ventilator for one room. Two 80 mm fans move air through a foam window insert: one brings fresh air in, the other exhausts stale air. A single butterfly-damper housing closes both holes with one shaft, turned by a silent stepper motor. An ESP32 reads a CO₂ sensor and runs the fans and the damper.

There is no heat recovery: every litre of air exhausted is lost heat. In exchange it is simple, cheap and automatic. See the estimates below.

> **Status: early prototype, not built.** The geometry is checked in CAD (closed solids, the discs swing freely, the lips stop them). Nothing has been printed or tested yet.

<p align="center">
  <img src="images/assembly.png" alt="Damper housing with two 80 mm fans, stepper motor on top, spigots in the foam insert" width="380">
</p>

## How it works

- **Foam insert.** A block of 2 in (51 mm) XPS foam fills the window gap (100 mm or less, so a child can't fit through). Two 82 mm holes, stacked vertically: intake on top, exhaust below. An insect screen covers the outdoor face.
- **Damper housing.** It sits on the **room** face of the foam, so its moving parts stay warm and dry (no ice). Its two spigots slide into the foam holes and seal with two O-rings each. The housing comes out in spring, and the foam insert stays reusable.
- **Butterfly dampers.** One vertical 5 mm steel shaft runs through both ducts and carries a disc in each. A quarter turn opens or closes both. Each disc closes against two half-ring lips lined with thin foam, one on each side of the shaft. One lip is flat; the other is a 45° cone, and the half of the disc that closes against it (engraved B) has a matching 45° bevel, so neither prints as a flat overhang.
- **Motor and encoder.** A NEMA 17 pancake stepper on top turns the shaft through a flexible coupler. A TMC2209 driver keeps it silent. The motor screws to a separate plate on the bench, and the plate then screws onto a frame on top of the housing from above. An AS5600 magnetic encoder at the bottom reads the absolute shaft angle, so the firmware always knows whether the dampers are really closed, with no homing and no limit switch.
- **Fans.** Two 80 mm PWM fans screw onto the room end of the housing.
- **Electronics box.** A tray under the housing holds a 5 × 7 cm perfboard with the ESP32 and the TMC2209 soldered on. The encoder plate is its lid, and its front wall rises to close the front of the bottom bay. The cables run down the right side (seen from the room), hidden behind the fans and held by three tie-wrap anchors on the back of the fan plate; the same anchors and a cable entry on the left side allow the mirror image. Power comes from two plug-in adapters: a 12 V brick for the fans and the motor, whose wire comes in with the other cables, and a 5 V USB-C adapter for the ESP32, whose cable passes through a diamond opening in the left wall. The [layout drawing](doc/ebox_layout.svg) shows where everything goes on the perfboard.
- **Water stays out of the room.** A 3 mm drip dam across the lower part of each bore, just before the fan, stops droplets from running indoors. Around the bottom shaft hole in each duct, a 16 mm boss rises 3 mm above the floor, so water flows around it instead of down the shaft.
- **How it seals.** The lips do the sealing, not the gap between the disc and the bore: the flat lip is 5.6 mm wide and overlaps the disc edge by 2 mm, and the conical lip meets the disc's bevelled rim over a band about 4 mm wide, with foam tape in between. The disc is 67 mm in a 74 mm bore so it can be slid in edge-on past the dam and the bosses. Around the shaft, where the lips must stop to clear the hub, a boss at the top and the one at the bottom close the gap. Their inner faces are curved, coaxial with the bore, so they follow the disc edge with an even gap of about 0.75 mm.

<p align="center">
  <img src="images/damper_section.png" alt="Top-down section through the upper duct: disc closed against the two half-ring lips, at 45 degrees, and fully open" width="640">
</p>

<p align="center">
  <img src="images/damper_cutaway.png" alt="Cutaway of a closed damper: the disc (orange) sits between two red half-ring lips, one on each side of the shaft and on opposite faces of the disc; the floor boss surrounds the bottom shaft hole" width="480">
</p>

<p align="center">
  <img src="images/damper_closed_view.png" alt="Looking along the duct at the closed disc: curved shaft bosses at the top and bottom follow the disc edge, and the lip behind the disc covers the rest of the gap" width="360">
</p>

<p align="center">
  <img src="images/side_section.png" alt="Side section through the shaft plane: drip dam at the fan end, raised boss around the bottom shaft hole, disc on the shaft, O-ring spigot at the foam end" width="420">
</p>

## Estimates (one sleeper)

| Airflow (each way) | CO₂ in the room | Heat lost at −20 °C outdoors |
|---|---|---|
| 5 L/s (11 CFM) | ~1000 ppm | ~250 W |
| 8 L/s (17 CFM) | ~800 ppm | ~400 W |
| 11 L/s (23 CFM) | ~700 ppm | ~540 W |

At 8 L/s, roughly 10 hours a day over a cold-climate heating season (about 200 days, electricity at 7–11 ¢/kWh), the lost heat costs about $35–45. The fans use about 1 W each.

## Printed parts

| Part | Qty | Description | Size (mm) | Print orientation | <div style="width:180px">Thumbnail</div> |
|---|---|---|---|---|:---:|
| `body` | 1 | Housing: two ducts with the damper lips, drip dams and shaft bosses, O-ring spigots, fan plate, motor frame and encoder plate | 90 × 241 × 114 | Fan plate on the bed, no supports | <img src="images/part_body.png" width="180"> |
| `disc` | 2 | Butterfly damper disc, clamped to the shaft by two M3 grub screws; the half engraved B has a 45° bevel on its rim | 67 × 67 × 14 | Plate on the bed, hub up | <img src="images/part_disc.png" width="180"> |
| `motor_plate` | 1 | The motor screws to it on the bench; it then sits on top of the housing: two screws in front of the motor, and two tabs at the back, down through the frame and screwed to the tower walls | 56 × 61 × 15 | Top face on the bed, tabs up | <img src="images/part_motor_plate.png" width="180"> |
| `magnet_cap` | 1 | Holds the encoder magnet on the bottom end of the shaft; one M3 grub screw, height adjustable ±1 mm | 14 × 14 × 12 | Bore down | <img src="images/part_magnet_cap.png" width="180"> |
| `ebox` | 1 | Electronics box under the housing; its front wall also covers the front of the bottom bay | 80 × 76 × 62 | Floor on the bed | <img src="images/part_ebox.png" width="180"> |

**For a 180 mm printer** (e.g. Bambu Lab A1 mini), print the housing in two halves instead of `body`. The cut runs midway between the two ducts, where only the fan plate joins them; a small splice plate behind the fan plate joins the halves again with four M3 screws, driven from the fan side in the band between the two fans. Each half prints like the full housing, in about half the time (roughly 5–6 h), so they can go on different days; use the same spool and profile for both.

| Part | Qty | Description | Size (mm) | Print orientation | <div style="width:180px">Thumbnail</div> |
|---|---|---|---|---|:---:|
| `body_top` | 1 | Upper half: intake duct, upper fan, motor frame, and both middle tie-wrap anchors (whole) | 90 × 130 × 114 | Fan plate on the bed, no supports | <img src="images/part_body_top.png" width="180"> |
| `body_bottom` | 1 | Lower half: exhaust duct, lower fan, encoder plate; notched under the two middle anchors | 90 × 116 × 114 | Fan plate on the bed, no supports | <img src="images/part_body_bottom.png" width="180"> |
| `splice` | 1 | Joins the halves behind the fan plate; four M3 nut pockets on its back | 60 × 32 × 6 | Flat, nut pockets up | <img src="images/part_splice.png" width="180"> |

<p align="center">
  <img src="images/split_view.png" alt="Exploded view of the split housing: upper and lower halves, the splice plate in the gap between the ducts behind the fan plate, and the four screws in front" width="360">
</p>

**Optional test prints, before the housing.** Print the small real parts first (discs, motor plate, magnet cap, about 1.5–2 h): they test the rod, the grub screws, the motor and the magnet. Then:

| Part | Size (mm) | Time | What it tests |
|---|---|---|---|
| `fittest` | 60 × 34 × 22 | about 20–30 min | The housing's printer-sensitive features, in its print orientation, engraved A to G (see below) |
| `oring_test` | Ø 90 × 18 | about 30 min | One spigot section with an O-ring groove: push it, with an O-ring, into a hole cut in a foam scrap |

<p align="center">
  <img src="images/part_fittest.png" alt="Fit-test coupon with its features engraved A to G" width="420">
</p>

| | Feature | Copied from | Pass if |
|---|---|---|---|
| A | M3 hole + nut pocket | fan plate | the nut drops in and stays; an M3 screw passes freely |
| B | Ø 2.5 self-tapping pilot | box bosses and back pillars | an M3 screw cuts a firm thread without splitting the post |
| C | 5.6 mm ledge with a 45° underside (on the back of the plate) | conical lip B in each bore | the slope is smooth, not drooping or stringy |
| D | Ø 5.4 shaft hole, horizontal | bearing holes in the duct walls | the 5 mm rod turns freely (if not, ream with a 5.5 mm drill) |
| E | AS5600 diagonal slot (3.5 wide) on a 2 mm standoff | encoder plate | an M3 screw passes at both ends of the slot |
| F | M3 hole, horizontal | motor frame | an M3 screw passes freely |
| G | M3 hole with a 90° countersink, opening on the bed | split housing joint (`body_top` and `body_bottom`) | an M3 flat-head screw sits flush or just below the surface |


PETG. No support is needed anywhere: every face that looks down when printing (the lip B seat, the disc bevel, the boss sides, the O-ring grooves, the countersinks) slopes at 45° or less.

### Filament

About **0.4–0.45 kg of PETG** for one unit (less than half a 1 kg spool), or roughly $11–16 at $25–35/kg.

| Part | Qty | Solid volume |
|---|---|---|
| `body` | 1 | 264 cm³ |
| `disc` | 2 | 2 × 14 = 28 cm³ |
| `motor_plate` | 1 | 12.5 cm³ |
| `magnet_cap` | 1 | 1.6 cm³ |
| `ebox` | 1 | 47 cm³ |
| **Total** | | **≈ 353 cm³** |

The split housing (`body_top` 127 cm³, `body_bottom` 136 cm³, `splice` 8 cm³) adds about 7 cm³ (10 g).

- Printed fully solid, 353 cm³ of PETG (1.27 g/cm³) weighs about 448 g.
- Infill hardly matters: almost every wall, plate, lip and disc is 6 mm thick or less, so with 4–6 perimeters the slicer prints it solid anyway. Expect about 400–450 g, plus a little for the skirt or brim and purging.
- The optional test prints add about 30 cm³ (37 g): `fittest` 12 cm³, `oring_test` 18 cm³.
- Print time: very roughly 9–12 hours for the housing on a Bambu Lab P1 (0.2 mm layers; about 7–9 hours at 0.28 mm), and about 3–4 hours for all the other parts together. The slicer gives the exact figures.

## Hardware

Prices: Amazon.ca, October 2026, before taxes. Packs of two leave a spare.

| Item | Qty | Notes | Price (CAD) |
|---|---|---|---|
| 80 mm PWM fan, ≥ 2 mm H₂O static pressure | 2 | Noctua NF-A8 PWM (2.37 mm H₂O, 17.7 dB(A) max). Run at 30–60% | 2 × $24.95 |
| Stepper motor, NEMA 17 pancake | 1 | StepperOnline 17HS08-1004S (42 × 42 × 20 mm, 5 mm shaft, 13 N·cm). Any NEMA 17 fits the mount | $26.50 |
| TMC2209 stepper driver | 1 | StealthChop for silent moves; UART for StallGuard | $16.99 (pack of 2) |
| AS5600 magnetic encoder board + **diametric** magnet | 1 | Sold with the magnet (the kit: 23.3 × 22.8 mm board, 3.95 × 2 mm magnet). A 20 × 20 board with 15 mm hole spacing also fits: 4 × M3 × 12 + nuts onto standoff pads on the bottom plate. See the magnet note below | $12.69 (pack of 2) |
| ESP32-S3 dev board | 1 | Freenove ESP32-S3-WROOM Lite (FNK0099), the board the firmware's pinout is written for; other ESP32-S3-WROOM-1 boards work with a pin check. Flash it over USB on the bench; the final firmware updates over Wi-Fi | — |
| CO₂ sensor, NDIR | 1 | Sensirion SCD40 module (CO₂ + temperature + humidity, I²C). Not CCS811/SGP30 ("eCO₂" estimates) | $37.45 |
| Steel rod, 5 mm × 200 mm | 1 | Damper shaft. 200 mm fits as is, no cutting. If it is HSS (very hard), grind a small flat with a rotary tool where each disc and the coupler clamp, so the screws can't slip | $12.79 (pack of 2) |
| Flexible shaft coupler, 5–5 mm, 19 × 25 mm | 1 | | $13.49 (pack of 2) |
| M3 × 35 screws + M3 nuts | 8 each | Fans | — |
| M3 × 8 screws | 4 | Motor to motor plate | — |
| M3 × 10 (or M3 × 12) screws + M3 nuts | 4 each | Motor plate: two through the frame in front of the motor, two through the tower walls and the plate's back tabs | — |
| M3 grub screws, 6 or 8 mm | 5 | Two per disc, 24 mm apart along the hub, so the disc can't rock on the shaft; one in the magnet cap. Self-tapping into the plastic | — |
| O-rings, 74 × 3 mm, nitrile 70A | 4 | Two per spigot (grooves sized for this O-ring: 4.7% stretch, about 23% squeeze in an 82 mm hole). Optional at first: the spigots also fit a snug hole | $12.79 (pack of 10) |
| Closed-cell neoprene foam sheet, self-adhesive, 1/16 in (1.6 mm) | 1 | Lip seals, cut with the [templates](#cutting-the-lip-foam). The model leaves a 1 mm gap, so the foam is squeezed about 37 %, a good range for a seal | |
| Perfboard (protoboard), 5 × 7 cm, holes 66 × 46 mm | 1 | Carrier for the ESP32 and the TMC2209 in the electronics box | |
| Resistors and capacitor for the perfboard | | 1 kΩ (TMC2209 UART), 10 kΩ × 5 (driver enable pull-up, two fan PWM pull-downs, two tach pull-ups), 100 kΩ + 22 kΩ (12 V sense), 100 µF ≥ 25 V electrolytic (TMC2209 motor supply). See [firmware/README.md](firmware/README.md) | — |
| Female pin headers, 2.54 mm (optional) | to suit | Sockets for the ESP32 and the TMC2209 instead of soldering them, so they unplug for replacement (`esp_mount`, `tmc_mount`; the box has room for both) | |
| M2 screws, about 6 mm | 4 | Perfboard onto the box standoffs (self-tapping) | |
| M3 × 12 countersunk (flat head, ISO 10642 or DIN 965) screws + M3 nuts | 4 each | Split housing only: fan plate to the splice, heads flush in 90° countersinks | — |
| M3 × 12 screws | 4 | Electronics box: two through the front cover, two from above through the encoder plate (self-tapping) | — |
| Small tie wraps, 2.5–3.6 mm | 3+ | Cable anchors (three on each side; use one side) | |
| 12 V power brick | 1 | Fans and motor, about 1 A. Only its wire enters the box, to a 2-pin screw terminal on the perfboard | — |
| USB-C power adapter, 5 V (1 A or more), and a USB-C cable | 1 | Powers the ESP32 through its USB-UART connector, which also gives the console. The cable passes through a diamond opening in the box's left or right wall (`usb_port`: or only a cross to drill, or nothing; `usb_side`: left, right or both) | — |
| **Total bought** | | Not counting the foam insert and foam sheet, or the two power adapters | **≈ $181** |

### The AS5600 board

The kit board, measured. Its four mounting holes form a 16.7 × 16.2 mm rectangle (not a square); the diagonal slots in the encoder plate take it as well as the smaller 20 × 20 boards. Mount it chip up, under the magnet, and solder the wires straight into its holes: they run inward under the board, in the 2 mm the standoff pads leave, and down through the diamond window under the chip.

<p align="center">
  <img src="doc/as5600.svg" alt="AS5600 kit board, dimensioned: 23.3 x 22.8 mm, four 3.6 mm holes 3.3 mm from the edges, a 3-pin row (VCC, OUT, GND) and a 4-pin row (DIR, SCL, SDA, GPO) 5.2 mm from the sides, chip in the middle; 1.6 mm board, 3.22 mm over the chip" width="520">
</p>

### The ESP32-S3 board

The Freenove ESP32-S3-WROOM Lite, measured. Its two pin rows are 25.3 mm apart, so they land 10 holes apart on the perfboard. It has two USB-C connectors at one end: plug the cable into the USB-UART one (power and console). The module's antenna sticks out 7 mm beyond the other end.

<p align="center">
  <img src="doc/esp32_s3.svg" alt="Freenove ESP32-S3-WROOM Lite, dimensioned: PCB 50 x 28.5 mm, antenna 7 mm beyond it over the middle 18.5 mm, two rows of 20 pins 25.3 mm apart, USB-OTG and USB-UART connectors 9 mm wide at the USB end; side view: 1.62 mm PCB on a 2.78 mm pin spacer, 5.54 mm pins, 4.85 mm to the top of the tallest part" width="640">
</p>

### The TMC2209 module

A StepStick-format driver: 21 × 15 mm, two rows of 8 pins 12.7 mm apart (5 holes on the perfboard). The chip is on the underside; its heatsink (15 × 14.5 × 13 mm, fins along the pin rows) sticks onto the thermal pad on top. The side-view heights are assumed equal to the ESP32's until measured on the part.

<p align="center">
  <img src="doc/tmc2209.svg" alt="TMC2209 module, dimensioned: PCB 15 x 21 mm, two rows of 8 pins 12.7 mm apart (EN, MS1, MS2, PDN, UART, CLK, STEP, DIR; VM, GND, M1B, M1A, M2A, M2B, VIO, GND), heatsink 14.5 x 15 mm outline; side view: 1.62 mm PCB on a 2.78 mm spacer, 5.54 mm pins, 13 mm heatsink" width="640">
</p>

### The electronics box layout

The box seen from above, to scale, with the room at the bottom. The ESP32 lies across the back half, its USB end three holes in from the left wall so its pins clear the corner standoff; the TMC2209 sits at the front right, next to the 12 V terminal and the cable entry. The ESP32 can also be turned 180° in the same place, USB end toward the right wall: the box has a diamond opening on each side (views `ebox_elec` and `ebox_elec_alt` in the model). Keep wires and copper away from the antenna's end.

<p align="center">
  <img src="doc/ebox_layout.svg" alt="Electronics box from above, to scale: the perfboard on four standoffs; the ESP32 across the back half, its USB-C plug through a diamond in the left wall; the TMC2209, 12 V terminal and capacitor at the front right by the cable entry; fan, motor and sensor connectors and resistors at the front left; a second diamond in the right wall for the ESP32 turned the other way" width="640">
</p>

### The encoder magnet

The AS5600 measures the direction of the magnetic field across the shaft, so the magnet's north-south axis must lie **across** the shaft and turn with it.

- A **diametric** magnet (magnetized across its diameter) does this lying flat on the shaft end. AS5600 boards are usually sold with one: this kit's measures 3.95 × 2 mm, others 6 × 2.5 or 6 × 3 mm. This is the default (`magnet = "diametric"`, `magnet_d = 4`, `magnet_h = 2`); set them to the one you have.
- An ordinary small cylinder magnet is usually **axial** (poles on its flat ends). Lying flat it would not work, but lying on its side it does: set `magnet = "sideways"` for a cap that holds a 2 × 2 mm cylinder across the shaft. A magnet that small may be too weak at 1–2 mm; the AS5600's status register reports "too weak / OK / too strong", so check it once.
- Without any magnet, the TMC2209's StallGuard can find "closed" by sensing the stall against the lips.

### Cutting the lip foam

Full-size templates for the foam on the four lips (two per duct). The flat lip takes a half-ring; the conical lip takes the cone unrolled, a flatter arc that lies on the 45° slope without wrinkles. Print the [PDF](doc/lip_templates.pdf) at 100 % (Actual size, not Fit to page), check its 100 mm and 50 mm bars with a ruler, then trace the shapes on the foam's backing paper and cut.

<p align="center">
  <a href="doc/lip_templates.pdf"><img src="images/lip_templates.png" alt="Preview of the lip templates page: two half-rings for the flat lips, two unrolled arcs for the conical lips, and 100 mm and 50 mm scale bars" width="300"></a>
</p>

If the 1.6 mm foam proves too stiff for the disc to close, setting `gasket = 1.6` moves the lips back to suit it (checked: the disc still swings freely and the lips still stop it).

## Assembly

0. Split housing only: press four M3 nuts into the splice's pockets. Stand the lower half upright, cut face up, hold the splice against the back of its fan plate, just above the duct, and fit the two lower countersunk M3 × 12 from the fan side. Lower the upper half onto it and fit the other two. Leave all four slightly loose until step 3.
1. Line the lips inside the ducts with foam cut from the [templates](#cutting-the-lip-foam): a half-ring on each flat lip, an unrolled arc on each conical lip (B).
2. Slide each disc edge-on into its duct from the fan end, hub toward the room, with the half engraved B on the side of the conical lip (the right side, seen from the room).
3. Push the shaft down through the frame on top, both ducts and both disc hubs. Split housing: the shaft now lines up the two halves; tighten the four splice screws.
4. Turn both discs closed against the lips and tighten their grub screws (two per disc) through the duct openings.
5. Screw the AS5600 board onto the four standoff pads, chip up, with its wires soldered into its holes and led inward under the board, then down through the diamond window under the chip. Glue the magnet into the cap and slide the cap onto the shaft's bottom end. Lay a 1 mm shim on the chip (a plastic card works), slide the cap down until the magnet rests on it, tighten the cap's grub screw, and remove the shim.
6. On the bench, screw the motor to the motor plate (4 × M3 × 8 from below) and fit the coupler on the motor shaft.
7. Lower the motor and plate onto the top of the housing, with the coupler through the big diamond and over the shaft end, and the plate's two back tabs down through the slots in the frame. In front of the motor, put an M3 × 10 down through the plate and the frame, with a nut underneath, reached from the tower's open front above the fan plate. At the back, put an M3 × 10 through each tower wall and its tab from outside, with a nut on the inside, reached from the tower's open back. Then tighten the coupler's lower screw through a side window.
8. Fit the fans: the top one blowing into the room, the bottom one blowing toward the window. Arrows engraved on both sides of the housing (above the upper duct and below the lower one) show each duct's airflow; match the arrows on the fan frames to them.
9. Electronics: solder the ESP32 and the TMC2209 onto the perfboard (or into female headers), following the [layout](#the-electronics-box-layout): the ESP32 across the back half with its USB end three holes in from the left wall (clear of the corner standoff), the TMC2209 at the front right. Or turn the ESP32 180° in the same place, its USB end toward the right wall (view `ebox_elec_alt`): the box has a diamond on each side. Wire it (connect the 12 V brick's GND to the ESP32's GND), and screw it onto the four standoffs in the box (M2). Plug the USB-C cable in through the matching side wall. Bring the 12 V wire and the fan and motor cables down the right side, tie them to the three anchors behind the fans, and into the box through the notch at the top of its right wall. The AS5600 wires drop in through the window in the encoder plate.
10. Fit the box under the housing: two M3 × 12 through the front cover into the bosses of the bottom bay, and two from above through the encoder plate (outside the bay walls) into the box's back tabs.
11. Roll two O-rings onto each spigot and push the housing into the foam holes.

## Optional: adjustable louvers for the intake fan

In winter the incoming air is cold, and a jet straight off the fan can feel like a draft. These louvers clip onto the room face of the intake fan and aim the air: upward along the ceiling, for example, so it mixes with the room air before it reaches anyone.

<p align="center">
  <img src="images/louvers.png" alt="Louvers: a frame with six horizontal blades, joined by a link bar on one side, two clips on top and bottom" width="380">
</p>

- **Clips, no screws.** Four hooks reach back over the fan's corner flanges and catch behind them. Recesses in the frame's corners fit over the fan's screw heads, so the fan keeps its normal screws. A firm pull takes the louvers off.
- **The blades turn together.** Each of the six blades pivots on pins in U-slots in the side walls. On one side, a link bar joins an offset pin on every blade, so turning any blade turns them all, from −45° to +45°.
- **They hold their angle.** The pins fit snugly in their slots, and a strip of felt or foam tape on the link bar rubs on the side wall. The strip also damps vibration. On the other side, a collar on each blade's pivot bears on the wall.
- **Nothing falls out.** The slots open toward the fan, so the blades drop in from behind. A retaining comb in each side wall then plugs the slots behind the pins.

| Part | Qty | Size (mm) | Print orientation | |
|---|---|---|---|---|
| `louver_chassis` | 1 | 80 × 86 × 36 | Front face on the bed, clips up | <img src="images/part_louver_chassis.png" width="180"> |
| `louver_blade` | 6 | 79 × 14 × 3.5 | Flat; its pins are flattened on the bed side | <img src="images/part_louver_blade.png" width="180"> |
| `louver_link` | 1 | 53 × 5 × 2.4 | Flat, holes up | <img src="images/part_louver_link.png" width="180"> |
| `louver_retainer` | 2 | 3 × 57 × 7.7 | Spine down, pegs up | <img src="images/part_louver_retainer.png" width="180"> |

About 34 cm³ (45 g) of PETG in all. Also needed: a strip of 1 mm felt or foam tape, about 5 × 52 mm, for the link bar.

**Assembly:**
1. Stick the felt strip on the link bar's flat face (the face without holes).
2. Push the link onto the six blades' offset pins.
3. Slide the blades into the U-slots from the back of the frame: the link and its strip go on the side with the link pins, the collars on the other.
4. Press a retaining comb into the back of each side wall.
5. Clip the frame onto the intake fan.

**Tuning after a test print**, in `cad/louvers.scad`:
- **`slot_w`:** the grip of the pins in their slots. Lower makes the blades stiffer.
- **`clip_lip`, `clip_edge` and `clip_w`:** the clips. They're sized for the Noctua NF-A8 (a 7 mm corner flange, with the clips 8 mm in from the side edges so they clear the corner screws).
- **`pad_t` and `pad_sq`:** the friction strip and how much it's squeezed.


## Files

```
doc/                   reference drawings: the AS5600, ESP32-S3 and TMC2209 boards, the electronics box layout;
                       the lip foam templates (PDF, to print at 100 %)
images/                renders used in this README
cad/window_vent.scad   parametric model (Customizer; part = "assembly" for the preview)
cad/louvers.scad       optional adjustable louvers for the intake fan
stl/                   exported parts (default parameters)
tools/check.py         geometry checks (must print ALL CHECKS PASSED)
tools/wiring_svg.py    draws firmware/images/wiring.svg (the wiring diagram)
tools/as5600_svg.py    draws doc/as5600.svg (the AS5600 board, dimensioned)
tools/ebox_layout_svg.py draws doc/ebox_layout.svg (the electronics box, to scale)
tools/esp32_svg.py     draws doc/esp32_s3.svg (the ESP32-S3 board, dimensioned)
tools/tmc2209_svg.py   draws doc/tmc2209.svg (the TMC2209 module, dimensioned)
tools/lip_templates_svg.py draws doc/lip_templates.svg and .pdf (full-size foam templates) and their preview
tools/render_images.py regenerates the images in images/ from the models
firmware/baremetal/    Arduino sketch: serial commands to test each electronic part (not tested on hardware yet; see firmware/README.md)
PRINT_CHECKLIST.md     every printed/bought part interface to verify before printing
```

## License

Copyright (c) 2026 Marc-Antoine Massicotte.

This design (CAD model, STL files, images, documentation and scripts) is released under the [CERN Open Hardware Licence Version 2 - Permissive](LICENSE) (CERN-OHL-P-2.0). You may use, modify, make, share and sell it freely, as long as you keep this notice. It comes with no warranty of any kind, and the author accepts no liability for its use.

The firmware in [`firmware/`](firmware) is software, so it is released under the [MIT License](firmware/LICENSE) instead: same idea, free to use, modify and share, keep the notice, no warranty.
