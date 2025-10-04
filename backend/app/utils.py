import csv
import io
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .config import logger
from .models import Transaction


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


def parse_from_mongo(item):
    if isinstance(item, dict):
        parsed = {}
        for key, value in item.items():
            if key in {'date', 'created_at'} and isinstance(value, str):
                try:
                    parsed[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning("Failed to parse ISO date for key %s: %s", key, value)
                    parsed[key] = datetime.now(timezone.utc)
            elif isinstance(value, dict):
                parsed[key] = parse_from_mongo(value)
            elif isinstance(value, list):
                parsed[key] = [parse_from_mongo(item) if isinstance(item, dict) else item for item in value]
            else:
                parsed[key] = value
        return parsed
    return item


def parse_date_string(date_str: str) -> datetime:
    date_formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%d %b %Y',
        '%d %B %Y',
        '%d-%b-%Y',
        '%d-%B-%Y'
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    logger.warning("Falling back to current time for unparsable date: %s", date_str)
    return datetime.now(timezone.utc)


def categorize_transaction(description: str, merchant: str) -> str:
    description_lower = description.lower()
    merchant_lower = merchant.lower()

    food_keywords = ['zomato', 'swiggy', 'restaurant', 'food', 'cafe', 'pizza', 'burger', 'mcdonald', 'kfc', 'dominos', 'starbucks']
    if any(keyword in description_lower or keyword in merchant_lower for keyword in food_keywords):
        return 'Food & Dining'

    transport_keywords = ['uber', 'ola', 'metro', 'bus', 'taxi', 'fuel', 'petrol', 'diesel', 'transport']
    if any(keyword in description_lower or keyword in merchant_lower for keyword in transport_keywords):
        return 'Transportation'

    shopping_keywords = ['amazon', 'flipkart', 'myntra', 'shopping', 'mall', 'store', 'purchase']
    if any(keyword in description_lower or keyword in merchant_lower for keyword in shopping_keywords):
        return 'Shopping'

    entertainment_keywords = ['netflix', 'spotify', 'movie', 'cinema', 'entertainment', 'bookmyshow', 'game']
    if any(keyword in description_lower or keyword in merchant_lower for keyword in entertainment_keywords):
        return 'Entertainment'

    utility_keywords = ['electricity', 'water', 'gas', 'internet', 'mobile', 'recharge', 'bill', 'utility']
    if any(keyword in description_lower or keyword in merchant_lower for keyword in utility_keywords):
        return 'Bills & Utilities'

    health_keywords = ['hospital', 'pharmacy', 'doctor', 'medical', 'health', 'medicine', 'clinic']
    if any(keyword in description_lower or keyword in merchant_lower for keyword in health_keywords):
        return 'Healthcare'

    investment_keywords = [
        'investment', 'sip', 'mutual fund', 'mutualfund', 'stock', 'stocks', 'equity',
        'portfolio', 'brokerage', 'demat', 'lic policy', 'ppf', 'nps', 'zerodha', 'groww',
        'upstox', 'paytm money', 'icici direct', 'hdfc securities'
    ]
    if any(keyword in description_lower or keyword in merchant_lower for keyword in investment_keywords):
        return 'Investments'

    return 'Others'


def _first_non_empty(row: Dict[str, str], keys: List[str], default: str = '') -> str:
    for key in keys:
        if key in row and row[key]:
            return row[key]
    return default


def _parse_amount(value: Optional[str]) -> Optional[float]:
    if not value:
        return None

    cleaned = value.replace(',', '').replace('₹', '').replace('rs', '').replace('RS', '').replace('INR', '')
    cleaned = cleaned.replace('Dr', '').replace('dr', '').replace('CR', '').replace('Cr', '').strip()
    if cleaned in {'', '-', '--'}:
        return None

    negative = False
    if '(' in cleaned and ')' in cleaned:
        negative = True
        cleaned = cleaned.replace('(', '').replace(')', '')

    if cleaned.startswith('-'):
        negative = True

    try:
        amount = float(cleaned)
    except ValueError:
        return None

    if negative:
        amount = -abs(amount)
    return amount


def parse_csv_transactions(content: str, user_id: str) -> Tuple[List[Transaction], List[str]]:
    transactions: List[Transaction] = []
    errors: List[str] = []

    try:
        if content.startswith('\ufeff'):
            content = content.lstrip('\ufeff')

        csv_reader = csv.DictReader(io.StringIO(content))

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                row_lower: Dict[str, str] = {}
                for key, value in row.items():
                    if not key:
                        continue
                    normalized_key = key.replace('\ufeff', '').lower().strip()
                    if not normalized_key:
                        continue
                    if isinstance(value, str):
                        row_lower[normalized_key] = value.strip()
                    else:
                        row_lower[normalized_key] = value or ''

                debit_raw = _first_non_empty(row_lower, ['debit', 'withdrawal', 'debit amount'])
                credit_raw = _first_non_empty(row_lower, ['credit', 'deposit', 'credit amount'])
                amount_raw = _first_non_empty(row_lower, ['amount', 'transaction_amount', 'txn amount'])

                date_str = _first_non_empty(
                    row_lower,
                    ['date', 'transaction_date', 'value_date', 'tran date', 'txn date', 'transaction dt']
                )

                description = _first_non_empty(
                    row_lower,
                    ['description', 'narration', 'particulars', 'details', 'remarks']
                ) or 'Import'

                merchant = _first_non_empty(
                    row_lower,
                    ['merchant', 'payee', 'counterparty']
                ) or (description.split()[0] if description else 'Unknown')

                cheque_no = row_lower.get('chq no') or row_lower.get('cheque no') or row_lower.get('chq no.')

                debit_amount = _parse_amount(debit_raw)
                credit_amount = _parse_amount(credit_raw)
                generic_amount = _parse_amount(amount_raw)

                transaction_type = 'expense'
                amount = None

                if debit_amount and debit_amount != 0:
                    amount = abs(debit_amount)
                    transaction_type = 'expense'
                elif credit_amount and credit_amount != 0:
                    amount = abs(credit_amount)
                    transaction_type = 'income'
                elif generic_amount and generic_amount != 0:
                    amount = abs(generic_amount)
                    transaction_type = 'income' if generic_amount > 0 else 'expense'

                if not date_str and not any([debit_raw, credit_raw, amount_raw]):
                    continue

                if amount is None or amount == 0:
                    if not any([debit_raw, credit_raw, amount_raw]):
                        continue
                    errors.append(f"Row {row_num}: Invalid amount")
                    continue

                if not date_str:
                    errors.append(f"Row {row_num}: Missing date")
                    continue

                transaction_date = parse_date_string(date_str)

                explicit_category = _first_non_empty(row_lower, ['category', 'category name', 'category_name'])
                if explicit_category:
                    category = explicit_category
                else:
                    category = categorize_transaction(description, merchant)

                if cheque_no:
                    description = f"{description} (Chq: {cheque_no})"

                transaction = Transaction(
                    user_id=user_id,
                    amount=amount,
                    category=category,
                    description=description[:200],
                    merchant=merchant[:100],
                    date=transaction_date,
                    type=transaction_type,
                    payment_method=row_lower.get('payment_method', 'Bank Transfer'),
                    location=row_lower.get('location')
                )

                transactions.append(transaction)

            except Exception as exc:
                logger.exception("Failed to parse row %s", row_num)
                errors.append(f"Row {row_num}: {str(exc)}")
                continue

    except Exception as exc:
        logger.exception("Failed to parse CSV content")
        errors.append(f"Failed to parse CSV: {str(exc)}")

    return transactions, errors
