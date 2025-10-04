from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, HTTPException

from ..config import logger
from ..database import get_database
from ..models import PaymentRequest, Transaction
from ..utils import prepare_for_mongo

router = APIRouter(prefix="/payments", tags=["payments"])

db = get_database()


@router.post("/upi-intent")
async def create_upi_payment(payment: PaymentRequest):
    transaction_id = str(uuid.uuid4())[:8]

    upi_url = (
        f"upi://pay?pa={payment.payee_vpa}&pn={payment.payee_name}"
        f"&am={payment.amount}&cu=INR&tn={payment.description}&tid={transaction_id}"
    )

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

    try:
        await db.payment_requests.insert_one(payment_record)
    except Exception as exc:
        logger.exception("Database error while creating payment intent")
        raise HTTPException(status_code=500, detail="Failed to create payment request") from exc

    return {
        "transaction_id": transaction_id,
        "upi_url": upi_url,
        "status": "pending",
        "message": "Payment intent created. Redirecting to UPI app..."
    }


@router.post("/callback/{transaction_id}")
async def payment_callback(transaction_id: str, status: str):
    try:
        await db.payment_requests.update_one(
            {"id": transaction_id},
            {"$set": {
                "status": status,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    except Exception as exc:
        logger.exception("Database error while updating payment status")
        raise HTTPException(status_code=500, detail="Failed to update payment status") from exc

    if status == "success":
        try:
            payment_record = await db.payment_requests.find_one({"id": transaction_id})
        except Exception as exc:
            logger.exception("Database error while fetching payment record")
            raise HTTPException(status_code=500, detail="Failed to fetch payment record") from exc

        if payment_record:
            transaction = Transaction(
                user_id=payment_record["user_id"],
                amount=payment_record["amount"],
                category="Transfer",
                description=payment_record["description"],
                merchant=payment_record["payee_name"],
                date=datetime.now(timezone.utc),
                type="expense",
                payment_method="UPI"
            )
            try:
                await db.transactions.insert_one(prepare_for_mongo(transaction.dict()))
            except Exception as exc:
                logger.exception("Failed to save transaction generated from payment callback")
                raise HTTPException(status_code=500, detail="Failed to record payment transaction") from exc

    return {"status": status, "transaction_id": transaction_id}
