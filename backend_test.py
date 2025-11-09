#!/usr/bin/env python3
"""
Backend Authentication Testing Script
Tests authentication endpoints for the academic management system
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://debug-assist-4.preview.emergentagent.com/api"

class AuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.users = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_registration(self):
        """Test user registration for both student and teacher"""
        self.log("=== Testing User Registration ===")
        
        # Test student registration
        student_data = {
            "full_name": "Juan Pérez",
            "email": "juan@test.com",
            "password": "test123",
            "role": "student"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=student_data)
            self.log(f"Student registration status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.tokens['student'] = data['access_token']
                self.users['student'] = data['user']
                self.log(f"✅ Student registered successfully: {data['user']['full_name']}")
                self.log(f"Student ID: {data['user']['id']}")
            else:
                self.log(f"❌ Student registration failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Student registration error: {str(e)}", "ERROR")
            return False
            
        # Test teacher registration
        teacher_data = {
            "full_name": "María López",
            "email": "maria@test.com",
            "password": "test123",
            "role": "teacher"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=teacher_data)
            self.log(f"Teacher registration status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.tokens['teacher'] = data['access_token']
                self.users['teacher'] = data['user']
                self.log(f"✅ Teacher registered successfully: {data['user']['full_name']}")
                self.log(f"Teacher ID: {data['user']['id']}")
                return True
            else:
                self.log(f"❌ Teacher registration failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Teacher registration error: {str(e)}", "ERROR")
            return False
    
    def test_login(self):
        """Test user login for both registered users"""
        self.log("=== Testing User Login ===")
        
        # Test student login
        student_credentials = {
            "email": "juan@test.com",
            "password": "test123"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=student_credentials)
            self.log(f"Student login status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.tokens['student_login'] = data['access_token']
                self.log(f"✅ Student login successful: {data['user']['full_name']}")
            else:
                self.log(f"❌ Student login failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Student login error: {str(e)}", "ERROR")
            return False
            
        # Test teacher login
        teacher_credentials = {
            "email": "maria@test.com",
            "password": "test123"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=teacher_credentials)
            self.log(f"Teacher login status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.tokens['teacher_login'] = data['access_token']
                self.log(f"✅ Teacher login successful: {data['user']['full_name']}")
                return True
            else:
                self.log(f"❌ Teacher login failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Teacher login error: {str(e)}", "ERROR")
            return False
    
    def test_authentication(self):
        """Test authentication using tokens"""
        self.log("=== Testing Authentication (/auth/me) ===")
        
        # Test student authentication
        try:
            headers = {"Authorization": f"Bearer {self.tokens['student']}"}
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            self.log(f"Student auth check status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Student authentication successful: {data['full_name']} ({data['role']})")
            else:
                self.log(f"❌ Student authentication failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Student authentication error: {str(e)}", "ERROR")
            return False
            
        # Test teacher authentication
        try:
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            self.log(f"Teacher auth check status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Teacher authentication successful: {data['full_name']} ({data['role']})")
                return True
            else:
                self.log(f"❌ Teacher authentication failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Teacher authentication error: {str(e)}", "ERROR")
            return False
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        self.log("=== Testing Invalid Credentials ===")
        
        invalid_credentials = {
            "email": "invalid@test.com",
            "password": "wrongpassword"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=invalid_credentials)
            self.log(f"Invalid login status: {response.status_code}")
            
            if response.status_code == 401:
                self.log("✅ Invalid credentials properly rejected")
                return True
            else:
                self.log(f"❌ Invalid credentials not properly handled: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Invalid credentials test error: {str(e)}", "ERROR")
            return False
    
    def test_duplicate_registration(self):
        """Test duplicate email registration"""
        self.log("=== Testing Duplicate Registration ===")
        
        duplicate_data = {
            "full_name": "Juan Duplicate",
            "email": "juan@test.com",  # Same email as first student
            "password": "test123",
            "role": "student"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=duplicate_data)
            self.log(f"Duplicate registration status: {response.status_code}")
            
            if response.status_code == 400:
                self.log("✅ Duplicate email properly rejected")
                return True
            else:
                self.log(f"❌ Duplicate email not properly handled: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Duplicate registration test error: {str(e)}", "ERROR")
            return False
    
    def verify_mongodb_persistence(self):
        """Verify that users are stored in MongoDB"""
        self.log("=== Verifying MongoDB Persistence ===")
        self.log("Note: Direct MongoDB verification requires database access")
        self.log("Indirect verification: successful login after registration indicates persistence")
        
        # We can verify persistence by attempting fresh logins
        # If data was only in memory, new session login would fail
        fresh_session = requests.Session()
        
        try:
            # Test fresh login for student
            student_creds = {"email": "juan@test.com", "password": "test123"}
            response = fresh_session.post(f"{BACKEND_URL}/auth/login", json=student_creds)
            
            if response.status_code == 200:
                self.log("✅ Student data persisted (fresh session login successful)")
            else:
                self.log("❌ Student data may not be persisted", "ERROR")
                return False
                
            # Test fresh login for teacher
            teacher_creds = {"email": "maria@test.com", "password": "test123"}
            response = fresh_session.post(f"{BACKEND_URL}/auth/login", json=teacher_creds)
            
            if response.status_code == 200:
                self.log("✅ Teacher data persisted (fresh session login successful)")
                return True
            else:
                self.log("❌ Teacher data may not be persisted", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Persistence verification error: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        self.log("Starting Authentication Tests for Academic Management System")
        self.log(f"Backend URL: {BACKEND_URL}")
        
        results = {
            "registration": False,
            "login": False,
            "authentication": False,
            "invalid_credentials": False,
            "duplicate_registration": False,
            "persistence": False
        }
        
        # Run tests in sequence
        results["registration"] = self.test_registration()
        if results["registration"]:
            results["login"] = self.test_login()
            results["authentication"] = self.test_authentication()
            results["persistence"] = self.verify_mongodb_persistence()
        
        results["invalid_credentials"] = self.test_invalid_credentials()
        results["duplicate_registration"] = self.test_duplicate_registration()
        
        # Summary
        self.log("=== TEST SUMMARY ===")
        passed = sum(results.values())
        total = len(results)
        
        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test.upper()}: {status}")
        
        self.log(f"Overall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All authentication tests PASSED!")
            return True
        else:
            self.log("⚠️  Some authentication tests FAILED!")
            return False

def main():
    """Main function to run tests"""
    tester = AuthTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()