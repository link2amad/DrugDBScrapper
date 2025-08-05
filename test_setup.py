#!/usr/bin/env python3
"""
Test script to verify the scraper setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import requests
        print("✓ requests imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import requests: {e}")
        return False
    
    try:
        import pyodbc
        print("✓ pyodbc imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pyodbc: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import BeautifulSoup: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ PIL imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PIL: {e}")
        return False
    
    try:
        from fake_useragent import UserAgent
        print("✓ fake_useragent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import fake_useragent: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import python-dotenv: {e}")
        return False
    
    return True

def test_project_imports():
    """Test if project modules can be imported"""
    print("\nTesting project imports...")
    
    try:
        from scraper import DawaaiScraper, DatabaseHandler, ImageDownloader
        print("✓ Project modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import project modules: {e}")
        return False
    
    return True

def test_directory_structure():
    """Test if required directories exist or can be created"""
    print("\nTesting directory structure...")
    
    directories = ['data/images', 'logs']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Directory '{directory}' ready")
        except Exception as e:
            print(f"✗ Failed to create directory '{directory}': {e}")
            return False
    
    return True

def test_environment_file():
    """Test if environment file exists"""
    print("\nTesting environment configuration...")
    
    if os.path.exists('.env'):
        print("✓ .env file found")
        return True
    else:
        print("⚠ .env file not found")
        print("  Please copy env.example to .env and configure your database settings")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("PAKISTAN MEDICAL INDUSTRY DRUG DATABASE SCRAPER")
    print("SETUP VERIFICATION")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test project imports
    if not test_project_imports():
        all_tests_passed = False
    
    # Test directory structure
    if not test_directory_structure():
        all_tests_passed = False
    
    # Test environment file
    if not test_environment_file():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✓ ALL TESTS PASSED")
        print("The scraper is ready to use!")
        print("\nNext steps:")
        print("1. Configure your database settings in .env file")
        print("2. Test database connection: python main.py --test-db")
        print("3. Start scraping: python main.py --scrape-letter a")
    else:
        print("✗ SOME TESTS FAILED")
        print("Please fix the issues above before proceeding")
    print("=" * 50)
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 