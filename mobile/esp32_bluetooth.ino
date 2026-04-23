// ============================================================
// BIOQUA: AI-Assisted Water Quality Monitoring System
//
// Authors         : Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D.
// Year            : 2026
// License         : MIT License
//
// This project is the original work of the authors.
// Unauthorized removal of this notice is prohibited.
// ============================================================

// ESP32 Bluetooth Serial (SPP) — Sensor Reader & LCD Display
//
// Reads pH and EC sensors, transmits readings over Bluetooth,
// receives classification results from a connected phone/laptop,
// and displays everything on a 20x4 I2C LCD.
//
// Wiring:
//   pH sensor  → GPIO 36 (A0 / ADC1_CH0)
//   EC sensor  → GPIO 39 (A1 / ADC1_CH3)
//   LCD SDA    → GPIO 21
//   LCD SCL    → GPIO 22

#include "BluetoothSerial.h"
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// --------------- Configuration ---------------

#define PH_PIN       36    // ADC1_CH0 (A0)
#define EC_PIN       39    // ADC1_CH3 (A1)

#define LCD_ADDR     0x27
#define LCD_COLS     20
#define LCD_ROWS     4

// Calibration constants — adjust for your specific sensors
#define PH_OFFSET    0.00   // Offset after calibration with pH 7 buffer
#define PH_SLOPE     3.5    // mV-to-pH slope (typical for analog pH module)
#define EC_KVALUE    1.0    // Cell constant for EC probe

#define ADC_VREF     3.3
#define ADC_RES      4095.0

#define SEND_INTERVAL_MS  2000  // Send readings every 2 seconds

// --------------- Globals ---------------

BluetoothSerial SerialBT;
LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);

String currentStatus    = "IDLE";
String bacteriaType     = "---";
String riskLevel        = "---";
unsigned long lastSendTime = 0;

// --------------- Sensor Reading ---------------

float readPH() {
  int raw = analogRead(PH_PIN);
  float voltage = raw * (ADC_VREF / ADC_RES);
  // Convert voltage to pH (linear calibration, inverse relationship)
  // NOTE: ESP32 uses 3.3V ADC, so midpoint is ~1.65V (not 2.5V like 5V Arduino)
  float ph = 7.0 + ((ADC_VREF / 2.0 - voltage) * PH_SLOPE) + PH_OFFSET;
  return constrain(ph, 0.0, 14.0);
}

float readEC() {
  int raw = analogRead(EC_PIN);
  float voltage = raw * (ADC_VREF / ADC_RES);
  // Convert voltage to EC in uS/cm (simplified linear model)
  float ec = (voltage * 1000.0) * EC_KVALUE;
  return max(ec, 0.0f);
}

// --------------- Bluetooth Receive ---------------

void processIncoming(String line) {
  // Expected format from phone/laptop:
  //   "result:SAFE,bacteria:None,risk:LOW"
  //   "result:CONTAMINATED,bacteria:E.coli,risk:HIGH"
  //   "status:SCANNING"

  line.trim();

  if (line.startsWith("status:")) {
    currentStatus = line.substring(7);
  }

  // Parse comma-separated key:value pairs
  int start = 0;
  while (start < (int)line.length()) {
    int commaIdx = line.indexOf(',', start);
    if (commaIdx == -1) commaIdx = line.length();

    String pair = line.substring(start, commaIdx);
    int colonIdx = pair.indexOf(':');
    if (colonIdx > 0) {
      String key = pair.substring(0, colonIdx);
      String val = pair.substring(colonIdx + 1);
      key.trim();
      val.trim();

      if (key == "result" || key == "status") {
        currentStatus = val;
      } else if (key == "bacteria") {
        bacteriaType = val;
      } else if (key == "risk") {
        riskLevel = val;
      }
    }
    start = commaIdx + 1;
  }
}

// --------------- LCD Display ---------------

void updateLCD(float ph, float ec) {
  // Use setCursor + overwrite instead of lcd.clear() to prevent flicker

  // Row 0: Title (static — only write once)
  static bool titleDrawn = false;
  if (!titleDrawn) {
    lcd.setCursor(0, 0);
    lcd.print("== BIOQUA v1.0 ==");
    titleDrawn = true;
  }

  // Row 1: pH and EC readings (pad to 20 chars to overwrite old content)
  lcd.setCursor(0, 1);
  String row1 = "pH:" + String(ph, 2) + "  EC:" + String(ec, 1);
  while (row1.length() < 20) row1 += " ";
  lcd.print(row1);

  // Row 2: Status and risk
  lcd.setCursor(0, 2);
  String row2 = "St:" + currentStatus.substring(0, 8) + " Rk:" + riskLevel.substring(0, 5);
  while (row2.length() < 20) row2 += " ";
  lcd.print(row2);

  // Row 3: Bacteria type
  lcd.setCursor(0, 3);
  String row3 = "Bact:" + bacteriaType.substring(0, 14);
  while (row3.length() < 20) row3 += " ";
  lcd.print(row3);
}

// --------------- Setup ---------------

void setup() {
  Serial.begin(115200);
  Serial.println("BIOQUA ESP32 starting...");

  // Initialise Bluetooth
  if (!SerialBT.begin("BIOQUA-ESP32")) {
    Serial.println("Bluetooth init failed!");
    while (true) { delay(1000); }
  }
  Serial.println("Bluetooth ready — device name: BIOQUA-ESP32");

  // Initialise LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("== BIOQUA v1.0 ==");
  lcd.setCursor(0, 1);
  lcd.print("Waiting for BT...");

  // Configure ADC
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  delay(1000);
}

// --------------- Main Loop ---------------

void loop() {
  // --- Read incoming Bluetooth data ---
  if (SerialBT.available()) {
    String incoming = SerialBT.readStringUntil('\n');
    processIncoming(incoming);
    // Echo to serial monitor for debugging
    Serial.print("BT RX: ");
    Serial.println(incoming);
  }

  // --- Send sensor data at interval ---
  unsigned long now = millis();
  if (now - lastSendTime >= SEND_INTERVAL_MS) {
    lastSendTime = now;

    float ph = readPH();
    float ec = readEC();

    // Build outgoing message
    String msg = "pH:" + String(ph, 2)
               + ",EC:" + String(ec, 1)
               + ",status:" + currentStatus
               + "\n";

    // Send over Bluetooth
    SerialBT.print(msg);

    // Echo to serial monitor
    Serial.print("BT TX: ");
    Serial.print(msg);

    // Update LCD
    updateLCD(ph, ec);
  }

  delay(10);  // Small yield
}
