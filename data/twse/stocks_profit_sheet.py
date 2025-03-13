from collections import namedtuple

from . import RedirectOldParser, TwseHTMLTableParser
from ..parser.html_parser import DataParser
from ..constant import StockType, RequestMethod


# https://mops.twse.com.tw/mops/#/web/t163sb04


class TwseStocksProfitSheetParser(RedirectOldParser):
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
                "apiName": "ajax_t163sb04",
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
        return _TwseStocksProfitSheetHTMLParser(self.request_cloud_scraper_mobile, self.request_cloud_scraper_desktop, self.stock_type, url, self.year, self.quarter, self.timeout)


class _TwseStocksProfitSheetHTMLParser(TwseHTMLTableParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_type: StockType, url: str, year: int, quarter: int, timeout: str = None) -> None:
        super().__init__(
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
            request_method=RequestMethod.GET,
            url=url,
            timeout=timeout,
        )

        self.stock_type = stock_type
        self.year = year
        self.quarter = quarter

    @property
    def data(self) -> dict:
        return [_to_data(raw_data, self.year, self.quarter) for raw_data in self._data]


BasicFields = namedtuple("BasicFields", [
    "id",
    "operating_revenue",
    "operating_revenue_detail",
    "profit_before_tax",
    "income_tax",
    "profit",
    "other_profit",
    "other_profit_from_merged_company",
    "comprehensive_profit",
    "profit_detail",
    "comprehensive_profit_detail",
    "eps",
])


