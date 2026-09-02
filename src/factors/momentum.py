from src import config
from src.factors.utils import get_latest_price_date

import pandas as pd
import numpy as np

def get_adj_close_price(prices, date):
    if date is not None:
        try:
            return prices.loc[date, "Adj Close"]
        except:
            return None

def calculate_momentum(prices, date, lookback_months, skip_num_months):
    current_date = get_latest_price_date(prices, date) #TODO change date to date - skipmonths
    current_price = get_adj_close_price(prices, current_date)

    past_date = get_latest_price_date(prices, date) #TODO change date to date - lookbackmonths
    past_price = get_adj_close_price(prices, past_date)

    if current_price is None or past_price is None:
        return np.nan
    return current_price / past_price - 1

def build_momentum_table(ticker, date, prices, latest_price_date, momentum_table):
    momentum_table = []
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
