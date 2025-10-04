from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import get_settings, logger


class DatabaseManager:
    """Wrapper for MongoDB client lifecycle management."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.mongo_url:
            logger.error("MONGO_URL environment variable is not set")
            raise RuntimeError("Database connection string is missing. Set MONGO_URL.")

        try:
            self.client = AsyncIOMotorClient(settings.mongo_url)
            self.database = self.client[settings.db_name]
            logger.info("Connected to MongoDB: %s", settings.db_name)
        except Exception as exc:  # pragma: no cover - connection failure
            logger.exception("Failed to initialize MongoDB client")
            raise RuntimeError("Failed to connect to MongoDB") from exc

    def get_database(self) -> AsyncIOMotorDatabase:
        return self.database

    async def close(self) -> None:
        self.client.close()
        logger.info("MongoDB client connection closed")


_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_database() -> AsyncIOMotorDatabase:
    return get_db_manager().get_database()
