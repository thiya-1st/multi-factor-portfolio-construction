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

def build_momentum_table(universe):
    momentum_table = []
    missing_files_log = []
    nan_log = []

    for ticker in universe["Ticker"]:
        try:
            prices = pd.read_csv(f"../data/raw/prices/{ticker}.csv", index_col = "Date") 
        except:
            missing_files_log.append({"ticker": ticker, "missing_file": "prices"})
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
    #TODO: check if we need logs
    return pd.DataFrame(momentum_table), pd.DataFrame(missing_files_log), pd.DataFrame(nan_log)

def get_latest_fundamental_period(fundamentals, date):
    pass

def calculate_roic(country, balance_sheet, income_statement, snapshot_date):
    pd_date = pd.Timestamp(snapshot_date)
    latest_balance_sheet_period = get_latest_fundamental_period(balance_sheet, pd_date)
    latest_income_statement_period = get_latest_fundamental_period(income_statement, pd_date)

    if latest_income_statement_period is None or latest_balance_sheet_period is None:
        return np.nan

    ebit = income_statement.loc["EBIT", latest_income_statement_period]
    total_debt = balance_sheet.loc["Total Debt", latest_balance_sheet_period]
    equity = balance_sheet.loc["Total Equity Gross Minority Interest", latest_balance_sheet_period]
    cash = balance_sheet.loc["Cash And Cash Equivalents", latest_balance_sheet_period]

    if ebit is None or total_debt is None or equity is None or cash is None:
        return np.nan

    tax_provision = income_statement.loc["Tax Provision", latest_income_statement_period]
    pretax_income = income_statement.loc["Pretax Income", latest_income_statement_period]

    if tax_provision is not None and pretax_income is not None:
        tax_rate = tax_provision / pretax_income
    elif country == "US":
        tax_rate = config.FLAT_US_TAX_RATE_FALLBACK
    else:
        tax_rate = config.FLAT_UK_TAX_RATE_FALLBACK

    nopat = ebit * (1 - tax_rate)
    invested_capital = total_debt + equity - cash

    return nopat / invested_capital

def build_quality(universe):
    quality_table = []
    missing_files_log = []

    for ticker in universe["Ticker"]:
        try:
            balance_sheet = pd.read_csv(f"../data/raw/fundamentals/{ticker}/balance_sheet.csv", index_col = 0) #TODO: check
        except:
            missing_files_log.append({"ticker": ticker, "missing_file": "balance sheet"})
            continue

        try:
            income_statement = pd.read_csv(f"../data/raw/fundamentals/{ticker}/income_statement.csv", index_col = 0) #TODO: check
        except:
            missing_files_log.append({"ticker": ticker, "missing_file": "income statement"})
            continue

        country = universe.loc[ticker, "Country"]

        for date in config.REBALANCE_DATES:
            roic = calculate_roic(country, balance_sheet, income_statement, date)