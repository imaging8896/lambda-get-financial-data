import logging
import re

from collections import namedtuple

from ..parser.html_parser import DataHTMLParser
from ..constant import StockType, RequestMethod


# https://mops.twse.com.tw/mops/web/t05st09_new#

logger = logging.getLogger(__name__)


class TwseDividendHTMLParser(DataHTMLParser):

    def __init__(self, request_cloud_scraper_mobile: bool, request_cloud_scraper_desktop: bool, stock_type: str, year: str, timeout: str = None) -> None:
        super().__init__(
            request_method=RequestMethod.POST,
            request_cloud_scraper_mobile=request_cloud_scraper_mobile,
            request_cloud_scraper_desktop=request_cloud_scraper_desktop,
        )

        self.stock_type = StockType(stock_type)
        self.year = int(year)
        self.timeout = int(timeout) if timeout else 20

        self._finished = False

        self._has_title = False
        self._entering_data_table = False
        self._entering_data_table_row_td = False
        self._entering_data_table_row_th = False

        self._stack = []
        self._data_groups = []
        self._data = []
        self._cur_row = None

        if year > 2020:
            self.expect_header1 = ('公司代號', '決議（擬議）進度', '股利所屬', '股利所屬', '期別', '董事會決議', '股東會', '期初未分配', '本期淨利', '可分配', '分配後期末未', '股東配發內容', '摘錄公司章程-', '備註')
            self.expect_header2 = ('盈餘分配', '法定盈餘', '資本公積', '股東配發', '盈餘轉', '法定盈餘', '資本公積', '股東配股')
        elif year > 2016:
            self.expect_header1 = ('公司代號', '決議（擬議）進度', '股利所屬', '股利所屬', '期別', '董事會決議', '股東會', '期初未分配', '本期淨利', '可分配', '分配後期末未', '股東配發內容', '摘錄公司章程-', '備註')
            self.expect_header2 = ('盈餘分配', '法定盈餘', '股東配發', '盈餘轉', '法定盈餘', '股東配股')
        else:
            self.expect_header1 = ('公司代號', '決議（擬議）進度', '股利所屬', '股利所屬', '期別', '董事會決議', '股東會', '期初未分配', '本期淨利', '可分配', '分配後期末未', '股東配發內容', '董監酬勞(元)', '員工紅利', '有無全數', '股東會', '摘錄公司章程-', '備註')
            self.expect_header2 = ('盈餘分配', '法定盈餘', '股東配發', '盈餘轉', '法定盈餘', '股東配股', '現金紅利', '股票紅利', '股票紅利', '股票紅利')

    @property
    def request_url(self) -> str:
        return "https://mops.twse.com.tw/server-java/t05st09sub"

    @property
    def request_kw(self) -> dict:
        return {
        "data": {
            "step": 1,
            "TYPEK": {
                StockType.PUBLIC: "sii",
                StockType.OTC: "otc",
                StockType.ROTC: "rotc",
            }[self.stock_type],
            "YEAR": f"{self.year - 1911}",
            "first": "",
            "qryType": 1,
        },
        "timeout": self.timeout,
    }

    @property
    def error(self) -> bool:
        if self._has_title:
            return False
        if self._finished:
            if not self._data_groups:
                return False # No data

            header1 = self._data[0]
            header2 = self._data[1]

            if header1 != self.expect_header1 or header2 != self.expect_header2:
                logger.error(f"Unexpected header. Expect\n{self.expect_header1=}\n{self.expect_header2=}\nGot\n{header1=}\n{header2=}")
                return True
            
            if len(self._data) > 2:
                expected_column_size = len(self._data[2])
                return any(len(row) != expected_column_size for row in self._data[2:])
        return False
    
    @property
    def data(self) -> dict:
        if self.error:
            raise RuntimeError(f"Error occurred when parsing\n{self.rawdata}")
        
        data = {}
        for data_group in self._data_groups:
            if data_group == [['']]:
                continue

            header1 = data_group[0]
            header2 = data_group[1]
            logger.info(f"Got headers\n{header1=}\n{header2=}")

            year = self.year

            for row_data in data_group[2:]:
                matched = re.match(r"^(\d+.*) - (.+)$", row_data[0])
                if not matched:
                    logger.error(f"Unexpected stock id and name\n{row_data}", exc_info=True)
                stock_id, stock_name = matched.groups()

                if stock_name == "測試帳號":
                    continue

                _fill_empty_fields(year, stock_id, row_data)

                if year > 2020:
                    dividend = _parse_after_2021(row_data)
                elif year > 2016 or \
                    (year == 2016 and stock_id == "4764" and len(row_data) < 25) or \
                        (year == 2016 and stock_id == "3306" and len(row_data) < 25) or \
                            (year == 2016 and stock_id == "3548" and len(row_data) < 25) or \
                                (year == 2016 and stock_id == "4923" and len(row_data) < 25) or \
                                    (year == 2016 and stock_id == "6508" and len(row_data) < 25):
                    dividend = _parse_between_2017_and_2020(row_data)
                else:
                    dividend = _parse_before_2016(row_data)

                if stock_id not in data:
                    data[stock_id] = []

                dividend.update({"year": year})

                logger.info(f"Got stock {stock_id} with dividend\n{dividend}")
                data[stock_id].append(dividend)
        
        return data
    
    def parse_response(self) -> None:
        response = self.request()
        response.encoding = "big5"
        self.feed(response.text)

    def handle_starttag(self, tag, attrs):
        self._stack.append(tag)
        if not self._finished:
            if tag == "table" and ("class", "hasBorder") in attrs:
                self._entering_data_table = True
            
            if tag == "tr" and self._entering_data_table:
                self._cur_row = []

            if tag == "td" and self._entering_data_table:
                self._cur_row.append("")
                self._entering_data_table_row_td = True

            if tag == "th" and self._entering_data_table:
                self._cur_row.append("")
                self._entering_data_table_row_th = True

    def handle_endtag(self, tag):
        if tag in self._stack:
            while self._stack[-1] != tag:
                self._stack.pop()
            self._stack.pop()
        
        if not self._finished:
            if tag == "table":
                self._entering_data_table = False
                if self._data:
                    self._data_groups.append(self._data)
                    self._data = []

            if tag == "tr" and self._entering_data_table and self._cur_row:
                self._data.append(self._cur_row)

            if tag == "td" and self._entering_data_table:
                self._entering_data_table_row_td = False

            if tag == "th" and self._entering_data_table:
                self._entering_data_table_row_th = False

    def handle_data(self, data):
        if not self._finished:
            if self._stack[-1] == "font" and self._stack[-2] == "h4" and data.strip() == "查無符合條件之資料":
                self._finished = True

            if self._entering_data_table_row_td:
                self._cur_row[-1] += data.strip().replace('\xa0', '')

            if self._entering_data_table_row_th:
                self._cur_row[-1] += data.strip()

            if self._stack[-1] == "b":
                if data.startswith("董事會決議（擬議）分配股利年度"):
                    self._has_title = True


