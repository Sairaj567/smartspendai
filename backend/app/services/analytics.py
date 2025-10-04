from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from ..utils import normalize_investment_category


def aggregate_spending_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    def _resolved_category(tx: Dict[str, Any]) -> str:
        return normalize_investment_category(
            tx.get('category'),
            tx.get('description'),
            tx.get('merchant'),
            tx.get('type'),
        )

    def _is_investment(tx: Dict[str, Any]) -> bool:
        category = _resolved_category(tx).strip().lower()
        return category in {'investment', 'investments'}

    total_expenses = sum(tx['amount'] for tx in transactions if tx.get('type') == 'expense')
    total_income = sum(tx['amount'] for tx in transactions if tx.get('type') == 'income')
    invested_amount = sum(tx['amount'] for tx in transactions if _is_investment(tx))
    investment_transactions = sum(1 for tx in transactions if _is_investment(tx))

    category_spending: Dict[str, float] = {}
    for tx in transactions:
        category = _resolved_category(tx)
        if tx.get('type') == 'expense':
            category_spending[category] = category_spending.get(category, 0) + tx['amount']

    top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
    investment_percentage = (
        round((invested_amount / total_expenses) * 100, 1)
        if total_expenses > 0 and invested_amount > 0
        else 0
    )

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
        "category_breakdown": {cat: round(amount, 2) for cat, amount in category_spending.items()},
        "invested_amount": round(invested_amount, 2),
        "investment_transaction_count": investment_transactions,
        "investment_category": {
            "category": "Investments",
            "amount": round(invested_amount, 2),
            "percentage": investment_percentage,
        } if invested_amount > 0 else None,
    }


def build_spending_trends(
    transactions: List[Dict[str, Any]],
    days: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    computed_start = start_date or (datetime.now(timezone.utc) - timedelta(days=days))
    computed_end = end_date or datetime.now(timezone.utc)

    if computed_start.tzinfo is None:
        computed_start = computed_start.replace(tzinfo=timezone.utc)
    else:
        computed_start = computed_start.astimezone(timezone.utc)

    if computed_end.tzinfo is None:
        computed_end = computed_end.replace(tzinfo=timezone.utc)
    else:
        computed_end = computed_end.astimezone(timezone.utc)

    if computed_end < computed_start:
        computed_end = computed_start

    start_of_window = computed_start.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_window = computed_end.replace(hour=0, minute=0, second=0, microsecond=0)
    start_day = start_of_window.date()
    end_day = end_of_window.date()

    daily_spending: Dict[str, float] = {}
    for tx in transactions:
        txn_date = tx.get('date')
        if not isinstance(txn_date, datetime):
            continue
        if txn_date.tzinfo is None:
            txn_date = txn_date.replace(tzinfo=timezone.utc)
        else:
            txn_date = txn_date.astimezone(timezone.utc)
        txn_day = txn_date.date()
        if txn_day < start_day or txn_day > end_day:
            continue
        if tx.get('type') != 'expense':
            continue

        date_key = txn_day.isoformat()
        daily_spending[date_key] = daily_spending.get(date_key, 0) + tx['amount']

    trends: List[Dict[str, Any]] = []
    current_date = start_of_window
    while current_date <= end_of_window:
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
