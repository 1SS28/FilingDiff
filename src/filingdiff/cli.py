"""Command-line interface for milestone 1."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from filingdiff.errors import FilingDiffError
from filingdiff.filings import get_two_most_recent_10q
from filingdiff.sec_client import SecClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="filingdiff",
        description=(
            "Retrieve the two newest exact-form 10-Q filings for a supported ticker."
        ),
    )
    parser.add_argument("ticker", help="AAPL, MSFT, JPM, WMT, or TSLA")
    parser.add_argument(
        "--user-agent",
        default=os.environ.get("FILINGDIFF_SEC_USER_AGENT"),
        help=(
            "Declared SEC user agent with contact email. Defaults to the "
            "FILINGDIFF_SEC_USER_AGENT environment variable."
        ),
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".cache/sec"),
        help="Directory for byte-for-byte SEC JSON response caching.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.user_agent:
        parser.error(
            "provide --user-agent or set FILINGDIFF_SEC_USER_AGENT; include "
            "an application name and contact email"
        )

    try:
        client = SecClient(args.user_agent, cache_dir=args.cache_dir)
        filings = get_two_most_recent_10q(args.ticker, client)
    except FilingDiffError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps([filing.to_dict() for filing in filings], indent=2))
    return 0

