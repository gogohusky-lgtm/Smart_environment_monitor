#include "DHT.h"

#define DHTPIN 7
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  delay(2000);

  int lm35_raw = analogRead(A0);
  int cds_raw = analogRead(A1);

  float voltage = lm35_raw * (5.0 / 1023.0);
  float lm35_temp = voltage * 100.0;

  float dht_humd = dht.readHumidity();
  float dht_temp = dht.readTemperature();

  if (isnan(dht_humd) || isnan(dht_temp)) {
    Serial.println("{\"error\":\"DHT11 read failed\"}");
    return;
  }

  String json = "{";
  json += "\"LM35_Temp\":" + String(lm35_temp, 2) + ",";
  json += "\"CDS_Light\":" + String(cds_raw) + ",";
  json += "\"DHT_Humd\":" + String(dht_humd, 2) + ",";
  json += "\"DHT_Temp\":" + String(dht_temp, 2);
  json += "}";

  Serial.println(json);
}
