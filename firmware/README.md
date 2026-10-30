# Firmware

> **Not tested on hardware yet.** The bare-metal sketch compiles without warnings (Arduino core esp32 3.3.12), but it has not run on a board or with any of the parts. The pin assignment, the wiring table and the driver code may still change after the first bench tests.

Two stages:

1. **`baremetal/`** (this stage): a serial command console to check every electronic part on its own, with no Wi-Fi and no control logic.
2. **The standalone application** (planned): CO₂ control running on the ESP32, with a web page served by the ESP32 itself on the home network (LAN) for status, settings and manual control.

## Board and tools

- **Board:** Freenove ESP32-S3-WROOM Lite (FNK0099): 16 MB flash, 8 MB octal PSRAM, and two USB-C connectors: **USB-UART** (the onboard code uploader, a CH343 USB-serial chip wired to the ESP32's UART0) and **USB-OTG** (the ESP32-S3's own USB, host or device). Dimensions and pinout: [doc/esp32_s3.svg](../doc/esp32_s3.svg).
- **Software:** Arduino IDE 2.x with the **esp32 by Espressif Systems** core, version 3.x (tested to compile with 3.3.12).
- **Library:** the project's own `WindowVent` (in `libs/`): the pin map and the drivers. In the Arduino IDE, copy `libs/WindowVent` into the `libraries` folder of the sketchbook (Documents > Arduino > libraries on Windows), or link it there, so the IDE finds it.
- **Arduino IDE settings (Tools menu):**

| Setting | Value |
|---|---|
| Board | ESP32S3 Dev Module |
| USB CDC On Boot | Disabled: the console (`Serial`) then goes through the USB-UART connector. Enabled would move it to the USB-OTG connector |
| Flash Size | 16MB (128Mb) |
| Partition Scheme | 16M Flash (3MB APP/9.9MB FATFS) |
| PSRAM | OPI PSRAM |
| Upload Mode | UART0 / Hardware CDC |

Plug the cable into the **USB-UART** connector (silkscreen: onboard code uploader); it is used both to flash and for the console. Windows lists it as "USB-SERIAL CH343 (COMx)" under "Ports (COM & LPT)"; if it doesn't appear, install the CH343 driver from Freenove's package. Leave the TX/RX header pins (GPIO 43/44) unconnected. For the console, use the Serial Monitor at 115200 baud, or a terminal such as PuTTY; the up and down arrows then recall earlier commands.

The same build from the command line, run from the `firmware` folder (`--libraries libs` points arduino-cli at the shared library):

```
arduino-cli compile --fqbn "esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB" --libraries libs baremetal
```

## Wiring

Every pin is defined in [`libs/WindowVent/src/Pins.h`](libs/WindowVent/src/Pins.h). "3V3" and "GND" are the ESP32 board's pins. Every ground is common.

<img src="images/wiring.svg" alt="Wiring diagram: SCD40, AS5600, 12 V sense divider and both fans on the left of the ESP32-S3, TMC2209, stepper, two DS18B20 temperature sensors and the optional MAX9814 microphone (audio mode, with its GPIO 21 to GPIO 3 wire) on the right, 12 V brick and 5 V USB-C adapter on top" width="100%">

The table below gives the same connections, pin by pin.

