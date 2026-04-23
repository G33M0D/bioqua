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
turbidity_sensor — Water Turbidity / Clarity Sensor
=====================================================

What does turbidity measure?
    Turbidity is how cloudy or murky the water looks. It is measured
    in NTU (Nephelometric Turbidity Units). Clear water has low NTU.

Why does turbidity matter?
    - Cloudy water can hide bacteria and parasites
    - WHO says safe drinking water should be below 5 NTU
    - High turbidity can indicate pollution or runoff

Hardware:
    The turbidity sensor connects to an Arduino analog pin.
    This is an OPTIONAL add-on. BIOQUA works without it.
"""

from sensors.base_sensor import BaseSensor


class TurbiditySensor(BaseSensor):
    """
    Reads turbidity values from Arduino serial data.

    Uses the shared serial connection from controller.py.
    The Arduino must send lines containing "TURB:" prefix
    (requires updating the Arduino sketch to include turbidity reading).

    Normal range: below 5 NTU (WHO maximum for drinking water).
    """

    TURB_MAX = 5.0

    def __init__(self, pin="A3", **kwargs):
        super().__init__(
            name="Turbidity Sensor",
            pin=pin,
            unit="NTU"
        )
        self._last_value = None

    def read(self):
        """
        Read the current turbidity from the shared serial connection.

        Returns:
            float: Turbidity in NTU, or last known value, or default 1.0.
        """
        if self._shared_serial is None:
            if self._last_value is not None:
                return self._last_value
            return 1.0  # Default clear water

        try:
            line = self._shared_serial.readline().decode('utf-8', errors='ignore').strip()
            if line and line.startswith("TURB:"):
                value = float(line.split(":")[1])
                if 0 <= value <= 1000:  # Sanity check
                    self._last_value = value
                    return value
        except (ValueError, IndexError):
            pass

        if self._last_value is not None:
            return self._last_value
        return 1.0

    def is_normal(self, value):
        """Check if turbidity is below 5 NTU (WHO limit)."""
        return 0 <= value < self.TURB_MAX
