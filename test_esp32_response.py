#!/usr/bin/env python3
"""
ESP32 Response Test Script

This script tests ESP32 response processing by creating consultations
and simulating ESP32 button responses.

Usage:
    cd ConsultEaseV7
    python test_esp32_response.py
"""

import sys
import os
import time
import json
import logging
import socket
import paho.mqtt.client as mqtt
from datetime import datetime

# Add central_system to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'central_system'))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Import central system modules
    from central_system.models.base import get_db, init_db
    from central_system.models.consultation import Consultation, ConsultationStatus
    from central_system.models.student import Student
    from central_system.models.faculty import Faculty
    
    logger.info("✅ Successfully imported central system modules")
except ImportError as e:
    logger.error(f"❌ Failed to import central system modules: {e}")
    logger.info("💡 Make sure you're running from the ConsultEaseV7 directory")
    logger.info("💡 Try: cd ConsultEaseV7 && python test_esp32_response.py")
    sys.exit(1)

# MQTT Configuration
POSSIBLE_BROKERS = [
    "172.20.10.8",      # From your successful test
    "192.168.1.100",    # ESP32 configured address
    "localhost",        # Default central system
    "127.0.0.1",        # Localhost IP
]
PORT = 1883
FACULTY_ID = 1
STUDENT_ID = 1

# Topics
RESPONSES_TOPIC = f"consultease/faculty/{FACULTY_ID}/responses"

def find_mqtt_broker():
    """Find an accessible MQTT broker."""
    logger.info("🔍 Searching for accessible MQTT brokers...")
    
    for broker in POSSIBLE_BROKERS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((broker, PORT))
            sock.close()
            if result == 0:
                logger.info(f"✅ Found accessible broker: {broker}:{PORT}")
                return broker
            else:
                logger.info(f"❌ Cannot reach {broker}:{PORT}")
        except Exception as e:
            logger.debug(f"Connection test failed for {broker}:{PORT} - {e}")
    
    logger.error("❌ No accessible MQTT brokers found!")
    return None

def setup_test_data():
    """Set up test student and faculty if they don't exist."""
    logger.info("📝 Setting up test data...")
    
    try:
        init_db()
        db = get_db()
        
        try:
            # Check if test student exists, create if not
            student = db.query(Student).filter(Student.id == STUDENT_ID).first()
            if not student:
                student = Student(
                    id=STUDENT_ID,
                    student_id="TEST123",
                    name="Test Student",
                    email="test@student.com",
                    course="Computer Science",
                    year_level="4th Year"
                )
                db.add(student)
                logger.info("➕ Created test student")
            
            # Check if test faculty exists
            faculty = db.query(Faculty).filter(Faculty.id == FACULTY_ID).first()
            if not faculty:
                faculty = Faculty(
                    id=FACULTY_ID,
                    name="Dave Jomillo",
                    department="Helpdesk",
                    email="djo@hd.com"
                )
                db.add(faculty)
                logger.info("➕ Created test faculty")
            
            db.commit()
            logger.info("✅ Test data setup complete")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Failed to setup test data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def create_test_consultation():
    """Create a test consultation in the database."""
    logger.info("📝 Creating test consultation...")
    
    try:
        db = get_db()
        
        try:
            # Create a new consultation
            consultation = Consultation(
                student_id=STUDENT_ID,
                faculty_id=FACULTY_ID,
                message="Please help me with my project - this is a test consultation",
                status=ConsultationStatus.PENDING,
                created_at=datetime.now()
            )
            
            db.add(consultation)
            db.commit()
            
            consultation_id = consultation.id
            logger.info(f"✅ Created test consultation with ID: {consultation_id}")
            
            return consultation_id
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Failed to create test consultation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def verify_consultation_status(consultation_id, expected_status):
    """Verify the consultation status in the database."""
    logger.info(f"🔍 Verifying consultation {consultation_id} status...")
    
    try:
        db = get_db()
        try:
            consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
            
            if not consultation:
                logger.error(f"❌ Consultation {consultation_id} not found in database")
                return False
            
            actual_status = consultation.status.value
            logger.info(f"📊 Consultation {consultation_id} status: {actual_status}")
            
            if actual_status == expected_status:
                logger.info(f"✅ Status verification successful: {actual_status}")
                return True
            else:
                logger.warning(f"⚠️ Status mismatch - Expected: {expected_status}, Actual: {actual_status}")
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Failed to verify consultation status: {e}")
        return False

