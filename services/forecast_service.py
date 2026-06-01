from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List


def forecast_monthly_expense(transactions: List[Dict[str, Any]], months: int = 3) -> Dict[str, Any]:
    """Simple monthly expense forecast based on historical averages.

    transactions: list of dict with keys date (ISO), type, amount
    Returns projected totals for next `months` months.
    """
    # Aggregate by month-year
    monthly = defaultdict(float)
    for t in transactions:
        if t.get('type') != 'expense':
            continue
        d = t.get('date')
        try:
            dt = datetime.fromisoformat(d)
        except Exception:
            continue
        key = (dt.year, dt.month)
        monthly[key] += t.get('amount', 0)

    if not monthly:
        return {'forecast': []}

    # Compute average monthly expense
    avg = sum(monthly.values()) / len(monthly)

    # Simple projection: next `months` months equal to avg
    forecast = []
    for i in range(1, months+1):
        forecast.append({'month_offset': i, 'projected_expense': round(avg, 2)})

    return {'forecast': forecast, 'average_monthly_expense': round(avg,2)}
