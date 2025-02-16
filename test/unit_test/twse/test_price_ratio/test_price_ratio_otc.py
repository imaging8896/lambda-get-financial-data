import pytest

from datetime import date, datetime
from unittest.mock import patch

from data.twse.price_ratio.otc import TwseOTCPriceRatioParser


@pytest.mark.parametrize(
    "mock_last_working_date_generator_values, expect_urls",[
        (
            [
                date(year=2021, month=2, day=22), 
                date(year=2009, month=12, day=1),
            ],
            [
                "https://www.tpex.org.tw/www/zh-tw/afterTrading/peQryDate?date=2021/02/22&cate=&id=&response=json",
                "https://www.tpex.org.tw/www/zh-tw/afterTrading/peQryDate?date=2009/12/01&cate=&id=&response=json",
            ]
        )
    ]
)
def test_request_url_property(mock_last_working_date_generator_values, expect_urls):
    with patch("data.twse.price_ratio.otc.last_working_date_generator") as mock_last_working_date_generator:
        mock_last_working_date_generator.return_value = iter(mock_last_working_date_generator_values)

        parser = TwseOTCPriceRatioParser(True, True, query_date=datetime.now().date().isoformat())

        assert parser.request_url == expect_urls[0]
        assert parser.request_url == expect_urls[1]
