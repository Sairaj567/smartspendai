import json
from math import floor
from typing import Any, Dict, List, Optional

import httpx

from ..config import get_settings, logger
from .openrouter_classifier import openrouter_available


_TIMEFRAME_MONTH_MAP = {
    "current_month": 1,
    "last_month": 1,
    "3_months": 3,
    "6_months": 6,
    "1_year": 12,
    "65_days": 2,
}

_MAX_INSIGHTS = 6
_DEFAULT_PRIORITY = "medium"
_VALID_PRIORITIES = {"low", "medium", "high"}


def _round_to_step(amount: float, step: int = 500) -> float:
    if amount <= 0:
        return 0
    rounded = floor(amount / step) * step
    return max(step, rounded)


async def generate_spending_insights(
    summary: Dict,
    trends: Dict,
    user_id: str,
    timeframe: str,
    timeframe_label: Optional[str] = None,
) -> List[Dict]:
    metrics = _compute_financial_metrics(summary, trends, timeframe, timeframe_label)

    if openrouter_available():
        llm_insights = await _generate_llm_insights(summary, trends, metrics, user_id, timeframe)
        if llm_insights:
            return llm_insights[:_MAX_INSIGHTS]

    return _generate_rule_based_insights(summary, metrics)


def _compute_financial_metrics(
    summary: Dict,
    trends: Dict,
    timeframe: str,
    timeframe_label: Optional[str] = None,
) -> Dict[str, Any]:
    total_expenses = summary.get('total_expenses', 0)
    total_income = summary.get('total_income', 0)
    net_savings = summary.get('net_savings', 0)
    top_categories = summary.get('top_categories', [])
    avg_daily_spending = trends.get('average_daily_spending', 0)
    savings_rate = (net_savings / total_income) * 100 if total_income else 0

    resolved_timeframe_label = timeframe_label or timeframe.replace('_', ' ').title()
    trends_list = trends.get('trends', [])
    months_in_window = _TIMEFRAME_MONTH_MAP.get(
        timeframe,
        max(1, round(len(trends_list) / 30) or 1)
    )
    avg_monthly_income = total_income / months_in_window if months_in_window else total_income
    avg_monthly_expenses = total_expenses / months_in_window if months_in_window else total_expenses
    monthly_surplus = max(0, net_savings / months_in_window if months_in_window else net_savings)
    investment_snapshot = summary.get('investment_category') or {}
    invested_amount = summary.get('invested_amount', 0)
    investment_percentage = investment_snapshot.get('percentage') or (
        round((invested_amount / total_expenses) * 100, 1)
        if total_expenses
        else 0
    )

    return {
        "timeframe": timeframe,
        "timeframe_label": resolved_timeframe_label,
        "months_in_window": months_in_window,
        "total_expenses": total_expenses,
        "total_income": total_income,
        "net_savings": net_savings,
        "top_categories": top_categories,
        "avg_daily_spending": avg_daily_spending,
        "savings_rate": savings_rate,
        "avg_monthly_income": avg_monthly_income,
        "avg_monthly_expenses": avg_monthly_expenses,
        "monthly_surplus": monthly_surplus,
        "investment_snapshot": investment_snapshot,
        "invested_amount": invested_amount,
        "investment_percentage": investment_percentage,
        "trends": trends_list,
    }


