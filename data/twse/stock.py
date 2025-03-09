import logging
import enum

from datetime import datetime

from . import RedirectOldParser, TwseHTMLTableParser
from ..parser.html_parser import DataParser
from ..constant import StockType, RequestMethod


# https://mops.twse.com.tw/mops/#/web/t51sb01

logger = logging.getLogger(__name__)


class TwseStockParser(RedirectOldParser):
    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_type: str, timeout: str = None) -> None:
        super().__init__(
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.stock_type = StockType(stock_type)
        self.timeout = int(timeout) if timeout else 20

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
    
    def get_internal_parser(self, url: str) -> DataParser:
        return _TwseStockHTMLParser(self.request_cloud_scraper_mobile, self.request_cloud_scraper_desktop, self.stock_type, url, self.timeout)
        

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


class _TwseStockHTMLParser(TwseHTMLTableParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_type: StockType, url: str, timeout: str = None) -> None:
        super().__init__(
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
            request_method=RequestMethod.GET,
            url=url,
            timeout=timeout,
        )

        self.stock_type = stock_type

    @property
    def data(self) -> dict:
        self._data = [
            {
                key: None if value == "－" else value
                for key, value in raw_data.items()
            }
            for raw_data in self._data
        ]

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
