// Maxim DS18B20 1-Wire temperature sensor, one per pin, so Skip ROM addresses it (no ROM search).
// Three-wire wiring (VDD powered, no parasite power), 4.7 k pull-up to 3.3 V on DQ.
// Bit-banged, with the pin in open-drain mode.
#pragma once
#include <Arduino.h>

enum Ds18b20Status
{
    DS18B20_OK,
    DS18B20_ABSENT,         // no presence pulse: not wired, or no pull-up
    DS18B20_CRC,            // the scratchpad came back corrupted: check the wiring and the pull-up
    DS18B20_NOT_CONVERTED,  // 85.0 C, the power-on value: no conversion since it powered up
};

void          Ds18b20Begin(uint8_t pin);
bool          Ds18b20Present(uint8_t pin);
bool          Ds18b20Start(uint8_t pin);                    // start a conversion; 750 ms at 12 bits
Ds18b20Status Ds18b20Read(uint8_t pin, float* tempC);       // the last conversion
bool          Ds18b20Rom(uint8_t pin, uint8_t rom[8]);      // 64-bit ROM code, family 0x28; false if absent or bad CRC
const char*   Ds18b20Text(Ds18b20Status s);
