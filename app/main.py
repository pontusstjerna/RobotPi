from dotenv import load_dotenv

load_dotenv()

import json
import subprocess
from mqtt_client import MqttClient
from controller import Controller, run_motors
from datetime import datetime, timedelta
from automation import Timer, redock
from functools import partial
from video import VideoProcessor
from charge_controller import ChargeController
from status import get_status
from time import time, sleep
from computer_vision.qr_follower import QrFollower
from computer_vision.voltage_display import VoltageDisplay
from computer_vision.calibration import Calibration
from automation import redock
import config

if not config.IS_DEBUG:
    from INA260_bridge import get_voltage


class RobotPi:
    last_message = datetime.now()
    attempted_redocks = 0

    def __init__(self):
        self.started = datetime.now()
        self.last_connected = self.started
        self.is_running = False
        self.mqtt_client = MqttClient(on_message=self.on_message)
        self.controller = Controller()
        self.video = VideoProcessor()
        self.qr_follower = QrFollower()
        self.charge_controller = ChargeController()
        self.calibration = Calibration()
        self.redock_timer = Timer(
            timedelta(minutes=30), partial(redock, self.controller)
        )

        self.video.add_cv_module(self.qr_follower)
        self.video.add_cv_module(VoltageDisplay(self.charge_controller))
        self.video.add_cv_module(self.calibration)

    def on_message(self, message):
        self.last_message = datetime.now()
        if not self.is_running:
            self.set_usb(on=True)
            self.video.start()
            self.is_running = True

            if config.FOLLOW_QR_DIRECTLY:
                self.qr_follower.activate()

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
        elif message == "calibrate":
            self.calibration.activate()
        elif message == "forward_500":
            calibration = self.calibration.get_calibration()
            seconds = calibration.get("seconds_per_millimeter")
            power = calibration.get("power")
            run_motors(power, power, seconds * 500)
        elif message == "turn_right_90":
            calibration = self.calibration.get_calibration()
            seconds = calibration.get("seconds_per_degree_right") * 90
            power = calibration.get("power")
            run_motors(power, -power, seconds)
        else:
            self.controller.handle_message(message)

    def run(self):
        print("Robotpi is now running!")
        self.mqtt_client.connect()
        self.set_usb(on=False)
        try:
            while True:
                if self.attempted_redocks >= config.MAX_REDOCK_ATTEMPTS:
                    print(
                        f"Attempted {self.attempted_redocks} - will unfortunately shut down (send notification in the future)"
                    )
                    subprocess.run(["sudo", "shutdown", "now"])
                    return

                self.video.update()
                self.charge_controller.update()

                if self.is_running and datetime.now() - self.last_message > timedelta(
                    seconds=config.IDLE_TIMEOUT_S
                ):
                    self.is_running = False
                    print("Timeout, stopping video stream.")
                    self.video.stop()
                    self.set_usb(on=False)

                self.redock_timer.update()

        except KeyboardInterrupt:
            print("Exiting...")

        self.video.stop()
        self.mqtt_client.disconnect()
        self.controller.exit()

    def set_usb(self, on):
        if not on:
            sleep(5)

        subprocess.run(
            ["sudo", "uhubctl", "-l", "1-1", "-p", "2", "-a", "1" if on else "0"]
        )

        if on:
            sleep(5)


print(f"Robotpi starting up with debug set to {config.IS_DEBUG}")
RobotPi().run()
