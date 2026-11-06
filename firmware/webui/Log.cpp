#include "Log.h"

static char         (*s_ring)[LOG_LEN];
static uint32_t     s_size;
static uint32_t     s_count;
static portMUX_TYPE s_mux = portMUX_INITIALIZER_UNLOCKED;

// The ring, allocated at the first line: in PSRAM, or a small one in internal RAM.
static bool ring()
{
    if (s_ring)
        return true;
    s_ring = (char (*)[LOG_LEN])ps_malloc(LOG_LINES * LOG_LEN);
    s_size = LOG_LINES;
    if (!s_ring)
    {
        s_ring = (char (*)[LOG_LEN])malloc(40 * LOG_LEN);
        s_size = 40;
    }
    return s_ring != nullptr;
}

void Log(const char* fmt, ...)
{
    char    line[LOG_LEN];
    uint32_t t = millis() / 1000;
    int     n = snprintf(line, sizeof(line), "%02lu:%02lu:%02lu ", (unsigned long)(t / 3600),
                         (unsigned long)(t / 60 % 60), (unsigned long)(t % 60));
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(line + n, sizeof(line) - n, fmt, ap);
    va_end(ap);
    Serial.printf("%s\r\n", line);
    if (!ring())
        return;
    portENTER_CRITICAL(&s_mux);
    memcpy(s_ring[s_count % s_size], line, LOG_LEN);
    s_count++;
    portEXIT_CRITICAL(&s_mux);
}

uint32_t LogCount()
{
    return s_count;
}

uint32_t LogFirst()
{
    uint32_t n = s_count;
    return n > s_size ? n - s_size : 0;
}

bool LogLine(uint32_t index, char* out)
{
    bool ok;
    portENTER_CRITICAL(&s_mux);
    ok = s_ring && index < s_count && s_count - index <= s_size;
    if (ok)
        memcpy(out, s_ring[index % s_size], LOG_LEN);
    portEXIT_CRITICAL(&s_mux);
    return ok;
}
