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

    if expect_slice_infos:
        for expect_slice_info in expect_slice_infos:
            assert expect_slice_info in results, f"Expected slice info {expect_slice_info} not found in results {results}"
    else:
        assert not results, f"Expected no slice info for {etf_id} in {etf_country}, but got {results}"
