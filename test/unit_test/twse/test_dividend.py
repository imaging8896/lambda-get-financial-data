import pytest

from data.twse.dividend import get_request_kw_and_parser, TwseDividendHTMLParser
from data.constant import StockType


@pytest.mark.parametrize("stock_type", list(StockType))
def test_get_request_kw_and_parser(stock_type):
    parser, kw = get_request_kw_and_parser(stock_type, 2024, 20)

    assert isinstance(kw, dict)
    assert isinstance(parser, TwseDividendHTMLParser)
