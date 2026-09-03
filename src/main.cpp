// #include <Arduino.h>
// #include <WiFi.h>

// constexpr uint32_t LED_PIN = LED_B;

// void setup()
// {
//     pinMode(LED_PIN, OUTPUT);
//     Serial.begin(115200);
//     Serial.println("BW16 + PlatformIO ready");

//     Serial.println("Scanning 2.4 GHz and 5 GHz Wi-Fi networks...");

//     const int count = WiFi.scanNetworks();
//     if (count <= 0)
//     {
//         Serial.println("No network found.");
//         return;
//     }

//     for (int index = 0; index < count; ++index)
//     {
//         Serial.print(index + 1);
//         Serial.print(". ");
//         Serial.print(WiFi.SSID(index));
//         Serial.print(" | RSSI: ");
//         Serial.println(WiFi.RSSI(index));
//     }
// }

// void loop()
// {
//     digitalWrite(LED_PIN, HIGH);
//     delay(500);
//     digitalWrite(LED_PIN, LOW);
//     delay(500);
// }
// #include <Arduino.h>
// #include <WiFi.h>

// void setup() {
//     Serial.begin(115200);
//     delay(3000);

//     Serial.println();
//     Serial.println("BW16 + PlatformIO ready");

//     Serial.println("Initializing WiFi...");

//     // IMPORTANT :
//     // WiFi.status() initialise le driver WiFi du RTL8720DN
//     int status = WiFi.status();

//     Serial.print("WiFi status: ");
//     Serial.println(status);

//     delay(2000);

//     // Affiche la MAC pour vérifier que le driver répond
//     byte mac[6];
//     WiFi.macAddress(mac);

//     Serial.print("MAC: ");
//     for (int i = 0; i < 6; i++) {
//         if (i) Serial.print(":");
//         if (mac[i] < 16) Serial.print("0");
//         Serial.print(mac[i], HEX);
//     }
//     Serial.println();

//     Serial.println();
//     Serial.println("Scanning 2.4 GHz and 5 GHz Wi-Fi networks...");

//     int n = WiFi.scanNetworks();

//     Serial.print("scanNetworks() returned: ");
//     Serial.println(n);

//     if (n < 0) {
//         Serial.println("WiFi scan failed.");
//         return;
//     }

//     if (n == 0) {
//         Serial.println("No network found.");
//         return;
//     }

//     Serial.print(n);
//     Serial.println(" networks found:");

//     for (int i = 0; i < n; i++) {
//         Serial.print(i + 1);
//         Serial.print(". ");

//         Serial.print(WiFi.SSID(i));

//         Serial.print(" | RSSI: ");
//         Serial.print(WiFi.RSSI(i));
//         Serial.println(" dBm");
//     }
// }

// void loop() {
// }

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