#include "SoundStream.h"
#include "Sound.h"
#include "driver/gpio.h"
#include "esp_adc/adc_continuous.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

#define FRAME_BYTES     1024    // one DMA frame: 256 conversions, 128 per pin, 16 ms
#define POOL_BYTES      8192    // the driver's buffer between DMA and the task: about 130 ms
#define SKIP_BLOCKS     2       // left out at the start, while the filters settle
#define DC_SHIFT        4096.0f // the DC estimate follows slowly: about 0.3 Hz

struct Block
{
    float    energyA, energyF;
    uint16_t lo, hi;
    uint32_t n;
};

static adc_continuous_handle_t s_adc;
static adc_cali_handle_t       s_caliMic, s_caliOther;
static adc_channel_t           s_chMic, s_chOther;
static Block                   s_ring[SOUND_STREAM_RING];
static volatile uint32_t       s_total;
static volatile int            s_dcMv, s_otherMv;
static volatile float          s_rate;
static portMUX_TYPE            s_mux = portMUX_INITIALIZER_UNLOCKED;

static int toMv(adc_cali_handle_t cali, int raw)
{
    int mv;
    if (cali && adc_cali_raw_to_voltage(cali, raw, &mv) == ESP_OK)
        return mv;
    return raw * 3100 / 4095;
}

static adc_cali_handle_t makeCali(adc_channel_t ch)
{
    adc_cali_curve_fitting_config_t c = {};
    c.unit_id  = ADC_UNIT_1;
    c.chan     = ch;
    c.atten    = ADC_ATTEN_DB_12;
    c.bitwidth = ADC_BITWIDTH_12;
    adc_cali_handle_t h = nullptr;
    return adc_cali_create_scheme_curve_fitting(&c, &h) == ESP_OK ? h : nullptr;
}

static void streamTask(void*)
{
    static uint8_t buf[FRAME_BYTES];
    const float a = 1.0f / (1.0f + 2.0f * PI * SOUND_HPF_HZ / SOUND_STREAM_RATE);
    float    dc = -1, prev = 0, y = 0, st[2][4] = {};
    Block    b = { 0, 0, 4095, 0, 0 };
    uint32_t otherSum = 0, otherN = 0, samples = 0, skip = SKIP_BLOCKS, t0 = micros();

    for (;;)
    {
        uint32_t got = 0;
        if (adc_continuous_read(s_adc, buf, sizeof(buf), &got, 200) != ESP_OK)
            continue;
        for (uint32_t i = 0; i + SOC_ADC_DIGI_RESULT_BYTES <= got; i += SOC_ADC_DIGI_RESULT_BYTES)
        {
            const adc_digi_output_data_t* p = (const adc_digi_output_data_t*)&buf[i];
            int raw = p->type2.data;
            if (p->type2.unit != 0)
                continue;
            if (p->type2.channel == s_chOther)
            {
                otherSum += raw;
                otherN++;
                continue;
            }
            if (p->type2.channel != s_chMic)
                continue;

            if (dc < 0)
                dc = raw;
            dc += (raw - dc) / DC_SHIFT;
            float x = raw - dc;

            y = a * (y + x - prev);                 // the 150 Hz high-pass
            prev = x;
            float v = x;                            // the A-weighting, direct form I
            for (int k = 0; k < 2; k++)
            {
                const float* c = SOUND_A_SOS[k];
                float* z = st[k];
                float o = c[0] * v + c[1] * z[0] + c[2] * z[1] - c[3] * z[2] - c[4] * z[3];
                z[1] = z[0]; z[0] = v;
                z[3] = z[2]; z[2] = o;
                v = o;
            }
            b.energyA += v * v;
            b.energyF += y * y;
            b.lo = min(b.lo, (uint16_t)raw);
            b.hi = max(b.hi, (uint16_t)raw);
            samples++;

            if (++b.n < SOUND_STREAM_BLOCK)
                continue;
            s_dcMv = toMv(s_caliMic, (int)dc);
            if (otherN)
                s_otherMv = toMv(s_caliOther, otherSum / otherN);
            otherSum = otherN = 0;
            s_rate = samples * 1e6f / (micros() - t0);
            if (skip)
                skip--;
            else
            {
                portENTER_CRITICAL(&s_mux);
                s_ring[s_total % SOUND_STREAM_RING] = b;
                s_total = s_total + 1;
                portEXIT_CRITICAL(&s_mux);
            }
            b = { 0, 0, 4095, 0, 0 };
        }
    }
}

