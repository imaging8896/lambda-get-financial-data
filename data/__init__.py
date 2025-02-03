import requests
import random
import ssl
import contextlib
import logging
import enum

from cloudscraper import CloudScraper

from .constant import RequestMethod
from .twse import dividend


logger = logging.getLogger(__name__)


@enum.unique
class GetDataType(enum.Enum):
    Dividend = "dividend"


def get(data_type: str, mobile: bool = True, desktop: bool = True, **kw):
    logger.info(f"Request {data_type=} {mobile=} {desktop=}")

    data_type: GetDataType = GetDataType(data_type)

    parser, request_kw = {
        GetDataType.Dividend: dividend.get_request_kw_and_parser,
    }[data_type](**kw)

    if raw_content := get_news_raw_content(mobile=mobile, desktop=desktop, **request_kw):
        parser.feed(raw_content)

        if parser.error:
            raise RuntimeError(f"Error occurred when parsing\n{raw_content}")

        return parser.data


def _raise_for_status(response: requests.Response):
    response.raise_for_status()


def get_news_raw_content(url: str, method: RequestMethod, mobile: bool = True, desktop: bool = True, encoding: str = None, handle_http_status_code = _raise_for_status, **request_kw):
    response = None
    
    try:
        response = get_news_raw_content_by_cloudscraper(url, method, mobile=mobile, desktop=desktop, **request_kw)
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
        with contextlib.suppress(requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            response = get_news_raw_content_by_cloudscraper(url, method, mobile=mobile, desktop=desktop, ssl_context=ssl.create_default_context(), **request_kw)

    if mobile and desktop:
        try:
            if response is None or response.status_code == 403:
                response = get_news_raw_content_by_cloudscraper(url, method, mobile=False, **request_kw)
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            with contextlib.suppress(requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                response = get_news_raw_content_by_cloudscraper(url, method, mobile=False, ssl_context=ssl.create_default_context(), **request_kw)

        try:
            if response is None or response.status_code == 403:
                response = get_news_raw_content_by_cloudscraper(url, method, desktop=False, **request_kw)
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            response = get_news_raw_content_by_cloudscraper(url, method, desktop=False, ssl_context=ssl.create_default_context(), **request_kw)

    if response is not None:
        handle_http_status_code(response)

        if encoding is not None:
            response.encoding = encoding

        return response.text
    raise RuntimeError("Code should not reach here. Response is None.")


def get_news_raw_content_by_cloudscraper(url: str, method: RequestMethod, mobile: bool = True, desktop: bool = True, ssl_context: ssl.SSLContext = None, **request_kw):
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
