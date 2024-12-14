import board
import busio
import adafruit_ina260
from typing import Any

i2c: Any = None
ina260: Any = None

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    ina260 = adafruit_ina260.INA260(i2c)
except ValueError:
    print("Could not connect to I2C!")


def get_current() -> float:
    return ina260.current if ina260 else "Unknown"


def get_voltage() -> float:
    return ina260.voltage if ina260 else "Unkown"