def _fill_empty_fields(year: int, stock_id: str, row_data: list[str]):
    if year < 2021:
        if year == 2014 and stock_id == "1231":
            row_data[14], row_data[15] = "1.2", "0.0"

        elif year == 2020 and stock_id == "1784":
            pass
    
        elif year == 2012 and stock_id in {"1410", "3338", "4960"}:
            row_data[12], row_data[16] = "0.0", "0"

        elif year == 2012 and stock_id in {"2324"}:
            row_data[16] = "0"

        elif year == 2020 and stock_id in {"4577"}:
            row_data[13], row_data[14], row_data[15], row_data[16] = "0", "0.0", "0.0", "0"

        elif year == 2012 and stock_id in {"1258"}:
            row_data[11], row_data[12], row_data[14], row_data[15] = "2.2", "0.0", "0.0", "0.0"

        elif year == 2012 and (row_data[11] != "" and row_data[12] == "" and row_data[13] != "" and row_data[14] != "" and row_data[15] != "" and row_data[16] != ""):
            # "2724", "3114", "4109", "4113", "4406", "4510", "4953", "5443", "6203"
            row_data[12] = "0.0"

        elif year == 2012 and stock_id in {"4154", "4905", "8289"}:
            pass

        elif year == 2012 and stock_id in {"5516"}:
            row_data[11], row_data[12], row_data[14], row_data[15], row_data[16] = "1.0", "0.0", "0.0", "0.0", "0"

        else:
            if row_data[13] == "0":
                if row_data[11] not in {"0.0", "0", ""} or row_data[12] not in {"0.0", "0", ""}:
                    raise RuntimeError(f"Stock `{stock_id}`, year `{year}` without cash total with cashes")
            elif row_data[13] == "":
                pass
            else:
                if row_data[11] in {"0.0", "0", ""} and row_data[12] in {"0.0", "0", ""}:
                    if year == 2018 and stock_id == "3447":
                        pass # TWSE wrong data
                    else:
                        raise RuntimeError(f"Stock `{stock_id}`, year `{year}` with cash total without cash")

            if row_data[16] == "0":
                if row_data[14] not in {"0.0", "0", ""} or row_data[15] not in {"0.0", "0", ""}:
                    raise RuntimeError(f"Stock `{stock_id}`, year `{year}` without share total with shares")
            elif row_data[16] == "":
                pass
            else:
                if row_data[14] in {"0.0", "0", ""} and row_data[15] in {"0.0", "0", ""}:
                    if year == 2018 and stock_id == "3447":
                        pass # TWSE wrong data
                    else:
                        raise RuntimeError(f"Stock `{stock_id}`, year `{year}` with share total without share")

            for i in range(11, 17):
                row_data[i] = row_data[i] if row_data[i] else "0"

