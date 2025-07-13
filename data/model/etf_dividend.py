from collections import namedtuple


ETFDividend = namedtuple("ETFDividend", [
        "dividend_year", 
        "dividend_quarter",
        "dividend_value",
        "dividend_return_rate",
        "dividend_date",
    ]
)
