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
base_sensor — Abstract Base Class for All Sensors
===================================================

Think of this file as the "blueprint" that every sensor must follow.
It defines the methods every sensor needs:

    name   — A human-friendly name like "pH Sensor"
    pin    — Which hardware pin it connects to
    unit   — The measurement unit (e.g. "pH", "uS/cm", "°C")
    read() — Take a reading and return a number
    is_normal(value) — Check if that number is in the safe range

Why use an abstract base class?
    It guarantees every sensor works the same way. The main program
    can loop over all sensors without caring what kind they are.
    This is a design pattern called "polymorphism" — one interface,
    many implementations.
"""

from abc import ABC, abstractmethod


class BaseSensor(ABC):
    """
    Abstract base class for AquaGuard sensor plugins.

    Every sensor you add to the system must inherit from this class
    and implement the read() and is_normal() methods.

    Attributes:
        name (str): Display name of the sensor (e.g. "pH Sensor").
        pin (str):  The hardware pin or port this sensor is connected to.
        unit (str): The unit of measurement (e.g. "pH", "NTU", "°C").
    """

    def __init__(self, name, pin, unit):
        self.name = name
        self.pin = pin
        self.unit = unit
        self._shared_serial = None  # Set by load_all_sensors()

    def set_serial(self, serial_connection):
        """
        Provide a shared serial connection from the controller.

        This avoids opening multiple serial ports to the same Arduino,
        which would cause conflicts and Arduino resets.

        Args:
            serial_connection: An open pyserial Serial object.
        """
        self._shared_serial = serial_connection

    @abstractmethod
    def read(self):
        """
        Take a measurement from the sensor hardware.

        Returns:
            float: The sensor reading in the sensor's unit.

        Raises:
            RuntimeError: If the sensor cannot be read.
        """
        pass

    @abstractmethod
    def is_normal(self, value):
        """
        Check whether a reading falls within the safe/normal range.

        Args:
            value (float): A sensor reading to evaluate.

        Returns:
            bool: True if the value is within the acceptable range.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}' pin='{self.pin}' unit='{self.unit}'>"
