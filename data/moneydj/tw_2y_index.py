
import logging

from datetime import datetime

from ..model import Price
from ..constant import RequestMethod
from ..exception import WrongDataFormat
from ..parser import DataParser


# https://www.moneydj.com/funddj/yl/BFRl00.djhtm?a=EB09999

logger = logging.getLogger(__name__)


class MoneydjTWIndex2YPriceParser(DataParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool) -> None:
        super().__init__(
            request_method=RequestMethod.GET,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self._data: list[dict] = None

    @property
    def request_url(self):
        return "https://www.moneydj.com/funddj/bcd/CZKC0.djbcd?a=EB09999&b=D"

    @property
    def data(self) -> dict:
        return self._data

    def parse_response(self) -> None:
        response = self.request()

        response.raise_for_status()

        response_text = response.text.strip("$")

        times_str, response_text = response_text.split(" ", 1)
        dates = [datetime.strptime(time_str, "%Y%m%d").date().isoformat() for time_str in times_str.split(",")]

        openings_str, response_text = response_text.split(" ", 1)
        openings = [opening for opening in openings_str.split(",")]
        if len(openings) != len(dates):
            raise WrongDataFormat(f"Openings length not equal to dates length for {response.url}")

        highests_str, response_text = response_text.split(" ", 1)
        highests = [highest for highest in highests_str.split(",")]
        if len(highests) != len(dates):
            raise WrongDataFormat(f"Highests length not equal to dates length for {response.url}")

        lowests_str, response_text = response_text.split(" ", 1)
        lowests = [lowest for lowest in lowests_str.split(",")]
        if len(lowests) != len(dates):
            raise WrongDataFormat(f"Lowests length not equal to dates length for {response.url}")

        closings_str, response_text = response_text.split(" ", 1)
        closings = [closing for closing in closings_str.split(",")]
        if len(closings) != len(dates):
            raise WrongDataFormat(f"Closings length not equal to dates length for {response.url}")

        volumes_str, response_text = response_text.split(" ", 1)
        volumes = [volume + "000000" for volume in volumes_str.split(",")]
        if len(volumes) != len(dates):
            raise WrongDataFormat(f"Volumes length not equal to dates length for {response.url}")
        
        margin_financing_balances_str, response_text = response_text.split(" ", 1)
        margin_financing_balances = [margin_financing_balance + "000000" for margin_financing_balance in margin_financing_balances_str.split(",")]
        if len(margin_financing_balances) != len(dates):
            raise WrongDataFormat(f"Margin financing balances length not equal to dates length for {response.url}")
        
        short_selling_amounts_str, response_text = response_text.split(" ", 1)
        short_selling_amounts = [short_selling_amount + "000" for short_selling_amount in short_selling_amounts_str.split(",")]
        if len(short_selling_amounts) != len(dates):
            raise WrongDataFormat(f"Short selling amounts length not equal to dates length for {response.url}")
        
        day_trading_amounts_str = response_text
        day_trading_amounts = [day_trading_amount + "000" for day_trading_amount in day_trading_amounts_str.split(",")]
        if len(day_trading_amounts) != len(dates):
            raise WrongDataFormat(f"Day trading amounts length not equal to dates length for {response.url}")

        self._data = [
            {
                **Price(
                    date=date,
                    opening=opening,
                    highest=highest,
                    lowest=lowest,
                    closing=closing,
                    volume=volume,
                )._asdict(),
                **dict(
                    margin_financing_balance=margin_financing_balance,
                    short_selling_amount=short_selling_amount,
                    day_trading_amount=day_trading_amount,
                )
            }
            for date, opening, highest, lowest, closing, volume, margin_financing_balance, short_selling_amount, day_trading_amount
            in zip(dates, openings, highests, lowests, closings, volumes, margin_financing_balances, short_selling_amounts, day_trading_amounts, strict=True)
        ]
