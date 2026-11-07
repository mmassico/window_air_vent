#include "Hw.h"
#include <Wire.h>
#include "Pins.h"
#include "Scd40.h"
#include "As5600.h"
#include "Tmc2209.h"
#include "Fans.h"
#include "Ds18b20.h"
#include "Sound.h"
#include "SoundStream.h"
#include "Log.h"

#define MICROSTEPS      16
#define RUN_MA          500
#define HOLD_PCT        50
#define ANGLE_TOL       1.0f        // degrees: close enough
#define SLOW_ZONE       15.0f       // degrees: slow down over the last part of a move
#define MOVE_TIMEOUT_MS 8000        // a quarter turn takes about 1 s
#define STALL_MS        600         // no progress toward the target for this long: the disc is stopped (at the
                                    //   slowest setting, 100 microsteps/s slowed to 15 %, 0.5 deg takes 0.3 s)
#define PROGRESS_DEG    0.5f        // ... progress meaning the closest approach so far improved by this much
#define SEATED_DEG      5.0f        // stopped this close to closed, closing: seated on the lips, not blocked
#define IDLE_OFF_MS     1500        // driver off this long after a move (the stepper's detent holds the damper)
#define CAL_TIMEOUT_MS  20000       // boundary test: no stop within this (a free disc, a slipping coupling): it fails
#define CAL_DIR_DEG     20.0f       // ... closing but the encoder went this far the other way: motorDir is inverted (not
                                    //   a few degrees: a disc already on the lips bounces back when the motor slips)
#define OPEN_MARGIN     2.0f        // the open target stays this far short of the open stop found by the test
#define CLOSE_PUSH      2.0f        // closing aims this far past the closed stop, so it seats on the lips

static HwStatus     s_st;
static portMUX_TYPE s_mux = portMUX_INITIALIZER_UNLOCKED;
static volatile float s_target;
static volatile bool  s_retry;                      // clear a fault and try the same target again
static volatile bool  s_calReq = true;              // run the boundary test (at boot, and on request)
static volatile bool  s_calSave;                    // the test changed encZero or motorDir: the loop saves them
static SemaphoreHandle_t s_bus;                     // the damper's buses (TMC2209 UART, AS5600 I2C): the damper
                                                    //   task holds it, the console takes it to read them

// --- damper task -----------------------------------------------------------------------------------------------

static float encAngle(uint16_t raw)
{
    float a = As5600Degrees((raw - g_set.encZero) & 0x0fff);
    return a > 180 ? a - 360 : a;                   // -180 to 180, closed = 0
}

// The boundary test: closes until the disc stops (the lips), then opens until it stops again, watching the encoder
// as for any move (no progress for STALL_MS: stopped). The closed stop becomes encZero, and the travel between the
// two stops caps the open angle. Closing first also checks the motor's direction: if the encoder goes the other
// way, motorDir is flipped and the test starts again.
struct Cal
{
    int      phase;                 // 0 idle, 1 closing, 2 opening
    uint32_t start, progressAt;
    uint16_t startRaw, prevRaw;
    int32_t  pos, best, closed;     // encoder counts from startRaw, unwrapped; best: furthest so far this phase
    bool     flipped;
    int8_t   dir0;                  // motorDir at the start: a test that fails puts it back
};

static float s_travel;              // degrees between the two stops, 0 until a test succeeded

