#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WiFiManager.h>

String deviceID;

const char* serverUrl = "http://10.98.80.35:8000/send_from_esp32";

Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(115200);

  deviceID = "ESP-" + WiFi.macAddress();
  Serial.println("My ID is: " + deviceID);
  
  WiFiManager wm;
  bool res = wm.autoConnect("ESP32-Setup-Portal"); 

  if(!res) {
      Serial.println("Failed to connect");
      ESP.restart(); 
  }

  while (!Serial) {
    delay(10);
  }
  
  Serial.println("Initializing MPU6050 start...");
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 ! Check your wiring.");
    while (1) {
      delay(10); 
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  delay(100);
}

void loop() {
  const int numSamples = 10;
  float magnitudes[numSamples];
  float sumMag = 0;
  float sumTemp = 0;

  // --- 1. DATA COLLECTION ---
  // Loop 10 times with a 100ms delay = exactly 1 second of data
  for(int i = 0; i < numSamples; i++){
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    // Calculate total vibration energy (Magnitude)
    float mag = sqrt(pow(a.acceleration.x, 2) + pow(a.acceleration.y, 2) + pow(a.acceleration.z, 2));
    
    magnitudes[i] = mag;          // Store for variance calculation later
    sumMag += mag;                // Add to total sum for mean calculation
    sumTemp += temp.temperature;  // Add to total sum for temp calculation
    
    delay(100); 
  }

  // --- 2. MATH COMPUTATION ---
  float meanMag = sumMag / numSamples;
  float avgTemp = sumTemp / numSamples;

  float varSum = 0;
  for(int i = 0; i < numSamples; i++) {
    varSum += pow(magnitudes[i] - meanMag, 2);
  }
  float varMag = varSum / numSamples;

  // --- 3. JSON CREATION ---
  JsonDocument doc;
  
  // Creates exactly: {"mean": 23.0, "var": 32.0, "temp": 23.0}
  doc["mean"] = meanMag;
  doc["var"] = varMag;
  doc["temp"] = avgTemp;
  
  // (Optional but recommended) Include the device ID so your backend knows who is sending i

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  // --- 4. NETWORK TRANSMISSION ---
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json"); // Tell FastAPI we are sending JSON

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      Serial.print("Success! Data sent to server. Response Code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error sending POST request. Code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end(); // Free up resources
  } else {
    Serial.println("Error: Wi-Fi disconnected!");
  }
}