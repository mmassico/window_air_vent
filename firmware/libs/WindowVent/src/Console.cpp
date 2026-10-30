#include "Console.h"

static ConHandler s_handler;
static char       s_line[CON_LINE_MAX];
static int        s_len;
static char       s_hist[CON_HIST_SIZE][CON_LINE_MAX];
static int        s_histCount;          // entries stored
static int        s_histPos = -1;       // entry being browsed, -1 = editing a new line
static int        s_esc;                // escape sequence state: 0 none, 1 got ESC, 2 got ESC [
static char       s_lastEol;            // swallows the LF of a CR LF pair

static void prompt()
{
    Serial.print("\r\n> ");
}

static void replaceLine(const char* text)
{
    while (s_len > 0) { Serial.print("\b \b"); s_len--; }
    strncpy(s_line, text, CON_LINE_MAX - 1);
    s_line[CON_LINE_MAX - 1] = 0;
    s_len = strlen(s_line);
    Serial.print(s_line);
}

static void historyAdd(const char* text)
{
    if (s_histCount > 0 && strcmp(s_hist[0], text) == 0)
        return;
    for (int i = CON_HIST_SIZE - 1; i > 0; i--)
        strcpy(s_hist[i], s_hist[i - 1]);
    strcpy(s_hist[0], text);
    if (s_histCount < CON_HIST_SIZE)
        s_histCount++;
}

static void historyMove(int dir)       // dir +1 = older, -1 = newer
{
    int pos = s_histPos + dir;
    if (pos >= s_histCount)
        return;
    s_histPos = pos < -1 ? -1 : pos;
    replaceLine(s_histPos < 0 ? "" : s_hist[s_histPos]);
}

static void execute()
{
    s_line[s_len] = 0;
    if (s_len > 0)
        historyAdd(s_line);
    s_histPos = -1;

    char* argv[CON_ARGS_MAX];
    int   argc = 0;
    for (char* tok = strtok(s_line, " \t"); tok && argc < CON_ARGS_MAX; tok = strtok(NULL, " \t"))
        argv[argc++] = tok;

    s_len = 0;
    if (argc == 0)
    {
        prompt();
        return;
    }
    if (strcmp(argv[0], "cls") == 0 || strcmp(argv[0], "clear") == 0)
    {
        Serial.print("\x1b[2J\x1b[H");
        Serial.print("> ");
        return;
    }
    Serial.print("\r\n");
    s_handler(argc, argv);
    prompt();
}

void ConBegin(ConHandler handler, const char* banner)
{
    s_handler = handler;
    Serial.print("\r\n");
    Serial.print(banner);
    Serial.print("\r\nType 'help' for the command list.");
    prompt();
}

void ConPoll()
{
    while (Serial.available())
    {
        char c = Serial.read();

        if (s_esc == 1) { s_esc = (c == '[') ? 2 : 0; continue; }
        if (s_esc == 2)
        {
            s_esc = 0;
            if (c == 'A') historyMove(+1);
            else if (c == 'B') historyMove(-1);
            continue;                   // other sequences (left/right, ...) are ignored
        }
        if (c == 0x1b) { s_esc = 1; continue; }

        if (c == '\r' || c == '\n')
        {
            bool pairEnd = (c == '\n' && s_lastEol == '\r');
            s_lastEol = c;
            if (!pairEnd)
                execute();
            continue;
        }
        s_lastEol = 0;

        if (c == '\b' || c == 0x7f)
        {
            if (s_len > 0) { s_len--; Serial.print("\b \b"); }
        }
        else if (c >= ' ' && s_len < CON_LINE_MAX - 1)
        {
            s_line[s_len++] = c;
            Serial.print(c);
        }
    }
}

bool ConKeyHit()
{
    if (!Serial.available())
        return false;
    while (Serial.available())
        Serial.read();
    s_lastEol = 0;
    return true;
}

bool ConParseInt(const char* s, long* value)
{
    bool neg = false;
    int  base = 10;
    int  len;

    if (*s == '-') { neg = true; s++; }
    len = strlen(s);
    if (len == 0)
        return false;

    if (len > 2 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) { base = 16; s += 2; len -= 2; }
    else if (len > 2 && s[0] == '0' && (s[1] == 'b' || s[1] == 'B')) { base = 2; s += 2; len -= 2; }
    else if (len > 1 && (s[len - 1] == 'h' || s[len - 1] == 'H')) { base = 16; len--; }
    else if (len > 1 && (s[len - 1] == 'b' || s[len - 1] == 'B') && strspn(s, "01") == (size_t)(len - 1)) { base = 2; len--; }

    long v = 0;
    for (int i = 0; i < len; i++)
    {
        char c = s[i];
        int  d;
        if (c >= '0' && c <= '9') d = c - '0';
        else if (c >= 'a' && c <= 'f') d = c - 'a' + 10;
        else if (c >= 'A' && c <= 'F') d = c - 'A' + 10;
        else return false;
        if (d >= base)
            return false;
        v = v * base + d;
    }
    *value = neg ? -v : v;
    return true;
}

bool ConArgInt(int argc, char* argv[], int i, long* value)
{
    if (i >= argc)
    {
        Serial.printf("Missing argument %d. Type 'help'.", i);
        return false;
    }
    if (!ConParseInt(argv[i], value))
    {
        Serial.printf("Not a number: '%s'.", argv[i]);
        return false;
    }
    return true;
}
