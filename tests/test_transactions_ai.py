import asyncio
import types
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from backend.app.models import Transaction, TransactionCreate
from backend.app.routes import transactions as transactions_route


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
