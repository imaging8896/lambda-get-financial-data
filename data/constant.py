import enum


@enum.unique
class RequestMethod(enum.Enum):
    GET = "get"
    POST = "post"


@enum.unique
class StockType(enum.Enum):
    PUBLIC = "上市"
    OTC = "上櫃"
    ROTC = "興櫃"


@enum.unique
class ETF_Country(enum.Enum):
    US = ""
    TW = ".TW"

    def to_str(self, etf_id: str) -> str:
        return f"{etf_id.upper()}{self.value}"
