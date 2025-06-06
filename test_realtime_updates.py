#!/usr/bin/env python3
"""
Standalone test script for MQTT real-time updates.
Run this while the application is running to test if real-time updates work.
"""

import sys
import os
import time
import logging

# Add the central_system to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'central_system'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mqtt_realtime_updates():
    """Test MQTT real-time updates."""
    try:
        logger.info("🚀 Starting MQTT real-time update test")
        
        # Import the MQTT utilities
        from central_system.utils.mqtt_utils import publish_faculty_status, is_mqtt_connected
        from central_system.utils.mqtt_test_publisher import MQTTTestPublisher
        
        # Check if MQTT is connected
        if not is_mqtt_connected():
            logger.error("❌ MQTT service is not connected. Start the main application first.")
            return False
        
        logger.info("✅ MQTT service is connected")
        
        # Create test publisher
        publisher = MQTTTestPublisher()
        
        logger.info("🧪 Testing faculty status updates...")
        
        # Test sequence: Faculty 1 through different states
        test_sequence = [
            (1, "available"),
            (2, "busy"), 
            (3, "offline"),
            (1, "busy"),
            (2, "available"),
            (3, "available"),
            (1, "offline")
        ]
        
        for faculty_id, status in test_sequence:
            logger.info(f"🔄 Setting Faculty {faculty_id} to {status}")
            
            # Use the utility function to publish
            success = publish_faculty_status(faculty_id, status)
            
            if success:
                logger.info(f"✅ Successfully published Faculty {faculty_id} -> {status}")
            else:
                logger.error(f"❌ Failed to publish Faculty {faculty_id} -> {status}")
            
            # Wait between updates
            time.sleep(2)
        
        # Test system notification
        logger.info("🔔 Testing system notification...")
        success = publisher.test_system_notification("Real-time update test completed!")
        
        if success:
            logger.info("✅ System notification test successful")
        else:
            logger.error("❌ System notification test failed")
        
        logger.info("🏁 MQTT real-time update test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during MQTT test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🧪 ConsultEase MQTT Real-time Update Test")
    print("=" * 60)
    print()
    print("This script tests if MQTT real-time updates are working.")
    print("Make sure the main ConsultEase application is running first.")
    print()
    
    input("Press Enter to start the test...")
    
    success = test_mqtt_realtime_updates()
    
    print()
    print("=" * 60)
    if success:
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("Check the main application to see if faculty cards updated.")
    else:
        print("❌ TEST FAILED")
        print("Check the logs for details.")
    print("=" * 60)

if __name__ == "__main__":
    main() 