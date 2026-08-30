from __future__ import annotations

from typing import Any

import pytest

from filingdiff.errors import InsufficientFilingsError, SecResponseError
from filingdiff.filings import get_two_most_recent_10q


class FakeSecClient:
    def __init__(
        self,
        main_payload: dict[str, Any],
        archives: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.main_payload = main_payload
        self.archives = archives or {}
        self.requested_ciks: list[str] = []
        self.requested_archives: list[str] = []

    def fetch_company_submissions(self, cik: str) -> dict[str, Any]:
        self.requested_ciks.append(cik)
        return self.main_payload

    def fetch_submission_archive(self, filename: str) -> dict[str, Any]:
        self.requested_archives.append(filename)
        return self.archives[filename]


def test_selects_newest_two_exact_10q_filings(load_fixture: Any) -> None:
    client = FakeSecClient(load_fixture("company_recent.json"))

    newest, previous = get_two_most_recent_10q("aapl", client)

    assert client.requested_ciks == ["0000320193"]
    assert client.requested_archives == []
    assert newest.accession_number == "0000320193-26-000101"
    assert previous.accession_number == "0000320193-26-000080"
    assert newest.form == previous.form == "10-Q"
    assert newest.report_period.isoformat() == "2026-06-27"
    assert newest.filing_url == (
        "https://www.sec.gov/Archives/edgar/data/320193/"
        "000032019326000101/aapl-20260627.htm"
    )


def test_uses_newest_archive_when_recent_history_has_only_one_10q(
    load_fixture: Any,
) -> None:
    main = load_fixture("company_archive_fallback.json")
    archive = load_fixture("company_archive_001.json")
    client = FakeSecClient(
        main,
        {"CIK0000789019-submissions-001.json": archive},
    )

    newest, previous = get_two_most_recent_10q("MSFT", client)

    assert client.requested_archives == ["CIK0000789019-submissions-001.json"]
    assert newest.accession_number == "0000789019-26-000050"
    assert previous.accession_number == "0000789019-25-000090"


def test_fewer_than_two_10q_filings_is_explicit() -> None:
    payload = {
        "filings": {
            "recent": {
                "accessionNumber": ["0000320193-26-000101"],
                "filingDate": ["2026-07-31"],
                "reportDate": ["2026-06-27"],
                "form": ["10-Q"],
                "primaryDocument": ["aapl-20260627.htm"],
            },
            "files": [],
        }
    }

    with pytest.raises(InsufficientFilingsError, match="fewer than two"):
        get_two_most_recent_10q("AAPL", FakeSecClient(payload))


def test_misaligned_sec_columns_are_rejected(load_fixture: Any) -> None:
    payload = load_fixture("company_recent.json")
    payload["filings"]["recent"]["reportDate"].pop()

    with pytest.raises(SecResponseError, match="misaligned"):
        get_two_most_recent_10q("AAPL", FakeSecClient(payload))


def test_missing_filings_object_is_rejected() -> None:
    with pytest.raises(SecResponseError, match="filings"):
        get_two_most_recent_10q("AAPL", FakeSecClient({}))


def test_malformed_primary_document_is_rejected(load_fixture: Any) -> None:
    payload = load_fixture("company_recent.json")
    payload["filings"]["recent"]["primaryDocument"][0] = "../filing.htm"

    with pytest.raises(SecResponseError, match="primary document"):
        get_two_most_recent_10q("AAPL", FakeSecClient(payload))


def test_results_are_sorted_and_duplicate_accessions_are_removed() -> None:
    payload = {
        "filings": {
            "recent": {
                "accessionNumber": [
                    "0000320193-25-000010",
                    "0000320193-26-000020",
                    "0000320193-26-000020",
                    "0000320193-26-000015",
                ],
                "filingDate": [
                    "2025-10-01",
                    "2026-07-01",
                    "2026-07-01",
                    "2026-04-01",
                ],
                "reportDate": [
                    "2025-09-01",
                    "2026-06-01",
                    "2026-06-01",
                    "2026-03-01",
                ],
                "form": ["10-Q", "10-Q", "10-Q", "10-Q"],
                "primaryDocument": ["old.htm", "new.htm", "new.htm", "middle.htm"],
            },
            "files": [],
        }
    }

    newest, previous = get_two_most_recent_10q("AAPL", FakeSecClient(payload))

    assert newest.accession_number == "0000320193-26-000020"
    assert previous.accession_number == "0000320193-26-000015"
