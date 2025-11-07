#!/usr/bin/env python3
"""
Quick API Test Script
Tests the AI Ticket Processor API endpoints
"""

import requests
import json
from typing import Dict

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str, success: bool, message: str = ""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if message:
        print(f"  {message}")

def test_health_check() -> bool:
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200
        print_test("Health Check", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False

def test_register(email: str = "test@example.com", password: str = "testpass123") -> tuple:
    """Test user registration"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password}
        )
        success = response.status_code in [200, 201, 400]  # 400 if already exists
        data = response.json() if success else {}
        
        if response.status_code == 400 and "already registered" in response.text:
            print_test("User Registration", True, "User already exists (OK)")
            return True, None
        
        print_test("User Registration", success, f"Status: {response.status_code}")
        return success, data
    except Exception as e:
        print_test("User Registration", False, f"Error: {str(e)}")
        return False, None

def test_login(email: str = "test@example.com", password: str = "testpass123") -> str:
    """Test user login and get token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": email, "password": password}
        )
        success = response.status_code == 200
        data = response.json() if success else {}
        token = data.get("access_token", "")
        
        print_test("User Login", success, f"Token: {token[:20]}..." if token else "No token")
        return token if success else None
    except Exception as e:
        print_test("User Login", False, f"Error: {str(e)}")
        return None

def test_get_user_info(token: str) -> bool:
    """Test getting current user info"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        success = response.status_code == 200
        data = response.json() if success else {}
        
        print_test("Get User Info", success, f"Email: {data.get('email', 'N/A')}")
        return success
    except Exception as e:
        print_test("Get User Info", False, f"Error: {str(e)}")
        return False

def test_get_settings(token: str) -> bool:
    """Test getting user settings"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/settings/", headers=headers)
        success = response.status_code == 200
        
        print_test("Get Settings", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("Get Settings", False, f"Error: {str(e)}")
        return False

def test_analytics(token: str) -> bool:
    """Test analytics endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
        success = response.status_code == 200
        data = response.json() if success else {}
        
        stats = data.get("stats", {}) if success else {}
        print_test("Analytics Dashboard", success, 
                   f"Tickets: {stats.get('tickets_today', 0)} today")
        return success
    except Exception as e:
        print_test("Analytics Dashboard", False, f"Error: {str(e)}")
        return False

def test_list_tickets(token: str) -> bool:
    """Test listing tickets"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/tickets/", headers=headers)
        success = response.status_code == 200
        data = response.json() if success else []
        
        print_test("List Tickets", success, f"Found {len(data)} tickets")
        return success
    except Exception as e:
        print_test("List Tickets", False, f"Error: {str(e)}")
        return False

def main():
    print(f"\n{Colors.BLUE}╔═══════════════════════════════════════════╗")
    print(f"║   AI TICKET PROCESSOR - API TEST SUITE   ║")
    print(f"╚═══════════════════════════════════════════╝{Colors.END}\n")
    
    # Test health check
    if not test_health_check():
        print(f"\n{Colors.RED}❌ API is not running! Please start the server first.{Colors.END}")
        print(f"{Colors.YELLOW}Run: ./start.sh{Colors.END}\n")
        return
    
    print()
    
    # Test authentication flow
    test_register()
    token = test_login()
    
    if not token:
        print(f"\n{Colors.RED}❌ Authentication failed! Cannot continue tests.{Colors.END}\n")
        return
    
    print()
    
    # Test protected endpoints
    test_get_user_info(token)
    test_get_settings(token)
    test_analytics(token)
    test_list_tickets(token)
    
    print(f"\n{Colors.GREEN}✨ API tests complete!{Colors.END}")
    print(f"\n{Colors.BLUE}📚 Full API documentation: {BASE_URL}/docs{Colors.END}\n")

if __name__ == "__main__":
    main()
