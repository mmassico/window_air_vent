// Window vent: bare-metal hardware validation.
//
// A serial command interpreter to check each part on its own: I2C buses, SCD40 CO2 sensor, AS5600 encoder,
// TMC2209 driver and stepper, fans, 12 V supply, DS18B20 temperature sensors. No WiFi, no control loop.
//
// Status: compiles, NOT TESTED ON HARDWARE YET.
//
// Board:   Freenove ESP32-S3-WROOM Lite (FNK0099), Arduino core esp32 3.x, "ESP32S3 Dev Module".
// Console: the board's USB-UART connector, 115200 baud. Pins are listed in Pins.h.

#include <Wire.h>
#include "Pins.h"
#include "Console.h"
#include "Scd40.h"
#include "As5600.h"
#include "Tmc2209.h"
#include "Fans.h"
#include "Ds18b20.h"

#define FW_NAME          "window-vent baremetal 1.1"
#define STEPS_PER_REV    200        // full steps per motor turn (1.8 deg)
#define DEF_MICROSTEPS   16
#define DEF_RUN_MA       500
#define DEF_HOLD_PCT     50
#define DEF_SPEED        800        // microsteps/s: at 16 microsteps, a quarter turn in 1 s

static TwoWire*  s_i2c[2] = { &Wire, &Wire1 };
static uint16_t s_encZero;          // raw AS5600 value taken as 0 deg ('enc zero')
static bool     s_tmcOk;
static const struct { const char* name; uint8_t pin; } s_temp[2] = { { "outdoor", PIN_TEMP_OUT }, { "indoor", PIN_TEMP_IN } };

static const char* HELP =
    "General\r\n"
    "  help                         this list\r\n"
    "  cls                          clear the screen\r\n"
    "  info                         chip, memory, 12 V, which devices answer\r\n"
    "  reboot                       restart the ESP32\r\n"
    "  led <r> <g> <b>              on-board RGB LED, 0-255 each\r\n"
    "  mon [ms]                     print every reading every ms (default 1000) until a key is pressed\r\n"
    "I2C (bus 0 = SCD40 on GPIO 8/9, bus 1 = AS5600 on GPIO 6/7)\r\n"
    "  i2c scan <bus>               list the addresses that answer\r\n"
    "  i2c rd <bus> <addr> <reg> [n]        read n bytes (default 1) from an 8-bit register\r\n"
    "  i2c wr <bus> <addr> <reg> <data>...  write bytes to an 8-bit register\r\n"
    "CO2 sensor (SCD40)\r\n"
    "  co2 start | stop             periodic measurement on (one reading every 5 s) or off\r\n"
    "  co2                          last reading: CO2 ppm, temperature, humidity\r\n"
    "  co2 serial                   serial number (stopped only)\r\n"
    "  co2 selftest                 10 s self-test (stopped only)\r\n"
    "  co2 frc <ppm>                forced recalibration to a known level, e.g. 420 outdoors (stopped only)\r\n"
    "Encoder (AS5600)\r\n"
    "  enc                          angle, magnet status, AGC, magnitude\r\n"
    "  enc zero                     take the present angle as 0 deg\r\n"
    "Motor (TMC2209 + stepper)\r\n"
    "  mot en <0|1>                 disable / enable the driver (EN pin)\r\n"
    "  mot step <n> [speed]         n microsteps (negative = reverse) with STEP/DIR, speed in microsteps/s\r\n"
    "  mot vel <speed>              turn with the driver's own step generator (UART), 0 stops\r\n"
    "  mot cur <mA> [hold%]         run current and hold current (percent of run)\r\n"
    "  mot ustep <n>                microsteps per full step: 1, 2, 4 ... 256\r\n"
    "  mot sgt <n>                  StallGuard threshold: DIAG goes high when SG_RESULT < 2 x n (0 = off)\r\n"
    "  tmc init                     redo the boot configuration (after powering 12 V)\r\n"
    "  tmc status                   version, interface counter, flags, StallGuard, DIAG pin\r\n"
    "  tmc rd <reg>                 read a register\r\n"
    "  tmc wr <reg> <value>         write a register\r\n"
    "Fans (0 = intake, 1 = exhaust)\r\n"
    "  fan                          duty and speed of both fans\r\n"
    "  fan <0|1|all> <duty%>        set the PWM duty\r\n"
    "Temperature (DS18B20: outdoor on GPIO 14, indoor on GPIO 21, optional)\r\n"
    "  temp                         read both (a conversion takes 0.75 s)\r\n"
    "  temp rom                     their 64-bit ROM codes (family 28)\r\n"
    "Numbers: 42, 0x2A, 2Ah, 0b101010 or 101010b.";

