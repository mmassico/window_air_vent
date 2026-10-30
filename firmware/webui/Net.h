// Wi-Fi: joins the saved network; with none saved, or when it can't join, it opens its own setup network
// (NET_AP_SSID, no password) with a captive portal: any page leads to the Wi-Fi setup page, at http://192.168.4.1.
// Once on the home network: http://<host>.local (mDNS), and the local time from NTP.
#pragma once
#include <Arduino.h>

#define NET_AP_SSID "WindowVent-setup"

void   NetBegin();
void   NetPoll();
bool   NetApOn();                       // the setup network is up
bool   NetStaOn();                      // joined the home network
String NetSsid();
String NetIp();                         // home network address, or the setup network's
int    NetRssi();
int    NetMinuteOfDay();                // local time, -1 until NTP answered
bool   NetTimeText(char* out, size_t n);
void   NetSetCredentials(const char* ssid, const char* pass);   // saves, then joins
void   NetForget();                     // erases them: setup network at the next boot
String NetScanJson();                   // {"busy":true} while scanning, else {"nets":[{"ssid","rssi","lock"}]}