Dividend = namedtuple("Dividend", [
        "progress_status", 
        "dividend_cal_time_str",
        "dividend_cal_time",

        "time_index",

        "dividend_board_plan_time",
        "dividend_shareholder_time",

        "rest_last_time",
        "earn",
        "assignable",
        "unassign",

        "dividend_cash_per_share_from_earn",
        "dividend_cash_per_share_from_earn_accumulation",
        "dividend_cash_per_share_from_other_accumulation",
        "dividend_cash_total",

        "dividend_share_per_share_from_earn",
        "dividend_share_per_share_from_earn_accumulation",
        "dividend_share_per_share_from_other_accumulation",
        "dividend_share_total",

        "note",
    ]
)


def _parse_after_2021(td_texts: list[str]):
    return Dividend(
        progress_status=td_texts[1],
        dividend_cal_time_str=td_texts[2],
        dividend_cal_time=td_texts[3],

        time_index=td_texts[4], # I don't know this

        dividend_board_plan_time = None if td_texts[5] in {"0"} else td_texts[5],
        dividend_shareholder_time = None if td_texts[6] in {"不適用", "&nbsp"} else td_texts[6],
        
        rest_last_time = td_texts[7].replace(",", ""),
        earn =           td_texts[8].replace(",", ""),
        assignable =     td_texts[9].replace(",", ""),
        unassign =       td_texts[10].replace(",", ""),

        dividend_cash_per_share_from_earn = td_texts[11].replace(",", ""),
        dividend_cash_per_share_from_earn_accumulation = td_texts[12].replace(",", ""),
        dividend_cash_per_share_from_other_accumulation = td_texts[13].replace(",", ""),
        dividend_cash_total = "0" if td_texts[14] == "" else td_texts[14].replace(",", ""),

        dividend_share_per_share_from_earn = "0" if td_texts[15] == "" else td_texts[15].replace(",", ""),
        dividend_share_per_share_from_earn_accumulation = "0" if td_texts[16] == "" else td_texts[16].replace(",", ""),
        dividend_share_per_share_from_other_accumulation = td_texts[17].replace(",", ""),
        dividend_share_total = "0" if td_texts[18] == "" else td_texts[18].replace(",", ""),

        note = None if td_texts[19] in {"無", "", "無。"} else td_texts[19],
    )._asdict()


