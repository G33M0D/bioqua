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
Test Arduino Serial Connection
================================
Run this to check if the laptop can talk to the Arduino.
It will show sensor readings (pH and EC) from the Arduino.

BEFORE RUNNING:
  1. Upload aquaguard_controller.ino to the Arduino
  2. Plug in the Arduino via USB

HOW TO RUN:
  python test_serial.py

WHAT YOU SHOULD SEE:
  - "Connected to Arduino on COM3" (or your port)
  - pH and EC values scrolling in the terminal

IF IT DOESN'T WORK:
  - Check the serial port in config.py (SERIAL_PORT)
  - Windows: Open Device Manager → Ports → note the COM number
  - Mac: Run 'ls /dev/tty.*' in Terminal
  - Linux: Run 'ls /dev/ttyUSB*' or 'ls /dev/ttyACM*'
  - Make sure Arduino IDE Serial Monitor is CLOSED
    (only one program can use the serial port at a time)
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import SERIAL_PORT, SERIAL_BAUD


def list_ports():
    """List available serial ports."""
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        if ports:
            print("Available serial ports:")
            for p in ports:
                print(f"  {p.device} — {p.description}")
        else:
            print("No serial ports found.")
            print("  - Is the Arduino plugged in via USB?")
            print("  - Do you have the CH340 driver installed?")
        return ports
    except ImportError:
        print("Cannot list ports (pyserial not installed)")
        return []


def main():
    print("=" * 50)
    print("  AquaGuard Serial Test")
    print("=" * 50)
    print()

    try:
        import serial
    except ImportError:
        print("ERROR: pyserial not installed.")
        print("Run: pip install pyserial")
        sys.exit(1)

    # List available ports
    list_ports()
    print()

    # Try to connect
    print(f"Connecting to {SERIAL_PORT} at {SERIAL_BAUD} baud...")

    try:
        arduino = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=2)
        time.sleep(2)  # Wait for Arduino to reset
        print(f"Connected!")
        print()
        print("Reading sensor data (press Ctrl+C to stop):")
        print("-" * 50)

        while True:
            line = arduino.readline().decode('utf-8', errors='ignore').strip()
            if line:
                if ',' in line and not line.startswith(('STEP:', 'STAINING', 'AQUAGUARD', 'STATUS:')):
                    try:
                        parts = line.split(',')
                        ph = float(parts[0])
                        ec = float(parts[1])
                        print(f"  pH: {ph:.2f}  |  EC: {ec:.1f} uS/cm")
                    except (ValueError, IndexError):
                        print(f"  Raw: {line}")
                else:
                    print(f"  Arduino: {line}")

    except serial.SerialException as e:
        print(f"ERROR: {e}")
        print()
        print("Troubleshooting:")
        print(f"  1. Change SERIAL_PORT in config.py (currently: '{SERIAL_PORT}')")
        print("  2. Close Arduino IDE Serial Monitor (only one program can connect)")
        print("  3. Unplug and replug the Arduino USB cable")
        print("  4. On Windows: install CH340 USB driver")
    except KeyboardInterrupt:
        print("\n\nTest stopped.")
        try:
            arduino.close()
        except NameError:
            pass  # arduino was never created

    print()
    print(f"If the correct port is different, update SERIAL_PORT in config.py")


if __name__ == "__main__":
    main()
