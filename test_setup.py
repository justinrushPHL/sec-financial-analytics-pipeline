#!/usr/bin/env python3
"""
Test script to verify setup is working
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import requests
        print("✓ requests imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import requests: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pandas: {e}")
        return False
    
    try:
        import sqlite3
        print("✓ sqlite3 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import sqlite3: {e}")
        return False
    
    try:
        import lxml
        print("✓ lxml imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import lxml: {e}")
        return False
    
    return True

def test_directory_structure():
    """Test that required directories exist"""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "src",
        "data",
        "data/raw", 
        "exports",
        "sql",
        "config",
        "notebooks",
        "tests"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} missing")
            all_exist = False
    
    return all_exist

def test_config():
    """Test config loading"""
    print("\nTesting configuration...")
    
    try:
        sys.path.append('.')
        from config.config import SEC_BASE_URL, SEC_HEADERS, INITIAL_TICKERS
        print("✓ Config imported successfully")
        print(f"  - SEC Base URL: {SEC_BASE_URL}")
        print(f"  - Initial tickers: {INITIAL_TICKERS}")
        
        if "your.email@example.com" in SEC_HEADERS["User-Agent"]:
            print("⚠️  WARNING: Please update your email in config/config.py")
        else:
            print("✓ Email appears to be updated in config")
        
        return True
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return False

def main():
    print("SEC Financial Analytics Pipeline - Setup Test")
    print("="*50)
    
    tests = [
        test_imports,
        test_directory_structure, 
        test_config
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    if all(results):
        print("🎉 All tests passed! Setup is ready.")
        print("\nNext steps:")
        print("1. Update your email in config/config.py if you haven't already")
        print("2. Run: python main.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)