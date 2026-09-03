#include <Arduino.h>

// On the standard BW16 board, LED_B is the onboard blue LED.
constexpr uint32_t LED_PIN = LED_B;

void setup() {
    pinMode(LED_PIN, OUTPUT);
    Serial.begin(115200);
    Serial.println("BW16 + PlatformIO ready");
}

void loop() {
    digitalWrite(LED_PIN, HIGH);
    delay(500);
    digitalWrite(LED_PIN, LOW);
    delay(500);
}
