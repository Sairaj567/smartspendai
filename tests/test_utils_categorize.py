import pytest

from backend.app.utils import categorize_transaction


@pytest.mark.parametrize(
    "description, merchant, expected",
    [
        ("UPI-MOMOS-HUB BLR", "VPA-xyz@upi", "Food & Dining"),
        ("upi/dmart/koramangala", "DMART123", "Groceries"),
        ("Reliance Fresh Indiranagar", "Reliance Fresh", "Groceries"),
    ],
)
def test_categorize_transaction_extended_keywords(description, merchant, expected):
    assert categorize_transaction(description, merchant) == expected
