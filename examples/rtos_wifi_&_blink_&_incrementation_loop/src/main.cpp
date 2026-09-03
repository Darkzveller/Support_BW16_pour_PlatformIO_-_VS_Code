#include <Arduino.h>
#include <WiFi.h>

extern "C"
{
#include "FreeRTOS.h"
#include "task.h"

// Fonction de ping déjà présente dans le SDK AmebaD
void do_ping_call(char *ip, int loop, int count);
}

constexpr uint32_t LED_PIN = LED_B;

// À remplacer par ton Wi-Fi
char WIFI_SSID[] = "Nom_WIFI";
char WIFI_PASSWORD[] = "Ton_Mot_De_Passe";

// Compteur utilisé par la tâche increment
volatile uint32_t compteur = 0;


// =============================================
// Tâche 1 : Ping Wi-Fi
// =============================================
void wifi_ping(void *parameter)
{
    while (true)
    {
        if (WiFi.status() == WL_CONNECTED)
        {
            Serial.println("[wifi_ping] Ping google.com...");

            char host[] = "google.com";

            // 1 seul ping
            do_ping_call(host, 0, 1);
        }
        else
        {
            Serial.println("[wifi_ping] Wi-Fi non connecte");
        }

        // Attend 5 secondes
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}


// =============================================
// Tâche 2 : Incrémentation
// =============================================
void incrementation_loop(void *parameter)
{
    while (true)
    {
        compteur++;

        Serial.print("[incrementation_loop] compteur = ");
        Serial.println(compteur);

        // Attend 1 seconde
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}


// =============================================
// SETUP
// =============================================
void setup()
{
    pinMode(LED_PIN, OUTPUT);

    Serial.begin(115200);
    delay(2000);

    Serial.println();
    Serial.println("BW16 + PlatformIO ready");

    // -----------------------------------------
    // Initialisation Wi-Fi
    // -----------------------------------------

    Serial.println("Initializing WiFi...");

    WiFi.status();

    Serial.print("Connecting to ");
    Serial.println(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    while (WiFi.status() != WL_CONNECTED)
    {
        Serial.print(".");
        delay(500);
    }

    Serial.println();
    Serial.println("Wi-Fi connected!");

    Serial.print("IP: ");
    Serial.println(WiFi.localIP());


    // =========================================
    // Création des tâches FreeRTOS
    // =========================================

    xTaskCreate(
        wifi_ping,                  // Fonction
        "wifi_ping",                // Nom
        2048,                       // Taille stack
        NULL,                       // Paramètre
        tskIDLE_PRIORITY + 2,       // Priorité
        NULL                        // Handle
    );


    xTaskCreate(
        incrementation_loop,        // Fonction
        "incrementation_loop",      // Nom
        1024,                       // Taille stack
        NULL,                       // Paramètre
        tskIDLE_PRIORITY + 1,       // Priorité
        NULL                        // Handle
    );

    Serial.println("RTOS tasks started.");
}


// =============================================
// Boucle Arduino : LED
// =============================================
void loop()
{
    digitalWrite(LED_PIN, HIGH);
    vTaskDelay(pdMS_TO_TICKS(500));

    digitalWrite(LED_PIN, LOW);
    vTaskDelay(pdMS_TO_TICKS(500));
}