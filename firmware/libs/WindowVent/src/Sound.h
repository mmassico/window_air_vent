// Sound level from an analog microphone module (MAX9814: about 1.25 V DC bias, up to 2 V peak to peak) on an ADC1 pin.
// Measured in blocking bursts of one-shot reads at SOUND_RATE: the 12 V sense also reads ADC1 one-shot, and the
// core's continuous (DMA) mode can't share a unit with one-shot reads. Each burst: DC removed, a first-order high-pass
// at SOUND_HPF_HZ (cuts wind rumble and the fans' hum), then the RMS. Levels are in dBFS: 0 dB is a sine filling the
// ADC's whole range (0 to about 3.1 V at 12 dB attenuation).
#pragma once
#include <Arduino.h>

#define SOUND_RATE      8000    // samples per second (aiming; the achieved rate is reported)
#define SOUND_HPF_HZ    150
#define SOUND_MAX_MS    500     // longest burst (the sample buffer holds SOUND_RATE * SOUND_MAX_MS / 1000 samples)

struct SoundReading
{
    float dbfs;         // level of the burst, after the high-pass filter
    float rms;          // the same, in ADC counts
    int   dcMv;         // DC bias (the module's output at rest), mV
    int   p2p;          // peak to peak, ADC counts (0-4095)
    bool  clipped;      // touched 0 or 4095: lower the module's gain
    float rateHz;       // achieved sample rate
};

void  SoundBegin(uint8_t pin, uint8_t linkPin);    // linkPin: the pin wired to it, left high impedance
bool  SoundMeasure(uint32_t ms, SoundReading* r);  // one burst of ms milliseconds (10 to SOUND_MAX_MS)
float SoundDb(float rms);                           // ADC counts RMS to dBFS