// One step of the test: the velocity to command (0 when it ends).
static long calStep(Cal& c, uint16_t raw, uint32_t now)
{
    int32_t d = (int32_t)raw - c.prevRaw;
    if (d > 2048) d -= 4096;
    if (d < -2048) d += 4096;
    c.prevRaw = raw;
    c.pos += d;

    int sgn = c.phase == 1 ? -1 : 1;                // the way the encoder should go
    if (sgn * c.pos > c.best + (int32_t)(PROGRESS_DEG * 4096 / 360))
    {
        c.best = sgn * c.pos;
        c.progressAt = now;
    }
    if (c.phase == 1 && !c.flipped && c.pos > (int32_t)(CAL_DIR_DEG * 4096 / 360))
    {
        g_set.motorDir = -g_set.motorDir;           // for this test; saved only if it succeeds
        c.flipped = true;
        Log("Damper: the motor turns the other way: motorDir now %d; closing again", g_set.motorDir);
        c.start = c.progressAt = now;
        c.startRaw = raw;
        c.pos = c.best = 0;
    }
    else if (now - c.progressAt > STALL_MS)
    {
        if (c.phase == 1)
        {
            c.closed = -c.best;
            c.phase = 2;
            c.start = c.progressAt = now;
            c.best = c.pos;
            Log("Damper: closed stop at raw %u; opening until it stops",
                (unsigned)((c.startRaw + c.closed) & 0x0fff));
        }
        else
        {
            float travel = (c.best - c.closed) * 360.0f / 4096;
            if ((travel < 20 || travel > 200) && !c.flipped)
            {
                // Started near the open stop with motorDir inverted: too close to tell while closing. Once, the
                // other way.
                g_set.motorDir = -g_set.motorDir;
                c.flipped = true;
                Log("Damper: only %.1f deg between the stops: trying motorDir %d", travel, g_set.motorDir);
                c.phase = 1;
                c.start = c.progressAt = now;
                c.startRaw = raw;
                c.pos = c.best = 0;
                return -max(100L, (long)g_set.motorSpeed / 2) * g_set.motorDir;
            }
            c.phase = 0;
            if (travel < 20 || travel > 200)
            {
                g_set.motorDir = c.dir0;
                Log("Damper: boundary test failed: %.1f deg between the stops; settings kept", travel);
                return 0;
            }
            uint16_t zero = (c.startRaw + c.closed) & 0x0fff;
            if (abs(((int)zero - g_set.encZero + 2048) % 4096 - 2048) > 6)      // more than about 0.5 deg
                s_calSave = true;
            if (g_set.motorDir != c.dir0)
                s_calSave = true;
            g_set.encZero = zero;
            s_travel = travel;
            Log("Damper: boundary test done: closed at raw %u, %.1f deg to the open stop; opens to %.1f deg", zero,
                travel, min((float)g_set.openDeg, travel - OPEN_MARGIN));
            return 0;
        }
    }
    if (now - c.start > CAL_TIMEOUT_MS)
    {
        c.phase = 0;
        g_set.motorDir = c.dir0;
        Log("Damper: boundary test failed: no stop within %d s; settings kept", CAL_TIMEOUT_MS / 1000);
        return 0;
    }
    long speed = max(100L, (long)g_set.motorSpeed / 2);
    return speed * (c.phase == 1 ? -1 : 1) * g_set.motorDir;
}

