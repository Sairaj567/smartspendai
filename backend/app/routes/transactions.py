from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union

import io
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from ..config import logger
from ..database import get_database
from ..models import (
    BulkTransactionCreateRequest,
    BulkTransactionResult,
    ImportResult,
    Transaction,
    TransactionCreate,
)
from ..services.openrouter_classifier import (
    classify_transaction_via_openrouter,
    enrich_transactions_with_ai,
)
from ..utils import (
    normalize_investment_category,
    parse_csv_transactions,
    parse_from_mongo,
    prepare_for_mongo,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])

db = get_database()


_DEMO_TRANSACTION_BLUEPRINT = [
    {
        "description": "Monthly Salary Credit",
        "merchant": "Acme Corp Payroll",
        "amount": 125000.0,
        "type": "income",
        "category": "Income",
        "payment_method": "Bank Transfer",
        "offset_days": 3,
    },
    {
        "description": "Flat Rent - Koramangala",
        "merchant": "Urban Homes",
        "amount": 32000.0,
        "type": "expense",
        "category": "Rent",
        "payment_method": "UPI",
        "offset_days": 2,
    },
    {
        "description": "Systematic Investment Plan",
        "merchant": "Groww Investments",
        "amount": 15000.0,
        "type": "expense",
        "category": "Investments",
        "payment_method": "Bank Transfer",
        "offset_days": 1,
    },
    {
        "description": "Weekend Groceries",
        "merchant": "Big Bazaar",
        "amount": 5400.0,
        "type": "expense",
        "category": "Groceries",
        "payment_method": "UPI",
        "offset_days": 5,
    },
    {
        "description": "Daily Commute - Metro Card",
        "merchant": "BMRCL",
        "amount": 2400.0,
        "type": "expense",
        "category": "Transportation",
        "payment_method": "UPI",
        "offset_days": 6,
    },
    {
        "description": "Friday Dinner with Friends",
        "merchant": "Toit Brewpub",
        "amount": 2600.0,
        "type": "expense",
        "category": "Food & Dining",
        "payment_method": "Credit Card",
        "offset_days": 7,
    },
    {
        "description": "Electricity Bill - BESCOM",
        "merchant": "BESCOM",
        "amount": 4200.0,
        "type": "expense",
        "category": "Bills & Utilities",
        "payment_method": "NetBanking",
        "offset_days": 8,
    },
    {
        "description": "Monthly Phone Bill",
        "merchant": "Airtel",
        "amount": 999.0,
        "type": "expense",
        "category": "Bills & Utilities",
        "payment_method": "UPI",
        "offset_days": 9,
    },
    {
        "description": "Streaming Subscription Renewal",
        "merchant": "Netflix",
        "amount": 649.0,
        "type": "expense",
        "category": "Entertainment",
        "payment_method": "Credit Card",
        "offset_days": 10,
    },
    {
        "description": "Coffee with client",
        "merchant": "Starbucks",
        "amount": 450.0,
        "type": "expense",
        "category": "Food & Dining",
        "payment_method": "UPI",
        "offset_days": 11,
    },
    {
        "description": "Cashback Reward",
        "merchant": "HDFC Bank",
        "amount": 1500.0,
        "type": "income",
        "category": "Income",
        "payment_method": "Bank Transfer",
        "offset_days": 12,
    },
    {
        "description": "Health Insurance Premium",
        "merchant": "Star Health",
        "amount": 7200.0,
        "type": "expense",
        "category": "Healthcare",
        "payment_method": "UPI",
        "offset_days": 13,
    },
    {
        "description": "Weekend Getaway Booking",
        "merchant": "Airbnb",
        "amount": 9800.0,
        "type": "expense",
        "category": "Travel",
        "payment_method": "Credit Card",
        "offset_days": 14,
    },
    {
        "description": "Quarterly Bonus",
        "merchant": "Acme Corp Payroll",
        "amount": 40000.0,
        "type": "income",
        "category": "Income",
        "payment_method": "Bank Transfer",
        "offset_days": 20,
    },
    {
        "description": "Equity Top-up",
        "merchant": "Zerodha Securities",
        "amount": 10000.0,
        "type": "expense",
        "category": "Investments",
        "payment_method": "NetBanking",
        "offset_days": 22,
    },
]


