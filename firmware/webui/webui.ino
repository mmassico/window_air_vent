// Window vent: the standalone application with its own web page on the home network (LAN).
//
// Every second: readings in (the sensors, or the simulation), the control logic (Control.cpp), the damper and the
// fans out, a record for the graphs (History.cpp), and the live state to every open page over a WebSocket (Web.cpp).
// Wi-Fi: Net.cpp (setup network on first start). Settings: Settings.cpp (saved in NVS).
//
// Serial console (115200 baud, USB-UART connector): help, info, wifi <ssid> <password>, wifi forget, sim on|off,
// reboot.
//
// Build: needs the WindowVent library (firmware/libs) and ArduinoJson 7.x; see firmware/README.md.
#include <ArduinoJson.h>
#include "Pins.h"
#include "Console.h"
#include "App.h"
#include "Settings.h"
#include "Control.h"
#include "Hw.h"
#include "Sim.h"
#include "History.h"
#include "Net.h"
#include "Web.h"
#include "Log.h"

#define CONTROL_MS   1000
#define SIM_MS       100
#define SIM_AUTO_MS  8000           // at boot, the simulation stays on unless the SCD40 answers within this

static Inputs   s_hwIn;             // the hardware's latest readings
static Inputs   s_in;               // what the control uses (hardware or simulation)
static Outputs  s_out;
static bool     s_reboot;
static bool     s_simChosen;        // the user switched the simulation: no automatic change any more
static uint32_t s_loopMaxUs;

// ------------------------------------------------------------------------------------------------
// Commands, from the web page (WebSocket or POST /api/cmd); called with the web lock held
// ------------------------------------------------------------------------------------------------

static const char* command(JsonObjectConst c)
{
    const char* cmd = c["cmd"] | "";

    if (!strcmp(cmd, "mode"))
    {
        const char* m = c["mode"] | "";
        Mode mode;
        if (!strcmp(m, "auto"))        mode = MODE_AUTO;
        else if (!strcmp(m, "manual")) mode = MODE_MANUAL;
        else if (!strcmp(m, "off"))    mode = MODE_OFF;
        else if (!strcmp(m, "boost"))  mode = MODE_BOOST;
        else return "unknown mode";
        ControlSetMode(mode);
        if (mode != MODE_BOOST && mode != g_set.mode)
        {
            g_set.mode = mode;
            SettingsSave();
        }
        Log("Mode: %s", m);
        return nullptr;
    }
    if (!strcmp(cmd, "manual"))     // {"open":true,"pct":50}: also switches to manual
    {
        if (c["open"].is<bool>()) g_set.manualOpen = c["open"];
        if (c["pct"].is<int>())   g_set.manualPct = constrain(c["pct"].as<int>(), 0, 100);
        ControlSetMode(MODE_MANUAL);
        g_set.mode = MODE_MANUAL;
        SettingsSave();
        return nullptr;
    }
    if (!strcmp(cmd, "sim"))
    {
        bool was = g_sim.on;
        SimFromJson(c);
        if (c["on"].is<bool>())
            s_simChosen = true;
        if (g_sim.on != was)
            Log("Simulation %s", g_sim.on ? "on" : "off");
        return nullptr;
    }
    if (!strcmp(cmd, "settings"))   // {"settings":{...}}, like POST /api/settings
    {
        SettingsFromJson(&g_set, c["settings"].as<JsonObjectConst>());
        SettingsSave();
        return nullptr;
    }
    if (!strcmp(cmd, "encZero"))    // the damper is closed now: take this encoder reading as 0 deg
    {
        HwStatus st;
        HwStatusGet(&st);
        if (!st.enc)
            return "no encoder";
        g_set.encZero = st.encRaw;
        SettingsSave();
        Log("Encoder zero set: raw %u", st.encRaw);
        return nullptr;
    }
    if (!strcmp(cmd, "forgetWifi"))
    {
        NetForget();
        return nullptr;
    }
    if (!strcmp(cmd, "reboot"))
    {
        s_reboot = true;
        return nullptr;
    }
    return "unknown command";
}

// ------------------------------------------------------------------------------------------------
// Live state for the web page
// ------------------------------------------------------------------------------------------------

static void num(JsonObject o, const char* key, bool ok, float v, int decimals)
{
    if (!ok)
        o[key] = nullptr;
    else
    {
        float k = decimals == 0 ? 1 : (decimals == 1 ? 10 : 100);
        o[key] = roundf(v * k) / k;
    }
}

