#include "SoundStream.h"
#include "Sound.h"
#include "driver/gpio.h"
#include "driver/i2s_std.h"
#include "esp_adc/adc_continuous.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

#define FRAME_BYTES     1024    // analog: one DMA frame, 256 conversions, 128 per pin, 16 ms
#define POOL_BYTES      8192    // analog: the driver's buffer between DMA and the task, about 130 ms
#define SKIP_ANALOG     2       // blocks left out at the start, while the filters settle
#define SKIP_I2S        8       // ... and for the INMP441, which also needs about 2^18 clocks (0.5 s) to wake up
#define DC_SHIFT        4096.0f // the DC estimate follows slowly: about 0.3 Hz
#define I2S_TO_COUNTS   (1.0f / 4096.0f)    // the INMP441's 24-bit samples to the ADC's 12-bit scale (Sound.h's dBFS)

struct Block
{
    float    energyA, energyF;
    uint16_t lo, hi;
    uint32_t n;
};

static adc_continuous_handle_t s_adc;
static adc_cali_handle_t       s_caliMic, s_caliOther;
static adc_channel_t           s_chMic, s_chOther;
static i2s_chan_handle_t       s_rx;
static bool                    s_i2s;
static Block                   s_ring[SOUND_STREAM_RING];
static volatile uint32_t       s_total;
static volatile int            s_dcMv, s_otherMv;
static volatile float          s_rate;
static portMUX_TYPE            s_mux = portMUX_INITIALIZER_UNLOCKED;

// The filters and the block being filled: one sample at a time, from either source.
static struct
{
    float    a, dc = -1, prev, y, st[2][4];
    Block    b = { 0, 0, 4095, 0, 0 };
    uint32_t samples, skip, t0;
} p;

static void filterBegin(uint32_t skip)
{
    p.a    = 1.0f / (1.0f + 2.0f * PI * SOUND_HPF_HZ / SOUND_STREAM_RATE);
    p.skip = skip;
    p.t0   = micros();
}

// raw: the sample on the 0-4095 scale (the DC still in it). True when it completed a block (p.dc is then that
// block's DC estimate).
static bool filterSample(float raw)
{
    if (p.dc < 0)
        p.dc = raw;
    p.dc += (raw - p.dc) / DC_SHIFT;
    float x = raw - p.dc;

    p.y = p.a * (p.y + x - p.prev);                 // the 150 Hz high-pass
    p.prev = x;
    float v = x;                                    // the A-weighting, direct form I
    for (int k = 0; k < 2; k++)
    {
        const float* c = SOUND_A_SOS[k];
        float* z = p.st[k];
        float o = c[0] * v + c[1] * z[0] + c[2] * z[1] - c[3] * z[2] - c[4] * z[3];
        z[1] = z[0]; z[0] = v;
        z[3] = z[2]; z[2] = o;
        v = o;
    }
    uint16_t r = (uint16_t)constrain(raw, 0.0f, 4095.0f);
    p.b.energyA += v * v;
    p.b.energyF += p.y * p.y;
    p.b.lo = min(p.b.lo, r);
    p.b.hi = max(p.b.hi, r);
    p.samples++;

    if (++p.b.n < SOUND_STREAM_BLOCK)
        return false;
    s_rate = p.samples * 1e6f / (micros() - p.t0);
    if (p.skip)
        p.skip--;
    else
    {
        portENTER_CRITICAL(&s_mux);
        s_ring[s_total % SOUND_STREAM_RING] = p.b;
        s_total = s_total + 1;
        portEXIT_CRITICAL(&s_mux);
    }
    p.b = { 0, 0, 4095, 0, 0 };
    return true;
}

// The link pin is wired to the microphone's pin: no output, no input buffer, no pull-up or pull-down, so it doesn't
// load the signal.
static void linkFloat(uint8_t linkPin)
{
    gpio_reset_pin((gpio_num_t)linkPin);
    gpio_set_direction((gpio_num_t)linkPin, GPIO_MODE_DISABLE);
    gpio_set_pull_mode((gpio_num_t)linkPin, GPIO_FLOATING);
}

// --- analog: the ADC's continuous mode ------------------------------------------------------------------------------
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

