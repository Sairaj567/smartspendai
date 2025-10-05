# SmartSpendAI – Copilot Onboarding

## Architecture map
- Full-stack app: FastAPI backend (`backend/app`) + CRA/Tailwind frontend (`frontend/src`); API responses live under the `/api` prefix from `routes/__init__.py`.
- Data persistence via MongoDB using Motor; schemas are expressed as Pydantic models in `app/models.py` and stored as ISO strings through `utils.prepare_for_mongo`.
- AI workflows live in `app/services/{openrouter_classifier,insights}.py`; analytics rollups run through `services/analytics.py` and are shared across routes and insights.
- Tests in `tests/` monkeypatch module-level `db` globals, so import `get_database()` at module scope when adding new collections.

## Backend patterns
- Always declare `db = get_database()` at module import time so routes share the cached Motor client managed by `DatabaseManager` in `database.py`.
- New endpoints belong under `app/routes/`; include them via `routes/__init__.py` and keep handlers `async` returning Pydantic models or serialisable dicts.
- Use `utils.prepare_for_mongo` before inserts and `parse_from_mongo` + `normalize_investment_category` on reads to preserve ISO dates and investment recategorisation.
- Runtime configuration comes from `.env` loaded in `config.get_settings()`; missing `MONGO_URL` aborts startup, so guard new features with helpful error messages.

## AI + data handling
- `services/openrouter_classifier` gates LLM calls behind `openrouter_available()` and caches responses; respect `_SEMAPHORE` limits if you add concurrent classification.
- Bulk flows (`routes/transactions.import_transactions`, `_execute_bulk_create`) expect duplicates matched on `user_id+amount+date+description`; reuse that rule when deduping.
- Insight generation first computes summaries/trends (`services/analytics`) then calls `generate_spending_insights`; keep rule-based fallbacks intact for offline behaviour.
- CSV ingestion relies on `utils.parse_csv_transactions` for header normalisation, amount parsing, and investment heuristics—extend those helpers rather than reimplementing.

## Frontend habits
- React app uses CRACO with Tailwind + Radix UI components from `src/components/ui`; import shared primitives instead of raw HTML where possible.
- API calls centralise through `resolveApiBase()` helpers that honour `REACT_APP_BACKEND_URL` and default to `http://localhost:8000/api`; keep new calls consistent.
- Auth is client-side only: store the pseudo user in `localStorage` (`spendsmart_user`) and guard routes via `ProtectedRoute` in `App.js`.
- Respect the design shell (sidebar + gradient background) and reuse page patterns from `Transactions.js` / `ImportTransactions.js` when adding screens.

## Local workflows
- Backend: `cd backend; pip install -r requirements.txt; python -m uvicorn server:app --reload` (requires MongoDB + `.env`).
- Frontend: `cd frontend; npm install; npm start` (CRACO dev server on port `3000`).
- Populate demo data via `POST /api/transactions/generate/{user}` or run `test_import.py` to hit the importer with `test_transactions.csv`.
- Configure OpenRouter with `OPENROUTER_*` env vars; without a key the system gracefully falls back to rule-based categorisation.

## Testing & tooling
- Run backend tests with `python -m pytest tests`; async helpers use `asyncio.run`, so expose coroutine-friendly APIs.
- `frontend/backend_test.py` performs request-based smoke tests and writes results to `test_reports/backend_test_results.json` for dashboards.
- Sample fixtures (`test_transactions.csv`, `data/sample_transactions.csv`, `data/bank_statement.csv`) cover importer scenarios—recycle them for new tests.
- Formatting/linting relies on `black`, `flake8`, `isort`, `mypy` (backend) and CRA ESLint/Tailwind configs (frontend); prefer these over ad-hoc tools.
