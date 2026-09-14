from src.factors.utils import get_latest_price_date, get_adj_close_price, has_missing_data

import pandas as pd
import numpy as np

def calculate_momentum(prices, date, lookback_months, skip_num_months):
    date = pd.Timestamp(date)
    
    current_target_date = date - pd.DateOffset(months = skip_num_months)
    current_price_date = get_latest_price_date(prices, current_target_date)
    current_price = get_adj_close_price(prices, current_price_date)

    past_target_date = date - pd.DateOffset(months = lookback_months)
    past_price_date = get_latest_price_date(prices, past_target_date) 
    past_price = get_adj_close_price(prices, past_price_date)

    if has_missing_data([current_price, past_price]):
        return np.nan
    return current_price / past_price - 1

def build_momentum_table(ticker, string_date, prices, latest_price_date, momentum_table):

    momentum_12_1 = calculate_momentum(prices, latest_price_date, 12, 1)
    momentum_6 = calculate_momentum(prices, latest_price_date, 6, 0) 
    momentum_3 = calculate_momentum(prices, latest_price_date, 3, 0)

    momentum_table.append({
        "ticker": ticker,
        "date": string_date,
        "momentum_12_1": momentum_12_1,
        "momentum_6": momentum_6,
        "momentum_3": momentum_3
    })

    return pd.DataFrame(momentum_table)
