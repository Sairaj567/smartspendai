from typing import Dict, List


def generate_spending_insights(summary: Dict, trends: Dict, user_id: str) -> List[Dict]:
    insights: List[Dict] = []

    total_expenses = summary.get('total_expenses', 0)
    total_income = summary.get('total_income', 0)
    net_savings = summary.get('net_savings', 0)
    top_categories = summary.get('top_categories', [])
    avg_daily_spending = trends.get('average_daily_spending', 0)

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

    return insights[:4]
