import pandas as pd

# Price data collection window
START_DATE = "2022-01-01"
END_DATE = "2025-12-31"

REBALANCE_FREQ = "QS" # quarterly
MOMENTUM_MIN_HISTORY_MONTHS = 12  # longest lookback needed (12-1 month momentum)

REBALANCE_START_DATE = pd.Timestamp(START_DATE) + pd.DateOffset(months = MOMENTUM_MIN_HISTORY_MONTHS)
REBALANCE_DATES = pd.date_range(start=REBALANCE_START_DATE, end=END_DATE, freq=REBALANCE_FREQ)

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