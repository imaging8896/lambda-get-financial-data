import logging
import re
import time

from collections import namedtuple
from datetime import date

from ...constant import RequestMethod
from ...exception import WebsiteMaintaince, WrongDataFormat
from ...lib import last_working_date_generator
from ...parser import DataParser


# https://www.twse.com.tw/zh/page/trading/exchange/BWIBBU_d.html


logger = logging.getLogger(__name__)


PriceRatio = namedtuple("PriceRatio", [
        "year", 
        "month",
        "stock_id",
        "close_price",
        "return_rate",
        "dividend_year",
        "per",
        "pa",
        "calculated_financial_year",
        "calculated_financial_quarter",
    ]
)


class TwsePublicPriceRatioParser(DataParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, query_date: str) -> None:
        super().__init__(
            request_method=RequestMethod.POST,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )
        query_date = date.fromisoformat(query_date)

        self._working_date = None
        self._last_working_date_generator = last_working_date_generator(query_date)
        self._data: list[dict] = None

    @property
    def request_url(self):
        self._working_date = next(self._last_working_date_generator)
        cur_timestamp = int((time.time() - 1000) * 1000) # Minus 1000 to avoid querying time greater than current time
        return f"https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=json&date={self._working_date.year}{self._working_date.month:02}{self._working_date.day:02}&selectType=ALL&_={cur_timestamp}"

    @property
    def data(self) -> dict:
        def _create_data(row: dict):
            for should_have_field in ["證券代號", "殖利率(%)", "本益比", "股價淨值比"]:
                if should_have_field not in row:
                    raise WrongDataFormat(f"Missing '{should_have_field}' key for {self.request_url} for\n{row}")

            tw_year, quarter = None, None
            if value := row.get("財報年/季"):
                if matched := re.match(r"^(\d{3})/(\d{1})$", value):
                    tw_year, quarter = matched.groups()
                    if quarter not in {"1", "2", "3", "4"}:
                        raise WrongDataFormat(f"Invalid '財報年/季' 季 value for {self.request_url} for\n{row}")
                else:
                    raise WrongDataFormat(f"Invalid '財報年/季' value for {self.request_url} for\n{row}")

            def _parse_year(raw_year: str | None):
                if raw_year is not None:
                    return str(int(raw_year) + 1911)
                
            def _parse_value(raw_value: str | None):
                if raw_value is not None and raw_value != "-":
                    if set(raw_value.replace(".", "")) == {"0"}:
                        return "0"
                    if set(raw_value.split(".")[-1]) == {"0"}:
                        raw_value = raw_value.split(".")[0]
                    return raw_value.replace(",", "")

            return PriceRatio(
                year=str(self._working_date.year),
                month=str(self._working_date.month),
                stock_id=row["證券代號"],
                close_price=row.get("收盤價"), # 2017/01/01
                return_rate=_parse_value(row["殖利率(%)"]),
                dividend_year=_parse_year(row.get("股利年度")), # 2017/01/01
                per=_parse_value(row["本益比"]),
                pa=_parse_value(row["股價淨值比"]),
                calculated_financial_year=_parse_year(tw_year),
                calculated_financial_quarter=quarter,
            )._asdict()

        return [_create_data(row) for row in self._data]

    def parse_response(self) -> None:
        while True:
            response = self.request()
            if response.status_code == 404:
                raise WebsiteMaintaince(f"Maybe maintaince try again later for {response.url}")

            data = response.json()
            if data.get("stat") == "OK":
                if title := data.get("title"):
                    logger.info(f"Title '{title}'")
                else:
                    raise WrongDataFormat(f"No 'title' key for {response.url}. Got\n{data}")

                raw_data = data.get("data")
                if raw_data is None:
                    raise WrongDataFormat(f"No 'data' key for {response.url}. Got\n{data}")
                
                fields = data.get("fields")
                if fields is None:
                    raise WrongDataFormat(f"No 'fields' key for {response.url}. Got\n{data}")
                logger.info(f"Fields {fields}")

                for row in raw_data:
                    if len(row) != len(fields):
                        raise WrongDataFormat(f"Data length not equal to fields length for {response.url} for\n{row}\nGot\n{data}")
                    
                self._data = [
                    {
                        field: value
                        for field, value in zip(fields, row_data, strict=True)
                    }
                    for row_data in raw_data
                ]
                return

            elif data.get("stat") == "很抱歉，沒有符合條件的資料!":
                pass
            else:
                raise WrongDataFormat(f"Invalid value for 'stat' key or no 'stat' key for {response.url}. Got\n{data}")
            
            time.sleep(1.32)
