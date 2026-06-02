# Architecture & Integration Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ExpensesIQ Application                      │
│                         (Flask App)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
        ┌───────▼───────┐  ┌──▼──────────┐ │
        │  Existing     │  │   NEW       │ │
        │  Routes       │  │  API Routes │ │
        │               │  │ (api_routes.py) │
        │  - /login     │  │             │ │
        │  - /dashboard │  │ ┌─────────┐ │ │
        │  - /settings  │  │ │ OTP API │ │ │
        │  - etc...     │  │ └─────────┘ │ │
        └───────────────┘  │             │ │
                           │ ┌─────────┐ │ │
                           │ │ Chat API│ │ │
                           │ └─────────┘ │ │
                           └─────────────┘ │
                                           │
        ┌──────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│                         Services Layer                            │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ OTP Service  │  │ AI Service   │  │ Email Svc    │  ...      │
│  │              │  │              │  │              │           │
│  │ - generate   │  │ - chat       │  │ - send_email │           │
│  │ - send       │  │ - insights   │  │              │           │
│  │ - verify     │  │ - advisor    │  │              │           │
│  │ - store      │  │              │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│       │                    │                │                    │
│       │                    │                │                    │
│     Twilio             OpenAI API       SMTP                      │
│       │                    │                │                    │
└───────┼────────────────────┼────────────────┼────────────────────┘
        │                    │                │
        ▼                    ▼                ▼
   ┌─────────┐         ┌──────────┐    ┌──────────┐
   │ Twilio  │         │ OpenAI   │    │ Email    │
   │ API     │         │ GPT API  │    │ Server   │
   └─────────┘         └──────────┘    └──────────┘

        │                    │
        ▼                    ▼
    SMS Sent             AI Response
```

---

## Request Flow Diagram

### OTP Sending Flow

```
User/Client
    │
    ├─→ POST /api/otp/send
    │   {email: "...", phone: "..."}
    │
    ▼
Flask Route Handler
    │
    ├─→ Validate input
    │
    ├─→ Generate OTP (6 digits)
    │
    ├─→ Send OTP
    │   ├─→ Email via SMTP
    │   └─→ SMS via Twilio API
    │
    ├─→ Store in DB
    │   └─→ Set 10-min expiry
    │
    ▼
Return Success/Error
```

### AI Chat Flow

```
User (logged in)
    │
    ├─→ POST /api/ai/chat
    │   {messages: [...], system_prompt: "..."}
    │
    ▼
Flask Route Handler
    │
    ├─→ Check authentication
    │
    ├─→ Validate input
    │
    ├─→ Call OpenAI Service
    │   │
    │   ├─→ Build request
    │   │   └─→ Format: {model: "gpt-4o-mini", messages: [...]}
    │   │
    │   ├─→ Call OpenAI API
    │   │   └─→ https://api.openai.com/v1/chat/completions
    │   │
    │   ▼
    │   ← Get response
    │
    ├─→ Format response
    │
    ▼
Return AI Response
```

### Expense Advisor Flow

```
User (logged in)
    │
    ├─→ POST /api/ai/expense-advisor
    │   {message: "How to save money?"}
    │
    ▼
Flask Route Handler
    │
    ├─→ Check authentication
    │
    ├─→ Get user's transactions
    │   └─→ Query: SELECT * FROM transactions
    │
    ├─→ Call AI Service
    │   ├─→ Build context from transactions
    │   ├─→ Create advisor prompt
    │   └─→ Call OpenAI API
    │
    ▼
Return Financial Advice
```

---

## Database Integration

```
┌─────────────────────────────────────┐
│      ExpensesIQ Database            │
│         (SQLite)                    │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ users                         │  │
│  │ - id, username, email, phone  │  │
│  │ - group_name                  │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │ OTP Verification
│  │ otp_tokens (UPDATED)          │  │ for password reset
│  │ - id                          │  │
│  │ - email TEXT (optional)       │  ├──→ Send OTP
│  │ - phone TEXT (NEW)            │  │
│  │ - otp TEXT                    │  ├──→ Verify OTP
│  │ - expires_at TEXT             │  │
│  │ - created_at TEXT             │  └──→ Delete OTP
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ transactions                  │  │ Used by AI for
│  │ - id, group_name, user        │  │ context & insights
│  │ - amount, category            │  │
│  │ - type, date, note            │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ groups, goals, payments, etc  │  │
│  └───────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

---

## External Service Integrations

