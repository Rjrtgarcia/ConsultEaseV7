# ESP32 Faculty Desk Unit - Button Debug Guide

## 🚨 ISSUE IDENTIFIED
- ✅ ESP32 receives consultation messages from central system
- ❌ ESP32 buttons don't send responses back to central system

## 🔧 ESP32 BUTTON DEBUGGING STEPS

### Step 1: Check ESP32 Serial Output for Button Detection

**Connect to ESP32 serial monitor and press buttons while watching for:**

```
✅ Expected output when pressing buttons:
Button A (Pin 15) pressed - ACKNOWLEDGE
Button B (Pin 4) pressed - BUSY
Button state changed: A=LOW, B=HIGH
Debounce delay completed for button A
Processing ACKNOWLEDGE button press
```

```
❌ If you see NOTHING when pressing buttons:
→ Hardware/wiring issue
→ Button code not running
→ Pins not configured correctly
```

### Step 2: Hardware Verification

**Physical button connections:**
- Button A (ACKNOWLEDGE): Pin 15 → GND (with pull-up resistor)
- Button B (BUSY): Pin 4 → GND (with pull-up resistor)
- Verify buttons are actually making contact when pressed
- Check for loose wires or bad solder joints

### Step 3: Check ESP32 Button Code

**Verify in your ESP32 code:**

```cpp
// Button pins should be configured as INPUT_PULLUP
pinMode(BUTTON_A_PIN, INPUT_PULLUP);  // Pin 15
pinMode(BUTTON_B_PIN, INPUT_PULLUP);  // Pin 4

// In main loop, check button states
bool buttonA = !digitalRead(BUTTON_A_PIN);  // Active LOW
bool buttonB = !digitalRead(BUTTON_B_PIN);  // Active LOW

if (buttonA && !lastButtonAState) {
    Serial.println("Button A pressed - ACKNOWLEDGE");
    handleAcknowledgeButton();
}
```

### Step 4: Test MQTT Publishing Function

**Add debug prints to your ESP32 MQTT publishing:**

```cpp
void sendButtonResponse(String responseType) {
    Serial.println("=== MQTT PUBLISH DEBUG ===");
    Serial.println("Response Type: " + responseType);
    Serial.println("Message ID: " + currentMessageId);
    Serial.println("Topic: " + String(RESPONSE_TOPIC));
    
    // Create JSON response
    DynamicJsonDocument doc(1024);
    doc["faculty_id"] = FACULTY_ID;
    doc["faculty_name"] = "Dave Jomillo";
    doc["response_type"] = responseType;
    doc["message_id"] = currentMessageId;  // Should be "2" for current consultation
    doc["timestamp"] = String(millis());
    doc["faculty_present"] = true;
    doc["response_method"] = "physical_button";
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    Serial.println("JSON Payload: " + jsonString);
    
    // Publish to MQTT
    bool result = mqtt.publish(RESPONSE_TOPIC, jsonString.c_str(), false);
    
    Serial.println("MQTT Publish Result: " + String(result ? "SUCCESS" : "FAILED"));
    
    if (!result) {
        Serial.println("MQTT Error: Check connection and topic");
    }
}
```

### Step 5: Verify MQTT Configuration

**Check these in your ESP32 code:**

```cpp
// Correct MQTT broker and topic
const char* mqtt_server = "172.20.10.8";
const int mqtt_port = 1883;
const char* RESPONSE_TOPIC = "consultease/faculty/1/responses";

// Verify MQTT client is connected before publishing
if (!mqtt.connected()) {
    Serial.println("ERROR: MQTT not connected, cannot send button response");
    return;
}
```

### Step 6: Test Button Response for Consultation ID 2

**When you press buttons, ESP32 should send:**

