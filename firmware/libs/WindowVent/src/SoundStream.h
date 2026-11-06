// Continuous sound level: the ADC's DMA mode samples the microphone at 8000 samples/s without a pause and without the
// CPU, and a task filters the samples into blocks of 1/8 s, a sound level meter's FAST response. Nothing is missed
// between readings, so a short sound such as a dog's bark shows up in its block.
// DMA can't share ADC1 with one-shot reads (analogRead), so the 12 V sense, also on ADC1, comes through here too: don't
// call analogRead on an ADC1 pin once this is started. For the blocking one-shot bursts, see Sound.h.
#pragma once
#include <Arduino.h>

#define SOUND_STREAM_RATE       8000    // samples per second, per pin
#define SOUND_STREAM_BLOCK      1000    // samples per block: 1/8 s
#define SOUND_STREAM_RING       64      // blocks kept: 8 s
#define SOUND_STREAM_PER_S      8       // blocks per second

// A span of blocks. Levels are in dBFS, as in Sound.h.
struct SoundStats
{
    uint32_t blocks;    // blocks in the span; 0: the other fields mean nothing
    float    dba;       // A-weighted level of the whole span (its energy average)
    float    dbaMax;    // A-weighted level of its loudest block
    float    dbfs;      // the whole span's level through the 150 Hz high-pass only
    int      p2p;       // peak to peak, ADC counts
    bool     clipped;   // touched 0 or 4095
    int      dcMv;      // the microphone's DC bias now, mV
    float    rateHz;    // samples per second achieved since the start
};

// linkPin: the pin wired to micPin, left high impedance. False if the ADC driver refuses.
bool     SoundStreamBegin(uint8_t micPin, uint8_t linkPin, uint8_t otherPin);
uint32_t SoundStreamCount();                            // blocks since the start
bool     SoundStreamRead(uint32_t* cursor, SoundStats* s);  // the blocks from *cursor on (the last 8 s at most), then
                                                        //   *cursor moves past them; false if there are none
int      SoundStreamOtherMv();                          // otherPin's voltage, mV (averaged over the last block)
