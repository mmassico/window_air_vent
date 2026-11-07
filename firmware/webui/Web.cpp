#include "Web.h"
#include <esp_http_server.h>
#include <Preferences.h>
#include <StreamString.h>
#include <Update.h>
#include <lwip/sockets.h>
#include "App.h"
#include "Settings.h"
#include "History.h"
#include "Net.h"
#include "Log.h"
#include "WebPage.h"
#include "SetupPage.h"

#define MAX_BODY      4096
#define MAX_SOCKETS   12            // pages hold several; 13 at most (LWIP_MAX_SOCKETS 16, less 3)
#define LOG_PER_GET   200           // log lines per GET /api/log at most
#define SHELL_WAIT_MS 15000         // a console command's answer, at most

static httpd_handle_t    s_server;
static WebCommandFn      s_onCommand;
static WebShellFn        s_onShell;
static SemaphoreHandle_t s_lock;
static volatile int      s_clients;
static volatile uint32_t s_restartAt;   // after a firmware update: restart at this millis() (0: no)

// Socket counters, kept by the server's open and close callbacks (both run in the server's task).
static volatile int      s_open, s_peak;
static volatile uint32_t s_opened, s_purged;
#define FD_SLOTS 64                         // lwIP's descriptors are below FD_SETSIZE (64)
static uint32_t          s_openedAt[FD_SLOTS];   // millis() at each descriptor's accept

void WebLock()   { xSemaphoreTakeRecursive(s_lock, portMAX_DELAY); }
void WebUnlock() { xSemaphoreGiveRecursive(s_lock); }

static void cors(httpd_req_t* req)
{
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
}

static esp_err_t sendJson(httpd_req_t* req, const String& js)
{
    cors(req);
    httpd_resp_set_type(req, "application/json");
    return httpd_resp_send(req, js.c_str(), js.length());
}

static esp_err_t sendError(httpd_req_t* req, const char* status, const char* msg)
{
    httpd_resp_set_status(req, status);
    return sendJson(req, String("{\"error\":\"") + msg + "\"}");
}

// Request body into a buffer (nul-terminated); false if too large or broken.
static bool readBody(httpd_req_t* req, char* buf, size_t size)
{
    if (req->content_len >= size)
        return false;
    size_t got = 0;
    while (got < req->content_len)
    {
        int n = httpd_req_recv(req, buf + got, req->content_len - got);
        if (n <= 0)
            return false;
        got += n;
    }
    buf[got] = 0;
    return true;
}

// --- the password, for the console and the firmware update (kept in NVS, never sent back) ---------------------

static String passGet()
{
    Preferences p;
    String pass;
    if (p.begin("vent", true))
    {
        pass = p.getString("admin", "");
        p.end();
    }
    return pass;
}

bool WebPassIsSet()
{
    return passGet().length() > 0;
}

bool WebPassSet(const char* pass)
{
    Preferences p;
    bool ok = p.begin("vent", false) && p.putString("admin", pass) == strlen(pass);
    p.end();
    return ok;
}

// nullptr if the request carries the password (header X-Pass), else why not; a wrong one costs a second.
static const char* unauthorized(httpd_req_t* req)
{
    String pass = passGet();
    if (!pass.length())
        return "no password set yet: on the serial console, type pass <password>";
    char got[64];
    if (httpd_req_get_hdr_value_str(req, "X-Pass", got, sizeof(got)) != ESP_OK || pass != got)
    {
        delay(1000);
        return "wrong password";
    }
    return nullptr;
}

// --- pages -----------------------------------------------------------------------------------------------------

static esp_err_t pageGzip(httpd_req_t* req, const uint8_t* data, size_t len)
{
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache");
    return httpd_resp_send(req, (const char*)data, len);
}

static esp_err_t onIndex(httpd_req_t* req)
{
    if (NetApOn() && !NetStaOn() && NetSsid().length() == 0)
    {
        httpd_resp_set_status(req, "302 Found");        // nothing to show before the Wi-Fi is set up
        httpd_resp_set_hdr(req, "Location", "/setup");
        return httpd_resp_send(req, nullptr, 0);
    }
    return pageGzip(req, WEB_INDEX_GZ, sizeof(WEB_INDEX_GZ));
}

static esp_err_t onSetup(httpd_req_t* req)
{
    return pageGzip(req, WEB_SETUP_GZ, sizeof(WEB_SETUP_GZ));
}

