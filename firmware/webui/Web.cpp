#include "Web.h"
#include <esp_http_server.h>
#include <Preferences.h>
#include "App.h"
#include "Settings.h"
#include "History.h"
#include "Net.h"
#include "Log.h"
#include "WebPage.h"
#include "SetupPage.h"

#define MAX_BODY 4096

static httpd_handle_t    s_server;
static WebCommandFn      s_onCommand;
static SemaphoreHandle_t s_lock;
static volatile int      s_clients;

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

static esp_err_t onHistory(httpd_req_t* req)
{
    HistHeader h;
    h.count    = HistCount();
    h.interval = HIST_INTERVAL_S;
    h.ageMs    = HistAgeMs();
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
    size_t fds = 8;
    int    list[8];
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

void WebPoll()
{
    if (s_newWifi)                                      // a new Wi-Fi network: joined from the loop, after the answer
    {
        s_newWifi = false;
        Log("Wi-Fi set to \"%s\"", s_newSsid.c_str());
        NetSetCredentials(s_newSsid.c_str(), s_newPass.c_str());
    }
}

// --- start -----------------------------------------------------------------------------------------------------

void WebBegin(WebCommandFn onCommand)
{
    s_onCommand = onCommand;
    s_lock = xSemaphoreCreateRecursiveMutex();

    httpd_config_t cfg   = HTTPD_DEFAULT_CONFIG();
    cfg.max_uri_handlers = 16;
    cfg.uri_match_fn     = httpd_uri_match_wildcard;
    cfg.lru_purge_enable = true;
    cfg.stack_size       = 10240;
    cfg.max_open_sockets = 8;
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
        { "/ws",           HTTP_GET,  onWs,           nullptr, true,  false, nullptr },
        { "/*",            HTTP_GET,  onOther,        nullptr, false, false, nullptr },
    };
    for (const httpd_uri_t& u : uris)
        httpd_register_uri_handler(s_server, &u);
    Log("HTTP server on port 80");
}
