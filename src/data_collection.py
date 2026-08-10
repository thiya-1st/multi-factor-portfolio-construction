import os
import yfinance as yf

def collect_prices(
        ticker: str, 
        ticker_object: yf.Ticker, 
        start_date: str, 
        end_date: str, 
        save_dir: str
    ) -> dict:
    """
    Pull daily price history for a single ticker and save it to CSV.

    Parameters:
        ticker: The ticker symbol (used for naming/logging).
        ticker_object: An initialized yf.Ticker instance for this ticker.
        start_date: Start date for the price history, e.g. "2022-01-01".
        end_date: End date for the price history, e.g. "2025-12-31".
        save_dir: Directory to save the resulting CSV into.

    Returns:
        A log entry dict describing the outcome (status, row count, date 
        range, missing values, error if any).
    """
    try:
        prices = ticker_object.history(start = start_date, end = end_date, auto_adjust = False)
        if prices.empty:
            log_entry = {
                "ticker": ticker, 
                "data_type": "prices",
                "status": "fail",
                "rows": 0,
                "start_date": None,
                "end_date": None,
                "missing_values": None,
                "missing_required_fields": None,
                "error": "empty data returned"
            }
        else:
            prices.to_csv(f"{save_dir}/{ticker}.csv")
            missing_values = prices.isna().sum().sum()
            log_entry = {
                "ticker": ticker, 
                "data_type": "prices",
                "status": "success",
                "rows": len(prices),
                "start_date": prices.index.min(),
                "end_date": prices.index.max(),
                "missing_values": missing_values,
                "missing_required_fields": None,
                "error": None
            }
    except Exception as e:
        log_entry = {
            "ticker": ticker, 
            "data_type": "prices",
            "status": "fail",
            "rows": 0,
            "start_date": None,
            "end_date": None,
            "missing_values": None,
            "missing_required_fields": None,
            "error": str(e)
        }
    return log_entry

def collect_fundamentals(
        ticker: str, 
        ticker_object: yf.Ticker, 
        fundamental_type: str, 
        required_fields: list[str], 
        save_dir: str
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
        save_dir: Base directory to save the resulting CSV into (a 
            per-ticker subfolder is created inside it).

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
            log_entry = {
                "ticker": ticker, 
                "data_type": fundamental_type,
                "status": "fail",
                "rows": 0,
                "start_date": None,
                "end_date": None,
                "missing_values": None,
                "missing_required_fields": None,
                "error": "empty data returned"
            }
        else:
            os.makedirs(f"{save_dir}/{ticker}", exist_ok = True)
            cleaned_statement = filtered_statement.dropna(axis = 1, how = "all")
            cleaned_statement.to_csv(f"{save_dir}/{ticker}/{fundamental_type}.csv")

            missing_values = cleaned_statement.isna().sum().sum()
            missing_fields = [field for field in required_fields if field not in cleaned_statement.index]

            log_entry = {
                "ticker": ticker, 
                "data_type": fundamental_type,
                "status": "success",
                "rows": cleaned_statement.shape[1],
                "start_date": cleaned_statement.columns.min(),
                "end_date": cleaned_statement.columns.max(),
                "missing_values": missing_values,
                "missing_required_fields": missing_fields,
                "error": None
            }

    except Exception as e:
        log_entry = {
            "ticker": ticker, 
            "data_type": fundamental_type,
            "status": "fail",
            "rows": 0,
            "start_date": None,
            "end_date": None,
            "missing_values": None,
            "missing_required_fields": None,
            "error": str(e)
        }

    return log_entry

def collect_metadata(
        ticker: str, 
        ticker_object: yf.Ticker, 
        required_fields: list[str]
    ) -> tuple[dict, dict | None]:
    """
    Pull metadata fields (e.g. currency, shares outstanding, exchange, 
    industry) for a single ticker from yfinance's info dictionary.

    Parameters:
        ticker: The ticker symbol (used for naming/logging).
        ticker_object: An initialized yf.Ticker instance for this ticker.
        required_fields: List of keys to look up in ticker_object.info.

    Returns:
        A tuple of (log_entry, metadata_entry). log_entry is always a dict 
        describing the outcome. metadata_entry is a dict of the collected 
        field values (with "ticker" as the first key) if at least one field 
        was found, otherwise None.
    """
    metadata_entry = None
    field_values = []

    try:
        info = ticker_object.info
        for field in required_fields:
            field_values.append(info.get(field))

        missing_fields = [required_fields[i] for i in range(len(required_fields)) if field_values[i] is None]

        if len(missing_fields) == len(required_fields):
            status = "fail"
        else:
            status = "success"
            metadata_entry = dict(zip(required_fields, field_values))
            metadata_entry = {"ticker": ticker, **metadata_entry}

        log_entry = {
            "ticker": ticker, 
            "data_type": "metadata",
            "status": status,
            "rows": None,
            "start_date": None,
            "end_date": None,
            "missing_values": None,
            "missing_required_fields": missing_fields,
            "error": None
        }
    except Exception as e:
        log_entry = {
            "ticker": ticker, 
            "data_type": "metadata",
            "status": "fail",
            "rows": None,
            "start_date": None,
            "end_date": None,
            "missing_values": None,
            "missing_required_fields": None,
            "error": str(e)
        }

    return log_entry, metadata_entry

def collect_all_data(
        ticker: str,
        start_date: str,
        end_date: str,
        balance_sheet_fields: list[str],
        cash_flow_fields: list[str],
        income_statement_fields: list[str],
        metadata_fields: list[str],
        prices_save_dir: str,
        fundamentals_save_dir: str
    ) -> tuple[list[dict], dict | None]:
    """
    Run the full data collection process for a single ticker: prices, 
    balance sheet, cash flow, income statement, and metadata.

    Parameters:
        ticker: The ticker symbol to collect data for.
        start_date: Start date for price history.
        end_date: End date for price history.
        balance_sheet_fields: Required line items for the balance sheet.
        cash_flow_fields: Required line items for the cash flow statement.
        income_statement_fields: Required line items for the income statement.
        metadata_fields: Required keys to look up in yfinance's info dict.
        prices_save_dir: Directory to save price CSVs into.
        fundamentals_save_dir: Base directory to save fundamentals CSVs into.

    Returns:
        A tuple of (log_entries, metadata_entry). log_entries is a list of 
        5 log entry dicts (prices, balance sheet, cash flow, income 
        statement, metadata). metadata_entry is a dict of this ticker's 
        metadata if available, otherwise None.
    """

    ticker_logs = []
    ticker_object = yf.Ticker(ticker)

    price_log = collect_prices(ticker, ticker_object, start_date, end_date, prices_save_dir)
    ticker_logs.append(price_log)

    balance_sheet_log = collect_fundamentals(ticker, ticker_object, "balance_sheet", balance_sheet_fields, fundamentals_save_dir)
    ticker_logs.append(balance_sheet_log)

    cash_flow_log = collect_fundamentals(ticker, ticker_object, "cash_flow", cash_flow_fields, fundamentals_save_dir)
    ticker_logs.append(cash_flow_log)

    income_statement_log = collect_fundamentals(ticker, ticker_object, "income_statement", income_statement_fields, fundamentals_save_dir)
    ticker_logs.append(income_statement_log)

    metadata_log, metadata_entry = collect_metadata(ticker, ticker_object, metadata_fields)
    ticker_logs.append(metadata_log)
    
    return ticker_logs, metadata_entry