// CORS preflight, for a page served from a PC that sends the X-Pass header.
static esp_err_t onOptions(httpd_req_t* req)
{
    cors(req);
    httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET, POST");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "X-Pass, Content-Type");
    httpd_resp_set_status(req, "204 No Content");
    return httpd_resp_send(req, nullptr, 0);
}

// Anything else: on the setup network, every address leads to the setup page (captive portal); else 404.
static esp_err_t onOther(httpd_req_t* req)
{
    if (NetApOn())
    {
        httpd_resp_set_status(req, "302 Found");
        httpd_resp_set_hdr(req, "Location", "http://192.168.4.1/setup");
        return httpd_resp_send(req, nullptr, 0);
    }
    return httpd_resp_send_err(req, HTTPD_404_NOT_FOUND, "Not found");
}

// --- API -------------------------------------------------------------------------------------------------------

static esp_err_t onGetSettings(httpd_req_t* req)
{
    JsonDocument doc;
    WebLock();
    SettingsToJson(g_set, doc.to<JsonObject>());
    WebUnlock();
    String js;
    serializeJson(doc, js);
    return sendJson(req, js);
}

static esp_err_t onPostSettings(httpd_req_t* req)
{
    static char body[MAX_BODY];                         // httpd runs one request at a time
    JsonDocument in;
    if (!readBody(req, body, sizeof(body)) || deserializeJson(in, body))
        return sendError(req, "400 Bad Request", "bad JSON");
    WebLock();
    SettingsFromJson(&g_set, in.as<JsonObjectConst>());
    bool saved = SettingsSave();
    WebUnlock();
    Log("Settings changed%s", saved ? " and saved" : ", NOT saved");
    return onGetSettings(req);
}

static esp_err_t onCmd(httpd_req_t* req)
{
    static char body[1024];
    JsonDocument in;
    if (!readBody(req, body, sizeof(body)) || deserializeJson(in, body))
        return sendError(req, "400 Bad Request", "bad JSON");
    WebLock();
    const char* err = s_onCommand(in.as<JsonObjectConst>());
    WebUnlock();
    return err ? sendError(req, "400 Bad Request", err) : sendJson(req, "{\"ok\":true}");
}

// GET /api/log?since=N: {"first":oldest kept,"end":next line's number,"from":first sent,"lines":[...]}, up to
// LOG_PER_GET lines from N (or from the oldest kept); ask again from "from" + the lines' count for the rest.
static esp_err_t onLog(httpd_req_t* req)
{
    char q[32], v[16];
    uint32_t since = 0;
    if (httpd_req_get_url_query_str(req, q, sizeof(q)) == ESP_OK && httpd_query_key_value(q, "since", v, sizeof(v)) == ESP_OK)
        since = strtoul(v, nullptr, 10);
    JsonDocument doc;
    uint32_t first = LogFirst(), end = LogCount();
    uint32_t from = max(since, first);
    doc["first"] = first;
    doc["end"]   = end;
    doc["from"]  = from;
    JsonArray lines = doc["lines"].to<JsonArray>();
    char line[LOG_LEN];
    for (uint32_t i = from; i < end && i < from + LOG_PER_GET; i++)
        if (LogLine(i, line))
            lines.add(line);
    String js;
    serializeJson(doc, js);
    return sendJson(req, js);
}

// POST /api/console: a command line (text), as on the serial console; answers with its text. It runs in the loop
// (WebPoll), where the sensors' buses are safe to use.
static char              s_shellLine[WEB_SHELL_LEN];
static StreamString      s_shellOut;
static volatile bool     s_shellPending;
static SemaphoreHandle_t s_shellDone;

static esp_err_t sendText(httpd_req_t* req, const char* status, const String& text)
{
    cors(req);
    httpd_resp_set_status(req, status);
    httpd_resp_set_type(req, "text/plain; charset=utf-8");
    return httpd_resp_send(req, text.c_str(), text.length());
}

static esp_err_t onConsole(httpd_req_t* req)
{
    const char* no = unauthorized(req);
    if (no)
        return sendText(req, "401 Unauthorized", String(no) + "\n");
    char line[WEB_SHELL_LEN];
    if (!readBody(req, line, sizeof(line)))
        return sendText(req, "400 Bad Request", "a command line, " + String(WEB_SHELL_LEN - 1) + " characters at most\n");
    size_t n = strlen(line);
    while (n && strchr("\r\n ", line[n - 1]))
        line[--n] = 0;
    xSemaphoreTake(s_shellDone, 0);                     // a stale answer, from a command that timed out
    strcpy(s_shellLine, line);
    s_shellOut.remove(0);
    s_shellPending = true;
    if (xSemaphoreTake(s_shellDone, pdMS_TO_TICKS(SHELL_WAIT_MS)) != pdTRUE)
    {
        s_shellPending = false;
        return sendText(req, "504 Gateway Timeout", "no answer from the loop\n");
    }
    return sendText(req, "200 OK", s_shellOut);
}

