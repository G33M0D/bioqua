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
ph_sensor — PH-4502C pH Sensor Module
=======================================

What does pH measure?
    pH tells you how acidic or basic (alkaline) water is on a scale
    from 0 to 14. Pure water is 7 (neutral). Lemon juice is about 2
    (very acidic). Baking soda in water is about 9 (basic).

Why does pH matter for drinking water?
    The World Health Organization (WHO) says safe drinking water
    should have a pH between 6.5 and 8.5. Water outside this range
    can taste bad, corrode pipes, or allow harmful bacteria to grow.

Hardware:
    The PH-4502C is an affordable analog pH sensor. It connects to
    the Arduino Mega via analog pin A0. The Arduino reads the voltage,
    converts it to a pH value, and sends it over serial.
"""

from sensors.base_sensor import BaseSensor


class PHSensor(BaseSensor):
    """
    Reads pH values from the Arduino serial data stream.

    The Arduino sends CSV lines like "7.02,850.5" where the FIRST
    value is pH. This class parses the pH value from that stream.

    Normal range: 6.5 to 8.5 (WHO drinking water guideline).
    """

    PH_MIN = 6.5
    PH_MAX = 8.5

    def __init__(self, **kwargs):
        super().__init__(
            name="pH Sensor",
            pin="A0",
            unit="pH"
        )
        self._last_value = None

    def read(self):
        """
        Read the current pH value from the shared serial connection.

        The Arduino sends "pH,EC" CSV lines (e.g., "7.02,850.5").
        This method parses the first value (pH).

        Returns:
            float: The pH reading (0-14), or last known value.
        """
        if self._shared_serial is None:
            if self._last_value is not None:
                return self._last_value
            raise RuntimeError("No serial connection. Call set_serial() first.")

        try:
            line = self._shared_serial.readline().decode('utf-8', errors='ignore').strip()
            if line and ',' in line:
                # Skip Arduino status messages
                if not line.startswith(('STEP:', 'STAINING', 'AQUAGUARD', 'STATUS:', 'RESULT:')):
                    parts = line.split(',')
                    value = float(parts[0])
                    if 0 <= value <= 14:  # Sanity check
                        self._last_value = value
                        return value
        except (ValueError, IndexError):
            pass

        if self._last_value is not None:
            return self._last_value
        return 7.0  # Default neutral pH

    def is_normal(self, value):
        """
        Check if the pH reading is within safe drinking water range.

        Returns:
            bool: True if pH is between 6.5 and 8.5 (inclusive).
        """
        return self.PH_MIN <= value <= self.PH_MAX