// ------------------------------------------------------------------------------------------------
// Helpers
// ------------------------------------------------------------------------------------------------

static float readSupply()
{
    return analogReadMilliVolts(PIN_12V_SENSE) * (V12_DIV_TOP + V12_DIV_BOTTOM) / V12_DIV_BOTTOM / 1000.0f;
}

static bool i2cPresent(TwoWire& bus, uint8_t addr)
{
    bus.beginTransmission(addr);
    return bus.endTransmission() == 0;
}

static float encDegrees(uint16_t raw)
{
    return As5600Degrees((raw - s_encZero) & 0x0fff);
}

// Signed difference between two raw readings, assuming less than half a turn between them.
static int encDelta(uint16_t from, uint16_t to)
{
    return ((int)(to - from + 2048) & 0x0fff) - 2048;
}

static bool needTmc()
{
    if (!s_tmcOk)
        Serial.print("Driver not configured: power 12 V, then 'tmc init'.");
    return s_tmcOk;
}

static void tmcInit()
{
    s_tmcOk = Tmc2209Init(DEF_MICROSTEPS, DEF_RUN_MA, DEF_HOLD_PCT);
    if (s_tmcOk)
        Serial.printf("TMC2209: OK, %d microsteps, %d mA run, %d%% hold, StealthChop.",
                      DEF_MICROSTEPS, Tmc2209GetCurrent(), DEF_HOLD_PCT);
    else
        Serial.print("TMC2209: no answer on the UART (12 V off, or wiring).");
}

// ------------------------------------------------------------------------------------------------
// Commands
// ------------------------------------------------------------------------------------------------

static void cmdInfo()
{
    Serial.printf("%s, built %s %s\r\n", FW_NAME, __DATE__, __TIME__);
    uint64_t mac = ESP.getEfuseMac();
    Serial.printf("Chip:    %s rev %d, %d cores, %lu MHz, MAC %02X:%02X:%02X:%02X:%02X:%02X\r\n", ESP.getChipModel(),
                  ESP.getChipRevision(), ESP.getChipCores(), (unsigned long)ESP.getCpuFreqMHz(), (int)(mac & 0xff),
                  (int)(mac >> 8 & 0xff), (int)(mac >> 16 & 0xff), (int)(mac >> 24 & 0xff), (int)(mac >> 32 & 0xff),
                  (int)(mac >> 40 & 0xff));
    Serial.printf("Memory:  flash %lu MB, PSRAM %lu MB, free heap %lu kB\r\n", (unsigned long)(ESP.getFlashChipSize() >> 20),
                  (unsigned long)(ESP.getPsramSize() >> 20), (unsigned long)(ESP.getFreeHeap() >> 10));
    Serial.printf("Uptime:  %lu s\r\n", (unsigned long)(millis() / 1000));
    Serial.printf("Supply:  %.2f V\r\n", readSupply());
    Serial.printf("SCD40:   %s (bus 0, 0x62)\r\n", i2cPresent(Wire, SCD40_ADDR) ? "answers" : "absent");
    Serial.printf("AS5600:  %s (bus 1, 0x36)\r\n", i2cPresent(Wire1, AS5600_ADDR) ? "answers" : "absent");
    for (int i = 0; i < 2; i++)
        Serial.printf("DS18B20: %s %s (GPIO %d)\r\n", s_temp[i].name, Ds18b20Present(s_temp[i].pin) ? "answers" : "absent",
                      s_temp[i].pin);
    uint32_t ioin;
    if (Tmc2209Read(TMC_IOIN, &ioin))
        Serial.printf("TMC2209: answers, version 0x%02lX (expected 0x21)", (unsigned long)(ioin >> 24));
    else
        Serial.print("TMC2209: no answer");
}

