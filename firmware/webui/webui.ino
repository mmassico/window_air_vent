// Window vent: the standalone application with its own web page on the home network (LAN).
//
// Every second: readings in (the sensors, or the simulation), the control logic (Control.cpp), the damper and the
// fans out, a record for the graphs (History.cpp), and the live state to every open page over a WebSocket (Web.cpp).
// Wi-Fi: Net.cpp (setup network on first start). Settings: Settings.cpp (saved in NVS).
//
// Console: the same commands on the serial port (115200 baud, USB-UART connector) and over the Wi-Fi (POST
// /api/console, with the password; the Developer tab has a box for it). 'help' lists them. Firmware updates over
// the Wi-Fi: POST /update (Web.cpp); a new firmware confirms itself once it is back on the Wi-Fi, or rolls back.
//
// Build: needs the WindowVent library (firmware/libs) and ArduinoJson 7.x; see firmware/README.md.
#include <ArduinoJson.h>
#include <Wire.h>
#include <esp_ota_ops.h>
#include "Pins.h"
#include "As5600.h"
#include "Tmc2209.h"
#include "Sound.h"
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
#define OTA_OK_MS    30000          // a new firmware confirms itself after this long on the Wi-Fi
#define OTA_GIVE_UP_MS (5 * 60 * 1000UL)    // ... or, not on the Wi-Fi by then, rolls back to the previous one
#define TEST_IDLE_MS (10 * 60 * 1000UL)     // test mode ends by itself after this long without a test command

static Inputs   s_hwIn;             // the hardware's latest readings
static Inputs   s_in;               // what the control uses (hardware or simulation)
static Outputs  s_out;
static bool     s_reboot;
static bool     s_simChosen;        // the user switched the simulation: no automatic change any more
static uint32_t s_loopMaxUs;
static bool     s_test;             // test mode: the console drives the fans and the damper, not the control
static uint32_t s_testAt;           // the last test command
static bool     s_otaPending;       // this firmware came by update and isn't confirmed yet

// The core checks a new firmware at boot unless this says the application will (it does, in the loop).
extern "C" bool verifyRollbackLater()
{
    return true;
}

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
    if (!strcmp(cmd, "damperCal"))  // the boundary test, as at boot
    {
        HwDamperCalibrate();
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
    num(h, "travel", hw.travel > 0, hw.travel, 1);
    h["audio"] = (bool)AUDIO_MODE;

    JsonObject n = doc["net"].to<JsonObject>();
    n["ssid"] = NetSsid(); n["ip"] = NetIp(); n["rssi"] = NetRssi();
    n["ap"] = NetApOn();   n["sta"] = NetStaOn(); n["host"] = g_set.host; n["clients"] = WebClients();

    JsonObject sys = doc["sys"].to<JsonObject>();
    sys["ver"]   = FW_VERSION;
    sys["heap"]  = ESP.getFreeHeap();
    sys["psram"] = ESP.getFreePsram();
    sys["loopMaxMs"] = s_loopMaxUs / 1000.0f;
    sys["test"]  = s_test;
    sys["pass"]  = WebPassIsSet();
    sys["otaPending"] = s_otaPending;
    s_loopMaxUs = 0;

    SimToJson(doc["sim"].to<JsonObject>());

    // Log lines since the last broadcast (up to the ring's size).
    JsonArray lines = doc["log"].to<JsonArray>();
    doc["logEnd"] = LogCount();
    char line[LOG_LEN];
    for (uint32_t i = max(max(logSent, LogFirst()), LogCount() > 50 ? LogCount() - 50 : 0); i < LogCount(); i++)
        if (LogLine(i, line))
            lines.add(line);
    logSent = LogCount();

    String js;
    serializeJson(doc, js);
    WebBroadcast(js.c_str());
}

// ------------------------------------------------------------------------------------------------
// Console: the same commands on the serial console and over the Wi-Fi (POST /api/console), run in the loop
// with the web lock held
// ------------------------------------------------------------------------------------------------