bool SoundStreamBegin(uint8_t micPin, uint8_t linkPin, uint8_t otherPin)
{
    // The link pin is wired to the ADC pin: no output, no input buffer, no pull-up or pull-down, so it doesn't load
    // the signal.
    gpio_reset_pin((gpio_num_t)linkPin);
    gpio_set_direction((gpio_num_t)linkPin, GPIO_MODE_DISABLE);
    gpio_set_pull_mode((gpio_num_t)linkPin, GPIO_FLOATING);
    gpio_set_pull_mode((gpio_num_t)micPin, GPIO_FLOATING);

    adc_unit_t unit;
    if (adc_continuous_io_to_channel(micPin, &unit, &s_chMic) != ESP_OK || unit != ADC_UNIT_1
        || adc_continuous_io_to_channel(otherPin, &unit, &s_chOther) != ESP_OK || unit != ADC_UNIT_1)
        return false;

    adc_continuous_handle_cfg_t hc = {};
    hc.max_store_buf_size = POOL_BYTES;
    hc.conv_frame_size    = FRAME_BYTES;
    if (adc_continuous_new_handle(&hc, &s_adc) != ESP_OK)
        return false;

    adc_digi_pattern_config_t pat[2] = {};
    pat[0].atten = pat[1].atten = ADC_ATTEN_DB_12;      // about 0 to 3.1 V
    pat[0].unit = pat[1].unit = ADC_UNIT_1;
    pat[0].bit_width = pat[1].bit_width = SOC_ADC_DIGI_MAX_BITWIDTH;
    pat[0].channel = s_chMic;
    pat[1].channel = s_chOther;
    adc_continuous_config_t cc = {};
    cc.pattern_num    = 2;
    cc.adc_pattern    = pat;
    cc.sample_freq_hz = 2 * SOUND_STREAM_RATE;          // shared by the two pins
    cc.conv_mode      = ADC_CONV_SINGLE_UNIT_1;
    cc.format         = ADC_DIGI_OUTPUT_FORMAT_TYPE2;
    if (adc_continuous_config(s_adc, &cc) != ESP_OK)
        return false;

    s_caliMic   = makeCali(s_chMic);
    s_caliOther = makeCali(s_chOther);
    if (adc_continuous_start(s_adc) != ESP_OK)
        return false;
    // Above the main loop, below the damper; on the loop's core, away from the Wi-Fi.
    return xTaskCreatePinnedToCore(streamTask, "sound", 4096, nullptr, 3, nullptr, 1) == pdPASS;
}

uint32_t SoundStreamCount()
{
    return s_total;
}

int SoundStreamOtherMv()
{
    return s_otherMv;
}

bool SoundStreamRead(uint32_t* cursor, SoundStats* s)
{
    float    sumA = 0, sumF = 0, maxA = 0;
    uint32_t n = 0, blocks = 0, lo = 4095, hi = 0;

    portENTER_CRITICAL(&s_mux);
    uint32_t total = s_total;
    uint32_t first = total > SOUND_STREAM_RING ? total - SOUND_STREAM_RING : 0;
    if (*cursor > first)
        first = *cursor;
    for (uint32_t i = first; i < total; i++)
    {
        const Block& b = s_ring[i % SOUND_STREAM_RING];
        sumA += b.energyA;
        sumF += b.energyF;
        n += b.n;
        maxA = max(maxA, b.energyA / b.n);
        lo = min(lo, (uint32_t)b.lo);
        hi = max(hi, (uint32_t)b.hi);
        blocks++;
    }
    portEXIT_CRITICAL(&s_mux);

    *cursor = total;
    s->blocks = blocks;
    if (!blocks)
        return false;
    s->dba     = SoundDb(sqrtf(sumA / n));
    s->dbaMax  = SoundDb(sqrtf(maxA));
    s->dbfs    = SoundDb(sqrtf(sumF / n));
    s->p2p     = hi - lo;
    s->clipped = lo == 0 || hi == 4095;
    s->dcMv    = s_dcMv;
    s->rateHz  = s_rate;
    return true;
}
