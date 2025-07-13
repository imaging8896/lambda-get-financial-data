
import logging

from ..constant import RequestMethod, ETF_Country
from ..exception import WrongDataFormat
from ..parser.html_parser import DataHTMLParser


# https://www.moneydj.com/ETF/X/Basic/basic0006.xdjhtm?etfid=0050.TW

logger = logging.getLogger(__name__)


class MoneydjETFSliceParser(DataHTMLParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, etf_id: str, etf_country: str) -> None:
        super().__init__(
            request_method=RequestMethod.GET,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self._data: list[list[str]] = []

        self.etf_id = etf_id
        self.etf_country = ETF_Country(etf_country)

        self._entering_data_table = False
        self._header_row: list[str] = []
        self._cur_row: list[str] = []
        self._got_header = False


    @property
    def request_url(self):
        return f"https://www.moneydj.com/ETF/X/Basic/basic0006.xdjhtm?etfid={self.etf_country.to_str(self.etf_id)}"

    @property
    def data(self):
        if self._header_row != ["日期", "事件", "比例"]:
            msg = f"Unexpected header row: {self._header_row}"
            raise WrongDataFormat(msg)
        
        if any(len(row) != 3 for row in self._data):
            msg = f"Unexpected data row size: {self._data}"
            raise WrongDataFormat(msg)
        return self._data
    
    def parse_response(self) -> None:
        response = self.request()
        # response.encoding = "big5"
        self.feed(response.text)

    def handle_starttag(self, tag, attrs):
        if tag == "table" and (("id", "ctl00_ctl00_MainContent_MainContent_gvTbl") in attrs or ("id", "ctl00_ctl00_MainContent_MainContent_gvTbl_gvTbl") in attrs):
            self._entering_data_table = True

        if tag == "tr" and self._entering_data_table:
            self._cur_row = []

        if tag in ["th", "td"] and self._entering_data_table:
            self._stack.append(tag)

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
    
        if tag == "table":
            self._entering_data_table = False

        if tag == "tr" and self._entering_data_table:
            if not self._got_header and self._header_row:
                self._got_header = True
            elif self._cur_row and len(self._cur_row) == 3:
                self._data.append(self._cur_row)
            elif self._cur_row and self._cur_row == ["查無資料"]:
                pass
            else:
                msg = f"Unexpected tr with unexpected header and data row: {self._header_row=} {self._cur_row=} {self._stack=}"
                raise WrongDataFormat(msg)

    def handle_data(self, data):
        if self._stack:
            if self._stack[-1] == "th":
                self._header_row.append(data.strip().replace('\xa0', ''))

            if self._stack[-1] == "td":
                self._cur_row.append(data.strip().replace('\xa0', ''))
