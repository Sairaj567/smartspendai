from datetime import datetime, timezone
from typing import List

import io
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from ..config import logger
from ..database import get_database
from ..models import ImportResult, Transaction, TransactionCreate
<<<<<<< HEAD
=======
from ..services.openrouter_classifier import (
    classify_transaction_via_openrouter,
    enrich_transactions_with_ai,
)
>>>>>>> 5cf7dfc3ec21208dff093e7bb9e2b1ea0885d130
from ..services.transactions import generate_mock_transactions
from ..utils import parse_csv_transactions, parse_from_mongo, prepare_for_mongo

router = APIRouter(prefix="/transactions", tags=["transactions"])

db = get_database()


@router.post("/", response_model=Transaction)
<<<<<<< HEAD
async def create_transaction(transaction: TransactionCreate) -> Transaction:
    transaction_dict = transaction.dict()
    transaction_dict['date'] = datetime.now(timezone.utc)
=======
async def create_transaction(transaction: TransactionCreate, auto_categorize: bool = True) -> Transaction:
    transaction_dict = transaction.dict()
    transaction_dict['date'] = datetime.now(timezone.utc)

    if auto_categorize:
        try:
            new_category = await classify_transaction_via_openrouter(
                description=transaction_dict.get('description', ''),
                merchant=transaction_dict.get('merchant'),
                amount=transaction_dict.get('amount'),
                transaction_type=transaction_dict.get('type'),
                current_category=transaction_dict.get('category'),
                allow_override=False,
            )
            if new_category:
                transaction_dict['category'] = new_category
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("AI categorization failed during transaction create: %s", exc)

>>>>>>> 5cf7dfc3ec21208dff093e7bb9e2b1ea0885d130
    transaction_obj = Transaction(**transaction_dict)

    try:
        prepared_data = prepare_for_mongo(transaction_obj.dict())
        await db.transactions.insert_one(prepared_data)
    except Exception as exc:
        logger.exception("Failed to create transaction")
        raise HTTPException(status_code=500, detail="Unable to create transaction") from exc

    return transaction_obj


@router.get("/{user_id}", response_model=List[Transaction])
async def get_user_transactions(user_id: str, limit: int = 50) -> List[Transaction]:
    try:
        transactions = await db.transactions.find({"user_id": user_id}).sort("date", -1).limit(limit).to_list(length=None)
        return [Transaction(**parse_from_mongo(transaction)) for transaction in transactions]
    except Exception as exc:
        logger.exception("Database error in get_user_transactions")
        raise HTTPException(status_code=500, detail="Failed to fetch user transactions") from exc


<<<<<<< HEAD
@router.post("/generate/{user_id}")
async def generate_demo_transactions(user_id: str):
    try:
        existing_count = await db.transactions.count_documents({"user_id": user_id})
        if existing_count > 0:
            return {"message": f"User already has {existing_count} transactions"}

        mock_transactions = generate_mock_transactions(user_id)
        prepared_transactions = [prepare_for_mongo(tx) for tx in mock_transactions]
        await db.transactions.insert_many(prepared_transactions)

        return {
            "message": f"Generated {len(mock_transactions)} demo transactions for user {user_id}",
            "count": len(mock_transactions)
        }
    except Exception as exc:
        logger.exception("Error generating demo transactions")
        raise HTTPException(status_code=500, detail="Failed to generate demo transactions") from exc


@router.post("/import/{user_id}", response_model=ImportResult)
async def import_transactions(user_id: str, file: UploadFile = File(...), skip_duplicates: bool = True) -> ImportResult:
=======



@router.post("/import/{user_id}", response_model=ImportResult)
async def import_transactions(
    user_id: str,
    file: UploadFile = File(...),
    skip_duplicates: bool = True,
    auto_categorize: bool = True,
) -> ImportResult:
>>>>>>> 5cf7dfc3ec21208dff093e7bb9e2b1ea0885d130
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

<<<<<<< HEAD
=======
    ai_updates = {}

    if auto_categorize and unique_transactions:
        try:
            ai_updates = await enrich_transactions_with_ai(unique_transactions)
            if ai_updates:
                logger.info("AI categorized %s transactions via OpenRouter", len(ai_updates))
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("AI categorization skipped due to error: %s", exc)

>>>>>>> 5cf7dfc3ec21208dff093e7bb9e2b1ea0885d130
    try:
        if unique_transactions:
            prepared_transactions = [prepare_for_mongo(tx.dict()) for tx in unique_transactions]
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
