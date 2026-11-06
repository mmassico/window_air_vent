// HTTP server (ESP-IDF's esp_http_server, part of the Arduino core) on port 80:
//   GET  /                 the application page (web/, packed gzipped into WebPage.h by tools/webui_pack.py)
//   GET  /setup            the Wi-Fi setup page
//   GET  /api/settings     settings, JSON          POST /api/settings  change some (any subset), saved at once
//   GET  /api/history      the graphs' history, binary (History.h)
//   GET  /api/scan         Wi-Fi networks          POST /api/wifi      {"ssid","pass"}: save and join
//   GET  /api/ui           the page's shared look (colours), JSON, as saved by POST /api/ui (up to 1 kB)
//   POST /api/cmd          a command, as on the WebSocket
//   GET  /ws               WebSocket: the live state every second out, commands in ({"cmd":...})
//   GET  /api/log?since=N  the log from line N, JSON (up to 200 lines per call; lines are numbered from boot)
//   POST /api/console      a console command line (text), as on the serial console; its answer, text  [pass]
//   POST /update           new firmware: the build's .bin as the body; the vent restarts into it      [pass]
// [pass]: the request needs the password in an X-Pass header; refused until one is set (serial: pass <password>).
// API answers allow any origin, so a page served from a PC (web/ during development) can talk to the ESP32.
#pragma once
#include <ArduinoJson.h>

#define WEB_SHELL_LEN 128                   // a console command line, with its nul

// The application's command handler: called with the web lock held; returns nullptr, or an error message.
typedef const char* (*WebCommandFn)(JsonObjectConst cmd);
// The application's console: runs a command line (it may change it), prints the answer to out. Called by
// WebPoll() in the loop, with the web lock held.
typedef void (*WebShellFn)(char* line, Print& out);

void WebBegin(WebCommandFn onCommand, WebShellFn onShell);
void WebBroadcast(const char* text);        // to every WebSocket client
void WebPoll();                             // call from the loop
int  WebClients();
void WebLock();                             // held by the loop while it reads or changes shared state
void WebUnlock();
bool WebPassIsSet();
bool WebPassSet(const char* pass);          // "" removes it
