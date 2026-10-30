#include "Control.h"

#define RAMP_PCT_PER_S  5.0f        // fan speed change rate
#define NO_CO2_PCT      30.0f       // fallback ventilation with no CO2 reading

static Mode     s_mode;
static uint32_t s_boostEnd;         // millis()
static bool     s_open;
static float    s_stateS = 1e9f;    // time in the current damper state; large: free to move at boot
static float    s_co2 = -1;         // last reading, -1 before the first
static float    s_fan;              // ramped fan %
static float    s_noiseLeftS;       // noise cap still held this long

void ControlBegin()
{
    s_mode = g_set.mode;
}

const char* ControlModeName(Mode m)
{
    switch (m)
    {
        case MODE_AUTO:   return "auto";
        case MODE_MANUAL: return "manual";
        case MODE_OFF:    return "off";
        case MODE_BOOST:  return "boost";
    }
    return "?";
}

void ControlSetMode(Mode m)
{
    s_mode = m;
    if (m == MODE_BOOST)
        s_boostEnd = millis() + g_set.boostMin * 60000UL;
}

Mode ControlMode()
{
    return s_mode;
}

uint32_t ControlBoostLeftS()
{
    return s_mode == MODE_BOOST ? (s_boostEnd - millis()) / 1000 : 0;
}

static float lerp(float x, float x0, float y0, float x1, float y1)
{
    if (x <= x0) return y0;
    if (x >= x1) return y1;
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0);
}

float ControlCurve(float co2)
{
    const Settings& s = g_set;
    if (co2 <= s.curvePpm[0])
        return s.curvePct[0];
    for (int i = 1; i < CURVE_POINTS; i++)
        if (co2 <= s.curvePpm[i])
            return lerp(co2, s.curvePpm[i - 1], s.curvePct[i - 1], s.curvePpm[i], s.curvePct[i]);
    return s.curvePct[CURVE_POINTS - 1];
}

static bool inQuietHours(int minute)
{
    const Settings& s = g_set;
    if (!s.quietEnabled || minute < 0)
        return false;
    if (s.quietStart <= s.quietEnd)
        return minute >= s.quietStart && minute < s.quietEnd;
    return minute >= s.quietStart || minute < s.quietEnd;     // spans midnight
}

// Ramp the fan % toward a target and split it by the balance trim.
static void fans(float target, float dt, Outputs* out)
{
    float step = RAMP_PCT_PER_S * dt;
    s_fan = target > s_fan ? min(target, s_fan + step) : max(target, s_fan - step);
    out->fanPct = s_fan;
    float half = s_fan > 0 ? g_set.balance / 2.0f : 0;
    out->intakePct  = constrain(s_fan + half, 0.0f, 100.0f);
    out->exhaustPct = constrain(s_fan - half, 0.0f, 100.0f);
}

static void setDamper(bool open)
{
    if (open != s_open)
    {
        s_open   = open;
        s_stateS = 0;
    }
}

