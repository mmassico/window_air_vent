#include "History.h"

static HistRec*     s_ring;
static uint32_t     s_cap, s_head, s_count;
static double       s_clock, s_lastRec;
static portMUX_TYPE s_mux = portMUX_INITIALIZER_UNLOCKED;

// Sums over the current interval: one per field, with its number of valid samples.
static struct { float sum[7]; int n[7]; } s_acc;

void HistBegin()
{
    s_cap  = HIST_COUNT;
    s_ring = (HistRec*)ps_malloc(s_cap * sizeof(HistRec));
    if (!s_ring)                                    // no PSRAM: a shorter history in RAM
    {
        s_cap  = HIST_COUNT / 8;
        s_ring = (HistRec*)malloc(s_cap * sizeof(HistRec));
    }
}

static int16_t avg(int i, float scale)
{
    return s_acc.n[i] ? (int16_t)lroundf(s_acc.sum[i] / s_acc.n[i] * scale) : HIST_NONE;
}

void HistAdd(const Inputs& in, float fanPct, float damperDeg, float dt)
{
    const bool  ok[7] = { in.co2Ok, in.tinOk, in.toutOk, in.rhOk, in.sndOk, true, true };
    const float v[7]  = { in.co2, in.tin, in.tout, in.rh, in.snd, fanPct, damperDeg };
    for (int i = 0; i < 7; i++)
        if (ok[i]) { s_acc.sum[i] += v[i]; s_acc.n[i]++; }

    s_clock += dt;
    if (s_clock - s_lastRec < HIST_INTERVAL_S || !s_ring)
        return;
    s_lastRec = s_clock;

    HistRec r;
    r.t      = (uint32_t)s_clock;
    r.co2    = avg(0, 1);
    r.tin    = avg(1, 10);
    r.tout   = avg(2, 10);
    r.rh     = avg(3, 10);
    r.snd    = avg(4, 10);
    r.fan    = (uint8_t)constrain(avg(5, 1), 0, 100);
    r.damper = (uint8_t)constrain(avg(6, 1), 0, 255);
    memset(&s_acc, 0, sizeof(s_acc));

    portENTER_CRITICAL(&s_mux);
    s_ring[s_head] = r;
    s_head = (s_head + 1) % s_cap;
    if (s_count < s_cap)
        s_count++;
    portEXIT_CRITICAL(&s_mux);
}

double HistClock()
{
    return s_clock;
}

uint32_t HistCount()
{
    return s_count;
}

void HistCopy(uint32_t first, uint32_t n, HistRec* out)
{
    portENTER_CRITICAL(&s_mux);
    uint32_t start = (s_head + s_cap - s_count + first) % s_cap;
    for (uint32_t i = 0; i < n && first + i < s_count; i++)
        out[i] = s_ring[(start + i) % s_cap];
    portEXIT_CRITICAL(&s_mux);
}
