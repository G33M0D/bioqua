# ============================================================
# BIOQUA: AI-Assisted Water Quality Monitoring System
#
# Authors         : Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D.
# Year            : 2026
# License         : MIT License
#
# This project is the original work of the authors.
# Unauthorized removal of this notice is prohibited.
# ============================================================

"""
BIOQUA Configuration
=======================
Change any setting below. All optional features are OFF by default.
Enable them one at a time when you're ready to explore.

To customize BIOQUA, only edit THIS file — you never need to
touch the other Python scripts unless you want to.
"""

import os

# ─── PATHS ────────────────────────────────────────────────────
# These are relative to the project root (where README.md lives)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── CORE (always on) ────────────────────────────────────────

# Serial port — how the laptop talks to the Arduino
# Windows: "COM3" (check Device Manager → Ports)
# Mac:     "/dev/tty.usbmodem..." (run: ls /dev/tty.* in Terminal)
# Linux:   "/dev/ttyUSB0"
SERIAL_PORT = "COM3"
SERIAL_BAUD = 9600

# Camera — which USB camera to use for the microscope
# Try 0 first. If the wrong camera shows (e.g., your webcam), try 1 or 2.
CAMERA_INDEX = 0

# AI Model — path to the trained model file
# After training, your model will be saved here automatically.
AI_MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "bioqua_model.h5")

# Class names — MUST match alphabetical order of folder names in training_data/
# because Keras flow_from_directory() assigns class indices alphabetically.
# Folders: gram_negative_bacilli, gram_negative_cocci, gram_positive_bacilli,
#          gram_positive_cocci, no_bacteria → indices 0, 1, 2, 3, 4
CLASS_NAMES = [
    "Gram- Bacilli",
    "Gram- Cocci",
    "Gram+ Bacilli",
    "Gram+ Cocci",
    "No Bacteria",
]

# ─── FEATURE TOGGLES ─────────────────────────────────────────
# Flip these to True when you're ready to explore each feature.
# Start with everything False — get the basic system working first.

FEATURE_DATA_LOGGING = False        # Save every test to CSV + capture images
FEATURE_PDF_REPORTS = False         # Generate printable PDF reports
FEATURE_MODULAR_SENSORS = False     # Enable plug-and-play sensor expansion
FEATURE_LEARNING_MODULES = False    # Interactive educational guides
FEATURE_BLUETOOTH_MOBILE = False    # ESP32 Bluetooth + phone app

# ─── SENSOR SETTINGS ─────────────────────────────────────────
# What counts as "normal" water — used for risk classification

PH_NORMAL_MIN = 6.5     # Below this = acidic (risky)
PH_NORMAL_MAX = 8.5     # Above this = alkaline (risky)
EC_NORMAL_MAX = 1500     # microsiemens/cm — above this = high dissolved solids

# Arduino analog pins for core sensors
PH_SENSOR_PIN = "A0"
EC_SENSOR_PIN = "A1"

# ─── GRAM STAIN TIMINGS (seconds) ────────────────────────────
# How long each solenoid valve stays open during automated staining.
# These match the standard Gram stain protocol.

STAIN_CRYSTAL_VIOLET = 60   # Step 1: Primary stain (purple)
STAIN_IODINE = 60           # Step 2: Mordant (fixes the purple)
STAIN_DECOLORIZER = 10      # Step 3: CRITICAL — too long = false Gram-negative
STAIN_SAFRANIN = 60          # Step 4: Counterstain (pink for Gram-negative)
WASH_DURATION = 15           # DI water rinse between each step
SETTLE_DURATION = 120        # Let bacteria settle before staining (seconds)

# ─── AI SETTINGS ──────────────────────────────────────────────

# Minimum confidence to trust a classification result.
# If the AI is less than 60% sure, it will say "Uncertain".
AI_CONFIDENCE_THRESHOLD = 0.6

# Image size expected by the model (Teachable Machine uses 224x224)
AI_IMAGE_SIZE = (224, 224)

# HSV color ranges for Gram stain detection
# Adjust these if your microscope lighting makes colors look different.
# Format: ((H_min, S_min, V_min), (H_max, S_max, V_max))
HSV_GRAM_POSITIVE = ((120, 50, 50), (160, 255, 255))    # Purple range
HSV_GRAM_NEGATIVE_1 = ((0, 50, 100), (20, 255, 255))    # Pink range (low hue)
HSV_GRAM_NEGATIVE_2 = ((160, 50, 100), (180, 255, 255))  # Pink range (high hue)

