import asyncio
import types
from typing import Optional
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.routes import analytics as analytics_route


class FakeCursor:
    def __init__(self, documents):
        self._documents = list(documents)

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):  # noqa: ARG002
        return list(self._documents)


class FakeCollection:
    def __init__(self, documents):
        self._documents = documents
        self.last_query = None

    def find(self, query):
        self.last_query = query
        min_iso = query.get("date", {}).get("$gte")
        max_iso = query.get("date", {}).get("$lt")

        def _within_range(doc):
            doc_dt = datetime.fromisoformat(doc["date"].replace("Z", "+00:00"))
            if min_iso:
                min_dt = datetime.fromisoformat(min_iso.replace("Z", "+00:00"))
                if doc_dt < min_dt:
                    return False
            if max_iso:
                max_dt = datetime.fromisoformat(max_iso.replace("Z", "+00:00"))
                if doc_dt >= max_dt:
                    return False
            return True

        filtered = [doc for doc in self._documents if _within_range(doc)]
        return FakeCursor(filtered)


def run_async(coro):
    return asyncio.run(coro)


def build_transaction(
    amount: float,
    txn_type: str,
    offset_days: int,
    *,
    merchant: str = "Test",
    description: str = "Test transaction",
    category: Optional[str] = None,
) -> dict:
    now = datetime.now(timezone.utc)
    if txn_type == "expense":
        category_value = category or "Others"
        txn_type_value = "expense"
    elif txn_type == "income":
        category_value = category or "Income"
        txn_type_value = "income"
    else:
        category_value = category or "Investments"
        txn_type_value = "expense"
    return {
        "_id": f"mongo-{txn_type}-{offset_days}",
        "id": f"txn-{txn_type}-{offset_days}",
        "user_id": "user123",
        "amount": amount,
        "category": category_value,
        "description": description,
        "merchant": merchant,
        "date": (now - timedelta(days=offset_days)).isoformat(),
        "type": txn_type_value,
        "payment_method": "UPI",
    }


def test_get_spending_summary_respects_days(monkeypatch):
    documents = [
        build_transaction(1000, "expense", offset_days=10),
        build_transaction(500, "income", offset_days=5),
        build_transaction(2000, "expense", offset_days=120),
    ]
    fake_db = types.SimpleNamespace(transactions=FakeCollection(documents))
    monkeypatch.setattr(analytics_route, "db", fake_db, raising=False)

    result = run_async(analytics_route.get_spending_summary("user123", days=30))

    assert fake_db.transactions.last_query["date"]["$gte"]
    assert result["total_expenses"] == 1000
    assert result["total_income"] == 500
    assert result["transaction_count"] == 2
    assert result["monthly_savings"] == 0
    assert result["emergency_fund_target"] == 6000
    assert result["emergency_monthly_contribution"] == 1000


def test_get_spending_summary_supports_year_range(monkeypatch):
    documents = [
        build_transaction(1200, "expense", offset_days=30),
        build_transaction(700, "income", offset_days=180),
        build_transaction(900, "expense", offset_days=200),
    ]
    fake_db = types.SimpleNamespace(transactions=FakeCollection(documents))
    monkeypatch.setattr(analytics_route, "db", fake_db, raising=False)

    result = run_async(analytics_route.get_spending_summary("user123", days=365))

    assert fake_db.transactions.last_query["date"]["$gte"]
    assert result["total_expenses"] == 2100
    assert result["total_income"] == 700
    assert result["transaction_count"] == 3
    assert "monthly_savings" in result
    assert result["monthly_savings"] == 0
    assert result["emergency_fund_target"] > 0


def test_get_spending_summary_rejects_invalid_days():
    with pytest.raises(Exception) as exc_info:
        run_async(analytics_route.get_spending_summary("user123", days=0))
    assert hasattr(exc_info.value, "status_code") and exc_info.value.status_code == 400


def test_get_spending_summary_normalizes_groww_transactions(monkeypatch):
    documents = [
        build_transaction(
            1800,
            "expense",
            offset_days=3,
            merchant="ICCL Groww",
            description="Groww SIP purchase",
            category="Others",
        )
    ]
    fake_db = types.SimpleNamespace(transactions=FakeCollection(documents))
    monkeypatch.setattr(analytics_route, "db", fake_db, raising=False)

    result = run_async(analytics_route.get_spending_summary("user123", days=30))

    assert result["invested_amount"] == 1800
    assert result["investment_transaction_count"] == 1
    assert result["category_breakdown"].get("Investments") == 1800


def test_get_spending_summary_supports_named_timeframe(monkeypatch):
    documents = [
        build_transaction(1500, "expense", offset_days=10),
        build_transaction(900, "expense", offset_days=45),
    ]
    fake_collection = FakeCollection(documents)
    fake_db = types.SimpleNamespace(transactions=fake_collection)
    monkeypatch.setattr(analytics_route, "db", fake_db, raising=False)

    window = {
        "key": "last_month",
        "label": "Last Month",
        "start": datetime(2024, 9, 1, tzinfo=timezone.utc),
        "end": datetime(2024, 10, 1, tzinfo=timezone.utc),
        "inclusive_end": datetime(2024, 9, 30, 23, 59, tzinfo=timezone.utc),
        "days": 30,
    }

    monkeypatch.setattr(
        analytics_route,
        "resolve_timeframe_window",
        lambda _: window,
        raising=False,
    )

    run_async(analytics_route.get_spending_summary("user123", timeframe="last_month"))

    assert fake_collection.last_query["date"]["$gte"] == window["start"].isoformat()
    assert fake_collection.last_query["date"]["$lt"] == window["end"].isoformat()


def test_get_spending_trends_honors_timeframe(monkeypatch):
    documents = [
        build_transaction(1200, "expense", offset_days=5),
        build_transaction(800, "expense", offset_days=35),
    ]
    fake_collection = FakeCollection(documents)
    fake_db = types.SimpleNamespace(transactions=fake_collection)
    monkeypatch.setattr(analytics_route, "db", fake_db, raising=False)

    window = {
        "key": "3_months",
        "label": "Last 3 Months",
        "start": datetime(2024, 8, 1, tzinfo=timezone.utc),
        "end": datetime(2024, 11, 1, tzinfo=timezone.utc),
        "inclusive_end": datetime(2024, 10, 31, 23, 59, tzinfo=timezone.utc),
        "days": 92,
    }

    captured = {}

    def fake_build_spending_trends(transactions, days, start_date=None, end_date=None):
        captured["transactions"] = transactions
        captured["days"] = days
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        return {"trends": [], "average_daily_spending": 0}

    monkeypatch.setattr(
        analytics_route,
        "resolve_timeframe_window",
        lambda _: window,
        raising=False,
    )
    monkeypatch.setattr(
        analytics_route,
        "build_spending_trends",
        fake_build_spending_trends,
        raising=False,
    )

    run_async(analytics_route.get_spending_trends("user123", timeframe="3_months"))

    assert fake_collection.last_query["date"]["$gte"] == window["start"].isoformat()
    assert fake_collection.last_query["date"]["$lt"] == window["end"].isoformat()
    assert captured["days"] == window["days"]
    assert captured["start_date"] == window["start"]
    assert captured["end_date"] == window["inclusive_end"]