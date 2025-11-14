#!/usr/bin/env python3
"""
Setup Verification Script
Checks if all requirements for the appointment scraper are met.
"""

import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.8+"""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (need 3.8+)")
        return False

def check_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print("\nChecking Python packages...")
    packages = {
        'selenium': 'selenium',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl',
        'webdriver_manager': 'webdriver-manager',
        'requests': 'requests'
    }
    
    all_installed = True
    for import_name, package_name in packages.items():
        status = "✓" if check_package(import_name) else "✗"
        print(f"  {status} {package_name}")
        if status == "✗":
            all_installed = False
    
    return all_installed

def check_chrome():
    """Check if Chrome/Chromium is installed"""
    print("\nChecking Chrome/Chromium installation...", end=" ")
    browsers = ['google-chrome', 'chromium', 'chromium-browser']
    
    for browser in browsers:
        result = subprocess.run(['which', browser], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Found {browser}")
            return True
    
    print("✗ Chrome/Chromium not found")
    return False

def main():
    print("="*60)
    print("Appointment Scraper - Setup Verification")
    print("="*60)
    
    checks = []
    
    # Run checks
    checks.append(("Python version", check_python_version()))
    checks.append(("Python packages", check_dependencies()))
    checks.append(("Chrome browser", check_chrome()))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = all(result for _, result in checks)
    
    for name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    if all_passed:
        print("\n✓ All checks passed! You're ready to run the scraper.")
        print("\nNext steps:")
        print("  1. Test mode: python appointment_scraper.py --test")
        print("  2. Live scraping: python appointment_scraper.py")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nTo fix missing packages:")
        print("  pip install -r requirements.txt")
        print("\nTo install Chrome (Ubuntu/Debian):")
        print("  sudo apt-get install chromium-browser")
    
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
