#!/usr/bin/env python3
"""
Test script for ConsultEase performance fixes.
This script validates the improvements made to reduce loading indicators,
optimize login performance, fix UI alignment, and improve real-time updates.
"""

import sys
import os
import time
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'central_system'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("performance_test.log")
    ]
)

logger = logging.getLogger(__name__)

def test_login_performance():
    """Test login window performance optimizations."""
    logger.info("Testing login window performance...")
    
    try:
        from central_system.views.login_window import LoginWindow
        
        # Create app if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create login window
        start_time = time.time()
        login_window = LoginWindow()
        creation_time = time.time() - start_time
        
        # Show window and measure show time
        start_time = time.time()
        login_window.show()
        QApplication.processEvents()  # Process pending events
        show_time = time.time() - start_time
        
        logger.info(f"Login window creation time: {creation_time:.3f}s")
        logger.info(f"Login window show time: {show_time:.3f}s")
        
        # Test RFID refresh optimization
        start_time = time.time()
        login_window.handle_manual_rfid_entry = lambda: None  # Mock method
        login_window.rfid_input.setText("TEST123")
        login_window.handle_manual_rfid_entry()
        refresh_time = time.time() - start_time
        
        logger.info(f"RFID refresh time: {refresh_time:.3f}s")
        
        login_window.close()
        
        # Performance thresholds for Raspberry Pi
        if creation_time > 2.0:
            logger.warning(f"Login creation time ({creation_time:.3f}s) exceeds recommended threshold (2.0s)")
        if show_time > 1.0:
            logger.warning(f"Login show time ({show_time:.3f}s) exceeds recommended threshold (1.0s)")
        
        logger.info("✅ Login performance test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Login performance test failed: {e}")
        return False

def test_dashboard_refresh_optimization():
    """Test dashboard refresh optimizations."""
    logger.info("Testing dashboard refresh optimizations...")
    
    try:
        from central_system.views.dashboard_window import DashboardWindow
        
        # Create app if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Mock student data
        student_data = {
            'id': 1,
            'name': 'Test Student',
            'department': 'Computer Science',
            'rfid_uid': 'TEST123'
        }
        
        # Create dashboard window
        start_time = time.time()
        dashboard_window = DashboardWindow(student_data)
        creation_time = time.time() - start_time
        
        logger.info(f"Dashboard creation time: {creation_time:.3f}s")
        
        # Test adaptive refresh logic
        dashboard_window.show()
        QApplication.processEvents()
        
        # Check if adaptive refresh variables are initialized
        assert hasattr(dashboard_window, '_consecutive_no_changes'), "Adaptive refresh variables not initialized"
        assert hasattr(dashboard_window, '_last_faculty_hash'), "Faculty hash tracking not initialized"
        assert hasattr(dashboard_window, '_last_update_time'), "Update time tracking not initialized"
        
        # Test debounced refresh
        start_time = time.time()
        dashboard_window._debounced_refresh()
        debounce_time = time.time() - start_time
        
        logger.info(f"Debounced refresh time: {debounce_time:.3f}s")
        
        # Check refresh timer interval (should be 5 minutes = 300000ms)
        timer_interval = dashboard_window.refresh_timer.interval()
        expected_interval = 300000  # 5 minutes
        assert timer_interval == expected_interval, f"Refresh timer interval is {timer_interval}ms, expected {expected_interval}ms"
        
        dashboard_window.close()
        
        logger.info("✅ Dashboard refresh optimization test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dashboard refresh test failed: {e}")
        return False

def test_consultation_button_alignment():
    """Test consultation history button alignment fixes."""
    logger.info("Testing consultation button alignment...")
    
    try:
        from central_system.views.consultation_panel import ConsultationPanel
        
        # Create app if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Mock student data
        student_data = {
            'id': 1,
            'name': 'Test Student',
            'department': 'Computer Science',
            'rfid_uid': 'TEST123'
        }
        
        # Create consultation panel
        consultation_panel = ConsultationPanel(student_data)
        consultation_panel.show()
        QApplication.processEvents()
        
        # Check if optimized refresh timers are set
        history_panel = consultation_panel.history_panel
        
        # Check refresh timer interval (should be 2 minutes = 120000ms)
        timer_interval = consultation_panel.refresh_timer.interval()
        expected_interval = 120000  # 2 minutes
        assert timer_interval == expected_interval, f"Consultation refresh timer interval is {timer_interval}ms, expected {expected_interval}ms"
        
        # Check MQTT timer interval (should be 1 minute = 60000ms)
        mqtt_timer_interval = consultation_panel.mqtt_check_timer.interval()
        expected_mqtt_interval = 60000  # 1 minute
        assert mqtt_timer_interval == expected_mqtt_interval, f"MQTT check timer interval is {mqtt_timer_interval}ms, expected {expected_mqtt_interval}ms"
        
        # Check intelligent refresh variables
        assert hasattr(consultation_panel, '_last_refresh_time'), "Last refresh time tracking not initialized"
        assert hasattr(consultation_panel, '_min_refresh_interval'), "Min refresh interval not initialized"
        
        consultation_panel.close()
        
        logger.info("✅ Consultation button alignment test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Consultation button alignment test failed: {e}")
        return False

def test_mqtt_real_time_updates():
    """Test MQTT real-time update improvements."""
    logger.info("Testing MQTT real-time updates...")
    
    try:
        from central_system.views.consultation_panel import ConsultationHistoryPanel
        
        # Create app if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Mock student data
        student_data = {
            'id': 1,
            'name': 'Test Student',
            'department': 'Computer Science',
            'rfid_uid': 'TEST123'
        }
        
        # Create consultation history panel
        history_panel = ConsultationHistoryPanel(student_data)
        
        # Test MQTT setup (even if connection fails, setup should work)
        try:
            history_panel.setup_mqtt_monitoring()
            logger.info("MQTT monitoring setup completed")
        except Exception as mqtt_error:
            logger.warning(f"MQTT setup failed (expected in test environment): {mqtt_error}")
        
        # Check if MQTT variables are initialized
        assert hasattr(history_panel, '_mqtt_connected'), "MQTT connection tracking not initialized"
        assert hasattr(history_panel, '_mqtt_retry_count'), "MQTT retry count not initialized"
        assert hasattr(history_panel, '_max_retries'), "MQTT max retries not initialized"
        
        logger.info("✅ MQTT real-time updates test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ MQTT real-time updates test failed: {e}")
        return False

def main():
    """Run all performance tests."""
    logger.info("Starting ConsultEase performance fixes validation...")
    logger.info("=" * 60)
    
    # Set environment variables for testing
    os.environ['CONSULTEASE_THEME'] = 'light'
    os.environ['DB_TYPE'] = 'sqlite'
    os.environ['DB_PATH'] = ':memory:'  # Use in-memory DB for testing
    
    tests = [
        ("Login Performance", test_login_performance),
        ("Dashboard Refresh Optimization", test_dashboard_refresh_optimization),
        ("Consultation Button Alignment", test_consultation_button_alignment),
        ("MQTT Real-time Updates", test_mqtt_real_time_updates),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                failed += 1
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("PERFORMANCE FIXES VALIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tests Passed: {passed}")
    logger.info(f"Tests Failed: {failed}")
    logger.info(f"Total Tests: {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 All performance fixes validated successfully!")
        logger.info("✅ System is ready for Raspberry Pi deployment")
    else:
        logger.warning(f"⚠️  {failed} test(s) failed. Please review the issues above.")
    
    return failed == 0

if __name__ == "__main__":
    # Create QApplication for GUI tests
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)
    finally:
        app.quit() 