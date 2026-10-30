#include "Hw.h"
#include <Wire.h>
#include "Pins.h"
#include "Scd40.h"
#include "As5600.h"
#include "Tmc2209.h"
#include "Fans.h"
#include "Ds18b20.h"
#include "Sound.h"
#include "Log.h"

#define MICROSTEPS      16
#define RUN_MA          500
#define HOLD_PCT        50
#define ANGLE_TOL       1.0f        // degrees: close enough
#define SLOW_ZONE       15.0f       // degrees: slow down over the last part of a move
#define MOVE_TIMEOUT_MS 8000        // a quarter turn takes about 1 s
#define IDLE_OFF_MS     1500        // driver off this long after a move (the stepper's detent holds the damper)

static HwStatus     s_st;
static portMUX_TYPE s_mux = portMUX_INITIALIZER_UNLOCKED;
static volatile float s_target;

// --- damper task -----------------------------------------------------------------------------------------------

static float encAngle(uint16_t raw)
{
    float a = As5600Degrees((raw - g_set.encZero) & 0x0fff);
    return a > 180 ? a - 360 : a;                   // -180 to 180, closed = 0
}

static void damperTask(void*)
{
    uint32_t lastTry = 0, stopAt = 0, moveStart = 0;
    bool     tmc = false, enabled = false, moving = false, fault = false;
    float    lastTarget = -999;
    long     lastV = 0;

    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(10));
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
            vTaskDelay(pdMS_TO_TICKS(490));        // no encoder: look for it twice a second only
        bool magnet = enc && (r.status & 0x20);
        float angle = enc ? encAngle(r.raw) : 0;
        float target = s_target;

        if (target != lastTarget)
        {
            lastTarget = target;
            fault = false;
            moveStart = now;
        }

        long v = 0;
        if (tmc && enc && magnet && !fault)
        {
            float err = target - angle;
            if (fabsf(err) > ANGLE_TOL)
            {
                if (!moving)
                {
                    moving = true;
                    moveStart = now;
                }
                float k = constrain(fabsf(err) / SLOW_ZONE, 0.15f, 1.0f);
                v = lroundf(g_set.motorSpeed * k) * (err > 0 ? 1 : -1) * g_set.motorDir;
                if (now - moveStart > MOVE_TIMEOUT_MS)
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

        portENTER_CRITICAL(&s_mux);
        s_st.tmc = tmc;
        s_st.enc = enc;
        s_st.magnet = magnet;
        s_st.encRaw = enc ? r.raw : 0;
        s_st.angle = angle;
        s_st.target = target;
        s_st.moving = moving;
        s_st.fault = fault;
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
    analogReadResolution(12);
    Ds18b20Begin(PIN_TEMP_OUT);
#if AUDIO_MODE
    SoundBegin(PIN_MIC, PIN_MIC_LINK);
#else
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
    // Sound: a 100 ms burst every 2 s (it blocks the loop meanwhile; the damper has its own task).
    if (now - sndLast >= 2000)
    {
        sndLast = now;
        SoundReading r;
        bool ok = SoundMeasure(100, &r) && r.dcMv > 300 && r.dcMv < 3000;   // no bias: no microphone
        in->sndOk = ok;
        if (ok)
            in->snd = r.dbfs + g_set.micCal;
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
        float v = analogReadMilliVolts(PIN_12V_SENSE) * (V12_DIV_TOP + V12_DIV_BOTTOM) / V12_DIV_BOTTOM / 1000.0f;
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