static void cmdI2c(int argc, char* argv[])
{
    long bus, addr, reg, n;
    if (argc < 3 || !ConArgInt(argc, argv, 2, &bus))
    {
        if (argc < 3) Serial.print("Usage: i2c scan|rd|wr <bus> ...");
        return;
    }
    if (bus < 0 || bus > 1)
    {
        Serial.print("Bus is 0 or 1.");
        return;
    }
    TwoWire& w = *s_i2c[bus];

    if (strcmp(argv[1], "scan") == 0)
    {
        int found = 0;
        for (int a = 1; a < 127; a++)
            if (i2cPresent(w, a))
                Serial.printf("%s0x%02X", found++ ? ", " : "Found: ", a);
        if (!found)
            Serial.print("Nothing answers (pull-ups? power? wiring?)");
    }
    else if (strcmp(argv[1], "rd") == 0)
    {
        if (!ConArgInt(argc, argv, 3, &addr) || !ConArgInt(argc, argv, 4, &reg))
            return;
        n = 1;
        if (argc > 5 && !ConArgInt(argc, argv, 5, &n))
            return;
        n = constrain(n, 1, 32);
        w.beginTransmission(addr);
        w.write(reg);
        if (w.endTransmission(false) != 0 || w.requestFrom((uint8_t)addr, (uint8_t)n) != n)
        {
            Serial.print("ERR (no ACK)");
            return;
        }
        Serial.printf("0x%02lX:", (unsigned long)reg);
        for (int i = 0; i < n; i++)
            Serial.printf(" %02X", w.read());
    }
    else if (strcmp(argv[1], "wr") == 0)
    {
        if (!ConArgInt(argc, argv, 3, &addr) || !ConArgInt(argc, argv, 4, &reg) || argc < 6)
        {
            if (argc < 6) Serial.print("Usage: i2c wr <bus> <addr> <reg> <data>...");
            return;
        }
        w.beginTransmission(addr);
        w.write(reg);
        for (int i = 5; i < argc; i++)
        {
            long d;
            if (!ConArgInt(argc, argv, i, &d))
                return;
            w.write((uint8_t)d);
        }
        Serial.print(w.endTransmission() == 0 ? "OK" : "ERR (no ACK)");
    }
    else
        Serial.print("Usage: i2c scan|rd|wr <bus> ...");
}

static void cmdCo2(int argc, char* argv[])
{
    const char* sub = argc > 1 ? argv[1] : "";

    if (strcmp(sub, "start") == 0)
        Serial.print(Scd40StartPeriodic() ? "Started: first reading in 5 s." : "ERR");
    else if (strcmp(sub, "stop") == 0)
        Serial.print(Scd40StopPeriodic() ? "Stopped." : "ERR");
    else if (strcmp(sub, "serial") == 0)
    {
        uint64_t sn;
        if (Scd40IsRunning()) { Serial.print("Run 'co2 stop' first."); return; }
        if (Scd40Serial(&sn))
            Serial.printf("Serial: 0x%04X%08lX", (unsigned)(sn >> 32), (unsigned long)(sn & 0xffffffff));
        else
            Serial.print("ERR");
    }
    else if (strcmp(sub, "selftest") == 0)
    {
        bool pass;
        if (Scd40IsRunning()) { Serial.print("Run 'co2 stop' first."); return; }
        Serial.print("Self-test, 10 s...");
        if (Scd40SelfTest(&pass))
            Serial.print(pass ? " passed." : " FAILED.");
        else
            Serial.print(" ERR");
    }
    else if (strcmp(sub, "frc") == 0)
    {
        long ppm;
        int  corr;
        if (Scd40IsRunning()) { Serial.print("Run 'co2 stop' first (after at least 3 min of 'co2 start' at that level)."); return; }
        if (!ConArgInt(argc, argv, 2, &ppm))
            return;
        if (Scd40ForcedRecal((uint16_t)ppm, &corr))
            Serial.printf("Recalibrated to %ld ppm, correction %+d ppm.", ppm, corr);
        else
            Serial.print("ERR (sensor must have run 3 min before 'co2 stop').");
    }
    else if (argc == 1)
    {
        bool ready;
        Scd40Reading r;
        if (!Scd40IsRunning()) { Serial.print("Not running: 'co2 start'."); return; }
        if (!Scd40DataReady(&ready)) { Serial.print("ERR"); return; }
        if (!ready) { Serial.print("No new reading yet (one every 5 s)."); return; }
        if (Scd40Read(&r))
            Serial.printf("CO2 %u ppm, %.1f C, %.1f %%RH", r.co2, r.tempC, r.rh);
        else
            Serial.print("ERR");
    }
    else
        Serial.print("Usage: co2 [start|stop|serial|selftest|frc <ppm>]");
}

