"""Supported ticker-to-CIK mappings."""

from types import MappingProxyType
from typing import Final, Mapping

from filingdiff.errors import UnsupportedTickerError
from filingdiff.models import Company


_COMPANIES: Final[dict[str, Company]] = {
    "AAPL": Company("AAPL", "Apple Inc.", "0000320193"),
    "MSFT": Company("MSFT", "Microsoft Corporation", "0000789019"),
    "JPM": Company("JPM", "JPMorgan Chase & Co.", "0000019617"),
    "WMT": Company("WMT", "Walmart Inc.", "0000104169"),
    "TSLA": Company("TSLA", "Tesla, Inc.", "0001318605"),
}

SUPPORTED_COMPANIES: Mapping[str, Company] = MappingProxyType(_COMPANIES)


def get_company(ticker: str) -> Company:
    """Normalize a ticker and return its configured company.

    Raises:
        UnsupportedTickerError: If the ticker is not in the version-one set.
    """

    if not isinstance(ticker, str):
        raise UnsupportedTickerError("Ticker must be text.")

    normalized = ticker.strip().upper()
    try:
        return SUPPORTED_COMPANIES[normalized]
    except KeyError as exc:
        supported = ", ".join(SUPPORTED_COMPANIES)
        shown = normalized or "<empty>"
        raise UnsupportedTickerError(
            f"Unsupported ticker {shown!r}. Supported tickers: {supported}."
        ) from exc

