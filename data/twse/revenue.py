
import csv

from datetime import date

from ..constant import StockType, RequestMethod
from ..exception import WrongDataFormat
from ..parser import DataParser


# https://mops.twse.com.tw/mops/#/web/t21sc04_ifrs


class TwseRevenueParser(DataParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_type: str, year: int, month: int, timeout: int) -> None:
        super().__init__(
            request_method=RequestMethod.POST,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.stock_type = StockType(stock_type)
        self.year = year
        self.month = month
        self.timeout = timeout

        self._data: list[dict] = None

    @property
    def request_url(self):
        return "https://mopsov.twse.com.tw/server-java/FileDownLoad"

    @property
    def request_kw(self):
        stock_type_code = {
            StockType.PUBLIC: "sii",
            StockType.OTC: "otc",
            StockType.ROTC: "rotc",
        }[self.stock_type]
        return {
            "data": {
                "step": 9,
                "functionName": "show_file2",
                "filePath": f"/t21/{stock_type_code}/", 
                "fileName": f"t21sc03_{self.year - 1911}_{self.month}.csv",
            },
            "timeout": self.timeout,
        }

    @property
    def data(self) -> dict:
        def _parse_date(time: str):
            tw_year, month, day = time.split("/")
            return date(year=int(tw_year) + 1911, month=int(month), day=int(day))
        
        def _parse_year_month(time: str):
            tw_year, month = time.split("/")
            year, month =  int(tw_year) + 1911, int(month)
            if year != self.year or month != self.month:
                raise WrongDataFormat(f"Expect {self.year} {self.month}. Got {year} {month}")

        def _parse_value(value: str):
            if value in {"-", ""}:
                return
            if value == "0":
                return "0"
            return value + "000"
        
        def _parse_percent(value: str):
            if value in {"-", ""}:
                return
            return value
        
        for data in self._data:
            _parse_year_month(data["資料年月"])

        return [
            {
                "stock_id": data["公司代號"],
                "stock_name": data["公司名稱"],
                "create_time": _parse_date(data["出表日期"]).isoformat(),
                "year": self.year, 
                "month": self.month,
                "value": _parse_value(data["營業收入-當月營收"]),
                "last_month": _parse_value(data["營業收入-上月營收"]),
                "last_year": _parse_value(data["營業收入-去年當月營收"]),
                "last_month_percent": _parse_percent(data["營業收入-上月比較增減(%)"]),
                "last_year_percent": _parse_percent(data["營業收入-去年同月增減(%)"]),
                "accumulation": _parse_value(data["累計營業收入-當月累計營收"]),
                "last_year_accumulation": _parse_value(data["累計營業收入-去年累計營收"]),
                "last_year_accumulation_percent": _parse_percent(data["累計營業收入-前期比較增減(%)"]),
                "note": None if data["備註"] == "-" else data["備註"],
            }
            for data in self._data
        ]

    def parse_response(self) -> None:
        response = self.request()

        response.raise_for_status()
        content = response.content.decode("utf-8-sig").splitlines()

        data = []
        hearders = None
        try:
            reader = csv.reader(content)
        except Exception as e:
            raise WrongDataFormat(f"Unable to parse csv for {self.year=} {self.month=} {self.stock_type=}\n{content}") from e
        
        try:
            for row in reader:
                if len(row) != 14:
                    raise WrongDataFormat(f"Expect 14 columns. Got {len(row)}\n{row}")
                
                if hearders is None:
                    hearders = row
                    continue

                data.append({header: value for header, value in zip(hearders, row)})
        except csv.Error as e:
            raise WrongDataFormat(f"Unable to parse csv =====\n{content}\n=====") from e

        self._data = data