def _model_dump(model):
    dump = getattr(model, "model_dump", None)
    if callable(dump):
        return dump()
    return model.dict()


def _model_copy(model, *, update):
    copier = getattr(model, "model_copy", None)
    if callable(copier):
        return copier(update=update)
    return model.copy(update=update)


async def _build_transaction_from_input(transaction: TransactionCreate) -> Transaction:
    transaction_dict = _model_dump(transaction)
    transaction_dict['date'] = transaction_dict.get('date') or datetime.now(timezone.utc)

    ai_category: Optional[str] = None
    try:
        ai_category = await classify_transaction_via_openrouter(
            description=transaction_dict.get('description'),
            merchant=transaction_dict.get('merchant'),
            amount=transaction_dict.get('amount'),
            transaction_type=transaction_dict.get('type'),
            current_category=transaction_dict.get('category'),
            allow_override=True,
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning("AI classification failed while preparing transaction: %s", exc)

    raw_category = transaction_dict.get('category')
    if isinstance(raw_category, str):
        raw_category = raw_category.strip()
    else:
        raw_category = None

    candidate_category = ai_category or raw_category or 'Others'
    normalized_candidate = normalize_investment_category(
        candidate_category,
        transaction_dict.get('description'),
        transaction_dict.get('merchant'),
        transaction_dict.get('type'),
    )

    if ai_category and normalized_candidate.lower() != 'investments':
        transaction_dict['category'] = ai_category
    else:
        transaction_dict['category'] = normalized_candidate

    return Transaction(**transaction_dict)


async def _execute_bulk_create(
    transaction_inputs: List[TransactionCreate],
    *,
    skip_duplicates: bool = True,
) -> BulkTransactionResult:
    prepared_transactions: List[Transaction] = []
    errors: List[str] = []

    for index, transaction_input in enumerate(transaction_inputs, start=1):
        try:
            prepared_transactions.append(await _build_transaction_from_input(transaction_input))
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to prepare transaction %s during bulk create", index)
            errors.append(f"Transaction {index}: {exc}")

    skipped_duplicates = 0
    transactions_to_insert: List[Transaction] = []

    if skip_duplicates:
        for transaction in prepared_transactions:
            try:
                existing = await db.transactions.find_one({
                    "user_id": transaction.user_id,
                    "amount": transaction.amount,
                    "date": transaction.date.isoformat(),
                    "description": transaction.description,
                })
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Duplicate check failed during bulk create: %s", exc)
                existing = None

            if existing:
                skipped_duplicates += 1
            else:
                transactions_to_insert.append(transaction)
    else:
        transactions_to_insert = prepared_transactions

    created_count = 0
    inserted_transactions: List[Transaction] = []
    if transactions_to_insert:
        try:
            prepared_payload = [prepare_for_mongo(_model_dump(tx)) for tx in transactions_to_insert]
            await db.transactions.insert_many(prepared_payload)
            created_count = len(transactions_to_insert)
            inserted_transactions = transactions_to_insert
        except Exception as exc:
            logger.exception("Failed to insert bulk transactions")
            errors.append("Database error during bulk insert")
            created_count = 0
            inserted_transactions = []

    failed_count = max(0, len(transaction_inputs) - created_count - skipped_duplicates)

    return BulkTransactionResult(
        total_requested=len(transaction_inputs),
        created_count=created_count,
        skipped_duplicates=skipped_duplicates,
        failed_count=failed_count,
        errors=errors,
        created_transactions=inserted_transactions[:10],
    )


@router.post("/generate/{user_id}")
async def generate_demo_transactions(user_id: str, overwrite: bool = False):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    try:
        existing_count = await db.transactions.count_documents({"user_id": user_id})
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed checking existing transactions for demo generation")
        raise HTTPException(status_code=500, detail="Database unavailable") from exc

    if existing_count and not overwrite:
        return {
            "created": 0,
            "skipped": existing_count,
            "message": "Demo data already present for user",
            "total_transactions": existing_count,
        }

    if existing_count and overwrite:
        try:
            await db.transactions.delete_many({"user_id": user_id})
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed wiping user transactions before regeneration")
            raise HTTPException(status_code=500, detail="Could not reset user transactions") from exc

    base_date = datetime.now(timezone.utc)
    transaction_inputs: List[TransactionCreate] = []

    for index, blueprint in enumerate(_DEMO_TRANSACTION_BLUEPRINT):
        offset_days = int(blueprint.get("offset_days", index))
        transaction_inputs.append(TransactionCreate(
            user_id=user_id,
            amount=blueprint["amount"],
            category=blueprint.get("category", "Others"),
            description=blueprint["description"],
            merchant=blueprint.get("merchant", "Demo Merchant"),
            type=blueprint.get("type", "expense"),
            payment_method=blueprint.get("payment_method", "UPI"),
            date=base_date - timedelta(days=offset_days),
        ))

    result = await _execute_bulk_create(transaction_inputs, skip_duplicates=True)

    return {
        "created": result.created_count,
        "skipped_duplicates": result.skipped_duplicates,
        "failed": result.failed_count,
        "total_requested": result.total_requested,
        "sample_preview": [
            _model_dump(tx)
            for tx in result.created_transactions
        ],
    }


@router.post("/", response_model=Union[Transaction, BulkTransactionResult])
async def create_transaction(
    payload: Union[TransactionCreate, BulkTransactionCreateRequest, List[TransactionCreate]]
):
    if isinstance(payload, list):
        if not payload:
            raise HTTPException(status_code=400, detail="No transactions supplied")
        return await _execute_bulk_create(payload, skip_duplicates=True)

    if isinstance(payload, BulkTransactionCreateRequest):
        if not payload.transactions:
            raise HTTPException(status_code=400, detail="No transactions supplied")
        return await _execute_bulk_create(payload.transactions, skip_duplicates=payload.skip_duplicates)

    transaction_obj = await _build_transaction_from_input(payload)

    try:
        prepared_data = prepare_for_mongo(_model_dump(transaction_obj))
        await db.transactions.insert_one(prepared_data)
    except Exception as exc:
        logger.exception("Failed to create transaction")
        raise HTTPException(status_code=500, detail="Unable to create transaction") from exc

    return transaction_obj


@router.get("/{user_id}", response_model=List[Transaction])
async def get_user_transactions(user_id: str, limit: Optional[int] = None) -> List[Transaction]:
    try:
        cursor = db.transactions.find({"user_id": user_id}).sort("date", -1)
        if limit and limit > 0:
            cursor = cursor.limit(limit)
        transactions = await cursor.to_list(length=None)
        normalized_transactions: List[Transaction] = []
        for transaction in transactions:
            parsed = parse_from_mongo(transaction)
            parsed['category'] = normalize_investment_category(
                parsed.get('category'),
                parsed.get('description'),
                parsed.get('merchant'),
                parsed.get('type'),
            )
            normalized_transactions.append(Transaction(**parsed))
        return normalized_transactions
    except Exception as exc:
        logger.exception("Database error in get_user_transactions")
        raise HTTPException(status_code=500, detail="Failed to fetch user transactions") from exc





@router.post("/import/{user_id}", response_model=ImportResult)
async def import_transactions(user_id: str, file: UploadFile = File(...), skip_duplicates: bool = True) -> ImportResult:
    if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")

    try:
        content = await file.read()
        if file.filename.lower().endswith('.csv'):
            file_content = content.decode('utf-8')
            transactions, errors = parse_csv_transactions(file_content, user_id)
        else:
            dataframe = pd.read_excel(io.BytesIO(content))
            csv_content = dataframe.to_csv(index=False)
            transactions, errors = parse_csv_transactions(csv_content, user_id)

        try:
            await enrich_transactions_with_ai(transactions, allow_override=True)
        except Exception as ai_exc:  # pragma: no cover - defensive logging
            logger.warning("AI enrichment skipped during import: %s", ai_exc)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("File parsing failed during import")
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(exc)}") from exc

    duplicate_count = 0
    unique_transactions: List[Transaction] = []
    database_insert_warning = False

    if skip_duplicates:
        try:
            for transaction in transactions:
                existing = await db.transactions.find_one({
                    "user_id": user_id,
                    "amount": transaction.amount,
                    "date": transaction.date.isoformat(),
                    "description": transaction.description
                })
                if existing:
                    duplicate_count += 1
                else:
                    unique_transactions.append(transaction)
        except Exception as exc:
            logger.exception("Failed duplicate check during import; defaulting to include all")
            unique_transactions = transactions
    else:
        unique_transactions = transactions

    successful_imports = 0
    failed_imports = 0

    try:
        if unique_transactions:
            prepared_transactions = [prepare_for_mongo(_model_dump(tx)) for tx in unique_transactions]
            await db.transactions.insert_many(prepared_transactions)
            successful_imports = len(unique_transactions)
    except Exception as exc:
        logger.exception("Database failure while importing transactions")
        errors.append("Database unavailable; transactions saved in session only")
        successful_imports = len(unique_transactions)
        database_insert_warning = True

    failed_imports = max(0, len(errors) - (1 if database_insert_warning else 0))

    return ImportResult(
        total_rows=len(transactions),
        successful_imports=successful_imports,
        failed_imports=failed_imports,
        errors=errors,
        duplicate_count=duplicate_count,
        imported_transactions=unique_transactions[:10]
    )


