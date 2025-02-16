import pytest

from datetime import date, datetime
from unittest.mock import patch

from data.twse.price_ratio.public import TwsePublicPriceRatioParser


@pytest.mark.parametrize(
    "mock_last_working_date_generator_values, mock_time_values, expect_urls",[
        (
            [
                date(year=2021, month=2, day=22), 
                date(year=2009, month=12, day=1),
            ],
            [2000, 3000],
            [
                "https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=json&date=20210222&selectType=ALL&_=1000000",
                "https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=json&date=20091201&selectType=ALL&_=2000000",
            ]
        )
    ]
)
def test_request_url_property(mock_last_working_date_generator_values, mock_time_values, expect_urls):
    with (
        patch("data.twse.price_ratio.public.last_working_date_generator") as mock_last_working_date_generator,
        patch("data.twse.price_ratio.public.time.time") as mock_time,
    ):
        mock_last_working_date_generator.return_value = iter(mock_last_working_date_generator_values)
        mock_time.side_effect = mock_time_values

        parser = TwsePublicPriceRatioParser(True, True, query_date=datetime.now().date().isoformat())

        assert parser.request_url == expect_urls[0]
        assert parser.request_url == expect_urls[1]
