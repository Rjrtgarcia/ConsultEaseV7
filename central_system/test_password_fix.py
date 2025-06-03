#!/usr/bin/env python3
"""
Test script to verify password change dialog fixes.
This script tests the admin authentication and password change logic.
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from central_system.models.base import init_db, get_db
from central_system.models.admin import Admin
from central_system.controllers.admin_controller import AdminController

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_admin_password_logic():
    """Test the admin password change logic."""
    
    print("🧪 Testing Admin Password Change Logic")
    print("="*50)
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        init_db(force_recreate=True)
        
        # Create admin controller
        admin_controller = AdminController()
        
        # Test 1: Create admin account
        print("\n1️⃣ Creating admin account...")
        result = admin_controller.create_admin_account("testadmin", "TempPass123!", force_password_change=True)
        
        if result['success']:
            print(f"✅ Admin account created: {result['admin']['username']}")
        else:
            print(f"❌ Failed to create admin: {result['error']}")
            return False
            
        # Test 2: First authentication (should require password change)
        print("\n2️⃣ Testing first authentication (should require password change)...")
        auth_result = admin_controller.authenticate("testadmin", "TempPass123!")
        
        if auth_result and auth_result.get('requires_password_change'):
            print("✅ Correctly requires password change on first login")
        else:
            print("❌ Should require password change but doesn't")
            return False
            
        # Test 3: Change password
        print("\n3️⃣ Changing password...")
        admin_id = auth_result['admin'].id
        success, errors = admin_controller.change_password(admin_id, "TempPass123!", "NewSecurePass123!")
        
        if success:
            print("✅ Password changed successfully")
        else:
            print(f"❌ Password change failed: {errors}")
            return False
            
        # Test 4: Second authentication (should NOT require password change)
        print("\n4️⃣ Testing second authentication (should NOT require password change)...")
        auth_result2 = admin_controller.authenticate("testadmin", "NewSecurePass123!")
        
        if auth_result2 and not auth_result2.get('requires_password_change'):
            print("✅ Correctly does NOT require password change after successful change")
        else:
            print("❌ Incorrectly still requires password change after successful change")
            print(f"Auth result: {auth_result2}")
            return False
            
        # Test 5: Check admin object state
        print("\n5️⃣ Checking admin object state...")
        db = get_db()
        admin = db.query(Admin).filter(Admin.username == "testadmin").first()
        
        if admin and not admin.force_password_change:
            print("✅ Admin force_password_change flag is correctly False")
        else:
            print(f"❌ Admin force_password_change flag is still True: {admin.force_password_change if admin else 'Admin not found'}")
            return False
            
        if admin and admin.last_password_change:
            print("✅ Admin last_password_change is set")
        else:
            print("❌ Admin last_password_change is not set")
            return False
            
        db.close()
        
        print("\n🎉 All tests passed! Password change logic is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        logger.exception("Test failed")
        return False

if __name__ == "__main__":
    success = test_admin_password_logic()
    if success:
        print("\n✅ Password change dialog fix verification PASSED")
        sys.exit(0)
    else:
        print("\n❌ Password change dialog fix verification FAILED")
        sys.exit(1) 