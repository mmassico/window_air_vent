// History for the dashboard's graphs: one averaged record every HIST_INTERVAL_S, HIST_HOURS of them, in PSRAM.
// Served as binary (Web.cpp): a header, then the records oldest first, little-endian.
#pragma once
#include "App.h"

#define HIST_INTERVAL_S 10
#define HIST_HOURS      24
#define HIST_COUNT      (HIST_HOURS * 3600 / HIST_INTERVAL_S)
#define HIST_NONE       (-32768)        // no reading in that interval

struct __attribute__((packed)) HistRec
{
    int16_t co2;                        // ppm
    int16_t tin, tout;                  // 0.1 C
    int16_t rh;                         // 0.1 %
    int16_t snd;                        // 0.1 dB
    uint8_t fan;                        // %
    uint8_t damper;                     // degrees from closed (0 to 255)
};

struct __attribute__((packed)) HistHeader
{
    uint32_t count;                     // records that follow
    uint32_t interval;                  // seconds between them
    uint32_t ageMs;                     // time since the last one
    uint32_t recSize;                   // sizeof(HistRec)
};

void     HistBegin();
void     HistAdd(const Inputs& in, float fanPct, float damperDeg);   // call every second; records every interval
uint32_t HistCount();
uint32_t HistAgeMs();
void     HistCopy(uint32_t first, uint32_t n, HistRec* out);          // first = 0: the oldest kept
