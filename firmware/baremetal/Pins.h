// Pin assignment for the Freenove ESP32-S3-WROOM Lite board (FNK0099).
//
// Avoided: strapping pins (0, 3, 45, 46), native USB (19, 20), octal PSRAM (35, 36, 37)
// and the console UART (43 TX, 44 RX, through the board's CH343 USB-UART port).
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

// On-board indicators.
#define PIN_LED         2       // blue LED, used as a heartbeat
#define PIN_RGB         48      // WS2812

// Reserved for the INMP441 microphone (I2S) later: SCK 38, WS 39, SD 40.
