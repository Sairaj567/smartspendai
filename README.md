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

## Backend Architecture

The FastAPI service is split into focused modules inside `backend/app`:

- `app/main.py` – App factory that wires middleware, routers, and lifecycle events.
- `app/config.py` – Environment loading and shared logging configuration.
- `app/database.py` – Lazy MongoDB client management with graceful shutdown handling.
- `app/models.py` – Pydantic schemas shared across routes.
- `app/services/` – Business logic helpers (analytics, insights, mock data generators).
- `app/routes/` – Feature-specific routers for transactions, analytics, AI insights, and payments.
- `app/utils.py` – CSV parsing, Mongo document serialization, and categorization helpers.

`backend/server.py` now simply instantiates the app via `create_app()`, making it easier to test and extend.

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
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_APP_URL=http://localhost:3000
OPENROUTER_APP_NAME=SmartSpendAI
EMERGENCY_FUND_MULTIPLIER=6
```

> `OPENROUTER_API_KEY` is optional—when omitted, the importer falls back to rule-based categorization. The additional values let OpenRouter attribute traffic from your app and may be left at their defaults in development.
> `EMERGENCY_FUND_MULTIPLIER` adjusts the emergency fund target (in months of average expenses). Set it to `3` or `4` if you prefer a smaller cushion.

### 2. Frontend

```powershell
cd frontend
npm install
npm start
```

Configure the frontend backend URL in `frontend/.env` (example):

```dotenv
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_TRANSACTION_FETCH_LIMIT=0
```

> `REACT_APP_TRANSACTION_FETCH_LIMIT` lets you cap the number of transactions fetched per request. Set it to `0` (default) to load the full history, or provide a positive integer for lightweight views on resource-constrained devices.

## Importing Transactions from CSV/Excel

1. Sign in and navigate to **Import** from the sidebar.
2. Choose a `.csv`, `.xlsx`, or `.xls` file that includes at minimum `Date` and `Amount` columns.
3. Optionally keep duplicate detection enabled to skip previously imported records.
4. Review the import summary, then jump to the Transactions page to see the newly added entries.

The backend endpoint is available at `POST /api/transactions/import/{user_id}` and supports multipart uploads. A sample dataset is provided at `test_transactions.csv` for quick testing.

> Bank statement exports that ship with headers such as `Tran Date`, `Chq No`, `Particulars`, `Debit`, `Credit`, `Balance`, and `Init. Br` are also recognized—dates are parsed automatically, cheque numbers are preserved in the description, and the importer classifies debits as expenses and credits as income. Files that arrive with a UTF-8 BOM, trailing blank columns, or multi-line descriptions (the common format for bank-generated CSVs) import without any additional cleanup.

### AI-Powered Categorization

When an OpenRouter API key is configured, SmartSpendAI upgrades "Others" or "Auto" categories using an LLM-backed classifier. Both the bulk importer and the single-transaction endpoint now invoke the classifier automatically after the rule-based heuristics run, so manual entries are refined the same way as file uploads. The importer batches asynchronous calls and caches results for a day to control latency. To fall back to heuristic-only categorisation, simply omit the OpenRouter credentials from your environment.

> **Transaction history endpoint**: `GET /api/transactions/{user_id}` now returns the full dataset by default. Pass a positive `limit` query parameter if you want to page or trim the result set (for example, `/api/transactions/demo?limit=100`).

> **Analytics endpoints**: Both `GET /api/analytics/spending-summary/{user_id}` and `GET /api/analytics/spending-trends/{user_id}` accept a `days` query parameter. The frontend selector simply forwards this value so switching from 30 days to 3 months updates every metric (total income, expenses, net savings, investments) in step. Values must be positive; the API will return `400` for invalid ranges.

## Testing the Import API

You can validate the importer without running the server by leveraging FastAPI's `TestClient`:

```powershell
python -c "import os, sys, json; os.chdir('c:/Users/saira/smartspendai'); sys.path.append('backend'); from fastapi.testclient import TestClient; import server; client = TestClient(server.app); files={'file': ('test_transactions.csv', open('test_transactions.csv','rb'), 'text/csv')}; response = client.post('/api/transactions/import/test_user', files=files); print(json.dumps(response.json(), indent=2))"
```

Or run the automated pytest that exercises the same workflow end-to-end:

```powershell
python -m pytest tests/test_import_transactions.py
```

## Useful Scripts

- `test_import.py` – Convenience script that posts `test_transactions.csv` to the running backend.
- `frontend/backend_test.py` – Example interactions against backend APIs (used for integration validation).

## Next Steps

- Integrate authentication with a persistent identity provider.
- Refine AI insights with machine learning models and historical trend data.
- Harden error handling and add end-to-end Cypress tests for the import workflow.
