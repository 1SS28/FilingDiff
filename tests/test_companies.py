import pytest

from filingdiff.companies import SUPPORTED_COMPANIES, get_company
from filingdiff.errors import UnsupportedTickerError


def test_all_supported_tickers_have_expected_zero_padded_ciks() -> None:
    assert {ticker: company.cik for ticker, company in SUPPORTED_COMPANIES.items()} == {
        "AAPL": "0000320193",
        "MSFT": "0000789019",
        "JPM": "0000019617",
        "WMT": "0000104169",
        "TSLA": "0001318605",
    }


def test_ticker_is_trimmed_and_normalized() -> None:
    assert get_company("  aapl ").ticker == "AAPL"


@pytest.mark.parametrize("ticker", ["NVDA", "", "   "])
def test_unsupported_ticker_has_actionable_error(ticker: str) -> None:
    with pytest.raises(UnsupportedTickerError, match="Supported tickers"):
        get_company(ticker)


def test_non_text_ticker_is_rejected() -> None:
    with pytest.raises(UnsupportedTickerError, match="must be text"):
        get_company(123)  # type: ignore[arg-type]

