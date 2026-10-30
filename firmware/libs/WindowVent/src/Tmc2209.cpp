#include "Tmc2209.h"

#define SYNC          0x05
#define REPLY_ADDR    0xff
#define REPLY_TIMEOUT 20        // ms
#define FCLK          12000000.0f

static HardwareSerial* s_uart;
static uint8_t         s_addr;
static float           s_rsense;
static int             s_runMa;

static uint8_t crc8(const uint8_t* data, int len)
{
    uint8_t crc = 0;
    for (int i = 0; i < len; i++)
    {
        uint8_t byte = data[i];
        for (int b = 0; b < 8; b++)
        {
            if ((crc >> 7) ^ (byte & 0x01))
                crc = (crc << 1) ^ 0x07;
            else
                crc = crc << 1;
            byte >>= 1;
        }
    }
    return crc;
}

// Read n bytes with a timeout.
static bool receive(uint8_t* buf, int n)
{
    uint32_t t0 = millis();
    int got = 0;
    while (got < n)
    {
        if (s_uart->available())
            buf[got++] = s_uart->read();
        else if (millis() - t0 > REPLY_TIMEOUT)
            return false;
    }
    return true;
}

// Send a datagram. RX is wired to the same line, so the bytes come back as an echo: swallow it.
static bool send(const uint8_t* buf, int n)
{
    uint8_t echo[8];
    while (s_uart->available())
        s_uart->read();
    s_uart->write(buf, n);
    s_uart->flush();
    return receive(echo, n) && memcmp(echo, buf, n) == 0;
}

void Tmc2209Begin(HardwareSerial* uart, uint8_t addr, float rsense)
{
    s_uart   = uart;
    s_addr   = addr;
    s_rsense = rsense;
}

bool Tmc2209Read(uint8_t reg, uint32_t* value)
{
    uint8_t req[4] = { SYNC, s_addr, (uint8_t)(reg & 0x7f), 0 };
    uint8_t rep[8];
    req[3] = crc8(req, 3);
    if (!send(req, 4) || !receive(rep, 8))
        return false;
    if (rep[0] != SYNC || rep[1] != REPLY_ADDR || rep[2] != (reg & 0x7f) || rep[7] != crc8(rep, 7))
        return false;
    *value = ((uint32_t)rep[3] << 24) | ((uint32_t)rep[4] << 16) | ((uint32_t)rep[5] << 8) | rep[6];
    return true;
}

bool Tmc2209Write(uint8_t reg, uint32_t value)
{
    uint8_t dg[8] = { SYNC, s_addr, (uint8_t)(reg | 0x80),
                      (uint8_t)(value >> 24), (uint8_t)(value >> 16), (uint8_t)(value >> 8), (uint8_t)value, 0 };
    dg[7] = crc8(dg, 7);
    return send(dg, 8);
}

bool Tmc2209Init(int microsteps, int runMilliAmps, int holdPercent)
{
    // GCONF: pdn_disable (bit 6) so PDN_UART is a UART, mstep_reg_select (bit 7) so CHOPCONF sets
    // the microsteps, multistep_filt (bit 8). I_scale_analog = 0 (internal reference, no VREF pot),
    // en_SpreadCycle = 0 (StealthChop, silent).
    if (!Tmc2209Write(TMC_GCONF, (1 << 6) | (1 << 7) | (1 << 8)))
        return false;
    if (!Tmc2209Write(TMC_GSTAT, 0x07))             // clear reset / error flags
        return false;
    if (!Tmc2209Write(TMC_TPOWERDOWN, 20))           // about 0.4 s still before dropping to hold current
        return false;
    if (!Tmc2209Write(TMC_TCOOLTHRS, 0xfffff))       // StallGuard result valid at every speed
        return false;
    if (!Tmc2209Write(TMC_SGTHRS, 0))                // DIAG stall output off until set
        return false;
    if (!Tmc2209Write(TMC_VACTUAL, 0))
        return false;
    return Tmc2209SetMicrosteps(microsteps) && Tmc2209SetCurrent(runMilliAmps, holdPercent);
}

bool Tmc2209SetMicrosteps(int microsteps)
{
    uint32_t chop;
    int mres = 0;                                    // MRES: 0 = 256 ... 8 = full step
    for (int m = 256; m > 1 && m > microsteps; m >>= 1)
        mres++;
    if ((256 >> mres) != microsteps)
        return false;
    if (!Tmc2209Read(TMC_CHOPCONF, &chop))
        return false;
    chop = (chop & ~(0x0fUL << 24)) | ((uint32_t)mres << 24) | (1UL << 28);   // intpol: interpolate to 256
    return Tmc2209Write(TMC_CHOPCONF, chop);
}

int Tmc2209GetMicrosteps()
{
    uint32_t chop;
    if (!Tmc2209Read(TMC_CHOPCONF, &chop))
        return 0;
    return 256 >> ((chop >> 24) & 0x0f);
}

// Irms = (CS + 1) / 32 * Vfs / (Rsense + 0.02) / sqrt(2), Vfs = 0.325 V, or 0.180 V with vsense = 1.
bool Tmc2209SetCurrent(int runMilliAmps, int holdPercent)
{
    float    amps   = runMilliAmps / 1000.0f;
    float    r      = s_rsense + 0.02f;
    bool     vsense = false;
    int      cs     = (int)(32.0f * 1.41421f * amps * r / 0.325f - 1.0f + 0.5f);
    uint32_t chop;

    if (cs < 16)                                     // better resolution with the low range
    {
        vsense = true;
        cs = (int)(32.0f * 1.41421f * amps * r / 0.180f - 1.0f + 0.5f);
    }
    cs = constrain(cs, 0, 31);
    int hold = constrain((cs * holdPercent + 50) / 100, 0, 31);

    if (!Tmc2209Read(TMC_CHOPCONF, &chop))
        return false;
    chop = vsense ? (chop | (1UL << 17)) : (chop & ~(1UL << 17));
    if (!Tmc2209Write(TMC_CHOPCONF, chop))
        return false;
    if (!Tmc2209Write(TMC_IHOLD_IRUN, (6UL << 16) | ((uint32_t)cs << 8) | hold))   // IHOLDDELAY = 6
        return false;

    s_runMa = (int)((cs + 1) / 32.0f * (vsense ? 0.180f : 0.325f) / r / 1.41421f * 1000.0f + 0.5f);
    return true;
}

int Tmc2209GetCurrent()
{
    return s_runMa;
}

// VACTUAL unit: microsteps per (2^24 / fCLK) seconds, about 0.715 microstep/s at 12 MHz.
bool Tmc2209SetVelocity(long microstepsPerSecond)
{
    long v = lroundf(microstepsPerSecond * 16777216.0f / FCLK);
    v = constrain(v, -0x7fffff, 0x7fffff);
    return Tmc2209Write(TMC_VACTUAL, (uint32_t)v & 0xffffff);
}
