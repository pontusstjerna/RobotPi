from datetime import datetime
import time

class Timer:
    start_time = datetime.now()

    def __init__(self, interval, action):
        self.interval = interval
        self.action = action

    def update(self):
        if self.start_time + self.interval >= datetime.now():
            self.start_time = datetime.now()
            self.action()

def redock(controller):
    controller.handle_message("set_power_low")
    controller.handle_message("backward")
    time.sleep(0.25)
    controller.handle_message("stop")
    time.sleep(1)
    controller.handle_message("forward")
    time.sleep(0.25)
    controller.handle_message("stop")