from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..config import logger
from ..database import get_database
from ..services.analytics import aggregate_spending_summary, build_spending_trends
from ..utils import parse_from_mongo, resolve_timeframe_window

router = APIRouter(prefix="/analytics", tags=["analytics"])

db = get_database()


@router.get("/spending-summary/{user_id}")
async def get_spending_summary(user_id: str, days: int = 30, timeframe: Optional[str] = None):
    if timeframe:
        window = resolve_timeframe_window(timeframe)
        window_start = window["start"]
        window_end = window["end"]
    else:
        if days <= 0:
            raise HTTPException(status_code=400, detail="days must be a positive integer")

        window_end = datetime.now(timezone.utc)
        window_start = window_end - timedelta(days=days)

    window_end = window_end if timeframe else window_end

    try:
        transactions = await db.transactions.find({
            "user_id": user_id,
            "date": {"$gte": window_start.isoformat(), "$lt": window_end.isoformat()}
        }).to_list(length=None)
        parsed_transactions = [parse_from_mongo(tx) for tx in transactions]
    except Exception as exc:
        logger.exception("Database error in get_spending_summary")
        raise HTTPException(status_code=500, detail="Failed to fetch spending summary") from exc

    return aggregate_spending_summary(parsed_transactions)


@router.get("/spending-trends/{user_id}")
async def get_spending_trends(user_id: str, days: int = 30, timeframe: Optional[str] = None):
    if timeframe:
        window = resolve_timeframe_window(timeframe)
        start_date = window["start"]
        end_date = window["inclusive_end"]
        target_days = window["days"]
    else:
        if days <= 0:
            raise HTTPException(status_code=400, detail="days must be a positive integer")

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        target_days = days

    try:
        transactions = await db.transactions.find({
            "user_id": user_id,
            "date": {"$gte": start_date.isoformat(), "$lt": (window["end"].isoformat() if timeframe else end_date.isoformat())},
            "type": "expense"
        }).to_list(length=None)
        parsed_transactions = [parse_from_mongo(tx) for tx in transactions]
    except Exception as exc:
        logger.exception("Database error in get_spending_trends")
        raise HTTPException(status_code=500, detail="Failed to fetch spending trends") from exc

    return build_spending_trends(parsed_transactions, target_days, start_date=start_date, end_date=end_date)
