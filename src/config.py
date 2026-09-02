import pandas as pd

# Price data collection window
START_DATE = "2022-01-01"
END_DATE = "2025-12-31"

FUNDAMENTALS_LAG_DAYS = 90  
FUNDAMENTALS_MAX_STALENESS_MONTHS = 15

PRICE_SEARCH_THRESHOLD_DAYS = 5  # max trading days to search backward for a valid price
MOMENTUM_MIN_HISTORY_MONTHS = 12  # longest lookback needed (12-1 month momentum)

REBALANCE_FREQ = "QS" # quarterly
REBALANCE_START_DATE = pd.Timestamp(START_DATE) + pd.DateOffset(months = MOMENTUM_MIN_HISTORY_MONTHS)
REBALANCE_DATES = pd.date_range(start=REBALANCE_START_DATE, end=END_DATE, freq=REBALANCE_FREQ)

FLAT_US_TAX_RATE_FALLBACK = 0.21
FLAT_UK_TAX_RATE_FALLBACK = 0.25

MISSING_DATA_THRESHOLD_PCT = 0.65

BALANCE_SHEET_REQUIRED_FIELDS = [
    "Cash And Cash Equivalents",
    "Total Debt",
    "Current Debt",
    "Long Term Debt",
    "Total Assets",
    "Total Liabilities Net Minority Interest",
    "Total Equity Gross Minority Interest"
]

CASH_FLOW_REQUIRED_FIELDS = [
    "Operating Cash Flow",
    "Capital Expenditure",
    "Depreciation And Amortization",
    "Free Cash Flow",
    "Stock Based Compensation"
]

INCOME_STATEMENT_REQUIRED_FIELDS = [
    "Total Revenue",
    "Gross Profit",
    "Operating Income",
    "EBIT",
    "EBITDA",
    "Pretax Income",
    "Net Income",
    "Diluted EPS",
    "Interest Expense",
    "Tax Provision",
]

METADATA_REQUIRED_FIELDS = [
    "currency", 
    "sharesOutstanding", 
    "exchange", 
    "industry"
]

PRICES_SAVE_DIR = "../data/raw/prices"
FUNDAMENTALS_SAVE_DIR = "../data/raw/fundamentals"