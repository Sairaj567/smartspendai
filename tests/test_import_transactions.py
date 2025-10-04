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
    sample_path = Path(__file__).resolve().parent.parent / "test_transactions.csv"
    assert sample_path.exists(), "sample CSV file is missing"

    user_id = f"pytest_{uuid.uuid4().hex}"

    with sample_path.open("rb") as f:
        files = {"file": (sample_path.name, f, "text/csv")}
        response = client.post(f"/api/transactions/import/{user_id}", files=files)

    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["successful_imports"] == 10
    assert payload["failed_imports"] == 0
    assert payload["duplicate_count"] == 0
    assert len(payload["imported_transactions"]) == 10

    # spot check a couple of imported rows
    amounts = {tx["amount"] for tx in payload["imported_transactions"]}
    assert 250.0 in amounts
    assert 45000.0 in amounts
