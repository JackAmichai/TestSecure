"""
Test script to verify all components are working correctly.
Run this before starting experiments to ensure everything is set up properly.
"""

import os
import sys
import json
import requests
import time

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from config import GROUP_SEED, HASH_MODE, PEPPER
        import bcrypt
        from argon2 import PasswordHasher
        import pyotp
        import flask
        print(f"✓ All imports successful")
        print(f"  GROUP_SEED: {GROUP_SEED}")
        print(f"  HASH_MODE: {HASH_MODE}")
        print(f"  PEPPER: {'Set' if PEPPER else 'Not set (OK for testing)'}")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_user_generation():
    """Test user generation"""
    print("\nTesting user generation...")
    try:
        from generate_users import generate_users
        from config import GROUP_SEED
        
        generate_users()
        
        # Check if file exists
        if not os.path.exists("data/users.json"):
            print("✗ users.json not created")
            return False
        
        # Load and verify
        with open("data/users.json", "r") as f:
            users = json.load(f)
        
        if len(users) != 30:
            print(f"✗ Expected 30 users, got {len(users)}")
            return False
        
        # Check if GROUP_SEED is first password
        # We can't directly check the password, but we can check the username
        if users[0]["username"] != "weak_user_01":
            print("✗ First user should be weak_user_01")
            return False
        
        print(f"✓ Generated 30 users successfully")
        print(f"  weak_user_01 password is GROUP_SEED ({GROUP_SEED})")
        return True
        
    except Exception as e:
        print(f"✗ User generation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server_endpoints():
    """Test that server endpoints are accessible"""
    print("\nTesting server endpoints...")
    print("Note: Server must be running for this test!")
    print("Start server in another terminal with: python app.py")
    
    time.sleep(2)
    
    try:
        # Test health endpoint
        resp = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if resp.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"✗ Health endpoint returned {resp.status_code}")
            return False
        
        # Test login endpoint with wrong password
        resp = requests.post(
            "http://127.0.0.1:5000/login",
            json={"username": "weak_user_01", "password": "wrongpassword"},
            timeout=5
        )
        if resp.status_code == 401:
            print("✓ Login endpoint working (correctly rejected bad password)")
        else:
            print(f"✗ Login endpoint unexpected response: {resp.status_code}")
            return False
        
        # Test admin CAPTCHA endpoint
        from config import GROUP_SEED
        resp = requests.get(
            f"http://127.0.0.1:5000/admin/get_captcha_token?group_seed={GROUP_SEED}&username=test",
            timeout=5
        )
        if resp.status_code == 200:
            print("✓ CAPTCHA admin endpoint working")
        else:
            print(f"✗ CAPTCHA endpoint returned {resp.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server")
        print("  Please start server: python app.py")
        return False
    except Exception as e:
        print(f"✗ Server test error: {e}")
        return False


def test_configurations():
    """Test configuration profiles"""
    print("\nTesting configuration profiles...")
    try:
        from config_profiles import CONFIGS
        
        expected_profiles = [
            "sha256_open", "sha256_lockout_rate", "sha256_full",
            "bcrypt_open", "bcrypt_lockout_rate", "bcrypt_full",
            "argon2_open", "argon2_lockout_rate", "argon2_full"
        ]
        
        for profile in expected_profiles:
            if profile not in CONFIGS:
                print(f"✗ Missing profile: {profile}")
                return False
        
        print(f"✓ All {len(expected_profiles)} configuration profiles present")
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "app.py",
        "config.py",
        "config_profiles.py",
        "generate_users.py",
        "attack_bruteforce.py",
        "attack_spray.py",
        "attack_bruteforce_enhanced.py",
        "attack_spray_enhanced.py",
        "analyze_logs.py",
        "analyze_logs_enhanced.py",
        "run_all_experiments.py",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md",
        "ETHICS.md",
        "REPORT_TEMPLATE.md",
        "PROJECT_COMPLETION.md",
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"✗ Missing files: {', '.join(missing)}")
        return False
    
    print(f"✓ All {len(required_files)} required files present")
    return True


def test_directories():
    """Test that required directories exist"""
    print("\nTesting directories...")
    
    dirs = ["data", "logs"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"  Created directory: {d}")
    
    print("✓ All required directories present")
    return True


def test_dependencies():
    """Test that all dependencies are installed"""
    print("\nTesting dependencies...")
    
    dependencies = [
        ("flask", "Flask"),
        ("bcrypt", "bcrypt"),
        ("argon2", "argon2-cffi"),
        ("pyotp", "pyotp"),
        ("requests", "requests"),
    ]
    
    missing = []
    for module, package in dependencies:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"✗ Missing packages: {', '.join(missing)}")
        print(f"  Install with: pip install {' '.join(missing)}")
        return False
    
    print("✓ All dependencies installed")
    return True


def run_all_tests(test_server=False):
    """Run all tests"""
    print("="*60)
    print("PASSWORD RESEARCH PROJECT - SYSTEM TEST")
    print("="*60)
    
    results = {
        "Dependencies": test_dependencies(),
        "Imports": test_imports(),
        "File Structure": test_file_structure(),
        "Directories": test_directories(),
        "Configurations": test_configurations(),
        "User Generation": test_user_generation(),
    }
    
    if test_server:
        results["Server Endpoints"] = test_server_endpoints()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20s} {status}")
    
    all_passed = all(results.values())
    
    print("="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED - System ready for experiments!")
    else:
        print("✗ SOME TESTS FAILED - Please fix issues before running experiments")
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    # Check if --with-server flag is provided
    test_server = "--with-server" in sys.argv
    
    if test_server:
        print("Note: Server tests enabled. Make sure server is running!")
        print("Start server in another terminal: python app.py")
        print()
    else:
        print("Note: Server tests skipped. Use --with-server to test server.")
        print()
    
    success = run_all_tests(test_server)
    sys.exit(0 if success else 1)
