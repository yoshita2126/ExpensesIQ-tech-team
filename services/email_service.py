import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def send_email(to_email: str, subject: str, body: str) -> Dict[str, Any]:
    smtp_host = os.environ.get('SMTP_HOST') or os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER') or os.environ.get('SENDER_EMAIL')
    smtp_pass = os.environ.get('SMTP_PASS') or os.environ.get('SENDER_PASSWORD')

    if smtp_pass:
        smtp_pass = smtp_pass.replace(' ', '')

    if not smtp_host or not smtp_user or not smtp_pass:
        return {'error': 'SMTP is not configured. Please set SMTP_SERVER, SENDER_EMAIL, and SENDER_PASSWORD in .env.'}

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}
