from fastapi import APIRouter

from . import ai, analytics, payments, transactions


def get_api_router() -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/")
    async def root():
        return {"message": "SpendSmart - AI Backend Ready"}

    router.include_router(transactions.router)
    router.include_router(analytics.router)
    router.include_router(ai.router)
    router.include_router(payments.router)
    return router
