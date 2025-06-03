// ================================
// FACULTY DESK UNIT CONFIGURATION
// ================================
// Copy this file to config.h and edit the values below

#ifndef CONFIG_H
#define CONFIG_H

// ================================
// DEBUG SETTINGS
// ================================
#define ENABLE_SERIAL_DEBUG true
#define SERIAL_BAUD_RATE 115200

// Debug macros - automatically disabled when ENABLE_SERIAL_DEBUG is false
#if ENABLE_SERIAL_DEBUG
    #define DEBUG_PRINT(x) Serial.print(x)
    #define DEBUG_PRINTLN(x) Serial.println(x)
    #define DEBUG_PRINTF(format, ...) Serial.printf(format, __VA_ARGS__)
#else
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINTLN(x)
    #define DEBUG_PRINTF(format, ...)
#endif

// ================================
// FACULTY INFORMATION
// ================================
#define FACULTY_ID 1
#define FACULTY_NAME "Dr. John Smith"
#define FACULTY_DEPARTMENT "Computer Science"

// ================================
// WIFI CONFIGURATION
// ================================
#define WIFI_SSID "YourWiFiNetwork"
#define WIFI_PASSWORD "YourWiFiPassword"
#define WIFI_CONNECT_TIMEOUT 20000
#define WIFI_RECONNECT_INTERVAL 5000
#define MAX_WIFI_RECONNECT_ATTEMPTS 5

// ================================
// MQTT CONFIGURATION
// ================================
#define MQTT_SERVER "192.168.1.100"  // IP address of your Raspberry Pi
#define MQTT_PORT 1883
#define MQTT_USERNAME "faculty_desk"
#define MQTT_PASSWORD "desk_password"
#define MQTT_CLIENT_ID_PREFIX "FacultyDesk"
#define MQTT_CONNECT_TIMEOUT 10000
#define MQTT_RECONNECT_INTERVAL 5000
#define MQTT_KEEPALIVE 60
#define MQTT_QOS 1
#define MQTT_MAX_PACKET_SIZE 1024  // Increased from default 128 bytes

// MQTT Topics
#define MQTT_TOPIC_PREFIX "consultease/faculty/"
#define MQTT_TOPIC_MESSAGES MQTT_TOPIC_PREFIX FACULTY_ID_STR "/messages"
#define MQTT_TOPIC_RESPONSES MQTT_TOPIC_PREFIX FACULTY_ID_STR "/responses"
#define MQTT_TOPIC_STATUS MQTT_TOPIC_PREFIX FACULTY_ID_STR "/status"
#define MQTT_TOPIC_HEARTBEAT MQTT_TOPIC_PREFIX FACULTY_ID_STR "/heartbeat"
#define MQTT_TOPIC_SYSTEM "consultease/system/"

// ================================
// BLE CONFIGURATION
// ================================
#define ENABLE_BLE_DETECTION true
#define FACULTY_BEACON_MAC "AA:BB:CC:DD:EE:FF"  // Replace with your beacon MAC
#define BLE_SCAN_INTERVAL 8000  // Scan every 8 seconds (reduced from 1s for performance)
#define BLE_SCAN_DURATION 3000  // Scan for 3 seconds
#define BLE_SIGNAL_THRESHOLD -80  // RSSI threshold for detection
#define PRESENCE_TIMEOUT 60000  // Consider faculty away after 60 seconds
#define GRACE_PERIOD 60000  // 1-minute grace period for temporary absence

// ================================
// DISPLAY CONFIGURATION
// ================================
#define TFT_CS    5
#define TFT_RST   22
#define TFT_DC    21
#define TFT_MOSI  23
#define TFT_SCLK  18
#define TFT_BL    4   // Backlight control pin
#define TFT_ROTATION 2  // 0=Portrait, 2=Landscape

// ================================
// BUTTON CONFIGURATION
// ================================
#define BUTTON_A_PIN 12  // Accept button
#define BUTTON_B_PIN 14  // Reject button
#define DEBOUNCE_DELAY 50  // Debounce time in milliseconds

// ================================
// SYSTEM CONFIGURATION
// ================================
#define HEARTBEAT_INTERVAL 30000  // Send heartbeat every 30 seconds
#define MESSAGE_DISPLAY_TIMEOUT 60000  // Display message for 60 seconds
#define STATUS_UPDATE_INTERVAL 10000  // Update status every 10 seconds
#define MAX_MESSAGE_LENGTH 512  // Maximum message length
#define ENABLE_DIAGNOSTICS true  // Enable diagnostic reporting
#define DIAGNOSTIC_INTERVAL 300000  // Send diagnostics every 5 minutes
#define WATCHDOG_TIMEOUT 30000  // Watchdog timeout in milliseconds

// ================================
// OFFLINE QUEUE CONFIGURATION
// ================================
#define MAX_QUEUE_SIZE 10
#define QUEUE_RETRY_INTERVAL 5000
#define MAX_RETRY_COUNT 5
#define EXPONENTIAL_BACKOFF true

// ================================
// NTP CONFIGURATION
// ================================
#define NTP_SERVER "pool.ntp.org"
#define TIMEZONE 8  // UTC+8 (Philippines)
#define ENABLE_NTP true
#define NTP_SYNC_INTERVAL 3600000  // Sync time every hour

// ================================
// HELPER MACROS
// ================================
// Convert FACULTY_ID to string for MQTT topics
#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)
#define FACULTY_ID_STR TOSTRING(FACULTY_ID)

#endif // CONFIG_H 