static void damperTask(void*)
{
    uint32_t lastTry = 0, stopAt = 0, moveStart = 0, progressAt = 0;
    bool     tmc = false, enabled = false, moving = false, fault = false, seated = false;
    float    lastTarget = -999, bestErr = 0;
    long     lastV = 0;
    Cal      cal = {};

    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(10));
        HwBusLock();
        uint32_t now = millis();

        // The driver only answers with 12 V on: retry every 3 s until it does.
        if (!tmc && now - lastTry >= 3000)
        {
            lastTry = now;
            tmc = Tmc2209Init(MICROSTEPS, RUN_MA, HOLD_PCT);
            if (tmc)
                Log("TMC2209 configured: %d microsteps, %d mA", MICROSTEPS, RUN_MA);
        }

        As5600Reading r;
        bool enc = As5600Read(&r);
        if (!enc && !s_st.enc)
        {
            HwBusUnlock();
            vTaskDelay(pdMS_TO_TICKS(490));        // no encoder: look for it twice a second only
            HwBusLock();
        }
        bool magnet = enc && (r.status & 0x20);
        float angle = enc ? encAngle(r.raw) : 0;
        float target = s_target;
        if (s_travel > 0)                           // the boundary test found the stops: stay short of the open
            target = target <= ANGLE_TOL ? -CLOSE_PUSH : min(target, s_travel - OPEN_MARGIN);   // one, seat on the lips

        long v = 0;
        if (s_calReq && tmc && enc && magnet && !cal.phase)
        {
            s_calReq = false;
            cal = {};
            cal.phase = 1;
            cal.dir0 = g_set.motorDir;
            cal.start = cal.progressAt = now;
            cal.startRaw = cal.prevRaw = r.raw;
            Log("Damper: boundary test: closing until it stops");
        }
        if (cal.phase)
        {
            if (tmc && enc && magnet)
                v = calStep(cal, r.raw, now);
            else
            {
                cal.phase = 0;
                g_set.motorDir = cal.dir0;
                Log("Damper: boundary test stopped: the driver or the encoder no longer answers");
            }
            if (!cal.phase)                         // ended: move to the target afresh
            {
                lastTarget = -999;
                stopAt = now;
            }
        }

        if (target != lastTarget || s_retry)
        {
            s_retry = false;
            lastTarget = target;
            fault = false;
            seated = false;
            moveStart = now;
            if (moving)                             // a new move, even in mid-move: the stall check starts over,
            {                                       //   or it would measure progress against the old target
                moving = false;
                stopAt = now;
            }
        }
        if (seated && enc && angle > SEATED_DEG)    // pushed open since (airflow, a hand): close it again
            seated = false;

        if (cal.phase)
            moving = false;
        else if (tmc && enc && magnet && !fault && !seated)
        {
            float err = target - angle;
            if (fabsf(err) > ANGLE_TOL)
            {
                if (!moving)
                {
                    moving = true;
                    moveStart = now;
                    progressAt = now;
                    bestErr = fabsf(err);
                }
                float k = constrain(fabsf(err) / SLOW_ZONE, 0.15f, 1.0f);
                v = lroundf(g_set.motorSpeed * k) * (err > 0 ? 1 : -1) * g_set.motorDir;

                // The encoder watches the disc: it must keep getting closer. Against the lips the motor slips and
                // the disc bounces back a few degrees, so only a new closest approach counts as progress.
                if (fabsf(err) < bestErr - PROGRESS_DEG)
                {
                    bestErr = fabsf(err);
                    progressAt = now;
                }
                if (now - progressAt > STALL_MS)
                {
                    v = 0;
                    moving = false;
                    stopAt = now;
                    if (target <= ANGLE_TOL && angle < SEATED_DEG)      // (target -CLOSE_PUSH after a test)
                    {
                        seated = true;
                        Log("Damper: closed, seated on the lips at %.1f deg", angle);
                    }
                    else
                    {
                        fault = true;
                        Log("Damper: blocked at %.1f deg on the way to %.1f: stopped", angle, target);
                    }
                }
                else if (now - moveStart > MOVE_TIMEOUT_MS)
                {
                    fault = true;
                    v = 0;
                    Log("Damper: no progress toward %.0f deg (at %.1f): stopped", target, angle);
                }
            }
            else if (moving)
            {
                moving = false;
                stopAt = now;
            }
        }
        else
            moving = false;

        if (v != 0 && !enabled)
        {
            digitalWrite(PIN_TMC_EN, LOW);
            enabled = true;
        }
        if (tmc && v != lastV)
        {
            if (!Tmc2209SetVelocity(v))
                tmc = false;                        // 12 V gone: retry the init later
            lastV = v;
        }
        if (v == 0 && enabled && now - stopAt >= IDLE_OFF_MS)
        {
            digitalWrite(PIN_TMC_EN, HIGH);
            enabled = false;
        }
        HwBusUnlock();

        portENTER_CRITICAL(&s_mux);
        s_st.tmc = tmc;
        s_st.enc = enc;
        s_st.magnet = magnet;
        s_st.encRaw = enc ? r.raw : 0;
        s_st.angle = angle;
        s_st.target = target;
        s_st.moving = moving;
        s_st.fault = fault;
        s_st.calibrating = cal.phase != 0;
        s_st.travel = s_travel;
        portEXIT_CRITICAL(&s_mux);
    }
}