# Shape classification thresholds
CIRCULARITY_COCCI = 0.7     # Above this = round (cocci)
ASPECT_RATIO_BACILLI = 2.0  # Above this = rod-shaped (bacilli)
MIN_CONTOUR_AREA = 50       # Ignore contours smaller than this (noise)

# ─── TAXONOMY — TABLE 2.1 (Phase II Classifications) ─────────
# The paper classifies bacteria into six final classes based on Gram stain
# + morphology. The MobileNetV2 stand-in ships with a simpler 5-class model
# (no chains/clusters split); the two Random Forest models described in the
# paper are what ultimately distinguish them. See docs/Phase.pdf §C.2.2.

BACTERIA_CLASSES = [
    "Gram-positive rods",
    "Gram-positive cocci (chains)",
    "Gram-positive cocci (clusters)",
    "Gram-positive cocci",            # bare label, no chain/cluster split
    "Gram-negative rods",
    "Gram-negative cocci",
]

# The UI/LCD still uses short labels (CLASS_NAMES below); this map translates
# them into the paper's Table 2.1 classes for the gated fusion lookup.
CLASS_NAME_TO_PAPER_CLASS = {
    "Gram- Bacilli": "Gram-negative rods",
    "Gram- Cocci":   "Gram-negative cocci",
    "Gram+ Bacilli": "Gram-positive rods",
    "Gram+ Cocci":   "Gram-positive cocci",
    "No Bacteria":   None,
}

# ─── CHEMICAL CONDITIONS — TABLE 2.2 (Phase III) ─────────────
CHEMICAL_SEVERE = "Severe Chemical Contamination"       # High TDS spike + pH drop
CHEMICAL_MODERATE = "Moderate Chemical Contamination"   # Moderate TDS, slight/stable pH
CHEMICAL_STABLE = "Chemically Stable Water"             # No TDS spike, normal pH

# Thresholds used by derive_chemical_condition() (see controller.py).
# EC is the proxy for TDS; a spike correlates with a pH drop per Phase III.
EC_SPIKE_HIGH = 2500         # microsiemens/cm — High TDS spike
EC_SPIKE_MODERATE = EC_NORMAL_MAX   # 1500 — Moderate TDS increase
PH_DROP_THRESHOLD = PH_NORMAL_MIN   # 6.5 — below this = pH drop

# ─── RISK LEVELS — TABLE 2.3 (Phase IV) ──────────────────────
RISK_HIGH          = "High-Risk Contamination"
RISK_MODERATE_HIGH = "Moderate-High Risk"
RISK_MODERATE      = "Moderate Risk"
RISK_MODERATE_BIO  = "Moderate Biological Risk"
RISK_LOW           = "Low-Risk Contamination"
RISK_NONE          = "Safe"                # not in paper table; used when no bacteria + stable chemistry

# Short code used on the 20x4 LCD and over serial (Arduino only sees this).
RISK_SHORT_CODE = {
    RISK_HIGH:          "HIGH",
    RISK_MODERATE_HIGH: "MOD-HIGH",
    RISK_MODERATE:      "MOD",
    RISK_MODERATE_BIO:  "MOD-BIO",
    RISK_LOW:           "LOW",
    RISK_NONE:          "SAFE",
}

# ─── GATED FUSION TABLE — Phase IV decision table (Table 2.3) ─
# Keyed by (paper bacteria class, Phase I chemical condition).
# Value: (risk level, interpretation).
#
# DELIBERATE RETENTION: rows for stable-chemistry Gram-negative rods and
# Gram-negative cocci use RISK_MODERATE_BIO ("Moderate Biological Risk")
# from the original Phase.pdf. The revised Chapter 3 PDF moves both rows
# to RISK_MODERATE, but the same revised PDF still lists "Moderate
# Biological Risk" as a defined level — likely an editing inconsistency.
# We preserve the more-specific label because pathogen-present-with-
# normal-chemistry is a meaningfully distinct failure mode worth naming.
GATED_FUSION_TABLE = {
    ("Gram-negative rods", CHEMICAL_SEVERE):   (RISK_HIGH,          "Pathogenic microorganisms with heavy chemical pollution"),
    ("Gram-negative rods", CHEMICAL_MODERATE): (RISK_MODERATE_HIGH, "Harmful microorganisms with the development of pollution"),
    ("Gram-negative rods", CHEMICAL_STABLE):   (RISK_MODERATE_BIO,  "Microorganism contamination was detected, but with normal chemical parameters"),

    ("Gram-positive cocci (chains)", CHEMICAL_SEVERE):   (RISK_HIGH,     "Microorganisms present with severe physicochemical pollution"),
    ("Gram-positive cocci (chains)", CHEMICAL_MODERATE): (RISK_MODERATE, "Developing microbial growth with increasing pollution"),
    ("Gram-positive cocci (chains)", CHEMICAL_STABLE):   (RISK_LOW,      "Limited microbial presence with absent chemical pollution"),

    ("Gram-positive cocci (clusters)", CHEMICAL_SEVERE):   (RISK_HIGH,     "Microorganism clusters with polluted water"),
    ("Gram-positive cocci (clusters)", CHEMICAL_MODERATE): (RISK_MODERATE, "Microorganism clusters with increasing polluted water"),
    ("Gram-positive cocci (clusters)", CHEMICAL_STABLE):   (RISK_LOW,      "Minimal microbial contamination and pollution"),

    ("Gram-positive rods", CHEMICAL_SEVERE):   (RISK_HIGH,     "Microbial rods detected with pollution"),
    ("Gram-positive rods", CHEMICAL_MODERATE): (RISK_MODERATE, "Microbial rods detected with developing pollution"),
    ("Gram-positive rods", CHEMICAL_STABLE):   (RISK_LOW,      "Possibly microbial rods only"),

    ("Gram-negative cocci", CHEMICAL_SEVERE):   (RISK_HIGH,          "Potential pathogenic bacteria with polluted water"),
    ("Gram-negative cocci", CHEMICAL_MODERATE): (RISK_MODERATE_HIGH, "Possible harmful microorganisms with developing pollution"),
    ("Gram-negative cocci", CHEMICAL_STABLE):   (RISK_MODERATE_BIO,  "Microbial presence detected but chemically stable water"),
}

