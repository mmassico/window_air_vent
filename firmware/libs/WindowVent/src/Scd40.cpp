#include "Scd40.h"

static TwoWire* s_bus;
static bool     s_running;

static uint8_t crc8(const uint8_t* data, int len)
{
    uint8_t crc = 0xff;
    for (int i = 0; i < len; i++)
    {
        crc ^= data[i];
        for (int b = 0; b < 8; b++)
            crc = (crc & 0x80) ? (crc << 1) ^ 0x31 : (crc << 1);
    }
    return crc;
}

static bool sendCommand(uint16_t cmd, const uint16_t* args = nullptr, int nargs = 0)
{
    s_bus->beginTransmission(SCD40_ADDR);
    s_bus->write(cmd >> 8);
    s_bus->write(cmd & 0xff);
    for (int i = 0; i < nargs; i++)
    {
        uint8_t w[2] = { (uint8_t)(args[i] >> 8), (uint8_t)(args[i] & 0xff) };
        s_bus->write(w, 2);
        s_bus->write(crc8(w, 2));
    }
    return s_bus->endTransmission() == 0;
}

static bool readWords(uint16_t* words, int n)
{
    uint8_t buf[3 * 9];
    if (s_bus->requestFrom((uint8_t)SCD40_ADDR, (uint8_t)(3 * n)) != 3 * n)
        return false;
    for (int i = 0; i < 3 * n; i++)
        buf[i] = s_bus->read();
    for (int i = 0; i < n; i++)
    {
        if (crc8(&buf[3 * i], 2) != buf[3 * i + 2])
            return false;
        words[i] = (buf[3 * i] << 8) | buf[3 * i + 1];
    }
    return true;
}

// Send a command, wait its execution time, read the answer.
static bool query(uint16_t cmd, uint16_t* words, int n, int waitMs = 1)
{
    if (!sendCommand(cmd))
        return false;
    delay(waitMs);
    return readWords(words, n);
}

void Scd40Begin(TwoWire* bus)
{
    s_bus = bus;
}

bool Scd40StartPeriodic()
{
    s_running = sendCommand(0x21b1);
    return s_running;
}

bool Scd40StopPeriodic()
{
    bool ok = sendCommand(0x3f86);
    delay(500);
    if (ok)
        s_running = false;
    return ok;
}

bool Scd40DataReady(bool* ready)
{
    uint16_t w;
    if (!query(0xe4b8, &w, 1))
        return false;
    *ready = (w & 0x07ff) != 0;
    return true;
}

bool Scd40Read(Scd40Reading* r)
{
    uint16_t w[3];
    if (!query(0xec05, w, 3))
        return false;
    r->co2   = w[0];
    r->tempC = -45.0f + 175.0f * w[1] / 65536.0f;
    r->rh    = 100.0f * w[2] / 65536.0f;
    return true;
}

bool Scd40Serial(uint64_t* serial)
{
    uint16_t w[3];
    if (!query(0x3682, w, 3))
        return false;
    *serial = ((uint64_t)w[0] << 32) | ((uint64_t)w[1] << 16) | w[2];
    return true;
}

bool Scd40SelfTest(bool* passed)
{
    uint16_t w;
    if (!query(0x3639, &w, 1, 10000))
        return false;
    *passed = (w == 0);
    return true;
}

bool Scd40ForcedRecal(uint16_t ppm, int* correction)
{
    uint16_t w;
    if (!sendCommand(0x362f, &ppm, 1))
        return false;
    delay(400);
    if (!readWords(&w, 1) || w == 0xffff)
        return false;
    *correction = (int)w - 0x8000;
    return true;
}

bool Scd40IsRunning()
{
    return s_running;
}
