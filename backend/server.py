from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Gemini AI Chat setup
gemini_api_key = os.environ.get('EMERGENT_LLM_KEY')

# Models
class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    category: str
    description: str
    merchant: str
    date: datetime
    type: str  # 'expense' or 'income'
    payment_method: str
    location: Optional[str] = None

class TransactionCreate(BaseModel):
    user_id: str
    amount: float
    category: str
    description: str
    merchant: str
    type: str = 'expense'
    payment_method: str = 'UPI'
    location: Optional[str] = None

class BudgetAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    category: str
    budget_limit: float
    current_spent: float
    alert_threshold: float
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SpendingInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    insight_type: str
    title: str
    description: str
    recommendation: str
    priority: str  # 'high', 'medium', 'low'
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentRequest(BaseModel):
    amount: float
    payee_name: str
    payee_vpa: str
    description: str
    user_id: str

# Sample data generation functions
def generate_mock_transactions(user_id: str, days: int = 30) -> List[Dict]:
    categories = {
        'Food & Dining': ['Zomato', 'Swiggy', 'McDonald\'s', 'Starbucks', 'Pizza Hut', 'KFC', 'Dominos'],
        'Transportation': ['Uber', 'Ola', 'Metro Card', 'BMTC Bus', 'Rapido', 'BluSmart'],
        'Shopping': ['Amazon', 'Flipkart', 'Myntra', 'BigBazaar', 'Reliance Fresh', 'Nike'],
        'Entertainment': ['BookMyShow', 'Netflix', 'Spotify', 'YouTube Premium', 'Disney+', 'Prime Video'],
        'Bills & Utilities': ['Electricity Bill', 'Water Bill', 'Mobile Recharge', 'Broadband', 'Gas Bill'],
        'Healthcare': ['Apollo Pharmacy', '1mg', 'Practo', 'Max Hospital', 'Fortis'],
        'Education': ['Coursera', 'Udemy', 'BYJU\'S', 'Unacademy', 'Khan Academy'],
        'Income': ['Salary', 'Freelance Payment', 'Investment Returns', 'Cashback']
    }
    
    locations = ['Bangalore', 'Mumbai', 'Delhi', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata']
    payment_methods = ['UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Cash']
    
    transactions = []
    
    for i in range(random.randint(80, 120)):  # 80-120 transactions in the period
        category = random.choice(list(categories.keys()))
        merchant = random.choice(categories[category])
        
        # Determine transaction type
        transaction_type = 'income' if category == 'Income' else 'expense'
        
        # Generate realistic amounts based on category
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
        
        # Generate date within the last 'days' period
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

# Helper function to prepare data for MongoDB
def prepare_for_mongo(data):
    if isinstance(data, dict):
        prepared = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                prepared[key] = value.isoformat()
            elif isinstance(value, dict):
                prepared[key] = prepare_for_mongo(value)
            elif isinstance(value, list):
                prepared[key] = [prepare_for_mongo(item) if isinstance(item, dict) else item for item in value]
            else:
                prepared[key] = value
        return prepared
    return data

# Helper function to parse data from MongoDB
def parse_from_mongo(item):
    if isinstance(item, dict):
        parsed = {}
        for key, value in item.items():
            if key == 'date' and isinstance(value, str):
                try:
                    parsed[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    parsed[key] = datetime.now(timezone.utc)
            elif key == 'created_at' and isinstance(value, str):
                try:
                    parsed[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    parsed[key] = datetime.now(timezone.utc)
            elif isinstance(value, dict):
                parsed[key] = parse_from_mongo(value)
            elif isinstance(value, list):
                parsed[key] = [parse_from_mongo(item) if isinstance(item, dict) else item for item in value]
            else:
                parsed[key] = value
        return parsed
    return item

# API Routes
@api_router.get("/")
async def root():
    return {"message": "SpendSmart - AI Backend Ready"}

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    transaction_dict = transaction.dict()
    transaction_dict['date'] = datetime.now(timezone.utc)
    transaction_obj = Transaction(**transaction_dict)
    
    prepared_data = prepare_for_mongo(transaction_obj.dict())
    await db.transactions.insert_one(prepared_data)
    return transaction_obj

@api_router.get("/transactions/{user_id}", response_model=List[Transaction])
async def get_user_transactions(user_id: str, limit: int = 50):
    transactions = await db.transactions.find(
        {"user_id": user_id}
    ).sort("date", -1).limit(limit).to_list(length=None)
    
    return [Transaction(**parse_from_mongo(transaction)) for transaction in transactions]

@api_router.post("/transactions/generate/{user_id}")
async def generate_demo_transactions(user_id: str):
    # Check if user already has transactions
    existing_count = await db.transactions.count_documents({"user_id": user_id})
    
    if existing_count > 0:
        return {"message": f"User already has {existing_count} transactions"}
    
    mock_transactions = generate_mock_transactions(user_id)
    
    # Prepare for MongoDB
    prepared_transactions = [prepare_for_mongo(tx) for tx in mock_transactions]
    
    await db.transactions.insert_many(prepared_transactions)
    
    return {
        "message": f"Generated {len(mock_transactions)} demo transactions for user {user_id}",
        "count": len(mock_transactions)
    }

@api_router.get("/analytics/spending-summary/{user_id}")
async def get_spending_summary(user_id: str):
    # Get transactions from last 30 days
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    transactions = await db.transactions.find({
        "user_id": user_id,
        "date": {"$gte": thirty_days_ago.isoformat()}
    }).to_list(length=None)
    
    # Parse transactions
    parsed_transactions = [parse_from_mongo(tx) for tx in transactions]
    
    # Calculate summary
    total_expenses = sum(tx['amount'] for tx in parsed_transactions if tx['type'] == 'expense')
    total_income = sum(tx['amount'] for tx in parsed_transactions if tx['type'] == 'income')
    
    # Category breakdown
    category_spending = {}
    for tx in parsed_transactions:
        if tx['type'] == 'expense':
            category = tx['category']
            category_spending[category] = category_spending.get(category, 0) + tx['amount']
    
    # Top categories
    top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_expenses": round(total_expenses, 2),
        "total_income": round(total_income, 2),
        "net_savings": round(total_income - total_expenses, 2),
        "transaction_count": len(parsed_transactions),
        "top_categories": [{
            "category": cat,
            "amount": round(amount, 2),
            "percentage": round((amount / total_expenses) * 100, 1) if total_expenses > 0 else 0
        } for cat, amount in top_categories],
        "category_breakdown": {cat: round(amount, 2) for cat, amount in category_spending.items()}
    }

@api_router.get("/analytics/spending-trends/{user_id}")
async def get_spending_trends(user_id: str, days: int = 30):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    transactions = await db.transactions.find({
        "user_id": user_id,
        "date": {"$gte": start_date.isoformat()},
        "type": "expense"
    }).to_list(length=None)
    
    parsed_transactions = [parse_from_mongo(tx) for tx in transactions]
    
    # Daily spending trends
    daily_spending = {}
    for tx in parsed_transactions:
        date_key = tx['date'].strftime('%Y-%m-%d')
        daily_spending[date_key] = daily_spending.get(date_key, 0) + tx['amount']
    
    # Fill missing dates with 0
    trends = []
    current_date = start_date
    while current_date <= datetime.now(timezone.utc):
        date_key = current_date.strftime('%Y-%m-%d')
        trends.append({
            "date": date_key,
            "amount": round(daily_spending.get(date_key, 0), 2)
        })
        current_date += timedelta(days=1)
    
    return {
        "trends": trends,
        "average_daily_spending": round(sum(daily_spending.values()) / len(trends), 2) if trends else 0
    }

@api_router.post("/ai/insights/{user_id}")
async def generate_ai_insights(user_id: str):
    try:
        # Get user's spending data
        summary = await get_spending_summary(user_id)
        trends = await get_spending_trends(user_id)
        
        # Initialize Gemini chat
        chat = LlmChat(
            api_key=gemini_api_key,
            session_id=f"insights-{user_id}",
            system_message="You are a financial advisor AI. Analyze spending patterns and provide personalized insights and recommendations. Be concise, practical, and focus on actionable advice."
        ).with_model("gemini", "gemini-2.5-pro")
        
        # Create prompt with user's financial data
        prompt = f"""
        Analyze this user's spending data and provide 3-4 key insights with actionable recommendations:
        
        Financial Summary (Last 30 days):
        - Total Expenses: ₹{summary['total_expenses']}
        - Total Income: ₹{summary['total_income']}
        - Net Savings: ₹{summary['net_savings']}
        - Transaction Count: {summary['transaction_count']}
        
        Top Spending Categories:
        {json.dumps(summary['top_categories'], indent=2)}
        
        Average Daily Spending: ₹{trends['average_daily_spending']}
        
        Provide insights in this JSON format:
        [
          {{
            "title": "Brief insight title",
            "description": "Detailed analysis",
            "recommendation": "Specific actionable advice",
            "priority": "high/medium/low",
            "category": "savings/spending/budgeting/optimization"
          }}
        ]
        
        Focus on practical advice for Indian users with UPI payments.
        """
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse AI response
        try:
            insights_data = json.loads(response)
            if not isinstance(insights_data, list):
                raise ValueError("Response is not a list")
        except:
            # Fallback if JSON parsing fails
            insights_data = [{
                "title": "AI Analysis Complete",
                "description": response[:200] + "..." if len(response) > 200 else response,
                "recommendation": "Review your spending patterns and consider setting up a budget.",
                "priority": "medium",
                "category": "general"
            }]
        
        # Store insights in database
        insights_to_store = []
        for insight_data in insights_data:
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
            "insights": insights_data,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@api_router.get("/ai/insights/{user_id}")
async def get_user_insights(user_id: str, limit: int = 10):
    insights = await db.spending_insights.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit).to_list(length=None)
    
    return [SpendingInsight(**parse_from_mongo(insight)) for insight in insights]

@api_router.post("/payments/upi-intent")
async def create_upi_payment(payment: PaymentRequest):
    # Generate UPI intent URL (mock for now)
    transaction_id = str(uuid.uuid4())[:8]
    
    upi_url = f"upi://pay?pa={payment.payee_vpa}&pn={payment.payee_name}&am={payment.amount}&cu=INR&tn={payment.description}&tid={transaction_id}"
    
    # Store payment request
    payment_record = {
        "id": transaction_id,
        "user_id": payment.user_id,
        "amount": payment.amount,
        "payee_name": payment.payee_name,
        "payee_vpa": payment.payee_vpa,
        "description": payment.description,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "upi_url": upi_url
    }
    
    await db.payment_requests.insert_one(payment_record)
    
    return {
        "transaction_id": transaction_id,
        "upi_url": upi_url,
        "status": "pending",
        "message": "Payment intent created. Redirecting to UPI app..."
    }

@api_router.post("/payments/callback/{transaction_id}")
async def payment_callback(transaction_id: str, status: str):
    # Update payment status based on callback
    await db.payment_requests.update_one(
        {"id": transaction_id},
        {"$set": {
            "status": status,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if status == "success":
        # Add transaction to user's history
        payment_record = await db.payment_requests.find_one({"id": transaction_id})
        if payment_record:
            transaction = Transaction(
                user_id=payment_record["user_id"],
                amount=payment_record["amount"],
                category="Transfer",
                description=payment_record["description"],
                merchant=payment_record["payee_name"],
                type="expense",
                payment_method="UPI"
            )
            await db.transactions.insert_one(prepare_for_mongo(transaction.dict()))
    
    return {"status": status, "transaction_id": transaction_id}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
