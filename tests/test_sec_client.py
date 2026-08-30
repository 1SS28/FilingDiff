from __future__ import annotations

from pathlib import Path
from urllib.error import URLError
from urllib.request import Request

import pytest

from filingdiff.errors import ConfigurationError, SecRequestError, SecResponseError
from filingdiff.sec_client import SecClient


def test_request_declares_user_agent_and_caches_raw_response(tmp_path: Path) -> None:
    calls: list[tuple[Request, float]] = []
    raw = b'{"filings":{"recent":{},"files":[]}}'

    def fetcher(request: Request, timeout: float) -> bytes:
        calls.append((request, timeout))
        return raw

    client = SecClient(
        "FilingDiff Test test@example.com",
        cache_dir=tmp_path,
        timeout=7,
        min_request_interval=0,
        fetcher=fetcher,
    )

    first = client.fetch_company_submissions("0000320193")
    second = client.fetch_company_submissions("0000320193")

    assert first == second
    assert len(calls) == 1
    request, timeout = calls[0]
    assert request.full_url.endswith("/CIK0000320193.json")
    assert request.get_header("User-agent") == "FilingDiff Test test@example.com"
    assert request.get_header("Accept") == "application/json"
    assert timeout == 7
    assert (tmp_path / "CIK0000320193.json").read_bytes() == raw


@pytest.mark.parametrize("user_agent", ["", "FilingDiff", "no-email-contact"])
def test_user_agent_requires_contact_email(user_agent: str, tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="contact email"):
        SecClient(user_agent, cache_dir=tmp_path)


def test_invalid_json_is_reported(tmp_path: Path) -> None:
    client = SecClient(
        "FilingDiff Test test@example.com",
        cache_dir=tmp_path,
        min_request_interval=0,
        fetcher=lambda request, timeout: b"not-json",
    )

    with pytest.raises(SecResponseError, match="not valid JSON"):
        client.fetch_company_submissions("0000320193")


def test_network_failure_is_reported(tmp_path: Path) -> None:
    def failing_fetcher(request: Request, timeout: float) -> bytes:
        raise URLError("offline")

    client = SecClient(
        "FilingDiff Test test@example.com",
        cache_dir=tmp_path,
        min_request_interval=0,
        fetcher=failing_fetcher,
    )

    with pytest.raises(SecRequestError, match="Could not retrieve SEC data"):
        client.fetch_company_submissions("0000320193")


def test_cik_must_be_zero_padded(tmp_path: Path) -> None:
    client = SecClient(
        "FilingDiff Test test@example.com",
        cache_dir=tmp_path,
        fetcher=lambda request, timeout: b"{}",
    )

    with pytest.raises(ConfigurationError, match="exactly 10 digits"):
        client.fetch_company_submissions("320193")


def test_archive_filename_cannot_escape_cache_or_sec_path(tmp_path: Path) -> None:
    client = SecClient(
        "FilingDiff Test test@example.com",
        cache_dir=tmp_path,
        fetcher=lambda request, timeout: b"{}",
    )

    with pytest.raises(SecResponseError, match="unsafe"):
        client.fetch_submission_archive("../private.json")
