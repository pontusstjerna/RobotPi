#define RELAY_PIN 2
#include "arduino_secrets.h"
#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>
#include <string>

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
const char topic[] = "robotpi";

int last_message_millis = millis();

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);


  // attempt to connect to Wi-Fi network:
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);

    // Blink while we try to connect...
    for (int i = 0; i < 10; i++) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(500);
      digitalWrite(LED_BUILTIN, LOW);
      delay(500);
    }
  }

  mqttClient.setUsernamePassword(mqtt_user, mqtt_password);

  if (!mqttClient.connect(mqtt_broker)) {
    while (1) {
      for (int i = 0; i < 3; i++) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(100);
        digitalWrite(LED_BUILTIN, LOW);
        delay(100);
      }
      delay(3000);
    }
  }

  mqttClient.onMessage(onMqttMessage);
  mqttClient.subscribe(topic);

  digitalWrite(LED_BUILTIN, HIGH);
  delay(10000);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  mqttClient.poll();
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(10000);

  // More than 6 minutes
  if ((millis() - last_message_millis) > (6 * 60 * 1000)) {
    digitalWrite(RELAY_PIN, LOW);
  }
}

void onMqttMessage(int messageSize) {
  while (mqttClient.available()) {
    String message = mqttClient.readString();
    if (message == "shutdown_pi") {
      // wait for 30 seconds, then kill power to Pi
      delay(30000);
      digitalWrite(RELAY_PIN, LOW);
    } else {
      digitalWrite(RELAY_PIN, HIGH);
      last_message_millis = millis();
    }
  }
}
