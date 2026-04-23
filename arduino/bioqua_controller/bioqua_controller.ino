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

/*
 * BIOQUA Arduino Controller — Four-Phase Implementation
 * =====================================================
 * Runs on Arduino Mega 2560. Each test cycle moves through the four
 * phases defined in docs/Phase.pdf:
 *
 *   Phase 1 — EC/TDS measurement on bulk water in the sensor manifold
 *   Phase 2 — Aspiration (1 mL syringe) and injection into the microchamber
 *   Phase 3 — On-chip Gram staining (CV → Iodine → Decolorizer → Safranin)
 *   Phase 4 — Risk result received from laptop and displayed on the LCD
 *
 * WIRING (see wiring/wiring_diagram.txt for full details):
 *   pH sensor           → A0
 *   TDS / EC sensor     → A1
 *   Reagent relays 1-4  → D2-D5  (CV, Iodine, Decolor, Safranin)
 *   DI water valve      → D6
 *   Peristaltic pump    → D7
 *   Start button        → D8
 *   3/2-way dir valve   → D9     (aspirate vs. inject path)
 *   Syringe actuator    → D10    (servo / stepper enable)
 *   LCD SDA             → SDA (pin 20)
 *   LCD SCL             → SCL (pin 21)
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ─── PIN ASSIGNMENTS ─────────────────────────────────────────
// Change these if you wire things differently.

#define PH_PIN          A0      // pH sensor analog input
#define TDS_PIN         A1      // TDS/EC sensor analog input

#define RELAY_CV        2       // Crystal Violet solenoid valve
#define RELAY_IODINE    3       // Iodine solenoid valve
#define RELAY_DECOLOR   4       // Decolorizer solenoid valve
#define RELAY_SAFRANIN  5       // Safranin solenoid valve
#define RELAY_WATER     6       // DI Water solenoid valve
#define RELAY_PUMP      7       // Peristaltic pump

#define BUTTON_START    8       // Start button (optional)

// Phase 2 hardware — aspiration + injection
#define VALVE_DIR       9       // 3/2-way directional valve
                                //   LOW  = intake path (manifold -> syringe)
                                //   HIGH = injection path (syringe -> chamber)
#define SYRINGE_PIN     10      // Syringe actuator (servo / stepper enable)

// ─── LCD SETUP ───────────────────────────────────────────────
// 20 characters wide, 4 rows. I2C address is usually 0x27 or 0x3F.
// If your LCD doesn't show anything, try changing 0x27 to 0x3F.

LiquidCrystal_I2C lcd(0x27, 20, 4);

// ─── STAIN TIMINGS (milliseconds) ───────────────────────────
// How long each valve stays open. Adjust these to calibrate staining.
// The DECOLORIZER timing is CRITICAL — start at 10 seconds.

unsigned long STAIN_CV_MS       = 60000;   // Crystal Violet: 60 sec
unsigned long STAIN_IODINE_MS   = 60000;   // Iodine: 60 sec
unsigned long STAIN_DECOLOR_MS  = 10000;   // Decolorizer: 10 sec (CRITICAL)
unsigned long STAIN_SAFRANIN_MS = 60000;   // Safranin: 60 sec
unsigned long WASH_MS           = 15000;   // DI water wash: 15 sec
unsigned long SETTLE_MS         = 120000;  // Bacteria settle time: 2 min

// Phase 1 timing — let the manifold fill before reading EC.
unsigned long MANIFOLD_FILL_MS  = 4000;    // Pump long enough to flood the EC probe
unsigned long EC_SETTLE_MS      = 1500;    // Dwell so the EC reading stabilises

// Phase 2 timings — keep in sync with python/config.py.
unsigned long ASPIRATION_MS     = 8000;    // Time to draw 1 mL
unsigned long INJECTION_MS      = 5000;    // Time to push 1 mL into chamber
unsigned long MIXING_MS         = 3000;    // Serpentine-channel mixing dwell

// ─── CALIBRATION VALUES ─────────────────────────────────────
// Adjust these based on your specific sensor readings.

float PH_OFFSET = 0.0;         // Add/subtract to correct pH reading
float PH_SLOPE = 5.7;          // pH units per volt (typical for PH-4502C)
float TDS_FACTOR = 0.5;        // Conversion factor for TDS sensor

// ─── STATE VARIABLES ─────────────────────────────────────────

bool stainingInProgress = false;
String lastResult = "";

// ─── SETUP ───────────────────────────────────────────────────

void setup() {
    // Start serial communication with laptop
    Serial.begin(9600);
    Serial.setTimeout(100);  // Don't block loop waiting for serial input

    // IMPORTANT: Set pins HIGH (OFF) BEFORE setting them as OUTPUT.
    // This prevents a momentary "blip" that could briefly open valves
    // during Arduino boot. Most relay modules are active-LOW.
    digitalWrite(RELAY_CV, HIGH);
    digitalWrite(RELAY_IODINE, HIGH);
    digitalWrite(RELAY_DECOLOR, HIGH);
    digitalWrite(RELAY_SAFRANIN, HIGH);
    digitalWrite(RELAY_WATER, HIGH);
    digitalWrite(RELAY_PUMP, HIGH);
    digitalWrite(VALVE_DIR, LOW);    // LOW = intake path at rest
    digitalWrite(SYRINGE_PIN, LOW);  // Syringe actuator disabled

    // Now set as outputs (pins are already at their safe default)
    pinMode(RELAY_CV, OUTPUT);
    pinMode(RELAY_IODINE, OUTPUT);
    pinMode(RELAY_DECOLOR, OUTPUT);
    pinMode(RELAY_SAFRANIN, OUTPUT);
    pinMode(RELAY_WATER, OUTPUT);
    pinMode(RELAY_PUMP, OUTPUT);
    pinMode(VALVE_DIR, OUTPUT);
    pinMode(SYRINGE_PIN, OUTPUT);

    // Optional start button
    pinMode(BUTTON_START, INPUT_PULLUP);

    // Set up LCD
    lcd.init();
    lcd.backlight();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("=== BIOQUA ===");
    lcd.setCursor(0, 1);
    lcd.print("System Ready");
    lcd.setCursor(0, 2);
    lcd.print("Press START or");
    lcd.setCursor(0, 3);
    lcd.print("send 'S' via Serial");

    Serial.println("BIOQUA_READY");
}

// ─── MAIN LOOP ───────────────────────────────────────────────

void loop() {
    // Read sensors continuously
    float pH = readPH();
    float ec = readEC();

    // Send sensor data to laptop every 2 seconds
    // Format: pH,EC (comma-separated)
    Serial.print(pH, 2);
    Serial.print(",");
    Serial.println(ec, 1);

    // Check for commands from laptop
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command == "S" || command == "START") {
            // Start the Gram staining sequence
            runGramStain();
        }
        else if (command.startsWith("RESULT:")) {
            // Laptop sent back classification result
            // Format: RESULT:Gram+ Cocci,HIGH
            lastResult = command.substring(7);
            displayResult(pH, ec, lastResult);
        }
        else if (command == "STATUS") {
            // Laptop requesting current status
            Serial.print("STATUS:");
            Serial.print(stainingInProgress ? "STAINING" : "IDLE");
            Serial.print(",pH=");
            Serial.print(pH, 2);
            Serial.print(",EC=");
            Serial.println(ec, 1);
        }
    }

    // Check physical start button
    if (digitalRead(BUTTON_START) == LOW && !stainingInProgress) {
        delay(200);  // Debounce
        if (digitalRead(BUTTON_START) == LOW) {
            runGramStain();
        }
    }

    // Update LCD with live sensor readings (when not staining)
    if (!stainingInProgress && lastResult == "") {
        lcd.setCursor(0, 2);
        lcd.print("pH: ");
        lcd.print(pH, 1);
        lcd.print("  EC: ");
        lcd.print(ec, 0);
        lcd.print("   ");  // Clear trailing chars
    }

    delay(2000);  // Read sensors every 2 seconds
}

// ─── SENSOR READING FUNCTIONS ────────────────────────────────

float readPH() {
    // Read pH sensor (PH-4502C module)
    // The sensor outputs 0-5V corresponding to pH 0-14
    int rawValue = analogRead(PH_PIN);
    float voltage = rawValue * (5.0 / 1023.0);

    // Convert voltage to pH (inverse relationship: higher voltage = lower pH)
    // PH-4502C neutral point is ~2.5V at pH 7. Slope ~-5.7 pH/V typical.
    // Calibrate with buffer solutions and adjust PH_OFFSET and PH_SLOPE.
    float pH = 7.0 + ((2.5 - voltage) * PH_SLOPE) + PH_OFFSET;

    // Clamp to valid range
    if (pH < 0) pH = 0;
    if (pH > 14) pH = 14;

    return pH;
}

float readEC() {
    // Read TDS/EC sensor
    // The sensor outputs an analog voltage proportional to conductivity
    int rawValue = analogRead(TDS_PIN);
    float voltage = rawValue * (5.0 / 1023.0);

    // Convert to TDS (ppm) — adjust TDS_FACTOR for your sensor
    float tds = (133.42 * voltage * voltage * voltage
                - 255.86 * voltage * voltage
                + 857.39 * voltage) * TDS_FACTOR;

    // Convert TDS to EC (microsiemens/cm): EC ≈ TDS * 2
    float ec = tds * 2.0;

    if (ec < 0) ec = 0;

    return ec;
}

// ─── FOUR-PHASE TEST CYCLE ──────────────────────────────────
// See docs/Phase.pdf. Each phase has a single entry point called by
// runGramStain() so the overall flow reads top-to-bottom.

void runGramStain() {
    stainingInProgress = true;
    Serial.println("CYCLE_START");

    phase1_ecTdsMeasurement();
    phase2_aspirateAndInject();
    phase3_gramStaining();

    stainingInProgress = false;
    Serial.println("CYCLE_DONE");

    // Phase 4 (risk fusion) happens on the laptop. This sketch returns
    // to the main loop and waits for a "RESULT:..." serial message that
    // displayResult() will render on the LCD.
}

// --- Phase 1: EC/TDS measurement on bulk water in the manifold ---
// Must run BEFORE the sample is sent to the chamber, because accurate
// TDS estimation needs volume (paper §Phase 1).
void phase1_ecTdsMeasurement() {
    Serial.println("PHASE:1_EC_TDS");
    lcdStatus("Phase 1: EC/TDS", 1);
    lcdStatus("Filling manifold", 2);

    // Fill the manifold so the EC probe is fully immersed.
    openValve(RELAY_WATER);
    openValve(RELAY_PUMP);
    delay(MANIFOLD_FILL_MS);
    closeValve(RELAY_PUMP);
    closeValve(RELAY_WATER);

    // Let EC reading stabilise, then sample.
    delay(EC_SETTLE_MS);
    float pH = readPH();
    float ec = readEC();
    Serial.print("PHASE1_READ:");
    Serial.print(pH, 2);
    Serial.print(",");
    Serial.println(ec, 1);
}

// --- Phase 2: Aspirate 1 mL, switch 3/2-way valve, inject into chamber ---
void phase2_aspirateAndInject() {
    Serial.println("PHASE:2_ASPIRATE_INJECT");
    lcdStatus("Phase 2: Aspirate", 1);
    lcdStatus("Drawing 1 mL", 2);

    // Aspiration: direct valve to intake path, run syringe backwards.
    digitalWrite(VALVE_DIR, LOW);    // LOW = intake (manifold -> syringe)
    digitalWrite(SYRINGE_PIN, HIGH); // Energise syringe actuator
    delay(ASPIRATION_MS);
    digitalWrite(SYRINGE_PIN, LOW);

    // Flip the 3/2-way valve to the injection path, then push.
    lcdStatus("Phase 2: Inject", 1);
    lcdStatus("To microchamber", 2);
    digitalWrite(VALVE_DIR, HIGH);   // HIGH = injection (syringe -> chamber)
    delay(500);                      // Let the valve mechanically settle
    digitalWrite(SYRINGE_PIN, HIGH);
    delay(INJECTION_MS);
    digitalWrite(SYRINGE_PIN, LOW);

    // Return valve to rest position so the chamber isn't backfed.
    digitalWrite(VALVE_DIR, LOW);

    // Brief mixing / settling dwell before staining starts.
    delay(MIXING_MS);
}

// --- Phase 3: On-chip Gram staining (sample already in microchamber) ---
void phase3_gramStaining() {
    Serial.println("PHASE:3_GRAM_STAIN");

    lcdStatus("Settling: 2 min", 1);
    Serial.println("STEP:SETTLE");
    delay(SETTLE_MS);

    // --- Step 1: Crystal Violet (primary stain) ---
    lcdStatus("Crystal Violet", 1);
    lcdStatus("60 sec...", 2);
    Serial.println("STEP:CRYSTAL_VIOLET");
    flowReagent(RELAY_CV, STAIN_CV_MS);
    washStep();

    // --- Step 2: Iodine (mordant) ---
    lcdStatus("Iodine Mordant", 1);
    lcdStatus("60 sec...", 2);
    Serial.println("STEP:IODINE");
    flowReagent(RELAY_IODINE, STAIN_IODINE_MS);
    washStep();

    // --- Step 3: Decolorizer (CRITICAL STEP) ---
    lcdStatus("** DECOLORIZER **", 1);
    lcdStatus("10 sec (critical!)", 2);
    Serial.println("STEP:DECOLORIZER");
    flowReagent(RELAY_DECOLOR, STAIN_DECOLOR_MS);
    washStep();  // Wash immediately to stop decolorization

    // --- Step 4: Safranin (counterstain) ---
    lcdStatus("Safranin", 1);
    lcdStatus("60 sec...", 2);
    Serial.println("STEP:SAFRANIN");
    flowReagent(RELAY_SAFRANIN, STAIN_SAFRANIN_MS);
    washStep();

    allValvesOff();
    lcdStatus("Staining Complete!", 1);
    lcdStatus("Analyzing...", 2);
    Serial.println("STAINING_DONE");
}

// ─── VALVE CONTROL HELPERS ───────────────────────────────────

void flowReagent(int relayPin, unsigned long durationMs) {
    // Open reagent valve + pump, wait, then close
    openValve(relayPin);
    openValve(RELAY_PUMP);
    delay(durationMs);
    closeValve(relayPin);
    closeValve(RELAY_PUMP);
}

void washStep() {
    // Flush with DI water between reagents
    openValve(RELAY_WATER);
    openValve(RELAY_PUMP);
    delay(WASH_MS);
    closeValve(RELAY_WATER);
    closeValve(RELAY_PUMP);
}

void openValve(int relayPin) {
    // Most relay modules are active LOW (LOW = ON)
    digitalWrite(relayPin, LOW);
}

void closeValve(int relayPin) {
    // HIGH = OFF for most relay modules
    digitalWrite(relayPin, HIGH);
}

void allValvesOff() {
    digitalWrite(RELAY_CV, HIGH);
    digitalWrite(RELAY_IODINE, HIGH);
    digitalWrite(RELAY_DECOLOR, HIGH);
    digitalWrite(RELAY_SAFRANIN, HIGH);
    digitalWrite(RELAY_WATER, HIGH);
    digitalWrite(RELAY_PUMP, HIGH);
    digitalWrite(VALVE_DIR, LOW);     // Return 3/2-way valve to rest (intake)
    digitalWrite(SYRINGE_PIN, LOW);   // Ensure syringe actuator is off
}

// ─── LCD DISPLAY HELPERS ─────────────────────────────────────

void lcdStatus(String message, int row) {
    lcd.setCursor(0, row);
    lcd.print("                    ");  // Clear the row (20 spaces)
    lcd.setCursor(0, row);
    lcd.print(message);
}

void displayResult(float pH, float ec, String result) {
    // Result format: "Gram+ Cocci,HIGH"
    int commaIndex = result.indexOf(',');
    String bacteria = result.substring(0, commaIndex);
    String risk = result.substring(commaIndex + 1);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("pH:");
    lcd.print(pH, 1);
    lcd.print(" EC:");
    lcd.print(ec, 0);

    lcd.setCursor(0, 1);
    lcd.print("Type: ");
    lcd.print(bacteria);

    lcd.setCursor(0, 2);
    lcd.print("Risk: ");
    lcd.print(risk);

    lcd.setCursor(0, 3);
    lcd.print("=== BIOQUA ===");
}
