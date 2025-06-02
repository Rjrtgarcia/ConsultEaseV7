# MQTT Publishing Troubleshooting Guide

## 🔍 **Problem Summary**
ESP32 shows:
- ✅ MQTT connected: TRUE
- ✅ WiFi connected: TRUE  
- ✅ MQTT state: 0 (CONNECTED)
- ❌ **All publish attempts FAIL**

## 🚀 **Immediate Action Plan**

### **Step 1: Run Enhanced Diagnostics**

1. **Add the enhanced debugging code** from `mqtt_debug_enhanced.ino` to your `faculty_desk_unit.ino`

2. **Call diagnostics in setup():**
```cpp
void setup() {
  // ... existing setup code ...
  
  // Add this after MQTT connection is established
  if (client.connected()) {
    runMQTTDiagnostics();
  }
}
```

3. **Replace your current publish calls** with:
```cpp
// Instead of: client.publish(topic, payload)
// Use: publishWithDetailedDebug(topic, payload)
bool success = publishWithDetailedDebug("consultease/faculty/1/responses", responseJson.c_str());
```

### **Step 2: Test MQTT Broker from Central System**

1. **Install MQTT client** (if not already installed):
```bash
pip install paho-mqtt
```

2. **Run the broker test script:**
```bash
cd central_system
python mqtt_broker_test.py
```

This will:
- Test broker connectivity
- Verify topic permissions  
- Send test consultation
- Listen for ESP32 responses

### **Step 3: Check Common Issues**

## 🔧 **Most Likely Causes & Fixes**

### **1. ❌ MQTT Broker Authentication Issues**

**Symptoms:** Connection shows successful but publishes fail

**Check:**
```bash
# Test with MQTT command line client
mosquitto_pub -h 172.20.10.8 -p 1883 -u faculty_desk -P desk_password -t "test/topic" -m "test message"
```

**Fix:** Verify credentials in `config.h`:
```cpp
#define MQTT_USERNAME "faculty_desk"
#define MQTT_PASSWORD "desk_password"
```

### **2. ❌ Topic Permission Issues**

**Symptoms:** Some topics work, others don't

**Fix:** Check MQTT broker ACL (Access Control List) configuration
- ESP32 needs **PUBLISH** permission to `consultease/faculty/+/responses`
- Central system needs **SUBSCRIBE** permission to same topic

### **3. ❌ MQTT Broker Overload**

**Symptoms:** Intermittent failures, timeouts

**Check:** MQTT broker resource usage
**Fix:** Increase broker connection limits or use QoS 0

### **4. ❌ Network Packet Loss**

**Symptoms:** WiFi connected but publish fails

**Fix:** Add WiFi signal strength check:
```cpp
int rssi = WiFi.RSSI();
if (rssi < -80) {
  DEBUG_PRINTLN("⚠️ Weak WiFi signal may cause MQTT issues");
}
```

### **5. ❌ MQTT Message Queue Full**

**Symptoms:** First few messages work, then fail

**Fix:** Increase buffer size or clear queue:
```cpp
client.setBufferSize(1024);  // Increase from default 256
```

## 🔬 **Advanced Debugging**

### **Check MQTT Broker Logs**

If you have access to MQTT broker:
```bash
# Mosquitto logs
tail -f /var/log/mosquitto/mosquitto.log

# Look for:
# - Connection attempts
# - Authentication failures  
# - Publish attempts
# - Permission denials
```

### **Network Analysis**

Use Wireshark to capture MQTT traffic:
1. Capture on port 1883
2. Filter: `mqtt`
3. Look for PUBLISH packets and responses

### **ESP32 Memory Issues**

Check if low memory is causing failures:
```cpp
DEBUG_PRINTF("Free heap before publish: %d bytes\n", ESP.getFreeHeap());
// Should be > 50KB for stable operation
```

## 📋 **Debugging Checklist**

### **ESP32 Side:**
- [ ] Enhanced debugging code added
- [ ] MQTT buffer size increased to 1024 bytes
- [ ] Free heap > 50KB during publish
- [ ] WiFi signal strength > -80 dBm
- [ ] MQTT credentials correct in config.h

### **Central System Side:**
- [ ] MQTT broker test script runs successfully
- [ ] Central system can subscribe to faculty response topics
- [ ] Faculty response controller logs show incoming messages
- [ ] Database updates happen after responses

### **Network Side:**
- [ ] MQTT broker accessible from both ESP32 and central system
- [ ] No firewall blocking port 1883
- [ ] Network latency < 100ms
- [ ] No packet loss between devices

## 🎯 **Expected Results After Fixes**

You should see:
```
🔍 MQTT Debug Info:
   Topic: consultease/faculty/1/responses
   Payload size: 239 bytes
   Client state: 0
   Buffer size: 1024 bytes
   WiFi RSSI: -45 dBm
   Free heap: 165432 bytes
🚀 Attempting MQTT publish...
✅ MQTT publish reported SUCCESS
```

And in central system logs:
```
🔥 FACULTY RESPONSE HANDLER TRIGGERED - Topic: consultease/faculty/1/responses
✅ Successfully updated consultation status: 11 (PENDING -> BUSY)
```

## 🚨 **If All Else Fails**

### **Alternative 1: Use Different Topic**
Try publishing to a simpler topic:
```cpp
// Test with basic topic
client.publish("test/faculty1", "hello");
```

### **Alternative 2: Reduce Payload Size**
Send minimal response first:
```cpp
String minimal = "{\"faculty_id\":1,\"response_type\":\"BUSY\",\"message_id\":\"11\"}";
```

### **Alternative 3: Use QoS 0**
Remove QoS requirements:
```cpp
client.publish(topic, payload, false);  // retained = false, QoS = 0
```

The key is identifying whether the issue is:
- **Authentication** (broker rejecting connection)
- **Authorization** (broker rejecting topic access)  
- **Network** (packets not reaching broker)
- **Resource** (broker or ESP32 overloaded) 