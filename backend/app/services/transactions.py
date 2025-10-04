import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional


def generate_mock_transactions(user_id: str, days: int = 30, count: Optional[int] = None) -> List[Dict]:
    categories = {
        'Food & Dining': ["Zomato", "Swiggy", "McDonald's", 'Starbucks', 'Pizza Hut', 'KFC', 'Dominos'],
        'Transportation': ['Uber', 'Ola', 'Metro Card', 'BMTC Bus', 'Rapido', 'BluSmart'],
        'Shopping': ['Amazon', 'Flipkart', 'Myntra', 'BigBazaar', 'Reliance Fresh', 'Nike'],
        'Entertainment': ['BookMyShow', 'Netflix', 'Spotify', 'YouTube Premium', 'Disney+', 'Prime Video'],
        'Bills & Utilities': ['Electricity Bill', 'Water Bill', 'Mobile Recharge', 'Broadband', 'Gas Bill'],
        'Healthcare': ['Apollo Pharmacy', '1mg', 'Practo', 'Max Hospital', 'Fortis'],
        'Education': ["Coursera", 'Udemy', "BYJU'S", 'Unacademy', 'Khan Academy'],
        'Income': ['Salary', 'Freelance Payment', 'Investment Returns', 'Cashback']
    }

    locations = ['Bangalore', 'Mumbai', 'Delhi', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata']
    payment_methods = ['UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Cash']

    transactions: List[Dict] = []

    if count is not None:
        try:
            total_transactions = max(0, int(count))
        except (TypeError, ValueError):
            total_transactions = 0
    else:
        total_transactions = random.randint(80, 120)

    if total_transactions == 0:
        return []

    for _ in range(total_transactions):
        category = random.choice(list(categories.keys()))
        merchant = random.choice(categories[category])

        transaction_type = 'income' if category == 'Income' else 'expense'

        if category == 'Food & Dining':
            amount = round(random.uniform(150, 1200), 2)
        elif category == 'Transportation':
            amount = round(random.uniform(50, 800), 2)
        elif category == 'Shopping':
            amount = round(random.uniform(500, 5000), 2)
        elif category == 'Entertainment':
            amount = round(random.uniform(99, 999), 2)
        elif category == 'Bills & Utilities':
            amount = round(random.uniform(200, 3000), 2)
        elif category == 'Healthcare':
            amount = round(random.uniform(100, 2000), 2)
        elif category == 'Education':
            amount = round(random.uniform(299, 1999), 2)
        elif category == 'Income':
            amount = round(random.uniform(5000, 75000), 2)
        else:
            amount = round(random.uniform(100, 2000), 2)

        date = datetime.now(timezone.utc) - timedelta(
            days=random.randint(0, days),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        transaction = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'amount': amount,
            'category': category,
            'description': f'{merchant} payment',
            'merchant': merchant,
            'date': date,
            'type': transaction_type,
            'payment_method': random.choice(payment_methods),
            'location': random.choice(locations)
        }

        transactions.append(transaction)

    return sorted(transactions, key=lambda x: x['date'], reverse=True)