```json
{
  "faculty_id": 1,
  "faculty_name": "Dave Jomillo",
  "response_type": "ACKNOWLEDGE",
  "message_id": "2",
  "original_message": "CID:2 From:Jerome Ibon...",
  "timestamp": "1748850000000",
  "faculty_present": true,
  "response_method": "physical_button"
}
```

**Topic:** `consultease/faculty/1/responses`

## 🔍 SYSTEMATIC TESTING

### Test 1: Manual Button Test
```cpp
// Add this to your ESP32 setup() function for testing
void testButtons() {
    Serial.println("=== BUTTON TEST MODE ===");
    while(true) {
        bool btnA = !digitalRead(BUTTON_A_PIN);
        bool btnB = !digitalRead(BUTTON_B_PIN);
        
        Serial.print("Button A: ");
        Serial.print(btnA ? "PRESSED" : "released");
        Serial.print(" | Button B: ");
        Serial.println(btnB ? "PRESSED" : "released");
        
        delay(100);
    }
}
```

### Test 2: Force MQTT Publish
```cpp
// Add this function to test MQTT publishing manually
void testMQTTPublish() {
    Serial.println("Testing MQTT publish...");
    sendButtonResponse("TEST_ACKNOWLEDGE");
}
```

### Test 3: Check Current Message ID
```cpp
// Verify ESP32 has the correct message ID stored
void printCurrentMessage() {
    Serial.println("Current Message ID: " + currentMessageId);
    Serial.println("Should be: 2");
}
```

## 🚨 COMMON ISSUES & FIXES

### Issue 1: Buttons Detected But No MQTT Publish
**Fix:** Check if MQTT client is still connected
```cpp
if (!mqtt.connected()) {
    Serial.println("MQTT disconnected, reconnecting...");
    reconnectMQTT();
}
```

### Issue 2: Wrong Message ID
**Fix:** Verify message parsing extracts correct ID
```cpp
// When receiving consultation message
if (message.startsWith("CID:")) {
    int colonPos = message.indexOf(":");
    int spacePos = message.indexOf(" ", colonPos);
    currentMessageId = message.substring(colonPos + 1, spacePos);
    Serial.println("Extracted Message ID: " + currentMessageId);
}
```

### Issue 3: Button Debouncing Issues
**Fix:** Add proper debouncing
```cpp
unsigned long lastButtonPressTime = 0;
const unsigned long DEBOUNCE_DELAY = 200; // 200ms

if (buttonPressed && (millis() - lastButtonPressTime > DEBOUNCE_DELAY)) {
    lastButtonPressTime = millis();
    // Process button press
}
```

## ⚡ QUICK FIX TO TRY

**Add this debug code to your ESP32 main loop:**

```cpp
void loop() {
    mqtt.loop();
    
    // Existing consultation handling code...
    
    // DEBUG: Test buttons every loop
    static unsigned long lastTest = 0;
    if (millis() - lastTest > 1000) {  // Every second
        bool btnA = !digitalRead(BUTTON_A_PIN);
        bool btnB = !digitalRead(BUTTON_B_PIN);
        
        if (btnA || btnB) {
            Serial.print("BUTTON DETECTED - A:");
            Serial.print(btnA);
            Serial.print(" B:");
            Serial.println(btnB);
            
            if (btnA) {
                Serial.println("Sending ACKNOWLEDGE...");
                sendButtonResponse("ACKNOWLEDGE");
            }
            if (btnB) {
                Serial.println("Sending BUSY...");
                sendButtonResponse("BUSY");
            }
        }
        lastTest = millis();
    }
}
```

Run this and press buttons while watching serial output!

## 🎯 EXPECTED RESULT

When working correctly, pressing Button A should show:
```
Button A pressed - ACKNOWLEDGE
Sending ACKNOWLEDGE response for message_id: 2
MQTT Publish Result: SUCCESS
```

And you should see in central system logs:
```
🔥 FACULTY RESPONSE HANDLER TRIGGERED
✅ Successfully updated consultation 2 to status ACCEPTED
``` 