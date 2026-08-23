from src import config

import pandas as pd
import numpy as np

def calculate_momentum(prices, snapshot_date, lookback_months, skip_num_months):
    pd_date = pd.Timestamp(snapshot_date)

    current_price = None
    for i in range(config.PRICE_SEARCH_THRESHOLD_DAYS):
        current_date = pd_date - pd.DateOffset(months = skip_num_months) - pd.Timedelta(days = i)
        try:
            current_price = prices.loc[current_date, "Adj Close"]
            break
        except KeyError:
            pass

    past_price = None
    for i in range(config.PRICE_SEARCH_THRESHOLD_DAYS):
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

def build_momentum_table(universe):
    momentum_table = []
    missing_prices_log = []
    nan_log = []

    for ticker in universe["Ticker"]:
        try:
            prices = pd.read_csv(f"../data/raw/prices/{ticker}.csv", index_col = "Date") ##TODO: add ../
        except:
            missing_prices_log.append({"ticker": ticker, "missing_file": "prices"})
            continue

        prices.index = pd.to_datetime(prices.index.astype(str).str[:10])

        for date in config.REBALANCE_DATES:
            momentum_12_1 = calculate_momentum(prices, date, 12, 1)
            momentum_6 = calculate_momentum(prices, date, 6, 0) 
            momentum_3 = calculate_momentum(prices, date, 3, 0)

            for metric_name, value in [
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

    return pd.DataFrame(momentum_table), pd.DataFrame(missing_prices_log), pd.DataFrame(nan_log)
