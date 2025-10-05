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
        self.openrouter_api_key: str = os.environ.get('OPENROUTER_API_KEY', '')
        self.openrouter_model: str = os.environ.get('OPENROUTER_MODEL', 'openai/gpt-4o-mini')
        self.openrouter_app_url: str = os.environ.get('OPENROUTER_APP_URL', '')
        self.openrouter_app_name: str = os.environ.get('OPENROUTER_APP_NAME', 'SmartSpendAI')
        self.openrouter_base_url: str = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        timeout_raw = os.environ.get('OPENROUTER_TIMEOUT', '30')
        try:
            self.openrouter_timeout: float = float(timeout_raw)
        except (TypeError, ValueError):
            self.openrouter_timeout = 30.0

        emergency_fund_multiplier_raw = os.environ.get('EMERGENCY_FUND_MULTIPLIER', '6')
        try:
            self.emergency_fund_multiplier: float = max(0.0, float(emergency_fund_multiplier_raw))
        except (TypeError, ValueError):
            self.emergency_fund_multiplier = 6.0

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(',') if origin]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
