import os
import yfinance as yf
from src import config

def collect_prices(ticker: str, ticker_object: yf.Ticker) -> dict:
    """
    Pull daily price history for a single ticker and save it to CSV.

    Parameters:
        ticker: The ticker symbol (used for naming/logging).
        ticker_object: An initialized yf.Ticker instance for this ticker.

    Returns:
        A log entry dict describing the outcome (status, row count, date 
        range, missing values, error if any).
    """
    try:
        prices = ticker_object.history(start = config.START_DATE, end = config.END_DATE, auto_adjust = False)
        if prices.empty:
            log_entry = get_empty_log(ticker, "prices")
        else:
            prices.to_csv(f"{config.PRICES_SAVE_DIR}/{ticker}.csv")
            missing_values = prices.isna().sum().sum()
            total_values = prices.shape[0] * prices.shape[1]
            missing_values_pct = missing_values/total_values * 100
            log_entry = {
                "ticker": ticker, 
                "data_type": "prices",
                "status": "success",
                "rows": len(prices),
                "start_date": prices.index.min(),
                "end_date": prices.index.max(),
                "missing_values_pct": missing_values_pct,
                "missing_required_fields": None,
                "error": None
            }
    except Exception as e:
       log_entry = get_exception_log (ticker, e, "prices")
    return log_entry

def collect_fundamentals(
        ticker: str, 
        ticker_object: yf.Ticker, 
        fundamental_type: str, 
        required_fields: list[str], 
    ) -> dict:
    """
    Pull a fundamentals statement (balance sheet, cash flow, or income 
    statement) for a single ticker, filter to required fields, clean fully 
    empty periods, and save it to CSV.

    Parameters:
        ticker: The ticker symbol (used for naming/logging).
        ticker_object: An initialized yf.Ticker instance for this ticker.
        fundamental_type: One of "balance_sheet", "cash_flow", or 
            "income_statement" — determines which yfinance attribute is 
            pulled and where the file is saved.
        required_fields: List of line-item labels expected in the statement.

    Returns:
        A log entry dict describing the outcome (status, period count, 
        date range, missing values, missing required fields, error if any).
    """
    try:
        if fundamental_type == "balance_sheet":
            fundamental_statement = ticker_object.balance_sheet
        elif fundamental_type == "cash_flow":
            fundamental_statement = ticker_object.cash_flow
        else:
            fundamental_statement = ticker_object.income_stmt

        available_fields = [field for field in required_fields if field in fundamental_statement.index]
        filtered_statement = fundamental_statement.loc[available_fields]

        if filtered_statement.empty:
            log_entry = get_empty_log(ticker, fundamental_type)
        else:
            os.makedirs(f"{config.FUNDAMENTALS_SAVE_DIR}/{ticker}", exist_ok = True)
            cleaned_statement = filtered_statement.dropna(axis = 1, how = "all")
            cleaned_statement.to_csv(f"{config.FUNDAMENTALS_SAVE_DIR}/{ticker}/{fundamental_type}.csv")

            missing_values = cleaned_statement.isna().sum().sum()
            total_values = cleaned_statement.shape[0]*cleaned_statement.shape[1]
            missing_values_pct = missing_values/total_values * 100
            missing_fields = [field for field in required_fields if field not in cleaned_statement.index]

            log_entry = {
                "ticker": ticker, 
                "data_type": fundamental_type,
                "status": "success",
                "rows": cleaned_statement.shape[1],
                "start_date": cleaned_statement.columns.min(),
                "end_date": cleaned_statement.columns.max(),
                "missing_values_pct": missing_values_pct,
                "missing_required_fields": missing_fields,
                "error": None
            }

    except Exception as e:
        log_entry = get_exception_log (ticker, e, fundamental_type)

    return log_entry

def collect_metadata(ticker: str, ticker_object: yf.Ticker) -> tuple[dict, dict | None]:
    """
    Pull metadata fields (e.g. currency, shares outstanding, exchange, 
    industry) for a single ticker from yfinance's info dictionary.

    Parameters:
        ticker: The ticker symbol (used for naming/logging).
        ticker_object: An initialized yf.Ticker instance for this ticker.

    Returns:
        A tuple of (log_entry, metadata_entry). log_entry is always a dict 
        describing the outcome. metadata_entry is a dict of the collected 
        field values (with "ticker" as the first key) if at least one field 
        was found, otherwise None.
    """
    try:
        info = ticker_object.info

        field_values = {field: info.get(field) for field in config.METADATA_REQUIRED_FIELDS}
        missing_fields = [field for field, value in field_values.items() if value is None] #TO DO: CHECK

        if len(missing_fields) == len(config.METADATA_REQUIRED_FIELDS):
            status = "fail"
            metadata_entry = None
        else:
            status = "success"
            metadata_entry = dict(zip(config.METADATA_REQUIRED_FIELDS, field_values))
            metadata_entry = {"ticker": ticker, **metadata_entry}

        log_entry = {
            "ticker": ticker, 
            "data_type": "metadata",
            "status": status,
            "rows": len(config.METADATA_REQUIRED_FIELDS) - len(missing_fields),
            "start_date": None,
            "end_date": None,
            "missing_values_pct": None,
            "missing_required_fields": missing_fields,
            "error": None
        }
    except Exception as e:
        log_entry = get_exception_log (ticker, e, "metadata")

    return log_entry, metadata_entry

def collect_all_data(ticker: str) -> tuple[list[dict], dict | None]:
    """
    Run the full data collection process for a single ticker: prices, 
    balance sheet, cash flow, income statement, and metadata.

    Parameters:
        ticker: The ticker symbol to collect data for.

    Returns:
        A tuple of (log_entries, metadata_entry). log_entries is a list of 
        5 log entry dicts (prices, balance sheet, cash flow, income 
        statement, metadata). metadata_entry is a dict of this ticker's 
        metadata if available, otherwise None.
    """

    ticker_logs = []
    ticker_object = yf.Ticker(ticker)

    price_log = collect_prices(ticker, ticker_object)
    balance_sheet_log = collect_fundamentals(ticker, ticker_object, "balance_sheet", config.BALANCE_SHEET_REQUIRED_FIELDS)
    cash_flow_log = collect_fundamentals(ticker, ticker_object, "cash_flow", config.CASH_FLOW_REQUIRED_FIELDS)
    income_statement_log = collect_fundamentals(ticker, ticker_object, "income_statement", config.INCOME_STATEMENT_REQUIRED_FIELDS)
    metadata_log, metadata_entry = collect_metadata(ticker, ticker_object)

    ticker_logs.extend([price_log, balance_sheet_log, cash_flow_log, income_statement_log, metadata_log])

    return ticker_logs, metadata_entry

def get_exception_log(ticker: str,e: Exception, data_type: str) -> dict:
    return {
        "ticker": ticker, 
        "data_type": data_type,
        "status": "fail",
        "rows": 0,
        "start_date": None,
        "end_date": None,
        "missing_values_pct": None,
        "missing_required_fields": None,
        "error": str(e)
    }

def get_empty_log(ticker: str, data_type: str) -> dict:
    return {
        "ticker": ticker, 
        "data_type": data_type,
        "status": "fail",
        "rows": 0,
        "start_date": None,
        "end_date": None,
        "missing_values_pct": None,
        "missing_required_fields": None,
        "error": "empty data returned"
    }
        