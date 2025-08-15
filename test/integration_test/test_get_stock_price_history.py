from datetime import date, timedelta

import pytest

from data import get
from data.exception import WrongDataFormat


@pytest.mark.parametrize("stock_id, start_date, end_date, expect_start_price, expect_end_price", [
    ("2330", date(2025, 8, 15), date(2025, 8, 16), (1175.0, 1180.0, 1185.0, 1170.0, 23577178), (1175.0, 1180.0, 1185.0, 1170.0, 23577178)),
    ("2330", date(2025, 5, 2), date(2025, 8, 15), (938.0, 950.0, 950.0, 932.0, 48129292), (1185.0, 1175.0, 1190.0, 1175.0, 35269337)),
])
def test_get_stock_price_history(stock_id, start_date, end_date, expect_start_price, expect_end_price):
    results = get("stock_price_history", stock_id=stock_id, start_date_included=start_date.isoformat(), end_date_excluded=end_date.isoformat())

    if expect_start_price is not None:
        assert start_date.isoformat() in results
        assert results[start_date.isoformat()] == expect_start_price

    if expect_end_price is not None:
        end_date = (end_date - timedelta(days=1)).isoformat()
        assert end_date in results
        assert results[end_date] == expect_end_price


def test_get_stock_price_history_start_date_is_holiday():
    expect_start_date = date(2025, 5, 2)
    results = get("stock_price_history", stock_id="2330", start_date_included=expect_start_date.isoformat())

    assert expect_start_date.isoformat() in results
    assert results[expect_start_date.isoformat()] == (938.0, 950.0, 950.0, 932.0, 48129292)


def test_get_stock_price_history_for_none_stock():
    with pytest.raises(WrongDataFormat):
        get("stock_price_history", stock_id="99999", start_date_included=date.today().isoformat())
