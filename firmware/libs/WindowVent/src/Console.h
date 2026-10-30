// Tiny serial command interpreter: line editing, history (up/down arrows), argument splitting.
#pragma once
#include <Arduino.h>

#define CON_LINE_MAX  64
#define CON_ARGS_MAX  10
#define CON_HIST_SIZE 8

// Called with the split command line; argv[0] is the command name.
typedef void (*ConHandler)(int argc, char* argv[]);

void ConBegin(ConHandler handler, const char* banner);
void ConPoll();                         // call from loop(): handles every character received
bool ConKeyHit();                       // true (and discards it) if a key arrived; aborts long commands

// Number parsing: decimal, 0x1F, 1Fh, 0b101, 101b, with an optional leading '-'.
bool ConParseInt(const char* s, long* value);
// Fetch argv[i] as a number; prints an error and returns false if missing or malformed.
bool ConArgInt(int argc, char* argv[], int i, long* value);
