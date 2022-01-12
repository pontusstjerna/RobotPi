import L298NHBridge
import servo_controller
from functools import partial

def set_motors(left = 0, right = 0):

    # They are inverted...
    L298NHBridge.setMotorRight(left)
    L298NHBridge.setMotorLeft(right)

class Controller:
    def __init__(self):
        self.power = 1

    def handle_message(self, message):
        def set_power(left_power_factor, right_power_factor):
            return partial(set_motors, self.power * left_power_factor, self.power * right_power_factor)

        controls = {
            "stop": set_motors,
            "forward": set_power(1, 1),
            "backward": set_power(-1, -1),
            "reverse": self.reverse,
            "left": set_power(0.7, 1),
            "right": set_power(1, 0.7),
            "rot_left": set_power(-1, 1),
            "rot_right": set_power(1, -1),
            "set_power_low": partial(self.set_power, 0.15),
            "set_power_medium_low": partial(self.set_power, 0.3),
            "set_power_medium": partial(self.set_power, 0.5),
            "set_power_high": partial(self.set_power, 1.0),
            "tilt_camera_stop": servo_controller.stop,
            "tilt_camera_up": servo_controller.increase_angle,
            "tilt_camera_down": servo_controller.decrease_angle
        }

        command = controls.get(message)
        if command: command()
        else: print(f"Unkown command: {message}")

    def exit(self):
        L298NHBridge.exit()
        servo_controller.exit()

    def reverse(self):
        self.power = -self.power

    def set_power(self, pwr):
        self.power = pwr

    





