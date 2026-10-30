// Simulation for the developer view: stands in for the sensors, the fans and the damper, so the whole application
// runs on a bare ESP32. Two ways to drive it:
//   - manual: each reading is a slider;
//   - room model: occupants breathe CO2 into a room and the ventilation carries it out, warming or cooling the
//     room toward the outdoor temperature; time can run faster than real time.
#pragma once
#include <ArduinoJson.h>
#include "App.h"

struct SimState
{
    bool  on;
    bool  model;                    // room model (else: manual values)
    float co2, tin, rh, tout, snd;  // manual values; in the model, co2 and tin are computed
    int   occupants;
    float volume;                   // m3
    float flowMax;                  // m3/h per fan at 100 %
    float speed;                    // model time per real second
    float heatSetC;                 // the room's heating keeps it near this (when it's colder outside)
    float angle;                    // damper, degrees
    float rpm[2];
};

extern SimState g_sim;

void SimBegin();
void SimStep(float dt, float targetDeg, float intakePct, float exhaustPct);   // real seconds
void SimInputs(Inputs* in);
void SimToJson(JsonObject o);
void SimFromJson(JsonObjectConst o);
