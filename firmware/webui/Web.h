// HTTP server (ESP-IDF's esp_http_server, part of the Arduino core) on port 80:
//   GET  /                 the application page (web/, packed gzipped into WebPage.h by tools/webui_pack.py)
//   GET  /setup            the Wi-Fi setup page
//   GET  /api/settings     settings, JSON          POST /api/settings  change some (any subset), saved at once
//   GET  /api/history      the graphs' history, binary (History.h)
//   GET  /api/scan         Wi-Fi networks          POST /api/wifi      {"ssid","pass"}: save and join
//   GET  /api/ui           the page's shared look (colours), JSON, as saved by POST /api/ui (up to 1 kB)
//   POST /api/cmd          a command, as on the WebSocket
//   GET  /ws               WebSocket: the live state every second out, commands in ({"cmd":...})
// API answers allow any origin, so a page served from a PC (web/ during development) can talk to the ESP32.
#pragma once
#include <ArduinoJson.h>

// The application's command handler: called with the web lock held; returns nullptr, or an error message.
typedef const char* (*WebCommandFn)(JsonObjectConst cmd);

void WebBegin(WebCommandFn onCommand);
void WebBroadcast(const char* text);        // to every WebSocket client
void WebPoll();                             // call from the loop
int  WebClients();
void WebLock();                             // held by the loop while it reads or changes shared state
void WebUnlock();
