import config
from time import sleep
from typing import Any

motor_bridge = None

if not config.IS_DEBUG:
    import motor_bridge

from functools import partial


def run_motors(left: float = 0, right: float = 0, for_seconds: float = 0.0):
    set_motors(left, right)
    sleep(for_seconds)
    set_motors(0, 0)


def set_motors(left: float = 0, right: float = 0):
    if motor_bridge:
        motor_bridge.set_left_motors(int(left * 100))
        motor_bridge.set_right_motors(int(right * 100))


class Controller:
    def __init__(self):
        self.power: float = 1

    def handle_message(self, message: str):
        if config.IS_DEBUG:
            return

        def set_power(left_power_factor: float, right_power_factor: float):
            return partial(
                set_motors,
                self.power * left_power_factor,
                self.power * right_power_factor,
            )

        controls: dict[str, Any] = {
            "stop": set_motors,
            "forward": set_power(1, 1),
            "backward": set_power(-1, -1),
            "reverse": self.reverse,
            "left": set_power(0.3, 1),
            "right": set_power(1, 0.3),
            "rot_left": set_power(-1, 1),
            "rot_right": set_power(1, -1),
            "set_power_low": partial(self.set_power, 0.3),
            "set_power_medium_low": partial(self.set_power, 0.5),
            "set_power_medium": partial(self.set_power, 0.75),
            "set_power_high": partial(self.set_power, 1.0),
        }

        command = controls.get(message)
        if command:
            command()
        else:
            print(f"Unkown command: {message}")

    def exec(self, message: str):
        self.handle_message(message)

    def exit(self):
        if motor_bridge:
            motor_bridge.cleanup()

    def reverse(self):
        self.power = -self.power

    def set_power(self, pwr: float):
        self.power = pwr