async def _generate_llm_insights(
    summary: Dict,
    trends: Dict,
    metrics: Dict[str, Any],
    user_id: str,
    timeframe: str,
) -> List[Dict[str, Any]]:
    settings = get_settings()

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    if settings.openrouter_app_url:
        headers["HTTP-Referer"] = settings.openrouter_app_url
    if settings.openrouter_app_name:
        headers["X-Title"] = settings.openrouter_app_name

    context = {
        "user_id": user_id,
        "timeframe": timeframe,
        "timeframe_label": metrics["timeframe_label"],
        "summary": summary,
        "derived_metrics": {
            "total_expenses": metrics["total_expenses"],
            "total_income": metrics["total_income"],
            "net_savings": metrics["net_savings"],
            "savings_rate": round(metrics["savings_rate"], 2),
            "monthly_surplus": round(metrics["monthly_surplus"], 2),
            "avg_daily_spending": metrics["avg_daily_spending"],
            "investment_percentage": metrics["investment_percentage"],
        },
        "top_categories": metrics["top_categories"],
        "trends": {
            "average_daily_spending": trends.get('average_daily_spending', 0),
            "recent_daily_totals": trends.get('trends', [])[-30:],
        },
    }

    user_prompt = (
        "You are a certified financial planner for Indian professionals. "
        "Review the analytics context and produce up to six personalised spending insights. "
        "Each insight must be a JSON object with fields: title, description, recommendation, priority, category. "
        "Priorities must be one of: low, medium, high. "
        "Categories should be short slugs like savings, investment, budgeting, optimization, spending, general. "
        "Focus on actionable advice grounded in the provided numbers. "
        "Respond ONLY with a JSON array (no prose)."
    )

    payload = {
        "model": settings.openrouter_model,
        "temperature": 0.3,
        "messages": [
            {
                "role": "system",
                "content": user_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(context, ensure_ascii=False, indent=2),
            },
        ],
    }

    try:
        async with httpx.AsyncClient(base_url=settings.openrouter_base_url, timeout=settings.openrouter_timeout) as client:
            response = await client.post("/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("OpenRouter insight generation failed: %s", exc)
        return []

    try:
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return []
        content = choices[0]["message"].get("content", "")
    except (ValueError, KeyError, TypeError) as exc:
        logger.warning("Unexpected OpenRouter insight response: %s", exc)
        return []

    return _parse_llm_content(content)


def _parse_llm_content(content: str) -> List[Dict[str, Any]]:
    if not content:
        return []

    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # remove first and last fence if present
        if lines:
            lines = [line for line in lines if not line.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        logger.info("OpenRouter insight payload not valid JSON")
        return []

    if isinstance(parsed, dict):
        parsed = parsed.get("insights") or [parsed]

    if not isinstance(parsed, list):
        return []

    insights: List[Dict[str, Any]] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip() or "Personalised Financial Insight"
        description = str(item.get("description", "")).strip() or "Insight generated from your recent spending patterns."
        recommendation = str(item.get("recommendation", "")).strip() or "Review your cash flow and adjust according to the recommendation."
        priority = str(item.get("priority", _DEFAULT_PRIORITY)).strip().lower()
        if priority not in _VALID_PRIORITIES:
            priority = _DEFAULT_PRIORITY
        category = str(item.get("category", "general")).strip() or "general"

        insights.append({
            "title": title,
            "description": description,
            "recommendation": recommendation,
            "priority": priority,
            "category": category.lower(),
        })

    return insights


def _generate_rule_based_insights(summary: Dict, metrics: Dict[str, Any]) -> List[Dict]:
    insights: List[Dict] = []

    total_expenses = metrics['total_expenses']
    total_income = metrics['total_income']
    net_savings = metrics['net_savings']
    top_categories = metrics['top_categories']
    avg_daily_spending = metrics['avg_daily_spending']
    savings_rate = metrics['savings_rate']
    timeframe_label = metrics['timeframe_label']
    months_in_window = metrics['months_in_window']
    avg_monthly_income = metrics['avg_monthly_income']
    avg_monthly_expenses = metrics['avg_monthly_expenses']
    monthly_surplus = metrics['monthly_surplus']
    investment_snapshot = metrics['investment_snapshot']
    invested_amount = metrics['invested_amount']
    investment_percentage = metrics['investment_percentage']

    if total_income > 0:
        savings_rate = (net_savings / total_income) * 100
        if savings_rate < 10:
            insights.append({
                "title": "Low Savings Rate Alert",
                "description": f"Your current savings rate is {savings_rate:.1f}%. Financial experts recommend saving at least 20% of your income.",
                "recommendation": "Consider reducing discretionary spending or finding additional income sources. Start with small cuts in entertainment and dining expenses.",
                "priority": "high",
                "category": "savings"
            })
        elif savings_rate < 20:
            insights.append({
                "title": "Moderate Savings Opportunity",
                "description": f"You're saving {savings_rate:.1f}% of your income. You're on the right track but there's room for improvement.",
                "recommendation": "Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings. Look for areas to optimize your spending.",
                "priority": "medium",
                "category": "savings"
            })
        else:
            insights.append({
                "title": "Excellent Savings Discipline",
                "description": f"Great job! You're saving {savings_rate:.1f}% of your income, which exceeds the recommended 20%.",
                "recommendation": "Consider investing your excess savings in mutual funds or SIPs for better long-term returns.",
                "priority": "low",
                "category": "optimization"
            })

    emergency_target = avg_monthly_expenses * 6 if avg_monthly_expenses else 0
    emergency_monthly_goal = emergency_target / 6 if emergency_target else 0

    if emergency_target:
        emergency_examples = "job loss, medical treatment, or urgent home/vehicle repairs"
        monthly_goal_note = (
            f"Setting aside ₹{emergency_monthly_goal:,.0f} each month will build this safety net in six months."
            if emergency_monthly_goal
            else "Set aside a consistent amount each month to build this safety net."
        )
        insights.append({
            "title": f"Build a ₹{emergency_target:,.0f} Emergency Cushion",
            "description": (
                f"Your core expenses suggest keeping at least ₹{emergency_target:,.0f} handy for emergencies such as {emergency_examples}."
            ),
            "recommendation": (
                f"Keep this fund in a liquid account (high-yield savings or money-market). {monthly_goal_note}"
            ),
            "priority": "high" if savings_rate < 20 else "medium",
            "category": "savings",
        })

    if monthly_surplus >= 1000:
        sip_base = min(
            monthly_surplus * 0.4,
            avg_monthly_income * 0.25 if avg_monthly_income else monthly_surplus * 0.4,
        )
        sip_cap = _round_to_step(monthly_surplus * 0.8, 500)
        sip_amount = min(_round_to_step(sip_base, 500), sip_cap, 25000)
        months_to_emergency = emergency_target / sip_amount if sip_amount > 0 else None
        emergency_note = (
            f"Build a 6-month safety net (~₹{emergency_target:,.0f}) covering job loss, hospital bills, or urgent repairs. "
            "Park it in a high-yield savings account like AU Small Finance, IDFC FIRST, or SBI Digital FD."
            if emergency_target
            else "Use a high-yield savings account to build an emergency fund."
        )

        insights.append({
            "title": f"Automate a ₹{sip_amount:,.0f} Monthly SIP",
            "description": (
                f"Across the {timeframe_label.lower()}, you retained roughly ₹{monthly_surplus:,.0f} per month after expenses. "
                "Channeling a portion into disciplined investing will compound faster than idle cash."
            ),
            "recommendation": (
                f"Set up a ₹{sip_amount:,.0f} SIP into diversified mutual funds: 60% Nifty 50/ Sensex index fund, "
                "25% flexi-cap fund, 15% short-term debt. "
                f"This plan can fund your emergency corpus in about {months_to_emergency:.0f} months." if months_to_emergency and months_to_emergency > 0 else emergency_note
            ),
            "priority": "medium" if savings_rate < 20 else "low",
            "category": "investment"
        })

        if monthly_surplus >= 4000:
            equity_allocation = _round_to_step(monthly_surplus * 0.5, 1000)
            high_yield_buffer = _round_to_step(monthly_surplus * 0.2, 500)
            risk_note = (
                "Your current investment allocation is light at "
                f"{investment_percentage:.1f}% of expenses." if investment_percentage < 15 else
                "You're already investing consistently—consider widening your mix."
            )
            insights.append({
                "title": "Grow with Low-Cost Equity",
                "description": (
                    f"{risk_note} With ₹{monthly_surplus:,.0f} free each month, you can comfortably add equities without straining cash flow."
                ),
                "recommendation": (
                    f"Deploy ₹{equity_allocation:,.0f} into large-cap ETFs (Nifty 50, Sensex) via Zerodha/ Groww, keep ₹{high_yield_buffer:,.0f} "
                    "in a sweep-in savings account (Yes Optima, Kotak ActivMoney) for near-term goals, and route the balance into a conservative hybrid fund."
                ),
                "priority": "medium" if investment_percentage < 15 else "low",
                "category": "investment"
            })

    if top_categories:
        top_category = top_categories[0]
        category_name = top_category.get('category', 'Unknown')
        category_amount = top_category.get('amount', 0)
        category_percentage = top_category.get('percentage', 0)

        if category_percentage > 40:
            insights.append({
                "title": f"High {category_name} Spending",
                "description": f"{category_name} accounts for {category_percentage:.1f}% (₹{category_amount:.0f}) of your total expenses. This seems unusually high.",
                "recommendation": f"Review your {category_name.lower()} expenses. Look for subscriptions you don't use or opportunities to find better deals.",
                "priority": "high",
                "category": "spending"
            })
        elif category_percentage > 25:
            insights.append({
                "title": f"{category_name} Budget Review",
                "description": f"You're spending {category_percentage:.1f}% (₹{category_amount:.0f}) on {category_name}. This is significant but manageable.",
                "recommendation": f"Set a monthly budget for {category_name.lower()} and track it weekly to avoid overspending.",
                "priority": "medium",
                "category": "budgeting"
            })

    if avg_daily_spending > 0:
        monthly_projection = avg_daily_spending * 30
        if total_income and monthly_projection > total_income * 0.8:
            insights.append({
                "title": "High Daily Spending Alert",
                "description": f"Your average daily spending of ₹{avg_daily_spending:.0f} projects to ₹{monthly_projection:.0f} monthly, which is high relative to your income.",
                "recommendation": "Try setting a daily spending limit to 60% of your income split over 30 days. Use UPI payment limits to control impulse purchases.",
                "priority": "high",
                "category": "budgeting"
            })
        else:
            insights.append({
                "title": "Spending Pattern Analysis",
                "description": f"Your average daily spending is ₹{avg_daily_spending:.0f}, which seems reasonable for your income level.",
                "recommendation": "Maintain this spending pattern and consider automating your savings to ensure consistent wealth building.",
                "priority": "low",
                "category": "optimization"
            })

    insights.append({
        "title": "Digital Payment Benefits",
        "description": "You're using UPI for most transactions, which provides excellent tracking and cashback opportunities.",
        "recommendation": "Link your UPI to a rewards credit card or use payment apps that offer cashback to maximize your benefits on routine expenses.",
        "priority": "medium",
        "category": "optimization"
    })

    if not insights:
        insights.append({
            "title": "Start Your Financial Journey",
            "description": "Begin tracking your expenses consistently to unlock personalized insights and recommendations.",
            "recommendation": "Record all your transactions for the next 30 days to get meaningful financial insights and budget recommendations.",
            "priority": "medium",
            "category": "general"
        })

    return insights[:_MAX_INSIGHTS]
