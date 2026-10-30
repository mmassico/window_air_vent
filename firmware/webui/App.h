// Shared types of the window-vent application: settings, sensor inputs, control outputs, live state.
#pragma once
#include <Arduino.h>

#define FW_NAME      "window-vent webui"
#define FW_VERSION   "0.1.0"

#define CURVE_POINTS 5          // CO2 to fan look-up curve: ppm -> %, linear between the points

enum Mode : uint8_t { MODE_AUTO, MODE_MANUAL, MODE_OFF, MODE_BOOST };

// Every tunable value. Saved in NVS as JSON (Settings.cpp); missing keys keep their defaults.
struct Settings
{
    // CO2
    uint16_t curvePpm[CURVE_POINTS];    // ascending
    uint8_t  curvePct[CURVE_POINTS];    // fan % at each point; below the first point, the first %
    uint16_t openPpm;                   // the damper opens at or above this
    uint16_t closePpm;                  // and closes at or below this (hysteresis)
    uint16_t maxPpm;                    // absolute maximum: full ventilation, comfort limits ignored
    uint16_t targetLo, targetHi;        // target range, shown on the dashboard
    uint16_t minOpenS, minClosedS;      // shortest time between two damper moves
    uint8_t  minFanPct;                 // fan floor while open

    // Temperature
    bool     tempEnabled;
    float    tinMin, tinMax;            // indoor comfort range, C
    float    coldT[2];                  // outdoor temperature -> fan cap, linear between the two points
    uint8_t  coldPct[2];
    float    closeBelowC;               // colder outside than this: closed (unless CO2 >= maxPpm)
    float    coolDeltaC;                // free cooling: room above tinMax and outside this much cooler
    uint8_t  coolPct;                   // ... then at least this %
    uint8_t  hotPct;                    // warmer outside and the room above tinMax: cap

    // Quiet hours (local time, minutes after midnight; start > end spans midnight)
    bool     quietEnabled;
    uint16_t quietStart, quietEnd;
    uint8_t  quietPct;

    // Outdoor noise (audio mode)
    bool     noiseEnabled;
    float    noiseDb;                   // dB SPL (or dBFS if the microphone is uncalibrated)
    uint8_t  noisePct;                  // cap while too loud; 0 closes the damper
    uint16_t noiseHoldS;                // stays capped this long after the last loud reading
    float    micCal;                    // dB SPL = dBFS + this (0: uncalibrated, levels in dBFS)

    // Fans
    int8_t   balance;                   // intake minus exhaust, % (-20 to 20)
    uint8_t  fanMinDuty;                // PWM duty at 1 % demand

    // Modes
    Mode     mode;                      // the mode at boot (MODE_BOOST is never saved)
    uint16_t boostMin;
    bool     manualOpen;
    uint8_t  manualPct;

    // Damper (motor and encoder)
    uint16_t encZero;                   // raw AS5600 value with the damper closed
    uint8_t  openDeg;                   // open angle from closed
    int8_t   motorDir;                  // +1 or -1: which way the motor turns to open
    uint16_t motorSpeed;                // microsteps/s

    // Network and time
    char     host[24];                  // mDNS name: http://<host>.local
    char     tz[48];                    // POSIX TZ string
};

// One set of sensor readings (from the hardware, or the simulation).
struct Inputs
{
    float co2;   bool co2Ok;            // ppm
    float tin;   bool tinOk;            // indoor C
    float rh;    bool rhOk;             // %
    float tout;  bool toutOk;           // outdoor C
    float snd;   bool sndOk;            // dB
    int   minuteOfDay;                  // local time, -1 if unknown
};

// Limits that shaped the last control decision (bits), shown on the dashboard.
enum Limit : uint16_t
{
    LIM_COLD   = 1 << 0,                // capped: cold outside
    LIM_FREEZE = 1 << 1,                // closed: below closeBelowC
    LIM_HOT    = 1 << 2,                // capped: warmer outside, room warm
    LIM_COOL   = 1 << 3,                // raised: free cooling
    LIM_QUIET  = 1 << 4,                // capped: quiet hours
    LIM_NOISE  = 1 << 5,                // capped or closed: loud outside
    LIM_MAX    = 1 << 6,                // CO2 above the absolute maximum: full
    LIM_NOCO2  = 1 << 7,                // no CO2 reading: fallback
    LIM_HOLD   = 1 << 8,                // damper held by its minimum open/closed time
    LIM_ROOM   = 1 << 9,                // capped: room below its comfort minimum
};

struct Outputs
{
    bool     open;                      // damper
    float    demandPct;                 // what CO2 (and cooling) ask for
    float    fanPct;                    // after the caps and the ramp
    float    intakePct, exhaustPct;     // after the balance trim
    uint16_t limits;                    // Limit bits
    char     reason[96];                // one line for the dashboard
};

extern Settings g_set;
