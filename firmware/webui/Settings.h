// Settings: defaults, JSON in and out, saved in NVS.
#pragma once
#include <ArduinoJson.h>
#include "App.h"

void SettingsDefaults(Settings* s);
void SettingsLoad();                                // into g_set; defaults if nothing saved
bool SettingsSave();
uint32_t SettingsRev();                             // counts the saves since boot: open pages reload when it changes
void SettingsToJson(const Settings& s, JsonObject o);
void SettingsFromJson(Settings* s, JsonObjectConst o);  // keys present only, each clamped to its range
