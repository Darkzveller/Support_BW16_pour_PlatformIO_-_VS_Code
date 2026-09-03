# BW16 PlatformIO

Support communautaire de la carte **Ai-Thinker BW16** basée sur le **Realtek RTL8720DN** dans PlatformIO et VS Code.

Ce projet permet de sélectionner `bw16`, compiler du code Arduino, générer l'image Realtek `km0_km4_image2.bin`, téléverser le firmware par USB-série et utiliser le moniteur série depuis PlatformIO.

> Version 0.2.0 pour Windows : la compilation de Blink et du scan Wi-Fi a été validée avec PlatformIO 6.1.19 et le cœur Arduino AmebaD 3.1.9. Le téléversement utilise l'outil officiel Realtek, mais doit encore être confirmé sur une carte physique BW16.

## Fonctionnalités

- Carte PlatformIO : `bw16`
- SoC : RTL8720DN, Cortex-M33 à 200 MHz
- Framework : Arduino AmebaD officiel
- Wi-Fi 2,4 GHz et 5 GHz
- Bluetooth Low Energy
- Compilation C/C++ depuis `src/main.cpp`
- Génération automatique du firmware Realtek
- Upload USB-série à 1 500 000 ou 921 600 bauds
- Moniteur série PlatformIO
- Paquet Windows autonome, sans téléchargement de dépendances ni `bzip2`

## Installation sous Windows

### 1. Prérequis

- Visual Studio Code
- Extension PlatformIO IDE
- Le pilote du convertisseur USB-série de la carte, souvent CH340 ou CP210x

### 2. Ouvrir et compiler

1. Décompresse entièrement `BW16-PlatformIO-v0.2.0-Windows.zip`.
2. Dans VS Code, sélectionne **File > Open Folder** et ouvre le dossier `BW16-PlatformIO` extrait.
3. Clique sur **PlatformIO: Build**.

PlatformIO installe automatiquement depuis le dossier `vendor` :

- Arduino AmebaD `3.1.9`
- Realtek ASDK toolchain `1.0.1`
- Realtek upload tools `1.1.3`
- SCons `4.8.1`, utilisé par PlatformIO pour compiler

Il n'est plus nécessaire de lancer un script PowerShell, de changer la stratégie d'exécution ou d'installer `bzip2`. `INSTALLER_BW16.bat` reste disponible uniquement pour réparer une ancienne installation globale incomplète.

## Premier test

1. Branche le BW16 avec un câble Micro USB capable de transmettre des données.
2. Clique sur **PlatformIO: Build**.
3. Mets la carte en mode téléchargement.
4. Clique sur **PlatformIO: Upload**.
5. Ouvre **PlatformIO: Serial Monitor** à 115200 bauds.

Le programme présent dans `src/main.cpp` doit faire clignoter la LED bleue et afficher :

```text
BW16 + PlatformIO ready
```

## Mettre le BW16 en mode téléchargement

Sur le BW16 Micro USB standard, l'entrée en mode UART se fait généralement avec les boutons **BURN** et **RESET** :

1. Maintiens **BURN** appuyé.
2. Appuie puis relâche **RESET**.
3. Relâche **BURN**.
4. Lance rapidement l'upload lorsque PlatformIO affiche qu'il cherche le port.

Si ta carte possède un circuit d'auto-upload DTR/RTS, tu peux essayer :

```ini
board_upload.auto_mode = Enable
```

## Configuration `platformio.ini`

Configuration minimale :

```ini
[env:bw16]
platform = file://platform
board = bw16
framework = arduino
monitor_speed = 115200
platform_packages =
    framework-arduinorealtek-amebad @ file://vendor/framework-arduinorealtek-amebad-3.1.9-bundle.tar.gz
    toolchain-realtek-amebad @ file://vendor/toolchain-realtek-amebad-windows-1.0.1-bundle.tar.gz
    tool-realtek-amebad @ file://vendor/tool-realtek-amebad-windows-1.1.3-bundle.tar.gz
    platformio/tool-scons @ file://vendor/tool-scons-4.40801.0-bundle.tar.gz
```

Si PlatformIO choisit le mauvais port :

```ini
upload_port = COM5
```

Remplace `COM5` par le port visible dans le gestionnaire de périphériques Windows.

Si l'upload est instable à 1 500 000 bauds :

```ini
board_upload.speed = 921600
```

Pour effacer la flash avant le téléversement :

```ini
board_upload.erase_flash = Enable
```

## Créer un nouveau projet

Après l'installation, ouvre PlatformIO Home et crée un projet avec :

- **Board** : `Ai-Thinker BW16 (RTL8720DN)`
- **Framework** : `Arduino`

Le fichier principal doit être `src/main.cpp`. Contrairement à un fichier `.ino`, ajoute explicitement :

```cpp
#include <Arduino.h>
```

Exemple minimal :

```cpp
#include <Arduino.h>

void setup() {
    Serial.begin(115200);
}

void loop() {
    Serial.println("Hello from BW16");
    delay(1000);
}
```

## Exemples inclus

- `examples/blink` : LED intégrée et port série
- `examples/wifi-scan` : scan des réseaux Wi-Fi visibles

## Fichiers générés

Après une compilation réussie :

```text
.pio/build/bw16/firmware.elf
.pio/build/bw16/firmware.bin
```

`firmware.bin` correspond à l'image combinée `km0_km4_image2.bin` attendue par l'outil Realtek.

## Dépannage

### `Enter Uart Download Mode`

La carte n'est pas en mode téléchargement. Recommence la séquence BURN/RESET et vérifie que le port COM est correct.

### `Flashloader download fail`

- essaie `board_upload.speed = 921600` ;
- vérifie le câble USB ;
- ferme tout autre moniteur série ;
- installe ou actualise le pilote CH340/CP210x.

### Le port COM n'apparaît pas

Vérifie le gestionnaire de périphériques, le pilote USB-série et utilise un câble de données plutôt qu'un câble de recharge uniquement.

### Erreur `bzip2 -d`

Cette erreur provenait de l'ancien installateur et du support `.tar.bz2` manquant dans certains Windows. Utilise la version 0.2.0 : la chaîne de compilation est désormais fournie en `.tar.gz` et installée automatiquement pendant le premier Build.

Si une installation incomplète subsiste, ferme VS Code, double-clique sur `INSTALLER_BW16.bat`, puis relance **Build**.

## Sources techniques

- [Cœur Arduino AmebaD officiel](https://github.com/Ameba-AIoT/ameba-arduino-d)
- [Documentation des plateformes personnalisées PlatformIO](https://docs.platformio.org/en/latest/platforms/creating_platform.html)
- [Demande de prise en charge RTL8720DN dans PlatformIO](https://github.com/platformio/platformio-core/issues/4080)

## Licence

Le code d'intégration de ce dépôt est distribué sous licence Apache-2.0. Le cœur Arduino, la chaîne de compilation et les outils de téléversement sont téléchargés depuis le dépôt officiel AmebaD et restent soumis à leurs licences respectives.
