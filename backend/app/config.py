import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / '.env')


def setup_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("backend")


logger = setup_logging()


class Settings:
    """Application settings sourced from environment variables."""

    def __init__(self) -> None:
        self.mongo_url: str = os.environ.get('MONGO_URL', '')
        self.db_name: str = os.environ.get('DB_NAME', 'smartspend')
        self.allowed_origins_raw: str = os.environ.get('CORS_ORIGINS', '*')
        self.app_title: str = os.environ.get('APP_TITLE', 'SpendSmart AI Backend')

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(',') if origin]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
