#!/usr/bin/env python3
"""
Test ESP32 Communication Script

This script simulates ESP32 communication to test if the central system
can receive and process faculty response messages properly.

Usage:
    python scripts/test_esp32_communication.py
"""

import sys
import time
import json
import logging
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MQTT Configuration
BROKER = "192.168.1.100"
PORT = 1883
FACULTY_ID = 1

# Topics
RESPONSES_TOPIC = f"consultease/faculty/{FACULTY_ID}/responses"
MESSAGES_TOPIC = f"consultease/faculty/{FACULTY_ID}/messages"

class ESP32CommunicationTester:
    """Test ESP32 communication with central system."""
    
    def __init__(self):
        self.client = mqtt.Client("ESP32_Communication_Tester")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection."""
        if rc == 0:
            logger.info(f"✅ Connected to MQTT broker at {BROKER}:{PORT}")
            
            # Subscribe to see if we get anything back
            client.subscribe("consultease/system/notifications")
            logger.info("📬 Subscribed to system notifications")
        else:
            logger.error(f"❌ Failed to connect to MQTT broker, return code: {rc}")
    
    def on_publish(self, client, userdata, mid):
        """Callback for published messages."""
        logger.info(f"📤 Message published successfully (MID: {mid})")
    
    def on_message(self, client, userdata, msg):
        """Callback for received messages."""
        logger.info(f"📥 Received response: {msg.topic} - {msg.payload.decode()}")
    
    def connect(self):
        """Connect to MQTT broker."""
        try:
            self.client.connect(BROKER, PORT, 60)
            self.client.loop_start()
            time.sleep(2)  # Wait for connection
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            return False
    
    def send_test_consultation_message(self):
        """Send a test consultation message to ESP32."""
        logger.info("=" * 60)
        logger.info("SENDING TEST CONSULTATION MESSAGE")
        logger.info("=" * 60)
        
        # Create test consultation message (simulating central system)
        consultation_id = int(time.time())
        message = f"CID:{consultation_id} From:Test Student (SID:123): Please help me with my project"
        
        logger.info(f"📨 Sending to topic: {MESSAGES_TOPIC}")
        logger.info(f"📨 Message: {message}")
        
        result = self.client.publish(MESSAGES_TOPIC, message, qos=2)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ Test consultation message sent successfully")
            return consultation_id
        else:
            logger.error(f"❌ Failed to send message, error code: {result.rc}")
            return None
    
    def send_test_button_response(self, consultation_id):
        """Send a test button response (simulating ESP32)."""
        logger.info("=" * 60)
        logger.info("SENDING TEST BUTTON RESPONSE")
        logger.info("=" * 60)
        
        # Create ESP32 button response
        response_data = {
            "faculty_id": FACULTY_ID,
            "faculty_name": "Dave Jomillo",
            "response_type": "ACKNOWLEDGE",
            "message_id": str(consultation_id),
            "original_message": "Test consultation request",
            "timestamp": str(int(time.time() * 1000)),
            "faculty_present": True,
            "response_method": "physical_button",
            "status": "Professor acknowledges the request and will respond accordingly"
        }
        
        logger.info(f"📨 Sending to topic: {RESPONSES_TOPIC}")
        logger.info(f"📨 Response data: {json.dumps(response_data, indent=2)}")
        
        result = self.client.publish(RESPONSES_TOPIC, json.dumps(response_data), qos=2)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ Test button response sent successfully")
            return True
        else:
            logger.error(f"❌ Failed to send response, error code: {result.rc}")
            return False
    
    def run_test(self):
        """Run the complete communication test."""
        logger.info("🚀 Starting ESP32 communication test...")
        
        if not self.connect():
            return False
        
        # Step 1: Send consultation message (central system → ESP32)
        consultation_id = self.send_test_consultation_message()
        if not consultation_id:
            return False
        
        # Wait a bit
        time.sleep(3)
        
        # Step 2: Send button response (ESP32 → central system)
        success = self.send_test_button_response(consultation_id)
        if not success:
            return False
        
        # Wait for any responses
        logger.info("⏳ Waiting for central system to process the response...")
        time.sleep(10)
        
        # Step 3: Send BUSY response as well
        response_data = {
            "faculty_id": FACULTY_ID,
            "faculty_name": "Dave Jomillo",
            "response_type": "BUSY",
            "message_id": str(consultation_id + 1),
            "original_message": "Another test consultation request",
            "timestamp": str(int(time.time() * 1000)),
            "faculty_present": True,
            "response_method": "physical_button",
            "status": "Professor is currently busy and cannot cater to this request"
        }
        
        logger.info("📨 Sending BUSY response test...")
        self.client.publish(RESPONSES_TOPIC, json.dumps(response_data), qos=2)
        
        # Final wait
        time.sleep(5)
        
        logger.info("✅ ESP32 communication test completed!")
        logger.info("🔍 Check central system logs for faculty response handling")
        
        return True
    
    def cleanup(self):
        """Clean up MQTT connection."""
        self.client.loop_stop()
        self.client.disconnect()

def main():
    """Main function."""
    tester = ESP32CommunicationTester()
    
    try:
        success = tester.run_test()
        if success:
            logger.info("🎉 Test completed successfully")
        else:
            logger.error("❌ Test failed")
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 