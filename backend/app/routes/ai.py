from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from ..config import logger
from ..database import get_database
from ..models import SpendingInsight
from ..services.analytics import aggregate_spending_summary, build_spending_trends
from ..services.insights import generate_spending_insights
from ..utils import DEFAULT_TIMEFRAME, parse_from_mongo, prepare_for_mongo, resolve_timeframe_window

router = APIRouter(prefix="/ai", tags=["ai"])

db = get_database()


@router.post("/insights/{user_id}")
async def create_ai_insights(user_id: str, timeframe: str = DEFAULT_TIMEFRAME):
    try:
        window = resolve_timeframe_window(timeframe)
        transactions = await db.transactions.find({
            "user_id": user_id,
            "date": {"$gte": window["start"].isoformat(), "$lt": window["end"].isoformat()}
        }).to_list(length=None)
        parsed_transactions = [parse_from_mongo(tx) for tx in transactions]

        summary = aggregate_spending_summary(parsed_transactions)
        trends = build_spending_trends(
            parsed_transactions,
            days=window["days"],
            start_date=window["start"],
            end_date=window["inclusive_end"],
        )
        raw_insights = await generate_spending_insights(
            summary,
            trends,
            user_id,
            timeframe=window["key"],
            timeframe_label=window["label"],
        )

        insights_payload = [
            {
                **insight_data,
                "timeframe": window["key"],
                "timeframe_label": window["label"],
            }
            for insight_data in raw_insights
        ]

        await db.spending_insights.delete_many({
            "user_id": user_id,
            "$or": [
                {"timeframe": window["key"]},
                {"timeframe": {"$exists": False}}
            ]
        })
        insights_to_store: List[dict] = []
        for insight_data in insights_payload:
            insight = SpendingInsight(
                user_id=user_id,
                insight_type=insight_data.get('category', 'general'),
                timeframe=window["key"],
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
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "timeframe": window["key"],
            "timeframe_label": window["label"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error generating AI insights")
        raise HTTPException(status_code=500, detail="Failed to generate insights") from exc


@router.get("/insights/{user_id}")
async def get_ai_insights(user_id: str, limit: int = 10, timeframe: Optional[str] = None):
    try:
        window = resolve_timeframe_window(timeframe or DEFAULT_TIMEFRAME)
        insights_cursor = db.spending_insights.find({
            "user_id": user_id,
            "timeframe": window["key"]
        }).sort("created_at", -1).limit(limit)
        insights = await insights_cursor.to_list(length=None)

        if not insights:
            fallback_cursor = db.spending_insights.find({
                "user_id": user_id
            }).sort("created_at", -1).limit(limit)
            fallback_insights = await fallback_cursor.to_list(length=None)

            if fallback_insights:
                latest_timeframe = fallback_insights[0].get("timeframe")
                if latest_timeframe:
                    insights = [
                        insight
                        for insight in fallback_insights
                        if insight.get("timeframe") == latest_timeframe
                    ][:limit]
                else:
                    insights = fallback_insights[:limit]

        return [SpendingInsight(**parse_from_mongo(insight)) for insight in insights]
    except Exception as exc:
        logger.exception("Error retrieving AI insights")
        raise HTTPException(status_code=500, detail="Failed to retrieve insights") from exc
