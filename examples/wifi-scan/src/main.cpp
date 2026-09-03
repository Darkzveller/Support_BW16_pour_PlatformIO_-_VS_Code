#include <Arduino.h>
#include <WiFi.h>

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.println();
    Serial.println("BW16 + PlatformIO ready");

    // Initialise le driver Wi-Fi
    Serial.println("Initializing WiFi...");
    int status = WiFi.status();

    Serial.print("WiFi status: ");
    Serial.println(status);

    delay(2000);

    // Vérification rapide avec l'adresse MAC
    byte mac[6];
    WiFi.macAddress(mac);

    Serial.print("MAC: ");
    for (int i = 0; i < 6; ++i) {
        if (i > 0) {
            Serial.print(":");
        }

        if (mac[i] < 0x10) {
            Serial.print("0");
        }

        Serial.print(mac[i], HEX);
    }
    Serial.println();

    Serial.println();
    Serial.println("Scanning 2.4 GHz and 5 GHz Wi-Fi networks...");

    const int count = WiFi.scanNetworks();

    Serial.print("scanNetworks() returned: ");
    Serial.println(count);

    if (count < 0) {
        Serial.println("Wi-Fi scan failed.");
        return;
    }

    if (count == 0) {
        Serial.println("No network found.");
        return;
    }

    Serial.print(count);
    Serial.println(" network(s) found:");

    for (int index = 0; index < count; ++index) {
        Serial.print(index + 1);
        Serial.print(". ");

        Serial.print(WiFi.SSID(index));

        Serial.print(" | RSSI: ");
        Serial.print(WiFi.RSSI(index));
        Serial.println(" dBm");
    }
}

void loop() {
    delay(1000);
}