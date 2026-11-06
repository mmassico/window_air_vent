// The real hardware: sensors read without blocking the loop, fans, and the damper motor.
// The damper runs in its own task: the TMC2209's internal step generator (VACTUAL) turns the motor, and the AS5600
// closes the loop, stopping at the target angle. At boot, a boundary test finds the closed and open stops (Hw.cpp):
// the closed one becomes encZero, and the open angle stays short of the other. Parts that don't answer are reported absent, and their readings
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
    bool     calibrating;                       // the boundary test is running
    float    travel;                            // degrees between the closed and open stops; 0: not measured
    int      duty[2], rpm[2];                   // fans: 0 intake, 1 exhaust
    float    snd;                               // last sound level, dB (calibrated or dBFS)
    float    scdT;                              // the SCD40's last temperature, C (after its offset)
};

void HwBegin();
void HwPoll(Inputs* in);                        // call often: updates in with fresh readings, keeps old ones
void HwSetFans(float intakePct, float exhaustPct);
void HwSetDamper(float deg);
void HwStatusGet(HwStatus* st);
int  HwDuty(float pct);                         // fan % to PWM duty, with the minimum duty

// For the console's test commands.
void HwDamperRetry();                           // clear a fault (blocked, seated) and move to the target again
void HwDamperCalibrate();                       // run the boundary test again (it runs once at boot by itself)
bool HwDamperCalSave();                         // true once after the test changed encZero or motorDir
void HwSetFanDuty(int fan, int duty);           // PWM duty %, as it is (no minimum duty)
void HwBusLock();                               // hold the damper's buses (TMC2209 UART, AS5600 I2C) to use
void HwBusUnlock();                             //   them from outside the damper task
