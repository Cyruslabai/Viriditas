#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define DHTPIN 13
#define DHTTYPE DHT11
#define SOIL_PIN 33

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_COMPUTER_IP:5000/sensor-data";

DHT dht(DHTPIN, DHTTYPE);

int toMoisturePercent(int rawValue) {
  int percent = map(rawValue, 4095, 1400, 0, 100);
  if (percent < 0) percent = 0;
  if (percent > 100) percent = 100;
  return percent;
}

void connectWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  analogReadResolution(12);
  connectWifi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWifi();
  }

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  int rawSoil = analogRead(SOIL_PIN);
  int soilMoisture = toMoisturePercent(rawSoil);

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("DHT11 read failed");
    delay(5000);
    return;
  }

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  String body = "{";
  body += "\"soil_moisture\":" + String(soilMoisture) + ",";
  body += "\"temperature\":" + String(temperature, 1) + ",";
  body += "\"humidity\":" + String(humidity, 1);
  body += "}";

  int responseCode = http.POST(body);
  Serial.println(responseCode);
  Serial.println(body);
  http.end();

  delay(10000);
}
