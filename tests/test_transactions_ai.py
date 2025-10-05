import asyncio
import types
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from backend.app.models import Transaction, TransactionCreate
from backend.app.routes import transactions as transactions_route
from backend.app.services import insights as insights_service
from backend.app.services import openrouter_classifier


def test_create_transaction_uses_ai_classification(monkeypatch):
    async def run_test():
        insert_one_mock = AsyncMock()
        fake_db = types.SimpleNamespace(
            transactions=types.SimpleNamespace(insert_one=insert_one_mock)
        )
        monkeypatch.setattr(transactions_route, "db", fake_db, raising=False)

        classifier_mock = AsyncMock(return_value="Food & Dining")
        monkeypatch.setattr(
            transactions_route,
            "classify_transaction_via_openrouter",
            classifier_mock,
            raising=False,
        )

        transaction_create = TransactionCreate(
            user_id="user123",
            amount=250.0,
            category="Others",
            description="Dinner at Subway",
            merchant="Subway",
            type="expense",
            payment_method="UPI",
        )

        result = await transactions_route.create_transaction(transaction_create)

        assert result.category == "Food & Dining"
        classifier_mock.assert_awaited_once()
        assert insert_one_mock.await_count == 1
        inserted_doc = insert_one_mock.await_args.args[0]
        assert inserted_doc["category"] == "Food & Dining"

    asyncio.run(run_test())


def test_import_transactions_enriches_categories(monkeypatch):
    async def run_test():
        inserted_documents = []

        async def fake_insert_many(documents):
            inserted_documents.extend(documents)

        fake_collection = types.SimpleNamespace(
            find_one=AsyncMock(return_value=None),
            insert_many=AsyncMock(side_effect=fake_insert_many),
        )
        fake_db = types.SimpleNamespace(transactions=fake_collection)
        monkeypatch.setattr(transactions_route, "db", fake_db, raising=False)

        async def fake_enrich(transactions, allow_override=False):
            for tx in transactions:
                tx.category = "Travel"

        enrich_mock = AsyncMock(side_effect=fake_enrich)
        monkeypatch.setattr(transactions_route, "enrich_transactions_with_ai", enrich_mock)

        def fake_parse_csv(content, user_id):
            tx = Transaction(
                user_id=user_id,
                amount=100.0,
                category="Others",
                description="Uber ride",
                merchant="Uber",
                date=datetime.now(timezone.utc),
                type="expense",
                payment_method="UPI",
                location="Bangalore",
            )
            return [tx], []

        monkeypatch.setattr(transactions_route, "parse_csv_transactions", fake_parse_csv)

        class DummyUploadFile:
            def __init__(self, filename: str, data: bytes):
                self.filename = filename
                self._data = data

            async def read(self) -> bytes:
                return self._data

        upload_file = DummyUploadFile("transactions.csv", b"id,amount\n1,100")

        result = await transactions_route.import_transactions(
            "user456", upload_file, skip_duplicates=True
        )

        enrich_mock.assert_awaited_once()
        assert result.imported_transactions
        assert result.imported_transactions[0].category == "Travel"
        assert inserted_documents
        assert inserted_documents[0]["category"] == "Travel"

    asyncio.run(run_test())


def test_enrich_transactions_with_ai_batches(monkeypatch):
    async def run_test():
        monkeypatch.setattr(openrouter_classifier, "openrouter_available", lambda: True)

        captured_batches = []

        async def fake_bulk(entries, *, batch_size=25):
            captured_batches.append((len(entries), batch_size))
            return {entry["id"]: "Shopping" for entry in entries}

        monkeypatch.setattr(openrouter_classifier, "classify_transactions_via_openrouter_bulk", fake_bulk)

        transactions = [
            Transaction(
                user_id="user789",
                amount=100 + index,
                category="Others",
                description=f"Purchase {index}",
                merchant="Test Store",
                date=datetime.now(timezone.utc),
                type="expense",
                payment_method="UPI",
            )
            for index in range(30)
        ]

        updated = await openrouter_classifier.enrich_transactions_with_ai(transactions, allow_override=True)

        assert captured_batches, "Bulk classifier was not invoked"
        batch_lengths = {length for length, _ in captured_batches}
        assert batch_lengths == {30}
        assert all(tx.category == "Shopping" for tx in transactions)
        assert len(updated) == len(transactions)

    asyncio.run(run_test())


def test_generate_spending_insights_includes_emergency(monkeypatch):
    async def run_test():
        monkeypatch.setattr(insights_service, "openrouter_available", lambda: False)

        summary = {
            "total_expenses": 60000,
            "total_income": 90000,
            "net_savings": 30000,
            "monthly_savings": 10000,
            "transaction_count": 12,
            "top_categories": [],
            "category_breakdown": {},
            "invested_amount": 5000,
            "investment_transaction_count": 1,
            "investment_category": None,
            "emergency_fund_target": 360000,
            "emergency_monthly_contribution": 60000,
        }
        trends = {"average_daily_spending": 2000, "trends": []}

        insights = await insights_service.generate_spending_insights(
            summary,
            trends,
            user_id="user123",
            timeframe="3_months",
            timeframe_label="Last 3 Months",
        )

        assert any("Emergency" in insight["title"] for insight in insights)

    asyncio.run(run_test())
