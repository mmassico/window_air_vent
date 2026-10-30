#include "Net.h"
#include <WiFi.h>
#include <ESPmDNS.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <time.h>
#include "App.h"
#include "Log.h"

#define JOIN_TIMEOUT_MS  20000          // then the setup network opens (joining keeps going)
#define AP_LINGER_MS     120000         // the setup network stays this long after joining, to show the new address

static DNSServer s_dns;
static String    s_ssid, s_pass;
static bool      s_ap, s_sta, s_mdns, s_ntp;
static uint32_t  s_joinStart, s_staSince, s_lostSince;

static void apStart()
{
    if (s_ap)
        return;
    WiFi.mode(WIFI_AP_STA);                         // STA too, for the network scan
    WiFi.softAP(NET_AP_SSID);
    s_dns.start(53, "*", WiFi.softAPIP());
    s_ap = true;
    Log("Setup network \"%s\" open: http://%s", NET_AP_SSID, WiFi.softAPIP().toString().c_str());
}

static void apStop()
{
    if (!s_ap)
        return;
    s_dns.stop();
    WiFi.softAPdisconnect(true);
    WiFi.mode(WIFI_STA);
    s_ap = false;
    Log("Setup network closed");
}

static void join()
{
    WiFi.setHostname(g_set.host);
    WiFi.mode(s_ap ? WIFI_AP_STA : WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.begin(s_ssid.c_str(), s_pass.c_str());
    s_joinStart = millis();
    Log("Joining \"%s\"", s_ssid.c_str());
}

void NetBegin()
{
    Preferences p;
    if (p.begin("wifi", true))
    {
        s_ssid = p.getString("ssid", "");
        s_pass = p.getString("pass", "");
        p.end();
    }
    WiFi.persistent(false);                         // the credentials live in our own NVS namespace
    if (s_ssid.length())
        join();
    else
        apStart();
}

void NetPoll()
{
    uint32_t now = millis();
    if (s_ap)
        s_dns.processNextRequest();

    bool sta = WiFi.status() == WL_CONNECTED;
    if (sta && !s_sta)
    {
        s_staSince = now;
        Log("Joined \"%s\": http://%s (or http://%s.local), signal %d dBm", s_ssid.c_str(),
            WiFi.localIP().toString().c_str(), g_set.host, WiFi.RSSI());
        if (!s_mdns && MDNS.begin(g_set.host))
        {
            MDNS.addService("http", "tcp", 80);
            s_mdns = true;
        }
        if (!s_ntp)
        {
            configTzTime(g_set.tz, "pool.ntp.org", "time.nrc.ca");
            s_ntp = true;
        }
    }
    if (!sta && s_sta)
    {
        s_lostSince = now;
        Log("Lost the Wi-Fi network; retrying");
    }
    s_sta = sta;

    if (s_ssid.length() && !sta && !s_ap)
    {
        bool joining = s_lostSince == 0 || s_lostSince < s_joinStart;
        uint32_t since = joining ? now - s_joinStart : now - s_lostSince;
        if (since > (joining ? JOIN_TIMEOUT_MS : 5 * 60000UL))
            apStart();                              // keep trying to join meanwhile
    }
    if (sta && s_ap && now - s_staSince > AP_LINGER_MS)
        apStop();
}

bool NetApOn()  { return s_ap; }
bool NetStaOn() { return s_sta; }
String NetSsid() { return s_ssid; }
int  NetRssi()  { return s_sta ? WiFi.RSSI() : 0; }

String NetIp()
{
    return s_sta ? WiFi.localIP().toString() : (s_ap ? WiFi.softAPIP().toString() : String(""));
}

int NetMinuteOfDay()
{
    struct tm t;
    if (!s_ntp || !getLocalTime(&t, 0) || t.tm_year < 120)
        return -1;
    return t.tm_hour * 60 + t.tm_min;
}

bool NetTimeText(char* out, size_t n)
{
    struct tm t;
    if (!s_ntp || !getLocalTime(&t, 0) || t.tm_year < 120)
        return false;
    strftime(out, n, "%Y-%m-%d %H:%M:%S", &t);
    return true;
}

void NetSetCredentials(const char* ssid, const char* pass)
{
    Preferences p;
    if (p.begin("wifi", false))
    {
        p.putString("ssid", ssid);
        p.putString("pass", pass);
        p.end();
    }
    s_ssid = ssid;
    s_pass = pass;
    WiFi.disconnect();
    join();
}

void NetForget()
{
    Preferences p;
    if (p.begin("wifi", false))
    {
        p.clear();
        p.end();
    }
    s_ssid = s_pass = "";
    Log("Wi-Fi credentials erased");
}

String NetScanJson()
{
    int n = WiFi.scanComplete();
    if (n == WIFI_SCAN_RUNNING)
        return "{\"busy\":true}";
    if (n < 0)                                      // not started (or failed): start one
    {
        WiFi.scanNetworks(true);
        return "{\"busy\":true}";
    }
    String js = "{\"nets\":[";
    for (int i = 0; i < n; i++)
    {
        String ssid = WiFi.SSID(i);
        ssid.replace("\\", "\\\\");
        ssid.replace("\"", "\\\"");
        js += (i ? ",{\"ssid\":\"" : "{\"ssid\":\"") + ssid + "\",\"rssi\":" + WiFi.RSSI(i) +
              ",\"lock\":" + (WiFi.encryptionType(i) == WIFI_AUTH_OPEN ? "false" : "true") + "}";
    }
    js += "]}";
    WiFi.scanDelete();
    return js;
}