| Part | Pin | Goes to | Extra parts |
|---|---|---|---|
| **SCD40** (CO₂) | VDD, GND | 3V3, GND | |
| | SDA, SCL | GPIO 8, GPIO 9 (I²C bus 0, 100 kHz) | Most modules have pull-ups; on a 1–2 m cable, 4.7 kΩ to 3V3 at the ESP32 end helps |
| **AS5600** (encoder) | VCC, GND | 3V3, GND | |
| | SDA, SCL | GPIO 6, GPIO 7 (I²C bus 1, 400 kHz) | Pull-ups are on the module |
| | DIR | GND (sets the counting direction) | |
| **TMC2209** | VM, GND | 12 V, GND | 100 µF ≥ 25 V across VM–GND, close to the module |
| | VIO | 3V3 | |
| | EN | GPIO 10 | 10 kΩ to 3V3: the motor stays off while the ESP32 boots |
| | STEP, DIR | GPIO 11, GPIO 12 | |
| | DIAG | GPIO 13 | |
| | PDN_UART | GPIO 18 directly, and GPIO 17 through 1 kΩ | Single-wire UART |
| | MS1, MS2 | GND | UART address 0 |
| | A1 A2 B1 B2 | Motor coils | Never plug or unplug the motor with 12 V on |
| **Fan 0, intake** (Noctua: black GND, yellow 12 V, green tach, blue PWM) | PWM | GPIO 4 | 10 kΩ to GND: the fan stays slow while the ESP32 boots |
| | Tach | GPIO 15 | 10 kΩ to 3V3 |
| **Fan 1, exhaust** | PWM | GPIO 5 | 10 kΩ to GND |
| | Tach | GPIO 16 | 10 kΩ to 3V3 |
| **12 V sense** | | GPIO 1 | 100 kΩ from 12 V to GPIO 1, 22 kΩ from GPIO 1 to GND |
| **DS18B20, outdoor** (waterproof probe through the foam insert) | VDD, GND | 3V3, GND | Three wires, no parasite power |
| | DQ | GPIO 14 | 4.7 kΩ to 3V3 |
| **DS18B20, indoor** (optional: the SCD40 also reads the room's temperature) | VDD, GND | 3V3, GND | |
| | DQ | GPIO 21 | 4.7 kΩ to 3V3 |
| **Microphone, audio mode** (optional, instead of the indoor DS18B20: a MAX9814 module) | VDD, GND | 3V3, GND | On the indoor probe's header |
| | OUT | GPIO 21, wired to GPIO 3 | No pull-up: leave the indoor probe's 4.7 kΩ out |

- **On the board itself:** the blue LED (GPIO 2) blinks as a heartbeat, and the RGB LED is on GPIO 48 (`led` command).
- **Temperature sensors:** read with the `temp` command; the sketch drives the 1-Wire bus itself (`Ds18b20.cpp`), so no library is needed. The outdoor probe goes near the intake, away from the exhaust outlet and out of the sun.
- **Audio mode (optional):** an analog microphone measures the outdoor sound level, for instance to close the damper when it's too loud outside. It takes the indoor DS18B20's header, so it replaces that probe. That header's line, GPIO 21, has no ADC, so GPIO 21 is joined to GPIO 3, the only free pin on ADC1: bridge the solder jumper JP2 on the back of the PCB (v1.1), or solder a short wire on a v1.0 PCB or the perfboard. ADC2 can't be used while Wi-Fi runs. Leave out that header's 4.7 kΩ pull-up: it would pull the microphone's output toward 3.3 V. Then set `AUDIO_MODE` to 1 in `Pins.h`. The firmware leaves GPIO 21 disconnected (input off, no pull-up or pull-down), reads the microphone on GPIO 3, and drops the indoor probe. GPIO 3 is a strapping pin, but only for the JTAG source, and only when an eFuse selects it, so the microphone's bias at reset does no harm. The MAX9814's output rests at about 1.25 V and swings up to 2 V peak to peak, inside the ADC's 0–3.1 V range. Tie its GAIN pin to VDD (40 dB) and leave A/R open. Its automatic gain control (AGC) holds loud sounds near a fixed output level, so a sound 10 dB louder may read only 1 or 2 dB higher. At 40 dB gain, it stays out of the way up to about 94 dB SPL, which covers outdoor noise (60 to 90 dB SPL); the readings stay linear and the `sound cal` offset holds. At 50 or 60 dB (GAIN to GND, or open), the AGC already acts from about 84 or 74 dB SPL.
- **Kept free for later:** GPIO 38, 39, 40, for the INMP441 microphone (I²S).
- **Power:** two adapters. A 12 V brick feeds VM, the fans and the 12 V sense; a 5 V USB-C adapter powers the ESP32 through its USB-UART connector (the board makes the 3V3 for the sensors and the TMC2209 logic). Join the brick's GND and the ESP32's GND on the perfboard. The [layout drawing](../doc/ebox_layout.svg) shows where the parts go in the box.
- **Driving the fan PWM directly:** the 3.3 V PWM output drives the Noctua PWM input as is (Noctua accepts a 3.3 V signal). If you ever add an inverting transistor, set `FAN_PWM_INVERT` to 1.

## Bring-up, one part at a time

Each step only needs the parts before it. Each line shows a command, then what you should see.

1. **ESP32 alone, on USB.**
   - Flash the sketch, open the console, and type `info`: the chip, 16 MB of flash and 8 MB of PSRAM should be listed.
   - `led 0 0 40`: the RGB LED turns blue.
2. **Encoder.**
   - `i2c scan 1` shows `0x36`.
   - `enc` gives the angle, with the magnet status "OK" and an AGC around mid-range (about 60–200).
   - Turn the shaft by hand: the angle follows.
   - "Too weak" means the magnet is too far away; "too strong" means it's too close.
3. **CO₂ sensor.**
   - `i2c scan 0` shows `0x62`, and `co2 serial` prints a number.
   - `co2 start`, wait 5 s, then `co2`: about 400–1000 ppm indoors, with the room's temperature and humidity. Breathe near it and the next reading jumps up.
   - The NDIR cell reads a little high in its first hours. `co2 frc 420` sets it against outdoor air: run `co2 start` outside for 3 minutes, then `co2 stop` and `co2 frc 420`.
4. **12 V on.**
   - `info`: Supply ≈ 12 V.
   - `fan all 30`, then `fan` a few seconds later: both fans report a speed.
   - Try `fan 0 100` and `fan 1 0`. The NF-A8 doesn't stop at 0%; it runs at its minimum speed.
5. **Driver and motor.**
   - `tmc init`, then `tmc status`: version `0x21`, and IFCNT goes up by one after each `tmc wr` or `mot cur` command. That proves both directions of the UART work.
   - `mot en 1`, then `mot step 800`: a quarter turn at the default 16 microsteps. The report compares the expected angle with the encoder's. If their signs are opposite, the firmware will simply flip one of them.
   - `mot step -800` comes back.
   - `mot vel 1000` turns continuously with the driver's own step generator. Run `mon`, slow the shaft with your fingers, and watch SG drop. `mot vel 0` stops it.
   - When the damper is fitted, the same test against the lips gives the StallGuard number for "closed".
6. **Temperature probes.**
   - `info` lists each DS18B20 as "answers" or "absent" (the indoor one is optional).
   - `temp`: both temperatures after a 0.75 s conversion. Warm the probe in your hand and the next reading rises.
   - `temp rom`: each probe's ROM code; family `28` is a genuine DS18B20 type.
   - "absent" means no presence pulse: check the three wires and the 4.7 kΩ pull-up. "CRC error" usually means a weak or missing pull-up, or a long cable.
7. **Microphone (audio mode only).**
   - `info`: the microphone's DC level is about 1250 mV with a MAX9814. Near 0 or 3300 mV means no bias: check its power and the GPIO 21 to GPIO 3 wire.
   - `sound`: one 0.25 s reading. It gives the level in dBFS (0 dB is a sine filling the ADC's whole range), the DC bias, the peak-to-peak swing and the achieved sample rate (8000 samples/s aimed). Clap: the level jumps.
   - "CLIPPING" means the signal reaches the ADC's limits. The MAX9814's AGC caps its output at about 2 V peak to peak, so it shouldn't happen; if it does, check that GAIN is tied to VDD and that the DC level is near 1250 mV.
   - `sound mon` prints the level every 0.5 s, with a 10 s average, the loudest so far and a bar graph.
   - To read dB SPL instead of dBFS, play a steady noise, read it on a phone sound meter app, and type `sound cal <dB>` with that value. The offset lasts until a reboot; to keep it, copy the printed value into `MIC_CAL_DB` in `Pins.h`.
   - The level is measured in short bursts of one-shot reads, after a 150 Hz high-pass filter that cuts wind rumble and the fans' hum. The 12 V sense also reads ADC1 one-shot, and the core's continuous (DMA) mode can't share a unit with it. For a sound level, that's enough.
8. **Everything at once.** `mon 1000` prints one line per second with every reading, until a key is pressed. In audio mode, the indoor temperature's place shows the sound level.

Note any number that looks wrong: the magnet status, the AGC, the SG values while turning freely and against the lips, and the fan speeds at 30% and 100%. They become the settings of the final firmware.

## Command list

Type `help` on the console for the full list. In brief:

| Group | Commands |
|---|---|
| General | `help`, `cls`, `info`, `reboot`, `led <r> <g> <b>`, `mon [ms]` |
| I²C | `i2c scan <bus>`, `i2c rd <bus> <addr> <reg> [n]`, `i2c wr <bus> <addr> <reg> <data>...` |
| CO₂ | `co2 start`, `co2 stop`, `co2`, `co2 serial`, `co2 selftest`, `co2 frc <ppm>` |
| Encoder | `enc`, `enc zero` |
| Motor | `mot en <0\|1>`, `mot step <n> [speed]`, `mot vel <speed>`, `mot cur <mA> [hold%]`, `mot ustep <n>`, `mot sgt <n>` |
| Driver registers | `tmc init`, `tmc status`, `tmc rd <reg>`, `tmc wr <reg> <value>` |
| Fans | `fan`, `fan <0\|1\|all> <duty%>` |
| Temperature | `temp`, `temp rom` |
| Sound (audio mode) | `sound`, `sound mon [ms]`, `sound cal <dB>` |

Numbers can be written as `42`, `0x2A`, `2Ah`, `0b101010` or `101010b`. A long move or `mon` stops when any key is pressed.

## Defaults

The settings applied at boot are in `baremetal.ino`:
- 16 microsteps (interpolated to 256 by the driver);
- 500 mA run current, with 50% hold current;
- StealthChop;
- 800 microsteps/s, which is a quarter turn per second.

The current calculation assumes 0.11 Ω sense resistors (`TMC_RSENSE` in `Pins.h`), the usual value on StepStick-style modules.

## License

The firmware is released under the [MIT License](LICENSE).
