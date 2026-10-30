#include "Sim.h"

#define OUTDOOR_CO2   420.0f        // ppm
#define CO2_PER_HEAD  0.015f        // m3/h exhaled, a sleeping adult
#define AIR_WEIGHT    0.25f         // share of the room's heat in its air (walls and furniture hold the rest)
#define HEAT_RATE     0.5f          // C per hour the heating can add
#define DAMPER_DEG_S  90.0f
#define RPM_MIN       450.0f        // Noctua NF-A8 PWM: about 450 rpm at its minimum, 2200 at full
#define RPM_MAX       2200.0f

SimState g_sim;

void SimBegin()
{
    g_sim.on        = true;
    g_sim.model     = true;
    g_sim.co2       = 800;
    g_sim.tin       = 21;
    g_sim.rh        = 40;
    g_sim.tout      = -5;
    g_sim.snd       = 45;
    g_sim.occupants = 1;
    g_sim.volume    = 30;
    g_sim.flowMax   = 30;
    g_sim.leakAch   = 0.1f;         // a fairly tight closed room
    g_sim.speed     = 1;
    g_sim.heatSetC  = 21;
}

void SimStep(float dt, float targetDeg, float intakePct, float exhaustPct)
{
    // Damper and fans follow their commands.
    float d = targetDeg - g_sim.angle, step = DAMPER_DEG_S * dt;
    g_sim.angle += constrain(d, -step, step);
    float pct[2] = { intakePct, exhaustPct };
    for (int i = 0; i < 2; i++)
        g_sim.rpm[i] = pct[i] > 0 ? RPM_MIN + (RPM_MAX - RPM_MIN) * pct[i] / 100.0f : 0;

    if (!g_sim.model)
        return;

    // Room model, in model time (hours). Flow only with the damper open, scaled by how far open.
    float h      = dt * g_sim.speed / 3600.0f;
    float open   = constrain(g_sim.angle / (g_set.openDeg ? g_set.openDeg : 90), 0.0f, 1.0f);
    float flow   = g_sim.flowMax * min(intakePct, exhaustPct) / 100.0f * open;     // m3/h, balanced part
    float ach    = flow / g_sim.volume + g_sim.leakAch;                             // air changes per hour
    g_sim.co2   += h * (g_sim.occupants * CO2_PER_HEAD * 1e6f / g_sim.volume - ach * (g_sim.co2 - OUTDOOR_CO2));
    g_sim.co2    = max(g_sim.co2, OUTDOOR_CO2);
    float heat   = g_sim.tin < g_sim.heatSetC ? min(HEAT_RATE, (g_sim.heatSetC - g_sim.tin) * 2) : 0;
    g_sim.tin   += h * (ach * AIR_WEIGHT * (g_sim.tout - g_sim.tin) + heat + 0.1f * g_sim.occupants);
}

void SimInputs(Inputs* in)
{
    in->co2  = g_sim.co2;  in->co2Ok  = true;
    in->tin  = g_sim.tin;  in->tinOk  = true;
    in->rh   = g_sim.rh;   in->rhOk   = true;
    in->tout = g_sim.tout; in->toutOk = true;
    in->snd  = g_sim.snd;  in->sndOk  = true;
}

void SimToJson(JsonObject o)
{
    o["on"] = g_sim.on;               o["model"] = g_sim.model;
    o["co2"] = roundf(g_sim.co2);     o["tin"] = roundf(g_sim.tin * 10) / 10;
    o["rh"] = roundf(g_sim.rh);       o["tout"] = roundf(g_sim.tout * 10) / 10;
    o["snd"] = roundf(g_sim.snd);
    o["occupants"] = g_sim.occupants; o["volume"] = g_sim.volume;  o["flowMax"] = g_sim.flowMax;
    o["leakAch"] = roundf(g_sim.leakAch * 10) / 10;
    o["speed"] = g_sim.speed;         o["heatSetC"] = g_sim.heatSetC;
}

template <typename T> static void num(JsonObjectConst o, const char* key, T* v, float lo, float hi)
{
    if (o[key].is<float>() || o[key].is<long>())
        *v = (T)constrain(o[key].as<float>(), lo, hi);
}

void SimFromJson(JsonObjectConst o)
{
    if (o["on"].is<bool>())    g_sim.on = o["on"];
    if (o["model"].is<bool>()) g_sim.model = o["model"];
    num(o, "co2", &g_sim.co2, 300, 5000);
    num(o, "tin", &g_sim.tin, -10, 45);
    num(o, "rh", &g_sim.rh, 0, 100);
    num(o, "tout", &g_sim.tout, -40, 45);
    num(o, "snd", &g_sim.snd, 0, 120);
    num(o, "occupants", &g_sim.occupants, 0, 8);
    num(o, "volume", &g_sim.volume, 5, 500);
    num(o, "flowMax", &g_sim.flowMax, 1, 200);
    num(o, "leakAch", &g_sim.leakAch, 0, 10);
    num(o, "speed", &g_sim.speed, 1, 600);
    num(o, "heatSetC", &g_sim.heatSetC, 5, 30);
}
