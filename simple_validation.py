#!/usr/bin/env python3
"""
Simple validation script for ConsultEase performance fixes.
This script checks if the code changes were properly applied without requiring GUI.
"""

import os
import sys
import re

def check_file_exists(filepath):
    """Check if a file exists and return its status."""
    if os.path.exists(filepath):
        print(f"✅ Found: {filepath}")
        return True
    else:
        print(f"❌ Missing: {filepath}")
        return False

def check_code_pattern(filepath, pattern, description):
    """Check if a specific code pattern exists in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(pattern, content):
                print(f"✅ {description}: Found in {filepath}")
                return True
            else:
                print(f"❌ {description}: Not found in {filepath}")
                return False
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

def main():
    """Run simple validation checks."""
    print("🔍 ConsultEase Performance Fix Validation")
    print("=" * 50)
    
    # Check if core files exist
    print("\n📁 File Existence Check:")
    files_exist = []
    files_exist.append(check_file_exists("central_system/views/dashboard_window.py"))
    files_exist.append(check_file_exists("central_system/views/login_window.py"))
    files_exist.append(check_file_exists("central_system/views/consultation_panel.py"))
    
    if not all(files_exist):
        print("\n❌ Some core files are missing. Please ensure all files are in place.")
        return False
    
    # Check dashboard optimizations
    print("\n⚡ Dashboard Optimization Checks:")
    dashboard_checks = []
    dashboard_checks.append(check_code_pattern(
        "central_system/views/dashboard_window.py",
        r"_consecutive_no_changes",
        "Adaptive refresh tracking"
    ))
    dashboard_checks.append(check_code_pattern(
        "central_system/views/dashboard_window.py",
        r"_debounced_refresh",
        "Debounced refresh method"
    ))
    dashboard_checks.append(check_code_pattern(
        "central_system/views/dashboard_window.py",
        r"300000",
        "5-minute refresh timer"
    ))
    dashboard_checks.append(check_code_pattern(
        "central_system/views/dashboard_window.py",
        r"hashlib\.md5",
        "MD5 hash change detection"
    ))
    
    # Check login optimizations
    print("\n🚀 Login Performance Checks:")
    login_checks = []
    login_checks.append(check_code_pattern(
        "central_system/views/login_window.py",
        r"_last_rfid_refresh",
        "RFID refresh caching"
    ))
    login_checks.append(check_code_pattern(
        "central_system/views/login_window.py",
        r"30.*second",
        "30-second minimum interval"
    ))
    
    # Check button alignment fixes
    print("\n🎨 Button Alignment Checks:")
    button_checks = []
    button_checks.append(check_code_pattern(
        "central_system/views/consultation_panel.py",
        r"Qt\.AlignCenter",
        "Button center alignment"
    ))
    button_checks.append(check_code_pattern(
        "central_system/views/consultation_panel.py",
        r"60.*32|70.*32",
        "Standardized button sizes"
    ))
    
    # Check MQTT improvements
    print("\n📡 MQTT Real-time Update Checks:")
    mqtt_checks = []
    mqtt_checks.append(check_code_pattern(
        "central_system/views/consultation_panel.py",
        r"on_mqtt_disconnect",
        "MQTT disconnect handling"
    ))
    mqtt_checks.append(check_code_pattern(
        "central_system/views/consultation_panel.py",
        r"120000",
        "2-minute consultation refresh"
    ))
    mqtt_checks.append(check_code_pattern(
        "central_system/views/consultation_panel.py",
        r"_handle_consultation_update",
        "Consultation update handler"
    ))
    
    # Summary
    print("\n📊 Validation Summary:")
    print("-" * 30)
    
    all_checks = [
        ("Dashboard Optimization", dashboard_checks),
        ("Login Performance", login_checks),
        ("Button Alignment", button_checks),
        ("MQTT Real-time Updates", mqtt_checks)
    ]
    
    overall_success = True
    for category, checks in all_checks:
        success_rate = sum(checks) / len(checks) * 100
        status = "✅" if success_rate >= 75 else "⚠️" if success_rate >= 50 else "❌"
        print(f"{status} {category}: {success_rate:.0f}% ({sum(checks)}/{len(checks)} checks passed)")
        if success_rate < 75:
            overall_success = False
    
    print(f"\n🎯 Overall Status: {'✅ SUCCESS' if overall_success else '❌ NEEDS ATTENTION'}")
    
    if overall_success:
        print("\n🎉 All performance fixes have been successfully applied!")
        print("📋 Next steps:")
        print("   1. Deploy to Raspberry Pi")
        print("   2. Install dependencies: pip3 install -r requirements.txt")
        print("   3. Test with actual hardware")
        print("   4. Monitor performance for 24 hours")
    else:
        print("\n⚠️  Some fixes may not be properly applied.")
        print("📋 Recommended actions:")
        print("   1. Review the failed checks above")
        print("   2. Re-apply the specific fixes that failed")
        print("   3. Run this validation again")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 