static const char* HELP =
    "help                        this list\n"
    "info                        firmware, reset reason, uptime, memory, Wi-Fi, mode\n"
    "status                      readings, control outputs, damper, fans, which parts answer\n"
    "log [n]                     the last n log lines (default 20)\n"
    "mode auto|manual|off|boost  as on the dashboard\n"
    "sim on|off                  the simulation\n"
    "test on|off                 test mode: the control stops driving the fans and the damper (off by\n"
    "                            itself after 10 min without a test command)\n"
    "fan <0|1|all> <duty%>       a fan's PWM duty, 0 = intake, 1 = exhaust (test mode)\n"
    "damper <deg>                move the damper to this angle from closed, with the encoder (test mode)\n"
    "damper cal                  boundary test: close until it stops, open until it stops (as at boot)\n"
    "enc                         encoder: raw, angle, magnet, AGC, magnitude\n"
    "enc zero                    the damper is closed: take this reading as 0 deg (until the next boundary\n"
    "                            test, at the next boot or damper cal)\n"
    "tmc                         TMC2209: version, interface counter, flags, StallGuard\n"
    "tmc rd <reg>                read a register\n"
    "tmc wr <reg> <value>        write a register (test mode)\n"
    "i2c scan <0|1>              the addresses that answer (0: SCD40 bus, 1: AS5600 bus)\n"
    "sound [ms]                  a fresh burst from the microphone (default 500 ms): dBA, dBFS, bias, clipping\n"
    "sound cal <dBA>             the sound is this level now (a sound level meter, A): sets micCal and saves\n"
    "wifi <ssid> <password>      join a network, name without spaces (serial only); wifi forget erases it\n"
    "pass <password>             the password of the web console and firmware updates; pass - removes it\n"
    "ota                         the firmware slots, and whether this one is confirmed\n"
    "reboot                      restart\n";

static bool     s_remote;           // the command came over the Wi-Fi

static const char* resetText(esp_reset_reason_t r)
{
    switch (r)
    {
    case ESP_RST_POWERON:   return "power-on";
    case ESP_RST_EXT:       return "reset pin";
    case ESP_RST_SW:        return "software restart";
    case ESP_RST_PANIC:     return "crash (panic)";
    case ESP_RST_INT_WDT:   return "interrupt watchdog";
    case ESP_RST_TASK_WDT:  return "task watchdog";
    case ESP_RST_WDT:       return "watchdog";
    case ESP_RST_DEEPSLEEP: return "deep sleep";
    case ESP_RST_BROWNOUT:  return "brown-out";
    case ESP_RST_USB:       return "USB";
    default:                return "other";
    }
}

static const char* otaText(esp_ota_img_states_t st)
{
    switch (st)
    {
    case ESP_OTA_IMG_NEW:            return "new";
    case ESP_OTA_IMG_PENDING_VERIFY: return "not confirmed yet";
    case ESP_OTA_IMG_VALID:          return "confirmed";
    case ESP_OTA_IMG_INVALID:        return "rejected";
    case ESP_OTA_IMG_ABORTED:        return "rolled back";
    default:                         return "flashed by USB";
    }
}

static bool testMode(Print& out)
{
    if (!s_test)
    {
        s_test = true;
        Log("Test mode on: the control no longer drives the fans and the damper");
        out.print("Test mode on (test off to leave it).\n");
    }
    s_testAt = millis();
    return true;
}

static void setTest(bool on)
{
    if (on == s_test)
        return;
    s_test = on;
    s_testAt = millis();
    Log(on ? "Test mode on: the control no longer drives the fans and the damper"
           : "Test mode off: the control drives the fans and the damper again");
}

static bool argInt(int argc, char* argv[], int i, long* v, Print& out)
{
    if (i < argc && ConParseInt(argv[i], v))
        return true;
    out.printf("%s: a number is missing or wrong\n", argv[0]);
    return false;
}

