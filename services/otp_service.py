import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sqlite3
import os
import traceback
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data.db"

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp(email: str = None, phone: str = None, otp: str = None) -> Dict[str, Any]:
    """Send OTP to email and/or phone"""
    if not email and not phone:
        return {'success': False, 'error': 'Email or phone is required'}
    
    if not otp:
        return {'success': False, 'error': 'OTP is required'}
    
    results = {}
    
    # Send to email
    if email:
        from services.email_service import send_email
        subject = "ExpensesIQ - Password Reset OTP"
        body = f"""
        Hello,
        
        Your OTP for password reset is: {otp}
        
        This OTP is valid for 10 minutes.
        
        If you did not request this, please ignore this email.
        
        Regards,
        ExpensesIQ Team
        """
        email_result = send_email(email, subject, body)
        if email_result.get('error'):
            return {
                'success': False,
                'error': f"Email send failed: {email_result['error']}",
                'details': {'email': email_result}
            }
        results['email'] = {'success': True}
    
    # Send to phone via Twilio
    if phone:
        sms_result = send_sms_otp(phone, otp)
        if sms_result.get('error'):
            return {
                'success': False,
                'error': f"SMS send failed: {sms_result['error']}",
                'details': {'phone': sms_result}
            }
        results['phone'] = {'success': True}
    
    return {'success': True, 'results': results}


def send_sms_otp(phone: str, otp: str) -> Dict[str, Any]:
    """Send OTP via SMS using Twilio"""
    try:
        from twilio.rest import Client
        
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, twilio_phone]):
            return {
                'success': False, 
                'error': 'Twilio credentials not configured'
            }
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"Your ExpensesIQ OTP is: {otp}. Valid for 10 minutes.",
            from_=twilio_phone,
            to=phone
        )
        
        return {
            'success': True,
            'message_sid': message.sid,
            'phone': phone
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def store_otp(email: str = None, otp: str = None, phone: str = None, expires_in_minutes: int = 10) -> bool:
    """Store OTP in database for email and/or phone"""
    if not email and not phone:
        return False
    
    if not otp:
        return False
    
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)
        cur = conn.cursor()
        
        expires_at = (datetime.now() + timedelta(minutes=expires_in_minutes)).isoformat()
        
        # Delete old OTPs for this email/phone
        if email:
            cur.execute("DELETE FROM otp_tokens WHERE email = ?", (email,))
        if phone:
            cur.execute("DELETE FROM otp_tokens WHERE phone = ?", (phone,))
        
        # Insert new OTP - use empty string for email if not provided
        email_to_store = email if email else ''
        
        cur.execute(
            "INSERT INTO otp_tokens (email, phone, otp, expires_at, created_at) VALUES (?, ?, ?, ?, ?)",
            (email_to_store, phone, otp, expires_at, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error storing OTP: {e}")
        traceback.print_exc()
        return False


def cleanup_expired_otps() -> None:
    """Delete expired OTP tokens from the database."""
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)
        cur = conn.cursor()
        cur.execute("DELETE FROM otp_tokens WHERE expires_at < ?", (datetime.now().isoformat(),))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error cleaning up expired OTPs: {e}")
        traceback.print_exc()


def verify_otp(otp: str, email: str = None, phone: str = None) -> bool:
    """Verify OTP for email or phone"""
    if not email and not phone:
        return False
    
    try:
        cleanup_expired_otps()

        conn = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)
        cur = conn.cursor()
        
        # Search by email
        if email:
            cur.execute(
                "SELECT otp, expires_at FROM otp_tokens WHERE email = ? ORDER BY created_at DESC LIMIT 1",
                (email,)
            )
        # Search by phone
        elif phone:
            cur.execute(
                "SELECT otp, expires_at FROM otp_tokens WHERE phone = ? ORDER BY created_at DESC LIMIT 1",
                (phone,)
            )
        
        result = cur.fetchone()
        conn.close()
        
        if not result:
            return False
        
        stored_otp, expires_at = result
        
        # Check if OTP is expired
        if datetime.fromisoformat(expires_at) < datetime.now():
            delete_otp(email=email, phone=phone)
            return False
        
        # Check if OTP matches
        if stored_otp != otp:
            return False
        
        return True
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        traceback.print_exc()
        return False


def delete_otp(email: str = None, phone: str = None) -> bool:
    """Delete OTP after successful verification"""
    if not email and not phone:
        return False
    
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)
        cur = conn.cursor()
        
        if email:
            cur.execute("DELETE FROM otp_tokens WHERE email = ?", (email,))
        if phone:
            cur.execute("DELETE FROM otp_tokens WHERE phone = ?", (phone,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting OTP: {e}")
        traceback.print_exc()
        return False
