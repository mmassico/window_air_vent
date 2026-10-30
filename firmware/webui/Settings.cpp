#include "Settings.h"
#include <Preferences.h>
#include "Pins.h"

Settings g_set;

void SettingsDefaults(Settings* s)
{
    static const uint16_t ppm[CURVE_POINTS] = { 600, 700, 850, 1000, 1200 };
    static const uint8_t  pct[CURVE_POINTS] = { 0, 20, 45, 70, 100 };
    memset(s, 0, sizeof(*s));
    memcpy(s->curvePpm, ppm, sizeof(ppm));
    memcpy(s->curvePct, pct, sizeof(pct));
    s->openPpm    = 750;
    s->closePpm   = 650;
    s->maxPpm     = 1400;
    s->targetLo   = 600;
    s->targetHi   = 900;
    s->minOpenS   = 300;
    s->minClosedS = 180;
    s->minFanPct  = 15;

    s->tempEnabled = true;
    s->tinMin      = 19.0f;
    s->tinMax      = 24.0f;
    s->coldT[0]    = -20.0f; s->coldPct[0] = 30;
    s->coldT[1]    = 10.0f;  s->coldPct[1] = 100;
    s->closeBelowC = -30.0f;
    s->coolDeltaC  = 2.0f;
    s->coolPct     = 60;
    s->hotPct      = 40;

    s->quietEnabled = false;
    s->quietStart   = 22 * 60;
    s->quietEnd     = 7 * 60;
    s->quietPct     = 40;

    s->noiseEnabled = false;
    s->noiseDb      = 70.0f;
    s->noisePct     = 0;
    s->noiseHoldS   = 120;
    s->micCal       = MIC_CAL_DB;

    s->balance    = 0;
    s->fanMinDuty = 20;

    s->mode       = MODE_AUTO;
    s->boostMin   = 30;
    s->manualOpen = true;
    s->manualPct  = 50;

    s->encZero    = 0;
    s->openDeg    = 90;
    s->motorDir   = 1;
    s->motorSpeed = 800;

    strlcpy(s->host, "window-vent", sizeof(s->host));
    strlcpy(s->tz, "EST5EDT,M3.2.0,M11.1.0", sizeof(s->tz));   // Eastern time with DST
}

// --- JSON ------------------------------------------------------------------------------------------------------

template <typename T> static void num(JsonObjectConst o, const char* key, T* v, float lo, float hi)
{
    JsonVariantConst x = o[key];
    if (x.is<float>() || x.is<long>())
        *v = (T)constrain(x.as<float>(), lo, hi);
}

static void flag(JsonObjectConst o, const char* key, bool* v)
{
    if (o[key].is<bool>())
        *v = o[key].as<bool>();
}

static void text(JsonObjectConst o, const char* key, char* v, size_t n)
{
    if (o[key].is<const char*>() && strlen(o[key].as<const char*>()) > 0)
        strlcpy(v, o[key].as<const char*>(), n);
}

void SettingsToJson(const Settings& s, JsonObject o)
{
    JsonObject c = o["co2"].to<JsonObject>();
    JsonArray  cp = c["curvePpm"].to<JsonArray>(), cq = c["curvePct"].to<JsonArray>();
    for (int i = 0; i < CURVE_POINTS; i++) { cp.add(s.curvePpm[i]); cq.add(s.curvePct[i]); }
    c["openPpm"] = s.openPpm;     c["closePpm"] = s.closePpm;     c["maxPpm"] = s.maxPpm;
    c["targetLo"] = s.targetLo;   c["targetHi"] = s.targetHi;
    c["minOpenS"] = s.minOpenS;   c["minClosedS"] = s.minClosedS; c["minFanPct"] = s.minFanPct;

    JsonObject t = o["temp"].to<JsonObject>();
    t["enabled"] = s.tempEnabled; t["tinMin"] = s.tinMin;          t["tinMax"] = s.tinMax;
    t["coldT0"] = s.coldT[0];     t["coldPct0"] = s.coldPct[0];
    t["coldT1"] = s.coldT[1];     t["coldPct1"] = s.coldPct[1];
    t["closeBelowC"] = s.closeBelowC;
    t["coolDeltaC"] = s.coolDeltaC; t["coolPct"] = s.coolPct;     t["hotPct"] = s.hotPct;

    JsonObject q = o["quiet"].to<JsonObject>();
    q["enabled"] = s.quietEnabled; q["start"] = s.quietStart; q["end"] = s.quietEnd; q["pct"] = s.quietPct;

    JsonObject n = o["noise"].to<JsonObject>();
    n["enabled"] = s.noiseEnabled; n["db"] = s.noiseDb; n["pct"] = s.noisePct; n["holdS"] = s.noiseHoldS; n["micCal"] = s.micCal;

    JsonObject f = o["fans"].to<JsonObject>();
    f["balance"] = s.balance;     f["minDuty"] = s.fanMinDuty;

    JsonObject m = o["mode"].to<JsonObject>();
    m["boostMin"] = s.boostMin;   m["manualOpen"] = s.manualOpen; m["manualPct"] = s.manualPct;

    JsonObject d = o["damper"].to<JsonObject>();
    d["encZero"] = s.encZero;     d["openDeg"] = s.openDeg;
    d["motorDir"] = s.motorDir;   d["motorSpeed"] = s.motorSpeed;

    JsonObject w = o["net"].to<JsonObject>();
    w["host"] = s.host;           w["tz"] = s.tz;
}