void ControlStep(const Inputs& in, float dt, Outputs* out)
{
    const Settings& s = g_set;
    out->limits = 0;
    s_stateS += dt;

    if (in.co2Ok)
        s_co2 = in.co2;

    if (s_mode == MODE_BOOST && (int32_t)(millis() - s_boostEnd) >= 0)
        s_mode = g_set.mode == MODE_BOOST ? MODE_AUTO : g_set.mode;

    if (s_mode == MODE_OFF)
    {
        setDamper(false);
        out->demandPct = 0;
        fans(0, dt, out);
        out->open = s_open;
        snprintf(out->reason, sizeof(out->reason), "Off");
        return;
    }
    if (s_mode == MODE_MANUAL)
    {
        setDamper(s.manualOpen);
        out->demandPct = s.manualOpen ? s.manualPct : 0;
        fans(out->demandPct, dt, out);
        out->open = s_open;
        snprintf(out->reason, sizeof(out->reason), "Manual: %s, fans %d %%", s.manualOpen ? "open" : "closed",
                 s.manualOpen ? s.manualPct : 0);
        return;
    }
    if (s_mode == MODE_BOOST)
    {
        setDamper(true);
        out->demandPct = 100;
        fans(100, dt, out);
        out->open = s_open;
        snprintf(out->reason, sizeof(out->reason), "Boost: full ventilation, %lu min left",
                 (unsigned long)(ControlBoostLeftS() + 59) / 60);
        return;
    }

    // --- Auto ---------------------------------------------------------------------------------------------------
    bool  haveCo2 = in.co2Ok && s_co2 >= 0;
    float co2     = haveCo2 ? s_co2 : 0;
    float demand  = haveCo2 ? ControlCurve(co2) : NO_CO2_PCT;
    bool  wantOpen;
    if (!haveCo2)
    {
        out->limits |= LIM_NOCO2;
        wantOpen = true;
    }
    else
        wantOpen = s_open ? co2 > s.closePpm : co2 >= s.openPpm;

    // Temperatures: free cooling raises the demand; cold or heat cap it.
    float    cap   = 100;
    uint16_t capBy = 0;                 // the limit that set the lowest cap
    bool     temps = s.tempEnabled && in.tinOk && in.toutOk;
    bool  freeze = false;
    if (temps)
    {
        bool warmRoom = in.tin > s.tinMax;
        if (warmRoom && in.tout <= in.tin - s.coolDeltaC)
        {
            demand   = max(demand, (float)s.coolPct);
            wantOpen = true;
            out->limits |= LIM_COOL;
        }
        if (in.tout < in.tin)
        {
            float c = lerp(in.tout, s.coldT[0], s.coldPct[0], s.coldT[1], s.coldPct[1]);
            if (c < cap) { cap = c; capBy = LIM_COLD; if (c < 100) out->limits |= LIM_COLD; }
            if (in.tin < s.tinMin && s.minFanPct < cap)
            {
                cap = s.minFanPct;
                capBy = LIM_ROOM;
                out->limits |= LIM_ROOM;
            }
        }
        else if (warmRoom && s.hotPct < cap)
        {
            cap = s.hotPct;
            capBy = LIM_HOT;
            out->limits |= LIM_HOT;
        }
        if (in.tout < s.closeBelowC)
        {
            freeze = true;
            out->limits |= LIM_FREEZE;
        }
    }
    else if (s.tempEnabled && in.toutOk && in.tout < s.closeBelowC)
    {
        freeze = true;
        out->limits |= LIM_FREEZE;
    }

    if (inQuietHours(in.minuteOfDay) && s.quietPct < cap)
    {
        cap = s.quietPct;
        capBy = LIM_QUIET;
        out->limits |= LIM_QUIET;
    }

    if (s.noiseEnabled && in.sndOk && in.snd >= s.noiseDb)
        s_noiseLeftS = s.noiseHoldS;
    else
        s_noiseLeftS = max(0.0f, s_noiseLeftS - dt);
    if (s.noiseEnabled && s_noiseLeftS > 0 && s.noisePct < cap)
    {
        cap = s.noisePct;
        capBy = LIM_NOISE;
        out->limits |= LIM_NOISE;
    }

    bool overMax = haveCo2 && co2 >= s.maxPpm;
    if (overMax)
    {
        cap      = 100;
        demand   = 100;
        wantOpen = true;
        freeze   = false;
        out->limits = (out->limits & ~(LIM_COLD | LIM_ROOM | LIM_HOT | LIM_QUIET | LIM_NOISE | LIM_FREEZE)) | LIM_MAX;
    }
    if (freeze || cap <= 0)
        wantOpen = false;

    // Damper, held a minimum time in each state (the maximum overrides the hold).
    if (wantOpen != s_open)
    {
        float hold = s_open ? s.minOpenS : s.minClosedS;
        if (s_stateS >= hold || overMax || freeze)
            setDamper(wantOpen);
        else
            out->limits |= LIM_HOLD;
    }

    out->demandPct = demand;
    float target   = s_open ? min(max(demand, (float)s.minFanPct), cap) : 0;
    fans(target, dt, out);
    out->open = s_open;

    // One line for the dashboard: the dominant reason.
    char* r = out->reason;
    size_t n = sizeof(out->reason);
    if (overMax)
        snprintf(r, n, "CO2 %.0f ppm, above the %u maximum: full ventilation", co2, s.maxPpm);
    else if (out->limits & LIM_FREEZE)
        snprintf(r, n, "Closed: %.1f C outside, below %.0f C", in.tout, s.closeBelowC);
    else if (!haveCo2)
        snprintf(r, n, "No CO2 reading: fallback ventilation at %.0f %%", target);
    else if (!s_open && cap <= 0)       // a limit at 0 % closed it, whatever the CO2
    {
        switch (capBy)
        {
            case LIM_NOISE: snprintf(r, n, "Closed: loud outside"); break;
            case LIM_QUIET: snprintf(r, n, "Closed: quiet hours"); break;
            case LIM_COLD:  snprintf(r, n, "Closed: cold outside (%.1f C)", in.tout); break;
            case LIM_HOT:   snprintf(r, n, "Closed: warmer outside (%.1f C)", in.tout); break;
            case LIM_ROOM:  snprintf(r, n, "Closed: room cool (%.1f C)", in.tin); break;
            default:        snprintf(r, n, "Closed"); break;
        }
    }
    else if (!s_open)
        snprintf(r, n, (out->limits & LIM_HOLD) ? "Closed: held a little longer before reopening"
                                                : "Closed: CO2 below the %u ppm opening level", s.openPpm);
    else if (out->limits & LIM_HOLD)
        snprintf(r, n, "Open: held a little longer before closing");
    else if (out->limits & LIM_NOISE)
        snprintf(r, n, "Loud outside: fans capped at %u %%", s.noisePct);
    else if (out->limits & LIM_QUIET)
        snprintf(r, n, "Quiet hours: fans capped at %u %%", s.quietPct);
    else if (out->limits & LIM_ROOM)
        snprintf(r, n, "Room cool (%.1f C): fans at the %u %% floor", in.tin, s.minFanPct);
    else if ((out->limits & LIM_COLD) && demand > cap)
        snprintf(r, n, "Cold outside (%.1f C): fans capped at %.0f %%", in.tout, cap);
    else if ((out->limits & LIM_HOT) && demand > cap)
        snprintf(r, n, "Warmer outside: fans capped at %.0f %%", cap);
    else if (out->limits & LIM_COOL)
        snprintf(r, n, "Free cooling: room %.1f C, outside %.1f C", in.tin, in.tout);
    else if (co2 > s.targetHi)
        snprintf(r, n, "Ventilating: CO2 above the target range (%u to %u ppm)", s.targetLo, s.targetHi);
    else
        snprintf(r, n, "Open until CO2 falls to %u ppm", s.closePpm);
}
