"""Helpers for categorizing transactions using OpenRouter models."""
from __future__ import annotations

import asyncio
import json
import re
import time
from collections import OrderedDict
from typing import TYPE_CHECKING, Dict, Iterable, Optional

import httpx

from ..config import get_settings, logger

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from ..models import Transaction

_CATEGORY_CANONICAL = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Income",
    "Savings",
    "Investments",
    "Travel",
    "Groceries",
    "Rent",
    "Others",
]

_CATEGORY_ALIASES: Dict[str, set[str]] = {
    "Food & Dining": {"food", "dining", "restaurant", "restaurants", "eating out"},
    "Transportation": {"transport", "commute", "fuel", "taxi", "cab", "ride"},
    "Shopping": {"retail", "ecommerce", "store", "mall", "purchase"},
    "Entertainment": {"movies", "music", "games", "subscriptions", "leisure"},
    "Bills & Utilities": {"utilities", "utility", "bill", "bills", "recharge", "electricity", "water", "gas"},
    "Healthcare": {"medical", "health", "doctor", "pharmacy", "hospital"},
    "Education": {"learning", "courses", "tuition", "study"},
    "Income": {"salary", "paycheck", "pay", "income", "credit", "deposit"},
    "Savings": {"savings", "saving"},
    "Investments": {"investment", "investments", "stocks", "mutual funds", "sip"},
    "Travel": {"travel", "trip", "hotel", "flight", "vacation"},
    "Groceries": {"grocery", "groceries", "supermarket"},
    "Rent": {"rent", "rental", "lease"},
    "Others": {"other", "misc", "miscellaneous", "general", "uncategorized", "unknown"},
}

class _TTLCache:
    def __init__(self, maxsize: int, ttl: float) -> None:
        self.maxsize = maxsize
        self.ttl = ttl
        self._store: "OrderedDict[str, tuple[float, str]]" = OrderedDict()

    def get(self, key: str) -> Optional[str]:
        record = self._store.get(key)
        if not record:
            return None
        expires_at, value = record
        now = time.monotonic()
        if expires_at <= now:
            self._store.pop(key, None)
            return None
        self._store.move_to_end(key)
        return value

    def __setitem__(self, key: str, value: str) -> None:
        expires_at = time.monotonic() + self.ttl
        self._store[key] = (expires_at, value)
        self._store.move_to_end(key)
        if len(self._store) > self.maxsize:
            self._store.popitem(last=False)


_CACHE = _TTLCache(maxsize=1024, ttl=60 * 60 * 24)
_SEMAPHORE = asyncio.Semaphore(3)


def _normalise_category(text: str) -> Optional[str]:
    clean = text.strip().lower()
    if not clean:
        return None

    for canonical in _CATEGORY_CANONICAL:
        if clean == canonical.lower():
            return canonical

    # exact alias match
    for canonical, aliases in _CATEGORY_ALIASES.items():
        if clean in aliases:
            return canonical

    # search for canonical tokens inside text
    for canonical in _CATEGORY_CANONICAL:
        if canonical.lower() in clean:
            return canonical

    # search for alias tokens inside text
    for canonical, aliases in _CATEGORY_ALIASES.items():
        if any(alias in clean for alias in aliases):
            return canonical

    return None


def _should_classify(category: Optional[str]) -> bool:
    if not category:
        return True
    category_lower = category.strip().lower()
    return category_lower in {
        "others",
        "other",
        "misc",
        "miscellaneous",
        "uncategorized",
        "unknown",
        "general",
        "auto",
        "autodetect",
        "category",
    }


def openrouter_available() -> bool:
    settings = get_settings()
    return bool(settings.openrouter_api_key and settings.openrouter_model)


