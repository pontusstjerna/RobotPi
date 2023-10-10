from computer_vision.cv_module import CVModule
import cv2
import config

if not config.IS_DEBUG:
    from INA260_bridge import get_current, get_voltage


class VoltageDisplay(CVModule):
    def __init__(self, charge_controller):
        self.activate()
        self.charge_controller = charge_controller

    def update(self, img):
        height, _, _ = img.shape

        if not config.IS_DEBUG:
            cv2.line(
                img,
                (0, height - 100),
                (400, int((height - 100) - 100000 * self.charge_controller.calc_charge_slope())),
                (0, 255, 0),
                2,
            )
            cv2.putText(
                img,
                f"Voltage: {round(get_voltage(), 2)}v, slope: {round(self.charge_controller.calc_charge_slope() * 10000, 2)}" + (", CHARGING"
                if self.charge_controller.is_charging()
                else ""),
                (0, height - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            cv2.putText(
                img,
                f"Current: {round(get_current(), 2)}mA",
                (0, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
