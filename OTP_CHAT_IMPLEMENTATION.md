# OTP SMS and AI Chat Features - Implementation Guide

## Features Added

This implementation adds two major features to ExpensesIQ:

### 1. **OTP (One-Time Password) via SMS**
- Send OTP to phone numbers using Twilio
- Support for both email and SMS OTP
- 10-minute expiration for security
- Verification and deletion of used OTPs

### 2. **AI Chat Integration with OpenAI**
- Chat endpoint for general conversations
- Expense Advisor endpoint for financial advice
- AI Insights generation from transaction history
- Context-aware responses

---

## Setup Instructions

### Prerequisites

1. **Twilio Account** (for SMS OTP)
   - Sign up at https://www.twilio.com
   - Get your Account SID, Auth Token, and Phone Number
   - Store these in environment variables

2. **OpenAI API Key** (for AI Chat)
   - Get your API key from https://platform.openai.com/api-keys
   - Store in environment variable

### Environment Variables

Create a `.env` file in the project root with:

```
# Twilio Configuration (for OTP SMS)
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# OpenAI Configuration (for AI Chat)
OPENAI_API_KEY=your_openai_api_key_here
```

### Installation

1. Install Twilio package:
   ```bash
   pip install twilio
   ```

2. Or use requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

---

## API Endpoints

### OTP Endpoints

#### 1. Send OTP
**Endpoint:** `POST /api/otp/send`

**Request:**
```json
{
    "email": "user@gmail.com",
    "phone": "+1234567890",
    "type": "password_reset"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "OTP sent successfully",
    "sent_to": {
        "email": "user@gmail.com",
        "phone": "+1234567890"
    }
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Email or phone number is required"
}
```

#### 2. Verify OTP
**Endpoint:** `POST /api/otp/verify`

**Request:**
```json
{
    "otp": "123456",
    "email": "user@gmail.com"
}
```

**Alternative (phone verification):**
```json
{
    "otp": "123456",
    "phone": "+1234567890"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "OTP verified successfully"
}
```

---

### AI Chat Endpoints

#### 1. General AI Chat
**Endpoint:** `POST /api/ai/chat`

**Requires:** User must be logged in (session required)

**Request:**
```json
{
    "messages": [
        {"role": "user", "content": "What's the best way to save money?"}
    ],
    "system_prompt": "You are a helpful financial advisor."
}
```

**Response:**
```json
{
    "success": true,
    "message": "Here are some practical ways to save money...",
    "model": "gpt-4o-mini",
    "usage": {
        "prompt_tokens": 25,
        "completion_tokens": 150,
        "total_tokens": 175
    }
}
```

#### 2. Expense Advisor
**Endpoint:** `POST /api/ai/expense-advisor`

**Requires:** User must be logged in

**Request:**
```json
{
    "message": "How can I reduce my expenses?"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Based on your spending patterns, here are recommendations...",
    "model": "gpt-4o-mini"
}
```

#### 3. Get AI Insights
**Endpoint:** `GET /api/ai/insights`

**Requires:** User must be logged in

**Response:**
```json
{
    "success": true,
    "insights": {
        "total_income": 50000,
        "total_expense": 30000,
        "net": 20000,
        "avg_daily_expense": 1000,
        "top_categories": [
            {"category": "Food", "count": 15},
            {"category": "Transport", "count": 10}
        ],
        "tips": [
            "Your average daily expense is high...",
            "Top category: Food — try setting a budget..."
        ],
        "ai_summary": "You're spending well but could optimize in food..."
    }
}
```

---

## Database Changes

### Updated OTP Tokens Table

```sql
CREATE TABLE IF NOT EXISTS otp_tokens(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    phone TEXT,
    otp TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL
)
```

**Changes:**
- `email` column is now optional (nullable)
- Added `phone` column for SMS OTP
- Both can be used together or separately

---

## Usage Examples

### Example 1: Send OTP for Password Reset (Email + Phone)

```bash
curl -X POST http://localhost:5000/api/otp/send \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@gmail.com",
    "phone": "+919876543210",
    "type": "password_reset"
  }'
```

### Example 2: Verify OTP

```bash
curl -X POST http://localhost:5000/api/otp/verify \
  -H "Content-Type: application/json" \
  -d '{
    "otp": "123456",
    "phone": "+919876543210"
  }'
```

### Example 3: Chat with AI About Finances

```bash
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "messages": [
      {"role": "user", "content": "What budget strategy would you recommend?"}
    ]
  }'
```

### Example 4: Get Expense Advice

```bash
curl -X POST http://localhost:5000/api/ai/expense-advisor \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "message": "I want to save more money. What should I cut back on?"
  }'
```

---

## File Structure

**New/Modified Files:**

- `api_routes.py` - Contains all new API endpoints
- `services/otp_service.py` - Enhanced with Twilio SMS support
- `services/ai_service.py` - Added chat endpoints
- `requirements.txt` - Added twilio package
- `app.py` - Registered API routes

---

## Security Considerations

1. **OTP Security:**
   - OTPs expire after 10 minutes
   - Only stored in database during verification window
   - Deleted after successful verification
   - Rate limiting recommended for production

2. **API Authentication:**
   - Chat endpoints require user login
   - All endpoints validate input
   - Error messages don't leak sensitive info

3. **Environment Variables:**
   - Never commit `.env` file
   - Use strong, unique API keys
   - Rotate keys regularly

---

## Error Handling

All endpoints return consistent error responses:

```json
{
    "success": false,
    "error": "Description of the error"
}
```

Common HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (missing/invalid fields)
- `401` - Unauthorized (not logged in for protected endpoints)
- `404` - Not Found
- `500` - Server Error

---

## Testing

### Test OTP Functionality

1. Send OTP:
   ```bash
   python
   >>> from services.otp_service import generate_otp, send_otp, store_otp, verify_otp
   >>> otp = generate_otp()
   >>> print(f"Generated OTP: {otp}")
   ```

2. Test without Twilio (mock):
   ```python
   # Edit send_sms_otp() to return mock success during testing
   ```

### Test AI Chat

```bash
python
>>> from services.ai_service import chat_with_ai
>>> result = chat_with_ai([{"role": "user", "content": "Hello!"}])
>>> print(result)
```

---

## Troubleshooting

### Twilio SMS Not Sending
- Check environment variables are set correctly
- Verify account is not in trial mode (trial has limitations)
- Check phone number format includes country code
- Verify account has sufficient balance

### OpenAI API Errors
- Verify API key is correct and has permissions
- Check rate limits haven't been exceeded
- Ensure model name is correct (gpt-4o-mini)
- Monitor API usage in OpenAI dashboard

### Database Errors
- Ensure `otp_tokens` table has `phone` column
- Run `init_db()` to update table schema
- Check database file has write permissions

---

## Future Enhancements

- [ ] Rate limiting for OTP endpoints
- [ ] Multi-language support for AI responses
- [ ] Voice OTP option
- [ ] Conversation history storage
- [ ] Advanced financial analysis with AI
- [ ] Integration with expense categorization AI
