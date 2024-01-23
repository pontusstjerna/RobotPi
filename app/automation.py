from datetime import datetime
import time
import config

if not config.IS_DEBUG:
    from INA260_bridge import get_voltage

class Timer:
    start_time = datetime.now()

    def __init__(self, interval, action):
        self.interval = interval
        self.action = action

    def update(self):
        if self.start_time + self.interval <= datetime.now():
            self.start_time = datetime.now()
            self.action()


def redock(controller):
    voltage = get_voltage()
    if voltage < config.REDOCK_VOLTAGE:
        if voltage < 5:
            print(
                f"Voltage unreasonably low ({round(voltage, 2)}v) - will not redock"
            )
        else:
            print(
                f"Voltage below {config.REDOCK_VOLTAGE}v ({round(voltage, 2)}v), will redock"
            )
            controller.handle_message("set_power_low")
            controller.handle_message("backward")
            time.sleep(0.25)
            controller.handle_message("stop")
            time.sleep(1)
            controller.handle_message("forward")
            time.sleep(0.25)
            controller.handle_message("stop")
