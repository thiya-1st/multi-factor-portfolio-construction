from src import config

import pandas as pd

def load_file(ticker, missing_files, file_name, file_path):
    try:
        return pd.read_csv(file_path, index_col = 0)
    except FileNotFoundError:
        missing_files.append({"ticker": ticker, "missing_file": file_name})
        return None

def get_latest_fundamental_period(fundamental_statement, date):
    period_dates = pd.Series(pd.to_datetime(fundamental_statement.columns), index = fundamental_statement.columns)

    known_dates = (period_dates + pd.Timedelta(days = config.FUNDAMENTALS_LAG_DAYS)) <= date
    not_stale_dates = (period_dates + pd.DateOffset(months = config.FUNDAMENTALS_MAX_STALENESS_MONTHS)) >= date

    valid_dates = period_dates[known_dates & not_stale_dates]

    if valid_dates.empty:
        return None
    
    return valid_dates.idxmax()

def get_latest_price_date(prices, date):
    pass

def has_missing_data(metrics):
    return any(pd.isna(m) for m in metrics)