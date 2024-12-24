#define RELAY_PIN 2
#define SHUTOFF_PIN 3
#define CHARGE_PIN 0
#define BATTERY_PIN 1

#include "arduino_secrets.h"
#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>
#include <string>
#include <ArduinoLowPower.h>

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
const char topic[] = "robotpi";
const char status_topic[] = "robotpi/status";


int last_message_millis = millis();
bool relay_on = false;

void (*resetFunc)(void) = 0;  // create a standard reset function

void connectToWifi() {
  // attempt to connect to Wi-Fi network:
  int status = WiFi.status();
  if (status != WL_CONNECTED) {
    WiFi.begin(ssid, pass);
  }
  while (status != WL_CONNECTED) {
    status = WiFi.status();
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
  }
}

void connectToMqtt() {



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


  mqttClient.subscribe(topic);
}

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(SHUTOFF_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(SHUTOFF_PIN, LOW);

  connectToWifi();
  mqttClient.setUsernamePassword(mqtt_user, mqtt_password);
  connectToMqtt();
  mqttClient.onMessage(onMqttMessage);

  digitalWrite(LED_BUILTIN, HIGH);
  delay(10000);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  connectToWifi();

  if (mqttClient.connected()) {
    mqttClient.poll();
  } else {
    connectToMqtt();
  }

  send_status();


  if (!relay_on) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
  } else {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(250);
    digitalWrite(LED_BUILTIN, LOW);
    delay(250);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(250);
    digitalWrite(LED_BUILTIN, LOW);
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
    send_status();
    delay(500);
  } else {
    LowPower.deepSleep(10000);
  }
}

void send_status() {
  float charge_voltage = analogRead(CHARGE_PIN) * (5.0 / 1023.0); 
  float battery_voltage = analogRead(BATTERY_PIN) * (5.0 / 1023.0);

  
  String is_relay_on = relay_on ? "true" : "false";

  String status = "{\"battery_voltage\": \"";
  status.concat(battery_voltage);
  status.concat("\", \"charge_voltage\": \"");
  status.concat(charge_voltage);
  status.concat("\", \"relay_on\": \"");
  status.concat(is_relay_on);
  status.concat("\"}");

  mqttClient.beginMessage(status_topic);
  mqttClient.println(status);
  mqttClient.endMessage();
}

void onMqttMessage(int messageSize) {
  while (mqttClient.available()) {
    String message = mqttClient.readString();
    if (message == "shutdown_pi") {
      // wait for 15 seconds, then kill power to Pi
      delay(15000);
      digitalWrite(RELAY_PIN, LOW);
      relay_on = false;
      digitalWrite(SHUTOFF_PIN, LOW);
    } else {
      digitalWrite(RELAY_PIN, HIGH);
      relay_on = true;
      last_message_millis = millis();
    }
  }
}
