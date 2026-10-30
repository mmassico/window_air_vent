#include "As5600.h"

#define REG_STATUS    0x0b
#define REG_RAW_ANGLE 0x0c
#define REG_AGC       0x1a
#define REG_MAGNITUDE 0x1b

static TwoWire* s_bus;

static bool readRegs(uint8_t reg, uint8_t* buf, int n)
{
    s_bus->beginTransmission(AS5600_ADDR);
    s_bus->write(reg);
    if (s_bus->endTransmission(false) != 0)
        return false;
    if (s_bus->requestFrom((uint8_t)AS5600_ADDR, (uint8_t)n) != n)
        return false;
    for (int i = 0; i < n; i++)
        buf[i] = s_bus->read();
    return true;
}

void As5600Begin(TwoWire* bus)
{
    s_bus = bus;
}

bool As5600RawAngle(uint16_t* raw)
{
    uint8_t b[2];
    if (!readRegs(REG_RAW_ANGLE, b, 2))
        return false;
    *raw = ((b[0] & 0x0f) << 8) | b[1];
    return true;
}

bool As5600Read(As5600Reading* r)
{
    uint8_t b[2];
    if (!As5600RawAngle(&r->raw))
        return false;
    if (!readRegs(REG_STATUS, b, 1))
        return false;
    r->status = b[0] & 0x38;
    if (!readRegs(REG_AGC, b, 1))
        return false;
    r->agc = b[0];
    if (!readRegs(REG_MAGNITUDE, b, 2))
        return false;
    r->magnitude = ((b[0] & 0x0f) << 8) | b[1];
    return true;
}

const char* As5600MagnetText(uint8_t status)
{
    if (!(status & 0x20)) return "no magnet";
    if (status & 0x10)    return "too weak";
    if (status & 0x08)    return "too strong";
    return "OK";
}

float As5600Degrees(uint16_t raw)
{
    return raw * 360.0f / 4096.0f;
}
