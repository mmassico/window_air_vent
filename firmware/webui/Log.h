// Log: printed on the serial console and kept in a ring (in PSRAM) for the web page's developer view and
// GET /api/log. Lines are numbered from 0 at boot.
#pragma once
#include <Arduino.h>

#define LOG_LINES 2000                          // kept in PSRAM (40 in internal RAM if there is none)
#define LOG_LEN   128

void     Log(const char* fmt, ...) __attribute__((format(printf, 1, 2)));
uint32_t LogCount();                            // lines logged since boot
uint32_t LogFirst();                            // the oldest line still in the ring
bool     LogLine(uint32_t index, char* out);    // false if that line has left the ring