// POST /update: the new firmware (the build's .bin) as the request's body. Written to the other app slot, then
// the vent restarts into it; the new firmware must confirm itself (webui.ino), or the next restart rolls it back.
static esp_err_t onUpdate(httpd_req_t* req)
{
    const char* no = unauthorized(req);
    if (no)
        return sendError(req, "401 Unauthorized", no);
    size_t left = req->content_len;
    if (!left || !Update.begin(left))
        return sendError(req, "400 Bad Request", left ? Update.errorString() : "no firmware in the request");
    Log("Firmware update: receiving %u bytes", (unsigned)left);
    static uint8_t buf[4096];                           // httpd runs one request at a time
    int timeouts = 0;
    while (left)
    {
        int n = httpd_req_recv(req, (char*)buf, min(left, sizeof(buf)));
        if (n == HTTPD_SOCK_ERR_TIMEOUT && ++timeouts < 5)
            continue;
        if (n <= 0 || Update.write(buf, n) != (size_t)n)
        {
            const char* why = n <= 0 ? "the upload broke off" : Update.errorString();
            Update.abort();
            Log("Firmware update failed: %s", why);
            return sendError(req, "500 Internal Server Error", why);
        }
        left -= n;
    }
    if (!Update.end(true))
    {
        Log("Firmware update failed: %s", Update.errorString());
        return sendError(req, "500 Internal Server Error", Update.errorString());
    }
    Log("Firmware update written: restarting into it");
    s_restartAt = millis() + 1000;                      // once the answer has gone out
    return sendJson(req, "{\"ok\":true}");
}

static esp_err_t onHistory(httpd_req_t* req)
{
    HistHeader h;
    h.count    = HistCount();
    h.interval = HIST_INTERVAL_S;
    h.clock    = (uint32_t)HistClock();
    h.recSize  = sizeof(HistRec);
    cors(req);
    httpd_resp_set_type(req, "application/octet-stream");
    httpd_resp_send_chunk(req, (const char*)&h, sizeof(h));
    const uint32_t CHUNK = 256;
    HistRec* buf = (HistRec*)malloc(CHUNK * sizeof(HistRec));
    if (!buf)
        return httpd_resp_send_chunk(req, nullptr, 0);
    for (uint32_t i = 0; i < h.count; i += CHUNK)
    {
        uint32_t n = min(CHUNK, h.count - i);
        HistCopy(i, n, buf);
        if (httpd_resp_send_chunk(req, (const char*)buf, n * sizeof(HistRec)) != ESP_OK)
            break;
    }
    free(buf);
    return httpd_resp_send_chunk(req, nullptr, 0);
}

// The page's look (its colours), saved here so every browser can load the same: kept as the JSON it arrives in.
static esp_err_t onGetUi(httpd_req_t* req)
{
    Preferences p;
    String js = "{}";
    if (p.begin("vent", true))
    {
        js = p.getString("ui", "{}");
        p.end();
    }
    return sendJson(req, js);
}

static esp_err_t onPostUi(httpd_req_t* req)
{
    char body[1025];
    JsonDocument in;
    if (!readBody(req, body, sizeof(body)) || deserializeJson(in, body) || !in.is<JsonObject>())
        return sendError(req, "400 Bad Request", "bad JSON (1 kB at most)");
    Preferences p;
    bool ok = p.begin("vent", false) && p.putString("ui", body) == strlen(body);
    p.end();
    Log("Page colours %s", ok ? "saved" : "NOT saved");
    return ok ? sendJson(req, "{\"ok\":true}") : sendError(req, "500 Internal Server Error", "not saved");
}

static esp_err_t onScan(httpd_req_t* req)
{
    return sendJson(req, NetScanJson());
}

static String s_newSsid, s_newPass;                     // applied by the loop, after the answer has gone out
static volatile bool s_newWifi;

