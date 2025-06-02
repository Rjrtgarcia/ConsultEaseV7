#!/usr/bin/env python3
"""
Test script to check for import errors in the ConsultEase central system.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_imports():
    """Test importing core modules."""
    print("="*60)
    print("ConsultEase Central System - Import Check")
    print("="*60)
    
    tests = [
        ("models/consultation", "from central_system.models.consultation import Consultation, ConsultationStatus"),
        ("models/base", "from central_system.models.base import get_db, init_db"),
        ("utils/theme", "from central_system.utils.theme import ConsultEaseTheme"),
        ("controllers/consultation", "from central_system.controllers.consultation_controller import ConsultationController"),
        ("controllers/faculty_response", "from central_system.controllers.faculty_response_controller import FacultyResponseController"),
        ("views/consultation_panel", "from central_system.views.consultation_panel import ConsultationPanel"),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name} - OK")
            passed += 1
        except Exception as e:
            print(f"❌ {name} - ERROR: {e}")
    
    print("="*60)
    print(f"Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All imports successful!")
    else:
        print("⚠️  Some imports failed.")
    
    return passed == total

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 