async def classify_transaction_via_openrouter(
    *,
    description: str,
    merchant: Optional[str],
    amount: Optional[float],
    transaction_type: Optional[str],
    current_category: Optional[str] = None,
    allow_override: bool = False,
) -> Optional[str]:
    """Return a refined category for a transaction using OpenRouter if configured."""

    if not openrouter_available():
        return None

    if not allow_override and not _should_classify(current_category):
        return None

    key_elements = [description or "", merchant or "", str(round(amount or 0, 2)), (transaction_type or "").lower()]
    cache_key = "|".join(key_elements)
    cached = _CACHE.get(cache_key)
    if cached:
        return cached

    settings = get_settings()

    user_message = (
        "Classify the following bank transaction into the best matching category. "
        "Respond with a JSON object like {\"category\": \"Category Name\"}.\n\n"
        f"Description: {description}\n"
        f"Merchant: {merchant or 'Unknown'}\n"
        f"Amount: {amount if amount is not None else 'Unknown'}\n"
        f"Type: {transaction_type or 'Unknown'}\n"
        f"Current category guess: {current_category or 'None'}\n\n"
        "Valid categories: " + ", ".join(_CATEGORY_CANONICAL)
    )

    payload = {
        "model": settings.openrouter_model,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert financial assistant that categorizes banking transactions. "
                    "Choose the single most appropriate category from the provided list and respond with valid JSON."
                ),
            },
            {"role": "user", "content": user_message},
        ],
    }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    if settings.openrouter_app_url:
        headers["HTTP-Referer"] = settings.openrouter_app_url
    if settings.openrouter_app_name:
        headers["X-Title"] = settings.openrouter_app_name

    try:
        async with _SEMAPHORE:
            async with httpx.AsyncClient(base_url=settings.openrouter_base_url, timeout=settings.openrouter_timeout) as client:
                response = await client.post("/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
    except (httpx.HTTPError, asyncio.TimeoutError) as exc:
        logger.warning("OpenRouter classification failed: %s", exc)
        return None

    try:
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return None
        content = choices[0]["message"].get("content", "")
    except (ValueError, KeyError, TypeError) as exc:
        logger.warning("Unexpected OpenRouter response format: %s", exc)
        return None

    category_text = _parse_category_from_content(content)
    category = _normalise_category(category_text) if category_text else None

    if category:
        _CACHE[cache_key] = category
    else:
        logger.info("OpenRouter returned unrecognised category: %s", category_text)

    return category


def _parse_category_from_content(content: str) -> Optional[str]:
    if not content:
        return None

    text = content.strip()

    # Attempt JSON decoding first.
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            for key in ("category", "label", "result"):
                if key in parsed and isinstance(parsed[key], str):
                    return parsed[key]
        if isinstance(parsed, list) and parsed:
            first_item = parsed[0]
            if isinstance(first_item, str):
                return first_item
            if isinstance(first_item, dict):
                for key in ("category", "label", "result"):
                    value = first_item.get(key)
                    if isinstance(value, str):
                        return value
    except json.JSONDecodeError:
        pass

    # If not JSON, strip to first word/line that looks like a category.
    first_line = text.splitlines()[0]
    match = re.search(r"([A-Za-z &]+)", first_line)
    if match:
        return match.group(1).strip()

    return first_line.strip() if first_line else None


async def enrich_transactions_with_ai(
    transactions: Iterable["Transaction"],
    *,
    allow_override: bool = False,
) -> Dict[str, str]:
    """Attempt to improve categories using OpenRouter; returns mapping of transaction id to new category."""
    if not openrouter_available():
        return {}

    tasks = []
    transactions_list = list(transactions)
    for tx in transactions_list:
        try:
            current_category = getattr(tx, "category", None)
            if not allow_override and not _should_classify(current_category):
                continue
            description = getattr(tx, "description", "")
            merchant = getattr(tx, "merchant", None)
            amount = getattr(tx, "amount", None)
            transaction_type = getattr(tx, "type", None)
            tasks.append(
                _classify_and_update(
                    tx,
                    description=description,
                    merchant=merchant,
                    amount=amount,
                    transaction_type=transaction_type,
                    current_category=current_category,
                    allow_override=allow_override,
                )
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Skipping transaction during AI categorisation: %s", exc)
            continue

    if not tasks:
        return {}

    results = await asyncio.gather(*tasks, return_exceptions=True)
    updated: Dict[str, str] = {}
    for result in results:
        if isinstance(result, Exception):  # pragma: no cover - already logged in callee
            continue
        if result:
            tx_id, category = result
            updated[tx_id] = category
    return updated


async def _classify_and_update(
    transaction: "Transaction",
    *,
    description: str,
    merchant: Optional[str],
    amount: Optional[float],
    transaction_type: Optional[str],
    current_category: Optional[str],
    allow_override: bool,
) -> Optional[tuple[str, str]]:
    category = await classify_transaction_via_openrouter(
        description=description,
        merchant=merchant,
        amount=amount,
        transaction_type=transaction_type,
        current_category=current_category,
        allow_override=allow_override,
    )
    if category:
        try:
            transaction.category = category
        except (AttributeError, TypeError):  # pragma: no cover - pydantic fallback
            if hasattr(transaction, "model_copy"):
                new_tx = transaction.model_copy(update={"category": category})
                transaction.__dict__.update(new_tx.__dict__)
        return getattr(transaction, "id", id(transaction)), category
    return None


__all__ = [
    "classify_transaction_via_openrouter",
    "enrich_transactions_with_ai",
    "openrouter_available",
]
