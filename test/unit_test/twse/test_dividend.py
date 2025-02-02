import pytest

from data.twse.dividend import get_request_kw
from data.constant import StockType


@pytest.mark.parametrize("stock_type", list(StockType))
def test_get_request_kw(stock_type):
    kw = get_request_kw(stock_type, 2024, 20)

    assert isinstance(kw, dict)
