// Trinamic TMC2209 stepper driver over its single-wire UART (8-byte write datagrams, 4-byte read requests).
#pragma once
#include <Arduino.h>

// Registers
#define TMC_GCONF      0x00
#define TMC_GSTAT      0x01
#define TMC_IFCNT      0x02
#define TMC_IOIN       0x06
#define TMC_IHOLD_IRUN 0x10
#define TMC_TPOWERDOWN 0x11
#define TMC_TSTEP      0x12
#define TMC_TPWMTHRS   0x13
#define TMC_TCOOLTHRS  0x14
#define TMC_VACTUAL    0x22
#define TMC_SGTHRS     0x40
#define TMC_SG_RESULT  0x41
#define TMC_COOLCONF   0x42
#define TMC_MSCNT      0x6a
#define TMC_CHOPCONF   0x6c
#define TMC_DRV_STATUS 0x6f
#define TMC_PWMCONF    0x70

void Tmc2209Begin(HardwareSerial* uart, uint8_t addr, float rsense);
bool Tmc2209Read(uint8_t reg, uint32_t* value);
bool Tmc2209Write(uint8_t reg, uint32_t value);

// Configuration done by the firmware at boot: UART control, StealthChop, microsteps from CHOPCONF.
bool Tmc2209Init(int microsteps, int runMilliAmps, int holdPercent);
bool Tmc2209SetMicrosteps(int microsteps);     // 1, 2, 4 ... 256
int  Tmc2209GetMicrosteps();
bool Tmc2209SetCurrent(int runMilliAmps, int holdPercent);
int  Tmc2209GetCurrent();                      // run current actually set, mA
bool Tmc2209SetVelocity(long microstepsPerSecond);  // internal step generator (VACTUAL), 0 = use STEP pin
