import pytest

from data import get
from data.constant import ETF_Country


@pytest.mark.parametrize("etf_id, etf_country, years, expect_dividends", [
    ("00632R", ETF_Country.TW, 1, []),
    ("00632R", ETF_Country.TW, 20, []),
    ("00646", ETF_Country.TW, 20, []),
    ("0050", ETF_Country.TW, 20, [
        {'dividend_year': 2025, 'dividend_quarter': 2, 'dividend_value': '0.36', 'dividend_return_rate': '0.73', 'dividend_date': '2025-07-21'}, 
        {'dividend_year': 2024, 'dividend_quarter': 4, 'dividend_value': '2.7', 'dividend_return_rate': '1.36', 'dividend_date': '2025-01-17'}, 
        {'dividend_year': 2024, 'dividend_quarter': 2, 'dividend_value': '1', 'dividend_return_rate': '0.51', 'dividend_date': '2024-07-16'}
    ]),
    ("SPY", ETF_Country.US, 20, [
        {'dividend_year': 2025, 'dividend_quarter': None, 'dividend_value': '1.761117', 'dividend_return_rate': '1.20', 'dividend_date': '2025-06-20'}, 
        {'dividend_year': 2025, 'dividend_quarter': None, 'dividend_value': '1.695528', 'dividend_return_rate': '1.27', 'dividend_date': '2025-03-21'}, 
        {'dividend_year': 2024, 'dividend_quarter': None, 'dividend_value': '1.965548', 'dividend_return_rate': '1.21', 'dividend_date': '2024-12-20'}, 
    ]),
])
def test_get_etf_dividend(etf_id, etf_country, years, expect_dividends):
    results = get("etf_dividend", etf_id=etf_id, etf_country=etf_country.value, years=years)

    if expect_dividends:
        for expect_dividend in expect_dividends:
            assert expect_dividend in results, f"Expected dividend {expect_dividend} not found in results {results}"
    else:
        assert not results, f"Expected no dividends for {etf_id} in {etf_country}, but got {results}"


@pytest.mark.parametrize("etf_id, etf_country, years", [
    ("0050", ETF_Country.TW, 10),
    ("0050", ETF_Country.TW, 1),
    ("SPY", ETF_Country.US, 1),
    ("SPY", ETF_Country.US, 20),
])
def test_get_etf_dividend_with_years(etf_id, etf_country, years):
    assert get("etf_dividend", etf_id=etf_id, etf_country=etf_country.value, years=years)