static void adcTask(void*)
{
    static uint8_t buf[FRAME_BYTES];
    uint32_t otherSum = 0, otherN = 0;
    filterBegin(SKIP_ANALOG);
    for (;;)
    {
        uint32_t got = 0;
        if (adc_continuous_read(s_adc, buf, sizeof(buf), &got, 200) != ESP_OK)
            continue;
        for (uint32_t i = 0; i + SOC_ADC_DIGI_RESULT_BYTES <= got; i += SOC_ADC_DIGI_RESULT_BYTES)
        {
            const adc_digi_output_data_t* d = (const adc_digi_output_data_t*)&buf[i];
            int raw = d->type2.data;
            if (d->type2.unit != 0)
                continue;
            if (d->type2.channel == s_chOther)
            {
                otherSum += raw;
                otherN++;
                continue;
            }
            if (d->type2.channel != s_chMic || !filterSample(raw))
                continue;
            s_dcMv = toMv(s_caliMic, (int)p.dc);
            if (otherN)
                s_otherMv = toMv(s_caliOther, otherSum / otherN);
            otherSum = otherN = 0;
        }
    }
}

bool SoundStreamBegin(uint8_t micPin, uint8_t linkPin, uint8_t otherPin)
{
    linkFloat(linkPin);
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
    return xTaskCreatePinnedToCore(adcTask, "sound", 4096, nullptr, 3, nullptr, 1) == pdPASS;
}

// --- I2S: the INMP441 ---------------------------------------------------------------------------------------------
static void i2sTask(void*)
{
    static int32_t buf[256];                        // 32 ms of samples
    filterBegin(SKIP_I2S);
    for (;;)
    {
        size_t got = 0;
        if (i2s_channel_read(s_rx, buf, sizeof(buf), &got, 200) != ESP_OK)
            continue;
        for (size_t i = 0; i < got / sizeof(int32_t); i++)
            filterSample((buf[i] >> 8) * I2S_TO_COUNTS + 2048.0f);     // 24 bits, left-justified in 32
    }
}

bool SoundStreamBeginI2s(uint8_t sckPin, uint8_t wsPin, uint8_t sdPin, uint8_t linkPin)
{
    linkFloat(linkPin);
    s_i2s = true;

    i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    if (i2s_new_channel(&cc, nullptr, &s_rx) != ESP_OK)
        return false;
    // Philips (standard I2S) format, 32-bit slots: 64 clocks per frame, so 512 kHz at 8000 samples/s, inside the
    // INMP441's 0.5 to 3.2 MHz. Its L/R pin to GND: it answers in the left slot (WS low).
    i2s_std_config_t sc = {};
    sc.clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(SOUND_STREAM_RATE);
    sc.slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO);
    sc.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;
    sc.gpio_cfg.mclk = I2S_GPIO_UNUSED;
    sc.gpio_cfg.bclk = (gpio_num_t)sckPin;
    sc.gpio_cfg.ws   = (gpio_num_t)wsPin;
    sc.gpio_cfg.dout = I2S_GPIO_UNUSED;
    sc.gpio_cfg.din  = (gpio_num_t)sdPin;
    if (i2s_channel_init_std_mode(s_rx, &sc) != ESP_OK)
        return false;
    // The INMP441 leaves SD floating in the other slot (its sheet: 100 k to GND). Without a microphone, the pull-down
    // (or the PCB's 4.7 k pull-up R9, if fitted, which wins) holds SD still: no signal, no false level.
    gpio_pulldown_en((gpio_num_t)sdPin);
    if (i2s_channel_enable(s_rx) != ESP_OK)
        return false;
    return xTaskCreatePinnedToCore(i2sTask, "sound", 4096, nullptr, 3, nullptr, 1) == pdPASS;
}

// --- both -----------------------------------------------------------------------------------------------------------
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
    s->dcMv    = s_i2s ? 0 : s_dcMv;
    // I2S: a stuck SD line (no microphone) is exactly constant, so nothing gets through the filters; a quiet room's
    // noise (about -87 dBFS) is below one count of the 0-4095 scale, so p2p can't tell
    s->micOk   = s_i2s ? sumF > 0 : s_dcMv > 300 && s_dcMv < 3000;
    s->rateHz  = s_rate;
    return true;
}
