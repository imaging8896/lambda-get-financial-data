import requests
import time
import itertools
import logging

from ..parser import DataParser
from ..parser.html_parser import DataHTMLParser
from ..constant import RequestMethod
from ..exception import WrongDataFormat, BlockingByWebsiteError


logger = logging.getLogger("twse")
logger.setLevel(logging.INFO)


class RedirectOldParser(DataParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool) -> None:
        super().__init__(
            request_method=RequestMethod.POST,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.internal_parser = None

    @property
    def request_url(self) -> str:
        return "https://mops.twse.com.tw/mops/api/redirectToOld"
    
    @property
    def data(self) -> dict:
        return self.internal_parser.data
    
    def get_internal_parser(self, url: str) -> DataParser:
        raise NotImplementedError

    def parse_response(self) -> None:
        response = self.request()

        response.raise_for_status()

        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            if "THE PAGE CANNOT BE ACCESSED!" in response.text:
                msg = f"THE PAGE CANNOT BE ACCESSED!\n{response.text}"
                logger.info(msg)
                raise BlockingByWebsiteError("THE PAGE CANNOT BE ACCESSED!")
            raise Exception(f"Unable to parse response\n{response.text}")

        if response_json["code"] != 200:
            msg = f"Unexpected code in {response_json}"
            raise Exception(msg)
        
        time.sleep(1.26) # Small delay

        self.internal_parser = self.get_internal_parser(response_json["result"]["url"])
        self.internal_parser.parse_response()


class TwseHTMLTableParser(DataHTMLParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, request_method: RequestMethod, url: str, timeout: str = None) -> None:
        super().__init__(
            request_method=request_method,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.url = url
        self.timeout = int(timeout) if timeout else 20

        self._table_index = 0
        self._td_row = []
        self._th_row = []
        self._current_th_value = None

        self._row_header = None
        self._rows = []
        self._data = []

        # self._is_no_data = False

    @property
    def request_url(self) -> str:
        return self.url

    @property
    def request_kw(self) -> dict:
        return {
            "timeout": self.timeout,
        }
    
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

        if self._stack and self._stack[-1] == "th":
            self._current_th_value = ""

    def handle_endtag(self, tag):
        if tag not in self._stack and tag == "td": # OTC 2024 4
            logger.warning(f"Tag {tag} not in stack {self._stack}")
            tag = "th"

        super().handle_endtag(tag)

        if self._table_index >= 2:
            if tag == "th":
                self._th_row.append(self._current_th_value)
                self._current_th_value = None
            if tag == "tr":
                if self._th_row:
                    if self._row_header is not None:
                        logger.warning("Multiple headers in a table")
                        self._data.extend([self._to_row_data_dict(self._row_header, row) for row in self._rows])
                        self._row_header = None
                        self._rows = []
                    self._row_header = self._th_row
                    self._th_row = []
                if self._td_row:
                    self._rows.append(self._td_row)
                    self._td_row = []
            if tag == "table":
                if self._row_header is not None:
                    self._data.extend([self._to_row_data_dict(self._row_header, row) for row in self._rows])
                    self._row_header = None
                    self._rows = []
                else:
                    logger.warning(f"No header in a table. Skip this table. Rows\n{self._rows}")

    @staticmethod
    def _to_row_data_dict(headers, row):
        if len(row) == len(headers):
            return dict(zip(headers, row))
        else:
            pairs = list(itertools.zip_longest(headers, row))
            msg = f"Row size not match. {len(row)=} != {len(headers)=}\n{pairs=}"
            raise WrongDataFormat(msg)
                    
    def handle_data(self, data):
        if self._table_index >= 2:
            if self.is_in_tag("th"):
                self._current_th_value = data.strip().strip("\xa0")

            if self.is_in_tag("td") or self.is_in_tags(["td", "a"]):
                self._td_row.append(data.strip().strip("\xa0"))

            if self.is_in_tags(["td", "br"]):
                self._td_row[-1] += f"\n{data.strip().strip('\xa0')}"

        # if self.is_in_tag("font") and data.strip().strip('\xa0') == "查詢無資料！":
        #     self._is_no_data = True
