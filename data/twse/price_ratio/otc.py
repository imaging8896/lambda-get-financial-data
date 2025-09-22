import logging
import re
import time
import requests

from datetime import date

from .public import PriceRatio
from ...constant import RequestMethod
from ...exception import WrongDataFormat
from ...lib import last_working_date_generator
from ...parser import DataParser


# https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera.php?l=zh-tw

logger = logging.getLogger(__name__)


class TwseOTCPriceRatioParser(DataParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, query_date: str) -> None:
        super().__init__(
            request_method=RequestMethod.POST,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )
        the_query_date = date.fromisoformat(query_date)
        self.requested_date = the_query_date

        self._last_working_date_generator = last_working_date_generator(the_query_date)
        self._working_date = the_query_date
        self._data: list[dict] = []

    @property
    def request_url(self):
        self._working_date = next(self._last_working_date_generator)
        return f"https://www.tpex.org.tw/www/zh-tw/afterTrading/peQryDate?date={self._working_date.year}/{self._working_date.month:02}/{self._working_date.day:02}&cate=&id=&response=json"

    @property
    def data(self):
        def _create_data(row: dict):
            for should_have_field in ["股票代號", "殖利率(%)", "股利年度", "本益比", "股價淨值比"]:
                if should_have_field not in row:
                    raise WrongDataFormat(f"Missing '{should_have_field}' key for {self.request_url} for\n{row}")

            tw_year, quarter = None, None
            if "財報年/季" in row:
                if matched := re.match(r"^(\d{3})Q(\d{1})$", row["財報年/季"]):
                    tw_year, quarter = matched.groups()
                    if quarter not in {"1", "2", "3", "4"}:
                        raise WrongDataFormat(f"Invalid '財報年/季' 季 value for {self.request_url} for\n{row}")
                else:
                    raise WrongDataFormat(f"Invalid '財報年/季' value for {self.request_url} for\n{row}")

            def _parse_year(raw_year: str | None):
                if raw_year is not None and raw_year != "":
                    return str(int(raw_year) + 1911)
                
            def _parse_value(raw_value: str | None):
                if raw_value is not None and raw_value not in ["N/A", "null"]:
                    if set(raw_value.replace(".", "")) == {"0"}:
                        return "0"
                    if set(raw_value.split(".")[-1]) == {"0"}:
                        raw_value = raw_value.split(".")[0]
                    return raw_value.replace(",", "").rstrip("0")

            return PriceRatio(
                year=str(self._working_date.year),
                month=str(self._working_date.month),
                stock_id=row["股票代號"],
                close_price=row.get("收盤價"), # 2025/02/01 still not available
                return_rate=_parse_value(row["殖利率(%)"]),
                dividend_year=_parse_year(row.get("股利年度")), # 2017/01/01
                per=_parse_value(row["本益比"]),
                pa=_parse_value(row["股價淨值比"]),
                calculated_financial_year=_parse_year(tw_year),
                calculated_financial_quarter=quarter,
            )._asdict()

        return [_create_data(row) for row in self._data]

    def parse_response(self) -> None:
        iterate_days = 14
        for _ in range(iterate_days):
            response = self.request()

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                msg = f"Unable to parse response to json\n{response.text}"
                raise RuntimeError(msg)

            if "tables" not in data:
                raise WrongDataFormat(f"No 'tables' key for {response.url}. Got\n{data}")
            if len(data["tables"]) == 0:
                raise WrongDataFormat(f"'tables' should be at least 1 item for {response.url}. Got\n{data}")
            
            table_item = data["tables"][0]

            fields = table_item.get("fields")
            if fields is None:
                raise WrongDataFormat(f"No 'fields' key for {response.url}. Got\n{table_item}")
            logger.warning(f"Fields {fields}")

            if "data" not in table_item:
                raise WrongDataFormat(f"No 'data' key for in table item for {response.url}. Got\n{data}")

            if data := table_item["data"]:
                for row in data:
                    if len(row) != len(fields):
                        raise WrongDataFormat(f"Data length not equal to fields length for {response.url} for\n{row}\nGot\n{data}")
                    
                self._data = [
                    {
                        field: value
                        for field, value in zip(fields, row_data, strict=True)
                    }
                    for row_data in data
                ]
                return
            logger.warning(f"No data for {self._working_date.isoformat()}, try previous working date")
            time.sleep(1.12)
        raise WrongDataFormat(f"No data found for {iterate_days} consecutive working days before {self.requested_date.isoformat()}")
