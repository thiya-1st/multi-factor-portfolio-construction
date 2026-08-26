# Multi Factor Portfolio Construction
A systematic equity research project that ranks UK and US companies using quality, value, momentum, growth and risk factors, then compares equal-weight and mathematically optimised portfolios through historical backtesting.
## Overview
Financial analysis exists both quantitatively and qualitatively, with analysts assimilating both into stock evaluation to select high-potential stocks for a portfolio. There exists significant proxies for quantitative investors to evaluate business economics, whereas fundamental investors often assess moats qualitatively, using intuition rather than statistics to determine business quality. Thus, these investors often miss hidden value levers such as switching costs, embedded workflows and pricing power into analysis.

This model aims to create quantitative proxies for these hidden value levers  that fundamental investors evaluate by establishing several factor scores to rank eligible US/UK equities, creating a portfolio with the highest ranked securities and comparing different factor methods and portfolio weightings.

This project tests whether the factor model can predict future performance, whether the matrix factor nature performs better than uni-dimensional strategies, and whether portfolio optimisation adds value over equal weighting.

## Research Questions

The primary question: **“Whether financial proxies for competitive moats, switching costs, pricing power, and reinvestment efficiency, can identify UK and European businesses that the market misprices relative to conventional quality and value metrics, and does this mispricing resolve into excess risk-adjusted returns?"**

With further analysis into: **"Whether mathematically optimised portfolios can improve on this signal, or does a simple equal-weight portfolio of top-ranked stocks perform better once estimation error and implementation costs are included?"**

## Investment Philosophy 
The primary investment philosophy that this portfolio construction project relies on is **"Value Discovery and Unlayering"**. This investment philosophy can be characterised by proxy selection through five distinct factors: quality, value, momentum, growth and risk.

This project builds financial proxies that get closer to the source of financial durability, and tests whether the market pays for it with a delay, creating a value-like entry point into structurally advantaged businesses. Ultimately, it brings light to business factors that are not inherently accounted for within natural means of valuation and presents their true transfer to financial returns.

## Universe Construction
The project universe consists of around 120 UK/US equities with an approximate 40 UK and 60 US equities split. The universe consists of 10 mega cap, 55 large cap, 35 mid cap and 27 small cap. The highest concentration of firms are within technology, consumer staples and information services sectors at around 17 respectively, with no category existing <20%.

Sectors excluded from the universe are: Banks, insurers, highly illiquid securities, companies with inadequate fundamentals and trusts mainly due to their exceedingly different capital structures potentially creating dissonance with factor selection. Comapnies are not assummed to be high quality due to their inclusion - variation in quality is intentionally maintained to ensure the factor model selects securities efficiently.


## Tech Stack
- Language: Python
- Data manipulation: pandas, NumPy
- Market/Fundamental Data: yfinance
<!-- - Statistics: SciPy / statsmodels -->
- Optimisation: 
<!-- - Visualisation: Matplotlib -->
- Research: Jupyter Notebook
- Version Control: Git / GitHub

## Data Sources and Data Audit
### Data Audit
Before constructing the full pipeline, multiple data sources were tested on a sample of UK equities to evaluate coverage, historical depth and point-in-time data availability.

y finance was selected as the primary data source due to the availability and range of equity data. However, limitations such as a lack of filling dates and history depth limited to 5 years were faced - thus the decision to complete the project in phases was decided.

### Decision

yfinance selected for Phase 1 - Modular architecture allows the data source to be replaced later.

## Methodology

### Data Collection

### Data Cleaning

### Factor Construction

### Composite Ranking

### Portfolio Formation

### Backtesting 






- title

**sigma**

`yfinance`

```text
goodboy
```


<!-- # Date range for price collection.
# Originally set to 2021-01-01, but shrunk to 2022-01-01 after the collection log 
# showed most companies' fundamentals only reliably cover ~4 years via yfinance. 
# The price window was aligned to match, so every period with price data also has 
# corresponding fundamentals to score against.

START_DATE = "2022-01-01"
END_DATE = "2025-12-31"

# Required fields for each fundamental statement type (cash flow, balance sheet, 
# income statement), a fixed list of required line items is defined below. These 
# are the specific metrics needed for factor scoring later. Not every company 
# reports every field — availability is checked and logged per company rather than 
# assumed. -->