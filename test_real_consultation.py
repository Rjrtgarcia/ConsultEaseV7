#!/usr/bin/env python3
"""
Test Real Consultation Button Response

This script simulates ESP32 button responses for the actual consultation
that was just created (ID: 1) for Jerome Ibon -> Dave Jomillo.

Usage: python test_real_consultation.py
"""

import time
import json
import logging
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
BROKER = "172.20.10.8"  # Working broker
PORT = 1883
FACULTY_ID = 1

# MQTT Topics
RESPONSE_TOPIC = f"consultease/faculty/{FACULTY_ID}/responses"

class RealConsultationTester:
    def __init__(self):
        self.client = mqtt.Client("RealConsultationTester")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Connected to MQTT broker at {BROKER}:{PORT}")
            # Subscribe to notifications
            client.subscribe("consultease/system/notifications")
            client.subscribe("consultease/consultations/+")
            logger.info("📬 Subscribed to system notifications and consultations")
        else:
            logger.error(f"❌ Failed to connect, return code: {rc}")
    
    def on_publish(self, client, userdata, mid):
        logger.info(f"📤 Message published (MID: {mid})")
    
    def on_message(self, client, userdata, msg):
        logger.info(f"📥 Received: {msg.topic} - {msg.payload.decode()}")
    
    def connect(self):
        try:
            logger.info(f"🔌 Connecting to {BROKER}:{PORT}...")
            self.client.connect(BROKER, PORT, 60)
            self.client.loop_start()
            
            # Wait for connection
            for i in range(50):
                if self.connected:
                    return True
                time.sleep(0.1)
            
            logger.error("❌ Connection timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def send_button_response_for_real_consultation(self, response_type):
        """Send button response for the real consultation ID 1."""
        logger.info("=" * 60)
        logger.info(f"🔘 TESTING {response_type} FOR REAL CONSULTATION ID 1")
        logger.info("=" * 60)
        logger.info("📋 This is for the actual consultation:")
        logger.info("   Student: Jerome Ibon (ID: 1)")
        logger.info("   Faculty: Dave Jomillo (ID: 1)")
        logger.info("   Consultation ID: 1")
        logger.info("=" * 60)
        
        # Create response data exactly like ESP32 sends for consultation ID 1
        response_data = {
            "faculty_id": FACULTY_ID,
            "faculty_name": "Dave Jomillo", 
            "response_type": response_type,
            "message_id": "1",  # This is the real consultation ID!
            "original_message": "CID:1 From:Jerome Ibon (SID:1): pussy ass nigga",
            "timestamp": str(int(time.time() * 1000)),
            "faculty_present": True,
            "response_method": "physical_button",
            "status": f"Professor {response_type.lower()}s the request"
        }
        
        logger.info(f"📨 Sending to: {RESPONSE_TOPIC}")
        logger.info(f"📄 Data: {json.dumps(response_data, indent=2)}")
        
        result = self.client.publish(RESPONSE_TOPIC, json.dumps(response_data), qos=2)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"✅ {response_type} response sent successfully for consultation ID 1")
            return True
        else:
            logger.error(f"❌ Failed to send {response_type} response")
            return False
    
    def test_real_consultation_buttons(self):
        """Test button responses for the real consultation."""
        logger.info("🚀 Testing ESP32 Buttons for REAL Consultation")
        logger.info("=" * 60)
        logger.info("🎯 This test will simulate pressing ESP32 buttons for")
        logger.info("   the actual consultation that was just created!")
        logger.info("")
        
        if not self.connect():
            return False
        
        # Wait a moment for any messages
        time.sleep(2)
        
        logger.info("🔵 Testing ACKNOWLEDGE button for consultation ID 1...")
        if self.send_button_response_for_real_consultation("ACKNOWLEDGE"):
            logger.info("⏳ Waiting 5 seconds for central system to process...")
            time.sleep(5)
            
            logger.info("📊 Check your dashboard! The consultation should now show:")
            logger.info("   Status: ACCEPTED (if ACKNOWLEDGE worked)")
            logger.info("")
        
        logger.info("🔴 Now testing BUSY button (this will create a conflict)...")
        if self.send_button_response_for_real_consultation("BUSY"):
            logger.info("⏳ Waiting 5 seconds for central system to process...")
            time.sleep(5)
            
            logger.info("📊 Check your dashboard! The consultation might show:")
            logger.info("   Status: BUSY (if BUSY response was processed)")
            logger.info("   OR Status: ACCEPTED (if already accepted)")
            logger.info("")
        
        logger.info("🏁 Real consultation button test completed!")
        logger.info("🔍 Look at your central system logs for:")
        logger.info("   🔥 FACULTY RESPONSE HANDLER TRIGGERED")
        logger.info("   ✅ Successfully updated consultation 1 to status ACCEPTED")
        logger.info("   ✅ Successfully updated consultation 1 to status BUSY")
        logger.info("")
        logger.info("📱 Check the student dashboard to see if consultation status changed!")
        
        # Wait for any responses
        logger.info("⏳ Waiting 10 seconds for system responses...")
        time.sleep(10)
        
        return True
    
    def cleanup(self):
        self.client.loop_stop()
        self.client.disconnect()

def main():
    logger.info("🔧 Real Consultation ESP32 Button Test")
    logger.info("Testing ESP32 buttons for actual consultation ID 1")
    logger.info("=" * 60)
    
    tester = RealConsultationTester()
    
    try:
        success = tester.test_real_consultation_buttons()
        if success:
            logger.info("✅ Test completed! Check dashboard for consultation status changes.")
        else:
            logger.error("❌ Test failed")
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 