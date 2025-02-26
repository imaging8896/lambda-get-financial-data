import logging
import json
import itertools
import enum

from datetime import datetime

from ..parser.html_parser import DataHTMLParser, DataParser
from ..constant import StockType, RequestMethod
from ..exception import WrongDataFormat


# https://mops.twse.com.tw/mops/#/web/t51sb01

logger = logging.getLogger(__name__)


class TwseStockParser(DataParser):
    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_type: str, timeout: str = None) -> None:
        super().__init__(
            request_method=RequestMethod.POST,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.stock_type = StockType(stock_type)
        self.timeout = int(timeout) if timeout else 20

        self.internal_parser = None

    @property
    def request_url(self) -> str:
        return "https://mops.twse.com.tw/mops/api/redirectToOld"

    @property
    def request_kw(self) -> dict:
        return {
            "json": {
                "apiName": "ajax_t51sb01",
                "parameters": {
                    "TYPEK": {
                        StockType.PUBLIC: "sii",
                        StockType.OTC: "otc",
                        StockType.ROTC: "rotc",
                    }[self.stock_type],
                    "code": "",
                    "encodeURIComponent": 1,
                    "step": 1,
                    "firstin": True,
                    "id": ""
                }
            },
            "timeout": self.timeout,
        }

    @property
    def data(self) -> dict:
        return self.internal_parser.data

    def parse_response(self) -> None:
        response = self.request()

        response.raise_for_status()

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise Exception(f"Unable to parse response\n{response.text}")

        if response_json["code"] != 200:
            msg = f"Unexpected code in {response_json}"
            raise Exception(msg)
        
        url = response_json["result"]["url"]
        self.internal_parser = _TwseStockHTMLParser(self.request_cloud_scraper_mobile, self.request_cloud_scraper_desktop, self.stock_type, url, self.timeout)
        self.internal_parser.parse_response()
        

class FinancialReportType(enum.Enum):
    INDIVIDUAL = "個別"
    CONSOLIDATED = "合併"


class DividendAssignPeriod(enum.Enum):
    YEARLY = "每年"
    QUARTERLY = "每季"
    HALF_YEARLY = "每半會計年度"


class DividendAssignDecideLevel(enum.Enum):
    BOARD = "董事會"
    SHAREHOLDER = "股東會"


class _TwseStockHTMLParser(DataHTMLParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_type: StockType, url: str, timeout: str = None) -> None:
        super().__init__(
            request_method=RequestMethod.GET,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.url = url
        self.stock_type = stock_type
        self.timeout = int(timeout) if timeout else 20

        self._table_index = 0
        self._td_row = []
        self._th_row = []

        self._rows = []
        self._row_header = None
        self._data = []

    @property
    def request_url(self) -> str:
        return self.url

    @property
    def request_kw(self) -> dict:
        return {
            "timeout": self.timeout,
        }

    @property
    def data(self) -> dict:
        if self._rows:
            self._data.extend([self._to_row_data_dict(self._row_header, row) for row in self._rows])

        public_date_key = {
            StockType.PUBLIC: "上市日期",
            StockType.OTC: "上櫃日期",
            StockType.ROTC: "興櫃日期",
        }[self.stock_type]

        def _parse_date(field: str):
            year, month, day = map(int, field.split("/"))
            return datetime(year=year + 1911, month=month, day=day).date()

        return [
            {
                "id": raw_data["公司"],
                "long_name": raw_data["公司名稱"],
                "name": raw_data["公司簡稱"],
                "stock_group": raw_data["產業類別"],
                "register_foreign_country": raw_data["外國企業"],
                "address": raw_data["住址"],
                "invoice_number": raw_data["營利事業"],
                "chairman": raw_data["董事長"],
                "manager": raw_data["總經理"],
                "spokesman": raw_data["發言人"],
                "spokesman_title": raw_data["發言人職稱"],
                "acting_spokesman": raw_data["代理發言人"],
                "phone": raw_data["總機電話"],
                "create_date": _parse_date(raw_data["成立日期"]).isoformat(),
                "public_date": _parse_date(raw_data[public_date_key]).isoformat(),
                "share_unit": raw_data["普通股每股面額"].replace("                 ", ""),
                "capital": raw_data["實收資本額(元)"].replace(",", ""),
                "public_shares": raw_data["已發行普通股數或"].replace(",", ""),
                "private_shares": raw_data["私募普通股(股)"].replace(",", ""),
                "special_shares": raw_data["特別股(股)"].replace(",", ""),
                "financial_repport_type": FinancialReportType(raw_data["編製財務報告類型"]).value,
                "dividend_assign_period": DividendAssignPeriod(raw_data["普通股盈餘分派或"]).value,
                "dividend_assign_decide_leve": DividendAssignDecideLevel(raw_data["普通股年度(含第4季或後半年度)"]).value,
                "english_name": raw_data["英文簡稱"].replace("'", "`"),
                "english_address": raw_data["英文通訊地址"].replace("'", "`"),
                "email": raw_data["電子郵件信箱"],
                "website": raw_data["公司網址"],
                "investor": raw_data["投資人關係聯絡人"],
                "investor_title": raw_data["投資人關係聯絡人職稱"],
                "investor_phone": raw_data["投資人關係聯絡電話"],
                "investor_email": raw_data["投資人關係聯絡電子郵件"],
                "investor_website": raw_data["公司網站內利害關係人專區網址"],
            }
            for raw_data in self._data
        ]
    
    def parse_response(self) -> None:
        response = self.request()
        self.feed(response.text)

    def handle_starttag(self, tag, attrs):
        if tag == "div" and ("id", "div01") in attrs:
            self._stack.append(tag)
        elif self._stack:
            self._stack.append(tag)
            if tag == "table":
                self._table_index += 1

    def handle_endtag(self, tag):
        super().handle_endtag(tag)

        if self._table_index == 2:
            if tag == "tr":
                if self._th_row:
                    if self._row_header is not None:
                        self._data.extend([self._to_row_data_dict(self._row_header, row) for row in self._rows])
                    self._row_header = self._th_row
                    self._rows = []
                    self._th_row = []
                if self._td_row:
                    self._rows.append(self._td_row)
                    self._td_row = []
    @staticmethod
    def _to_row_data_dict(headers, row):
        def _to_none(value):
            return None if value == "－" else value

        row = [_to_none(value) for value in row]
        if len(row) == len(headers):
            return dict(zip(headers, row))
        else:
            pairs = list(itertools.zip_longest(headers, row))
            msg = f"Row size not match. {len(row)=} != {len(headers)=}\n{pairs=}"
            raise WrongDataFormat(msg)
                    
    def handle_data(self, data):
        if self._table_index == 2:
            if self.is_in_tag("th"):
                self._th_row.append(data.strip().strip("\xa0"))

            if self.is_in_tag("td") or self.is_in_tags(["td", "a"]):
                self._td_row.append(data.strip().strip("\xa0"))

            if self.is_in_tags(["td", "br"]):
                self._td_row[-1] += f"\n{data.strip().strip('\xa0')}"
