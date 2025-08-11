
import json
import logging

from datetime import date, datetime

from ..constant import RequestMethod
from ..exception import WrongDataFormat
from ..parser import DataParser


# https://www.cnyes.com/twstock/2330

logger = logging.getLogger(__name__)


class CnyesStockPriceHistoryParser(DataParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_id: str, start_date_included: date, end_date_excluded: date | None = None) -> None:
        super().__init__(
            request_method=RequestMethod.GET,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.stock_id = stock_id
        self.start_date_included = start_date_included
        self.end_date_excluded = date.today() if end_date_excluded is None else end_date_excluded

        self._data: dict[str, tuple] | None = None

    @property
    def request_url(self):
        from_timestamp = datetime(year=self.start_date_included.year, month=self.start_date_included.month, day=self.start_date_included.day, hour=12).timestamp()
        to_timestamp = datetime(year=self.end_date_excluded.year, month=self.end_date_excluded.month, day=self.end_date_excluded.day).timestamp()
        return f"https://ws.api.cnyes.com/ws/api/v1/charting/history?resolution=D&symbol=TWS:{self.stock_id}:STOCK&from={int(to_timestamp)}&to={int(from_timestamp)}"

    @property
    def data(self):
        return self._data

    def parse_response(self) -> None:
        response = self.request()

        response.raise_for_status()

        try:
            json_data = response.json()
        except json.JSONDecodeError as e:
            raise WrongDataFormat(f"Error decoding JSON response from {response.url}. Response text: {response.text}") from e

        if json_data["data"]["t"] == []:
            raise WrongDataFormat(f"Unexpected response format for {response.url}. Got {json_data=}")
        
        try:
            self._data = {
                date.fromtimestamp(time).isoformat(): (opening, closing, high, low, int(volume * 1000))
                for time, opening, closing, high, low, volume in zip(
                    json_data["data"]["t"], 
                    json_data["data"]["o"], 
                    json_data["data"]["c"], 
                    json_data["data"]["h"], 
                    json_data["data"]["l"], 
                    json_data["data"]["v"], 
                    strict=True,
                )
            }
        except ValueError as e:
            raise WrongDataFormat(f"Error parsing response data for {response.url}. Got {json_data=}") from e
