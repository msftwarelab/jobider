"""
Quick test script to verify installation
Run this after setup to check everything is working
"""

import sys
import os

def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")
    try:
        import selenium
        import sqlalchemy
        import yaml
        import bs4
        import requests
        import apscheduler
        import colorlog
        from dotenv import load_dotenv
        print("✓ All packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    try:
        from src.database import Database
        db = Database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from src.utils import load_config
        config = load_config()
        print(f"✓ Configuration loaded successfully")
        print(f"  Keywords: {config['search_criteria']['keywords'][:2]}...")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_env():
    """Test environment variables"""
    print("\nTesting environment...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        dice_email = os.getenv('DICE_EMAIL')
        dice_password = os.getenv('DICE_PASSWORD')
        
        if dice_email and dice_password:
            if 'example.com' in dice_email:
                print("⚠ Warning: Using example credentials - update .env file")
                return False
            print("✓ Environment variables configured")
            return True
        else:
            print("✗ Missing DICE credentials in .env")
            return False
    except Exception as e:
        print(f"✗ Environment error: {e}")
        return False

def test_directories():
    """Test required directories exist"""
    print("\nTesting directories...")
    dirs = ['logs', 'resumes', 'templates']
    all_exist = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ missing")
            all_exist = False
    
    return all_exist

def test_resume():
    """Test resume file exists"""
    print("\nTesting resume...")
    resume_path = 'resumes/resume.pdf'
    if os.path.exists(resume_path):
        size = os.path.getsize(resume_path)
        print(f"✓ Resume found ({size} bytes)")
        return True
    else:
        print(f"⚠ Resume not found at {resume_path}")
        print("  Add your resume: cp /path/to/resume.pdf resumes/resume.pdf")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("JobBider Installation Test")
    print("="*60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Configuration", test_config()))
    results.append(("Environment", test_env()))
    results.append(("Directories", test_directories()))
    results.append(("Resume", test_resume()))
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20} {status}")
    
    print("="*60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run:")
        print("   python main.py --search-only")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("   Check INSTALL.md for troubleshooting steps.")
    
    print("="*60)

if __name__ == "__main__":
    main()
