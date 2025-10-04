import sys
from pathlib import Path

import uuid

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.append(str(BACKEND_PATH))

server = __import__("server")


@pytest.fixture(scope="module")
def client():
    return TestClient(server.app)


def test_import_transactions_success(client):
    sample_path = Path(__file__).resolve().parent / "data" / "sample_transactions.csv"
    assert sample_path.exists(), "sample CSV file is missing"

    user_id = f"pytest_{uuid.uuid4().hex}"

    with sample_path.open("rb") as f:
        files = {"file": (sample_path.name, f, "text/csv")}
        response = client.post(f"/api/transactions/import/{user_id}", files=files)

    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["successful_imports"] == 8
    assert payload["failed_imports"] == 0
    assert payload["duplicate_count"] == 0
    assert len(payload["imported_transactions"]) == 8

    imported = payload["imported_transactions"]
    cheque_rows = [tx for tx in imported if "(Chq:" in tx["description"]]
    assert len(cheque_rows) == 3

    income_amounts = {tx["amount"] for tx in imported if tx["type"] == "income"}
    assert income_amounts == {75000.0, 5000.0, 15000.0}

    expense_amounts = {tx["amount"] for tx in imported if tx["type"] == "expense"}
    assert 25000.0 in expense_amounts
    assert 8500.0 in expense_amounts


def test_import_bank_statement_headers(client):
    sample_path = Path(__file__).resolve().parent / "data" / "bank_statement.csv"
    assert sample_path.exists(), "bank statement CSV missing"

    user_id = f"pytest_{uuid.uuid4().hex}"

    with sample_path.open("rb") as f:
        files = {"file": (sample_path.name, f, "text/csv")}
        response = client.post(f"/api/transactions/import/{user_id}", files=files)

    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["successful_imports"] == 4
    assert payload["failed_imports"] == 0

    imported = payload["imported_transactions"]
    assert any(tx["description"].endswith("(Chq: 123456)") for tx in imported)
    assert any(tx["type"] == "income" and tx["amount"] == 60000.0 for tx in imported)
    assert any(tx["type"] == "expense" and tx["amount"] == 15000.0 for tx in imported)


def test_import_real_account_statement(client):
    sample_path = Path(__file__).resolve().parent.parent / "Account_stmt_XX2387_04102025.csv"
    assert sample_path.exists(), "account statement CSV missing"

    user_id = f"pytest_{uuid.uuid4().hex}"

    with sample_path.open("rb") as f:
        files = {"file": (sample_path.name, f, "text/csv")}
        response = client.post(f"/api/transactions/import/{user_id}", files=files)

    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["successful_imports"] == 65
    assert payload["failed_imports"] == 0

    imported = payload["imported_transactions"]
    # Ensure both income and expense transactions are captured
    assert any(tx["type"] == "income" for tx in imported)
    assert any(tx["type"] == "expense" for tx in imported)

    # Verify multi-line descriptions and cheque numbers are preserved in at least one transaction
    assert any("Valve Corporation" in tx["description"] for tx in imported)
    assert any("ICCL GROW" in tx["description"] for tx in imported)
