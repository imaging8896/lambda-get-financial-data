
import json
import logging

from datetime import datetime

from ..model import ETFDividend
from ..constant import RequestMethod, ETF_Country
from ..exception import WrongDataFormat
from ..parser import DataParser


# https://www.pocket.tw/etf/tw/0050/cashdividend
# https://www.pocket.tw/etf/us/TQQQ/cashdividend/

logger = logging.getLogger(__name__)


class PocketETFDividendParser(DataParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, etf_id: str, etf_country: str, years: str) -> None:
        super().__init__(
            request_method=RequestMethod.GET,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.etf_id = etf_id.upper()
        self.etf_country = ETF_Country(etf_country)
        self.api_dtno = {
            ETF_Country.US: "50405322",
            ETF_Country.TW: "59444834",
        }[self.etf_country]
        self.api_major_table = {
            ETF_Country.US: "M730",
            ETF_Country.TW: "M810",
        }[self.etf_country]
        self.years = int(years)

        self._data: list[dict] = []

    @property
    def request_url(self):
        return f"https://www.pocket.tw/api/cm/MobileService/ashx/GetDtnoData.ashx?action=getdtnodata&DtNo={self.api_dtno}&ParamStr=AssignID%3D{self.etf_id}%3BMTPeriod%3D3%3BDTMode%3D0%3BDTRange%3D{self.years}%3BDTOrder%3D1%3BMajorTable%3D{self.api_major_table}%3B&FilterNo=0"

    @property
    def data(self):
        return self._data

    def parse_response(self) -> None:
        response = self.request()

        response.raise_for_status()

        response_text = response.text.strip()

        try:
            json_data = json.loads(response_text)
        except json.JSONDecodeError:
            msg = f"Unable to parse response as JSON: {response_text}"
            logger.error(msg)
            raise WrongDataFormat(msg)
        
        if "Data" not in json_data or "Title" not in json_data:
            msg = f"Unexpected JSON format: {json_data}"
            logger.error(msg)
            raise WrongDataFormat(msg)
        
        expected_title = {
            ETF_Country.US: ["年度","現金股利(元)","現金股利殖利率(TTM)(%)","除息權日"],
            ETF_Country.TW: ["年季","現金股利合計(元)","現金股利殖利率(%)","除息日","發放日"],
        }[self.etf_country]
        if json_data["Title"] != expected_title:
            msg = f"Unexpected title in JSON: {json_data}. Expected: {expected_title}"
            logger.error(msg)
            raise WrongDataFormat(msg)
        
        def _data():
            def _parse_dividend_year_quarter(data):
                if expected_title[0] == "年度":
                    return int(data), None
                elif expected_title[0] == "年季":
                    return int(data[:-2]), int(data[-2:])
                else:
                    msg = f"Unexpected title format: {expected_title[0]} for {data} in {json_data}"
                    logger.error(msg)
                    raise WrongDataFormat(msg)

            for data in json_data["Data"]:
                data: list[str]
                # ["2025","1.6955280000","1.27","20250321"]
                # ["202502","0.257","0.67","20250716","20250808"]
                if len(data) != len(expected_title) or any(not isinstance(x, str) for x in data):
                    msg = f"Unexpected data length: {data} in {json_data}. Expected: {len(expected_title)}"
                    logger.error(msg)
                    raise WrongDataFormat(msg)
                
                if data[1].strip() == "":
                    # No dividend for this year/quarter
                    continue
                
                dividend_year, dividend_quarter = _parse_dividend_year_quarter(data[0])
                yield ETFDividend(
                    dividend_year=dividend_year,
                    dividend_quarter=dividend_quarter,
                    dividend_value=data[1].rstrip("0"),
                    dividend_return_rate=data[2],
                    dividend_date=datetime.strptime(data[3], "%Y%m%d").date().isoformat(),
                )._asdict()

        self._data = list(_data())
