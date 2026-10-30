#include "Ds18b20.h"
#include "driver/gpio.h"

// 1-Wire timing (us), standard speed.
#define T_RESET_LOW     480
#define T_PRESENCE      70
#define T_RESET_REST    410
#define T_WRITE1_LOW    6
#define T_WRITE1_REST   64
#define T_WRITE0_LOW    60
#define T_WRITE0_REST   10
#define T_READ_LOW      3
#define T_READ_SAMPLE   10
#define T_READ_REST     53

#define CMD_READ_ROM    0x33
#define CMD_SKIP_ROM    0xCC
#define CMD_CONVERT     0x44
#define CMD_READ_SCRATCH 0xBE

// Interrupts held off during each time slot, so nothing stretches the microsecond timing.
static portMUX_TYPE s_mux = portMUX_INITIALIZER_UNLOCKED;

static inline void lineLow(uint8_t pin)  { gpio_set_level((gpio_num_t)pin, 0); }
static inline void lineFree(uint8_t pin) { gpio_set_level((gpio_num_t)pin, 1); }   // open drain: the pull-up takes it high
static inline int  lineRead(uint8_t pin) { return gpio_get_level((gpio_num_t)pin); }

static bool reset(uint8_t pin)
{
    if (lineRead(pin) == 0)         // held low: shorted, or no pull-up
        return false;
    lineLow(pin);
    delayMicroseconds(T_RESET_LOW);
    portENTER_CRITICAL(&s_mux);
    lineFree(pin);
    delayMicroseconds(T_PRESENCE);
    bool present = lineRead(pin) == 0;
    portEXIT_CRITICAL(&s_mux);
    delayMicroseconds(T_RESET_REST);
    return present;
}

static void writeBit(uint8_t pin, int bit)
{
    portENTER_CRITICAL(&s_mux);
    lineLow(pin);
    delayMicroseconds(bit ? T_WRITE1_LOW : T_WRITE0_LOW);
    lineFree(pin);
    delayMicroseconds(bit ? T_WRITE1_REST : T_WRITE0_REST);
    portEXIT_CRITICAL(&s_mux);
}

static int readBit(uint8_t pin)
{
    portENTER_CRITICAL(&s_mux);
    lineLow(pin);
    delayMicroseconds(T_READ_LOW);
    lineFree(pin);
    delayMicroseconds(T_READ_SAMPLE);
    int bit = lineRead(pin);
    portEXIT_CRITICAL(&s_mux);
    delayMicroseconds(T_READ_REST);
    return bit;
}

static void writeByte(uint8_t pin, uint8_t b)
{
    for (int i = 0; i < 8; i++, b >>= 1)    // least significant bit first
        writeBit(pin, b & 1);
}

static uint8_t readByte(uint8_t pin)
{
    uint8_t b = 0;
    for (int i = 0; i < 8; i++)
        b |= readBit(pin) << i;
    return b;
}

// Dallas/Maxim CRC-8 (x^8 + x^5 + x^4 + 1, reflected)
static uint8_t crc8(const uint8_t* data, int len)
{
    uint8_t crc = 0;
    for (int i = 0; i < len; i++)
    {
        uint8_t b = data[i];
        for (int j = 0; j < 8; j++, b >>= 1)
        {
            uint8_t mix = (crc ^ b) & 1;
            crc >>= 1;
            if (mix)
                crc ^= 0x8C;
        }
    }
    return crc;
}

void Ds18b20Begin(uint8_t pin)
{
    gpio_reset_pin((gpio_num_t)pin);
    gpio_set_direction((gpio_num_t)pin, GPIO_MODE_INPUT_OUTPUT_OD);
    gpio_set_pull_mode((gpio_num_t)pin, GPIO_PULLUP_ONLY);   // weak backup; the 4.7 k does the real work
    lineFree(pin);
}

bool Ds18b20Present(uint8_t pin)
{
    return reset(pin);
}

bool Ds18b20Start(uint8_t pin)
{
    if (!reset(pin))
        return false;
    writeByte(pin, CMD_SKIP_ROM);
    writeByte(pin, CMD_CONVERT);
    return true;
}

Ds18b20Status Ds18b20Read(uint8_t pin, float* tempC)
{
    uint8_t sp[9];

    if (!reset(pin))
        return DS18B20_ABSENT;
    writeByte(pin, CMD_SKIP_ROM);
    writeByte(pin, CMD_READ_SCRATCH);
    for (int i = 0; i < 9; i++)
        sp[i] = readByte(pin);
    if (crc8(sp, 8) != sp[8])
        return DS18B20_CRC;
    int16_t raw = (int16_t)(sp[1] << 8 | sp[0]);
    int     res = (sp[4] >> 5) & 3;     // 0..3 = 9..12 bits: the low bits are undefined below 12
    raw &= ~((1 << (3 - res)) - 1);
    if (raw == 0x0550)
        return DS18B20_NOT_CONVERTED;
    *tempC = raw / 16.0f;
    return DS18B20_OK;
}

bool Ds18b20Rom(uint8_t pin, uint8_t rom[8])
{
    if (!reset(pin))
        return false;
    writeByte(pin, CMD_READ_ROM);
    for (int i = 0; i < 8; i++)
        rom[i] = readByte(pin);
    return crc8(rom, 7) == rom[7];
}

const char* Ds18b20Text(Ds18b20Status s)
{
    switch (s)
    {
        case DS18B20_OK:            return "OK";
        case DS18B20_ABSENT:        return "absent (no answer: wiring, or the 4.7 k pull-up)";
        case DS18B20_CRC:           return "CRC error (check the wiring and the pull-up)";
        case DS18B20_NOT_CONVERTED: return "no conversion yet";
    }
    return "?";
}
