import pytest
import time

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


@pytest.mark.parametrize("stock_type", [x.value for x in constant.StockType])
def test_get_this_quarter(stock_type):
    results = get("stocks_balance_sheet", year=THIS_QUARTER_YEAR, stock_type=stock_type, quarter=THIS_QUARTER)
    time.sleep(2.12)
    assert results == []


@pytest.mark.parametrize("stock_type", [x.value for x in constant.StockType])
def test_get_last_quarter(stock_type):
    results = get("stocks_balance_sheet", year=LAST_QUARTER_YEAR, stock_type=stock_type, quarter=LAST_QUARTER)
    time.sleep(3.32)
    assert isinstance(results, list)


@pytest.mark.parametrize("stock_type", [x.value for x in constant.StockType])
def test_get_last_last_quarter(stock_type):
    results = get("stocks_balance_sheet", year=LAST_LAST_QUARTER_YEAR, stock_type=stock_type, quarter=LAST_LAST_QUARTER)
    time.sleep(1.92)

    assert results != []
    for result in results:
        assert isinstance(result, dict)

        for basic_key in [
            "id",
            "assets",
            "liabilities",

            "share_capital",
            "capital_surplus",
            "retained_earnings",
            "other_equity",
            "treasure_stock",

            "total_equity_of_this_company",
            "equity_of_child_merge_from",
            "non_control_equity",
            "equity",

            "net_worth",
            ]:
                assert basic_key in result
