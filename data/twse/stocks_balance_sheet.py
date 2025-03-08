import logging
import itertools
import enum

from collections import namedtuple

from . import RedirectOldParser
from ..parser.html_parser import DataHTMLParser, DataParser
from ..constant import StockType, RequestMethod
from ..exception import WrongDataFormat


# https://mops.twse.com.tw/mops/#/web/t163sb05

logger = logging.getLogger(__name__)


class TwseStocksBalanceSheetParser(RedirectOldParser):
    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, year: int, stock_type: str, quarter: int, timeout: str = None) -> None:
        super().__init__(
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.year = year
        self.stock_type = StockType(stock_type)
        self.quarter = quarter
        self.timeout = int(timeout) if timeout else 20

    @property
    def request_kw(self) -> dict:
        return {
            "json": {
                "apiName": "ajax_t163sb05",
                "parameters": {
                    "year": f"{self.year - 1911}",
                    "TYPEK": {
                        StockType.PUBLIC: "sii",
                        StockType.OTC: "otc",
                        StockType.ROTC: "rotc",
                    }[self.stock_type],
                    "season": f"0{self.quarter}",
                    "encodeURIComponent": 1,
                    "off": 1,
                    "step": 1,
                    "firstin": 1,
                    "isQuery": "Y",
                }
            },
            "timeout": self.timeout,
        }
    
    def get_internal_parser(self, url: str) -> DataParser:
        return _TwseStocksBalanceSheetHTMLParser(self.request_cloud_scraper_mobile, self.request_cloud_scraper_desktop, self.stock_type, url, self.timeout)


class FinancialReportType(enum.Enum):
    INDIVIDUAL = "個別"
    CONSOLIDATED = "合併"


class DividendAssignPeriod(enum.Enum):
    YEARLY = "每年"
    QUARTERLY = "每季"
    HALF_YEARLY = "每半會計年度"


class DividendAssignDecideLevel(enum.Enum):
    BOARD = "董事會"
    SHAREHOLDER = "股東會"


class _TwseStocksBalanceSheetHTMLParser(DataHTMLParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_type: StockType, url: str, timeout: str = None) -> None:
        super().__init__(
            request_method=RequestMethod.GET,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.url = url
        self.stock_type = stock_type
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

    @property
    def data(self) -> dict:
        return [_to_data(raw_data) for raw_data in self._data]
    
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
                        raise WrongDataFormat(f"There are row headers\n{self._th_row=}\nand\n{self._row_header=}")
                    self._row_header = self._th_row
                    self._th_row = []
                if self._td_row:
                    self._rows.append(self._td_row)
                    self._td_row = []
            if tag == "table":
                self._data.extend([self._to_row_data_dict(self._row_header, row) for row in self._rows])
                self._row_header = None
                self._rows = []

    @staticmethod
    def _to_row_data_dict(headers, row):
        def _to_none(value):
            return "0" if value == "--" else value

        row = [_to_none(value) for value in row]
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


BasicFields = namedtuple("BasicFields", [
    "id",
    "assets",
    "liabilities",

    "share_capital",
    "capital_surplus",
    "retained_earnings",
    "other_equity",
    "treasure_stock",

    "total_equity_of_this_company",
    "equity_of_child_merge_from",
    "non_control_equity",
    "equity",

    "net_worth",
])


def _to_data(raw_data):
    def _pop_from_keys(keys, default_none=False, is_money=True):
        for key in keys:
            if key in raw_data:
                v = raw_data.pop(key).replace(",", "")
                if is_money and v != "0":
                    return v + "000"
                return v
        if default_none:
            return
        msg = f"Keys {keys} not in data {raw_data}"
        raise KeyError(msg)

    return {
        "assets_detail": {
            # General, stock exchange
            "current_assets": _pop_from_keys(["流動資產"], default_none=True),
            "non_current_assets": _pop_from_keys(["非流動資產"], default_none=True),

            # Bank, financial hold, insurance
            "cash": _pop_from_keys(["現金及約當現金"], default_none=True),
            "savings_in_other_bank": _pop_from_keys(["存放央行及拆借銀行同業", "存放央行及拆借金融同業"], default_none=True),
            "financial_assets_through_profit_or_loss": _pop_from_keys(["透過損益按公允價值衡量之金融資產"], default_none=True),
            "financial_assets_through_other": _pop_from_keys(["透過其他綜合損益按公允價值衡量之金融資產"], default_none=True),
            "invest_by_debt_tool": _pop_from_keys(["按攤銷後成本衡量之債務工具投資"], default_none=True),
            "assets_for_hedging": _pop_from_keys(["避險之衍生金融資產淨額", "避險之衍生金融資產"], default_none=True),
            "sell_back_bill_or_bond": _pop_from_keys(["附賣回票券及債券投資淨額", "附賣回票券及債券投資"], default_none=True),
            "accounts_receivable": _pop_from_keys(["應收款項－淨額", "應收款項"], default_none=True),
            "current_income_tax_overpaid": _pop_from_keys(["當期所得稅資產", "本期所得稅資產"], default_none=True),
            "unsell_assets": _pop_from_keys(["待出售資產－淨額", "待出售資產"], default_none=True),
            "assets_unpaid_to_owner": _pop_from_keys(["待分配予業主之資產－淨額", "待分配予業主之資產（或處分群組）"], default_none=True),
            "loans": _pop_from_keys(["貼現及放款－淨額"], default_none=True),
            
            # Financial hold, insurance
            "reinsurance_contract_assets": _pop_from_keys(["再保險合約資產－淨額", "再保險合約資產"], default_none=True),

            "invest_by_equity": _pop_from_keys(["採用權益法之投資－淨額", "投資"], default_none=True),
            "restricted_assets": _pop_from_keys(["受限制資產－淨額"], default_none=True),
            "other_financial_assets": _pop_from_keys(["其他金融資產－淨額"], default_none=True),
            "property_assets": _pop_from_keys(["不動產及設備－淨額", "不動產及設備"], default_none=True),
            "right_of_use_assets": _pop_from_keys(["使用權資產－淨額", "使用權資產"], default_none=True),
            "invest_property_assets": _pop_from_keys(["投資性不動產投資－淨額", "投資性不動產－淨額"], default_none=True),
            "intangible_assets": _pop_from_keys(["無形資產－淨額", "無形資產"], default_none=True),
            "income_tax_overpaid": _pop_from_keys(["遞延所得稅資產"], default_none=True),
            "other_assets": _pop_from_keys(["其他資產－淨額", "其他資產"], default_none=True),

            # insurance
            "invest_insurance_account_assets": _pop_from_keys(["分離帳戶保險商品資產"], default_none=True),
        },

        "liabilities_detail": {
            # General, stock exchange
            "current_liabilities": _pop_from_keys(["流動負債", "短期債務"], default_none=True),
            "non_current_liabilities": _pop_from_keys(["非流動負債"], default_none=True),

            "savings_from_other_bank": _pop_from_keys(["央行及銀行同業存款", "央行及金融同業存款"], default_none=True),
            "debt_from_other_bank": _pop_from_keys(["央行及同業融資"], default_none=True),
            "financial_liabilities_through_profit_or_loss": _pop_from_keys(["透過損益按公允價值衡量之金融負債"], default_none=True),
            "financial_liabilities_for_hedging": _pop_from_keys(["避險之衍生金融負債－淨額", "避險之衍生金融負債"], default_none=True),
            "buy_back_bill_or_bond": _pop_from_keys(["附買回票券及債券負債"], default_none=True),
            
            # Financial hold
            "commercial_paper_payable": _pop_from_keys(["應付商業本票－淨額"], default_none=True),
            
            "accounts_payable": _pop_from_keys(["應付款項"], default_none=True),
            "current_income_tax_unpaid": _pop_from_keys(["當期所得稅負債", "本期所得稅負債"], default_none=True),
            "liabilities_related_to_unsell_assets": _pop_from_keys(["與待出售資產直接相關之負債"], default_none=True),
            "savings": _pop_from_keys(["存款及匯款"], default_none=True),
            "bond_payable": _pop_from_keys(["應付金融債券", "應付債券"], default_none=True),
            "company_bond_payable": _pop_from_keys(["應付公司債", "其他借款"], default_none=True),
            "special_share_payable": _pop_from_keys(["特別股負債"], default_none=True),
            "other_financial_liabilities": _pop_from_keys(["其他金融負債"], default_none=True),
            "prepare_liabilities": _pop_from_keys(["負債準備"], default_none=True),
            "lease_liabilities": _pop_from_keys(["租賃負債"], default_none=True),

            # Insurance
            "insurance_product_liabilities": _pop_from_keys(["保險負債"], default_none=True),
            "financial_insurance_contract_prepare_liabilities": _pop_from_keys(["具金融商品性質之保險契約準備"], default_none=True),
            "foreign_currency_price_prepare_liabilities": _pop_from_keys(["外匯價格變動準備"], default_none=True),
            "invest_insurance_account_liabilities": _pop_from_keys(["分離帳戶保險商品負債"], default_none=True),

            "income_tax_unpaid": _pop_from_keys(["遞延所得稅負債"], default_none=True),
            "other_liabilities": _pop_from_keys(["其他負債"], default_none=True),
        },
        
        # Basic fields
        "virtual_currency": _pop_from_keys(["權益－具證券性質之虛擬通貨", "權益─具證券性質之虛擬通貨"], default_none=True),
        "share_of_child_merge_from": _pop_from_keys(["合併前非屬共同控制股權"], default_none=True),
        **BasicFields(
            id=_pop_from_keys(["公司"], is_money=False),
            assets=_pop_from_keys(["資產總計", "資產總額", "資產合計"]),
            liabilities=_pop_from_keys(["負債總計", "負債總額", "負債合計"]),
            share_capital=_pop_from_keys(["股本"]),
            capital_surplus=_pop_from_keys(["資本公積"]),
            retained_earnings=_pop_from_keys(["保留盈餘（或累積虧損）", "保留盈餘"]),
            other_equity=_pop_from_keys(["其他權益"]),
            treasure_stock=_pop_from_keys(["庫藏股票"]),
            total_equity_of_this_company=_pop_from_keys(["歸屬於母公司業主權益合計", "歸屬於母公司業主之權益合計", "歸屬於母公司業主之權益"]),
            equity_of_child_merge_from=_pop_from_keys(["共同控制下前手權益"]),
            non_control_equity=_pop_from_keys(["非控制權益"]),
            equity=_pop_from_keys(["權益總計", "權益總額", "權益合計"]),
            net_worth=_pop_from_keys(["每股參考淨值"], is_money=False),
        )._asdict(),
    }
