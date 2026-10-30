#include "Log.h"

static char         s_ring[LOG_LINES][LOG_LEN];
static uint32_t     s_count;
static portMUX_TYPE s_mux = portMUX_INITIALIZER_UNLOCKED;

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
    portENTER_CRITICAL(&s_mux);
    memcpy(s_ring[s_count % LOG_LINES], line, LOG_LEN);
    s_count++;
    portEXIT_CRITICAL(&s_mux);
}

uint32_t LogCount()
{
    return s_count;
}

bool LogLine(uint32_t index, char* out)
{
    bool ok;
    portENTER_CRITICAL(&s_mux);
    ok = index < s_count && s_count - index <= LOG_LINES;
    if (ok)
        memcpy(out, s_ring[index % LOG_LINES], LOG_LEN);
    portEXIT_CRITICAL(&s_mux);
    return ok;
}
