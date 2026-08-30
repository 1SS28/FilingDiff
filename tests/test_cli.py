from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from filingdiff import cli
from filingdiff.models import Filing


def _filing(accession: str, filing_date: date) -> Filing:
    return Filing(
        ticker="AAPL",
        cik="0000320193",
        form="10-Q",
        accession_number=accession,
        filing_date=filing_date,
        report_period=date(2026, 3, 28),
        primary_document="aapl.htm",
        filing_url="https://www.sec.gov/example",
    )


def test_cli_prints_json_without_network(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    expected = (
        _filing("0000320193-26-000101", date(2026, 7, 31)),
        _filing("0000320193-26-000080", date(2026, 5, 1)),
    )
    monkeypatch.setattr(cli, "SecClient", lambda *args, **kwargs: object())
    monkeypatch.setattr(cli, "get_two_most_recent_10q", lambda ticker, client: expected)

    exit_code = cli.main(
        ["aapl", "--user-agent", "FilingDiff Test test@example.com"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"accession_number": "0000320193-26-000101"' in captured.out
    assert captured.err == ""


def test_cli_requires_declared_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FILINGDIFF_SEC_USER_AGENT", raising=False)
    with pytest.raises(SystemExit) as error:
        cli.main(["AAPL"])
    assert error.value.code == 2


def test_cli_runs_end_to_end_from_raw_cache(
    tmp_path: Path, load_fixture: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = load_fixture("company_recent.json")
    (tmp_path / "CIK0000320193.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )

    exit_code = cli.main(
        [
            "AAPL",
            "--user-agent",
            "FilingDiff Test test@example.com",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert exit_code == 0
    assert [item["accession_number"] for item in result] == [
        "0000320193-26-000101",
        "0000320193-26-000080",
    ]
    assert captured.err == ""