def _parse_between_2017_and_2020(td_texts: list[str]):
    return Dividend(
        progress_status=td_texts[1],
        dividend_cal_time_str=td_texts[2],
        dividend_cal_time=td_texts[3],

        time_index=td_texts[4], # I don't know this

        dividend_board_plan_time = None if td_texts[5] in {"0"} else td_texts[5],
        dividend_shareholder_time = None if td_texts[6] in {"不適用", "&nbsp"} else td_texts[6],

        rest_last_time = td_texts[7].replace(",", ""),
        earn =           td_texts[8].replace(",", ""),
        assignable =     td_texts[9].replace(",", ""),
        unassign =       td_texts[10].replace(",", ""),

        dividend_cash_per_share_from_earn = td_texts[11].replace(",", ""),
        dividend_cash_per_share_from_earn_accumulation = "0.0",
        dividend_cash_per_share_from_other_accumulation = td_texts[12].replace(",", ""),
        dividend_cash_total = td_texts[13].replace(",", ""),

        dividend_share_per_share_from_earn = td_texts[14].replace(",", ""),
        dividend_share_per_share_from_earn_accumulation = "0.0",
        dividend_share_per_share_from_other_accumulation = td_texts[15].replace(",", ""),
        dividend_share_total = td_texts[16].replace(",", ""),

        note = None if td_texts[17] in {"無", ""} else td_texts[17],
    )._asdict()


def _parse_before_2016(td_texts: list[str]):
    # ['2450 - 神腦', '股東會確認', '104年年度', '104/01/01~104/12/31', '1', '0', '105/06/27', 
    # '931,058,057', '803,346,670', '1,653,407,984', '908,650,013', '3.00000000', '0.0', 
    # '744,757,971', '0.0', '0.0', '0', '0', '0', '0', '0', '0.00000', '無', '', 
    # '本公司年度決算如有盈餘，應依法完納稅捐、彌補虧損，次提百分之十為法定盈餘公積及依法令;或主管機關規定提撥或迴轉特別盈餘公積後，就其餘額除由董事會提請股東會決議保留外，如尚有盈餘連同以往年度未分配盈餘，由股東會決議保留或分派之。', '']
    if len(td_texts) < 25:
        raise RuntimeError(f"[twse] Not enough column expect 25. Got\n{td_texts}")

    return Dividend(
        progress_status=td_texts[1],
        dividend_cal_time_str=td_texts[2],
        dividend_cal_time=td_texts[3],

        time_index=td_texts[4], # I don't know this

        dividend_board_plan_time= None if td_texts[5] in {"0"} else td_texts[5],
        dividend_shareholder_time= None if td_texts[6] in {"不適用", "&nbsp"} else td_texts[6],
        
        rest_last_time= td_texts[7].replace(",", ""),
        earn=           td_texts[8].replace(",", ""),
        assignable=     td_texts[9].replace(",", ""),
        unassign=       td_texts[10].replace(",", ""),

        dividend_cash_per_share_from_earn= td_texts[11].replace(",", ""),
        dividend_cash_per_share_from_earn_accumulation= "0.0",
        dividend_cash_per_share_from_other_accumulation= td_texts[12].replace(",", ""),
        dividend_cash_total= td_texts[13].replace(",", ""),

        # 1231 in 2014 year bug
        dividend_share_per_share_from_earn= td_texts[14].replace(",", ""),
        dividend_share_per_share_from_earn_accumulation= "0.0",
        dividend_share_per_share_from_other_accumulation= td_texts[15].replace(",", ""),
        dividend_share_total= td_texts[16].replace(",", ""),

        note= None if td_texts[24] in {"無", ""} else td_texts[24],
    )._asdict()
