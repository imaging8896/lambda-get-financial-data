import logging
import json

from .moneydj import tw_2y_index
from .parser import DataParser
from .twse import dividend
from .twse import price_ratio
from .twse import stock


logger = logging.getLogger(__name__)


def get(data_type: str, mobile: bool = True, desktop: bool = True, **kw):
    logger.info(f"Request {data_type=} {mobile=} {desktop=} {kw=}")

    parser: DataParser = {
        "dividend": dividend.TwseDividendHTMLParser,
        "price_ratio": price_ratio.parser,
        "stock": stock.TwseStockParser,
        "tw_2y_index": tw_2y_index.MoneydjTWIndex2YPriceParser,
    }[data_type](mobile, desktop, **kw)

    parser.parse_response()

    json.dumps(parser.data)

    return parser.data
