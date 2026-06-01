import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sqlite3

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp(email: str, otp: str) -> Dict[str, Any]:
    """Send OTP to email"""
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
    
    return send_email(email, subject, body)


def store_otp(email: str, otp: str, expires_in_minutes: int = 10) -> bool:
    """Store OTP in database"""
    try:
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        
        expires_at = (datetime.now() + timedelta(minutes=expires_in_minutes)).isoformat()
        
        # Delete old OTPs for this email
        cur.execute("DELETE FROM otp_tokens WHERE email = ?", (email,))
        
        # Insert new OTP
        cur.execute(
            "INSERT INTO otp_tokens (email, otp, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (email, otp, expires_at, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error storing OTP: {e}")
        return False


def verify_otp(email: str, otp: str) -> bool:
    """Verify OTP"""
    try:
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        
        cur.execute(
            "SELECT otp, expires_at FROM otp_tokens WHERE email = ? ORDER BY created_at DESC LIMIT 1",
            (email,)
        )
        
        result = cur.fetchone()
        conn.close()
        
        if not result:
            return False
        
        stored_otp, expires_at = result
        
        # Check if OTP matches
        if stored_otp != otp:
            return False
        
        # Check if OTP is expired
        if datetime.fromisoformat(expires_at) < datetime.now():
            return False
        
        return True
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return False


def delete_otp(email: str) -> bool:
    """Delete OTP after successful verification"""
    try:
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM otp_tokens WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting OTP: {e}")
        return False
