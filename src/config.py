# Date range for price collection.
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
# assumed.

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