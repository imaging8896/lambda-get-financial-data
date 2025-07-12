import enum


@enum.unique
class ETF_Country(enum.Enum):
    US = ""
    TW = ".TW"

    def to_str(self, etf_id: str) -> str:
        return f"{etf_id.upper()}{self.value}"
