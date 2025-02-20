from collections import namedtuple


Price = namedtuple("Price", [
        "date", 
        "opening",
        "highest",
        "lowest",
        "closing",
        "volume",
    ]
)