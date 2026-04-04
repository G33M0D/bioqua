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
sensors — Modular Sensor Plugin Package
========================================

This package lets you add new water-quality sensors to AquaGuard
without changing the main code. Each sensor is a small Python class
that knows how to read one measurement (like pH or temperature).

How it works:
    1. config.py has a toggle called FEATURE_MODULAR_SENSORS.
    2. When that toggle is True, load_all_sensors() discovers and
       loads every available sensor plugin in this folder.
    3. Each sensor class inherits from BaseSensor and implements
       a read() method that returns a number and an is_normal()
       method that checks if that number is safe.
    4. Sensors share the Arduino serial connection from controller.py
       to avoid port conflicts.

Usage:
    from sensors import load_all_sensors

    active_sensors = load_all_sensors(arduino_serial=my_serial_connection)
    for sensor in active_sensors:
        value = sensor.read()
        print(f"{sensor.name}: {value} {sensor.unit}  OK={sensor.is_normal(value)}")
"""

import os
import sys

# Allow imports from the python/ directory where config.py lives
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from sensors.ph_sensor import PHSensor
from sensors.ec_sensor import ECSensor
from sensors.temperature_sensor import TemperatureSensor
from sensors.turbidity_sensor import TurbiditySensor


def load_all_sensors(arduino_serial=None):
    """
    Check if modular sensors are enabled and return a list of sensor instances.

    Args:
        arduino_serial: An open pyserial Serial object from controller.py.
                        Shared by all sensors to avoid port conflicts.

    Returns:
        list[BaseSensor]: A list of sensor objects. Empty if feature is off.
    """
    from config import FEATURE_MODULAR_SENSORS

    if not FEATURE_MODULAR_SENSORS:
        return []

    # Build the list of all available sensors
    sensors = []

    # Core sensors (always loaded when feature is on)
    sensors.append(PHSensor())
    sensors.append(ECSensor())

    # Optional add-on sensors
    try:
        from config import TEMPERATURE_SENSOR_PIN
        sensors.append(TemperatureSensor(pin=TEMPERATURE_SENSOR_PIN))
    except ImportError:
        pass

    try:
        from config import TURBIDITY_SENSOR_PIN
        sensors.append(TurbiditySensor(pin=TURBIDITY_SENSOR_PIN))
    except ImportError:
        pass

    # Share the Arduino serial connection with all sensors
    if arduino_serial:
        for sensor in sensors:
            sensor.set_serial(arduino_serial)

    loaded_names = [s.name for s in sensors]
    print(f"[sensors] Loaded {len(sensors)} sensor(s): {', '.join(loaded_names)}")

    return sensors
