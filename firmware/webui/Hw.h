// The real hardware: sensors read without blocking the loop, fans, and the damper motor.
// The damper runs in its own task: the TMC2209's internal step generator (VACTUAL) turns the motor, and the AS5600
// closes the loop, stopping at the target angle. Parts that don't answer are reported absent, and their readings
// marked invalid; the rest keeps working (and with nothing connected, the simulation stands in).
#pragma once
#include "App.h"

struct HwStatus
{
    bool     scd, enc, tmc, tout, tin, mic;     // present and answering
    bool     magnet;                            // AS5600 sees its magnet
    float    v12;                               // supply, V
    uint16_t encRaw;
    float    angle;                             // damper, degrees from closed
    float    target;
    bool     moving, fault;                     // fault: didn't reach the target in time
    int      duty[2], rpm[2];                   // fans: 0 intake, 1 exhaust
    float    snd;                               // last sound level, dB (calibrated or dBFS)
};

void HwBegin();
void HwPoll(Inputs* in);                        // call often: updates in with fresh readings, keeps old ones
void HwSetFans(float intakePct, float exhaustPct);
void HwSetDamper(float deg);
void HwStatusGet(HwStatus* st);
int  HwDuty(float pct);                         // fan % to PWM duty, with the minimum duty
