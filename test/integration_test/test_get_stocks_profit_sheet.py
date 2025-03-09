import pytest
import time
import requests

from datetime import datetime

from data import get, constant


NOW = datetime.now()

THIS_QUARTER_YEAR = NOW.year
THIS_QUARTER = NOW.month // 4 + 1

if THIS_QUARTER == 1:
    LAST_QUARTER_YEAR = THIS_QUARTER_YEAR - 1
    LAST_QUARTER = 4
else:
    LAST_QUARTER_YEAR = THIS_QUARTER_YEAR
    LAST_QUARTER = THIS_QUARTER - 1

if LAST_QUARTER == 1:
    LAST_LAST_QUARTER_YEAR = LAST_QUARTER_YEAR - 1
    LAST_LAST_QUARTER = 4
else:
    LAST_LAST_QUARTER_YEAR = LAST_QUARTER_YEAR
    LAST_LAST_QUARTER = LAST_QUARTER - 1


def _call_get_stocks_profit_sheet(year: int, stock_type: str, quarter: int):
    for _ in range(5):
        try:
            return get("stocks_profit_sheet", year=year, stock_type=stock_type, quarter=quarter)
        except requests.exceptions.HTTPError as e:
            print(e)
            time.sleep(3.14)
    raise Exception("Unable to get stocks_profit_sheet")


@pytest.mark.parametrize("stock_type", [x.value for x in constant.StockType])
def test_get_this_quarter(stock_type):
    results = _call_get_stocks_profit_sheet(THIS_QUARTER_YEAR, stock_type, THIS_QUARTER)
    assert results == []


@pytest.mark.parametrize("stock_type", [x.value for x in constant.StockType])
def test_get_last_quarter(stock_type):
    results = _call_get_stocks_profit_sheet(LAST_QUARTER_YEAR, stock_type, LAST_QUARTER)
    assert isinstance(results, list)


@pytest.mark.parametrize("stock_type", [x.value for x in constant.StockType])
def test_get_last_last_quarter(stock_type):
    results = _call_get_stocks_profit_sheet(LAST_LAST_QUARTER_YEAR, stock_type, LAST_LAST_QUARTER)

    assert results != []
    for result in results:
        assert isinstance(result, dict)

        for basic_key in [
            "id",
            "operating_revenue",
            "operating_revenue_detail",
            "profit_before_tax",
            "income_tax",
            "profit",
            "other_profit",
            "other_profit_from_merged_company",
            "comprehensive_profit",
            "profit_detail",
            "comprehensive_profit_detail",
            "eps",
            ]:
                assert basic_key in result
