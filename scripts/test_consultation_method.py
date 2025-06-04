#!/usr/bin/env python3
"""
Quick test to verify the consultation controller get_consultations method works.
"""

import sys
import os

# Add the central_system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'central_system'))

try:
    from controllers.consultation_controller import ConsultationController
    from models.base import init_db
    
    print("🔧 Testing ConsultationController...")
    
    # Initialize database
    init_db()
    
    # Create controller
    controller = ConsultationController()
    
    # Test the method with a sample student ID
    print("📊 Testing get_consultations method...")
    consultations = controller.get_consultations(student_id=1)
    
    print(f"✅ Method call successful! Found {len(consultations)} consultations for student 1")
    
    # List all available methods
    print("\n📋 Available methods in ConsultationController:")
    methods = [method for method in dir(controller) if not method.startswith('_')]
    for method in methods:
        print(f"   - {method}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 