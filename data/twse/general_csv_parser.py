import csv
import logging
import re

from io import StringIO

from ..parser import DataParser
from ..constant import RequestMethod
from ..exception import WrongDataFormat


# e.g. https://mopsov.twse.com.tw/mops/web/t108sb27


logger = logging.getLogger(__name__)


class TwseCsvFileParser(DataParser):

    def __init__(self, request_method: RequestMethod, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, timeout: str = "180") -> None:
        super().__init__(
            request_method=request_method,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        if m := re.match(r"^.+\/ajax_(.+)$", self.request_url):
            csv_file_prefix = m.group(1)
        else:
            raise WrongDataFormat(f"Unable to find prefix of csv file name from {self.request_url}")

        self.file_name_pattern = rf"({csv_file_prefix}_\d+_\d+\.csv)"
        self.timeout = timeout

        self._data = None

    @property
    def data(self):
        return self._data
    
    def parse_response(self) -> None:
        response = self.request()
        response_html = response.text

        if "查無符合條件之資料" in response_html:
            return
        elif m := re.search(self.file_name_pattern, response_html):
            got_csv_file_name = m.group(1)
            logger.warning(f"Got CSV file name: {got_csv_file_name}")
            csv_parser = _TwseCsvFileContentParser(
                request_cloud_scraper_mobile=self.request_cloud_scraper_mobile,
                request_cloud_scraper_desktop=self.request_cloud_scraper_desktop,
                file_name=got_csv_file_name,
                timeout=self.timeout,
            )
            csv_parser.parse_response()
            self._data = csv_parser.data
        else:
            raise WrongDataFormat(f"[twse] Cannot find dividend announcement csv filename in response\n{response_html}")


class _TwseCsvFileContentParser(DataParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, file_name: str, timeout: str = "180") -> None:
        super().__init__(
            request_method=RequestMethod.POST,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.file_name = file_name
        self.timeout = int(timeout)

        self.raw_data = None

    @property
    def request_url(self) -> str:
        return "https://mopsov.twse.com.tw/server-java/t105sb02"

    @property
    def request_kw(self) -> dict:
        return {
            "data": {
                "firstin": True,
                "step": 10,
                "filename": self.file_name,
            }, 
            "timeout": self.timeout,
        }

    @property
    def data(self):
        return self.raw_data
    
    def parse_response(self) -> None:
        response = self.request()
        response.encoding = "big5"
        response_text = response.text
        reader = csv.reader(StringIO(response_text))
        rows = list(reader)

        if not rows or len(rows) < 2:
            return

        rows = [[cell.strip() for cell in row] for row in rows]

        header = rows[0]
        data_rows = rows[1:]

        self.raw_data = [dict(zip(header, row)) for row in data_rows]
        self.raw_data = [
            data for data in self.raw_data if not all(
                key == value for key, value in data.items()
            )
        ]
