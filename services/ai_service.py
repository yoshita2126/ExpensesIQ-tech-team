import os
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
