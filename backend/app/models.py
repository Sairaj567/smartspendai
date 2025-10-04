from datetime import datetime, timezone
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    category: str
    description: str
    merchant: str
    date: datetime
    type: str
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
    timeframe: str = Field(default="3_months")
    title: str
    description: str
    recommendation: str
    priority: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaymentRequest(BaseModel):
    amount: float
    payee_name: str
    payee_vpa: str
    description: str
    user_id: str


class ImportResult(BaseModel):
    total_rows: int
    successful_imports: int
    failed_imports: int
    errors: List[str]
    duplicate_count: int
    imported_transactions: List[Transaction]
