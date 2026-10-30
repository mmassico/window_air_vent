// History for the dashboard's graphs: one averaged record every HIST_INTERVAL_S of the history clock, HIST_HOURS of
// them, in PSRAM. Served as binary (Web.cpp): a header, then the records oldest first, little-endian.
//
// The history clock runs at real speed, except while the simulation's room model runs faster than real time: it then
// follows the model's time, so the graphs show the simulated hours at their own pace. Each record carries its time.
#pragma once
#include "App.h"

#define HIST_INTERVAL_S 10
#define HIST_HOURS      24
#define HIST_COUNT      (HIST_HOURS * 3600 / HIST_INTERVAL_S)
#define HIST_NONE       (-32768)        // no reading in that interval

struct __attribute__((packed)) HistRec
{
    uint32_t t;                         // history clock, seconds
    int16_t  co2;                       // ppm
    int16_t  tin, tout;                 // 0.1 C
    int16_t  rh;                        // 0.1 %
    int16_t  snd;                       // 0.1 dB
    uint8_t  fan;                       // %
    uint8_t  damper;                    // degrees from closed (0 to 255)
};

struct __attribute__((packed)) HistHeader
{
    uint32_t count;                     // records that follow
    uint32_t interval;                  // history-clock seconds between them
    uint32_t clock;                     // the history clock now, seconds
    uint32_t recSize;                   // sizeof(HistRec)
};

void     HistBegin();
// Call every control step: dt is the step in history-clock seconds (real seconds, or model seconds when faster).
void     HistAdd(const Inputs& in, float fanPct, float damperDeg, float dt);
double   HistClock();
uint32_t HistCount();
void     HistCopy(uint32_t first, uint32_t n, HistRec* out);          // first = 0: the oldest kept
