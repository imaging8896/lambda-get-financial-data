import logging

from .twse import dividend


logger = logging.getLogger(__name__)


def get(data_type: str, mobile: bool = True, desktop: bool = True, **kw):
    logger.info(f"Request {data_type=} {mobile=} {desktop=} {kw=}")

    parser = {
        "dividend": dividend.TwseDividendHTMLParser,
    }[data_type](mobile, desktop, **kw)

    parser.parse_response()
    return parser.data
