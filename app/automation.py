from datetime import datetime

class Timer:
    start_time = datetime.now()

    def __init__(self, interval, action):
        self.interval = interval
        self.action = action

    def update(self):
        if self.start_time + self.interval <= datetime.now():
            self.start_time = datetime.now()
            self.action()