### Twilio Integration
```
ExpensesIQ                Twilio API
    │                         │
    ├──→ POST /Messages      │
    │    {from: "+...",       │
    │     to: "+...",         │
    │     body: "OTP: 123456"}│
    │                         │
    ◀────────────────────────│
         {sid: "SM..."}       │
    │                         │
    └──→ SMS to User's Phone  │
         (actual SMS)         │
```

### OpenAI Integration
```
ExpensesIQ              OpenAI API
    │                      │
    ├──→ POST /chat/completions
    │    {model: "gpt-4o-mini",
    │     messages: [...]}
    │                      │
    ◀────────────────────────
         {choices: [{
            message: {
              content: "..."
            }
          }]}              │
```

---

## Authentication & Security

```
┌──────────────────────────────────┐
│    Authentication Flow           │
│                                  │
│  Public Endpoints (no auth):    │
│  ├─ POST /api/otp/send         │
│  └─ POST /api/otp/verify       │
│                                  │
│  Protected Endpoints (require login): │
│  ├─ POST /api/ai/chat          │
│  ├─ POST /api/ai/expense-advisor│
│  └─ GET  /api/ai/insights      │
│                                  │
│  Check: if 'user' not in session │
│  ├─→ Return 401 Unauthorized   │
│  └─→ Forward to login page      │
│                                  │
└──────────────────────────────────┘
```

---

## Data Flow Example: Complete User Journey

```
1. USER REGISTRATION
   User → /api/otp/send → OTP sent to phone → Verify with /api/otp/verify

2. USER LOGIN
   User → /login → Dashboard (authenticated)

3. ADD EXPENSES
   User → /dashboard → POST /add_transaction → DB saved

4. GET AI INSIGHTS
   User → /dashboard → GET /api/ai/insights
           ↓
           Fetch recent transactions
           ↓
           Send to OpenAI
           ↓
           Get financial insights
           ↓
           Display in dashboard

5. CHAT WITH AI
   User → "How to save money?" → POST /api/ai/expense-advisor
           ↓
           Fetch user transactions (context)
           ↓
           Send question + context to OpenAI
           ↓
           Get personalized advice
           ↓
           Display response
```

---

## Configuration & Environment

```
┌─────────────────────────────────────┐
│        Environment Setup            │
│                                     │
│  .env (not in git):                │
│  ├─ TWILIO_ACCOUNT_SID            │
│  ├─ TWILIO_AUTH_TOKEN             │
│  ├─ TWILIO_PHONE_NUMBER           │
│  └─ OPENAI_API_KEY                │
│                                     │
│  app.py:                           │
│  ├─ Reads from .env               │
│  ├─ Initializes services          │
│  └─ Registers API routes          │
│                                     │
│  Runtime:                          │
│  ├─ Check env vars present         │
│  ├─ Connect to external APIs       │
│  └─ Gracefully degrade if missing  │
│                                     │
└─────────────────────────────────────┘
```

---

## Error Handling & Fallbacks

```
┌─────────────────────────────────────┐
│    Error Handling Strategy          │
│                                     │
│  Missing Twilio Credentials:       │
│  └─→ OTP endpoint returns error    │
│  └─→ Other endpoints work normally │
│                                     │
│  Missing OpenAI API Key:           │
│  └─→ Chat endpoints return error   │
│  └─→ Insights generated without AI │
│                                     │
│  Database Error:                   │
│  └─→ Return 500 with error message │
│  └─→ Log error for debugging       │
│                                     │
│  Invalid Input:                    │
│  └─→ Return 400 with validation msg│
│                                     │
│  Auth Failure:                     │
│  └─→ Return 401 Unauthorized       │
│                                     │
└─────────────────────────────────────┘
```

---

## Scalability Considerations

```
Current Setup (Single Server):
├─ SQLite Database
├─ Single Python Process
└─ Direct API calls to Twilio/OpenAI
   └─ Latency: 1-5 seconds per request

Future Scalability:
├─ PostgreSQL Database
├─ Multiple Python Workers (Gunicorn)
├─ Redis Cache for OTPs
├─ Message Queue (Celery + RabbitMQ)
│  ├─ Async OTP sending
│  └─ Async AI requests
├─ Load Balancer (Nginx)
└─ CDN for static assets
   └─ Latency: <100ms for OTP, 1-2s for AI
```

---

This architecture is designed for:
- ✓ Easy to understand and maintain
- ✓ Secure credential management
- ✓ Graceful degradation
- ✓ Easy to scale
- ✓ Production-ready
