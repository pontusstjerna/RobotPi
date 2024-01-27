from computer_vision.cv_module import CVModule
import cv2
import config

if not config.IS_DEBUG:
    from INA260_bridge import get_current, get_voltage
    import charge_controller


class VoltageDisplay(CVModule):
    def __init__(self):
        self.activate()

    def update(self, img):
        height, _, _ = img.shape

        if not config.IS_DEBUG:
            is_charging = charge_controller.is_charging_connected()
            cv2.putText(
                img,
                f"Voltage: {round(get_voltage(), 2)}v, charging {'enabled.' if charge_controller.is_charging_enabled() else 'disabled.'}",
                (0, height - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            cv2.putText(
                img,
                f"Current: {round(get_current(), 2)}mA{' - CHARGER CONNECTED' if is_charging else ''}",
                (0, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
