# SmartSpendAI

SmartSpendAI is a personal finance assistant that combines transaction tracking, spending analytics, and rule-based AI insights in a single experience. It provides a full-stack application with a FastAPI backend, MongoDB persistence, and a modern React frontend.

## Features

- **Secure authentication & dashboard** – Personalized landing page with quick stats and shortcuts.
- **Transaction management** – View, search, and generate sample transaction data per user.
- **Spending analytics** – Visualize category breakdowns and trends across time windows.
- **AI-powered insights** – Rule-driven recommendations that highlight savings opportunities and spending alerts.
- **File import pipeline** – Upload transactions from CSV or Excel sources with duplicate detection and auto-categorization.
- **UPI payment flow (preview)** – Generate UPI intent links for streamlined payments.

## Tech Stack

- **Backend:** FastAPI, Motor (MongoDB driver), Pydantic, Pandas
- **Frontend:** React 19 + Tailwind CSS + Lucide icons
- **Tooling:** CRACO, Axios, dotenv, httpx for testing

## Prerequisites

- Python 3.11+ (tested with 3.13)
- Node.js 18+
- A running MongoDB instance with connection details stored in `backend/.env`

## Quick Start

### 1. Backend

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Environment variables expected in `backend/.env`:

```dotenv
MONGO_URL=mongodb://localhost:27017
DB_NAME=smartspend
```

### 2. Frontend

```powershell
cd frontend
npm install
npm start
```

Configure the frontend backend URL in `frontend/.env` (example):

```dotenv
REACT_APP_BACKEND_URL=http://localhost:8000
```

## Importing Transactions from CSV/Excel

1. Sign in and navigate to **Import** from the sidebar.
2. Choose a `.csv`, `.xlsx`, or `.xls` file that includes at minimum `Date` and `Amount` columns.
3. Optionally keep duplicate detection enabled to skip previously imported records.
4. Review the import summary, then jump to the Transactions page to see the newly added entries.

The backend endpoint is available at `POST /api/transactions/import/{user_id}` and supports multipart uploads. A sample dataset is provided at `test_transactions.csv` for quick testing.

## Testing the Import API

You can validate the importer without running the server by leveraging FastAPI's `TestClient`:

```powershell
python -c "import os, sys, json; os.chdir('c:/Users/saira/smartspendai'); sys.path.append('backend'); from fastapi.testclient import TestClient; import server; client = TestClient(server.app); files={'file': ('test_transactions.csv', open('test_transactions.csv','rb'), 'text/csv')}; response = client.post('/api/transactions/import/test_user', files=files); print(json.dumps(response.json(), indent=2))"
```

## Useful Scripts

- `test_import.py` – Convenience script that posts `test_transactions.csv` to the running backend.
- `frontend/backend_test.py` – Example interactions against backend APIs (used for integration validation).

## Next Steps

- Integrate authentication with a persistent identity provider.
- Refine AI insights with machine learning models and historical trend data.
- Harden error handling and add end-to-end Cypress tests for the import workflow.
