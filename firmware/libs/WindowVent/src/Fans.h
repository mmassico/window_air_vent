// Two 4-wire PWM fans: 25 kHz PWM out, tach in (2 pulses per turn).
#pragma once
#include <Arduino.h>

#define FAN_COUNT 2

void FansBegin();
void FansSetDuty(int fan, int percent);
int  FansGetDuty(int fan);
int  FansRpm(int fan);          // from the last tach periods; 0 if no pulse for 1 s
