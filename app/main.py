from dotenv import load_dotenv
import json
from mqtt_client import MqttClient
from controller import Controller
import os
import sys
from datetime import datetime, timedelta
import time

load_dotenv()

is_debug = os.environ.get("DEBUG") or sys.argv[1] == "nopi"
idle_timeout_s = 60 * 5

class RobotPi:
    def __init__(self):
        self.started = datetime.now()
        self.last_connected = self.started
        self.is_running = False
        self.mqtt_client = MqttClient(on_message = self.on_message)
        self.controller = Controller()

    def on_message(self, message):
        if not self.is_running:
            print("Starting video stream.")
            self.is_running = True

        if message == "started":
            self.mqtt_client.publish_message("started", message=json.dumps({
                "started": self.started.strftime("%Y-%m-%d %H:%M:%S"),
                "lastConnected": self.last_connected.strftime("%Y-%m-%d %H:%M:%S"),
            }))
            self.last_connected = datetime.now()
        elif message == "status":
            if is_debug: self.mqtt_client.publish_message("status", None)

        else: self.controller.handle_message(message)

    def startup(self):
        self.mqtt_client.connect()
        try:
            while True:
                time.sleep(10)
                if self.is_running and datetime.now() - self.last_connected > timedelta(seconds=idle_timeout_s):
                    self.is_running = False
                    print("Timeout, stopping video stream.")

        except KeyboardInterrupt:
            print("Exiting...")
            pass
        
        self.mqtt_client.disconnect()
        self.controler.exit()

        
print(f"Robotpi starting up with debug set to {is_debug}")
RobotPi().startup()

