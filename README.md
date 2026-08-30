# FilingDiff

FilingDiff is a research-first project for understanding changes between public
company SEC filings. This repository currently contains **milestone 1 only**:
given one of five supported tickers, retrieve its official SEC filing history
and report its two newest exact-form 10-Q filings.

It does not yet download filing documents, compare filing text, retrieve market
data, calculate research statistics, expose an API, or provide a website.

## What the command returns

For each filing, FilingDiff returns:

- ticker and zero-padded SEC CIK
- accession number (the SEC's unique submission identifier)
- filing date
- report period (the quarter described by the filing)
- primary document filename
- official SEC document URL

`10-Q/A` amendments and other form types are excluded.

## Setup

From PowerShell in this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Run the offline tests:

```powershell
python -m pytest -q
```

## Perform a live SEC lookup

The SEC requires automated clients to identify themselves with an application
name and contact information. Supply this at runtime; do not commit your email
address:

```powershell
$env:FILINGDIFF_SEC_USER_AGENT = "FilingDiff YourName you@example.com"
filingdiff AAPL
```

Alternatively:

```powershell
python -m filingdiff MSFT --user-agent "FilingDiff YourName you@example.com"
```

Responses are cached byte-for-byte in `.cache/sec/`. Delete that cache only when
you intentionally want fresh metadata. The cache is excluded from Git.

Supported tickers are `AAPL`, `MSFT`, `JPM`, `WMT`, and `TSLA`. Lowercase input
is accepted.

## Data source and access behavior

Filing metadata comes from the official SEC submissions endpoint:

```text
https://data.sec.gov/submissions/CIK##########.json
```

The client sends a declared `User-Agent`, requests JSON, caches raw responses,
and spaces uncached requests so it remains well below the SEC's published limit
of 10 requests per second. Tests use fixtures and injected HTTP behavior; they
never call the live SEC service.

## Repository layout

```text
src/filingdiff/    application code
tests/             automated tests and sample SEC responses
docs/              product specification and research plan
```