# The paper's Table 2.3 omits the bare "Gram-positive cocci" class that the
# MobileNetV2 stand-in can produce. Treat it as the "chains" sub-class —
# the conservative middle row — until the two-RF morphology model lands.
GATED_FUSION_FALLBACK = {
    "Gram-positive cocci": "Gram-positive cocci (chains)",
}

# ─── DATA LOGGING (only used if FEATURE_DATA_LOGGING = True) ─

LOG_FILE = os.path.join(PROJECT_ROOT, "results", "test_log.csv")
IMAGE_SAVE_DIR = os.path.join(PROJECT_ROOT, "results", "images")

# ─── OPTIONAL SENSOR PINS (only if FEATURE_MODULAR_SENSORS = True) ─

TEMPERATURE_SENSOR_PIN = "D7"    # DS18B20 digital temperature sensor
TURBIDITY_SENSOR_PIN = "A3"     # Analog turbidity sensor module

# ─── BLUETOOTH (only used if FEATURE_BLUETOOTH_MOBILE = True) ─

ESP32_BLUETOOTH_NAME = "BIOQUA"

# ─── ARDUINO PIN ASSIGNMENTS ─────────────────────────────────
# IMPORTANT: These values are for REFERENCE ONLY on the Python side.
# The Arduino sketch has its OWN copy of pin assignments and timings.
# If you change values here, you MUST also update the Arduino sketch
# (arduino/bioqua_controller/bioqua_controller.ino) to match!

RELAY_PINS = {
    "crystal_violet": 2,   # Relay 1 → Solenoid valve 1
    "iodine": 3,           # Relay 2 → Solenoid valve 2
    "decolorizer": 4,      # Relay 3 → Solenoid valve 3
    "safranin": 5,         # Relay 4 → Solenoid valve 4
    "di_water": 6,         # Relay 5 → Solenoid valve 5
    "pump": 7,             # Relay 6 → Peristaltic pump
}

# ─── PHASE 2 HARDWARE — Aspiration and Injection ─────────────
# These components sit between the sensor manifold (Phase 1) and the
# microfluidic chamber (Phase 3). See docs/Phase.pdf §Phase 2.
#
#   Aspiration: DIR_VALVE routed to intake → syringe pulls 1 mL
#   Injection:  DIR_VALVE routed to chamber → syringe pushes 1 mL
#
# The 3/2-way valve is on Arduino pin D9; the syringe actuator (servo
# or stepper enable) is on pin D10. Adjust to match your wiring.
VALVE_3_2_PIN = 9                  # 3/2-way directional valve
SYRINGE_ACTUATOR_PIN = 10          # Syringe drive (servo / stepper enable)

MICROCHAMBER_VOLUME_ML = 1.0       # Syringe draw volume — matches chamber
ASPIRATION_DURATION_MS = 8000      # Time to draw 1 mL at rated speed
INJECTION_DURATION_MS = 5000       # Time to push 1 mL into the chamber
MIXING_DURATION_MS = 3000          # Extra dwell for serpentine-channel mixing

LCD_ADDRESS = 0x27  # I2C address of the 20x4 LCD (common: 0x27 or 0x3F)
