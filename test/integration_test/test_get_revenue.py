import pytest
import time
import requests

from datetime import datetime

from data import get, constant


NOW = datetime.now()

THIS_MONTH_YEAR = NOW.year
THIS_MONTH = NOW.month

if THIS_MONTH == 1:
    LAST_MONTH_YEAR = THIS_MONTH_YEAR - 1
    LAST_MONTH = 12
else:
    LAST_MONTH_YEAR = THIS_MONTH_YEAR
    LAST_MONTH = THIS_MONTH - 1

if LAST_MONTH == 1:
    LAST_LAST_MONTH_YEAR = LAST_MONTH_YEAR - 1
    LAST_LAST_MONTH = 12
else:
    LAST_LAST_MONTH_YEAR = LAST_MONTH_YEAR
    LAST_LAST_MONTH = LAST_MONTH - 1


def _call_get_revenue(year: int, month: int, stock_type: constant.StockType):
    for i in range(5):
        try:
            return get("revenue", year=year, stock_type=stock_type.value, month=month, timeout=60)
        except requests.exceptions.HTTPError as e:
            print(e)
            time.sleep(3.14 * (i + 1))
    raise Exception("Unable to get stocks_balance_sheet")


@pytest.mark.parametrize("stock_type", [x for x in constant.StockType])
def test_get_this_month(stock_type):
    results = _call_get_revenue(THIS_MONTH_YEAR, THIS_MONTH, stock_type)
    assert results == []


@pytest.mark.parametrize("stock_type", [x for x in constant.StockType])
def test_get_last_month(stock_type):
    results = _call_get_revenue(LAST_MONTH_YEAR, LAST_MONTH, stock_type)
    assert isinstance(results, list)


@pytest.mark.parametrize("stock_type", [x for x in constant.StockType])
def test_get_last_last_month(stock_type):
    results = _call_get_revenue(LAST_LAST_MONTH_YEAR, LAST_LAST_MONTH, stock_type)

    assert results != []
    for result in results:
        assert isinstance(result, dict)

        for basic_key in [
            "stock_id",
            "stock_name",
            "create_time",
            "year",
            "month",
            "value",
            "last_month",
            "last_year",
            "last_month_percent",
            "last_year_percent",
            "accumulation",
            "last_year_accumulation",
            "last_year_accumulation_percent",
            "note",
            ]:
                assert basic_key in result
