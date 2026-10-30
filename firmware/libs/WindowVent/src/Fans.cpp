#include "Fans.h"
#include "Pins.h"

#define PWM_BITS     10
#define MIN_EDGE_US  2000       // ignore edges closer than this (noise); 2 ms = 15000 rpm
#define AVG_PULSES   4          // the period is averaged over this many pulses

static const uint8_t s_pwmPin[FAN_COUNT]  = { PIN_FAN0_PWM, PIN_FAN1_PWM };
static const uint8_t s_tachPin[FAN_COUNT] = { PIN_FAN0_TACH, PIN_FAN1_TACH };
static int           s_duty[FAN_COUNT];

static volatile uint32_t s_lastEdge[FAN_COUNT];
static volatile uint32_t s_period[FAN_COUNT];     // microseconds per AVG_PULSES pulses
static volatile uint32_t s_firstEdge[FAN_COUNT];
static volatile int      s_count[FAN_COUNT];

static void IRAM_ATTR onTach(void* arg)
{
    int      fan = (int)(intptr_t)arg;
    uint32_t now = micros();
    if (now - s_lastEdge[fan] < MIN_EDGE_US)
        return;
    s_lastEdge[fan] = now;
    int count = s_count[fan] + 1;
    s_count[fan] = count;
    if (count >= AVG_PULSES)
    {
        s_period[fan]    = now - s_firstEdge[fan];
        s_firstEdge[fan] = now;
        s_count[fan]     = 0;
    }
}

void FansBegin()
{
    for (int i = 0; i < FAN_COUNT; i++)
    {
        ledcAttach(s_pwmPin[i], FAN_PWM_HZ, PWM_BITS);
        FansSetDuty(i, 0);
        pinMode(s_tachPin[i], INPUT_PULLUP);
        attachInterruptArg(s_tachPin[i], onTach, (void*)(intptr_t)i, FALLING);
    }
}

void FansSetDuty(int fan, int percent)
{
    percent = constrain(percent, 0, 100);
    s_duty[fan] = percent;
    uint32_t v = (uint32_t)percent * ((1 << PWM_BITS) - 1) / 100;
    ledcWrite(s_pwmPin[fan], FAN_PWM_INVERT ? ((1 << PWM_BITS) - 1) - v : v);
}

int FansGetDuty(int fan)
{
    return s_duty[fan];
}

int FansRpm(int fan)
{
    noInterrupts();
    uint32_t period = s_period[fan];
    uint32_t last   = s_lastEdge[fan];
    interrupts();
    if (period == 0 || micros() - last > 1000000)
        return 0;
    // AVG_PULSES pulses in 'period' us, 2 pulses per turn.
    return (int)(60.0f * 1e6f * AVG_PULSES / 2.0f / period + 0.5f);
}