static void shell(int argc, char* argv[], Print& out)
{
    const char* c = argv[0];
    HwStatus    hw;
    HwStatusGet(&hw);

    if (!strcmp(c, "help"))
        out.print(HELP);

    else if (!strcmp(c, "info"))
    {
        const esp_partition_t* run = esp_ota_get_running_partition();
        esp_ota_img_states_t   st = ESP_OTA_IMG_UNDEFINED;
        esp_ota_get_state_partition(run, &st);
        uint32_t t = millis() / 1000;
        out.printf("%s %s, built %s %s, in %s (%s)\n", FW_NAME, FW_VERSION, __DATE__, __TIME__, run->label, otaText(st));
        out.printf("Up %lu d %02lu:%02lu:%02lu; last reset: %s\n", (unsigned long)(t / 86400),
                   (unsigned long)(t / 3600 % 24), (unsigned long)(t / 60 % 60), (unsigned long)(t % 60),
                   resetText(esp_reset_reason()));
        out.printf("Free: %u kB RAM (lowest %u kB), %u kB PSRAM\n", (unsigned)(ESP.getFreeHeap() / 1024),
                   (unsigned)(ESP.getMinFreeHeap() / 1024), (unsigned)(ESP.getFreePsram() / 1024));
        out.printf("Wi-Fi: %s, %s, %s (%d dBm), http://%s.local\n", NetSsid().length() ? NetSsid().c_str() : "(none)",
                   NetStaOn() ? "joined" : NetApOn() ? "setup network open" : "not joined", NetIp().c_str(),
                   NetRssi(), g_set.host);
        out.printf("Mode %s, simulation %s, test mode %s, password %s\n", ControlModeName(ControlMode()),
                   g_sim.on ? "on" : "off", s_test ? "on" : "off", WebPassIsSet() ? "set" : "not set");
        out.printf("%s\n", s_out.reason);
    }

    else if (!strcmp(c, "status"))
    {
        auto val = [&](const char* name, bool ok, float v, int dec, const char* unit, const char* sep) {
            if (ok) out.printf("%s %.*f %s%s", name, dec, v, unit, sep);
            else    out.printf("%s --%s", name, sep);
        };
        out.print(g_sim.on ? "Readings (simulation): " : "Readings: ");
        val("CO2", s_in.co2Ok, s_in.co2, 0, "ppm", ", ");
        val("indoor", s_in.tinOk, s_in.tin, 1, "C", ", ");
        val("RH", s_in.rhOk, s_in.rh, 0, "%", ", ");
        val("outdoor", s_in.toutOk, s_in.tout, 1, "C", ", ");
        val("sound", s_in.sndOk, s_in.snd, 0, "dB", "");
        out.printf("\nControl: mode %s, %s, demand %.0f %%, fans %.0f %% (intake %.0f, exhaust %.0f)%s\n",
                   ControlModeName(ControlMode()), s_out.open ? "open" : "closed", s_out.demandPct, s_out.fanPct,
                   s_out.intakePct, s_out.exhaustPct, s_test ? ", NOT APPLIED (test mode)" : "");
        out.printf("  %s\n", s_out.reason);
        if (hw.enc)
            out.printf("Damper: %.1f deg (raw %u, magnet %s), target %.1f, %s%s\n", hw.angle, hw.encRaw,
                       hw.magnet ? "ok" : "MISSING", hw.target,
                       hw.calibrating ? "boundary test running" : hw.moving ? "moving" : "still",
                       hw.fault ? ", FAULT (blocked or no progress)" : "");
        else
            out.printf("Damper: no encoder, target %.0f\n", hw.target);
        if (hw.travel > 0)
            out.printf("  stops: closed at raw %u (encZero), open %.1f deg further\n", g_set.encZero, hw.travel);
        else
            out.print("  stops: not measured (no boundary test yet, or it failed)\n");
        for (int i = 0; i < 2; i++)
            out.printf("Fan %d (%s): duty %d %%, %d rpm\n", i, i ? "exhaust" : "intake", hw.duty[i], hw.rpm[i]);
        out.printf("12 V: %.2f V\n", hw.v12);
        out.printf("Answering: SCD40 %s, AS5600 %s, TMC2209 %s, DS18B20 out %s, %s %s\n", hw.scd ? "yes" : "NO",
                   hw.enc ? "yes" : "NO", hw.tmc ? "yes" : "NO", hw.tout ? "yes" : "NO",
                   AUDIO_MODE ? "microphone" : "DS18B20 in", (AUDIO_MODE ? hw.mic : hw.tin) ? "yes" : "NO");
    }

    else if (!strcmp(c, "log"))
    {
        long n = 20;
        if (argc > 1 && !argInt(argc, argv, 1, &n, out))
            return;
        uint32_t end = LogCount(), k = n > 0 ? n : 0;
        uint32_t from = max(LogFirst(), end > k ? end - k : 0);
        char line[LOG_LEN];
        for (uint32_t i = from; i < end; i++)
            if (LogLine(i, line))
                out.printf("%s\n", line);
    }

    else if (!strcmp(c, "mode") && argc == 2)
    {
        JsonDocument d;
        d["cmd"] = "mode";
        d["mode"] = argv[1];
        const char* err = command(d.as<JsonObjectConst>());
        out.printf("%s\n", err ? err : "ok");
    }

    else if (!strcmp(c, "sim") && argc == 2)
    {
        bool on = !strcmp(argv[1], "on");
        if (on != g_sim.on)
            Log("Simulation %s", on ? "on" : "off");
        g_sim.on = on;
        s_simChosen = true;
        out.printf("Simulation %s\n", g_sim.on ? "on" : "off");
    }

    else if (!strcmp(c, "test") && argc == 2)
    {
        setTest(!strcmp(argv[1], "on"));
        out.printf("Test mode %s\n", s_test ? "on" : "off");
    }

    else if (!strcmp(c, "fan") && argc == 3)
    {
        long duty;
        if (!argInt(argc, argv, 2, &duty, out) || !testMode(out))
            return;
        bool all = !strcmp(argv[1], "all");
        for (int i = 0; i < 2; i++)
            if (all || atoi(argv[1]) == i)
                HwSetFanDuty(i, duty);
        out.printf("Fan %s: duty %ld %%\n", argv[1], constrain(duty, 0L, 100L));
    }

    else if (!strcmp(c, "damper") && argc == 2 && !strcmp(argv[1], "cal"))
    {
        HwDamperCalibrate();
        out.print("Boundary test started: closing, then opening, until each stop (the log follows it)\n");
    }

    else if (!strcmp(c, "damper") && argc == 2)
    {
        long deg;
        if (!argInt(argc, argv, 1, &deg, out) || !testMode(out))
            return;
        deg = constrain(deg, -10L, 120L);
        HwSetDamper(deg);
        HwDamperRetry();
        out.printf("Damper: to %ld deg (status shows where it is)\n", deg);
    }

    else if (!strcmp(c, "enc"))
    {
        if (argc == 2 && !strcmp(argv[1], "zero"))
        {
            JsonDocument d;
            d["cmd"] = "encZero";
            const char* err = command(d.as<JsonObjectConst>());
            out.printf("%s\n", err ? err : "ok: this angle is now 0 deg");
            return;
        }
        As5600Reading r;
        HwBusLock();
        bool ok = As5600Read(&r);
        HwBusUnlock();
        if (!ok)
            out.print("AS5600: no answer\n");
        else
            out.printf("AS5600: raw %u, %.1f deg from zero (raw %u), magnet: %s, AGC %u, magnitude %u\n", r.raw,
                       hw.angle, g_set.encZero, As5600MagnetText(r.status), r.agc, r.magnitude);
    }

    else if (!strcmp(c, "tmc"))
    {
        long reg, value;
        uint32_t v;
        if (argc >= 3 && !strcmp(argv[1], "rd"))
        {
            if (!argInt(argc, argv, 2, &reg, out))
                return;
            HwBusLock();
            bool ok = Tmc2209Read(reg, &v);
            HwBusUnlock();
            if (ok) out.printf("reg 0x%02lx = 0x%08lx\n", reg, (unsigned long)v);
            else    out.print("TMC2209: no answer\n");
        }
        else if (argc >= 4 && !strcmp(argv[1], "wr"))
        {
            if (!argInt(argc, argv, 2, &reg, out) || !argInt(argc, argv, 3, &value, out) || !testMode(out))
                return;
            HwBusLock();
            bool ok = Tmc2209Write(reg, value);
            HwBusUnlock();
            out.printf(ok ? "reg 0x%02lx <- 0x%08lx\n" : "reg 0x%02lx: write failed\n", reg, (unsigned long)value);
        }
        else
        {
            static const struct { uint8_t reg; const char* name; } regs[] = {
                { TMC_IOIN, "IOIN" }, { TMC_IFCNT, "IFCNT" }, { TMC_GSTAT, "GSTAT" }, { TMC_GCONF, "GCONF" },
                { TMC_CHOPCONF, "CHOPCONF" }, { TMC_DRV_STATUS, "DRV_STATUS" }, { TMC_SG_RESULT, "SG_RESULT" },
                { TMC_TSTEP, "TSTEP" } };
            HwBusLock();
            for (auto& x : regs)
            {
                if (Tmc2209Read(x.reg, &v))
                    out.printf("%-10s 0x%08lx%s\n", x.name, (unsigned long)v,
                               x.reg == TMC_IOIN ? (v >> 24 == 0x21 ? "  (version 0x21: TMC2209)" : "  (version?)") : "");
                else
                    out.printf("%-10s no answer\n", x.name);
            }
            HwBusUnlock();
            out.printf("EN pin %s, DIAG pin %s\n", digitalRead(PIN_TMC_EN) ? "high (driver off)" : "low (driver on)",
                       digitalRead(PIN_TMC_DIAG) ? "high" : "low");
        }
    }

    else if (!strcmp(c, "sound"))
    {
#if AUDIO_MODE
        SoundReading r;
        bool cal = argc == 3 && !strcmp(argv[1], "cal");
        long ms = 500;
        if (!cal && argc > 1 && !argInt(argc, argv, 1, &ms, out))
            return;
        SoundMeasure(ms, &r);
        if (cal)
        {
            g_set.micCal = atof(argv[2]) - r.dba;
            bool saved = SettingsSave();
            Log("Microphone calibrated: micCal %.1f dB%s", g_set.micCal, saved ? "" : ", NOT saved");
        }
        out.printf("%.1f dBFS A-weighted -> %.1f dBA (micCal %.1f); %.1f dBFS flat (150 Hz high-pass), bias %d mV, "
                   "peak to peak %d counts%s, %.0f samples/s\n", r.dba, r.dba + g_set.micCal, g_set.micCal, r.dbfs,
                   r.dcMv, r.p2p, r.clipped ? " CLIPPED" : "", r.rateHz);
#else
        out.print("sound: not in audio mode (AUDIO_MODE in Pins.h)\n");
#endif
    }

    else if (!strcmp(c, "i2c") && argc == 3 && !strcmp(argv[1], "scan"))
    {
        int bus = atoi(argv[2]);
        TwoWire* w = bus ? &Wire1 : &Wire;
        int n = 0;
        if (bus) HwBusLock();
        for (uint8_t a = 0x08; a < 0x78; a++)
        {
            w->beginTransmission(a);
            if (w->endTransmission() == 0)
            {
                out.printf("0x%02x ", a);
                n++;
            }
        }
        if (bus) HwBusUnlock();
        out.printf("%s(bus %d: %d found)\n", n ? "" : "nothing ", bus, n);
    }

    else if (!strcmp(c, "wifi") && argc >= 2)
    {
        if (s_remote)
            out.print("wifi: on the serial console only (a change would cut this connection)\n");
        else if (argc == 2 && !strcmp(argv[1], "forget"))
            NetForget();
        else
            NetSetCredentials(argv[1], argc > 2 ? argv[2] : "");
    }

    else if (!strcmp(c, "pass") && argc == 2)
    {
        bool off = !strcmp(argv[1], "-");
        if (!WebPassSet(off ? "" : argv[1]))
            out.print("not saved\n");
        else
        {
            Log("Password %s", off ? "removed" : "set");
            out.printf("Password %s\n", off ? "removed: the web console and updates are refused" : "set");
        }
    }

    else if (!strcmp(c, "ota"))
    {
        const esp_partition_t* run = esp_ota_get_running_partition();
        const esp_partition_t* other = esp_ota_get_next_update_partition(nullptr);
        esp_ota_img_states_t   st = ESP_OTA_IMG_UNDEFINED, ost = ESP_OTA_IMG_UNDEFINED;
        esp_app_desc_t         d;
        esp_ota_get_state_partition(run, &st);
        bool prev = other && esp_ota_get_partition_description(other, &d) == ESP_OK;
        if (prev)
            esp_ota_get_state_partition(other, &ost);
        out.printf("Running: %s, %s %s built %s %s, %s\n", run->label, FW_NAME, FW_VERSION, __DATE__, __TIME__,
                   otaText(st));
        out.printf("Other slot: %s, %s%s\n", other ? other->label : "none",
                   prev ? "a firmware, kept for a rollback until the next update overwrites it" : "empty",
                   prev && (ost == ESP_OTA_IMG_INVALID || ost == ESP_OTA_IMG_ABORTED) ? " (rejected)" : "");
        if (s_otaPending)
            out.print("This firmware confirms itself once on the Wi-Fi for 30 s; else it rolls back after 5 min.\n");
    }

    else if (!strcmp(c, "reboot"))
    {
        out.print("Restarting\n");
        s_reboot = true;
    }

    else
        out.print("Unknown command; 'help' lists them.\n");
}

