from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

from ..config import logger
from ..database import get_database
from ..services.analytics import aggregate_spending_summary, build_spending_trends
from ..utils import parse_from_mongo

router = APIRouter(prefix="/analytics", tags=["analytics"])

db = get_database()


@router.get("/spending-summary/{user_id}")
async def get_spending_summary(user_id: str, days: int = 30):
    if days <= 0:
        raise HTTPException(status_code=400, detail="days must be a positive integer")

    window_start = datetime.now(timezone.utc) - timedelta(days=days)

    try:
        transactions = await db.transactions.find({
            "user_id": user_id,
            "date": {"$gte": window_start.isoformat()}
        }).to_list(length=None)
        parsed_transactions = [parse_from_mongo(tx) for tx in transactions]
    except Exception as exc:
        logger.exception("Database error in get_spending_summary")
        raise HTTPException(status_code=500, detail="Failed to fetch spending summary") from exc

    return aggregate_spending_summary(parsed_transactions)


@router.get("/spending-trends/{user_id}")
async def get_spending_trends(user_id: str, days: int = 30):
    if days <= 0:
        raise HTTPException(status_code=400, detail="days must be a positive integer")

    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    try:
        transactions = await db.transactions.find({
            "user_id": user_id,
            "date": {"$gte": start_date.isoformat()},
            "type": "expense"
        }).to_list(length=None)
        parsed_transactions = [parse_from_mongo(tx) for tx in transactions]
    except Exception as exc:
        logger.exception("Database error in get_spending_trends")
        raise HTTPException(status_code=500, detail="Failed to fetch spending trends") from exc

    return build_spending_trends(parsed_transactions, days)