static void cmdEnc(int argc, char* argv[])
{
    As5600Reading r;
    if (!As5600Read(&r))
    {
        Serial.print("ERR (AS5600 not answering on bus 1)");
        return;
    }
    if (argc > 1 && strcmp(argv[1], "zero") == 0)
    {
        s_encZero = r.raw;
        Serial.printf("Zero set at raw %u.", r.raw);
        return;
    }
    Serial.printf("Angle %.2f deg (raw %u), magnet %s, AGC %u, magnitude %u",
                  encDegrees(r.raw), r.raw, As5600MagnetText(r.status), r.agc, r.magnitude);
}

// Blocking move with STEP/DIR and a linear speed ramp; any key aborts. The encoder is sampled on the way
// so the reported rotation is right even over several turns.
static void motorStep(long n, long speed)
{
    const long start = max(50L, speed / 8);
    const long accel = speed * 4;                   // full speed in a quarter second
    bool       rev   = n < 0;
    long       total = labs(n), done = 0;
    uint16_t   encPrev = 0, enc;
    long       encSum  = 0;
    bool       haveEnc = As5600RawAngle(&encPrev);

    if (digitalRead(PIN_TMC_EN))
        Serial.print("Note: driver disabled ('mot en 1'), the motor will not turn.\r\n");
    digitalWrite(PIN_TMC_DIR, rev ? HIGH : LOW);
    delayMicroseconds(5);

    uint32_t t = micros();
    for (; done < total; done++)
    {
        long  left = total - done;
        float v    = min((float)speed, min(sqrtf((float)start * start + 2.0f * accel * done),
                                           sqrtf((float)start * start + 2.0f * accel * left)));
        uint32_t period = (uint32_t)(1e6f / v);

        digitalWrite(PIN_TMC_STEP, HIGH);
        delayMicroseconds(2);
        digitalWrite(PIN_TMC_STEP, LOW);

        if ((done & 63) == 63)
        {
            if (haveEnc && As5600RawAngle(&enc)) { encSum += encDelta(encPrev, enc); encPrev = enc; }
            if (ConKeyHit()) { done++; Serial.print("Aborted. "); break; }
        }
        while (micros() - t < period)
            ;
        t += period;
    }

    int   ustep    = Tmc2209GetMicrosteps();
    float expected = done * 360.0f / (STEPS_PER_REV * (float)(ustep ? ustep : DEF_MICROSTEPS));
    Serial.printf("%ld microsteps, expected %.1f deg", rev ? -done : done, rev ? -expected : expected);
    if (haveEnc && As5600RawAngle(&enc))
    {
        encSum += encDelta(encPrev, enc);
        Serial.printf(", encoder %+.1f deg", encSum * 360.0f / 4096.0f);
    }
}

