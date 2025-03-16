import pytest

from datetime import date

from data import get


@pytest.mark.parametrize(
    "expect_price", [
        {'date': date(2025, 3, 14).isoformat(), 'opening': '21986.81', 'highest': '22074.03', 'lowest': '21895.9', 'closing': '21968.05', 'volume': '348017000000', 'margin_financing_balance': '325695000000', 'short_selling_amount': '235795000', 'day_trading_amount': '6402000'}
])
def test_get_tw_2y_index(expect_price):
    results = get("tw_2y_index")

    assert expect_price in results
