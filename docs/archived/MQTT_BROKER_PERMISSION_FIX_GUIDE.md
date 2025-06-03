# MQTT Broker Permission Fix Guide for ConsultEase

## 🔍 **Problem Identified**
Your ESP32 faculty desk unit can **subscribe** to MQTT topics but **cannot publish** responses back to the central system. This is an **asymmetric permission issue** in the MQTT broker configuration.

**Symptoms:**
- ✅ ESP32 receives consultation messages 
- ❌ ESP32 cannot send button responses
- ✅ MQTT connection is stable (state 0 = CONNECTED)

## 🚀 **Solution Overview**

The issue is in the Mosquitto MQTT broker Access Control List (ACL) configuration. The `faculty_desk` user needs **WRITE** permissions for response topics.

## 📋 **Option 1: Automated Fix (Recommended)**

### Step 1: Transfer Fix Script to Raspberry Pi

**From Windows (this computer):**
```powershell
# Copy the fix script to your Raspberry Pi
scp scripts/fix_mqtt_permissions.sh pi@<your_pi_ip>:/home/pi/
scp scripts/test_mqtt_permissions.py pi@<your_pi_ip>:/home/pi/
```

### Step 2: Run the Fix Script on Raspberry Pi

**SSH into your Raspberry Pi:**
```bash
ssh pi@<your_pi_ip>
```

**Run the automated fix:**
```bash
sudo bash fix_mqtt_permissions.sh
```

The script will:
1. ✅ Backup existing configuration
2. ✅ Create proper user accounts
3. ✅ Set up ACL with correct permissions
4. ✅ Test the configuration
5. ✅ Restart Mosquitto service

### Step 3: Verify the Fix

**Test MQTT permissions:**
```bash
python3 test_mqtt_permissions.py
```

If successful, you should see:
```
✅ Faculty can now publish responses! Permission issue FIXED!
🎉 PERMISSION ISSUE FIXED!
```

## 📋 **Option 2: Manual Fix**

If you prefer to fix manually or the script doesn't work:

### Step 1: SSH to Raspberry Pi
```bash
ssh pi@<your_pi_ip>
```

### Step 2: Stop Mosquitto Service
```bash
sudo systemctl stop mosquitto
```

### Step 3: Backup Existing Configuration
```bash
sudo cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.backup
sudo cp /etc/mosquitto/acl.conf /etc/mosquitto/acl.conf.backup 2>/dev/null || true
```

### Step 4: Create Mosquitto Configuration
```bash
sudo tee /etc/mosquitto/mosquitto.conf << 'EOF'
# ConsultEase MQTT Broker Configuration
pid_file /var/run/mosquitto.pid
persistence true
persistence_location /var/lib/mosquitto/
log_dest file /var/log/mosquitto/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# Network settings  
port 1883
max_connections -1
allow_anonymous false

# Authentication
password_file /etc/mosquitto/passwd

# Access Control List
acl_file /etc/mosquitto/acl.conf

# Connection settings
connection_messages true
log_timestamp true
EOF
```

### Step 5: Create ACL File with Proper Permissions
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

# Faculty Desk Units - Specific permissions for faculty operations
user faculty_desk
# Read permissions (subscribe)
topic read consultease/faculty/+/messages
topic read consultease/faculty/+/commands
topic read consultease/system/+
topic read test/+

# Write permissions (publish) - THIS IS THE KEY FIX
topic write consultease/faculty/+/responses
topic write consultease/faculty/+/status
topic write consultease/faculty/+/heartbeat
topic write faculty/+/responses
topic write faculty/+/status
topic write test/+

# Legacy topic support
topic read faculty/+/messages
topic write faculty/+/responses
topic write faculty/+/status
EOF
```

### Step 6: Create User Accounts
```bash
# Remove existing password file
sudo rm -f /etc/mosquitto/passwd

# Create central system user
sudo mosquitto_passwd -c /etc/mosquitto/passwd central_system
# When prompted, enter: central_secure_password

