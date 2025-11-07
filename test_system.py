#!/usr/bin/env python3
"""
test_system.py - Comprehensive system test
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_env_vars():
    """Check if environment variables are set"""
    print("🔍 Checking Environment Variables...")
    
    required_vars = [
        'ZENDESK_SUBDOMAIN',
        'ZENDESK_EMAIL',
        'ZENDESK_API_TOKEN',
        'OPENAI_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your'):
            missing.append(var)
            print(f"   ❌ {var} - NOT SET")
        else:
            # Show partial value for security
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"   ✅ {var} - {display_value}")
    
    if missing:
        print(f"\n❌ Missing variables: {', '.join(missing)}")
        print("   Please update your .env file!")
        return False
    
    print("   ✅ All environment variables set!\n")
    return True


def test_zendesk():
    """Test Zendesk connection"""
    print("🔌 Testing Zendesk Connection...")
    
    try:
        from fetch_tickets import test_connection
        if test_connection():
            print("   ✅ Zendesk connection successful!\n")
            return True
        else:
            print("   ❌ Zendesk connection failed!\n")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
        return False


def test_openai():
    """Test OpenAI connection"""
    print("🤖 Testing OpenAI Connection...")
    
    try:
        from analyze_ticket import test_openai_connection
        if test_openai_connection():
            print("   ✅ OpenAI connection successful!\n")
            return True
        else:
            print("   ❌ OpenAI connection failed!\n")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
        return False


def test_fetch_tickets():
    """Test fetching tickets"""
    print("📥 Testing Ticket Fetch...")
    
    try:
        from fetch_tickets import get_recent_tickets
        tickets = get_recent_tickets(3)
        
        if tickets:
            print(f"   ✅ Fetched {len(tickets)} tickets")
            for i, ticket in enumerate(tickets, 1):
                print(f"      {i}. #{ticket['id']}: {ticket['subject'][:50]}...")
            print()
            return True
        else:
            print("   ❌ No tickets fetched\n")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
        return False


def test_analysis():
    """Test ticket analysis"""
    print("🧪 Testing AI Analysis...")
    
    try:
        from analyze_ticket import analyze_ticket
        
        sample_subject = "App crashed when I tried to login"
        sample_desc = "I clicked login button and got error 500. This is urgent!"
        
        result = analyze_ticket(sample_subject, sample_desc)
        
        if result and 'summary' in result:
            print(f"   ✅ Analysis successful!")
            print(f"      Summary: {result['summary']}")
            print(f"      Root Cause: {result['root_cause']}")
            print(f"      Urgency: {result['urgency']}")
            print(f"      Sentiment: {result['sentiment']}")
            print()
            return True
        else:
            print("   ❌ Analysis failed\n")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 AI TICKET PROCESSOR - SYSTEM TEST")
    print("="*60 + "\n")
    
    results = {
        "Environment Variables": check_env_vars(),
        "Zendesk Connection": test_zendesk(),
        "OpenAI Connection": test_openai(),
        "Fetch Tickets": test_fetch_tickets(),
        "AI Analysis": test_analysis()
    }
    
    print("="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*60)
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready to use!")
        print("\n📋 Next Steps:")
        print("   python ai_ticket_processor.py --limit 5")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