static void cmdMot(int argc, char* argv[])
{
    const char* sub = argc > 1 ? argv[1] : "";
    long a, b;

    if (strcmp(sub, "en") == 0)
    {
        if (!ConArgInt(argc, argv, 2, &a))
            return;
        digitalWrite(PIN_TMC_EN, a ? LOW : HIGH);
        Serial.print(a ? "Driver enabled." : "Driver disabled.");
    }
    else if (strcmp(sub, "step") == 0)
    {
        if (!needTmc() || !ConArgInt(argc, argv, 2, &a))
            return;
        b = DEF_SPEED;
        if (argc > 3 && !ConArgInt(argc, argv, 3, &b))
            return;
        if (b <= 0 || b > 20000) { Serial.print("Speed is 1 to 20000 microsteps/s."); return; }
        motorStep(a, b);
    }
    else if (strcmp(sub, "vel") == 0)
    {
        if (!needTmc() || !ConArgInt(argc, argv, 2, &a))
            return;
        if (Tmc2209SetVelocity(a))
            Serial.print(a ? "Turning (internal generator); 'mot vel 0' stops." : "Stopped.");
        else
            Serial.print("ERR");
    }
    else if (strcmp(sub, "cur") == 0)
    {
        if (!needTmc() || !ConArgInt(argc, argv, 2, &a))
            return;
        b = DEF_HOLD_PCT;
        if (argc > 3 && !ConArgInt(argc, argv, 3, &b))
            return;
        if (Tmc2209SetCurrent(a, b))
            Serial.printf("Run current %d mA (nearest step), hold %ld%%.", Tmc2209GetCurrent(), b);
        else
            Serial.print("ERR");
    }
    else if (strcmp(sub, "ustep") == 0)
    {
        if (!needTmc() || !ConArgInt(argc, argv, 2, &a))
            return;
        if (Tmc2209SetMicrosteps(a))
            Serial.printf("%ld microsteps per full step.", a);
        else
            Serial.print("ERR (1, 2, 4, 8, 16, 32, 64, 128 or 256)");
    }
    else if (strcmp(sub, "sgt") == 0)
    {
        if (!needTmc() || !ConArgInt(argc, argv, 2, &a))
            return;
        Serial.print(Tmc2209Write(TMC_SGTHRS, constrain(a, 0, 255)) ? "OK" : "ERR");
    }
    else
        Serial.print("Usage: mot en|step|vel|cur|ustep|sgt ...");
}

static void cmdTmc(int argc, char* argv[])
{
    const char* sub = argc > 1 ? argv[1] : "";
    long     reg, val;
    uint32_t v;

    if (strcmp(sub, "init") == 0)
        tmcInit();
    else if (strcmp(sub, "rd") == 0)
    {
        if (!ConArgInt(argc, argv, 2, &reg))
            return;
        if (Tmc2209Read(reg, &v))
            Serial.printf("0x%02lX = 0x%08lX (%lu)", (unsigned long)reg, (unsigned long)v, (unsigned long)v);
        else
            Serial.print("ERR (no answer)");
    }
    else if (strcmp(sub, "wr") == 0)
    {
        if (!ConArgInt(argc, argv, 2, &reg) || !ConArgInt(argc, argv, 3, &val))
            return;
        Serial.print(Tmc2209Write(reg, (uint32_t)val) ? "OK (check that IFCNT went up: 'tmc status')" : "ERR");
    }
    else if (strcmp(sub, "status") == 0)
    {
        uint32_t ioin, ifcnt, gstat, drv, sg;
        if (!Tmc2209Read(TMC_IOIN, &ioin) || !Tmc2209Read(TMC_IFCNT, &ifcnt) || !Tmc2209Read(TMC_GSTAT, &gstat) ||
            !Tmc2209Read(TMC_DRV_STATUS, &drv) || !Tmc2209Read(TMC_SG_RESULT, &sg))
        {
            Serial.print("ERR (no answer on the UART: 12 V off, or wiring)");
            return;
        }
        Serial.printf("Version 0x%02lX, IFCNT %lu (writes received), GSTAT 0x%lX%s\r\n", (unsigned long)(ioin >> 24),
                      (unsigned long)(ifcnt & 0xff), (unsigned long)gstat,
                      (gstat & 2) ? " DRIVER ERROR" : (gstat & 1) ? " (reset since last init)" : "");
        Serial.printf("Pins: EN %s, DIAG %d. Current scale %lu/31, %s, %s\r\n",
                      digitalRead(PIN_TMC_EN) ? "high (disabled)" : "low (enabled)", digitalRead(PIN_TMC_DIAG),
                      (unsigned long)((drv >> 16) & 0x1f), (drv & (1UL << 30)) ? "StealthChop" : "SpreadCycle",
                      (drv & (1UL << 31)) ? "standstill" : "moving");
        Serial.printf("Flags:%s%s%s%s%s%s%s%s", (drv & 1) ? " overtemp-warning" : "", (drv & 2) ? " OVERTEMP" : "",
                      (drv & 0x0c) ? " SHORT-TO-GND" : "", (drv & 0x30) ? " SHORT-TO-SUPPLY" : "",
                      (drv & 0x40) ? " open-load-A" : "", (drv & 0x80) ? " open-load-B" : "",
                      (drv & 0xff) ? "" : " none", "\r\n");
        Serial.printf("StallGuard: SG_RESULT %lu (meaningful while turning; lower = more load)", (unsigned long)sg);
    }
    else
        Serial.print("Usage: tmc init|status|rd <reg>|wr <reg> <value>");
}

