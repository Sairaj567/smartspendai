from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


def aggregate_spending_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_expenses = sum(tx['amount'] for tx in transactions if tx.get('type') == 'expense')
    total_income = sum(tx['amount'] for tx in transactions if tx.get('type') == 'income')

    category_spending: Dict[str, float] = {}
    for tx in transactions:
        if tx.get('type') == 'expense':
            category = tx.get('category') or 'Uncategorized'
            category_spending[category] = category_spending.get(category, 0) + tx['amount']

    top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_expenses": round(total_expenses, 2),
        "total_income": round(total_income, 2),
        "net_savings": round(total_income - total_expenses, 2),
        "transaction_count": len(transactions),
        "top_categories": [
            {
                "category": cat,
                "amount": round(amount, 2),
                "percentage": round((amount / total_expenses) * 100, 1) if total_expenses > 0 else 0
            }
            for cat, amount in top_categories
        ],
        "category_breakdown": {cat: round(amount, 2) for cat, amount in category_spending.items()}
    }


def build_spending_trends(transactions: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    daily_spending: Dict[str, float] = {}
    for tx in transactions:
        txn_date = tx.get('date')
        if not isinstance(txn_date, datetime):
            continue
        if txn_date < start_date:
            continue
        if tx.get('type') != 'expense':
            continue

        date_key = txn_date.strftime('%Y-%m-%d')
        daily_spending[date_key] = daily_spending.get(date_key, 0) + tx['amount']

    trends: List[Dict[str, Any]] = []
    current_date = start_date
    while current_date <= datetime.now(timezone.utc):
        date_key = current_date.strftime('%Y-%m-%d')
        trends.append({
            "date": date_key,
            "amount": round(daily_spending.get(date_key, 0), 2)
        })
        current_date += timedelta(days=1)

    average_daily_spending = round(sum(daily_spending.values()) / len(trends), 2) if trends else 0

    return {
        "trends": trends,
        "average_daily_spending": average_daily_spending
    }
