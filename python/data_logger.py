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
Data Logger (FEATURE_DATA_LOGGING)
====================================
Saves every water test result to a CSV file with timestamps.
Also saves microscope images for reference.

This is enabled by setting FEATURE_DATA_LOGGING = True in config.py.

The CSV file can be opened in Excel or Google Sheets to analyze
water quality trends over time.
"""

import os
import sys
import csv
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import cv2
except ImportError:
    cv2 = None

from config import LOG_FILE, IMAGE_SAVE_DIR, PROJECT_ROOT

CSV_HEADERS = [
    "timestamp",
    "date",
    "time",
    "location",
    "ph",
    "ec_us_cm",
    "bacteria_class",
    "confidence_pct",
    "risk_level",
    "image_file",
    "notes",
]


class DataLogger:
    """Logs test results to CSV and saves images."""

    def __init__(self, location="Unknown"):
        self.location = location
        self._ensure_dirs()
        self._ensure_csv()
        print(f"Data logger initialized. Log file: {LOG_FILE}")

    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

    def _ensure_csv(self):
        """Create the CSV file with headers if it doesn't exist."""
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)

    def set_location(self, location):
        """Set the sample location name (e.g., 'Tap Water', 'River')."""
        self.location = location

    def log(self, ph, ec, bacteria_class, confidence, risk, frame=None, notes=""):
        """
        Log a single test result.

        Args:
            ph: pH sensor reading
            ec: EC sensor reading (microsiemens/cm)
            bacteria_class: AI classification result (e.g., "Gram+ Cocci")
            confidence: AI confidence (0.0 - 1.0)
            risk: Risk level ("LOW", "MODERATE", "HIGH")
            frame: Microscope image (numpy array) — saved if provided
            notes: Optional notes about this test
        """
        now = time.localtime()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", now)
        date_str = time.strftime("%Y-%m-%d", now)
        time_str = time.strftime("%H:%M:%S", now)

        # Save image if provided
        image_file = ""
        if frame is not None and cv2 is not None:
            filename = time.strftime(f"%Y%m%d_%H%M%S_{self.location}.jpg", now)
            filepath = os.path.join(IMAGE_SAVE_DIR, filename)
            cv2.imwrite(filepath, frame)
            image_file = os.path.relpath(filepath, PROJECT_ROOT)

        # Append to CSV
        row = [
            timestamp,
            date_str,
            time_str,
            self.location,
            f"{ph:.2f}",
            f"{ec:.1f}",
            bacteria_class,
            f"{confidence:.1%}",
            risk,
            image_file,
            notes,
        ]

        with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def get_all_entries(self):
        """Read all log entries."""
        entries = []
        if not os.path.exists(LOG_FILE):
            return entries

        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(row)
        return entries

    def get_summary(self):
        """Get a summary of all logged tests."""
        entries = self.get_all_entries()
        if not entries:
            return "No tests logged yet."

        total = len(entries)
        risk_counts = {"LOW": 0, "MODERATE": 0, "HIGH": 0}
        locations = set()

        for entry in entries:
            risk = entry.get("risk_level", "")
            if risk in risk_counts:
                risk_counts[risk] += 1
            locations.add(entry.get("location", "Unknown"))

        first_date = entries[0].get("date", "?")
        last_date = entries[-1].get("date", "?")

        summary = f"""
Test Log Summary
================
Total tests:  {total}
Date range:   {first_date} to {last_date}
Locations:    {', '.join(sorted(locations))}

Risk breakdown:
  LOW:      {risk_counts['LOW']}
  MODERATE: {risk_counts['MODERATE']}
  HIGH:     {risk_counts['HIGH']}
"""
        return summary


if __name__ == "__main__":
    logger = DataLogger("Test Run")
    print(logger.get_summary())