static void broadcast()
{
    static uint32_t logSent;
    JsonDocument doc;
    HwStatus     hw;
    HwStatusGet(&hw);

    doc["type"]   = "state";
    doc["uptime"] = millis() / 1000;
    doc["clock"]  = roundf(HistClock() * 10) / 10;     // the history clock (model time while simulating faster)
    char tm[24];
    if (NetTimeText(tm, sizeof(tm)))
        doc["time"] = tm;
    doc["mode"]      = ControlModeName(ControlMode());
    doc["bootMode"]  = ControlModeName(g_set.mode);
    doc["boostLeft"] = ControlBoostLeftS();

    JsonObject in = doc["in"].to<JsonObject>();
    num(in, "co2", s_in.co2Ok, s_in.co2, 0);
    num(in, "tin", s_in.tinOk, s_in.tin, 1);
    num(in, "rh", s_in.rhOk, s_in.rh, 0);
    num(in, "tout", s_in.toutOk, s_in.tout, 1);
    num(in, "snd", s_in.sndOk, s_in.snd, 0);

    JsonObject out = doc["out"].to<JsonObject>();
    out["open"]    = s_out.open;
    num(out, "demand", true, s_out.demandPct, 0);
    num(out, "fan", true, s_out.fanPct, 0);
    num(out, "intake", true, s_out.intakePct, 0);
    num(out, "exhaust", true, s_out.exhaustPct, 0);
    out["limits"]  = s_out.limits;
    out["reason"]  = s_out.reason;
    num(out, "curve", s_in.co2Ok, ControlCurve(s_in.co2), 0);

    JsonObject d = doc["damper"].to<JsonObject>();
    float target = s_out.open ? g_set.openDeg : 0;
    if (g_sim.on)
    {
        num(d, "angle", true, g_sim.angle, 1);
        d["target"] = target;
        d["moving"] = fabsf(g_sim.angle - target) > 1;
        d["fault"]  = false;
    }
    else
    {
        num(d, "angle", hw.enc && hw.magnet, hw.angle, 1);
        d["target"] = hw.target;
        d["moving"] = hw.moving;
        d["fault"]  = hw.fault;
    }

    JsonArray fans = doc["fans"].to<JsonArray>();
    for (int i = 0; i < 2; i++)
    {
        JsonObject f = fans.add<JsonObject>();
        float pct = i ? s_out.exhaustPct : s_out.intakePct;
        f["pct"]  = roundf(pct);
        f["duty"] = g_sim.on ? HwDuty(pct) : hw.duty[i];
        f["rpm"]  = g_sim.on ? (int)g_sim.rpm[i] : hw.rpm[i];
    }

    JsonObject h = doc["hw"].to<JsonObject>();
    h["scd"] = hw.scd;   h["enc"] = hw.enc;   h["magnet"] = hw.magnet; h["tmc"] = hw.tmc;
    h["tout"] = hw.tout; h["tin"] = hw.tin;   h["mic"] = hw.mic;       h["encRaw"] = hw.encRaw;
    num(h, "v12", true, hw.v12, 1);
    num(h, "hwAngle", hw.enc, hw.angle, 1);
    h["audio"] = (bool)AUDIO_MODE;

    JsonObject n = doc["net"].to<JsonObject>();
    n["ssid"] = NetSsid(); n["ip"] = NetIp(); n["rssi"] = NetRssi();
    n["ap"] = NetApOn();   n["sta"] = NetStaOn(); n["host"] = g_set.host; n["clients"] = WebClients();

    JsonObject sys = doc["sys"].to<JsonObject>();
    sys["ver"]   = FW_VERSION;
    sys["heap"]  = ESP.getFreeHeap();
    sys["psram"] = ESP.getFreePsram();
    sys["loopMaxMs"] = s_loopMaxUs / 1000.0f;
    s_loopMaxUs = 0;

    SimToJson(doc["sim"].to<JsonObject>());

    // Log lines since the last broadcast (up to the ring's size).
    JsonArray lines = doc["log"].to<JsonArray>();
    doc["logEnd"] = LogCount();
    char line[LOG_LEN];
    for (uint32_t i = max(logSent, LogCount() > LOG_LINES ? LogCount() - LOG_LINES : 0); i < LogCount(); i++)
        if (LogLine(i, line))
            lines.add(line);
    logSent = LogCount();

    String js;
    serializeJson(doc, js);
    WebBroadcast(js.c_str());
}

// ------------------------------------------------------------------------------------------------
// Serial console
// ------------------------------------------------------------------------------------------------

