from dotenv import load_dotenv

load_dotenv()

import json
from mqtt_client import MqttClient
from controller import Controller
from datetime import datetime, timedelta
from automation import Timer, redock
from functools import partial
from video import VideoProcessor
from status import get_status
from time import time
from computer_vision.qr_follower import QrFollower
from computer_vision.voltage_display import VoltageDisplay
from automation import redock
import config

if not config.IS_DEBUG:
    from INA260_bridge import get_voltage


class RobotPi:
    last_message = datetime.now()

    def __init__(self):
        self.started = datetime.now()
        self.last_connected = self.started
        self.is_running = False
        self.mqtt_client = MqttClient(on_message=self.on_message)
        self.controller = Controller()
        self.video = VideoProcessor()
        self.qr_follower = QrFollower()
#        self.qr_follower.deactivate()

        self.video.add_cv_module(self.qr_follower)
        self.video.add_cv_module(VoltageDisplay())

    def on_message(self, message):
        self.last_message = datetime.now()
        if not self.is_running:
            self.video.start()
            self.is_running = True

        if message == "started":
            self.mqtt_client.publish_message(
                "started",
                message=json.dumps(
                    {
                        "started": self.started.strftime("%Y-%m-%d %H:%M:%S"),
                        "lastConnected": self.last_connected.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                ),
            )
            self.last_connected = datetime.now()
        elif message == "status":
            if config.IS_DEBUG:
                self.mqtt_client.publish_message("status", None)
            else:
                self.mqtt_client.publish_message(
                    "status", message=json.dumps(get_status(self.controller))
                )
        elif message == "dock_start" or message == "follow_qr_start":
            self.qr_follower.activate()
        elif message == "dock_stop" or message == "follow_qr_stop":
            self.qr_follower.deactivate()
        else:
            self.controller.handle_message(message)

    def startup(self):
        self.mqtt_client.connect()
        try:
            while True:
                # curr = time()
                self.video.update()
                # print(f"Video update took: {round((time() - curr) * 1000, 0)} ms")
                # curr = time()

                if self.is_running and datetime.now() - self.last_message > timedelta(
                    seconds=config.IDLE_TIMEOUT_S
                ):
                    self.is_running = False
                    print("Timeout, stopping video stream.")
                    self.video.stop()
                # print(f"Rest took: {round((time() - curr) * 1000, 0)} ms")

                if not config.IS_DEBUG and not self.is_running:
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
                            redock(self.controller)

        except KeyboardInterrupt:
            print("Exiting...")
            pass

        self.video.stop()
        self.mqtt_client.disconnect()
        self.controller.exit()


print(f"Robotpi starting up with debug set to {config.IS_DEBUG}")
RobotPi().startup()
