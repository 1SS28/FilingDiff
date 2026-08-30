"""Convert SEC columnar metadata into the newest comparable filings."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import PurePosixPath
from typing import Any, Protocol
from urllib.parse import quote

from filingdiff.companies import get_company
from filingdiff.errors import InsufficientFilingsError, SecResponseError
from filingdiff.models import Company, Filing


_REQUIRED_COLUMNS = (
    "accessionNumber",
    "filingDate",
    "reportDate",
    "form",
    "primaryDocument",
)
_ACCESSION_PATTERN = re.compile(r"^\d{10}-\d{2}-\d{6}$")


class SubmissionClient(Protocol):
    """The SEC retrieval operations required by the selection logic."""

    def fetch_company_submissions(self, cik: str) -> dict[str, Any]: ...

    def fetch_submission_archive(self, filename: str) -> dict[str, Any]: ...


def get_two_most_recent_10q(
    ticker: str, client: SubmissionClient
) -> tuple[Filing, Filing]:
    """Retrieve and select the newest two exact-form 10-Q filings."""

    company = get_company(ticker)
    payload = client.fetch_company_submissions(company.cik)
    filings_object = _require_mapping(payload.get("filings"), "filings")
    recent = _require_mapping(filings_object.get("recent"), "filings.recent")

    candidates = _parse_columnar_filings(recent, company, "filings.recent")
    if len(_deduplicate(candidates)) < 2:
        archive_entries = filings_object.get("files", [])
        if not isinstance(archive_entries, list):
            raise SecResponseError("SEC field 'filings.files' must be a list.")

        for filename in _ordered_archive_names(archive_entries):
            archive_payload = client.fetch_submission_archive(filename)
            candidates.extend(
                _parse_columnar_filings(archive_payload, company, filename)
            )
            if len(_deduplicate(candidates)) >= 2:
                break

    selected = sorted(
        _deduplicate(candidates),
        key=lambda filing: (filing.filing_date, filing.accession_number),
        reverse=True,
    )
    if len(selected) < 2:
        raise InsufficientFilingsError(
            f"{company.ticker} has fewer than two exact-form 10-Q filings in "
            "the SEC submissions history."
        )
    return selected[0], selected[1]


def _parse_columnar_filings(
    table: Mapping[str, Any], company: Company, source_name: str
) -> list[Filing]:
    columns: dict[str, list[Any]] = {}
    for column_name in _REQUIRED_COLUMNS:
        value = table.get(column_name)
        if not isinstance(value, list):
            raise SecResponseError(
                f"SEC field {source_name}.{column_name!s} must be a list."
            )
        columns[column_name] = value

    row_count = len(columns["form"])
    unequal = [name for name, values in columns.items() if len(values) != row_count]
    if unequal:
        raise SecResponseError(
            f"SEC response {source_name!r} has misaligned filing columns: "
            f"{', '.join(unequal)}."
        )

    filings: list[Filing] = []
    for index in range(row_count):
        if columns["form"][index] != "10-Q":
            continue
        filings.append(
            _build_filing(
                company=company,
                accession_number=_require_text(
                    columns["accessionNumber"][index],
                    f"{source_name}.accessionNumber[{index}]",
                ),
                filing_date_text=_require_text(
                    columns["filingDate"][index],
                    f"{source_name}.filingDate[{index}]",
                ),
                report_period_text=_require_text(
                    columns["reportDate"][index],
                    f"{source_name}.reportDate[{index}]",
                ),
                primary_document=_require_text(
                    columns["primaryDocument"][index],
                    f"{source_name}.primaryDocument[{index}]",
                ),
            )
        )
    return filings


def _build_filing(
    *,
    company: Company,
    accession_number: str,
    filing_date_text: str,
    report_period_text: str,
    primary_document: str,
) -> Filing:
    if not _ACCESSION_PATTERN.fullmatch(accession_number):
        raise SecResponseError(f"Invalid SEC accession number {accession_number!r}.")
    if (
        PurePosixPath(primary_document).name != primary_document
        or "\\" in primary_document
        or primary_document in {".", ".."}
    ):
        raise SecResponseError(f"Invalid SEC primary document {primary_document!r}.")

    try:
        filing_date = date.fromisoformat(filing_date_text)
        report_period = date.fromisoformat(report_period_text)
    except ValueError as exc:
        raise SecResponseError(
            f"Invalid SEC date for accession {accession_number!r}."
        ) from exc

    cik_without_leading_zeroes = str(int(company.cik))
    accession_without_dashes = accession_number.replace("-", "")
    encoded_document = quote(primary_document, safe="._-")
    filing_url = (
        "https://www.sec.gov/Archives/edgar/data/"
        f"{cik_without_leading_zeroes}/{accession_without_dashes}/{encoded_document}"
    )
    return Filing(
        ticker=company.ticker,
        cik=company.cik,
        form="10-Q",
        accession_number=accession_number,
        filing_date=filing_date,
        report_period=report_period,
        primary_document=primary_document,
        filing_url=filing_url,
    )


def _ordered_archive_names(entries: Sequence[Any]) -> list[str]:
    normalized: list[tuple[str, str]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise SecResponseError(f"SEC field filings.files[{index}] must be an object.")
        name = _require_text(entry.get("name"), f"filings.files[{index}].name")
        filing_to = entry.get("filingTo", "")
        if filing_to is not None and not isinstance(filing_to, str):
            raise SecResponseError(
                f"SEC field filings.files[{index}].filingTo must be text."
            )
        normalized.append((filing_to or "", name))
    normalized.sort(reverse=True)
    return [name for _, name in normalized]


def _deduplicate(filings: Sequence[Filing]) -> list[Filing]:
    by_accession: dict[str, Filing] = {}
    for filing in filings:
        by_accession.setdefault(filing.accession_number, filing)
    return list(by_accession.values())


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SecResponseError(f"SEC field {field_name!r} must be an object.")
    return value


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SecResponseError(f"SEC field {field_name!r} must be non-empty text.")
    return value.strip()
