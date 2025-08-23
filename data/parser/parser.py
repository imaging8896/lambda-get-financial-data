import logging
import random
import time

from typing import Sequence

from cloudscraper import CloudScraper
from curl_cffi import requests as curl_requests

from ..constant import RequestMethod


logger = logging.getLogger(__name__)


class DataParser:

    def __init__(self, 
        request_method: RequestMethod,
        request_cloud_scraper_mobile: bool, 
        request_cloud_scraper_desktop: bool,
        expected_status_codes: Sequence[int] = [200],
    ) -> None:
        self.request_method = request_method
        self.request_cloud_scraper_mobile = request_cloud_scraper_mobile
        self.request_cloud_scraper_desktop = request_cloud_scraper_desktop

        self.expected_status_codes = expected_status_codes

    @property
    def request_url(self) -> str:
        raise NotImplementedError

    @property
    def request_kw(self) -> dict:
        return {}

    @property   
    def error(self) -> bool:
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError
    
    def request(self) -> curl_requests.Response:
        request_method = self.request_method
        request_url = self.request_url
        request_kw = self.request_kw
        request_cloud_scraper_mobile = self.request_cloud_scraper_mobile
        request_cloud_scraper_desktop = self.request_cloud_scraper_desktop
        expected_status_codes = self.expected_status_codes

        if self.request_method not in RequestMethod:
            raise ValueError(f"Unsupported method {self.request_method=}")
        
        response = request(
            request_url, 
            request_method, 
            request_cloud_scraper_mobile, 
            request_cloud_scraper_desktop, 
            **request_kw,
        )
        if response.status_code not in expected_status_codes:
            raise curl_requests.exceptions.HTTPError(f"Unexpected status code: {response.status_code}\n{response.text}")
        return response

    def parse_response(self) -> None:
        raise NotImplementedError


def request(url: str, method: RequestMethod, mobile: bool = True, desktop: bool = True, **request_kw):
    response = None
    exception = None
    
    try:
        response = request_by_cloud_scraper(url, method, mobile=mobile, desktop=desktop, **request_kw)
    except (curl_requests.exceptions.SSLError, curl_requests.exceptions.ConnectionError) as e:
        logger.warning(f"Request error with random client header", exc_info=True)
        exception = e

    if mobile and desktop:
        try:
            if response is None or response.status_code == 403:
                response = request_by_cloud_scraper(url, method, mobile=False, **request_kw)
        except (curl_requests.exceptions.SSLError, curl_requests.exceptions.ConnectionError) as e:
            logger.warning(f"Request error with desktop client header", exc_info=True)
            exception = e

        try:
            if response is None or response.status_code == 403:
                response = request_by_cloud_scraper(url, method, desktop=False, **request_kw)
        except (curl_requests.exceptions.SSLError, curl_requests.exceptions.ConnectionError) as e:
            logger.warning(f"Request error with mobile client header", exc_info=True)
            exception = e

    if response is not None:
        return response
    
    if exception is not None:
        raise exception from None
    raise RuntimeError("Code should not reach here. Response is None.")


def request_by_cloud_scraper(url: str, method: RequestMethod, mobile: bool = True, desktop: bool = True, impersonate="chrome", **request_kw):
    request_kw["impersonate"] = impersonate

    if not mobile:
        platforms = ['linux', 'windows', 'darwin']

        scraper = CloudScraper(browser={"mobile": False, "platform": random.SystemRandom().choice(platforms)})
    elif not desktop:
        scraper = CloudScraper(browser={"dessktop": False, "browser": "chrome"})
    else:
        scraper = CloudScraper()

    headers = {
        'User-Agent': scraper.headers['User-Agent'], 
        'Accept': 'application/json, text/plain, */*', 
        'Accept-Language': 'en-US,en;q=0.9', 
        # 'Referer': 'https://www.moneydj.com/XQMBondPo/api/Data/GetProdHist',
        # 'Origin': 'https://www.moneydj.com',
        'Referer': url.split('?')[0],  # Extract base URL from full URL
        'Origin': '/'.join(url.split('/')[:3]),  # Extract scheme://hostname from URL
    }

    try:
        if method == RequestMethod.POST:
            return curl_requests.post(url, headers=headers, **request_kw)
        elif method == RequestMethod.GET:
            return curl_requests.get(url, headers=headers, **request_kw)
    except curl_requests.exceptions.Timeout:
        time.sleep(10)
        try:
            if method == RequestMethod.POST:
                return curl_requests.post(url, headers=headers, **request_kw)
            elif method == RequestMethod.GET:
                return curl_requests.get(url, headers=headers, **request_kw)
        except Exception as e:
            raise e from None
    raise ValueError(f"Unsupported method {method=}")
