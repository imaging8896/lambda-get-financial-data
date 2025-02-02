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
