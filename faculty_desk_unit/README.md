# Faculty Desk Unit

This directory contains the firmware for the ESP32-based faculty desk units used in the ConsultEase system.

## Overview

The faculty desk unit is a small device placed on faculty desks that:
- Displays incoming consultation requests from students
- Allows faculty to accept or reject requests
- Provides real-time status updates to the central system
- Detects faculty presence using BLE beacons

## Hardware Requirements

- ESP32 development board
- 2.4-inch TFT SPI Display (ST7789)
- Two push buttons (for Accept/Reject)
- Power supply (USB or wall adapter)
- Case or enclosure

## Dependencies

The following Arduino libraries are required:
- WiFi.h (built-in)
- BLEDevice.h (ESP32 BLE)
- Adafruit_GFX.h
- Adafruit_ST7789.h
- SPI.h (built-in)
- ArduinoJson.h
- PubSubClient.h (for MQTT)

## Configuration

1. Copy `config_template.h` to `config.h`
2. Edit `config.h` to set:
   - WiFi credentials
   - MQTT broker address
   - Faculty ID and name
   - BLE beacon MAC address
   - Display pins

## Installation

1. Install the Arduino IDE
2. Install required libraries through the Library Manager
3. Open `faculty_desk_unit.ino` in the Arduino IDE
4. Select your ESP32 board from the Tools menu
5. Upload the sketch to your ESP32

## Features

- **Robust Connectivity**: Automatic reconnection to WiFi and MQTT
- **BLE Faculty Detection**: Detects faculty presence via BLE beacon
- **Grace Period**: 1-minute grace period when faculty temporarily leaves
- **Offline Queue**: Stores messages when offline and sends when connection is restored
- **Diagnostic Information**: Displays connection status and error messages
- **Low Power Mode**: Dims display when faculty is away

## Testing

Use the test utility from the central system:

```bash
# Test MQTT communication
python scripts/test_utility.py mqtt-test --broker 192.168.1.100

# Send a test message
python scripts/test_utility.py faculty-desk --faculty-id 3 --message "Test message"
```

## Troubleshooting

If you encounter issues:

1. Check the serial monitor for diagnostic messages
2. Verify WiFi and MQTT broker settings
3. Ensure the BLE beacon MAC address is correct
4. See `docs/mqtt_troubleshooting.md` for MQTT-specific issues 