def _to_data(raw_data, year, quarter):
    # XXX Workaround for dirty data 6693 in 2018 Q2 which EPS is '--'
    if raw_data["基本每股盈餘（元）"] == "--" and raw_data["公司"] == "6693" and year == 2018 and quarter == 2:
        raw_data["基本每股盈餘（元）"] = "0.53" # From Goodinfo

    def _pop_from_keys(keys, default_none=False, is_money=True, preserve_key=False):
        for key in keys:
            if key in raw_data:
                v = raw_data.pop(key).replace(",", "")

                if preserve_key:
                    raw_data[key] = v

                v = "0" if v == "--" else v

                if is_money and v != "0":
                    return v + "000"
                return v
        if default_none:
            return
        msg = f"{keys=} are not in data {raw_data}"
        raise KeyError(msg)
    
    def _merge_value_of_keys(keys):
        values = [_pop_from_keys([key], preserve_key=True) for key in keys]
        return str(sum([int(v) for v in values if v]))
    
    def _get_operating_revenue():
        if v := _pop_from_keys(["營業收入", "收益", "收入"], default_none=True):
            return v
        elif "利息淨收益" in raw_data:
            if "利息以外淨損益" in raw_data:
                return _merge_value_of_keys(["利息淨收益", "利息以外淨損益"])
            elif "利息以外淨收益" in raw_data:
                return _merge_value_of_keys(["利息淨收益", "利息以外淨收益"])
        raise KeyError(f"Operating revenue not defined in\n{raw_data}")

    return {
        ## General, Stock exchange
        # 營業成本是指相關銷售產品的直接成本，但它不包括間接成本，兩者的差別如下： 
        # 直接成本：每銷售一個物品就必須付出的成本，例如：運費、儲存成本、購買原料的成本。 在財報上一般是歸屬「營業成本」。 
        # 間接成本：不管商品銷售量多寡，都會一定會付出的成本，像是辦公室租金、水電費、人事、行銷
        "operating_costs": _pop_from_keys(["營業成本"], default_none=True),

        "biological_assets_profit_or_loss": _pop_from_keys(["原始認列生物資產及農產品之利益（損失）"], default_none=True),
        "biological_assets_current_profit_or_loss": _pop_from_keys(["生物資產當期公允價值減出售成本之變動利益（損失）"], default_none=True),
        
        "operating_gross_profit": _pop_from_keys(["營業毛利（毛損）"], default_none=True),

        # Should exclude from gross profit
        "unrealized_selling_profit": _pop_from_keys(["未實現銷貨（損）益"], default_none=True),
        "realized_selling_profit": _pop_from_keys(["已實現銷貨（損）益"], default_none=True),

        "net_operating_gross_profit": _pop_from_keys(["營業毛利（毛損）淨額"], default_none=True),

        "operating_expenses": _pop_from_keys(["營業費用", "支出及費用", "支出"], default_none=True),
        "net_other_expenses_or_profit": _pop_from_keys(["其他收益及費損淨額"], default_none=True),

        "operating_profit": _pop_from_keys(["營業利益（損失）", "營業利益"], default_none=True),

        "non_operating_profit": _pop_from_keys(["營業外收入及支出", "營業外損益"], default_none=True),

        ## Bank, Financial holder
        # Cost
        "prepare_bad_debt": _pop_from_keys(["呆帳費用、承諾及保證責任準備提存", "呆帳費用及保證責任準備提存", "呆帳費用及保證責任準備提存（各項提存）"], default_none=True),
       
        ## Financial holder
        # Cost
        "prepare_insurance_debt": _pop_from_keys(["保險負債準備淨變動"], default_none=True),

        # Basic fields
        **BasicFields(
            id=_pop_from_keys(["公司"], is_money=False),
            operating_revenue=_get_operating_revenue(),
            operating_revenue_detail={
                "interest_revenue": _pop_from_keys(["利息淨收益"], default_none=True),
                "non_interest_revenue": _pop_from_keys(["利息以外淨損益", "利息以外淨收益"], default_none=True),
            },
            profit_before_tax=_pop_from_keys(["稅前淨利（淨損）", "繼續營業單位稅前淨利（淨損）", "繼續營業單位稅前損益", "繼續營業單位稅前純益（純損）"]),
            income_tax=_pop_from_keys(["所得稅費用（利益）", "所得稅（費用）利益", "所得稅利益（費用）"]),
            profit=_pop_from_keys(["本期淨利（淨損）", "本期稅後淨利（淨損）"]),
            # 讓股東 "賺/虧" 到，但是卻不能認列在 "本期損益" 的項目。
            # 1、備供出售金融資產之未實現評價損益
            # 2、現金流量避險工具之末實現評價損益(僅有效避險部分)
            # 3、國外營運機構財報換算之兌換差額
            # 4、資產重估增值
            # 5、符合條件之 確定福利計畫精算損益
            # 6、採用權益法認列所享有 之關聯企業及合資 的其他綜合損益
            # 例如花10億投資某公司，結果該公司股票價值只剩8億，這個2億的虧損，會被記在這裡。
            other_profit=_pop_from_keys(["其他綜合損益（淨額）", "其他綜合損益（稅後）", "本期其他綜合損益（稅後淨額）", "其他綜合損益（稅後淨額）", "其他綜合損益"]),
            other_profit_from_merged_company=_pop_from_keys(["合併前非屬共同控制股權綜合損益淨額"], default_none=True),
            comprehensive_profit=_pop_from_keys(["本期綜合損益總額", "本期綜合損益總額（稅後）"]),
            profit_detail={
                "this_company": _pop_from_keys(["淨利（淨損）歸屬於母公司業主", "淨利（損）歸屬於母公司業主"], default_none=True),
                "from_before_merge": _pop_from_keys(["淨利（淨損）歸屬於共同控制下前手權益", "淨利（損）歸屬於共同控制下前手權益"], default_none=True),
                "non_control_equity": _pop_from_keys(["淨利（淨損）歸屬於非控制權益", "淨利（損）歸屬於非控制權益"], default_none=True),
                "from_continuing_operation": _pop_from_keys(["繼續營業單位本期淨利（淨損）", "繼續營業單位本期稅後淨利（淨損）", "繼續營業單位本期純益（純損）"], default_none=True),
                "from_discontinuing_operation": _pop_from_keys(["停業單位損益"], default_none=True),
                "from_merged_company": _pop_from_keys(["合併前非屬共同控制股權損益"], default_none=True),
            },
            comprehensive_profit_detail={
                "this_company": _pop_from_keys(["綜合損益總額歸屬於母公司業主"], default_none=True),
                "from_before_merge": _pop_from_keys(["綜合損益總額歸屬於共同控制下前手權益"], default_none=True),
                "non_control_equity": _pop_from_keys(["綜合損益總額歸屬於非控制權益"], default_none=True),
            },
            eps=_pop_from_keys(["基本每股盈餘（元）"], is_money=False),
        )._asdict(),
    }
