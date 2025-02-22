import pytest

from datetime import date

from data import get


@pytest.mark.parametrize(
    "expect_price", [
        {'date': date(2025, 2, 19).isoformat(), 'opening': '23589.44', 'highest': '23683.46', 'lowest': '23550.99', 'closing': '23604.08', 'volume': '389394000000'}
])
def test_get_tw_2y_index(expect_price):
    results = get("tw_2y_index")

    assert expect_price in results
