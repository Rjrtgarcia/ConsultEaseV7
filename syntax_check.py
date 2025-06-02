#!/usr/bin/env python3
"""
Comprehensive syntax check for ConsultEase central system.
This script checks for Python syntax errors without importing modules.
"""

import os
import py_compile
import sys
from pathlib import Path

def check_syntax(file_path):
    """
    Check syntax of a Python file using py_compile.
    
    Args:
        file_path (str): Path to the Python file
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"

def find_python_files(directory):
    """
    Find all Python files in a directory recursively.
    
    Args:
        directory (str): Directory to search
        
    Returns:
        list: List of Python file paths
    """
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """Run syntax check on all Python files in the central system."""
    print("="*70)
    print("ConsultEase Central System - Comprehensive Syntax Check")
    print("="*70)
    
    # Define directories to check
    directories_to_check = [
        'central_system/models',
        'central_system/controllers', 
        'central_system/views',
        'central_system/services',
        'central_system/utils',
    ]
    
    all_files = []
    for directory in directories_to_check:
        if os.path.exists(directory):
            files = find_python_files(directory)
            all_files.extend(files)
            print(f"Found {len(files)} Python files in {directory}")
        else:
            print(f"⚠️  Directory not found: {directory}")
    
    print(f"\nTotal Python files to check: {len(all_files)}")
    print("-" * 70)
    
    passed = 0
    failed = 0
    errors = []
    
    for file_path in sorted(all_files):
        # Get relative path for cleaner output
        rel_path = os.path.relpath(file_path)
        
        success, error = check_syntax(file_path)
        
        if success:
            print(f"✅ {rel_path}")
            passed += 1
        else:
            print(f"❌ {rel_path}")
            print(f"   Error: {error}")
            failed += 1
            errors.append((rel_path, error))
    
    print("="*70)
    print(f"Syntax Check Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All files passed syntax check!")
        print("✅ No syntax errors found in the central system.")
    else:
        print(f"⚠️  {failed} files have syntax errors:")
        print()
        for file_path, error in errors:
            print(f"❌ {file_path}")
            print(f"   {error}")
            print()
    
    print("="*70)
    
    # Also check some key files that might not be in the standard directories
    additional_files = [
        'test_imports.py',
        'syntax_check.py'
    ]
    
    print("Checking additional files:")
    for file_path in additional_files:
        if os.path.exists(file_path):
            success, error = check_syntax(file_path)
            if success:
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path}: {error}")
                failed += 1
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 