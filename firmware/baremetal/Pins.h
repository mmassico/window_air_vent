// Pin assignment for the Freenove ESP32-S3-WROOM Lite board (FNK0099).
//
// Avoided: strapping pins (0, 3, 45, 46; 3 only carries the microphone in audio mode), native USB (19, 20),
// octal PSRAM (35, 36, 37) and the console UART (43 TX, 44 RX, through the board's CH343 USB-UART port).
#pragma once

// Console: UART0 on GPIO 43/44 (the USB-UART connector, "onboard code uploader"), 115200 baud.
#define CONSOLE_BAUD    115200

// I2C bus 0: SCD40 CO2 sensor, on a 1-2 m cable, so kept slow.
#define PIN_SCD_SDA     8
#define PIN_SCD_SCL     9
#define SCD_I2C_HZ      100000

// I2C bus 1: AS5600 encoder, local, on its own bus so a sensor cable fault cannot block it.
#define PIN_ENC_SDA     6
#define PIN_ENC_SCL     7
#define ENC_I2C_HZ      400000

// TMC2209 stepper driver.
//   EN is active low; a 10 k pull-up to 3.3 V keeps the motor off until the firmware enables it.
//   UART is single-wire: 1 k from TX to PDN_UART, RX straight to PDN_UART. MS1 = MS2 = GND (address 0).
#define PIN_TMC_EN      10
#define PIN_TMC_STEP    11
#define PIN_TMC_DIR     12
#define PIN_TMC_DIAG    13
#define PIN_TMC_TX      17
#define PIN_TMC_RX      18
#define TMC_UART_BAUD   115200
#define TMC_ADDR        0
#define TMC_RSENSE      0.11f   // ohms, the usual value on StepStick-style modules

// 80 mm 4-wire PWM fans (index 0 = intake, 1 = exhaust).
//   PWM: 25 kHz, 10 k pull-down so the fans stay slow while the ESP32 boots.
//   Tach: open collector, 2 pulses per turn, 10 k pull-up to 3.3 V.
#define PIN_FAN0_PWM    4
#define PIN_FAN1_PWM    5
#define PIN_FAN0_TACH   15
#define PIN_FAN1_TACH   16
#define FAN_PWM_HZ      25000
#define FAN_PWM_INVERT  0       // set to 1 if the PWM line goes through an inverting transistor

// 12 V supply sense: 100 k (top) / 22 k (bottom) divider into an ADC1 pin (ADC2 is unusable with WiFi).
#define PIN_12V_SENSE   1
#define V12_DIV_TOP     100.0f
#define V12_DIV_BOTTOM  22.0f

// DS18B20 temperature sensors (1-Wire), one per pin so each is known by its pin. Three wires each (no parasite
// power), 4.7 k pull-up to 3.3 V per pin at the ESP32 end. Read with the 'temp' command (Ds18b20.cpp).
#define PIN_TEMP_OUT    14      // outdoor: waterproof probe through the foam insert, near the intake, in the shade
#define PIN_TEMP_IN     21      // indoor, optional (the SCD40 also reads room temperature): on an inside wall at
                                // about 1.2-1.5 m, away from the window and heaters; not in audio mode (below)

// Audio mode (optional): an analog microphone module (MAX9814: 3V3, OUT, GND) on the indoor DS18B20's header (J7)
// instead of the probe, to measure the outdoor sound level. That header's line is GPIO 21, which has no ADC, so a wire
// on the PCB joins GPIO 21 to GPIO 3 (ADC1 channel 2, the only free ADC1 pin). GPIO 3 is a strapping pin, but only for
// the JTAG source, and only if an eFuse says so: the mic's bias at reset is harmless. Leave out J7's 4.7 k pull-up
// (R9): it would pull the mic's output toward 3.3 V. The firmware leaves GPIO 21 disconnected (input off, no pulls),
// and the indoor DS18B20 is unavailable. 1 = audio mode, 0 = indoor DS18B20 on GPIO 21.
#ifndef AUDIO_MODE                      // (or -DAUDIO_MODE=1 on the compiler's command line)
#define AUDIO_MODE      0
#endif
#define PIN_MIC         3
#define PIN_MIC_LINK    21      // wired to PIN_MIC, kept high impedance
#define MIC_CAL_DB      0.0f    // dB SPL = dBFS + this ('sound cal' measures it); 0 = uncalibrated, levels in dBFS

// On-board indicators.
#define PIN_LED         2       // blue LED, used as a heartbeat
#define PIN_RGB         48      // WS2812

// Reserved for the INMP441 microphone (I2S) later: SCK 38, WS 39, SD 40.
