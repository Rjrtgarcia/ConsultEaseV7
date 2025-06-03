# MQTT Troubleshooting Guide for ConsultEase

## Overview
This consolidated guide covers all common MQTT issues and troubleshooting steps for the ConsultEase system.

## Common Issues

### 1. ESP32 Cannot Publish Responses
- **Symptoms**: ESP32 faculty desk unit can receive messages but cannot publish responses back
- **Likely Cause**: MQTT broker Access Control List (ACL) permissions
- **Verification**: ESP32 shows "MQTT connected: TRUE" but responses never arrive at central system

#### Solution
1. **Check MQTT Broker ACL Configuration**:
   ```bash
   # For Mosquitto, check:
   sudo cat /etc/mosquitto/acl.conf
   # or
   sudo cat /etc/mosquitto/mosquitto.conf
   ```

2. **Add publish permissions**:
   ```bash
   sudo tee /etc/mosquitto/acl.conf << 'EOF'
   # ConsultEase MQTT Access Control List

   # Central System - Full access to all topics
   user central_system
   topic readwrite consultease/#
   topic readwrite faculty/#
   topic readwrite student/#
   topic readwrite system/#
   topic readwrite test/#

   # Faculty Desk Units - Specific permissions
   user faculty_desk
   # Read permissions (subscribe)
   topic read consultease/faculty/+/messages
   topic read consultease/faculty/+/commands
   topic read consultease/system/+
   topic read test/+

   # Write permissions (publish)
   topic write consultease/faculty/+/responses
   topic write consultease/faculty/+/status
   topic write consultease/faculty/+/heartbeat
   topic write faculty/+/responses
   topic write faculty/+/status
   topic write test/+
   EOF
   ```

3. **Restart MQTT broker**:
   ```bash
   sudo systemctl restart mosquitto
   ```

4. **Verify fix with test tools**:
   ```bash
   # Test with the test utility
   python scripts/test_utility.py mqtt-test --broker 192.168.1.100
   ```

### 2. MQTT Broker Fails to Start

#### Diagnostic Steps
```bash
# Check service status
sudo systemctl status mosquitto.service

# Check detailed logs
sudo journalctl -xeu mosquitto.service --no-pager -n 20

# Check for configuration errors
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
```

#### Common Fixes
1. **Configuration File Issues**:
   ```bash
   # Test the configuration
   sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v

   # If there are errors, restore the backup or create minimal config
   sudo cp /etc/mosquitto/mosquitto.conf.backup /etc/mosquitto/mosquitto.conf
   # or
   sudo tee /etc/mosquitto/mosquitto.conf << 'EOF'
   # Basic Mosquitto Configuration
   pid_file /var/run/mosquitto.pid
   persistence true
   persistence_location /var/lib/mosquitto/
   log_dest file /var/log/mosquitto/mosquitto.log
   port 1883
   allow_anonymous true
   EOF
   ```

2. **Password File Issues**:
   ```bash
   # Remove the password file and recreate
   sudo rm -f /etc/mosquitto/passwd

   # Create users
   sudo mosquitto_passwd -c /etc/mosquitto/passwd central_system
   sudo mosquitto_passwd /etc/mosquitto/passwd faculty_desk

   # Set proper permissions
   sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
   sudo chmod 640 /etc/mosquitto/passwd
   ```

### 3. Connection Issues on ESP32

#### Diagnostic Checks
1. **Add enhanced diagnostics to ESP32**:
   ```cpp
   void runMQTTDiagnostics() {
     Serial.println("📊 MQTT Diagnostics:");
     Serial.print("   Connected: ");
     Serial.println(mqttClient.connected() ? "TRUE" : "FALSE");
     Serial.print("   State: ");
     Serial.print(mqttClient.state());
     Serial.print(" (");
     Serial.print(getMqttStateString(mqttClient.state()));
     Serial.println(")");
     Serial.print("   Server: ");
     Serial.print(MQTT_SERVER);
     Serial.print(":");
     Serial.println(MQTT_PORT);
     Serial.print("   Client ID: ");
     Serial.println(mqttClient.getClientId());
   }
   ```

2. **Add this after MQTT connection in ESP32 code**:
   ```cpp
   runMQTTDiagnostics();
   ```

#### Common ESP32 Issues and Fixes

1. **Weak WiFi Signal**:
   - Move ESP32 closer to WiFi router
   - Check signal strength with diagnostics
   - Consider using external antenna for ESP32

2. **MQTT Message Queue Full**:
   - Increase `MQTT_MAX_PACKET_SIZE` in ESP32 code
   - Implement better queue management

3. **MQTT Credential Issues**:
   - Verify MQTT credentials match broker configuration
   - Check for special characters in passwords

## Using the Fix Script

For convenience, a fix script is included to repair common MQTT issues:

```bash
# Run the fix script
sudo bash scripts/fix_mqtt_permissions.sh

# Test if the fix worked
python scripts/test_utility.py mqtt-test
```

## Advanced Troubleshooting

### Testing with MQTT CLI Tools
```bash
# Subscribe to all messages
mosquitto_sub -h localhost -u central_system -P central_secure_password -t "#" -v

# Publish test message
mosquitto_pub -h localhost -u faculty_desk -P desk_password -t "consultease/faculty/1/status" -m "available"
```

### Analyzing MQTT Traffic
Use Wireshark to capture MQTT traffic:
1. Install Wireshark
2. Start capture on network interface
3. Filter: `mqtt`
4. Observe MQTT packets

### Security Considerations
- Never use default or weak passwords for MQTT
- Use ACLs to restrict topic access
- Consider using TLS encryption for production

## Checklist for MQTT Problems

- [ ] MQTT broker running (check with `systemctl status mosquitto`)
- [ ] Users created in password file
- [ ] ACL configuration allows both read and write
- [ ] ESP32 has correct broker IP and port
- [ ] ESP32 has correct credentials
- [ ] ESP32 has adequate WiFi signal
- [ ] MQTT max packet size is sufficient (>=1024 bytes)
- [ ] No firewall blocking MQTT traffic 