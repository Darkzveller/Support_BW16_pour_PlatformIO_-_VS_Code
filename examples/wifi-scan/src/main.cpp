#include <Arduino.h>
#include <WiFi.h>

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("Scanning 2.4 GHz and 5 GHz Wi-Fi networks...");

    const int count = WiFi.scanNetworks();
    if (count <= 0) {
        Serial.println("No network found.");
        return;
    }

    for (int index = 0; index < count; ++index) {
        Serial.print(index + 1);
        Serial.print(". ");
        Serial.print(WiFi.SSID(index));
        Serial.print(" | RSSI: ");
        Serial.println(WiFi.RSSI(index));
    }
}

void loop() {
    delay(1000);
}
