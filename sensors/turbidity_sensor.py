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
turbidity_sensor — Analog Turbidity Sensor Module
====================================================

What does turbidity measure?
    Turbidity is a measure of how cloudy or murky water is. It is
    measured in NTU (Nephelometric Turbidity Units). The sensor
    shines a light through the water and measures how much of that
    light gets scattered by tiny particles floating in it.

    - 0 NTU = perfectly clear (like distilled water)
    - 1 NTU = very clear tap water
    - 5 NTU = slightly hazy, getting concerning
    - 100+ NTU = visibly murky, like muddy water

Why does turbidity matter for drinking water?
    Cloudy water is not just ugly — those tiny particles can:

    1. **Hide bacteria** — Harmful microbes like E. coli can attach
       to particles, shielding them from disinfection (chlorine).

    2. **Indicate contamination** — A sudden rise in turbidity often
       means something got into the water supply (soil, sewage, rust).

    3. **Reduce UV effectiveness** — UV water purifiers cannot kill
       bacteria hiding behind particles.

    The WHO says drinking water should be below 1 NTU ideally, and
    must not exceed 5 NTU. AquaGuard uses 5 NTU as the threshold.

Hardware:
    The turbidity sensor module connects to an analog pin on the
    Arduino (configured in config.py as TURBIDITY_SENSOR_PIN). The
    Arduino reads the voltage, converts it to NTU, and sends it
    over serial as "TURB:3.2".

    This sensor is an OPTIONAL add-on. AquaGuard works without it.
"""

import serial
import time

from sensors.base_sensor import BaseSensor


class TurbiditySensor(BaseSensor):
    """
    Reads turbidity values from an analog sensor via Arduino serial.

    The Arduino sends lines like "TURB:3.2" where the number is
    the turbidity in NTU (Nephelometric Turbidity Units).

    Normal range: below 5 NTU (WHO maximum for drinking water).
    This is an optional add-on sensor.
    """

    # Maximum safe turbidity for drinking water (NTU)
    TURB_MAX = 5.0

    def __init__(self, pin="A3", serial_port="COM3", baud_rate=9600):
        """
        Set up the turbidity sensor.

        Args:
            pin (str):         Arduino analog pin (e.g. "A3").
            serial_port (str): Serial port where the Arduino is connected.
            baud_rate (int):   Communication speed — must match the Arduino sketch.
        """
        super().__init__(
            name="Turbidity Sensor",
            pin=pin,
            unit="NTU"
        )
        self.serial_port = serial_port
        self.baud_rate = baud_rate

    def read(self):
        """
        Read the current turbidity from the Arduino over serial.

        Opens the serial port, waits for a line starting with "TURB:",
        parses the number, and returns it.

        Returns:
            float: The turbidity reading in NTU.

        Raises:
            RuntimeError: If no valid turbidity reading is received
                          within the timeout period.
        """
        try:
            ser = serial.Serial(self.serial_port, self.baud_rate, timeout=5)
            time.sleep(2)  # Wait for Arduino to reset after serial connect

            # Try up to 10 lines to find a turbidity reading
            for _ in range(10):
                line = ser.readline().decode("utf-8").strip()
                if line.startswith("TURB:"):
                    value = float(line.split(":")[1])
                    ser.close()
                    return value

            ser.close()
            raise RuntimeError("No turbidity reading received from Arduino within timeout.")

        except serial.SerialException as e:
            raise RuntimeError(f"Could not connect to turbidity sensor on {self.serial_port}: {e}")

    def is_normal(self, value):
        """
        Check if the turbidity is within the safe drinking water limit.

        Args:
            value (float): A turbidity reading in NTU.

        Returns:
            bool: True if turbidity is below 5 NTU.

        Example:
            >>> sensor = TurbiditySensor()
            >>> sensor.is_normal(2.0)
            True
            >>> sensor.is_normal(8.0)
            False
        """
        return 0 <= value < self.TURB_MAX
