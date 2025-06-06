"""
MQTT test publisher for testing real-time faculty status updates.
This utility can be used to manually test if the real-time update system is working.
"""

import json
import time
import logging
from .mqtt_utils import publish_faculty_status, publish_mqtt_message

logger = logging.getLogger(__name__)


class MQTTTestPublisher:
    """Test publisher for simulating faculty status changes."""
    
    def __init__(self):
        self.faculty_ids = [1, 2, 3, 4, 5]  # Test with faculty IDs 1-5
        self.statuses = ["available", "busy", "offline"]
        
    def test_faculty_status_update(self, faculty_id: int, status: str):
        """
        Test publishing a faculty status update.
        
        Args:
            faculty_id: Faculty ID to update
            status: New status (available, busy, offline)
        """
        logger.info(f"🧪 Testing faculty status update: Faculty {faculty_id} -> {status}")
        
        # Test different payload formats
        test_formats = [
            # Format 1: Dictionary with 'present' and 'status' fields (desk unit format)
            {
                "present": status != "offline",
                "status": status,
                "timestamp": time.time(),
                "desk_id": faculty_id
            },
            
            # Format 2: Simple string status
            status,
            
            # Format 3: Dictionary with direct status
            {
                "status": status,
                "faculty_id": faculty_id,
                "timestamp": time.time()
            }
        ]
        
        success_count = 0
        for i, payload in enumerate(test_formats):
            topic = f"consultease/faculty/{faculty_id}/status"
            logger.info(f"  🔄 Test {i+1}: Publishing to {topic} with payload: {payload}")
            
            if publish_mqtt_message(topic, payload):
                success_count += 1
                logger.info(f"  ✅ Test {i+1}: Success")
            else:
                logger.error(f"  ❌ Test {i+1}: Failed")
            
            # Wait between tests
            time.sleep(0.5)
        
        logger.info(f"🧪 Test completed: {success_count}/{len(test_formats)} successful")
        return success_count == len(test_formats)
    
    def test_all_faculty_status_cycle(self):
        """Test cycling through all faculty and all statuses."""
        logger.info("🧪 Starting comprehensive faculty status test cycle")
        
        results = []
        for faculty_id in self.faculty_ids:
            for status in self.statuses:
                result = self.test_faculty_status_update(faculty_id, status)
                results.append(result)
                time.sleep(1)  # Wait between each test
        
        successful_tests = sum(results)
        total_tests = len(results)
        
        logger.info(f"🧪 Test cycle completed: {successful_tests}/{total_tests} tests successful")
        return successful_tests == total_tests
    
    def test_rapid_status_changes(self, faculty_id: int = 1, count: int = 10):
        """Test rapid status changes for a single faculty member."""
        logger.info(f"🧪 Testing rapid status changes for Faculty {faculty_id}")
        
        import random
        success_count = 0
        
        for i in range(count):
            status = random.choice(self.statuses)
            topic = f"consultease/faculty/{faculty_id}/status"
            
            payload = {
                "present": status != "offline",
                "status": status,
                "timestamp": time.time(),
                "test_sequence": i
            }
            
            if publish_mqtt_message(topic, payload):
                success_count += 1
                logger.debug(f"  ✅ Rapid test {i+1}: Faculty {faculty_id} -> {status}")
            else:
                logger.error(f"  ❌ Rapid test {i+1}: Failed")
            
            time.sleep(0.1)  # Very short delay
        
        logger.info(f"🧪 Rapid test completed: {success_count}/{count} successful")
        return success_count == count
    
    def test_system_notification(self, message: str = "Test system notification"):
        """Test publishing a system notification."""
        logger.info(f"🧪 Testing system notification: {message}")
        
        payload = {
            "type": "test_notification",
            "message": message,
            "level": "info",
            "timestamp": time.time()
        }
        
        topic = "consultease/system/notifications"
        success = publish_mqtt_message(topic, payload)
        
        if success:
            logger.info("✅ System notification test successful")
        else:
            logger.error("❌ System notification test failed")
        
        return success
    
    def test_faculty_status_change_notification(self, faculty_id: int, new_status: str):
        """Test publishing a faculty status change system notification."""
        logger.info(f"🧪 Testing faculty status change notification: Faculty {faculty_id} -> {new_status}")
        
        payload = {
            "type": "faculty_status_changed",
            "message": f"Faculty {faculty_id} status changed to {new_status}",
            "level": "info",
            "faculty_id": faculty_id,
            "new_status": new_status,
            "timestamp": time.time()
        }
        
        topic = "consultease/system/notifications"
        success = publish_mqtt_message(topic, payload)
        
        if success:
            logger.info("✅ Faculty status change notification test successful")
        else:
            logger.error("❌ Faculty status change notification test failed")
        
        return success


# Convenience functions for quick testing
def quick_test_faculty_available(faculty_id: int = 1):
    """Quick test to make a faculty available."""
    publisher = MQTTTestPublisher()
    return publisher.test_faculty_status_update(faculty_id, "available")


def quick_test_faculty_busy(faculty_id: int = 1):
    """Quick test to make a faculty busy."""
    publisher = MQTTTestPublisher()
    return publisher.test_faculty_status_update(faculty_id, "busy")


def quick_test_faculty_offline(faculty_id: int = 1):
    """Quick test to make a faculty offline."""
    publisher = MQTTTestPublisher()
    return publisher.test_faculty_status_update(faculty_id, "offline")


def run_comprehensive_test():
    """Run a comprehensive test of all MQTT functionality."""
    logger.info("🚀 Starting comprehensive MQTT test suite")
    
    publisher = MQTTTestPublisher()
    
    # Test system notification
    test1 = publisher.test_system_notification("Comprehensive MQTT test started")
    
    # Test individual faculty updates
    test2 = publisher.test_faculty_status_update(1, "available")
    test3 = publisher.test_faculty_status_update(2, "busy")
    test4 = publisher.test_faculty_status_update(3, "offline")
    
    # Test system notification for faculty status change
    test5 = publisher.test_faculty_status_change_notification(1, "available")
    
    # Test rapid changes
    test6 = publisher.test_rapid_status_changes(1, 5)
    
    all_tests = [test1, test2, test3, test4, test5, test6]
    successful_tests = sum(all_tests)
    
    logger.info(f"🏁 Comprehensive test completed: {successful_tests}/{len(all_tests)} tests successful")
    
    # Final system notification
    publisher.test_system_notification(f"Comprehensive MQTT test completed: {successful_tests}/{len(all_tests)} successful")
    
    return successful_tests == len(all_tests)


if __name__ == "__main__":
    # Setup logging for standalone execution
    logging.basicConfig(level=logging.INFO)
    
    # Run comprehensive test
    success = run_comprehensive_test()
    print(f"Test result: {'SUCCESS' if success else 'FAILURE'}") 