import asyncio
import types
from datetime import datetime, timezone

from backend.app.routes import transactions as transactions_route


class FakeCursor:
    def __init__(self, documents):
        self._documents = list(documents)
        self._limit = None

    def sort(self, *args, **kwargs):
        return self

    def limit(self, value):
        if value and value > 0:
            self._limit = value
        else:
            self._limit = None
        return self

    async def to_list(self, length=None):
        if self._limit is None:
            return list(self._documents)
        return list(self._documents[: self._limit])


class FakeCollection:
    def __init__(self, documents):
        self._documents = documents

    def find(self, query):
        return FakeCursor(self._documents)


def build_documents(count: int):
    base_date = datetime.now(timezone.utc).isoformat()
    documents = []
    for idx in range(count):
        documents.append(
            {
                "_id": f"mongo{idx}",
                "id": f"txn{idx}",
                "user_id": "user123",
                "amount": float(idx + 1),
                "category": "Others",
                "description": f"Transaction {idx}",
                "merchant": "Merchant",
                "date": base_date,
                "type": "expense",
                "payment_method": "UPI",
            }
        )
    return documents


def run_async(coro):
    return asyncio.run(coro)


def test_get_user_transactions_default_returns_all(monkeypatch):
    documents = build_documents(120)
    fake_db = types.SimpleNamespace(transactions=FakeCollection(documents))
    monkeypatch.setattr(transactions_route, "db", fake_db, raising=False)

    result = run_async(transactions_route.get_user_transactions("user123"))
    assert len(result) == 120


def test_get_user_transactions_no_limit(monkeypatch):
    documents = build_documents(175)
    fake_db = types.SimpleNamespace(transactions=FakeCollection(documents))
    monkeypatch.setattr(transactions_route, "db", fake_db, raising=False)

    result = run_async(transactions_route.get_user_transactions("user123", limit=0))
    assert len(result) == 175


def test_get_user_transactions_custom_limit(monkeypatch):
    documents = build_documents(175)
    fake_db = types.SimpleNamespace(transactions=FakeCollection(documents))
    monkeypatch.setattr(transactions_route, "db", fake_db, raising=False)

    result = run_async(transactions_route.get_user_transactions("user123", limit=120))
    assert len(result) == 120
