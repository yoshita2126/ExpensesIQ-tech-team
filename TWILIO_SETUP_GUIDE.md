# Twilio SMS OTP Setup Guide

## Overview
This guide explains how to set up Twilio for sending SMS OTP (One-Time Passwords) in ExpensesIQ.

## Prerequisites
- A Twilio account (free trial available at https://www.twilio.com/try-twilio)
- A phone number verified for Twilio (required before sending SMS)
- Your Twilio Account SID and Auth Token

## Step-by-Step Setup

### 1. Create a Twilio Account
1. Visit https://www.twilio.com/try-twilio
2. Sign up for a free account
3. Verify your email address
4. Complete the phone verification process

### 2. Get Your Credentials
1. Go to your Twilio Dashboard: https://console.twilio.com/
2. In the left sidebar, click **Account**
3. Copy your **Account SID** (looks like: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
4. Copy your **Auth Token** (looks like: your_auth_token_here)
5. Note these credentials - you'll need them in Step 4

### 3. Get a Twilio Phone Number
1. In the Twilio Console, go to **Phone Numbers** → **Manage**
2. Click **Get your first Twilio phone number**
3. Follow the prompts to claim a phone number
4. Copy your Twilio phone number (format: +1XXXXXXXXXX)

### 4. Configure Environment Variables
1. Open the `.env` file in the project root
2. Add or update these lines:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
```

Replace the values with your actual Twilio credentials.

### 5. Test the SMS OTP

#### Via API (Using curl or Postman)
```bash
curl -X POST http://localhost:5000/api/otp/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+91XXXXXXXXXX",
    "email": "user@example.com",
    "type": "password_reset"
  }'
```

Expected successful response:
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "sent_to": {
    "email": "Email sent successfully",
    "phone": "SMS sent to +91XXXXXXXXXX"
  }
}
```

#### Via Web UI
1. Start the Flask app: `python app.py`
2. Go to http://localhost:5000/test-otp
3. Enter your phone number (with country code, e.g., +91XXXXXXXXXX)
4. Click "Send OTP via SMS"
5. Check your phone for the SMS

### 6. Verify OTP

```bash
curl -X POST http://localhost:5000/api/otp/verify \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+91XXXXXXXXXX",
    "otp": "123456"
  }'
```

## Troubleshooting

### "Twilio credentials not configured"
- Check that TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER are set in `.env`
- Restart the Flask app after updating `.env`
- Verify no extra spaces in `.env` values

### SMS not received
1. **Free Trial Limitation**: Twilio free trial can only send SMS to verified phone numbers
   - Go to Twilio Console → Verified Caller IDs
   - Add your phone number to the verified list
2. **Wrong phone format**: Use international format with country code: +91XXXXXXXXXX (India), +1XXXXXXXXXX (USA)
3. **Network Issues**: Check internet connection
4. **Twilio Account Status**: Verify your account is active (not suspended)

### Can't find Account SID/Auth Token
1. Log in to https://console.twilio.com/
2. Look at the top of the dashboard - your Account SID is displayed there
3. Click the lock icon next to "Auth Token" to reveal it

### SMS cost
- **Free Trial**: Limited to $15 credit (enough for 30+ SMS)
- **Production**: Pay-as-you-go pricing (~₹2-3 per SMS in India)

## Integration in Application

### OTP Workflow
1. User requests OTP → `/api/otp/send` endpoint sends SMS + Email
2. User receives SMS with 6-digit OTP valid for 10 minutes
3. User submits OTP → `/api/otp/verify` endpoint verifies it
4. Backend returns success/failure

### Code Example (JavaScript)
```javascript
// Send OTP
async function sendOTP(phone) {
  const response = await fetch('/api/otp/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone: phone,
      type: 'password_reset'
    })
  });
  const data = await response.json();
  console.log(data);
}

// Verify OTP
async function verifyOTP(phone, otp) {
  const response = await fetch('/api/otp/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone: phone,
      otp: otp
    })
  });
  const data = await response.json();
  console.log(data);
}
```

## API Reference

### Send OTP Endpoint
- **URL**: `/api/otp/send`
- **Method**: POST
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
    "phone": "+91XXXXXXXXXX",  // Optional - SMS OTP
    "email": "user@gmail.com",  // Optional - Email OTP
    "type": "password_reset"    // Purpose of OTP
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "OTP sent successfully",
    "sent_to": {
      "phone": "SMS sent to +91XXXXXXXXXX",
      "email": "Email sent successfully"
    }
  }
  ```

### Verify OTP Endpoint
- **URL**: `/api/otp/verify`
- **Method**: POST
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
    "phone": "+91XXXXXXXXXX",  // Optional - verify SMS OTP
    "email": "user@gmail.com",  // Optional - verify Email OTP
    "otp": "123456"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "OTP verified successfully",
    "verified": true
  }
  ```

## Security Notes
- OTP is valid for 10 minutes by default (configurable in `.env`: OTP_EXPIRY_MINUTES)
- OTP length is 6 digits (configurable: OTP_LENGTH)
- All OTPs are deleted after successful verification or expiration
- Phone numbers are stored in database only if SMS is explicitly used

## Support
- Twilio Documentation: https://www.twilio.com/docs/sms
- Twilio Console: https://console.twilio.com/
- Twilio Support: https://support.twilio.com/
