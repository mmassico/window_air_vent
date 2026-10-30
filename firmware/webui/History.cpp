#include "History.h"

static HistRec*     s_ring;
static uint32_t     s_head, s_count, s_lastMs;
static portMUX_TYPE s_mux = portMUX_INITIALIZER_UNLOCKED;

// Sums over the current interval: one per field, with its number of valid samples.
static struct { float sum[7]; int n[7]; } s_acc;

void HistBegin()
{
    s_ring = (HistRec*)ps_malloc(HIST_COUNT * sizeof(HistRec));
    if (!s_ring)                                    // no PSRAM: a shorter history in RAM
        s_ring = (HistRec*)malloc(HIST_COUNT / 8 * sizeof(HistRec));
    s_lastMs = millis();
}

static int16_t avg(int i, float scale)
{
    return s_acc.n[i] ? (int16_t)lroundf(s_acc.sum[i] / s_acc.n[i] * scale) : HIST_NONE;
}

void HistAdd(const Inputs& in, float fanPct, float damperDeg)
{
    const bool  ok[7] = { in.co2Ok, in.tinOk, in.toutOk, in.rhOk, in.sndOk, true, true };
    const float v[7]  = { in.co2, in.tin, in.tout, in.rh, in.snd, fanPct, damperDeg };
    for (int i = 0; i < 7; i++)
        if (ok[i]) { s_acc.sum[i] += v[i]; s_acc.n[i]++; }

    if (millis() - s_lastMs < HIST_INTERVAL_S * 1000UL || !s_ring)
        return;
    s_lastMs += HIST_INTERVAL_S * 1000UL;

    HistRec r;
    r.co2    = avg(0, 1);
    r.tin    = avg(1, 10);
    r.tout   = avg(2, 10);
    r.rh     = avg(3, 10);
    r.snd    = avg(4, 10);
    r.fan    = (uint8_t)constrain(avg(5, 1), 0, 100);
    r.damper = (uint8_t)constrain(avg(6, 1), 0, 255);
    memset(&s_acc, 0, sizeof(s_acc));

    uint32_t cap = psramFound() ? HIST_COUNT : HIST_COUNT / 8;
    portENTER_CRITICAL(&s_mux);
    s_ring[s_head] = r;
    s_head = (s_head + 1) % cap;
    if (s_count < cap)
        s_count++;
    portEXIT_CRITICAL(&s_mux);
}

uint32_t HistCount()
{
    return s_count;
}

uint32_t HistAgeMs()
{
    return millis() - s_lastMs;
}

void HistCopy(uint32_t first, uint32_t n, HistRec* out)
{
    uint32_t cap = psramFound() ? HIST_COUNT : HIST_COUNT / 8;
    portENTER_CRITICAL(&s_mux);
    uint32_t start = (s_head + cap - s_count + first) % cap;
    for (uint32_t i = 0; i < n && first + i < s_count; i++)
        out[i] = s_ring[(start + i) % cap];
    portEXIT_CRITICAL(&s_mux);
}
