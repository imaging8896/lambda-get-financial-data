import pytest
import time
import requests

from data import get
from data.exception import BlockingByWebsiteError
from data.constant import StockType


@pytest.mark.parametrize("stock_type, expect_stocks", [
    (StockType.PUBLIC, [
        {'id': '2330', 'long_name': '台灣積體電路製造股份有限公司', 'name': '台積電', 'stock_group': '半導體業', 'register_foreign_country': None, 'address': '新竹科學園區力行六路8號', 'invoice_number': '22099131', 'chairman': '魏哲家', 'manager': '總裁: 魏哲家', 'spokesman': '黃仁昭', 'spokesman_title': '資深副總經理暨財務長', 'acting_spokesman': '高孟華', 'phone': '03-5636688', 'create_date': '1987-02-21', 'public_date': '1994-09-05', 'share_unit': '新台幣10.0000元', 'capital': '259327332420', 'public_shares': '25932733242', 'private_shares': '0', 'special_shares': '0', 'financial_repport_type': '合併', 'dividend_assign_period': '每季', 'dividend_assign_decide_leve': '董事會', 'english_name': 'TSMC', 'english_address': 'No. 8, Li-Hsin Rd. 6, Hsinchu Science Park,\nHsin-Chu 300096, Taiwan, R.O.C.', 'email': 'invest@tsmc.com', 'website': 'https://www.tsmc.com', 'investor': '蘇志凱', 'investor_title': '處長', 'investor_phone': '03-568-2089', 'investor_email': 'jeff_su@tsmc.com', 'investor_website': 'https://esg.tsmc.com/zh-Hant/sustainable-management/materiality-analysis'}
    ]),
    (StockType.OTC, [
        {'id': '3268', 'long_name': '海德威電子工業股份有限公司', 'name': '海德威', 'stock_group': '半導體業', 'register_foreign_country': None, 'address': '台中市西屯區台灣大道四段925號14F-6', 'invoice_number': '86105539', 'chairman': '黃 (方方土) 芳', 'manager': '游賜傑', 'spokesman': '游賜傑', 'spokesman_title': '總經理', 'acting_spokesman': '楊仁德', 'phone': '(04)2355-0011', 'create_date': '1991-04-13', 'public_date': '2005-01-27', 'share_unit': '新台幣10.0000元', 'capital': '347207960', 'public_shares': '34720796', 'private_shares': '0', 'special_shares': '0', 'financial_repport_type': '合併', 'dividend_assign_period': '每年', 'dividend_assign_decide_leve': '股東會', 'english_name': 'Higher Way', 'english_address': '14F-6  No.925, Sec. 4, Taiwan Boulevard, Xitun Dist\nTaichung, Taiwan, R.O.C', 'email': 'fina.inve@higherway.com.tw', 'website': 'www.higherway.com.tw', 'investor': '劉姿幸', 'investor_title': '處長', 'investor_phone': '04-23550011', 'investor_email': 'fina.inve@higherway.com.tw', 'investor_website': 'www.higherway.com.tw'}
    ]),
    (StockType.ROTC, [
        {'id': '1260', 'long_name': '富味鄉食品股份有限公司', 'name': '富味鄉', 'stock_group': '食品工業', 'register_foreign_country': None, 'address': '台北市大安區市民大道四段102號11樓', 'invoice_number': '12467902', 'chairman': '陳昶宏', 'manager': '劉兆華', 'spokesman': '陳淑紋', 'spokesman_title': '副總經理', 'acting_spokesman': '李芳怡', 'phone': '(02)2750-5667', 'create_date': '1983-11-08', 'public_date': '2012-11-26', 'share_unit': '新台幣10.0000元', 'capital': '1020981820', 'public_shares': '102098182', 'private_shares': '0', 'special_shares': '0', 'financial_repport_type': '合併', 'dividend_assign_period': '每年', 'dividend_assign_decide_leve': '董事會', 'english_name': 'FLAVOR', 'english_address': '11F., No. 102, Sec. 4, Civic Blvd., Da`an Dist.,\nTaipei City 106, Taiwan', 'email': 'flavor@flavor.com.tw', 'website': 'www.flavor.com.tw', 'investor': None, 'investor_title': None, 'investor_phone': None, 'investor_email': None, 'investor_website': 'www.flavor.com.tw'},
    ]),
])
def test_get_stock(stock_type, expect_stocks):
    results = None
    for i in range(5):
        try:
            results = get("stock", stock_type=stock_type.value, timeout=60)
            break
        except (requests.exceptions.HTTPError, BlockingByWebsiteError) as e:
            print(e)
            time.sleep(2.3 * (i + 1))

    assert results is not None, "Failed to get stock data"

    for expect_stock in expect_stocks:
        assert expect_stock in results