// --- sensors ---------------------------------------------------------------------------------------------------

void HwBegin()
{
    pinMode(PIN_TMC_EN, OUTPUT);                    // motor off first thing
    digitalWrite(PIN_TMC_EN, HIGH);
    pinMode(PIN_TMC_STEP, OUTPUT);
    digitalWrite(PIN_TMC_STEP, LOW);
    pinMode(PIN_TMC_DIR, OUTPUT);
    digitalWrite(PIN_TMC_DIR, LOW);
    pinMode(PIN_TMC_DIAG, INPUT);

    FansBegin();
    Ds18b20Begin(PIN_TEMP_OUT);
#if AUDIO_MODE && MIC_INMP441
    analogReadResolution(12);                       // the ADC stays free: the 12 V sense reads one-shot
    if (!SoundStreamBeginI2s(PIN_I2S_SCK, PIN_I2S_WS, PIN_I2S_SD, PIN_MIC))  // GPIO 3, if JP2 joins it, left floating
        Log("Microphone: the I2S driver didn't start");
#elif AUDIO_MODE
    if (!SoundStreamBegin(PIN_MIC, PIN_MIC_LINK, PIN_12V_SENSE))    // it also reads the 12 V sense
        Log("Microphone: the ADC's continuous mode didn't start");
#else
    analogReadResolution(12);
    Ds18b20Begin(PIN_TEMP_IN);
#endif

    Serial1.begin(TMC_UART_BAUD, SERIAL_8N1, PIN_TMC_RX, PIN_TMC_TX);
    Wire.begin(PIN_SCD_SDA, PIN_SCD_SCL, SCD_I2C_HZ);
    Wire1.begin(PIN_ENC_SDA, PIN_ENC_SCL, ENC_I2C_HZ);
    Wire.setTimeOut(50);
    Wire1.setTimeOut(20);
    Scd40Begin(&Wire);
    As5600Begin(&Wire1);
    Tmc2209Begin(&Serial1, TMC_ADDR, TMC_RSENSE);

    s_target = 0;
    s_bus = xSemaphoreCreateMutex();
    xTaskCreatePinnedToCore(damperTask, "damper", 4096, nullptr, 5, nullptr, 1);
}

