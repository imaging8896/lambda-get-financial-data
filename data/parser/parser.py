import requests
import time
import logging
import random
import ssl
import contextlib

from cloudscraper import CloudScraper

from ..constant import RequestMethod


logger = logging.getLogger(__name__)


class DataParser:

    def __init__(self, 
        request_method: RequestMethod,
        request_cloud_scraper_mobile: bool, 
        request_cloud_scraper_desktop: bool,
        expected_status_codes: list[int] = frozenset([200]),
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
    def data(self) -> dict:
        raise NotImplementedError
    
    def request(self) -> requests.Response:
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
            raise requests.exceptions.HTTPError(f"Unexpected status code: {response.status_code}")
        return response

    def parse_response(self) -> None:
        raise NotImplementedError


def request(url: str, method: RequestMethod, mobile: bool = True, desktop: bool = True, **request_kw):
    response = None
    
    try:
        response = request_by_cloud_scraper(url, method, mobile=mobile, desktop=desktop, **request_kw)
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
        with contextlib.suppress(requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            response = request_by_cloud_scraper(url, method, mobile=mobile, desktop=desktop, ssl_context=ssl.create_default_context(), **request_kw)

    if mobile and desktop:
        try:
            if response is None or response.status_code == 403:
                response = request_by_cloud_scraper(url, method, mobile=False, **request_kw)
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            with contextlib.suppress(requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                response = request_by_cloud_scraper(url, method, mobile=False, ssl_context=ssl.create_default_context(), **request_kw)

        try:
            if response is None or response.status_code == 403:
                response = request_by_cloud_scraper(url, method, desktop=False, **request_kw)
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            response = request_by_cloud_scraper(url, method, desktop=False, ssl_context=ssl.create_default_context(), **request_kw)

    if response is not None:
        return response
    raise RuntimeError("Code should not reach here. Response is None.")


def request_by_cloud_scraper(url: str, method: RequestMethod, mobile: bool = True, desktop: bool = True, ssl_context: ssl.SSLContext = None, **request_kw):
    if ssl_context is not None:
        ssl_context.check_hostname = False

    if not mobile:
        platforms = ['linux', 'windows', 'darwin']

        scraper = CloudScraper(browser={"mobile": False, "platform": random.SystemRandom().choice(platforms)}, ssl_context=ssl_context)
    elif not desktop:
        scraper = CloudScraper(browser={"dessktop": False, "browser": "chrome"}, ssl_context=ssl_context)
    else:
        scraper = CloudScraper(ssl_context=ssl_context)

    if method == RequestMethod.POST:
        return scraper.post(url, verify=ssl_context is None, **request_kw)
    elif method == RequestMethod.GET:
        return scraper.get(url, verify=ssl_context is None, **request_kw)
    else:
        raise ValueError(f"Unsupported method {method=}")
