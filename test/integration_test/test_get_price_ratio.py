import pytest

from datetime import datetime, date

from data import get
from data.exception import WebsiteMaintaince
from data.constant import StockType


@pytest.fixture(params=[StockType.PUBLIC, StockType.OTC])
def price_ratio_stock_type(request):
    return request.param.value


@pytest.mark.parametrize("query_date, stock_type, expect_price_ratio", [
    (
        date(year=2009, month=2, day=12), StockType.PUBLIC, {
            'year': '2009', 
            'month': '2', 
            'stock_id': '8070', 
            'close_price': None, 
            'return_rate': '17.46', 
            'dividend_year': None, 
            'per': '9.62', 
            'pa': '1.03', 
            'calculated_financial_year': None, 
            'calculated_financial_quarter': None
        },
    ),
    (
        date(year=2017, month=1, day=1), StockType.PUBLIC, {
            'year': '2016', 
            'month': '12', 
            'stock_id': '9945', 
            'close_price': None, 
            'return_rate': '0', 
            'dividend_year': None, 
            'per': '7.93', 
            'pa': '1.46', 
            'calculated_financial_year': None, 
            'calculated_financial_quarter': None
        },
    ),
    (
        date(year=2025, month=2, day=4), StockType.PUBLIC, {
            'year': '2025', 
            'month': '2', 
            'stock_id': '2910', 
            'close_price': '24.90', 
            'return_rate': '1.37', 
            'dividend_year': '2023', 
            'per': '20.92', 
            'pa': '1.63', 
            'calculated_financial_year': '2024', 
            'calculated_financial_quarter': '3'
        },
    ),
    (
        date(year=2009, month=11, day=3), StockType.OTC, {
            'year': '2009', 
            'month': '11', 
            'stock_id': '3498', 
            'close_price': None, 
            'return_rate': '4.4', 
            'dividend_year': '2008', 
            'per': '8.36', 
            'pa': '1.45', 
            'calculated_financial_year': None, 
            'calculated_financial_quarter': None
        },
    ),
    (
        date(year=2025, month=1, day=22), StockType.OTC, {
            'year': '2025', 
            'month': '1', 
            'stock_id': '4416', 
            'close_price': None, 
            'return_rate': '2.62', 
            'dividend_year': '2024', 
            'per': '948.75', 
            'pa': '3.03', 
            'calculated_financial_year': '2024', 
            'calculated_financial_quarter': '3'
        },
    ),
])
def test_get_price_ratio(query_date, stock_type, expect_price_ratio):
    results = get("price_ratio", query_date=query_date.isoformat(), stock_type=stock_type.value)

    expect_stock_id_results = [result for result in results if result["stock_id"] == expect_price_ratio["stock_id"]]
    assert expect_stock_id_results
    
    assert expect_stock_id_results[0] == expect_price_ratio


def test_get_latest_price_ratio(price_ratio_stock_type):
    now = datetime.now().date().isoformat()

    results = get("price_ratio", query_date=now, stock_type=price_ratio_stock_type)
    assert isinstance(results, list)
    assert all(isinstance(result, dict) for result in results)


def test_get_no_price_ratio_error(price_ratio_stock_type):
    with pytest.raises(WebsiteMaintaince):
        get("price_ratio", query_date=date(year=3000, month=2, day=12).isoformat(), stock_type=price_ratio_stock_type)


def test_get_price_ratio_not_support_rotc():
    with pytest.raises(KeyError):
        get("price_ratio", query_date=date(year=2009, month=2, day=12).isoformat(), stock_type="興櫃")
