import logging
import re

from collections import namedtuple
from datetime import datetime

from .general_csv_parser import TwseCsvFileParser
from ..constant import StockType, RequestMethod
from ..exception import WrongDataFormat


# https://mopsov.twse.com.tw/mops/web/t108sb27

logger = logging.getLogger(__name__)


class TwseDividendAnnouncementParser(TwseCsvFileParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_type: str, year: str, month: str | None = None, timeout: str = "180") -> None:
        super().__init__(
            request_method=RequestMethod.POST,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
            timeout=timeout,
        )

        self.stock_type = StockType(stock_type)
        self.year = int(year)
        self.month = month
        self.timeout = int(timeout)

    @property
    def request_url(self) -> str:
        return "https://mopsov.twse.com.tw/mops/web/ajax_t108sb27"

    @property
    def request_kw(self) -> dict:
        return {
            "data": {
                "encodeURIComponent": 1,
                "step": 1,
                "firstin": 1,
                "off": 1,
                "keyword4": "",
                "code1": "",
                "TYPEK2": "",
                "checkbtn": "",
                "queryName": "",
                "TYPEK": {
                    StockType.PUBLIC: "sii",
                    StockType.OTC: "otc",
                    StockType.ROTC: "rotc",
                }[self.stock_type],
                "co_id_1": "",
                "co_id_2": "",
                "year": f"{self.year - 1911}",
                "month": self.month.zfill(2) if self.month else "",
                "b_date": "",
                "e_date": "",
                "type": "",
            }, 
            "timeout": self.timeout,
        }
    
    @property
    def data(self):

        def _strip_number(value: str):
            value = value.replace(",", "")
            if "." in value:
                value = value.rstrip("0")
            return value.rstrip(".")

        def _parse_str(expected_keys: list[str], row: dict[str, str]):
            for key in expected_keys:
                if key in row:
                    return row[key].strip()
            raise WrongDataFormat(f"Missing {expected_keys=} in row {row}")
        

        def _parse_nullable_number(expected_keys: list[str], row: dict[str, str]):
            value = _strip_number(_parse_str(expected_keys, row))
            if value:
                return value

        def _parse_date_to_isoformat(expected_keys: list[str], row: dict[str, str]):
            value = _parse_str(expected_keys, row)
            return datetime.strptime(value, "%Y/%m/%d").date().isoformat()


        def _parse_nullable_date_to_isoformat(expected_keys: list[str], row: dict[str, str]):
            value = _parse_str(expected_keys, row)
            if value:
                return datetime.strptime(value, "%Y/%m/%d").date().isoformat()


        def _parse_par(expected_keys: list[str], row: dict[str, str]):
            value = _parse_str(expected_keys, row)
            if value == "無面額":
                return

            if m := re.match(r"^新台幣(\d+\.\d*)元$", value):
                value = _strip_number(m.group(1))
                if value:
                    return value
                raise WrongDataFormat(f"Unable to parse par value(not a number) from {value=} of row {row}")
            raise WrongDataFormat(f"Unable to parse par value from {value=} of row {row}")

        def _parse_count_time(expected_keys: list[str], row: dict[str, str]):
            value = _parse_str(expected_keys, row)
            if value == "不適用":
                return 
            return value


        if self._data is None:
            return None
        

        def _get_stock_name(data: dict[str, str]):
            return _parse_str(["公司名稱"], data)


        def _get_special_cash_dividend(data: dict[str, str]):
            if self.year >= 2016:
                return _parse_nullable_number(["現金股利-特別股配發現金股利(元/股)"], data)

        return [
            DividendAnnouncement(
                stock_id=_parse_str(["公司代號"], data),
                stock_name=_get_stock_name(data),
                count_time_str=_parse_count_time(["股利所屬期間", "股利所屬年度"], data),
                share_holder_list_final_date=_parse_date_to_isoformat(["權利分派基準日"], data),

                cash_from_earning=_parse_nullable_number(["現金股利-盈餘分配之股東現金股利(元/股)", "現金股利-股東配發內容-盈餘分配之股東現金股利(元/股)"], data),
                cash_from_accumulation=_parse_nullable_number(["現金股利-法定盈餘公積、資本公積發放之現金(元/股)", "現金股利-股東配發內容-法定盈餘公積、資本公積發放之現金(元/股)"], data),
                cash_for_special=_get_special_cash_dividend(data),
                cash_date=_parse_nullable_date_to_isoformat(["現金股利-除息交易日"], data),
                cash_distribute_date=_parse_nullable_date_to_isoformat(["現金股利-現金股利發放日"], data),

                share_from_earning=_parse_nullable_number(["股票股利-盈餘轉增資配股(元/股)", "股票股利-股東配發內容-盈餘轉增資配股(元/股)"], data),
                share_from_accumulation=_parse_nullable_number(["股票股利-資本公積轉增資配股(元/股)", "股票股利-股東配發內容-法定盈餘公積、資本公積轉增資配股(元/股)"], data),
                share_date=_parse_nullable_date_to_isoformat(["股票股利-除權交易日"], data),

                capital_increase=_parse_nullable_number(["現金增資總股數(股)"], data),
                capital_increase_rate=_parse_nullable_number(["現金增資認股比率(%)"], data),
                capital_increase_price=_parse_nullable_number(["現金增資認購價(元/股)"], data),

                announcement_date=_parse_date_to_isoformat(["公告日期"], data),
                par_value=_parse_par(["普通股每股面額"], data),
            )._asdict()
            for data in self._data
            if self.year >= 2016 or "特別股" not in _get_stock_name(data)
        ]


DividendAnnouncement = namedtuple("DividendAnnouncement", [
        "stock_id", 
        "stock_name",
        "count_time_str",
        "share_holder_list_final_date",

        "cash_from_earning",
        "cash_from_accumulation",
        "cash_for_special",
        "cash_date",
        "cash_distribute_date",

        "share_from_earning",
        "share_from_accumulation",
        "share_date",

        "capital_increase",
        "capital_increase_rate",
        "capital_increase_price",

        "announcement_date",
        "par_value",
    ]
)