@router.post("/bulk", response_model=BulkTransactionResult)
async def bulk_create_transactions(payload: BulkTransactionCreateRequest) -> BulkTransactionResult:
    if not payload.transactions:
        raise HTTPException(status_code=400, detail="No transactions supplied")

    prepared_transactions: List[Transaction] = []
    errors: List[str] = []

    for index, transaction_input in enumerate(payload.transactions, start=1):
        try:
            prepared_transactions.append(await _build_transaction_from_input(transaction_input))
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to prepare transaction %s during bulk create", index)
            errors.append(f"Transaction {index}: {str(exc)}")

    skipped_duplicates = 0
    transactions_to_insert: List[Transaction] = []

    if payload.skip_duplicates:
        for transaction in prepared_transactions:
            try:
                existing = await db.transactions.find_one({
                    "user_id": transaction.user_id,
                    "amount": transaction.amount,
                    "date": transaction.date.isoformat(),
                    "description": transaction.description,
                })
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Duplicate check failed during bulk create: %s", exc)
                existing = None

            if existing:
                skipped_duplicates += 1
            else:
                transactions_to_insert.append(transaction)
    else:
        transactions_to_insert = prepared_transactions

    created_count = 0
    if transactions_to_insert:
        try:
            prepared_payload = [prepare_for_mongo(_model_dump(tx)) for tx in transactions_to_insert]
            await db.transactions.insert_many(prepared_payload)
            created_count = len(transactions_to_insert)
        except Exception as exc:
            logger.exception("Failed to insert bulk transactions")
            errors.append("Database error during bulk insert")
            created_count = 0
            transactions_to_insert = []

    failed_count = max(0, len(payload.transactions) - created_count - skipped_duplicates)

    return BulkTransactionResult(
        total_requested=len(payload.transactions),
        created_count=created_count,
        skipped_duplicates=skipped_duplicates,
        failed_count=failed_count,
        errors=errors,
        created_transactions=transactions_to_insert[:10],
    )

#a special commit for alok
