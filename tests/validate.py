import json
from pathlib import Path


root = Path(__file__).resolve().parents[1]

with (root / "platform" / "platform.json").open(encoding="utf-8") as handle:
    platform = json.load(handle)

with (root / "platform" / "boards" / "bw16.json").open(encoding="utf-8") as handle:
    board = json.load(handle)

assert platform["name"] == "realtek-amebad"
assert platform["frameworks"]["arduino"]["package"] == "framework-arduinorealtek-amebad"
assert board["build"]["mcu"] == "RTL8720DN"
assert board["build"]["variant"] == "rtl8720dn_bw16"
assert board["upload"]["protocol"] == "usb_serial"
assert board["upload"]["maximum_size"] == 2097152

print("Manifests are valid.")
