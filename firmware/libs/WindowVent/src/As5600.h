// AMS AS5600 12-bit magnetic angle encoder (I2C address 0x36). Read-only use: nothing is burned to OTP.
#pragma once
#include <Wire.h>

#define AS5600_ADDR 0x36

struct As5600Reading
{
    uint16_t raw;           // 0..4095, unscaled
    uint8_t  status;        // bit 5 MD magnet detected, bit 4 ML too weak, bit 3 MH too strong
    uint8_t  agc;           // automatic gain, 0..255 at 3.3 V; mid-range is ideal
    uint16_t magnitude;     // CORDIC magnitude
};

void        As5600Begin(TwoWire* bus);
bool        As5600Read(As5600Reading* r);
bool        As5600RawAngle(uint16_t* raw);
const char* As5600MagnetText(uint8_t status);
float       As5600Degrees(uint16_t raw);