# Create faculty desk user
sudo mosquitto_passwd /etc/mosquitto/passwd faculty_desk
# When prompted, enter: desk_password
```

### Step 7: Set File Permissions
```bash
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
sudo chown mosquitto:mosquitto /etc/mosquitto/acl.conf
sudo chown mosquitto:mosquitto /etc/mosquitto/mosquitto.conf
sudo chmod 640 /etc/mosquitto/passwd
sudo chmod 644 /etc/mosquitto/acl.conf
sudo chmod 644 /etc/mosquitto/mosquitto.conf
```

### Step 8: Start Mosquitto Service
```bash
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

### Step 9: Test the Fix
```bash
# Test faculty desk can publish responses (the key test)
mosquitto_pub -h localhost -u faculty_desk -P desk_password \
  -t "consultease/faculty/1/responses" \
  -m '{"test":"permission_fix","faculty_id":1,"status":"available"}'
```

If successful, no error should appear.

## 🧪 **Verification Steps**

### Test 1: Manual MQTT Test
```bash
# In terminal 1 - Subscribe to responses
mosquitto_sub -h localhost -u central_system -P central_secure_password \
  -t "consultease/faculty/1/responses" -v

# In terminal 2 - Publish a response
mosquitto_pub -h localhost -u faculty_desk -P desk_password \
  -t "consultease/faculty/1/responses" \
  -m '{"consultation_id":123,"faculty_id":1,"response":"ACKNOWLEDGED"}'
```

### Test 2: Python Test Script
```bash
python3 test_mqtt_permissions.py
```

### Test 3: ESP32 Test
1. Power cycle your ESP32
2. Send a consultation from the central system
3. Press the ACKNOWLEDGE or BUSY button
4. Check if the central system receives the response

## 🔧 **ESP32 Configuration Update**

After fixing the broker, ensure your ESP32 has the correct configuration:

**In `config.h`:**
```cpp
#define MQTT_SERVER "192.168.1.100"  // Your Raspberry Pi IP
#define MQTT_PORT 1883
#define MQTT_USERNAME "faculty_desk"
#define MQTT_PASSWORD "desk_password"
```

## 📊 **Expected Results After Fix**

**✅ What should work now:**
- ESP32 connects to MQTT broker
- ESP32 receives consultation messages
- ESP32 publishes button responses
- Central system receives ESP32 responses
- Faculty status updates work

**🔍 Central System Logs Should Show:**
```
🔥 FACULTY RESPONSE HANDLER TRIGGERED
📨 Received faculty response: {"consultation_id":123,"response":"ACKNOWLEDGED"}
✅ Successfully updated consultation status: 123 (PENDING -> BUSY)
```

**🔍 ESP32 Serial Monitor Should Show:**
```
✅ MQTT publish reported SUCCESS
📤 Response sent: {"consultation_id":123,"faculty_id":1,"response":"ACKNOWLEDGED"}
```

## 🚨 **Troubleshooting**

### If the Fix Doesn't Work:

1. **Check Mosquitto Logs:**
   ```bash
   sudo journalctl -u mosquitto -f
   ```

2. **Verify Service Status:**
   ```bash
   sudo systemctl status mosquitto
   ```

3. **Test Basic Connectivity:**
   ```bash
   mosquitto_pub -h localhost -t "test" -m "hello"
   mosquitto_sub -h localhost -t "test" -C 1
   ```

4. **Check Configuration Syntax:**
   ```bash
   sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
   ```

### Common Issues:

- **Permission denied:** Check file ownership with `ls -la /etc/mosquitto/`
- **Authentication failed:** Verify password file with `sudo cat /etc/mosquitto/passwd`
- **Topic access denied:** Check ACL file syntax in `/etc/mosquitto/acl.conf`

## 🎯 **Summary**

The core issue was that the MQTT broker ACL only allowed the `faculty_desk` user to **read** topics but not **write** to response topics. The fix adds these critical **write** permissions:

```
topic write consultease/faculty/+/responses
topic write consultease/faculty/+/status
topic write consultease/faculty/+/heartbeat
```

This allows your ESP32 faculty desk unit to publish button responses back to the central system, completing the two-way communication flow.

## 📞 **Need Help?**

If you encounter any issues:
1. Run the automated fix script first
2. Check the troubleshooting section
3. Verify ESP32 configuration matches the broker settings
4. Test step-by-step using the verification commands

The permission fix should resolve the asymmetric MQTT communication issue and enable full ESP32 ↔ Central System communication. 