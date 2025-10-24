import pytest

from datetime import datetime, timedelta

from data import get
from data.constant import StockType


@pytest.mark.parametrize("year, month, stock_type, timeout, test_stock_id, expect_results", [
    ("2025", "5", StockType.PUBLIC, "20", "1215", [{
        'stock_id': '1215', 
        'stock_name': '卜蜂', 
        'count_time_str': '113年', 
        'share_holder_list_final_date': '2025-06-03', 
        'cash_from_earning': '4.5', 
        'cash_from_accumulation': None, 
        'cash_for_special': None, 
        'cash_date': '2025-05-28', 
        'cash_distribute_date': '2025-06-20', 
        'share_from_earning': None, 
        'share_from_accumulation': None, 
        'share_date': None, 
        'capital_increase': None, 
        'capital_increase_rate': None, 
        'capital_increase_price': None, 
        'announcement_date': '2025-05-09', 
        'par_value': '10'
    }]),
    ("2025", "3", StockType.OTC, "20", "3526", [{
        'stock_id': '3526', 
        'stock_name': '凡甲', 
        'count_time_str': '113年', 
        'share_holder_list_final_date': '2025-04-19', 
        'cash_from_earning': '13.21812075', 
        'cash_from_accumulation': "3.2431077", 
        'cash_for_special': None, 
        'cash_date': '2025-04-11', 
        'cash_distribute_date': '2025-05-08', 
        'share_from_earning': None, 
        'share_from_accumulation': None, 
        'share_date': None, 
        'capital_increase': None, 
        'capital_increase_rate': None, 
        'capital_increase_price': None, 
        'announcement_date': '2025-03-24', 
        'par_value': '10'
    }]),
    ("2025", "8", StockType.ROTC, "20", "4117", [{
        'stock_id': '4117', 
        'stock_name': '普生', 
        'count_time_str': None, 
        'share_holder_list_final_date': '2025-09-14', 
        'cash_from_earning': None, 
        'cash_from_accumulation': None, 
        'cash_for_special': None, 
        'cash_date': None, 
        'cash_distribute_date': None, 
        'share_from_earning': None, 
        'share_from_accumulation': None, 
        'share_date': '2025-09-08', 
        'capital_increase': "10000000", 
        'capital_increase_rate': "14.79670073", 
        'capital_increase_price': "12", 
        'announcement_date': '2025-08-25', 
        'par_value': '10'
    }]),
    ("2025", None, StockType.ROTC, "20", "6987", [{
        'stock_id': '6987', 
        'stock_name': '寶晶能源*', 
        'count_time_str': "113年", 
        'share_holder_list_final_date': '2025-06-29', 
        'cash_from_earning': "0.52", 
        'cash_from_accumulation': None, 
        'cash_for_special': None, 
        'cash_date': "2025-06-23", 
        'cash_distribute_date': "2025-07-16", 
        'share_from_earning': None, 
        'share_from_accumulation': None, 
        'share_date': None, 
        'capital_increase': None, 
        'capital_increase_rate': None, 
        'capital_increase_price': None, 
        'announcement_date': '2025-06-10', 
        'par_value': None
    }]),
    ("2024", None, StockType.PUBLIC, "20", "2330", [
        {
            'stock_id': '2330', 
            'stock_name': '台積電', 
            'count_time_str': "112年第3季", 
            'share_holder_list_final_date': '2024-03-24', 
            'cash_from_earning': "3.49978969", 
            'cash_from_accumulation': None, 
            'cash_for_special': None, 
            'cash_date': "2024-03-18", 
            'cash_distribute_date': "2024-04-11", 
            'share_from_earning': None, 
            'share_from_accumulation': None, 
            'share_date': None, 
            'capital_increase': None, 
            'capital_increase_rate': None, 
            'capital_increase_price': None, 
            'announcement_date': '2024-03-01', 
            'par_value': "10"
        },
        {
            'stock_id': '2330', 
            'stock_name': '台積電', 
            'count_time_str': "112年第4季", 
            'share_holder_list_final_date': '2024-06-19', 
            'cash_from_earning': "3.49978969", 
            'cash_from_accumulation': None, 
            'cash_for_special': None, 
            'cash_date': "2024-06-13", 
            'cash_distribute_date': "2024-07-11", 
            'share_from_earning': None, 
            'share_from_accumulation': None, 
            'share_date': None, 
            'capital_increase': None, 
            'capital_increase_rate': None, 
            'capital_increase_price': None, 
            'announcement_date': '2024-05-28', 
            'par_value': "10"
        },
        {
            'stock_id': '2330', 
            'stock_name': '台積電', 
            'count_time_str': "113年第1季", 
            'share_holder_list_final_date': '2024-09-18', 
            'cash_from_earning': "4.0001382", 
            'cash_from_accumulation': None, 
            'cash_for_special': None, 
            'cash_date': "2024-09-12", 
            'cash_distribute_date': "2024-10-09", 
            'share_from_earning': None, 
            'share_from_accumulation': None, 
            'share_date': None, 
            'capital_increase': None, 
            'capital_increase_rate': None, 
            'capital_increase_price': None, 
            'announcement_date': '2024-08-28', 
            'par_value': "10"
        },
        {
            'stock_id': '2330', 
            'stock_name': '台積電', 
            'count_time_str': "113年第2季", 
            'share_holder_list_final_date': '2024-12-18', 
            'cash_from_earning': "3.99963706", 
            'cash_from_accumulation': None, 
            'cash_for_special': None, 
            'cash_date': "2024-12-12", 
            'cash_distribute_date': "2025-01-09", 
            'share_from_earning': None, 
            'share_from_accumulation': None, 
            'share_date': None, 
            'capital_increase': None, 
            'capital_increase_rate': None, 
            'capital_increase_price': None, 
            'announcement_date': '2024-11-27', 
            'par_value': "10"
        },
    ]),
    ("2025", "7", StockType.PUBLIC, "20", "2002A", [{
        'stock_id': '2002A', 
        'stock_name': '特別股A', 
        'count_time_str': "113年", 
        'share_holder_list_final_date': '2025-08-01', 
        'cash_from_earning': None, 
        'cash_from_accumulation': None, 
        'cash_for_special': "1.4", 
        'cash_date': "2025-07-24", 
        'cash_distribute_date': "2025-08-27", 
        'share_from_earning': None, 
        'share_from_accumulation': None, 
        'share_date': None, 
        'capital_increase': None, 
        'capital_increase_rate': None, 
        'capital_increase_price': None, 
        'announcement_date': '2025-07-03', 
        'par_value': "10"
    }]),
    ("2025", None, StockType.ROTC, "20", "2245", [
        {
            'stock_id': '2245', 
            'stock_name': '詠勝昌*', 
            'count_time_str': "113年", 
            'share_holder_list_final_date': '2025-06-17', 
            'cash_from_earning': "2", 
            'cash_from_accumulation': None, 
            'cash_for_special': None, 
            'cash_date': "2025-06-11", 
            'cash_distribute_date': "2025-07-16", 
            'share_from_earning': None, 
            'share_from_accumulation': None, 
            'share_date': None, 
            'capital_increase': None, 
            'capital_increase_rate': None, 
            'capital_increase_price': None, 
            'announcement_date': '2025-05-20', 
            'par_value': "10"
        },
        {
            'stock_id': '2245', 
            'stock_name': '詠勝昌*', 
            'count_time_str': "113年", 
            'share_holder_list_final_date': '2025-10-25', 
            'cash_from_earning': None, 
            'cash_from_accumulation': None, 
            'cash_for_special': None, 
            'cash_date': None, 
            'cash_distribute_date': None, 
            'share_from_earning': "1", 
            'share_from_accumulation': None, 
            'share_date': "2025-10-17", 
            'capital_increase': None, 
            'capital_increase_rate': None, 
            'capital_increase_price': None, 
            'announcement_date': '2025-09-30', 
            'par_value': "5"
        },
    ]),
    ("2025", None, StockType.ROTC, "20", "2644", [{
        'stock_id': '2644', 
        'stock_name': '中信造船', 
        'count_time_str': "113年", 
        'share_holder_list_final_date': '2025-09-01', 
        'cash_from_earning': "0.3", 
        'cash_from_accumulation': None, 
        'cash_for_special': None, 
        'cash_date': "2025-08-26", 
        'cash_distribute_date': "2025-10-03", 
        'share_from_earning': "0.2", 
        'share_from_accumulation': None, 
        'share_date': "2025-08-26", 
        'capital_increase': None, 
        'capital_increase_rate': None, 
        'capital_increase_price': None, 
        'announcement_date': '2025-08-13', 
        'par_value': "10"
    }]),
])
def test_get_dividend_announcement(year, month, stock_type, timeout, test_stock_id, expect_results):
    result = get("dividend_announcement", year=year, month=month, stock_type=stock_type.value, timeout=timeout)

    results = [x for x in result if x["stock_id"] == test_stock_id]
    assert results, f"Cannot find dividend announcement for stock_id={test_stock_id}"

    assert sorted(expect_results, key=lambda x: x["announcement_date"]) == sorted(results, key=lambda x: x["announcement_date"])


@pytest.mark.parametrize("stock_type", [x for x in StockType])
def test_get_latest_dividend_announcement(stock_type):
    now = datetime.now()

    results = get("dividend_announcement", year=str(now.year), stock_type=stock_type.value, timeout=str(20))
    assert isinstance(results, list)
    for result in results:
        assert isinstance(result, dict)
        assert "stock_id" in result
        assert "announcement_date" in result


@pytest.mark.parametrize("stock_type", [x for x in StockType])
def test_get_no_dividend_announcement(stock_type):
    next_month = datetime.now() + timedelta(days=60)

    assert get("dividend_announcement", year=str(next_month.year), month=str(next_month.month), stock_type=stock_type.value, timeout=str(20)) is None
