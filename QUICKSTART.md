# Quick Start Guide - OTP SMS & AI Chat Features

## 🚀 What's New?

Your ExpensesIQ app now has two powerful features:

1. **📱 OTP via Phone SMS** - Send one-time passwords to users' phone numbers using Twilio
2. **🤖 AI Chat Integration** - Chat with OpenAI GPT models for financial advice and expense analysis

---

## ⚙️ Setup in 5 Minutes

### Step 1: Database Migration
First, run the database migration to add phone support:

```bash
python migrate_db.py
```

✓ This adds the `phone` column to the OTP table.

### Step 2: Install Dependencies

All dependencies are already in `requirements.txt`. Just ensure they're installed:

```bash
pip install -r requirements.txt
```

Key packages:
- `twilio` - For SMS OTP
- `openai` - For AI chat (requests-based)
- `python-dotenv` - For environment variables

### Step 3: Configure Credentials

Copy the sample file and add your credentials:

```bash
# Windows
copy .env.sample .env

# Mac/Linux
cp .env.sample .env
```

Edit `.env` and add:

**For Twilio SMS (Optional):**
- Get from https://www.twilio.com/console
- `TWILIO_ACCOUNT_SID` - Your account SID
- `TWILIO_AUTH_TOKEN` - Your auth token  
- `TWILIO_PHONE_NUMBER` - Your Twilio number (e.g., +1234567890)

**For OpenAI Chat (Optional):**
- Get from https://platform.openai.com/api-keys
- `OPENAI_API_KEY` - Your API key (sk-...)

### Step 4: Test the Features

```bash
python test_new_features.py
```

All green? You're ready to go! ✓

### Step 5: Start the App

```bash
python app.py
```

The app is now live with OTP SMS and AI Chat features!

---

## 📚 API Usage Examples

### 1. Send OTP for Password Reset

```bash
curl -X POST http://localhost:5000/api/otp/send \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@gmail.com",
    "phone": "+919876543210"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "sent_to": {
    "email": "user@gmail.com",
    "phone": "+919876543210"
  }
}
```

### 2. Verify OTP

```bash
curl -X POST http://localhost:5000/api/otp/verify \
  -H "Content-Type: application/json" \
  -d '{
    "otp": "123456",
    "phone": "+919876543210"
  }'
```

### 3. Ask for Financial Advice

```bash
curl -X POST http://localhost:5000/api/ai/expense-advisor \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "message": "How can I save more money?"
  }'
```

### 4. Get AI Insights

```bash
curl -X GET http://localhost:5000/api/ai/insights \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

---

## 🔑 Key Features

### OTP Service
- ✓ Send OTP to email and phone
- ✓ Verify OTP with expiration check
- ✓ Automatic cleanup after verification
- ✓ 10-minute expiration for security

### AI Chat Service
- ✓ General chat with OpenAI GPT
- ✓ Financial advisor mode with context
- ✓ Expense insights generation
- ✓ Context-aware responses based on transaction history

---

## 📋 Files Modified/Created

**New Files:**
- `api_routes.py` - API endpoints (500+ lines)
- `test_new_features.py` - Test suite
- `migrate_db.py` - Database migration
- `.env.sample` - Sample environment config
- `OTP_CHAT_IMPLEMENTATION.md` - Detailed documentation

**Modified Files:**
- `services/otp_service.py` - Added Twilio SMS support
- `services/ai_service.py` - Added chat endpoints
- `app.py` - Registered API routes
- `requirements.txt` - Added twilio package

---

## ⚠️ Important Notes

1. **Credentials are Optional**
   - Features work without credentials (graceful fallback)
   - Only enable what you need

2. **Costs**
   - Twilio: SMS charges apply (~$0.0075 per SMS)
   - OpenAI: API charges based on tokens used
   - Set spending limits in respective dashboards

3. **Security**
   - Never commit `.env` file to git
   - Rotate API keys regularly
   - Use environment variables for all secrets

4. **Trial Limitations**
   - Twilio trial: Limited recipients, need to verify numbers
   - OpenAI free trial: Limited tokens/month

---

## 🐛 Troubleshooting

### "Twilio credentials not configured"
→ Add TWILIO_* variables to `.env`

### "OpenAI API error"
→ Check API key is valid and has balance

### "OTP not sending"
→ Verify Twilio phone number format includes country code

### "Database error: phone column missing"
→ Run `python migrate_db.py`

---

## 📖 Full Documentation

See `OTP_CHAT_IMPLEMENTATION.md` for:
- Complete API documentation
- Response examples
- Error handling
- Advanced usage
- Future enhancements

---

## ✨ Next Steps

1. ✓ Test the features locally
2. Set up Twilio and OpenAI accounts
3. Add credentials to `.env`
4. Deploy to production
5. Monitor API usage and costs

**Questions?** Check the documentation files or test output.

Happy expense tracking! 🎉
