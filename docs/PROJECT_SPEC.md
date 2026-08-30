# FilingDiff Project Specification

## 1. Product summary

FilingDiff helps a user understand what changed between two comparable public
company SEC filings. Version one focuses on 10-Q filings and a fixed set of five
companies.

The finished project will eventually let a user:

1. Select a supported company.
2. Compare its two most recent 10-Q filings.
3. Review important additions and removals in selected narrative sections.
4. Inspect a transparent, descriptive filing-novelty score.
5. View price and trading volume around the filing event.
6. Explore research on whether filing novelty is associated with abnormal
   volume, returns, or volatility.

The product is educational and exploratory. It is not an investment-advice,
stock-prediction, or trading-strategy product.

## 2. Intended users

The primary audience is financially curious students and technically minded
resume reviewers. Financial terminology should be explained in plain language,
while methodology and intermediate calculations remain available for technical
inspection.

## 3. Supported companies

Version one supports:

- Apple (`AAPL`, CIK `0000320193`)
- Microsoft (`MSFT`, CIK `0000789019`)
- JPMorgan Chase (`JPM`, CIK `0000019617`)
- Walmart (`WMT`, CIK `0000104169`)
- Tesla (`TSLA`, CIK `0001318605`)

The fixed universe keeps parsing, data quality, and manual verification feasible
within the first release. Later versions may expand to approximately 20-50
companies.

## 4. Definitions

### 4.1 10-Q

A 10-Q is a quarterly report that a US public company files with the Securities
and Exchange Commission. It usually includes unaudited financial statements,
management's discussion of business performance, and updates to material risks.
Most companies file three 10-Qs per fiscal year; the annual 10-K covers the
remaining quarter and the full year.

### 4.2 CIK

The Central Index Key is the SEC's persistent numeric identifier for a filer.
Tickers can change and are not the SEC's primary identifier, so FilingDiff maps
each supported ticker to a known CIK.

### 4.3 Accession number

An accession number uniquely identifies an SEC submission. It is used to locate
the submission and construct links to its EDGAR archive directory.

### 4.4 Comparable filings

The default comparison uses the two most recent filings whose form value is
exactly `10-Q`. It does not include `10-Q/A` amendments. Reporting periods must
be displayed so users can see that consecutive 10-Qs cover different fiscal
quarters.

## 5. Product hierarchy

The eventual public application has three levels:

1. A guided summary of important changes.
2. A detailed view of additions and removals.
3. A research view connecting filing novelty with market behavior.

The design target is clean, credible, responsive, and research-focused. Extensive
animation, branding, authentication, subscriptions, and payments are out of
scope.

## 6. Proposed architecture

- Python ingestion and research pipeline
- Typed internal models
- SQLite for processed application data
- FastAPI read-only backend
- React and TypeScript frontend
- Reproducible Jupyter research notebook
- Automated tests in GitHub Actions
- Preprocessed public-demo data rather than arbitrary live processing

Only components required by the current milestone should be created.

## 7. Milestones

### Milestone 1: SEC filing-history discovery

Given a supported ticker, retrieve its SEC filing history and identify its two
most recent 10-Q filings.

#### Required input

- One ticker from `AAPL`, `MSFT`, `JPM`, `WMT`, or `TSLA`
- Lowercase input may be accepted and normalized to uppercase

#### Required output for each filing

- Normalized ticker
- Zero-padded CIK
- Accession number
- Filing date
- Report period
- Primary document filename
- Official SEC filing URL

#### Selection rules

- Use official SEC company-submissions data.
- Match form exactly to `10-Q`.
- Exclude `10-Q/A` and every other form.
- Select by filing recency using the SEC-provided filing metadata.
- Handle recent filing arrays and older submissions files when necessary; do not
  assume the recent array always contains two 10-Qs.
- Preserve a deterministic ordering, newest first.

#### Milestone 1 acceptance criteria

- All five supported tickers resolve to their intended CIKs.
- A representative SEC response yields the correct two most recent exact
  `10-Q` entries in newest-first order.
- Interleaved forms and `10-Q/A` entries are ignored.
- Lowercase supported input behaves like uppercase input.
- Unsupported tickers produce a clear error.
- Fewer than two qualifying filings produce a clear error.
- SEC request failures and invalid response shapes produce clear errors.
- Tests run without network access.
- No filing comparison, market analysis, or website code is introduced.

### Milestone 2: Section extraction and text normalization

Extract selected narrative sections, initially Management's Discussion and
Analysis and Risk Factors. Missing, unchanged, and failed extraction states must
remain distinguishable.

### Milestone 3: Filing differences and novelty score

Show paragraph- or sentence-level additions and removals and calculate a
descriptive score from transparent components. The score measures difference,
not whether a filing is good or bad.

### Milestone 4: Market-event research dataset

Align filing acceptance times with trading sessions and calculate abnormal
volume, market-adjusted returns, and volatility around filing events.

### Milestone 5: Reproducible analysis and report

Generate exploratory statistics, charts, sensitivity checks, and a concise
report without causal or predictive claims.

### Milestone 6: Public demonstration application

Expose preprocessed results through a small read-only API and a clean React
interface, then deploy a public demonstration.

## 8. Deferred features

- Positive/negative or bullish/bearish filing classification
- Machine-learning prediction
- Trading signals or portfolio simulation
- Arbitrary-company live processing
- 10-K, 8-K, or cross-form comparisons
- Authentication and user accounts
- Payments, subscriptions, and commercial workflows
- Large-scale company coverage

## 9. Project-level definition of done

The first public release requires a reproducible repository, validated SEC
comparisons for five companies, transparent novelty metrics, event-study data,
automated tests, a public demonstration website, and a concise research report.
Inconclusive research results are acceptable and must be reported honestly.

