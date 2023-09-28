import os
from paho.mqtt import client as mqtt_client


class MqttClient:
    def __init__(self, on_message):
        self.topic = "robotpi"
        self.on_message = on_message

    def connect(self):
        url = os.environ["MQTT_BROKER_URL"]
        username = os.environ["MQTT_USERNAME"]
        password = os.environ["MQTT_PASSWORD"]
        client_id = "robotpi-mqtt-client"

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Successfully connected to MQTT broker {url}")
            else:
                print(f"Failed to connect, return code {rc}")

        print(f"Connecting MQTT to {url}")

        client = mqtt_client.Client(client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.on_message = self.on_message_received
        client.connect(url)

        client.loop_start()
        client.subscribe(self.topic)
        self.client = client

    def disconnect(self):
        self.client.loop_stop()

    def publish_message(self, subtopic, message):
        result = self.client.publish(f"{self.topic}/{subtopic}", message)
        if result[0] != 0:
            print("Failed to send message!")

    def on_message_received(self, topic, userdata, msg):
        decoded_message = msg.payload.decode()
        print(f"Received {decoded_message} from topic {msg.topic}")

        self.on_message(decoded_message)
