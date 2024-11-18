from dotenv import load_dotenv

load_dotenv()

import json
from mqtt_client import MqttClient
from controller import Controller
from datetime import datetime, timedelta
from video import VideoProcessor
from status import get_status
from computer_vision.voltage_display import VoltageDisplay
import config
import os


class RobotPi:
    last_message = datetime.now()
    attempted_redocks = 0

    def __init__(self):
        self.started = datetime.now()
        self.last_connected = self.started
        self.is_running = False
        self.mqtt_client = MqttClient(on_message=self.on_message, on_connect=self.start)
        self.controller = Controller()
        self.video = VideoProcessor()
        self.video.add_cv_module(VoltageDisplay())

    def on_message(self, message: str):
        self.last_message = datetime.now()

        if message == "status":
            if config.IS_DEBUG:
                self.mqtt_client.publish_message("status", None)
            else:
                self.mqtt_client.publish_message(
                    "status", message=json.dumps(get_status(self.controller))
                )
        else:
            self.controller.handle_message(message)

    def start(self):
        self.mqtt_client.publish_message(
            "started",
            message=json.dumps(
                {
                    "started": self.started.strftime("%Y-%m-%d %H:%M:%S"),
                    "lastConnected": self.last_connected.strftime("%Y-%m-%d %H:%M:%S"),
                }
            ),
        )
        self.last_connected = datetime.now()
        print("Starting video stream.")
        self.video.start()

    def run(self):
        print("Robotpi is now running!")
        self.mqtt_client.connect()
        self.is_running = True

        try:
            while self.is_running:
                self.video.update()

                if self.is_running and datetime.now() - self.last_message > timedelta(
                    seconds=config.IDLE_TIMEOUT_S
                ):
                    self.is_running = False
                    print("Timeout, shutting down.")
                    self.video.stop()

        except KeyboardInterrupt:
            print("Exiting...")

        self.video.stop()
        self.mqtt_client.disconnect()
        self.controller.exit()

        os.system("sudo shutdown now")


print(f"Robotpi starting up with debug set to {config.IS_DEBUG}")
RobotPi().run()
