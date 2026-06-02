import os
import json
import requests
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List


def generate_insights(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate basic insights from a list of transaction dicts.

    transactions: list of dict with keys: date, user, type, amount, category, note
    Returns a dict of insights. If OPENAI_API_KEY is set, it will attempt
    to call the OpenAI completion API as an optional enhancement (best-effort).
    """
    insights = {}

    if not transactions:
        insights['summary'] = 'No transactions available for insights.'
        insights['top_categories'] = []
        return insights

    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    insights['total_income'] = round(total_income, 2)
    insights['total_expense'] = round(total_expense, 2)
    insights['net'] = round(total_income - total_expense, 2)

    # Top categories
    categories = [t.get('category') or 'Uncategorized' for t in transactions if t['type'] == 'expense']
    cat_counts = Counter(categories)
    top = cat_counts.most_common(5)
    insights['top_categories'] = [{'category': c, 'count': n} for c, n in top]

    # Average daily spend (simple)
    dates = {}
    for t in transactions:
        d = t.get('date')
        try:
            day = datetime.fromisoformat(d).date()
        except Exception:
            continue
        dates.setdefault(day, 0)
        if t['type'] == 'expense':
            dates[day] += t['amount']

    if dates:
        avg_daily = sum(dates.values()) / len(dates)
        insights['avg_daily_expense'] = round(avg_daily, 2)
    else:
        insights['avg_daily_expense'] = 0

    # Simple tips
    tips = []
    if insights['avg_daily_expense'] > 1000:
        tips.append('Your average daily expense is high; consider reviewing recurring costs.')
    if top and top[0][1] > 3:
        tips.append(f"Top category: {top[0][0]} — try setting a budget for it.")

    insights['tips'] = tips

    # Optional: call an LLM if API key present (non-blocking enhancement)
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        try:
            prompt = (
                "Provide a short, actionable summary and 3 suggestions based on these numbers:\n"
                f"Total income: {insights['total_income']}, total expense: {insights['total_expense']}, net: {insights['net']}.\n"
            )
            resp = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 200
                },
                timeout=5
            )
            if resp.ok:
                j = resp.json()
                text = j['choices'][0]['message']['content']
                insights['ai_summary'] = text
        except Exception:
            # best-effort, ignore AI failure
            pass

    return insights


def chat_with_ai(messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
    """Chat with OpenAI using GPT model
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        system_prompt: Optional system prompt to set the AI behavior
    
    Returns:
        Dict with 'success', 'message' (the AI response), and optionally 'error'
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        return {
            'success': False,
            'error': 'OpenAI API key not configured. Set OPENAI_API_KEY environment variable.'
        }
    
    if not messages:
        return {
            'success': False,
            'error': 'No messages provided'
        }
    
    try:
        # Build messages with system prompt if provided
        request_messages = []
        if system_prompt:
            request_messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        request_messages.extend(messages)
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': request_messages,
                'max_tokens': 1000,
                'temperature': 0.7
            },
            timeout=30
        )
        
        if response.ok:
            data = response.json()
            message_content = data['choices'][0]['message']['content']
            return {
                'success': True,
                'message': message_content,
                'model': data.get('model'),
                'usage': data.get('usage')
            }
        else:
            error_text = response.text
            return {
                'success': False,
                'error': f'OpenAI API error: {error_text}'
            }
    
    except requests.Timeout:
        return {
            'success': False,
            'error': 'OpenAI API request timed out'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def get_expense_advisor_response(user_message: str, transactions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get financial advice from AI based on user's financial data
    
    Args:
        user_message: The user's question or request
        transactions: Optional list of user's transactions for context
    
    Returns:
        Dict with AI response
    """
    # Build context from transactions if provided
    context = ""
    if transactions:
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        context = f"\nUser's Financial Context:\n- Total Income: {total_income}\n- Total Expenses: {total_expense}\n- Net: {total_income - total_expense}"
    
    system_prompt = (
        "You are a helpful financial advisor for ExpensesIQ, an expense tracking application. "
        "Provide practical, actionable financial advice. Be concise but thorough. "
        "Focus on budgeting, expense management, and financial health."
    )
    
    messages = [
        {
            'role': 'user',
            'content': user_message + context
        }
    ]
    
    return chat_with_ai(messages, system_prompt)


def estimate_daily_saving_amount(goal_title: str, target_amount: float, current_saved: float, 
                                 due_date: str, avg_daily_expense: float = None, 
                                 monthly_income: float = None) -> Dict[str, Any]:
    """Estimate daily saving amount needed to reach goal using AI
    
    Args:
        goal_title: Title of the savings goal
        target_amount: Target amount to save
        current_saved: Amount already saved
        due_date: Target date in YYYY-MM-DD format
        avg_daily_expense: Optional average daily expense
        monthly_income: Optional monthly income for context
    
    Returns:
        Dict with 'success', 'daily_amount', 'recommendation', and other analysis
    """
    from datetime import datetime as dt
    
    try:
        # Calculate days remaining
        today = dt.now().date()
        target_date = dt.strptime(due_date, '%Y-%m-%d').date()
        days_remaining = (target_date - today).days
        
        if days_remaining <= 0:
            return {
                'success': False,
                'error': 'Target date has already passed'
            }
        
        # Calculate amount needed
        amount_needed = target_amount - current_saved
        
        if amount_needed <= 0:
            return {
                'success': True,
                'daily_amount': 0,
                'recommendation': f'Congratulations! You have already reached your goal of ₹{target_amount:,.2f}!'
            }
        
        # Calculate simple daily saving requirement
        daily_required = amount_needed / days_remaining
        
        # Use AI for intelligent recommendation
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            context = f"""
Goal: {goal_title}
Target Amount: ₹{target_amount:,.2f}
Already Saved: ₹{current_saved:,.2f}
Amount Needed: ₹{amount_needed:,.2f}
Days Remaining: {days_remaining} days
Simple Daily Requirement: ₹{daily_required:,.2f}
"""
            if avg_daily_expense:
                context += f"Average Daily Expense: ₹{avg_daily_expense:,.2f}\n"
            if monthly_income:
                context += f"Monthly Income: ₹{monthly_income:,.2f}\n"
            
            prompt = f"""Based on this savings goal information:
{context}

Provide a brief financial recommendation for achieving this goal. Consider:
1. Is the daily savings requirement realistic?
2. Any practical tips to achieve this goal?
3. A suggested daily saving amount (be practical and achievable)

Format your response as JSON with keys: "is_realistic" (boolean), "daily_amount" (number), "tips" (array of 2-3 strings), "summary" (string)
Only output valid JSON, no markdown formatting."""

            try:
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-4o-mini',
                        'messages': [{'role': 'user', 'content': prompt}],
                        'max_tokens': 300,
                        'temperature': 0.5
                    },
                    timeout=10
                )
                
                if response.ok:
                    data = response.json()
                    ai_response = data['choices'][0]['message']['content']
                    
                    # Parse JSON response
                    ai_recommendation = json.loads(ai_response)
                    
                    return {
                        'success': True,
                        'daily_amount': round(ai_recommendation.get('daily_amount', daily_required), 2),
                        'is_realistic': ai_recommendation.get('is_realistic', True),
                        'tips': ai_recommendation.get('tips', []),
                        'recommendation': ai_recommendation.get('summary', ''),
                        'simple_daily_requirement': round(daily_required, 2),
                        'days_remaining': days_remaining
                    }
            except (json.JSONDecodeError, KeyError, IndexError):
                # Fallback to simple calculation
                pass
        
        # Fallback: return simple calculation
        return {
            'success': True,
            'daily_amount': round(daily_required, 2),
            'simple_daily_requirement': round(daily_required, 2),
            'days_remaining': days_remaining,
            'recommendation': f'To reach your goal of ₹{target_amount:,.2f}, you need to save ₹{daily_required:,.2f} daily for the next {days_remaining} days.'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Error estimating daily amount: {str(e)}'
        }
