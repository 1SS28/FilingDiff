"""Typed models used at FilingDiff module boundaries."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True, slots=True)
class Company:
    """A company supported by the first FilingDiff release."""

    ticker: str
    name: str
    cik: str


@dataclass(frozen=True, slots=True)
class Filing:
    """The SEC metadata needed to identify one quarterly filing."""

    ticker: str
    cik: str
    form: str
    accession_number: str
    filing_date: date
    report_period: date
    primary_document: str
    filing_url: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        result = asdict(self)
        result["filing_date"] = self.filing_date.isoformat()
        result["report_period"] = self.report_period.isoformat()
        return result