static esp_err_t onWifi(httpd_req_t* req)
{
    char body[256];
    JsonDocument in;
    if (!readBody(req, body, sizeof(body)) || deserializeJson(in, body) || !in["ssid"].is<const char*>())
        return sendError(req, "400 Bad Request", "bad JSON");
    s_newSsid = in["ssid"].as<const char*>();
    s_newPass = in["pass"] | "";
    s_newWifi = true;
    return sendJson(req, "{\"ok\":true}");
}

// --- WebSocket -------------------------------------------------------------------------------------------------

static esp_err_t onWs(httpd_req_t* req)
{
    if (req->method == HTTP_GET)                        // the handshake
    {
        Log("WebSocket client connected");
        return ESP_OK;
    }
    httpd_ws_frame_t f = {};
    if (httpd_ws_recv_frame(req, &f, 0) != ESP_OK)
        return ESP_FAIL;
    if (f.type != HTTPD_WS_TYPE_TEXT || f.len == 0 || f.len > 1024)
        return ESP_OK;
    char buf[1025];
    f.payload = (uint8_t*)buf;
    if (httpd_ws_recv_frame(req, &f, f.len) != ESP_OK)
        return ESP_FAIL;
    buf[f.len] = 0;
    JsonDocument in;
    if (deserializeJson(in, buf))
        return ESP_OK;
    WebLock();
    const char* err = s_onCommand(in.as<JsonObjectConst>());
    WebUnlock();
    if (err)
    {
        String js = String("{\"type\":\"error\",\"msg\":\"") + err + "\"}";
        httpd_ws_frame_t r = {};
        r.type = HTTPD_WS_TYPE_TEXT;
        r.payload = (uint8_t*)js.c_str();
        r.len = js.length();
        httpd_ws_send_frame(req, &r);
    }
    return ESP_OK;
}

// Runs in the server's task (httpd_queue_work): sends one text to every WebSocket client.
static void sendAll(void* arg)
{
    char* text = (char*)arg;
    size_t fds = MAX_SOCKETS;
    int    list[MAX_SOCKETS];
    int    n = 0;
    if (httpd_get_client_list(s_server, &fds, list) == ESP_OK)
    {
        httpd_ws_frame_t f = {};
        f.type = HTTPD_WS_TYPE_TEXT;
        f.payload = (uint8_t*)text;
        f.len = strlen(text);
        for (size_t i = 0; i < fds; i++)
            if (httpd_ws_get_fd_info(s_server, list[i]) == HTTPD_WS_CLIENT_WEBSOCKET)
            {
                httpd_ws_send_frame_async(s_server, list[i], &f);
                n++;
            }
    }
    s_clients = n;
    free(text);
}

void WebBroadcast(const char* text)
{
    if (!s_server)
        return;
    char* copy = strdup(text);
    if (copy && httpd_queue_work(s_server, sendAll, copy) != ESP_OK)
        free(copy);
}

int WebClients()
{
    return s_clients;
}

// --- socket statistics -----------------------------------------------------------------------------------------

static esp_err_t onSockOpen(httpd_handle_t, int fd)
{
    s_open = s_open + 1;
    s_opened = s_opened + 1;
    if (s_open > s_peak)
        s_peak = s_open;
    if (fd >= 0 && fd < FD_SLOTS)
        s_openedAt[fd] = millis();
    return ESP_OK;
}

// With the table full, a close is almost always the LRU purge making room for a new connection.
static void onSockClose(httpd_handle_t, int fd)
{
    if (s_open >= MAX_SOCKETS)
        s_purged = s_purged + 1;
    if (s_open > 0)
        s_open = s_open - 1;
    close(fd);                              // with a close callback, closing is ours to do
}

void WebSockStats(WebSockCounts* c)
{
    c->open = s_open;
    c->max = MAX_SOCKETS;
    c->peak = s_peak;
    c->opened = s_opened;
    c->purged = s_purged;
}

