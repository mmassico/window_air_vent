// The ventilation logic: sensor inputs and settings in, damper and fan speeds out. No hardware access, so it runs
// the same on real sensors and in the simulation.
//
// Auto mode, each step:
//   1. demand = CO2 look-up curve; free cooling may raise it. No smoothing: the open/close hysteresis and the fan
//      ramp keep it steady (and the SCD40 gives one reading every 5 s).
//   2. cap    = the lowest of: cold outside (linear in the outdoor temperature), room below its comfort minimum,
//               warmer outside with a warm room, quiet hours, outdoor noise.
//   3. CO2 at or above the absolute maximum lifts every cap: full ventilation.
//   4. damper: opens at openPpm (or for free cooling), closes at closePpm, each state held a minimum time; a cap of
//      0 closes it. Fans run at max(demand, floor) within the cap while open, and stop when closed.
//   5. the fan % ramps (no sudden jumps), then the balance trim splits it into intake and exhaust.
#pragma once
#include "App.h"

void        ControlBegin();
void        ControlStep(const Inputs& in, float dt, Outputs* out);   // dt: seconds since the last step
void        ControlSetMode(Mode m);                                  // MODE_BOOST starts the boost timer
Mode        ControlMode();
uint32_t    ControlBoostLeftS();
const char* ControlModeName(Mode m);
float       ControlCurve(float co2);                                 // the look-up curve alone, %