// A command line from the web (POST /api/console): split, then run.
static void webShell(char* line, Print& out)
{
    char* argv[CON_ARGS_MAX];
    int   argc = 0;
    for (char* t = strtok(line, " \t"); t && argc < CON_ARGS_MAX; t = strtok(nullptr, " \t"))
        argv[argc++] = t;
    if (!argc)
        return;
    s_remote = true;
    shell(argc, argv, out);
    s_remote = false;
}

// The serial console's output: line ends as CR LF, and the last one left to the console's prompt.
class SerialOut : public Print
{
public:
    bool pending = false;
    size_t write(uint8_t ch) override
    {
        if (pending)
            Serial.print("\r\n");
        pending = ch == '\n';
        if (!pending)
            Serial.write(ch);
        return 1;
    }
};

static void console(int argc, char* argv[])
{
    SerialOut out;
    WebLock();
    shell(argc, argv, out);
    WebUnlock();
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
    esp_ota_img_states_t st;
    s_otaPending = esp_ota_get_state_partition(esp_ota_get_running_partition(), &st) == ESP_OK
                   && st == ESP_OTA_IMG_PENDING_VERIFY;
    SettingsLoad();
    ControlBegin();
    SimBegin();
    HistBegin();
    NetBegin();                     // first: it starts the network stack the server's socket needs
    WebBegin(command, webShell);
    Log("Started %s (last reset: %s)%s; simulation on until the SCD40 answers", FW_VERSION,
        resetText(esp_reset_reason()), s_otaPending ? ", new firmware, not confirmed yet" : "");
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

    if (s_otaPending)               // a new firmware: confirm it, or give it up
    {
        static bool     sta;
        static uint32_t staSince;
        if (!NetStaOn())
            sta = false;
        else if (!sta)
        {
            sta = true;
            staSince = now;
        }
        if (sta && now - staSince >= OTA_OK_MS)
        {
            esp_ota_mark_app_valid_cancel_rollback();
            s_otaPending = false;
            Log("New firmware confirmed");
        }
        else if (now >= OTA_GIVE_UP_MS)
        {
            Log("New firmware not on the Wi-Fi after 5 min: back to the previous one");
            delay(300);
            esp_ota_mark_app_invalid_rollback_and_reboot();
        }
    }

    WebLock();
    if (s_test && millis() - s_testAt >= TEST_IDLE_MS)   // not now: a console command may have set s_testAt since
        setTest(false);
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
            if (!s_test)
                HwSetFans(0, 0);    // the real fans stay off while simulating
            HistAdd(s_in, s_out.fanPct, g_sim.angle, dtModel);
        }
        else
        {
            if (!s_test)            // test mode: the console drives them
            {
                HwSetFans(s_out.intakePct, s_out.exhaustPct);
                HwSetDamper(s_out.open ? g_set.openDeg : 0);
            }
            HwStatus hw;
            HwStatusGet(&hw);
            HistAdd(s_in, s_out.fanPct, hw.enc ? max(0.0f, hw.angle) : 0, dtModel);
        }
        if (HwDamperCalSave())      // the boundary test changed encZero or motorDir
        {
            Log("Damper: encZero %u, motorDir %d %s", g_set.encZero, g_set.motorDir,
                SettingsSave() ? "saved" : "NOT saved");
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
