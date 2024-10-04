import board
import busio
import adafruit_ina260

i2c = busio.I2C(board.SCL, board.SDA)
ina260 = adafruit_ina260.INA260(i2c)


def get_current() -> float:
    return ina260.current


def get_voltage() -> float:
    return ina260.voltage
