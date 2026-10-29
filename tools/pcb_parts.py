"""Parts and nets of the controller PCB (pcb/window_vent_ctrl), shared by tools/pcb_schematic.py and tools/pcb_layout.py.

The circuit is the one in firmware/images/wiring.svg and doc/perfboard.svg; pins as in firmware/baremetal/Pins.h.
Each part: reference, lib_id (KiCad symbol), value, footprint, {pin number: net}. Pins left out are not connected.
"""

ESP_L = ["3V3", "EN", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46", "9", "10", "11", "12", "13", "14", "5V"]
ESP_R = ["TX", "RX", "1", "2", "42", "41", "40", "39", "38", "37", "36", "35", "0", "45", "48", "47", "21", "20", "19", "GND"]
TMC_S = ["EN", "MS1", "MS2", "PDN", "UART", "CLK", "STEP", "DIR"]
TMC_P = ["VM", "GND", "M1B", "M1A", "M2A", "M2B", "VIO", "GND"]

# ESP32-S3 GPIO -> net (the rest of its pins stay free)
ESP_GPIO = {
    "4": "FAN0_PWM", "5": "FAN1_PWM", "6": "ENC_SDA", "7": "ENC_SCL", "15": "FAN0_TACH", "16": "FAN1_TACH",
    "17": "TMC_TX", "18": "TMC_UART", "8": "SCD_SDA", "9": "SCD_SCL", "10": "TMC_EN", "11": "TMC_STEP",
    "12": "TMC_DIR", "13": "TMC_DIAG", "14": "DQ_OUT", "1": "V12_SENSE", "21": "DQ_IN", "3": "MIC",
}


def esp_nets():
    nets = {}
    for i, name in enumerate(ESP_L + ESP_R, 1):
        if name == "3V3":
            nets[str(i)] = "+3V3"
        elif name == "GND":
            nets[str(i)] = "GND"
        elif name in ESP_GPIO:
            nets[str(i)] = ESP_GPIO[name]
    return nets


TMC_NETS = {"1": "TMC_EN", "2": "GND", "3": "GND", "5": "TMC_UART", "7": "TMC_STEP", "8": "TMC_DIR",
            "9": "+12V", "10": "GND", "11": "MOT_1B", "12": "MOT_1A", "13": "MOT_2A", "14": "MOT_2B",
            "15": "+3V3", "16": "GND"}

R_FLAT = "window_vent:R_DIN0207_P10.16mm_Flat_Tight"   # lying under the modules' edges (courtyard = body)
R_UP = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical"


def hdr(n):
    return f"Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical"


PARTS = [
    # ref, lib_id, value, footprint, pins, description (for the schematic)
    ("U1", "window_vent:ESP32S3_Lite", "Freenove ESP32-S3 Lite", "window_vent:Freenove_ESP32S3_Lite", esp_nets(), ""),
    ("U2", "window_vent:TMC2209_Module", "TMC2209 module", "window_vent:TMC2209_StepStick", TMC_NETS, ""),
    ("J1", "Connector_Generic:Conn_01x02", "12V IN", hdr(2), {"1": "VIN", "2": "GND"}, ""),
    ("JP1", "Jumper:Jumper_2_Open", "D1 bypass", hdr(2), {"1": "VIN", "2": "+12V"}, ""),
    # audio mode: a microphone on J7 instead of the indoor probe; GPIO 21 has no ADC, so JP2 joins it to GPIO 3 (ADC1)
    ("JP2", "Jumper:SolderJumper_2_Open", "AUDIO", "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
     {"1": "DQ_IN", "2": "MIC"}, ""),
    ("D1", "Device:D_Schottky", "1N5822", "Diode_THT:D_DO-201AD_P5.08mm_Vertical_AnodeUp", {"1": "+12V", "2": "VIN"}, ""),
    ("C1", "Device:C_Polarized", "220uF 50V", "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm", {"1": "+12V", "2": "GND"}, ""),
    ("R1", "Device:R", "10k", R_UP, {"1": "FAN0_TACH", "2": "+3V3"}, ""),
    ("R2", "Device:R", "10k", R_UP, {"1": "FAN0_PWM", "2": "GND"}, ""),
    ("R3", "Device:R", "10k", R_UP, {"1": "FAN1_TACH", "2": "+3V3"}, ""),
    ("R4", "Device:R", "10k", R_UP, {"1": "FAN1_PWM", "2": "GND"}, ""),
    ("R5", "Device:R", "10k", R_FLAT, {"1": "TMC_EN", "2": "+3V3"}, ""),
    ("R6", "Device:R", "1k", R_FLAT, {"1": "TMC_TX", "2": "TMC_UART"}, ""),
    ("R7", "Device:R", "100k", R_FLAT, {"1": "+12V", "2": "V12_SENSE"}, ""),
    ("R8", "Device:R", "22k", R_FLAT, {"1": "V12_SENSE", "2": "GND"}, ""),
    ("R9", "Device:R", "4.7k", R_UP, {"1": "DQ_IN", "2": "+3V3"}, ""),
    ("R10", "Device:R", "4.7k", R_UP, {"1": "DQ_OUT", "2": "+3V3"}, ""),
    ("J2", "Connector_Generic:Conn_01x04", "FAN 0 intake", hdr(4), {"1": "GND", "2": "+12V", "3": "FAN0_TACH", "4": "FAN0_PWM"}, ""),
    ("J3", "Connector_Generic:Conn_01x04", "FAN 1 exhaust", hdr(4), {"1": "GND", "2": "+12V", "3": "FAN1_TACH", "4": "FAN1_PWM"}, ""),
    ("J4", "Connector_Generic:Conn_01x04", "MOTOR", hdr(4), {"1": "MOT_1A", "2": "MOT_1B", "3": "MOT_2A", "4": "MOT_2B"}, ""),
    ("J5", "Connector_Generic:Conn_01x04", "SCD40", hdr(4),   # 1:1 with the SCD40 module: GND, VDD, SCL, SDA
     {"1": "GND", "2": "+3V3", "3": "SCD_SCL", "4": "SCD_SDA"}, ""),
    ("J6", "Connector_Generic:Conn_01x04", "AS5600", hdr(4), {"1": "+3V3", "2": "GND", "3": "ENC_SDA", "4": "ENC_SCL"}, ""),
    ("J7", "Connector_Generic:Conn_01x03", "DS18B20 in", hdr(3), {"1": "+3V3", "2": "DQ_IN", "3": "GND"}, ""),
    ("J8", "Connector_Generic:Conn_01x03", "DS18B20 out", hdr(3), {"1": "GND", "2": "DQ_OUT", "3": "+3V3"}, ""),
    ("TP1", "Connector:TestPoint", "GND", "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm", {"1": "GND"}, ""),
    ("TP2", "Connector:TestPoint", "3V3", "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm", {"1": "+3V3"}, ""),
    ("TP3", "Connector:TestPoint", "VIN", "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm", {"1": "VIN"}, ""),
    ("TP4", "Connector:TestPoint", "12V", "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm", {"1": "+12V"}, ""),
    ("TP5", "Connector:TestPoint", "DIAG", "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm", {"1": "TMC_DIAG"}, ""),
    ("H1", "Mechanical:MountingHole", "M2", "MountingHole:MountingHole_2.2mm_M2", {}, ""),
    ("H2", "Mechanical:MountingHole", "M2", "MountingHole:MountingHole_2.2mm_M2", {}, ""),
    ("H3", "Mechanical:MountingHole", "M2", "MountingHole:MountingHole_2.2mm_M2", {}, ""),
    ("H4", "Mechanical:MountingHole", "M2", "MountingHole:MountingHole_2.2mm_M2", {}, ""),
]

POWER_NETS = {"GND": "power:GND", "+3V3": "power:+3V3", "+12V": "power:+12V"}
