#!/usr/bin/env python3
"""
ConsultEase - Consultation History Update Diagnostic Script

This script tests the end-to-end flow of consultation updates:
1. Creates a test consultation request
2. Simulates faculty desk unit response
3. Verifies database update
4. Checks if consultation history reflects the change

Usage:
    python test_consultation_history_update.py --faculty-id 1 --student-id 1
"""

import sys
import time
import json
import argparse
import logging
from datetime import datetime
import paho.mqtt.client as mqtt

# Add the central_system path
sys.path.insert(0, '../central_system')

from models.base import get_db
from models.consultation import Consultation, ConsultationStatus
from controllers.consultation_controller import ConsultationController
from controllers.faculty_response_controller import get_faculty_response_controller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 1883
DEFAULT_FACULTY_ID = 1
DEFAULT_STUDENT_ID = 1

class ConsultationHistoryTester:
    """Test consultation history update flow."""
    
    def __init__(self, broker_host, broker_port, faculty_id, student_id):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.faculty_id = faculty_id
        self.student_id = student_id
        
        # MQTT client for sending test responses
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        # Test data
        self.test_consultation_id = None
        self.initial_status = None
        self.updated_status = None
        
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            logger.info(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
        else:
            logger.error(f"❌ Failed to connect to MQTT broker. Return code: {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback."""
        logger.info(f"Disconnected from MQTT broker. Return code: {rc}")
        
    def create_test_consultation(self):
        """Create a test consultation request."""
        logger.info("=" * 60)
        logger.info("STEP 1: CREATING TEST CONSULTATION")
        logger.info("=" * 60)
        
        try:
            # Create consultation using the controller
            consultation_controller = ConsultationController()
            
            consultation_data = {
                'student_id': self.student_id,
                'faculty_id': self.faculty_id,
                'request_message': 'Test consultation for history update verification',
                'course_code': 'TEST101'
            }
            
            consultation = consultation_controller.create_consultation(consultation_data)
            
            if consultation:
                self.test_consultation_id = consultation.id
                self.initial_status = consultation.status
                logger.info(f"✅ Created test consultation ID: {self.test_consultation_id}")
                logger.info(f"   Student ID: {consultation.student_id}")
                logger.info(f"   Faculty ID: {consultation.faculty_id}")
                logger.info(f"   Initial Status: {consultation.status.value}")
                logger.info(f"   Created At: {consultation.created_at}")
                return True
            else:
                logger.error("❌ Failed to create test consultation")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating test consultation: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
            
    def verify_initial_consultation(self):
        """Verify the consultation was created correctly."""
        logger.info("=" * 60)
        logger.info("STEP 2: VERIFYING INITIAL CONSULTATION")
        logger.info("=" * 60)
        
        try:
            db = get_db()
            consultation = db.query(Consultation).filter(Consultation.id == self.test_consultation_id).first()
            
            if consultation:
                logger.info(f"✅ Found consultation in database:")
                logger.info(f"   ID: {consultation.id}")
                logger.info(f"   Status: {consultation.status.value}")
                logger.info(f"   Student ID: {consultation.student_id}")
                logger.info(f"   Faculty ID: {consultation.faculty_id}")
                logger.info(f"   Message: {consultation.request_message}")
                
                if consultation.status == ConsultationStatus.PENDING:
                    logger.info("✅ Consultation status is PENDING as expected")
                    return True
                else:
                    logger.warning(f"⚠️ Expected PENDING status, got {consultation.status.value}")
                    return False
            else:
                logger.error(f"❌ Consultation {self.test_consultation_id} not found in database")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verifying consultation: {e}")
            return False
        finally:
            db.close()
            
    def send_faculty_response(self, response_type="ACKNOWLEDGE"):
        """Send a faculty response to test the update flow."""
        logger.info("=" * 60)
        logger.info(f"STEP 3: SENDING {response_type} RESPONSE")
        logger.info("=" * 60)
        
        try:
            # Connect to MQTT broker
            logger.info(f"Connecting to MQTT broker...")
            result = self.client.connect(self.broker_host, self.broker_port, 60)
            
            if result != 0:
                logger.error(f"❌ Failed to connect to MQTT broker. Result: {result}")
                return False
                
            # Wait for connection
            time.sleep(1)
            
            # Create faculty response message
            response_data = {
                "faculty_id": self.faculty_id,
                "faculty_name": "Test Faculty",
                "response_type": response_type,
                "message_id": str(self.test_consultation_id),
                "timestamp": str(int(time.time() * 1000)),
                "faculty_present": True,
                "response_method": "physical_button",
                "status": f"Test {response_type.lower()} response"
            }
            
            topic = f"consultease/faculty/{self.faculty_id}/responses"
            message = json.dumps(response_data)
            
            logger.info(f"📤 Publishing to topic: {topic}")
            logger.info(f"📤 Message: {message}")
            
            # Publish the response
            result = self.client.publish(topic, message, qos=2)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"✅ {response_type} response published successfully")
                logger.info(f"   Message ID: {result.mid}")
                return True
            else:
                logger.error(f"❌ Failed to publish response. Error code: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending faculty response: {e}")
            return False
        finally:
            self.client.disconnect()
            
    def wait_for_processing(self, timeout=10):
        """Wait for the response to be processed."""
        logger.info("=" * 60)
        logger.info("STEP 4: WAITING FOR RESPONSE PROCESSING")
        logger.info("=" * 60)
        
        logger.info(f"⏳ Waiting {timeout} seconds for response processing...")
        time.sleep(timeout)
        
    def verify_status_update(self, expected_status=ConsultationStatus.ACCEPTED):
        """Verify that the consultation status was updated."""
        logger.info("=" * 60)
        logger.info("STEP 5: VERIFYING STATUS UPDATE")
        logger.info("=" * 60)
        
        try:
            db = get_db()
            consultation = db.query(Consultation).filter(Consultation.id == self.test_consultation_id).first()
            
            if consultation:
                self.updated_status = consultation.status
                logger.info(f"📊 Current consultation status:")
                logger.info(f"   ID: {consultation.id}")
                logger.info(f"   Initial Status: {self.initial_status.value}")
                logger.info(f"   Current Status: {consultation.status.value}")
                logger.info(f"   Updated At: {consultation.updated_at}")
                
                if consultation.status == expected_status:
                    logger.info(f"✅ Status successfully updated to {expected_status.value}")
                    return True
                else:
                    logger.error(f"❌ Expected status {expected_status.value}, got {consultation.status.value}")
                    logger.error("❌ CONSULTATION HISTORY UPDATE FAILED!")
                    return False
            else:
                logger.error(f"❌ Consultation {self.test_consultation_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verifying status update: {e}")
            return False
        finally:
            db.close()
            
    def cleanup_test_consultation(self):
        """Clean up the test consultation."""
        logger.info("=" * 60)
        logger.info("STEP 6: CLEANUP")
        logger.info("=" * 60)
        
        try:
            if self.test_consultation_id:
                consultation_controller = ConsultationController()
                # Instead of deleting, just mark as completed
                consultation_controller.update_consultation_status(
                    self.test_consultation_id, 
                    ConsultationStatus.COMPLETED
                )
                logger.info(f"✅ Marked test consultation {self.test_consultation_id} as completed")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            
    def run_full_test(self):
        """Run the complete test flow."""
        logger.info("🚀 STARTING CONSULTATION HISTORY UPDATE TEST")
        logger.info("🚀 " + "=" * 58)
        
        success = True
        
        # Step 1: Create test consultation
        if not self.create_test_consultation():
            logger.error("❌ TEST FAILED: Could not create test consultation")
            return False
            
        # Step 2: Verify initial state
        if not self.verify_initial_consultation():
            logger.error("❌ TEST FAILED: Initial consultation verification failed")
            success = False
            
        # Step 3: Send faculty response
        if success and not self.send_faculty_response():
            logger.error("❌ TEST FAILED: Could not send faculty response")
            success = False
            
        # Step 4: Wait for processing
        if success:
            self.wait_for_processing()
            
        # Step 5: Verify update
        if success and not self.verify_status_update():
            logger.error("❌ TEST FAILED: Status update verification failed")
            success = False
            
        # Step 6: Cleanup
        self.cleanup_test_consultation()
        
        # Final result
        logger.info("=" * 60)
        if success:
            logger.info("✅ CONSULTATION HISTORY UPDATE TEST PASSED")
            logger.info("✅ The consultation history should update correctly")
        else:
            logger.error("❌ CONSULTATION HISTORY UPDATE TEST FAILED")
            logger.error("❌ This explains why the consultation history is not updating")
            
        logger.info("=" * 60)
        
        return success


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test consultation history update flow')
    parser.add_argument('--broker', default=DEFAULT_BROKER, help='MQTT broker host')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='MQTT broker port')
    parser.add_argument('--faculty-id', type=int, default=DEFAULT_FACULTY_ID, help='Faculty ID')
    parser.add_argument('--student-id', type=int, default=DEFAULT_STUDENT_ID, help='Student ID')
    
    args = parser.parse_args()
    
    # Create and run tester
    tester = ConsultationHistoryTester(
        broker_host=args.broker,
        broker_port=args.port,
        faculty_id=args.faculty_id,
        student_id=args.student_id
    )
    
    success = tester.run_full_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 