int WebSockList(WebSockInfo* out, int max)
{
    if (!s_server)
        return 0;
    size_t fds = MAX_SOCKETS;
    int    list[MAX_SOCKETS];
    if (httpd_get_client_list(s_server, &fds, list) != ESP_OK)
        return 0;
    int n = 0;
    for (size_t i = 0; i < fds && n < max; i++)
    {
        WebSockInfo& s = out[n++];
        struct sockaddr_storage a = {};
        socklen_t               len = sizeof(a);
        s.fd = list[i];
        s.ws = httpd_ws_get_fd_info(s_server, list[i]) == HTTPD_WS_CLIENT_WEBSOCKET;
        s.ageS = list[i] >= 0 && list[i] < FD_SLOTS ? (millis() - s_openedAt[list[i]]) / 1000 : 0;
        s.port = 0;
        strlcpy(s.ip, "?", sizeof(s.ip));
        if (getpeername(list[i], (struct sockaddr*)&a, &len) == 0)
        {
            if (a.ss_family == AF_INET)
            {
                struct sockaddr_in* v4 = (struct sockaddr_in*)&a;
                inet_ntoa_r(v4->sin_addr, s.ip, sizeof(s.ip));
                s.port = ntohs(v4->sin_port);
            }
            else if (a.ss_family == AF_INET6)       // lwIP reports IPv4 peers of a dual-stack socket this way
            {
                struct sockaddr_in6* v6 = (struct sockaddr_in6*)&a;
                const uint8_t*       b = (const uint8_t*)&v6->sin6_addr;
                snprintf(s.ip, sizeof(s.ip), "%u.%u.%u.%u", b[12], b[13], b[14], b[15]);
                s.port = ntohs(v6->sin6_port);
            }
        }
    }
    return n;
}

void WebPoll()
{
    if (s_shellPending)                                 // a console command from POST /api/console
    {
        WebLock();
        s_onShell(s_shellLine, s_shellOut);
        WebUnlock();
        s_shellPending = false;
        xSemaphoreGive(s_shellDone);
    }
    if (s_restartAt && (int32_t)(millis() - s_restartAt) >= 0)
        ESP.restart();
    if (s_newWifi)                                      // a new Wi-Fi network: joined from the loop, after the answer
    {
        s_newWifi = false;
        Log("Wi-Fi set to \"%s\"", s_newSsid.c_str());
        NetSetCredentials(s_newSsid.c_str(), s_newPass.c_str());
    }
}

// --- start -----------------------------------------------------------------------------------------------------

void WebBegin(WebCommandFn onCommand, WebShellFn onShell)
{
    s_onCommand = onCommand;
    s_onShell = onShell;
    s_lock = xSemaphoreCreateRecursiveMutex();
    s_shellDone = xSemaphoreCreateBinary();

    httpd_config_t cfg   = HTTPD_DEFAULT_CONFIG();
    cfg.max_uri_handlers = 20;
    cfg.uri_match_fn     = httpd_uri_match_wildcard;
    cfg.lru_purge_enable = true;
    cfg.stack_size       = 10240;
    cfg.max_open_sockets = MAX_SOCKETS;
    cfg.open_fn          = onSockOpen;
    cfg.close_fn         = onSockClose;
    if (httpd_start(&s_server, &cfg) != ESP_OK)
    {
        Log("HTTP server failed to start");
        return;
    }

    static const httpd_uri_t uris[] = {
        { "/",             HTTP_GET,  onIndex,        nullptr, false, false, nullptr },
        { "/setup",        HTTP_GET,  onSetup,        nullptr, false, false, nullptr },
        { "/api/settings", HTTP_GET,  onGetSettings,  nullptr, false, false, nullptr },
        { "/api/settings", HTTP_POST, onPostSettings, nullptr, false, false, nullptr },
        { "/api/cmd",      HTTP_POST, onCmd,          nullptr, false, false, nullptr },
        { "/api/history",  HTTP_GET,  onHistory,      nullptr, false, false, nullptr },
        { "/api/scan",     HTTP_GET,  onScan,         nullptr, false, false, nullptr },
        { "/api/ui",       HTTP_GET,  onGetUi,        nullptr, false, false, nullptr },
        { "/api/ui",       HTTP_POST, onPostUi,       nullptr, false, false, nullptr },
        { "/api/wifi",     HTTP_POST, onWifi,         nullptr, false, false, nullptr },
        { "/api/log",      HTTP_GET,  onLog,          nullptr, false, false, nullptr },
        { "/api/console",  HTTP_POST, onConsole,      nullptr, false, false, nullptr },
        { "/update",       HTTP_POST, onUpdate,       nullptr, false, false, nullptr },
        { "/ws",           HTTP_GET,  onWs,           nullptr, true,  false, nullptr },
        { "/*",            HTTP_GET,  onOther,        nullptr, false, false, nullptr },
        { "/*",            HTTP_OPTIONS, onOptions,   nullptr, false, false, nullptr },
    };
    for (const httpd_uri_t& u : uris)
        httpd_register_uri_handler(s_server, &u);
    Log("HTTP server on port 80");
}
