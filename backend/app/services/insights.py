from math import floor
from typing import Dict, List, Optional


_TIMEFRAME_MONTH_MAP = {
    "current_month": 1,
    "last_month": 1,
    "3_months": 3,
    "6_months": 6,
    "1_year": 12,
    "65_days": 2,
}


def _round_to_step(amount: float, step: int = 500) -> float:
    if amount <= 0:
        return 0
    rounded = floor(amount / step) * step
    return max(step, rounded)


def generate_spending_insights(
    summary: Dict,
    trends: Dict,
    user_id: str,
    timeframe: str,
    timeframe_label: Optional[str] = None,
) -> List[Dict]:
    insights: List[Dict] = []

    total_expenses = summary.get('total_expenses', 0)
    total_income = summary.get('total_income', 0)
    net_savings = summary.get('net_savings', 0)
    top_categories = summary.get('top_categories', [])
    avg_daily_spending = trends.get('average_daily_spending', 0)
    savings_rate = (net_savings / total_income) * 100 if total_income else 0

    timeframe_label = timeframe_label or timeframe.replace('_', ' ').title()
    months_in_window = _TIMEFRAME_MONTH_MAP.get(timeframe, max(1, round(len(trends.get('trends', [])) / 30) or 1))
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

    if monthly_surplus >= 1000:
        sip_base = min(
            monthly_surplus * 0.4,
            avg_monthly_income * 0.25 if avg_monthly_income else monthly_surplus * 0.4,
        )
        sip_cap = _round_to_step(monthly_surplus * 0.8, 500)
        sip_amount = min(_round_to_step(sip_base, 500), sip_cap, 25000)
        emergency_target = avg_monthly_expenses * 6 if avg_monthly_expenses else 0
        months_to_emergency = emergency_target / sip_amount if sip_amount > 0 else None
        emergency_note = (
            f"Build a 6-month safety net (~₹{emergency_target:,.0f}) in a high-yield savings account "
            "like AU Small Finance, IDFC FIRST, or State Bank's Digital FD."
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

    return insights[:6]
