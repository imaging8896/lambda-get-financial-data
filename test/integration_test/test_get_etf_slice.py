import pytest

from data import get
from data.constant import ETF_Country


@pytest.mark.parametrize("etf_id, etf_country, expect_slice_infos", [
    ("00632R", ETF_Country.TW, [
        ["2024/12/11", "合併", "七股合併為一股(7:1)"],
    ]),
    ("0051", ETF_Country.TW, []),
    ("0050", ETF_Country.TW, [
        ["2025/06/11", "分割", "一股分為四股(1:4)"],
    ]),
    ("QQQ", ETF_Country.US, []),
    ("TQQQ", ETF_Country.US, [
        ["2022/01/13", "分割", "一股分為二股(1:2)"],
        ["2021/01/21", "分割", "一股分為二股(1:2)"],
        ["2018/05/24", "分割", "一股分為三股(1:3)"],
        ["2017/01/11", "分割", "一股分為二股(1:2)"],
        ["2014/01/24", "分割", "一股分為二股(1:2)"],
        ["2012/05/08", "分割", "一股分為二股(1:2)"],
    ]),
])
def test_get_etf_slice(etf_id, etf_country, expect_slice_infos):
    results = get("etf_slice", etf_id=etf_id, etf_country=etf_country.value)

    assert results == expect_slice_infos