static void cmdFan(int argc, char* argv[])
{
    long duty;
    if (argc == 1)
    {
        for (int i = 0; i < FAN_COUNT; i++)
            Serial.printf("%sFan %d (%s): %d%%, %d rpm", i ? "\r\n" : "", i, i ? "exhaust" : "intake",
                          FansGetDuty(i), FansRpm(i));
        return;
    }
    if (!ConArgInt(argc, argv, 2, &duty))
        return;
    if (strcmp(argv[1], "all") == 0)
    {
        for (int i = 0; i < FAN_COUNT; i++)
            FansSetDuty(i, duty);
    }
    else
    {
        long fan;
        if (!ConParseInt(argv[1], &fan) || fan < 0 || fan >= FAN_COUNT) { Serial.print("Fan is 0, 1 or all."); return; }
        FansSetDuty(fan, duty);
    }
    Serial.print("OK (speed settles in a second or two: 'fan')");
}

static void cmdTemp(int argc, char* argv[])
{
    if (argc > 1 && strcmp(argv[1], "rom") == 0)
    {
        for (int i = 0; i < 2; i++)
        {
            uint8_t rom[8];
            Serial.printf("%-7s (GPIO %2d): ", s_temp[i].name, s_temp[i].pin);
            if (Ds18b20Rom(s_temp[i].pin, rom))
                Serial.printf("family %02X, serial %02X%02X%02X%02X%02X%02X%s", rom[0], rom[6], rom[5], rom[4], rom[3], rom[2],
                              rom[1], rom[0] == 0x28 ? "" : " (not a DS18B20?)");
            else
                Serial.print("no answer, or bad CRC");
            if (i == 0)
                Serial.print("\r\n");
        }
        return;
    }
    bool started[2];
    for (int i = 0; i < 2; i++)
        started[i] = Ds18b20Start(s_temp[i].pin);
    delay(800);
    for (int i = 0; i < 2; i++)
    {
        float         t;
        Ds18b20Status st = started[i] ? Ds18b20Read(s_temp[i].pin, &t) : DS18B20_ABSENT;
        Serial.printf("%-7s (GPIO %2d): ", s_temp[i].name, s_temp[i].pin);
        if (st == DS18B20_OK)
            Serial.printf("%6.2f C", t);
        else
            Serial.print(Ds18b20Text(st));
        if (i == 0)
            Serial.print("\r\n");
    }
}

static void cmdMon(int argc, char* argv[])
{
    long         ms = 1000;
    Scd40Reading co2 = {};
    bool         haveCo2 = false;
    float        temp[2];
    bool         haveTemp[2] = { false, false };
    uint32_t     tempStart = 0;
    bool         tempBusy = false;

    if (argc > 1 && !ConArgInt(argc, argv, 1, &ms))
        return;
    ms = max(ms, 100L);
    Serial.print("Press any key to stop.\r\n");
    while (!ConKeyHit())
    {
        bool          ready;
        As5600Reading enc;
        uint32_t      sg;

        if (Scd40IsRunning() && Scd40DataReady(&ready) && ready && Scd40Read(&co2))
            haveCo2 = true;
        if (haveCo2)
            Serial.printf("CO2 %4u ppm %4.1f C %4.1f %% | ", co2.co2, co2.tempC, co2.rh);
        else
            Serial.print(Scd40IsRunning() ? "CO2 waiting...          | " : "CO2 off ('co2 start')   | ");
        if (As5600Read(&enc))
            Serial.printf("enc %6.2f deg %-10s | ", encDegrees(enc.raw), As5600MagnetText(enc.status));
        else
            Serial.print("enc ---                   | ");
        if (!tempBusy || millis() - tempStart >= 800)   // DS18B20: read the last conversion, start the next
        {
            for (int i = 0; i < 2; i++)
                haveTemp[i] = tempBusy && Ds18b20Read(s_temp[i].pin, &temp[i]) == DS18B20_OK;
            for (int i = 0; i < 2; i++)
                Ds18b20Start(s_temp[i].pin);
            tempStart = millis();
            tempBusy = true;
        }
        if (haveTemp[0])
            Serial.printf("out %5.1f ", temp[0]);
        else
            Serial.print("out   --- ");
        if (haveTemp[1])
            Serial.printf("in %5.1f C | ", temp[1]);
        else
            Serial.print("in   --- C | ");
        Serial.printf("fans %4d %4d rpm | ", FansRpm(0), FansRpm(1));
        if (Tmc2209Read(TMC_SG_RESULT, &sg))
            Serial.printf("SG %3lu DIAG %d | ", (unsigned long)sg, digitalRead(PIN_TMC_DIAG));
        else
            Serial.print("SG ---       | ");
        Serial.printf("%.2f V\r\n", readSupply());

        uint32_t t0 = millis();
        while (millis() - t0 < (uint32_t)ms && !Serial.available())
            delay(10);
    }
    Serial.print("Stopped.");
}

