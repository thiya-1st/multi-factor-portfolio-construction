from src import config

import pandas as pd
import numpy as np

def calculate_momentum(prices, snapshot_date, lookback_months, skip_num_months):
    pd_date = pd.Timestamp(snapshot_date)

    current_price = None
    for i in range(config.PRICE_SEARCH_THRESHOLD_DAYS): #TODO: make into function if possible
        current_date = pd_date - pd.DateOffset(months = skip_num_months) - pd.Timedelta(days = i)
        try:
            current_price = prices.loc[current_date, "Adj Close"]
            break
        except KeyError:
            pass

    past_price = None
    for i in range(config.PRICE_SEARCH_THRESHOLD_DAYS): #TODO: function
        past_date = pd_date - pd.DateOffset(months = lookback_months) - pd.Timedelta(days = i)
        try:
            past_price = prices.loc[past_date, "Adj Close"]
            break
        except KeyError:
            pass

    if current_price is None or past_price is None:
        return np.nan
    else:
        return current_price / past_price - 1

def build_momentum_table(ticker, date, prices, latest_price_date, momentum_table):
    momentum_table = []
    missing_files_log = []
    nan_log = []

    prices.index = pd.to_datetime(prices.index.astype(str).str[:10])

    momentum_12_1 = calculate_momentum(prices, latest_price_date, 12, 1)
    momentum_6 = calculate_momentum(prices, latest_price_date, 6, 0) 
    momentum_3 = calculate_momentum(prices, latest_price_date, 3, 0)

    for metric_name, value in [ #TODO: check 
        ("momentum_12_1", momentum_12_1), 
        ("momentum_6", momentum_6), 
        ("momentum_3", momentum_3)
        ]:
        if pd.isna(value):
            nan_log.append({"ticker": ticker, "date": date, "metric": metric_name})

    momentum_table.append({
        "ticker": ticker,
        "date": date,
        "momentum_12_1": momentum_12_1,
        "momentum_6": momentum_6,
        "momentum_3": momentum_3
    })

    return pd.DataFrame(momentum_table), pd.DataFrame(nan_log) #TODO: check
