#include <Arduino.h>
#include <WiFi.h>

constexpr uint32_t LED_PIN = LED_B;

void setup()
{
    pinMode(LED_PIN, OUTPUT);
    Serial.begin(115200);
    Serial.println("BW16 + PlatformIO ready");

    Serial.println("Scanning 2.4 GHz and 5 GHz Wi-Fi networks...");

    const int count = WiFi.scanNetworks();
    if (count <= 0)
    {
        Serial.println("No network found.");
        return;
    }

    for (int index = 0; index < count; ++index)
    {
        Serial.print(index + 1);
        Serial.print(". ");
        Serial.print(WiFi.SSID(index));
        Serial.print(" | RSSI: ");
        Serial.println(WiFi.RSSI(index));
    }
}

void loop()
{
    digitalWrite(LED_PIN, HIGH);
    delay(500);
    digitalWrite(LED_PIN, LOW);
    delay(500);
}
