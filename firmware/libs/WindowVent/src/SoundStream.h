// Continuous sound level at 8000 samples/s, without a pause and without the CPU, from either microphone:
// - the MAX9814 (analog): the ADC's DMA mode samples it. DMA can't share ADC1 with one-shot reads (analogRead), so
//   the 12 V sense, also on ADC1, comes through here too: don't call analogRead on an ADC1 pin once this is started.
// - the INMP441 (I2S, digital): the I2S peripheral reads it by DMA. The ADC stays free for analogRead.
// A task filters the samples into blocks of 1/8 s, a sound level meter's FAST response. Nothing is missed between
// readings, so a short sound such as a dog's bark shows up in its block. For the blocking one-shot bursts, see Sound.h.
#pragma once
#include <Arduino.h>

#define SOUND_STREAM_RATE       8000    // samples per second, per pin
#define SOUND_STREAM_BLOCK      1000    // samples per block: 1/8 s
#define SOUND_STREAM_RING       64      // blocks kept: 8 s
#define SOUND_STREAM_PER_S      8       // blocks per second

// A span of blocks. Levels are in dBFS, as in Sound.h: for the INMP441, 0 dBFS is a sine filling its 24-bit range,
// and its sheet gives -26 dBFS for 94 dB SPL at 1 kHz, so dBA = A-weighted dBFS + 120.
struct SoundStats
{
    uint32_t blocks;    // blocks in the span; 0: the other fields mean nothing
    float    dba;       // A-weighted level of the whole span (its energy average)
    float    dbaMax;    // A-weighted level of its loudest block
    float    dbfs;      // the whole span's level through the 150 Hz high-pass only
    int      p2p;       // peak to peak, on a 0-4095 scale (ADC counts; the INMP441's range scaled to it)
    bool     clipped;   // touched either end of the range
    int      dcMv;      // analog: the microphone's DC bias now, mV; I2S: 0
    bool     micOk;     // a microphone seems connected: analog, a bias in range; I2S, a signal that isn't constant
    float    rateHz;    // samples per second achieved since the start
};

// Analog (MAX9814). linkPin: the pin wired to micPin, left high impedance. False if the ADC driver refuses.
bool     SoundStreamBegin(uint8_t micPin, uint8_t linkPin, uint8_t otherPin);
// I2S (INMP441, its L/R pin to GND: the left slot). linkPin: a pin that may be wired to sdPin (PCB's JP2), left high
// impedance. False if the I2S driver refuses.
bool     SoundStreamBeginI2s(uint8_t sckPin, uint8_t wsPin, uint8_t sdPin, uint8_t linkPin);
uint32_t SoundStreamCount();                            // blocks since the start
bool     SoundStreamRead(uint32_t* cursor, SoundStats* s);  // the blocks from *cursor on (the last 8 s at most), then
                                                        //   *cursor moves past them; false if there are none
int      SoundStreamOtherMv();                          // analog only: otherPin's voltage, mV (over the last block)