static void console(int argc, char* argv[])
{
    const char* c = argv[0];
    if (!strcmp(c, "help"))
        Serial.print("help, info, wifi <ssid> <password>, wifi forget, sim on|off, reboot");
    else if (!strcmp(c, "info"))
        Serial.printf("%s %s. Wi-Fi: %s, %s (%s). Mode %s, simulation %s. %s",
                      FW_NAME, FW_VERSION, NetSsid().length() ? NetSsid().c_str() : "(none)",
                      NetStaOn() ? "joined" : "not joined", NetIp().c_str(), ControlModeName(ControlMode()),
                      g_sim.on ? "on" : "off", s_out.reason);
    else if (!strcmp(c, "wifi") && argc == 2 && !strcmp(argv[1], "forget"))
        NetForget();
    else if (!strcmp(c, "wifi") && argc >= 2)
        NetSetCredentials(argv[1], argc > 2 ? argv[2] : "");
    else if (!strcmp(c, "sim") && argc == 2)
    {
        WebLock();
        g_sim.on = !strcmp(argv[1], "on");
        s_simChosen = true;
        WebUnlock();
        Serial.printf("Simulation %s", g_sim.on ? "on" : "off");
    }
    else if (!strcmp(c, "reboot"))
        s_reboot = true;
    else
        Serial.print("Unknown command; 'help' lists them. (A network name with spaces: use the setup page.)");
}

// ------------------------------------------------------------------------------------------------
// Setup and loop
// ------------------------------------------------------------------------------------------------

void setup()
{
    Serial.begin(CONSOLE_BAUD);
    pinMode(PIN_LED, OUTPUT);
    HwBegin();                      // motor off first thing
    delay(500);
    Serial.printf("\r\n%s %s\r\n", FW_NAME, FW_VERSION);
    SettingsLoad();
    ControlBegin();
    SimBegin();
    HistBegin();
    NetBegin();                     // first: it starts the network stack the server's socket needs
    WebBegin(command);
    Log("Started; simulation on until the SCD40 answers");
    ConBegin(console, "Ready ('help' lists the commands).");
}

void loop()
{
    static uint32_t lastCtl, lastSim, lastBeat, t0 = micros();
    uint32_t now = millis();

    ConPoll();
    NetPoll();
    WebPoll();
    HwPoll(&s_hwIn);

    WebLock();
    if (!s_simChosen && now > SIM_AUTO_MS && g_sim.on)
    {
        HwStatus hw;
        HwStatusGet(&hw);
        s_simChosen = true;         // decided once
        if (hw.scd)
        {
            g_sim.on = false;
            Log("SCD40 answers: simulation off");
        }
    }

    if (now - lastSim >= SIM_MS)
    {
        float dt = (now - lastSim) / 1000.0f;
        lastSim = now;
        if (g_sim.on)
            SimStep(min(dt, 1.0f), s_out.open ? g_set.openDeg : 0, s_out.intakePct, s_out.exhaustPct);
    }

    if (now - lastCtl >= CONTROL_MS)
    {
        float dt = min((now - lastCtl) / 1000.0f, 5.0f);
        lastCtl = now;
        if (g_sim.on)
            SimInputs(&s_in);
        else
            s_in = s_hwIn;
        s_in.minuteOfDay = NetMinuteOfDay();
        float dtModel = g_sim.on && g_sim.model ? dt * g_sim.speed : dt;   // the control and the history follow model time
        ControlStep(s_in, dtModel, &s_out);
        if (g_sim.on)
        {
            HwSetFans(0, 0);        // the real fans stay off while simulating
            HistAdd(s_in, s_out.fanPct, g_sim.angle, dtModel);
        }
        else
        {
            HwSetFans(s_out.intakePct, s_out.exhaustPct);
            HwSetDamper(s_out.open ? g_set.openDeg : 0);
            HwStatus hw;
            HwStatusGet(&hw);
            HistAdd(s_in, s_out.fanPct, hw.enc ? max(0.0f, hw.angle) : 0, dtModel);
        }
        broadcast();
    }
    WebUnlock();

    if (now - lastBeat >= 500)      // heartbeat on the blue LED
    {
        lastBeat = now;
        digitalWrite(PIN_LED, !digitalRead(PIN_LED));
    }
    if (s_reboot)
    {
        Log("Restarting");
        delay(300);
        ESP.restart();
    }

    uint32_t t = micros();
    s_loopMaxUs = max(s_loopMaxUs, t - t0);
    t0 = t;
    delay(2);
}