void SettingsFromJson(Settings* s, JsonObjectConst o)
{
    JsonObjectConst c = o["co2"];
    if (c)
    {
        JsonArrayConst cp = c["curvePpm"], cq = c["curvePct"];
        if (cp.size() == CURVE_POINTS && cq.size() == CURVE_POINTS)
        {
            uint16_t prev = 0;
            for (int i = 0; i < CURVE_POINTS; i++)      // ascending ppm, at least 10 ppm apart
            {
                uint16_t p = constrain(cp[i].as<int>(), 400, 5000);
                s->curvePpm[i] = prev = (i && p < prev + 10) ? prev + 10 : p;
                s->curvePct[i] = constrain(cq[i].as<int>(), 0, 100);
            }
        }
        num(c, "openPpm", &s->openPpm, 400, 5000);
        num(c, "closePpm", &s->closePpm, 400, 5000);
        if (s->closePpm >= s->openPpm)
            s->closePpm = s->openPpm - 10;
        num(c, "maxPpm", &s->maxPpm, 600, 5000);
        num(c, "targetLo", &s->targetLo, 400, 5000);
        num(c, "targetHi", &s->targetHi, 400, 5000);
        num(c, "minOpenS", &s->minOpenS, 0, 3600);
        num(c, "minClosedS", &s->minClosedS, 0, 3600);
        num(c, "minFanPct", &s->minFanPct, 0, 100);
    }

    JsonObjectConst t = o["temp"];
    if (t)
    {
        flag(t, "enabled", &s->tempEnabled);
        num(t, "tinMin", &s->tinMin, 5, 35);
        num(t, "tinMax", &s->tinMax, 5, 40);
        num(t, "coldT0", &s->coldT[0], -40, 30);
        num(t, "coldPct0", &s->coldPct[0], 0, 100);
        num(t, "coldT1", &s->coldT[1], -40, 30);
        num(t, "coldPct1", &s->coldPct[1], 0, 100);
        if (s->coldT[1] <= s->coldT[0])
            s->coldT[1] = s->coldT[0] + 1;
        num(t, "closeBelowC", &s->closeBelowC, -50, 20);
        num(t, "coolDeltaC", &s->coolDeltaC, 0.5f, 15);
        num(t, "coolPct", &s->coolPct, 0, 100);
        num(t, "hotPct", &s->hotPct, 0, 100);
    }

    JsonObjectConst q = o["quiet"];
    if (q)
    {
        flag(q, "enabled", &s->quietEnabled);
        num(q, "start", &s->quietStart, 0, 1439);
        num(q, "end", &s->quietEnd, 0, 1439);
        num(q, "pct", &s->quietPct, 0, 100);
    }

    JsonObjectConst n = o["noise"];
    if (n)
    {
        flag(n, "enabled", &s->noiseEnabled);
        num(n, "db", &s->noiseDb, -90, 130);
        num(n, "pct", &s->noisePct, 0, 100);
        num(n, "holdS", &s->noiseHoldS, 0, 3600);
        num(n, "micCal", &s->micCal, -20, 150);
    }

    JsonObjectConst f = o["fans"];
    if (f)
    {
        num(f, "balance", &s->balance, -20, 20);
        num(f, "minDuty", &s->fanMinDuty, 0, 60);
    }

    JsonObjectConst m = o["mode"];
    if (m)
    {
        num(m, "boostMin", &s->boostMin, 1, 240);
        flag(m, "manualOpen", &s->manualOpen);
        num(m, "manualPct", &s->manualPct, 0, 100);
    }

    JsonObjectConst d = o["damper"];
    if (d)
    {
        num(d, "encZero", &s->encZero, 0, 4095);
        num(d, "openDeg", &s->openDeg, 30, 120);
        int dir = s->motorDir;
        num(d, "motorDir", &dir, -1, 1);
        s->motorDir = dir < 0 ? -1 : 1;
        num(d, "motorSpeed", &s->motorSpeed, 100, 3200);
    }

    JsonObjectConst w = o["net"];
    if (w)
    {
        text(w, "host", s->host, sizeof(s->host));
        text(w, "tz", s->tz, sizeof(s->tz));
    }
}

// --- NVS -------------------------------------------------------------------------------------------------------

void SettingsLoad()
{
    SettingsDefaults(&g_set);
    Preferences p;
    if (!p.begin("vent", true))
        return;
    String js = p.getString("cfg", "");
    g_set.mode = (Mode)p.getUChar("mode", MODE_AUTO);
    if (g_set.mode == MODE_BOOST)
        g_set.mode = MODE_AUTO;
    p.end();
    JsonDocument doc;
    if (js.length() && !deserializeJson(doc, js))
        SettingsFromJson(&g_set, doc.as<JsonObjectConst>());
}

bool SettingsSave()
{
    JsonDocument doc;
    SettingsToJson(g_set, doc.to<JsonObject>());
    String js;
    serializeJson(doc, js);
    Preferences p;
    if (!p.begin("vent", false))
        return false;
    bool ok = p.putString("cfg", js) == js.length();
    p.putUChar("mode", g_set.mode == MODE_BOOST ? MODE_AUTO : g_set.mode);
    p.end();
    return ok;
}
