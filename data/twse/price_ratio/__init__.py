from .otc import TwseOTCPriceRatioParser
from .public import TwsePublicPriceRatioParser


def parser(*args, stock_type: str, **kw):
    return {
        "上市": TwsePublicPriceRatioParser,
        "上櫃": TwseOTCPriceRatioParser,
    }[stock_type](*args, **kw)
