import asyncio
import types
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
        if min_iso is None:
            filtered = list(self._documents)
        else:
            min_dt = datetime.fromisoformat(min_iso.replace("Z", "+00:00"))
            filtered = [
                doc
                for doc in self._documents
                if datetime.fromisoformat(doc["date"].replace("Z", "+00:00")) >= min_dt
            ]
        return FakeCursor(filtered)


def run_async(coro):
    return asyncio.run(coro)


def build_transaction(amount: float, txn_type: str, offset_days: int) -> dict:
    now = datetime.now(timezone.utc)
    if txn_type == "expense":
        category, txn_type_value = "Others", "expense"
    elif txn_type == "income":
        category, txn_type_value = "Income", "income"
    else:
        category, txn_type_value = "Investments", "expense"
    return {
        "_id": f"mongo-{txn_type}-{offset_days}",
        "id": f"txn-{txn_type}-{offset_days}",
        "user_id": "user123",
        "amount": amount,
        "category": category,
        "description": "Test transaction",
        "merchant": "Test",
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
    assert result["total_expenses"] == 1200
    assert result["total_income"] == 700
    assert result["transaction_count"] == 2


def test_get_spending_summary_rejects_invalid_days():
    with pytest.raises(Exception) as exc_info:
        run_async(analytics_route.get_spending_summary("user123", days=0))
    assert hasattr(exc_info.value, "status_code") and exc_info.value.status_code == 400