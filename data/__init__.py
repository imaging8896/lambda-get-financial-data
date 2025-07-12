import logging
import json

from .moneydj import etf_slice
from .moneydj import tw_2y_index
from .parser import DataParser
from .twse import dividend
from .twse import price_ratio
from .twse import revenue
from .twse import stock
from .twse import stocks_balance_sheet
from .twse import stocks_profit_sheet


logger = logging.getLogger("data")


def get(data_type: str, mobile: bool = True, desktop: bool = True, **kw):
    logger.info(f"Request {data_type=} {mobile=} {desktop=} {kw=}")

    parser: DataParser = {
        "dividend": dividend.TwseDividendHTMLParser,
        "etf_slice": etf_slice.MoneydjETFSliceParser,
        "price_ratio": price_ratio.parser,
        "revenue": revenue.TwseRevenueParser,
        "stock": stock.TwseStockParser,
        "tw_2y_index": tw_2y_index.MoneydjTWIndex2YPriceParser,
        "stocks_balance_sheet": stocks_balance_sheet.TwseStocksBalanceSheetParser,
        "stocks_profit_sheet": stocks_profit_sheet.TwseStocksProfitSheetParser,
    }[data_type](mobile, desktop, **kw)

    parser.parse_response()

    data = parser.data

    json.dumps(data)

    return data