class ESP32ResponseTester:
    """Test ESP32 response processing."""
    
    def __init__(self, broker_host):
        self.broker_host = broker_host
        self.client = mqtt.Client("ESP32_Response_Tester")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.connected = False
        self.received_messages = []
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection."""
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Connected to MQTT broker at {self.broker_host}:{PORT}")
            
            # Subscribe to system notifications to see if central system responds
            client.subscribe("consultease/system/notifications")
            logger.info("📬 Subscribed to system notifications")
        else:
            self.connected = False
            logger.error(f"❌ Failed to connect to MQTT broker, return code: {rc}")
    
    def on_publish(self, client, userdata, mid):
        """Callback for published messages."""
        logger.info(f"📤 Message published successfully (MID: {mid})")
    
    def on_message(self, client, userdata, msg):
        """Callback for received messages."""
        message_info = {
            'topic': msg.topic,
            'payload': msg.payload.decode(),
            'timestamp': datetime.now()
        }
        self.received_messages.append(message_info)
        logger.info(f"📥 Received: {msg.topic} - {msg.payload.decode()}")
    
    def connect(self):
        """Connect to MQTT broker."""
        try:
            logger.info(f"🔌 Connecting to MQTT broker at {self.broker_host}:{PORT}...")
            self.client.connect(self.broker_host, PORT, 60)
            self.client.loop_start()
            
            # Wait for connection with timeout
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                logger.info("✅ MQTT connection established successfully")
                return True
            else:
                logger.error("❌ MQTT connection timeout")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            return False
    
    def send_esp32_response(self, consultation_id, response_type="ACKNOWLEDGE"):
        """Send ESP32-style button response."""
        logger.info("=" * 60)
        logger.info(f"SENDING ESP32 {response_type} RESPONSE")
        logger.info("=" * 60)
        
        # Create ESP32 button response exactly as ESP32 sends it
        response_data = {
            "faculty_id": FACULTY_ID,
            "faculty_name": "Dave Jomillo",
            "response_type": response_type,
            "message_id": str(consultation_id),  # ESP32 sends as string
            "original_message": "Test consultation request",
            "timestamp": str(int(time.time() * 1000)),
            "faculty_present": True,
            "response_method": "physical_button",
            "status": f"Professor {response_type.lower()}s the request"
        }
        
        logger.info(f"📨 Sending to topic: {RESPONSES_TOPIC}")
        logger.info(f"📨 Response data: {json.dumps(response_data, indent=2)}")
        
        result = self.client.publish(RESPONSES_TOPIC, json.dumps(response_data), qos=2)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"✅ ESP32 {response_type} response sent successfully")
            return True
        else:
            logger.error(f"❌ Failed to send ESP32 response, error code: {result.rc}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive ESP32 response test."""
        logger.info("🚀 Starting ESP32 Response Test...")
        
        # Step 1: Setup test data
        if not setup_test_data():
            logger.error("❌ Failed to setup test data")
            return False
        
        # Step 2: Connect to MQTT
        if not self.connect():
            logger.error("❌ Failed to connect to MQTT broker")
            return False
        
        # Step 3: Test ACKNOWLEDGE response
        logger.info("\n🔵 Testing ACKNOWLEDGE Response Flow")
        logger.info("-" * 40)
        
        consultation_id_1 = create_test_consultation()
        if not consultation_id_1:
            logger.error("❌ Failed to create consultation for ACKNOWLEDGE test")
            return False
        
        time.sleep(2)  # Brief pause
        
        if not self.send_esp32_response(consultation_id_1, "ACKNOWLEDGE"):
            logger.error("❌ Failed to send ACKNOWLEDGE response")
            return False
        
        logger.info("⏳ Waiting for central system to process ACKNOWLEDGE...")
        time.sleep(5)
        
        acknowledge_success = verify_consultation_status(consultation_id_1, "ACCEPTED")
        
        # Step 4: Test BUSY response
        logger.info("\n🔴 Testing BUSY Response Flow")
        logger.info("-" * 40)
        
        consultation_id_2 = create_test_consultation()
        if not consultation_id_2:
            logger.error("❌ Failed to create consultation for BUSY test")
            return False
        
        time.sleep(2)  # Brief pause
        
        if not self.send_esp32_response(consultation_id_2, "BUSY"):
            logger.error("❌ Failed to send BUSY response")
            return False
        
        logger.info("⏳ Waiting for central system to process BUSY...")
        time.sleep(5)
        
        busy_success = verify_consultation_status(consultation_id_2, "BUSY")
        
        # Final Results
        logger.info("\n📋 ESP32 Response Test Results")
        logger.info("=" * 50)
        logger.info(f"✅ ACKNOWLEDGE test: {'PASSED' if acknowledge_success else 'FAILED'}")
        logger.info(f"🔴 BUSY test: {'PASSED' if busy_success else 'FAILED'}")
        logger.info(f"📥 MQTT messages received: {len(self.received_messages)}")
        
        if acknowledge_success and busy_success:
            logger.info("🎉 ALL TESTS PASSED! ESP32 ↔ Central System communication is working!")
            logger.info("✅ The Faculty Response Controller is properly processing ESP32 button responses")
        elif acknowledge_success or busy_success:
            logger.info("⚠️ PARTIAL SUCCESS - Some responses are working")
            logger.info("🔧 Check central system logs for Faculty Response Controller issues")
        else:
            logger.error("❌ ALL TESTS FAILED")
            logger.info("🔍 Troubleshooting steps:")
            logger.info("   1. Make sure central system is running: python central_system/main.py")
            logger.info("   2. Check for '🔥 FACULTY RESPONSE HANDLER TRIGGERED' in central system logs")
            logger.info("   3. Verify MQTT broker configuration matches")
            logger.info("   4. Check Faculty Response Controller is subscribed to topics")
        
        return acknowledge_success and busy_success
    
    def cleanup(self):
        """Clean up MQTT connection."""
        self.client.loop_stop()
        self.client.disconnect()

def main():
    """Main function."""
    logger.info("🔧 ESP32 Response Processing Test")
    logger.info("=" * 60)
    logger.info("This test verifies that the central system can receive")
    logger.info("and process ESP32 button responses correctly.")
    logger.info("=" * 60)
    
    # Find accessible broker
    broker_host = find_mqtt_broker()
    if not broker_host:
        logger.error("❌ Cannot proceed without an accessible MQTT broker")
        logger.info("💡 Make sure MQTT broker is running and accessible")
        return False
    
    # Run the test
    tester = ESP32ResponseTester(broker_host)
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            logger.info("\n🎉 Test completed successfully!")
            logger.info("The ESP32 faculty desk unit button system should work correctly.")
        else:
            logger.info("\n⚠️ Test had issues. Please check central system configuration.")
            
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 