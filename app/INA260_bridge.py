import board
import busio
import adafruit_ina260
from typing import Any

i2c: Any = None
ina260: Any = None

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    ina260 = adafruit_ina260.INA260(i2c)
except ValueError as e:
    print(f"Could not connect to I2C: {e}")


def get_current() -> float:
    try:
        return ina260.current if ina260 else -1
    except OSError as e:
        print(f"Error when reading current: {e}")
        return -1


def get_voltage() -> float:
    try:
        return ina260.voltage if ina260 else -1
    except OSError as e:
        print(f"Error when reading voltage: {e}")
        return -1
