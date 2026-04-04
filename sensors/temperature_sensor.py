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
    The temperature of the water in degrees Celsius (°C).

Why does temperature matter for water quality?
    - Bacteria growth is fastest between 20°C and 45°C
    - Higher temperatures speed up chemical reactions
    - Warm water holds less dissolved oxygen
    - Most people prefer drinking water between 15°C and 25°C

Hardware:
    The DS18B20 uses a "1-Wire" digital protocol on one Arduino pin.
    The Arduino reads it and includes the value in serial output.

    This sensor is an OPTIONAL add-on. AquaGuard works without it.
"""

from sensors.base_sensor import BaseSensor


class TemperatureSensor(BaseSensor):
    """
    Reads water temperature from Arduino serial data.

    Uses the shared serial connection from controller.py.
    The Arduino must send lines containing "TEMP:" prefix
    (requires updating the Arduino sketch to include temperature reading).

    Normal range: 15°C to 30°C (general drinking water guideline).
    """

    TEMP_MIN = 15.0
    TEMP_MAX = 30.0

    def __init__(self, pin="D7", **kwargs):
        super().__init__(
            name="Temperature Sensor",
            pin=pin,
            unit="°C"
        )
        self._last_value = None

    def read(self):
        """
        Read the current water temperature from the shared serial connection.

        Returns:
            float: Temperature in °C, or last known value, or default 22.0.
        """
        if self._shared_serial is None:
            if self._last_value is not None:
                return self._last_value
            return 22.0  # Default room temperature

        try:
            line = self._shared_serial.readline().decode('utf-8', errors='ignore').strip()
            if line and line.startswith("TEMP:"):
                value = float(line.split(":")[1])
                if -10 <= value <= 100:  # Sanity check
                    self._last_value = value
                    return value
        except (ValueError, IndexError):
            pass

        if self._last_value is not None:
            return self._last_value
        return 22.0

    def is_normal(self, value):
        """Check if temperature is in comfortable range (15-30°C)."""
        return self.TEMP_MIN <= value <= self.TEMP_MAX
