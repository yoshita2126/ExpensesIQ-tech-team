"""
API routes for OTP SMS and AI Chat features
"""

from flask import request, jsonify, session
from functools import wraps
import sqlite3
from services.otp_service import generate_otp, send_otp, store_otp, verify_otp, delete_otp
from services.ai_service import chat_with_ai, get_expense_advisor_response, estimate_daily_saving_amount


def require_login(f):
    """Decorator to require user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function


def register_api_routes(app):
    """Register all API routes"""
    
    # ===== OTP ENDPOINTS =====
    
    @app.route('/api/otp/send', methods=['POST'])
    def send_otp_endpoint():
        """Send OTP to email and/or phone for password reset
        
        Request JSON:
        {
            "email": "user@gmail.com",  # optional
            "phone": "+1234567890",     # optional (must include country code)
            "type": "password_reset"    # purpose of OTP
        }
        
        Response:
        {
            "success": true,
            "message": "OTP sent successfully",
            "results": {...}
        }
        """
        try:
            data = request.get_json() or {}
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            otp_type = data.get('type', 'password_reset')
            
            if not email and not phone:
                return jsonify({
                    'success': False,
                    'error': 'Email or phone number is required'
                }), 400
            
            # Generate OTP
            otp = generate_otp()
            
            # Send OTP
            send_results = send_otp(email=email, phone=phone, otp=otp)
            
            # Store OTP in database
            store_otp(email=email, phone=phone, otp=otp, expires_in_minutes=10)
            
            # Check if send succeeded
            if not send_results.get('success'):
                return jsonify({
                    'success': False,
                    'error': 'Failed to send OTP',
                    'details': send_results
                }), 500
            
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully',
                'sent_to': {
                    'email': email if email and email_success else None,
                    'phone': phone if phone and phone_success else None
                }
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Server error: {str(e)}'
            }), 500
    
    
    @app.route('/api/otp/verify', methods=['POST'])
    def verify_otp_endpoint():
        """Verify OTP sent to email or phone
        
        Request JSON:
        {
            "otp": "123456",
            "email": "user@gmail.com",  # either email or phone
            "phone": "+1234567890"      # either email or phone
        }
        
        Response:
        {
            "success": true,
            "message": "OTP verified successfully"
        }
        """
        try:
            data = request.get_json() or {}
            otp = data.get('otp', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            
            if not otp:
                return jsonify({
                    'success': False,
                    'error': 'OTP is required'
                }), 400
            
            if not email and not phone:
                return jsonify({
                    'success': False,
                    'error': 'Email or phone is required'
                }), 400
            
            # Verify OTP
            is_valid = verify_otp(otp=otp, email=email, phone=phone)
            
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': 'Invalid or expired OTP'
                }), 400
            
            # Delete OTP after verification
            delete_otp(email=email, phone=phone)
            
            return jsonify({
                'success': True,
                'message': 'OTP verified successfully'
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Server error: {str(e)}'
            }), 500
    
    
    # ===== AI CHAT ENDPOINTS =====
    
    @app.route('/api/ai/chat', methods=['POST'])
    @require_login
    def ai_chat_endpoint():
        """AI chat endpoint for general conversation
        
        Request JSON:
        {
            "messages": [
                {"role": "user", "content": "What's the best way to save money?"}
            ],
            "system_prompt": "You are a helpful financial advisor."  # optional
        }
        
        Response:
        {
            "success": true,
            "message": "AI response here...",
            "model": "gpt-4o-mini",
            "usage": {...}
        }
        """
        try:
            data = request.get_json() or {}
            messages = data.get('messages', [])
            system_prompt = data.get('system_prompt')
            
            if not messages:
                return jsonify({
                    'success': False,
                    'error': 'Messages are required'
                }), 400
            
            # Call AI service
            result = chat_with_ai(messages, system_prompt)
            
            if not result.get('success'):
                return jsonify(result), 500
            
            return jsonify(result), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Server error: {str(e)}'
            }), 500
    
    
    @app.route('/api/ai/expense-advisor', methods=['POST'])
    @require_login
    def expense_advisor_endpoint():
        """Get financial advice from AI based on user's message and transaction history
        
        Request JSON:
        {
            "message": "How can I reduce my expenses?"
        }
        
        Response:
        {
            "success": true,
            "message": "Detailed financial advice..."
        }
        """
        try:
            user = session.get('user')
            data = request.get_json() or {}
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return jsonify({
                    'success': False,
                    'error': 'Message is required'
                }), 400
            
            # Fetch user's transactions for context
            try:
                conn = sqlite3.connect('data.db')
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                
                # Get user's group and transactions
                cur.execute('SELECT group_name FROM users WHERE username = ?', (user,))
                user_row = cur.fetchone()
                if not user_row:
                    conn.close()
                    return jsonify({
                        'success': False,
                        'error': 'User not found'
                    }), 404
                
                group_name = user_row['group_name']
                
                # Get recent transactions
                cur.execute(
                    '''SELECT date, type, amount, category, note 
                       FROM transactions 
                       WHERE group_name = ? 
                       ORDER BY date DESC LIMIT 100''',
                    (group_name,)
                )
                
                transactions = [dict(row) for row in cur.fetchall()]
                conn.close()
            
            except Exception as db_err:
                print(f"Database error: {db_err}")
                transactions = []
            
            # Get AI response
            result = get_expense_advisor_response(user_message, transactions)
            
            if not result.get('success'):
                return jsonify(result), 500
            
            return jsonify(result), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Server error: {str(e)}'
            }), 500
    
    
    @app.route('/api/ai/insights', methods=['GET'])
    @require_login
    def get_ai_insights():
        """Get AI-generated insights from recent transactions
        
        Response:
        {
            "success": true,
            "insights": {
                "total_income": 50000,
                "total_expense": 30000,
                "net": 20000,
                "ai_summary": "You're doing well financially...",
                "tips": [...]
            }
        }
        """
        try:
            from services.ai_service import generate_insights
            user = session.get('user')
            
            # Fetch user's transactions
            try:
                conn = sqlite3.connect('data.db')
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                
                cur.execute('SELECT group_name FROM users WHERE username = ?', (user,))
                user_row = cur.fetchone()
                if not user_row:
                    conn.close()
                    return jsonify({
                        'success': False,
                        'error': 'User not found'
                    }), 404
                
                group_name = user_row['group_name']
                
                cur.execute(
                    '''SELECT date, user, type, amount, category, note 
                       FROM transactions 
                       WHERE group_name = ?''',
                    (group_name,)
                )
                
                transactions = [dict(row) for row in cur.fetchall()]
                conn.close()
            
            except Exception as db_err:
                print(f"Database error: {db_err}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to fetch transactions'
                }), 500
            
            # Generate insights
            insights = generate_insights(transactions)
            
            return jsonify({
                'success': True,
                'insights': insights
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Server error: {str(e)}'
            }), 500
    
    
    @app.route('/api/goals/estimate-daily-amount', methods=['POST'])
    @require_login
    def estimate_goal_daily_amount():
        """Estimate daily saving amount for a goal using AI
        
        Request JSON:
        {
            "goal_title": "Emergency Fund",
            "target_amount": 100000,
            "current_saved": 25000,
            "due_date": "2026-12-31",
            "include_expense_context": true  # optional - includes user's avg expense
        }
        
        Response:
        {
            "success": true,
            "daily_amount": 250.5,
            "recommendation": "AI-generated recommendation",
            "tips": [...],
            "days_remaining": 214,
            "is_realistic": true
        }
        """
        try:
            data = request.get_json() or {}
            goal_title = data.get('goal_title', '').strip()
            target_amount = data.get('target_amount')
            current_saved = data.get('current_saved', 0)
            due_date = data.get('due_date', '').strip()
            include_context = data.get('include_expense_context', True)
            
            # Validate required fields
            if not goal_title or not target_amount or not due_date:
                return jsonify({
                    'success': False,
                    'error': 'goal_title, target_amount, and due_date are required'
                }), 400
            
            try:
                target_amount = float(target_amount)
                current_saved = float(current_saved)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'target_amount and current_saved must be numbers'
                }), 400
            
            # Fetch user's expense context if requested
            avg_daily_expense = None
            monthly_income = None
            
            if include_context:
                try:
                    user = session.get('user')
                    conn = sqlite3.connect('data.db')
                    conn.row_factory = sqlite3.Row
                    cur = conn.cursor()
                    
                    # Get user's group
                    cur.execute('SELECT group_name FROM users WHERE username = ?', (user,))
                    user_row = cur.fetchone()
                    
                    if user_row:
                        group_name = user_row['group_name']
                        
                        # Get recent transactions for context
                        cur.execute(
                            '''SELECT date, type, amount 
                               FROM transactions 
                               WHERE group_name = ? AND type = 'expense'
                               ORDER BY date DESC LIMIT 100''',
                            (group_name,)
                        )
                        
                        transactions = cur.fetchall()
                        if transactions:
                            # Calculate average daily expense
                            daily_expenses = {}
                            for txn in transactions:
                                date_str = txn['date']
                                daily_expenses.setdefault(date_str, 0)
                                daily_expenses[date_str] += txn['amount']
                            
                            if daily_expenses:
                                avg_daily_expense = sum(daily_expenses.values()) / len(daily_expenses)
                    
                    conn.close()
                except Exception as db_err:
                    print(f"Warning: Could not fetch expense context: {db_err}")
            
            # Estimate daily amount using AI
            result = estimate_daily_saving_amount(
                goal_title=goal_title,
                target_amount=target_amount,
                current_saved=current_saved,
                due_date=due_date,
                avg_daily_expense=avg_daily_expense,
                monthly_income=monthly_income
            )
            
            if not result.get('success'):
                return jsonify(result), 400
            
            return jsonify(result), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Server error: {str(e)}'
            }), 500
