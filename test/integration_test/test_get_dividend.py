import pytest

from datetime import datetime

from data import get
from data.constant import StockType


@pytest.mark.parametrize("year, stock_type, timeout, test_stock_id, expect_dividends", [
    (2025, StockType.PUBLIC, 20, "3443", [
        {
            'progress_status': '股東會確認', 
            'dividend_cal_time_str': '113年年度', 
            'dividend_cal_time': '113/01/01~113/12/31', 
            'time_index': '1', 
            'dividend_board_plan_time': '114/01/23', 
            'dividend_shareholder_time': '114/05/15', 
            'rest_last_time': '4653244650', 
            'earn': '3450587494', 
            'assignable': '7796291983', 
            'unassign': '5652101407', 
            'dividend_cash_per_share_from_earn': '16.00000000', 
            'dividend_cash_per_share_from_earn_accumulation': '0.0', 
            'dividend_cash_per_share_from_other_accumulation': '0.0', 
            'dividend_cash_total': '2144190576', 
            'dividend_share_per_share_from_earn': '0.0', 
            'dividend_share_per_share_from_earn_accumulation': '0.0', 
            'dividend_share_per_share_from_other_accumulation': '0.0', 
            'dividend_share_total': '0', 
            'note': """公司無盈餘時，不得分派股息及紅利。
本公司分派每一會計年度盈餘時，應先彌補歷年虧損，並依下列順序提列後分派之：
（一）提列百分之十為法定盈餘公積；但法定盈餘公積累積已達本公司資本總額時，不在此限。
（二）依法令或主管機關規定經股東會決議得提列特別盈餘公積。
（三）餘額得為股東紅利，依股東會決議按股份總數比例分派之。
於當年度公司無盈餘可分派，或雖有盈餘但盈餘數額遠低於公司前一年度實際分派之盈餘，或依公司財務、業務及經營面等因素之考量，得將公積全部或一部依法令或主管機關規定分派。""", 
            'year': 2025
        }
    ]),
    (2024, StockType.ROTC, 100, "6586", [
        {
            'assignable': '-306086468',
            'dividend_board_plan_time': '113/12/12',
            'dividend_cal_time': '113/07/01~113/09/30',
            'dividend_cal_time_str': '113年第3季',
            'dividend_cash_per_share_from_earn': '0.0',
            'dividend_cash_per_share_from_earn_accumulation': '0.0',
            'dividend_cash_per_share_from_other_accumulation': '0.0',
            'dividend_cash_total': '0',
            'dividend_share_per_share_from_earn': '0.0',
            'dividend_share_per_share_from_earn_accumulation': '0.0',
            'dividend_share_per_share_from_other_accumulation': '0.0',
            'dividend_share_total': '0',
            'dividend_shareholder_time': None,
            'earn': '0',
            'note': '本公司盈餘分派或虧損撥補得於每季終了\n'
                    '後為之，每季決算如有盈餘，應先提繳稅\n'
                    '款，彌補以往虧損，次提百分之十為法定\n'
                    '盈餘公積，另依法令或主管機關規定提撥\n'
                    '或迴轉特別盈餘公積，其餘額累計未分配\n'
                    '之盈餘由董事會擬具股東股息或紅利分派\n'
                    '議案，以發行新股方式為之，提請股東會\n'
                    '決議後分派之；以現金方式為之時，由董\n'
                    '事會決議之。\n'
                    '本公司年度總決算如有盈餘，應先提繳稅\n'
                    '款，彌補以往虧損，次提百分之十為法定\n'
                    '盈餘公積，另依法令或主管機關規定提撥\n'
                    '或迴轉特別盈餘公積，其餘額累計未分配\n'
                    '之盈餘由董事會擬具股東股息或紅利分派\n'
                    '議案提請股東會決議分派之。',
            'progress_status': '董事會決議',
            'rest_last_time': '-306086468',
            'time_index': '1',
            'unassign': '-306086468',
            'year': 2024
        },
        {
            'assignable': '-306086468',
            'dividend_board_plan_time': '113/08/08',
            'dividend_cal_time': '113/04/01~113/06/30',
            'dividend_cal_time_str': '113年第2季',
            'dividend_cash_per_share_from_earn': '0.0',
            'dividend_cash_per_share_from_earn_accumulation': '0.0',
            'dividend_cash_per_share_from_other_accumulation': '0.0',
            'dividend_cash_total': '0',
            'dividend_share_per_share_from_earn': '0.0',
            'dividend_share_per_share_from_earn_accumulation': '0.0',
            'dividend_share_per_share_from_other_accumulation': '0.0',
            'dividend_share_total': '0',
            'dividend_shareholder_time': None,
            'earn': '0',
            'note': '本公司盈餘分派或虧損撥補得於每季終了\n'
                    '後為之，每季決算如有盈餘，應先提繳稅\n'
                    '款，彌補以往虧損，次提百分之十為法定\n'
                    '盈餘公積，另依法令或主管機關規定提撥\n'
                    '或迴轉特別盈餘公積，其餘額累計未分配\n'
                    '之盈餘由董事會擬具股東股息或紅利分派\n'
                    '議案，以發行新股方式為之，提請股東會\n'
                    '決議後分派之；以現金方式為之時，由董\n'
                    '事會決議之。\n'
                    '本公司年度總決算如有盈餘，應先提繳稅\n'
                    '款，彌補以往虧損，次提百分之十為法定\n'
                    '盈餘公積，另依法令或主管機關規定提撥\n'
                    '或迴轉特別盈餘公積，其餘額累計未分配\n'
                    '之盈餘由董事會擬具股東股息或紅利分派\n'
                    '議案提請股東會決議分派之。',
            'progress_status': '董事會決議',
            'rest_last_time': '-306086468',
            'time_index': '1',
            'unassign': '-306086468',
            'year': 2024
        },
        {
            'assignable': '-306086468',
            'dividend_board_plan_time': '113/05/23',
            'dividend_cal_time': '113/01/01~113/03/31',
            'dividend_cal_time_str': '113年第1季',
            'dividend_cash_per_share_from_earn': '0.0',
            'dividend_cash_per_share_from_earn_accumulation': '0.0',
            'dividend_cash_per_share_from_other_accumulation': '0.0',
            'dividend_cash_total': '0',
            'dividend_share_per_share_from_earn': '0.0',
            'dividend_share_per_share_from_earn_accumulation': '0.0',
            'dividend_share_per_share_from_other_accumulation': '0.0',
            'dividend_share_total': '0',
            'dividend_shareholder_time': None,
            'earn': '0',
            'note': '本公司盈餘分派或虧損撥補得於每季終了\n'
                    '後為之，每季決算如有盈餘，應先提繳稅\n'
                    '款，彌補以往虧損，次提百分之十為法定\n'
                    '盈餘公積，另依法令或主管機關規定提撥\n'
                    '或迴轉特別盈餘公積，其餘額累計未分配\n'
                    '之盈餘由董事會擬具股東股息或紅利分派\n'
                    '議案，以發行新股方式為之，提請股東會\n'
                    '決議後分派之；以現金方式為之時，由董\n'
                    '事會決議之。\n'
                    '本公司年度總決算如有盈餘，應先提繳稅\n'
                    '款，彌補以往虧損，次提百分之十為法定\n'
                    '盈餘公積，另依法令或主管機關規定提撥\n'
                    '或迴轉特別盈餘公積，其餘額累計未分配\n'
                    '之盈餘由董事會擬具股東股息或紅利分派\n'
                    '議案提請股東會決議分派之。',
            'progress_status': '董事會決議',
            'rest_last_time': '-306086468',
            'time_index': '1',
            'unassign': '-306086468',
            'year': 2024
        },
        {
            'assignable': '-306086468',
            'dividend_board_plan_time': '113/03/14',
            'dividend_cal_time': '112/10/01~112/12/31',
            'dividend_cal_time_str': '112年第4季',
            'dividend_cash_per_share_from_earn': '0.0',
            'dividend_cash_per_share_from_earn_accumulation': '0.0',
            'dividend_cash_per_share_from_other_accumulation': '0.0',
            'dividend_cash_total': '0',
            'dividend_share_per_share_from_earn': '0.0',
            'dividend_share_per_share_from_earn_accumulation': '0.0',
            'dividend_share_per_share_from_other_accumulation': '0.0',
            'dividend_share_total': '0',
            'dividend_shareholder_time': '113/06/27',
            'earn': '-306086468',
            'note': '本公司盈餘分派或虧損撥補得於每季終了\n'
                    '後為之，每季決算如有盈餘，應先提繳稅\n'
                    '款，彌補以往虧損，次提百分之十為法定\n'
                    '盈餘公積，另依法令或主管機關規定提撥\n'
                    '或迴轉特別盈餘公積，其餘額累計未分配\n'
                    '之盈餘由董事會擬具股東股息或紅利分派\n'
                    '議案，以發行新股方式為之，提請股東會\n'
                    '決議後分派之；以現金方式為之時，由董\n'
                    '事會決議之。\n'
                    '本公司年度總決算如有盈餘，應先提繳稅\n'
                    '款，彌補以往虧損，次提百分之十為法定\n'
                    '盈餘公積，另依法令或主管機關規定提撥\n'
                    '或迴轉特別盈餘公積，其餘額累計未分配\n'
                    '之盈餘由董事會擬具股東股息或紅利分派\n'
                    '議案提請股東會決議分派之。',
            'progress_status': '股東會確認',
            'rest_last_time': '-544318185',
            'time_index': '1',
            'unassign': '-306086468',
            'year': 2024
        }
    ]),
    (2018, StockType.OTC, 40, "6629", [
        {
            'assignable': '105871163',
            'dividend_board_plan_time': '107/06/22',
            'dividend_cal_time': '106/07/01~106/12/31',
            'dividend_cal_time_str': '106年下半年',
            'dividend_cash_per_share_from_earn': '3.00000000',
            'dividend_cash_per_share_from_earn_accumulation': '0.0',
            'dividend_cash_per_share_from_other_accumulation': '0.0',
            'dividend_cash_total': '90000000',
            'dividend_share_per_share_from_earn': '0.0',
            'dividend_share_per_share_from_earn_accumulation': '0.0',
            'dividend_share_per_share_from_other_accumulation': '0.0',
            'dividend_share_total': '0',
            'dividend_shareholder_time': '107/06/27',
            'earn': '126564696',
            'note': '14.5就本公司股利政策之決定，董事會了解本公司營運之業務係屬成長階段。於各會計年度建請股東同意之股利或其他分派數額（若有）之決定，董事會：\r\n'
                    '（a)得考量本公司各該會計年度之盈餘、整體發展、財務規劃、資本需求、產業展望及本公司未來前景等，以確保股東權利及利益之保障；及\r\n'
                    '（b)除依本章程第14.4條提撥外，應於當期淨利中提列：（i）支付相關會計年度稅款之準備金；（ii）彌補虧損；（iii）百分之十之一般公積（下稱「法定盈餘公積」），及（iv）董事會依證券主管機關依公開發行公司規則要求之特別盈餘公積或本章程第15.1條決議之公積。',
            'progress_status': '股東會確認',
            'rest_last_time': '14697537',
            'time_index': '1',
            'unassign': '15871163',
            'year': 2018,
        }
    ]),
    (2013, StockType.PUBLIC, 30, "1102", [
        {
            'assignable': '12744001917',
            'dividend_board_plan_time': None,
            'dividend_cal_time': '101/01/01~101/12/31',
            'dividend_cal_time_str': '101年年度',
            'dividend_cash_per_share_from_earn': '1.70000000',
            'dividend_cash_per_share_from_earn_accumulation': '0.0',
            'dividend_cash_per_share_from_other_accumulation': '0.0',
            'dividend_cash_total': '5492560783',
            'dividend_share_per_share_from_earn': '0.20000000',
            'dividend_share_per_share_from_earn_accumulation': '0.0',
            'dividend_share_per_share_from_other_accumulation': '0.0',
            'dividend_share_total': '64618362',
            'dividend_shareholder_time': '102/06/21',
            'earn': '6235191559',
            'note': """1.本公司股利應參酌所營事業景氣變化之特性，考量各項產品或服務所處生命週期對未來資金之需求與稅制之影響，在維持穩定股利之目標下，依本公司章程所訂比例分配之。股利之發放，其現金股利部分不低於當年度股息及股東紅利總和之百分之十。\r
2.本公司每年決算如有盈餘，於依法繳納營利事業所得稅後，應先彌補歷年虧損，如尚有盈餘，於提列法定盈餘公積百分之十，並按法令規定提列特別盈餘公積後，再將其餘額連同上年度累積未分配盈餘，作為可供分配之盈餘，惟得視業務狀況酌予保留一部分後，按後列百分比分配之：\r
一、股息百分之六十，按全部股份平均分派。但遇增加資本時，除法令另有規定外，其當年度新增股份應分派之股息，依照股東會之決議辦理。\r
二、股東紅利百分之三十三，按全部股份平均分派。但遇增加資本時，其當年度新增股份應分派之紅利，依照股東會之決議辦理。\r
三、董事、監察人酬勞金百分之三。\r
四、員工紅利百分之四。""",
            'progress_status': '股東會確認',
            'rest_last_time': '7196455761',
            'time_index': '1',
            'unassign': '6605257514',
            'year': 2013,
        }
    ]),
    (2013, StockType.PUBLIC, 30, "6168", [
        {
            'assignable': '-510314553',
            'dividend_board_plan_time': None,
            'dividend_cal_time': '101/01/01~101/12/31',
            'dividend_cal_time_str': '101年年度',
            'dividend_cash_per_share_from_earn': '0.0',
            'dividend_cash_per_share_from_earn_accumulation': '0.0',
            'dividend_cash_per_share_from_other_accumulation': '0.0',
            'dividend_cash_total': '0',
            'dividend_share_per_share_from_earn': '0.0',
            'dividend_share_per_share_from_earn_accumulation': '0.0',
            'dividend_share_per_share_from_other_accumulation': '0.0',
            'dividend_share_total': '0',
            'dividend_shareholder_time': '102/06/18',
            'earn': '-532483032',
            'note': """本公司年度決算如有盈餘，依下列順序分派之。\r
  一、提繳稅捐。\r
  二、彌補虧損。\r
  三、提存百分之十為法定盈餘公積。\r
  四、依法令或主管機關規定提撥或迴轉特\r
      別盈餘公積。\r
  五、董事監察人酬勞金就一至四款規定數\r
      額後剩餘之數提撥不高於百分之一。\r
  六、提撥員工紅利不得低於一至四款規定\r
      數額後之6%，不得高於12%。員工紅\r
      利之分派得以現金或股票方式發放，\r
      其中股票紅利分配對象得包括符合一\r
      定條件之從屬公司員工，該一定條件\r
      授權董事會訂定之。\r
  七、餘額為股東紅利。\r
本公司股東紅利之分配得以現金或股票方式發放，惟現金股利分派之比例以不低於股利總額之百分之二十。董監事酬勞以現金發放。本公司目前所屬產業正處於成長階段，分配股利之政策，須視公司目前及未來之投資環境、資金需求、國內外競爭狀況及資本預算等因素，兼顧股東利益、平衡股利及公司長期財務規劃等，每年依法由董事會擬具分派案，提報股東會。""",
            'progress_status': '股東會確認',
            'rest_last_time': '22168479',
            'time_index': '1',
            'unassign': '0',
            'year': 2013
        }
    ]),
])
def test_get_dividend(year, stock_type, timeout, test_stock_id, expect_dividends):
    results = get("dividend", year=year, stock_type=stock_type.value, timeout=timeout)[test_stock_id]

    assert results == expect_dividends


@pytest.mark.parametrize("stock_type", [x for x in StockType])
def test_get_latest_dividend(stock_type):
    now = datetime.now()

    assert isinstance(get("dividend", year=now.year, stock_type=stock_type.value, timeout=20), dict)


@pytest.mark.parametrize("stock_type", [x for x in StockType])
def test_get_no_dividend(stock_type):
    assert {} == get("dividend", year=3000, stock_type=stock_type.value, timeout=20)
