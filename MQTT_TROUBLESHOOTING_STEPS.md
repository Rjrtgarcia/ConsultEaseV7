# MQTT Troubleshooting Steps for ConsultEase

## 🚨 **Current Issue**
The Mosquitto service failed to start after running the permission fix script. Let's diagnose and fix this.

## 🔍 **Step 1: Check Service Status and Logs**

**Run these commands on your Raspberry Pi:**

```bash
# Check Mosquitto service status
sudo systemctl status mosquitto.service

# Check detailed logs
sudo journalctl -xeu mosquitto.service --no-pager -n 20

# Check if there are any configuration errors
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
```

## 🔧 **Step 2: Common Fixes**

### Fix A: Configuration File Issues

**Check if the config file has syntax errors:**
```bash
# Test the configuration
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v

# If there are errors, restore the backup
sudo cp /etc/mosquitto/mosquitto.conf.backup_20250602_214114 /etc/mosquitto/mosquitto.conf
```

### Fix B: Password File Issues

**The password creation might have failed. Let's recreate the users:**
```bash
# Remove the password file and recreate
sudo rm -f /etc/mosquitto/passwd

# Create central system user (enter: central_secure_password when prompted)
sudo mosquitto_passwd -c /etc/mosquitto/passwd central_system

# Create faculty desk user (enter: desk_password when prompted)  
sudo mosquitto_passwd /etc/mosquitto/passwd faculty_desk

# Set proper permissions
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
sudo chmod 640 /etc/mosquitto/passwd
```

### Fix C: ACL File Issues

**Check if the ACL file has syntax errors:**
```bash
# Check ACL file exists and has content
sudo cat /etc/mosquitto/acl.conf

# If it's empty or has issues, recreate it
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

# Set proper permissions
sudo chown mosquitto:mosquitto /etc/mosquitto/acl.conf
sudo chmod 644 /etc/mosquitto/acl.conf
```

## 🔄 **Step 3: Restart Mosquitto Service**

```bash
# Try to start the service
sudo systemctl start mosquitto

# Check if it's running
sudo systemctl status mosquitto

# If successful, enable it to start on boot
sudo systemctl enable mosquitto
```

## 🧪 **Step 4: Test the Configuration**

**If Mosquitto starts successfully, test the permissions:**

```bash
# Test 1: Basic connectivity
mosquitto_pub -h localhost -t "test" -m "hello"

# Test 2: Faculty desk authentication  
mosquitto_pub -h localhost -u faculty_desk -P desk_password -t "test/faculty" -m "test"

# Test 3: Key permission test - Faculty publishing responses
mosquitto_pub -h localhost -u faculty_desk -P desk_password \
  -t "consultease/faculty/1/responses" \
  -m '{"test":"permission_fix","faculty_id":1,"status":"available"}'
```

**If Test 3 works without errors, the permission issue is FIXED! 🎉**

## 🚨 **Step 5: Alternative Fix - Simple Configuration**

**If the above doesn't work, let's try a minimal configuration:**

```bash
# Stop mosquitto
sudo systemctl stop mosquitto

# Create a simple configuration without ACL first
sudo tee /etc/mosquitto/mosquitto.conf << 'EOF'
# Basic Mosquitto Configuration
pid_file /var/run/mosquitto.pid
persistence true
persistence_location /var/lib/mosquitto/
log_dest file /var/log/mosquitto/mosquitto.log

# Network settings  
port 1883
max_connections -1
allow_anonymous true

# Connection settings
connection_messages true
log_timestamp true
EOF

# Start mosquitto with basic config
sudo systemctl start mosquitto
sudo systemctl status mosquitto
```

**Test basic functionality:**
```bash
# This should work with allow_anonymous true
mosquitto_pub -h localhost -t "test" -m "basic_test"
mosquitto_sub -h localhost -t "test" -C 1
```

**If basic config works, then gradually add authentication back:**

```bash
# Stop service
sudo systemctl stop mosquitto

# Add authentication back
sudo tee /etc/mosquitto/mosquitto.conf << 'EOF'
# ConsultEase MQTT Broker Configuration
pid_file /var/run/mosquitto.pid
persistence true
persistence_location /var/lib/mosquitto/
log_dest file /var/log/mosquitto/mosquitto.log

# Network settings  
port 1883
max_connections -1
allow_anonymous false

# Authentication
password_file /etc/mosquitto/passwd

# Connection settings
connection_messages true
log_timestamp true
EOF

# Recreate password file
sudo rm -f /etc/mosquitto/passwd
sudo mosquitto_passwd -c /etc/mosquitto/passwd central_system  # Enter: central_secure_password
sudo mosquitto_passwd /etc/mosquitto/passwd faculty_desk      # Enter: desk_password
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
sudo chmod 640 /etc/mosquitto/passwd

# Start service
sudo systemctl start mosquitto
```

## 🎯 **Step 6: Run the Fixed Script**

**Once you've fixed the configuration manually, you can run the corrected script:**

```bash
# Copy the updated script from your Windows machine again, or
# Run the fixed version that should now work:
sudo bash fix_mqtt_permissions.sh
```

## 📋 **Common Error Messages and Solutions**

| Error Message | Solution |
|---------------|----------|
| `Error: Unable to open password file` | Recreate password file with proper permissions |
| `Error: Invalid user/password` | Check password file format and user creation |
| `Error: Unable to load ACL file` | Check ACL file syntax and permissions |
| `Error: Address already in use` | Another MQTT broker is running on port 1883 |
| `Permission denied` | Check file ownership with `ls -la /etc/mosquitto/` |

## 🎉 **Success Indicators**

You'll know it's working when:
- `sudo systemctl status mosquitto` shows "active (running)"
- `mosquitto_pub -h localhost -u faculty_desk -P desk_password -t "consultease/faculty/1/responses" -m "test"` succeeds
- No errors in `sudo journalctl -u mosquitto -f`

## 📞 **Next Steps After Fix**

Once Mosquitto is running properly:
1. Test with: `python3 test_mqtt_permissions.py` 
2. Update your ESP32 with the new credentials
3. Test the full consultation flow

Let me know what the error logs show and I'll help you fix the specific issue! 