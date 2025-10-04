from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, HTTPException

from ..config import logger
from ..database import get_database
from ..models import SpendingInsight
from ..services.analytics import aggregate_spending_summary, build_spending_trends
from ..services.insights import generate_spending_insights
from ..utils import parse_from_mongo, prepare_for_mongo

router = APIRouter(prefix="/ai", tags=["ai"])

db = get_database()


@router.post("/insights/{user_id}")
async def create_ai_insights(user_id: str):
    try:
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        transactions = await db.transactions.find({
            "user_id": user_id,
            "date": {"$gte": thirty_days_ago.isoformat()}
        }).to_list(length=None)
        parsed_transactions = [parse_from_mongo(tx) for tx in transactions]

        summary = aggregate_spending_summary(parsed_transactions)
        trends = build_spending_trends(parsed_transactions, days=30)
        insights_payload = generate_spending_insights(summary, trends, user_id)

        await db.spending_insights.delete_many({"user_id": user_id})
        insights_to_store: List[dict] = []
        for insight_data in insights_payload:
            insight = SpendingInsight(
                user_id=user_id,
                insight_type=insight_data.get('category', 'general'),
                title=insight_data.get('title', 'Financial Insight'),
                description=insight_data.get('description', ''),
                recommendation=insight_data.get('recommendation', ''),
                priority=insight_data.get('priority', 'medium')
            )
            insights_to_store.append(prepare_for_mongo(insight.dict()))

        if insights_to_store:
            await db.spending_insights.insert_many(insights_to_store)

        return {
            "insights": insights_payload,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error generating AI insights")
        raise HTTPException(status_code=500, detail="Failed to generate insights") from exc


@router.get("/insights/{user_id}")
async def get_ai_insights(user_id: str, limit: int = 10):
    try:
        insights = await db.spending_insights.find({"user_id": user_id}).sort("created_at", -1).limit(limit).to_list(length=None)
        return [SpendingInsight(**parse_from_mongo(insight)) for insight in insights]
    except Exception as exc:
        logger.exception("Error retrieving AI insights")
        raise HTTPException(status_code=500, detail="Failed to retrieve insights") from exc