void HwPoll(Inputs* in)
{
    static uint32_t scdTry, scdLast, tempStart, sndLast, v12Last;
    static bool     scdRunning, tempBusy;
    uint32_t now = millis();

    // SCD40: start the periodic mode once it answers; a reading every 5 s.
    if (!scdRunning && now - scdTry >= 5000)
    {
        scdTry = now;
        scdRunning = Scd40StartPeriodic();
        if (scdRunning)
            Log("SCD40 found: periodic measurement started");
    }
    if (scdRunning && now - scdTry >= 1000)
    {
        scdTry = now;
        bool ready;
        Scd40Reading r;
        if (!Scd40DataReady(&ready))
        {
            if (now - scdLast > 30000)
            {
                scdRunning = false;
                Log("SCD40 not answering");
            }
        }
        else if (ready && Scd40Read(&r) && r.co2 > 0)
        {
            scdLast = now;
            in->co2 = r.co2;   in->co2Ok = true;
            portENTER_CRITICAL(&s_mux);
            s_st.scdT = r.tempC;
            portEXIT_CRITICAL(&s_mux);
            if (!s_st.tin)                          // the SCD40's own temperature, unless the indoor DS18B20 answers
            {
                in->tin = r.tempC;
                in->tinOk = true;
            }
            in->rh = r.rh;
            in->rhOk = true;
        }
    }
    if (now - scdLast > 30000)
    {
        in->co2Ok = in->rhOk = false;
        if (!s_st.tin)
            in->tinOk = false;
    }

    // DS18B20: a conversion every 5 s (750 ms each).
    if (!tempBusy && now - tempStart >= 5000)
    {
        tempStart = now;
        tempBusy = true;
        bool o = Ds18b20Start(PIN_TEMP_OUT);
#if !AUDIO_MODE
        bool i = Ds18b20Start(PIN_TEMP_IN);
#else
        bool i = false;
#endif
        portENTER_CRITICAL(&s_mux);
        s_st.tout = o;
        s_st.tin = i;
        portEXIT_CRITICAL(&s_mux);
    }
    if (tempBusy && now - tempStart >= 800)
    {
        tempBusy = false;
        float t;
        in->toutOk = s_st.tout && Ds18b20Read(PIN_TEMP_OUT, &t) == DS18B20_OK;
        if (in->toutOk)
            in->tout = t;
#if !AUDIO_MODE
        if (s_st.tin && Ds18b20Read(PIN_TEMP_IN, &t) == DS18B20_OK)
        {
            in->tin = t;
            in->tinOk = true;
        }
#endif
    }

#if AUDIO_MODE
    // Sound: continuous (SoundStream.h). The level over the last second, and the loudest block since the control's
    // last step, which clears sndMax: nothing between two readings is lost.
    if (now - sndLast >= 250)
    {
        static uint32_t cursor, lastCount, lastNew;
        sndLast = now;
        SoundStats st;
        if (SoundStreamRead(&cursor, &st))
            in->sndMax = max(in->sndMax, st.dbaMax + g_set.micCal);     // A-weighted: dBA once calibrated
        uint32_t count = SoundStreamCount();
        if (count != lastCount)
        {
            lastCount = count;
            lastNew = now;
        }
        uint32_t sec = count > SOUND_STREAM_PER_S ? count - SOUND_STREAM_PER_S : 0;
        bool ok = now - lastNew < 2000 && SoundStreamRead(&sec, &st) && st.micOk;
        in->sndOk = ok;
        if (ok)
            in->snd = st.dba + g_set.micCal;
        portENTER_CRITICAL(&s_mux);
        s_st.mic = ok;
        s_st.snd = ok ? in->snd : 0;
        portEXIT_CRITICAL(&s_mux);
    }
#else
    (void)sndLast;
    in->sndOk = false;
#endif

    if (now - v12Last >= 1000)
    {
        v12Last = now;
#if AUDIO_MODE && !MIC_INMP441
        float mv = SoundStreamOtherMv();
#else
        float mv = analogReadMilliVolts(PIN_12V_SENSE);
#endif
        float v = mv * (V12_DIV_TOP + V12_DIV_BOTTOM) / V12_DIV_BOTTOM / 1000.0f;
        portENTER_CRITICAL(&s_mux);
        s_st.v12 = v;
        s_st.scd = scdRunning;
        portEXIT_CRITICAL(&s_mux);
    }
}

int HwDuty(float pct)
{
    if (pct <= 0)
        return 0;
    return lroundf(g_set.fanMinDuty + pct * (100 - g_set.fanMinDuty) / 100.0f);
}

void HwSetFans(float intakePct, float exhaustPct)
{
    FansSetDuty(0, HwDuty(intakePct));
    FansSetDuty(1, HwDuty(exhaustPct));
}

void HwSetDamper(float deg)
{
    s_target = deg;
}

void HwDamperRetry()
{
    s_retry = true;
}

void HwDamperCalibrate()
{
    s_calReq = true;
}

bool HwDamperCalSave()
{
    bool save = s_calSave;
    s_calSave = false;
    return save;
}

void HwSetFanDuty(int fan, int duty)
{
    FansSetDuty(fan, constrain(duty, 0, 100));
}

void HwBusLock()   { xSemaphoreTake(s_bus, portMAX_DELAY); }
void HwBusUnlock() { xSemaphoreGive(s_bus); }

void HwStatusGet(HwStatus* st)
{
    portENTER_CRITICAL(&s_mux);
    *st = s_st;
    portEXIT_CRITICAL(&s_mux);
    for (int i = 0; i < 2; i++)
    {
        st->duty[i] = FansGetDuty(i);
        st->rpm[i]  = FansRpm(i);
    }
}
