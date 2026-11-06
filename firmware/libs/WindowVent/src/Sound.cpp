#include "Sound.h"
#include "driver/gpio.h"

#define FULL_SCALE_RMS  (2048.0f / 1.41421356f)    // a sine from 0 to 4095
#define SETTLE          32                         // samples skipped while the high-pass filter settles
#define SETTLE_A        240                        // ... and while the A-weighting settles (its slowest pole, 20.6 Hz)

// A-weighting at 8000 samples/s: the analog filter's poles at 20.6 Hz (twice), 107.7 Hz and 737.9 Hz, by the
// bilinear transform, 0 dB at 1 kHz. Its two poles at 12.2 kHz are left out: they act above 4 kHz, where the
// transform would bend the response. Two biquads: b0 b1 b2 a1 a2 (a0 = 1).
const float SOUND_A_SOS[2][5] = {
    { 0.8983096816f, -1.7966193631f, 0.8983096816f, -1.4695579119f, 0.5060072156f },
    { 1.0f,          -2.0f,          1.0f,          -1.9679028120f, 0.9681603694f },
};

static uint8_t  s_pin;
static uint16_t s_buf[SOUND_RATE * SOUND_MAX_MS / 1000];

void SoundBegin(uint8_t pin, uint8_t linkPin)
{
    s_pin = pin;
    // The link pin is wired to the ADC pin: no output, no input buffer, no pull-up or pull-down, so it doesn't load
    // the signal. (gpio_reset_pin() alone would leave its pull-up on.)
    gpio_reset_pin((gpio_num_t)linkPin);
    gpio_set_direction((gpio_num_t)linkPin, GPIO_MODE_DISABLE);
    gpio_set_pull_mode((gpio_num_t)linkPin, GPIO_FLOATING);
    gpio_set_pull_mode((gpio_num_t)pin, GPIO_FLOATING);
    analogSetPinAttenuation(pin, ADC_11db);         // 12 dB: about 0 to 3.1 V
    analogRead(pin);                                // attaches the pin to ADC1
}

float SoundDb(float rms)
{
    return rms > 0.01f ? 20.0f * log10f(rms / FULL_SCALE_RMS) : -120.0f;
}

bool SoundMeasure(uint32_t ms, SoundReading* r)
{
    uint32_t n = constrain(ms, 10UL, (uint32_t)SOUND_MAX_MS) * SOUND_RATE / 1000;
    uint32_t period = 1000000UL / SOUND_RATE;

    // Sample: paced by micros(); if a read takes longer than a period, the burst simply runs slower (reported).
    uint32_t t0 = micros(), t = t0;
    for (uint32_t i = 0; i < n; i++)
    {
        while (micros() - t < period)
            ;
        t += period;
        s_buf[i] = analogRead(s_pin);
    }
    uint32_t elapsed = micros() - t0;

    uint32_t sum = 0;
    int      lo = 4095, hi = 0;
    for (uint32_t i = 0; i < n; i++)
    {
        sum += s_buf[i];
        lo = min(lo, (int)s_buf[i]);
        hi = max(hi, (int)s_buf[i]);
    }
    float mean = (float)sum / n;

    // High-pass: y[i] = a * (y[i-1] + x[i] - x[i-1]), on the signal less its mean (a smaller start-up step).
    float rate = elapsed ? n * 1e6f / elapsed : SOUND_RATE;
    float a    = 1.0f / (1.0f + 2.0f * PI * SOUND_HPF_HZ / rate);
    float prev = s_buf[0] - mean, y = 0, energy = 0, energyA = 0;
    float st[2][4] = {};                            // per biquad: x[n-1], x[n-2], y[n-1], y[n-2]
    for (uint32_t i = 1; i < n; i++)
    {
        float x = s_buf[i] - mean;
        y = a * (y + x - prev);
        prev = x;
        if (i >= SETTLE)
            energy += y * y;
        float v = x;                                // A-weighting, direct form I
        for (int k = 0; k < 2; k++)
        {
            const float* c = SOUND_A_SOS[k];
            float* z = st[k];
            float o = c[0] * v + c[1] * z[0] + c[2] * z[1] - c[3] * z[2] - c[4] * z[3];
            z[1] = z[0]; z[0] = v;
            z[3] = z[2]; z[2] = o;
            v = o;
        }
        if (i >= SETTLE_A)
            energyA += v * v;
    }

    long mv = 0;                                     // DC bias, calibrated: a few millivolt reads
    for (int i = 0; i < 16; i++)
        mv += analogReadMilliVolts(s_pin);

    r->rms     = sqrtf(energy / (n - SETTLE));
    r->dbfs    = SoundDb(r->rms);
    r->dba     = n > SETTLE_A ? SoundDb(sqrtf(energyA / (n - SETTLE_A))) : r->dbfs;
    r->dcMv    = mv / 16;
    r->p2p     = hi - lo;
    r->clipped = lo == 0 || hi == 4095;
    r->rateHz  = rate;
    return true;
}
