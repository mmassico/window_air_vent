// Sensirion SCD40 CO2 / temperature / humidity sensor (I2C address 0x62).
// Commands are 16-bit; every 16-bit word on the wire is followed by a CRC-8.
#pragma once
#include <Wire.h>

#define SCD40_ADDR 0x62

struct Scd40Reading
{
    uint16_t co2;       // ppm
    float    tempC;
    float    rh;        // %
};

void Scd40Begin(TwoWire* bus);
bool Scd40StartPeriodic();              // one reading every 5 s
bool Scd40StopPeriodic();               // needed before serial, self-test and recalibration
bool Scd40DataReady(bool* ready);
bool Scd40Read(Scd40Reading* r);
bool Scd40Serial(uint64_t* serial);     // idle mode only
bool Scd40SelfTest(bool* passed);       // idle mode only, takes 10 s
bool Scd40ForcedRecal(uint16_t ppm, int* correction);  // idle mode only; run after 3 min at a known level
bool Scd40IsRunning();
