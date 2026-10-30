// Log: printed on the serial console and kept in a small ring for the web page's developer view.
#pragma once
#include <Arduino.h>

#define LOG_LINES 40
#define LOG_LEN   96

void     Log(const char* fmt, ...) __attribute__((format(printf, 1, 2)));
uint32_t LogCount();                            // lines logged since boot
bool     LogLine(uint32_t index, char* out);    // false if that line has left the ring
