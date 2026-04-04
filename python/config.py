# ============================================================
# AquaGuard: AI-Powered Bacteria Detection for Safe Drinking Water
#
# Original Author : Guillanne Marie Agreda
# Year            : 2026
# License         : MIT License
#
# This project is the original work of the author.
# Unauthorized removal of this notice is prohibited.
# ============================================================

"""
AquaGuard Configuration
=======================
Change any setting below. All optional features are OFF by default.
Enable them one at a time when you're ready to explore.

To customize AquaGuard, only edit THIS file — you never need to
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
AI_MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "aquaguard_model.h5")

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

# ─── RISK CLASSIFICATION ─────────────────────────────────────
# How sensor data + bacteria classification combine into a risk level.

RISK_RULES = {
    "HIGH": "Gram-negative bacteria detected OR pH outside 5.0-9.0",
    "MODERATE": "Any bacteria detected OR pH/EC slightly outside normal",
    "LOW": "No bacteria detected AND normal pH AND normal EC",
}

# ─── DATA LOGGING (only used if FEATURE_DATA_LOGGING = True) ─

LOG_FILE = os.path.join(PROJECT_ROOT, "results", "test_log.csv")
IMAGE_SAVE_DIR = os.path.join(PROJECT_ROOT, "results", "images")

# ─── OPTIONAL SENSOR PINS (only if FEATURE_MODULAR_SENSORS = True) ─

TEMPERATURE_SENSOR_PIN = "D7"    # DS18B20 digital temperature sensor
TURBIDITY_SENSOR_PIN = "A3"     # Analog turbidity sensor module

# ─── BLUETOOTH (only used if FEATURE_BLUETOOTH_MOBILE = True) ─

ESP32_BLUETOOTH_NAME = "AquaGuard"

# ─── ARDUINO PIN ASSIGNMENTS ─────────────────────────────────
# IMPORTANT: These values are for REFERENCE ONLY on the Python side.
# The Arduino sketch has its OWN copy of pin assignments and timings.
# If you change values here, you MUST also update the Arduino sketch
# (arduino/aquaguard_controller/aquaguard_controller.ino) to match!

RELAY_PINS = {
    "crystal_violet": 2,   # Relay 1 → Solenoid valve 1
    "iodine": 3,           # Relay 2 → Solenoid valve 2
    "decolorizer": 4,      # Relay 3 → Solenoid valve 3
    "safranin": 5,         # Relay 4 → Solenoid valve 4
    "di_water": 6,         # Relay 5 → Solenoid valve 5
    "pump": 7,             # Relay 6 → Peristaltic pump
}

LCD_ADDRESS = 0x27  # I2C address of the 20x4 LCD (common: 0x27 or 0x3F)
