#define RELAY_PIN 2
#define SHUTOFF_PIN 3
#include "arduino_secrets.h"
#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>
#include <string>
#include <ArduinoLowPower.h>

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
const char topic[] = "robotpi";

int last_message_millis = millis();
bool relay_on = false;

void(* resetFunc) (void) = 0; // create a standard reset function

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(SHUTOFF_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(SHUTOFF_PIN, LOW);

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
  if (WiFi.status() != WL_CONNECTED) {
      resetFunc();
  }
  if (!mqttClient.connected()) {
    mqttClient.connect(mqtt_broker);
  }

  mqttClient.poll();

  if (!relay_on) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
  } else {
    digitalWrite(LED_BUILTIN, HIGH);
  }
  

  // More than 6 minutes
  if (relay_on && (millis() - last_message_millis) > (6 * 60 * 1000)) {
    // Send shutoff first, wait for 20 seconds and then cut power
    digitalWrite(SHUTOFF_PIN, HIGH);
    delay(20000);
    digitalWrite(RELAY_PIN, LOW);
    relay_on = false;
    digitalWrite(SHUTOFF_PIN, LOW);
  } else if (relay_on) {
    delay(10000);
  } else {
    LowPower.deepSleep(10000);
  }
}

void onMqttMessage(int messageSize) {
  while (mqttClient.available()) {
    String message = mqttClient.readString();
    if (message == "shutdown_pi") {
      // wait for 15 seconds, then kill power to Pi
      delay(15000);
      digitalWrite(RELAY_PIN, LOW);
      digitalWrite(SHUTOFF_PIN, LOW);
    } else {
      relay_on = true;
      digitalWrite(RELAY_PIN, HIGH);
      last_message_millis = millis();
    }
  }
}