static void handleCommand(int argc, char* argv[])
{
    const char* c = argv[0];

    if (strcmp(c, "help") == 0 || strcmp(c, "h") == 0 || strcmp(c, "?") == 0) Serial.print(HELP);
    else if (strcmp(c, "info") == 0) cmdInfo();
    else if (strcmp(c, "reboot") == 0) { Serial.print("Restarting...\r\n"); Serial.flush(); ESP.restart(); }
    else if (strcmp(c, "led") == 0)
    {
        long r, g, b;
        if (ConArgInt(argc, argv, 1, &r) && ConArgInt(argc, argv, 2, &g) && ConArgInt(argc, argv, 3, &b))
            rgbLedWrite(PIN_RGB, r, g, b);
    }
    else if (strcmp(c, "mon") == 0) cmdMon(argc, argv);
    else if (strcmp(c, "i2c") == 0) cmdI2c(argc, argv);
    else if (strcmp(c, "co2") == 0) cmdCo2(argc, argv);
    else if (strcmp(c, "enc") == 0) cmdEnc(argc, argv);
    else if (strcmp(c, "mot") == 0) cmdMot(argc, argv);
    else if (strcmp(c, "tmc") == 0) cmdTmc(argc, argv);
    else if (strcmp(c, "fan") == 0) cmdFan(argc, argv);
    else if (strcmp(c, "temp") == 0) cmdTemp(argc, argv);
    else Serial.printf("Unknown command '%s', type 'help'.", c);
}

// ------------------------------------------------------------------------------------------------
// Setup and loop
// ------------------------------------------------------------------------------------------------

void setup()
{
    // Motor off first thing.
    pinMode(PIN_TMC_EN, OUTPUT);
    digitalWrite(PIN_TMC_EN, HIGH);
    pinMode(PIN_TMC_STEP, OUTPUT);
    digitalWrite(PIN_TMC_STEP, LOW);
    pinMode(PIN_TMC_DIR, OUTPUT);
    digitalWrite(PIN_TMC_DIR, LOW);
    pinMode(PIN_TMC_DIAG, INPUT);
    pinMode(PIN_LED, OUTPUT);

    FansBegin();
    Ds18b20Begin(PIN_TEMP_OUT);
    Ds18b20Begin(PIN_TEMP_IN);
    analogReadResolution(12);

    Serial.begin(CONSOLE_BAUD);
    Serial1.begin(TMC_UART_BAUD, SERIAL_8N1, PIN_TMC_RX, PIN_TMC_TX);
    Wire.begin(PIN_SCD_SDA, PIN_SCD_SCL, SCD_I2C_HZ);
    Wire1.begin(PIN_ENC_SDA, PIN_ENC_SCL, ENC_I2C_HZ);
    Scd40Begin(&Wire);
    As5600Begin(&Wire1);
    Tmc2209Begin(&Serial1, TMC_ADDR, TMC_RSENSE);

    delay(1000);                    // SCD40 needs 1 s after power-up; also lets the terminal attach
    Serial.printf("\r\n%s\r\n", FW_NAME);
    tmcInit();
    ConBegin(handleCommand, "Ready.");
}

void loop()
{
    static uint32_t s_beat;

    ConPoll();
    if (millis() - s_beat >= 500)   // heartbeat on the blue LED
    {
        s_beat = millis();
        digitalWrite(PIN_LED, !digitalRead(PIN_LED));
    }
}
