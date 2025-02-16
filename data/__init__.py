import logging

from .twse import dividend
from .twse import price_ratio


logger = logging.getLogger(__name__)


def get(data_type: str, mobile: bool = True, desktop: bool = True, **kw):
    logger.info(f"Request {data_type=} {mobile=} {desktop=} {kw=}")

    parser = {
        "dividend": dividend.TwseDividendHTMLParser,
        "price_ratio": price_ratio.parser,
    }[data_type](mobile, desktop, **kw)

    parser.parse_response()
    return parser.data
