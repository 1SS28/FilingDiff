# FilingDiff Research Plan

## 1. Research question

Are larger or more unusual changes between a company's consecutive 10-Q filings
associated with unusual trading volume, market-adjusted returns, or volatility
around the later filing's publication?

This is an exploratory association question. The study does not test whether
FilingDiff predicts stocks, causes market movements, or creates a profitable
trading strategy.

## 2. Study universe

The initial sample contains Apple, Microsoft, JPMorgan Chase, Walmart, and Tesla.
The target history is approximately five years.

Companies generally file three 10-Qs per year, so five years provides roughly 15
filings and 14 consecutive comparisons per company before exclusions. The total
sample is expected to be approximately 70 filing events, not 100. Actual sample
size will depend on data quality and filing availability.

## 3. Unit of observation

One observation is a pair of consecutive exact-form `10-Q` filings for the same
company. The earlier filing supplies the baseline text. The later filing supplies
the changed text and event timestamp.

The public demo defaults to the latest pair. The research dataset uses all valid
consecutive pairs in the study period.

## 4. Filing inputs

- Filing source: official SEC EDGAR data
- Form: exact `10-Q` only
- Initial sections: Management's Discussion and Analysis and Risk Factors
- Amendments: exclude `10-Q/A` in the initial study
- Primary identifier: SEC CIK
- Filing identifier: accession number
- Event timestamp: SEC acceptance timestamp when available

Raw filing inputs and metadata should be cached so analysis can be reproduced.
Extraction failures and missing sections must be recorded explicitly.

## 5. Filing-novelty measure

Novelty is descriptive: a high value means that the later filing differs more
from the earlier filing. It does not mean that the filing is positive, negative,
important to investors, or likely to move the stock in a particular direction.

The initial score will combine interpretable components such as:

- Changed-text share: how much text was added or removed relative to section
  length.
- New-phrase share: how much meaningful new language appears.
- Salient-change share: how much changed text contains values, percentages,
  dates, or documented finance and risk terms.

Every component, transformation, and weight must be visible. Initial weights are
design choices and must be tested with alternative reasonable weights.

The exact score formula is deferred until the filing extraction and difference
representations have been validated.

## 6. Market outcomes

### 6.1 Primary outcome: abnormal trading volume

Abnormal volume measures whether trading activity around the filing is unusual
relative to the stock's own recent activity. The initial baseline is the prior
20 trading days. A volume ratio or log-volume ratio will make companies with
different raw trading volumes easier to compare.

Volume is primary because a disclosure may attract attention even when investors
disagree about whether its information is favorable or unfavorable.

### 6.2 Secondary outcome: market-adjusted return

The simple initial calculation is:

`company return - broad-market benchmark return`

A benchmark such as SPY removes part of a market-wide move. This is not a full
asset-pricing model and should be described as a simple market adjustment.

### 6.3 Secondary outcome: volatility

Initial measures should remain interpretable:

- Absolute daily return for a one-day response
- Standard deviation of daily returns for multi-day windows

Advanced volatility models are outside version one.

## 7. Event timing and windows

Use the SEC acceptance timestamp when possible.

- A filing accepted before or during the relevant trading session uses that
  trading date as event day zero.
- A filing accepted after market close uses the next trading day as event day
  zero.
- Weekend and market-holiday filings roll forward to the next trading day.

The primary response window is event day zero through the next trading day.
Wider windows, such as one day before through three or five days after, are
sensitivity checks.

The exact market calendar, time-zone conversion, and market-close rule must be
documented before calculations are implemented.

## 8. Initial analysis

Use simple, interpretable methods:

1. Describe the filing and event sample, including exclusions.
2. Plot novelty and each score component by company and over time.
3. Plot novelty against abnormal volume, returns, and volatility.
4. Calculate Spearman rank correlations.
5. Fit simple exploratory regressions where justified.
6. Report confidence intervals and sample sizes.
7. Repeat results across reasonable event windows and novelty weights.
8. Show company-level results so one volatile company cannot silently dominate.

Machine learning is not appropriate for the initial small sample.

## 9. Interpretation rules

Allowed language includes:

- "In this sample, higher novelty was associated with..."
- "The estimate was imprecise."
- "The result was sensitive to the event window."
- "No reliable relationship was detected."

Avoid language such as:

- "Filing novelty causes..."
- "The score predicts..."
- "Investors can profit by..."
- "A high score means the stock will..."

## 10. Main limitations

- Five companies are not representative of the full public market.
- Approximately 70 events provide limited statistical power.
- Multiple observations from one company are not independent in the ordinary
  sense.
- Consecutive 10-Qs cover different fiscal quarters, so seasonality may affect
  language and market outcomes.
- SEC HTML structure and section presentation vary across companies and years.
- Market movements around a filing may be driven by earnings calls, guidance,
  macroeconomic news, or unrelated company events.
- Novelty-score weights include researcher judgment.
- A simple benchmark does not remove every source of expected return.

These are study limitations to discuss, not reasons to conceal inconvenient
results.

## 11. Reproducibility requirements

- Preserve raw-source identifiers and retrieval metadata.
- Keep raw, normalized, and analysis-ready data conceptually separate.
- Do not perform live network calls in automated tests.
- Generate analysis tables and charts from code.
- State all exclusions with machine-readable reasons.
- Record package versions and documented execution commands.
- Ensure the short report agrees with notebook-generated results.

## 12. Research completion criteria

The research component is complete when the analysis can be reproduced from
documented inputs, every metric is defined, sample sizes and exclusions are
visible, sensitivity checks are included, and the conclusions remain accurate
even if the primary relationship is weak or inconclusive.

