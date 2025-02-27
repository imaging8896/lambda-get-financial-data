import json

from ..parser import DataParser
from ..constant import StockType, RequestMethod


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
        except json.JSONDecodeError:
            raise Exception(f"Unable to parse response\n{response.text}")

        if response_json["code"] != 200:
            msg = f"Unexpected code in {response_json}"
            raise Exception(msg)
        
        self.internal_parser = self.get_internal_parser(response_json["result"]["url"])
        self.internal_parser.parse_response()
