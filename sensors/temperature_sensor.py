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
temperature_sensor — DS18B20 Waterproof Temperature Sensor
============================================================

What does a temperature sensor measure?
    Exactly what it sounds like — the temperature of the water,
    measured in degrees Celsius (°C). The DS18B20 is a popular
    digital sensor that comes in a waterproof stainless steel probe,
    making it perfect for submerging in water samples.

Why does temperature matter for water quality?
    Temperature affects almost everything about water:

    1. **Bacteria growth** — Most harmful bacteria (like E. coli)
       grow fastest between 20°C and 45°C. Cold water slows them down.

    2. **Chemical reactions** — Higher temperatures speed up chemical
       reactions, which can release more contaminants from pipes.

    3. **Dissolved oxygen** — Warm water holds less oxygen. Fish and
       other aquatic life need dissolved oxygen to survive.

    4. **Taste** — Most people prefer drinking water between 15°C
       and 25°C. Very warm tap water can taste unpleasant.

    For AquaGuard, we consider 15°C to 30°C a normal range. Water
    outside this range is not necessarily unsafe, but it is worth
    flagging for further investigation.

Hardware:
    The DS18B20 uses a "1-Wire" digital protocol. It connects to a
    single digital pin on the Arduino (configured in config.py as
    TEMPERATURE_SENSOR_PIN). The Arduino reads the sensor and sends
    the value over serial as "TEMP:23.5".

    This sensor is an OPTIONAL add-on. AquaGuard works without it.
"""

import serial
import time

from sensors.base_sensor import BaseSensor


class TemperatureSensor(BaseSensor):
    """
    Reads water temperature from a DS18B20 sensor via Arduino serial.

    The Arduino sends lines like "TEMP:23.5" where the number is
    the temperature in degrees Celsius.

    Normal range: 15°C to 30°C (general drinking water guideline).
    This is an optional add-on sensor.
    """

    # Comfortable/normal temperature range for drinking water (°C)
    TEMP_MIN = 15.0
    TEMP_MAX = 30.0

    def __init__(self, pin="D7", serial_port="COM3", baud_rate=9600):
        """
        Set up the temperature sensor.

        Args:
            pin (str):         Arduino digital pin (e.g. "D7").
            serial_port (str): Serial port where the Arduino is connected.
            baud_rate (int):   Communication speed — must match the Arduino sketch.
        """
        super().__init__(
            name="Temperature Sensor",
            pin=pin,
            unit="°C"
        )
        self.serial_port = serial_port
        self.baud_rate = baud_rate

    def read(self):
        """
        Read the current water temperature from the Arduino over serial.

        Opens the serial port, waits for a line starting with "TEMP:",
        parses the number, and returns it.

        Returns:
            float: The temperature reading in degrees Celsius.

        Raises:
            RuntimeError: If no valid temperature reading is received
                          within the timeout period.
        """
        try:
            ser = serial.Serial(self.serial_port, self.baud_rate, timeout=5)
            time.sleep(2)  # Wait for Arduino to reset after serial connect

            # Try up to 10 lines to find a temperature reading
            for _ in range(10):
                line = ser.readline().decode("utf-8").strip()
                if line.startswith("TEMP:"):
                    value = float(line.split(":")[1])
                    ser.close()
                    return value

            ser.close()
            raise RuntimeError("No temperature reading received from Arduino within timeout.")

        except serial.SerialException as e:
            raise RuntimeError(f"Could not connect to temperature sensor on {self.serial_port}: {e}")

    def is_normal(self, value):
        """
        Check if the water temperature is in the comfortable range.

        Args:
            value (float): A temperature reading in °C.

        Returns:
            bool: True if temperature is between 15°C and 30°C (inclusive).

        Note:
            Water outside this range is not necessarily dangerous.
            Very cold water is generally safe to drink. This check
            is mainly to flag unusual conditions.

        Example:
            >>> sensor = TemperatureSensor()
            >>> sensor.is_normal(22.0)
            True
            >>> sensor.is_normal(5.0)
            False
        """
        return self.TEMP_MIN <= value <= self.TEMP_MAX
