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
ec_sensor — Electrical Conductivity (EC) / TDS Sensor
=======================================================

What does EC measure?
    Electrical Conductivity (EC) measures how well water conducts
    electricity. Pure water barely conducts at all. But when salts,
    minerals, or other dissolved substances are in the water, it
    conducts much better. EC is measured in microsiemens per
    centimeter (uS/cm).

Why does EC/TDS matter for drinking water?
    High EC means lots of dissolved minerals or contaminants. The WHO
    recommends drinking water have EC below 1500 uS/cm. Very high
    levels can indicate pollution, sewage, or industrial runoff.

Hardware:
    The TDS sensor probe connects to analog pin A1 on the Arduino.
    The Arduino converts the voltage to a conductivity value and
    sends it as the second value in the CSV serial output.
"""

from sensors.base_sensor import BaseSensor


class ECSensor(BaseSensor):
    """
    Reads Electrical Conductivity values from the Arduino serial data stream.

    The Arduino sends CSV lines like "7.02,850.5" where the SECOND
    value is EC in microsiemens per centimeter (uS/cm).

    Normal range: 0 to 1500 uS/cm (WHO guideline for drinking water).
    """

    EC_MAX = 1500

    def __init__(self, **kwargs):
        super().__init__(
            name="EC/TDS Sensor",
            pin="A1",
            unit="uS/cm"
        )
        self._last_value = None

    def read(self):
        """
        Read the current EC value from the shared serial connection.

        The Arduino sends "pH,EC" CSV lines (e.g., "7.02,850.5").
        This method parses the second value (EC).

        Returns:
            float: The conductivity reading in uS/cm, or last known value.
        """
        if self._shared_serial is None:
            if self._last_value is not None:
                return self._last_value
            raise RuntimeError("No serial connection. Call set_serial() first.")

        try:
            line = self._shared_serial.readline().decode('utf-8', errors='ignore').strip()
            if line and ',' in line:
                if not line.startswith(('STEP:', 'STAINING', 'AQUAGUARD', 'STATUS:', 'RESULT:')):
                    parts = line.split(',')
                    if len(parts) >= 2:
                        value = float(parts[1])
                        if value >= 0:  # Sanity check
                            self._last_value = value
                            return value
        except (ValueError, IndexError):
            pass

        if self._last_value is not None:
            return self._last_value
        return 500.0  # Default moderate EC

    def is_normal(self, value):
        """
        Check if the EC reading is within safe drinking water range.

        Returns:
            bool: True if EC is at or below 1500 uS/cm.
        """
        return 0 <= value <= self.EC_MAX
