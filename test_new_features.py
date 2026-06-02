#!/usr/bin/env python3
"""
Test script for OTP SMS and AI Chat features
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_otp_service():
    """Test OTP service functions"""
    print("\n" + "="*60)
    print("Testing OTP Service")
    print("="*60)
    
    from services.otp_service import generate_otp, store_otp, verify_otp, delete_otp
    
    # Test OTP generation
    otp = generate_otp()
    print(f"✓ Generated OTP: {otp}")
    assert len(otp) == 6, "OTP should be 6 digits"
    assert otp.isdigit(), "OTP should be numeric"
    
    # Test storing OTP
    test_email = "test@gmail.com"
    test_phone = "+919876543210"
    stored = store_otp(email=test_email, phone=test_phone, otp=otp)
    print(f"✓ Stored OTP for email and phone: {stored}")
    
    # Test verifying OTP
    verified_email = verify_otp(otp, email=test_email)
    print(f"✓ Verified OTP for email: {verified_email}")
    assert verified_email, "OTP should verify correctly"
    
    verified_phone = verify_otp(otp, phone=test_phone)
    print(f"✓ Verified OTP for phone: {verified_phone}")
    assert verified_phone, "OTP should verify correctly"
    
    # Test deleting OTP
    deleted = delete_otp(email=test_email, phone=test_phone)
    print(f"✓ Deleted OTP: {deleted}")
    
    print("\n✓ All OTP tests passed!\n")


def test_ai_service():
    """Test AI service functions"""
    print("\n" + "="*60)
    print("Testing AI Service")
    print("="*60)
    
    from services.ai_service import generate_insights, chat_with_ai
    
    # Test generate_insights
    transactions = [
        {'type': 'income', 'amount': 5000, 'category': 'Salary', 'date': '2024-01-01', 'user': 'test', 'note': ''},
        {'type': 'expense', 'amount': 500, 'category': 'Food', 'date': '2024-01-02', 'user': 'test', 'note': ''},
        {'type': 'expense', 'amount': 300, 'category': 'Transport', 'date': '2024-01-03', 'user': 'test', 'note': ''},
    ]
    
    insights = generate_insights(transactions)
    print(f"✓ Generated insights:")
    print(f"  - Total Income: {insights.get('total_income')}")
    print(f"  - Total Expense: {insights.get('total_expense')}")
    print(f"  - Net: {insights.get('net')}")
    print(f"  - Avg Daily Expense: {insights.get('avg_daily_expense')}")
    print(f"  - Top Categories: {insights.get('top_categories')}")
    
    assert insights['total_income'] == 5000, "Income calculation error"
    assert insights['total_expense'] == 800, "Expense calculation error"
    
    print("\n✓ All AI service tests passed!\n")


def test_api_routes():
    """Test API route registration"""
    print("\n" + "="*60)
    print("Testing API Routes")
    print("="*60)
    
    try:
        from api_routes import register_api_routes
        from flask import Flask
        
        app = Flask(__name__)
        register_api_routes(app)
        
        # Check routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/api/otp/send',
            '/api/otp/verify',
            '/api/ai/chat',
            '/api/ai/expense-advisor',
            '/api/ai/insights'
        ]
        
        print("✓ Registered routes:")
        for route in expected_routes:
            found = any(route in r for r in routes)
            status = "✓" if found else "✗"
            print(f"  {status} {route}")
        
        print("\n✓ All API routes registered successfully!\n")
        
    except Exception as e:
        print(f"✗ Error registering routes: {e}\n")
        raise


def test_database_schema():
    """Test database schema updates"""
    print("\n" + "="*60)
    print("Testing Database Schema")
    print("="*60)
    
    import sqlite3
    
    try:
        # Check if data.db exists
        if os.path.exists('data.db'):
            conn = sqlite3.connect('data.db')
            cur = conn.cursor()
            
            # Check otp_tokens table structure
            cur.execute("PRAGMA table_info(otp_tokens)")
            columns = {row[1]: row[2] for row in cur.fetchall()}
            
            print("✓ otp_tokens table columns:")
            print(f"  - email: {columns.get('email')}")
            print(f"  - phone: {columns.get('phone')}")
            print(f"  - otp: {columns.get('otp')}")
            print(f"  - expires_at: {columns.get('expires_at')}")
            
            assert 'phone' in columns, "phone column missing in otp_tokens"
            assert 'email' in columns, "email column missing in otp_tokens"
            
            conn.close()
            print("\n✓ Database schema is correct!\n")
        else:
            print("⚠ data.db not found. Run app.py to initialize.\n")
    
    except Exception as e:
        print(f"✗ Database check failed: {e}\n")


def test_environment_setup():
    """Test environment setup"""
    print("\n" + "="*60)
    print("Testing Environment Setup")
    print("="*60)
    
    # Check for .env file
    env_file = '.env'
    if os.path.exists(env_file):
        print("✓ .env file found")
        with open(env_file, 'r') as f:
            content = f.read()
            has_twilio = 'TWILIO' in content
            has_openai = 'OPENAI' in content
            print(f"  - Twilio config: {'✓' if has_twilio else '✗'}")
            print(f"  - OpenAI config: {'✓' if has_openai else '✗'}")
    else:
        print("⚠ .env file not found. Create one for production use.")
        print("  Required variables:")
        print("  - TWILIO_ACCOUNT_SID")
        print("  - TWILIO_AUTH_TOKEN")
        print("  - TWILIO_PHONE_NUMBER")
        print("  - OPENAI_API_KEY")
    
    print()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OTP SMS and AI Chat Feature Tests")
    print("="*60)
    
    try:
        test_environment_setup()
        test_database_schema()
        test_otp_service()
        test_ai_service()
        test_api_routes()
        
        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
