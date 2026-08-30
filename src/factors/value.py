from src import config

import pandas as pd
import numpy as np

def get_latest_fundamental_period(fundamentals, date):
    pass

def get_latest_price_date(prices, date):
    pass

def has_missing_data(latest_fundamental_periods, metrics):
    for period in latest_fundamental_periods:
        if period is None:
            return True
    for metric in metrics:
        if pd.isna(metric):
            return True
    return False #going to put it into a repeated file later

def build_value_table(universe):
    value_table = []
    missing_files_log = []

    for ticker in universe["Ticker"]:
        try:
            balance_sheet = pd.read_csv(f"../../data/raw/fundamentals/{ticker}/balance_sheet.csv", index_col = 0) #TODO: check
        except FileNotFoundError:
            missing_files_log.append({"ticker": ticker, "missing_file": "balance sheet"})
            continue

        try:
            income_statement = pd.read_csv(f"../../data/raw/fundamentals/{ticker}/income_statement.csv", index_col = 0) #TODO: check
        except FileNotFoundError:
            missing_files_log.append({"ticker": ticker, "missing_file": "income statement"})
            continue

        try:
            cash_flow_statement = pd.read_csv(f"../../data/raw/fundamentals/{ticker}/cash_flow_statement.csv", index_col = 0) #TODO: check
        except FileNotFoundError:
            missing_files_log.append({"ticker": ticker, "missing_file": "cash flow statement"})
            continue

        try:
            prices = pd.read_csv(f"../../data/raw/prices/{ticker}.csv", index_col = 0) #TODO: check
        except FileNotFoundError:
            missing_files_log.append({"ticker": ticker, "missing_file": "prices"}) #ROWS AND COLUMNS ARE SWAPPED
            continue

        for date in config.REBALANCE_DATES:
            latest_balance_sheet_period = get_latest_fundamental_period(balance_sheet, date)
            latest_income_statement_period = get_latest_fundamental_period(income_statement, date)
            latest_cash_flow_statement_period = get_latest_fundamental_period(cash_flow_statement, date)
            latest_price_date = get_latest_price_date(prices, date)
            #TODO: log if periods are different and check if fine



            price_adj_close = prices.loc[latest_price_date, "Adj Close"]

            earnings_per_share = income_statement.loc["EPS", latest_income_statement_period]
            ebitda = income_statement.loc["EBITDA", latest_income_statement_period]
            net_income = income_statement.loc["Net Income", latest_income_statement_period]

            total_debt = balance_sheet.loc["Total Debt", latest_balance_sheet_period]
            cash = balance_sheet.loc["Cash And Cash Equivalents", latest_balance_sheet_period]
            
            operating_cash_flow = cash_flow_statement.loc["Operating Cash Flow" , latest_cash_flow_statement_period]
            capital_expenditure = cash_flow_statement.loc["Capital Expenditure" , latest_cash_flow_statement_period]

            ev_ebitda = calculate_ev_ebitda(
                price_adj_close,
                total_debt,
                ebitda,
                cash,
                earnings_per_share,
                net_income
            )

            free_cash_flow_yield = calculate_fcf_yield(
                price_adj_close,
                operating_cash_flow,
                capital_expenditure,
                earnings_per_share,
                net_income
            )

            earnings_yield = calculate_earnings_yield(
                price_adj_close,
                net_income,
                earnings_per_share
            )

            value_table.append({
                "ticker": ticker,
                "date": date,
                "ev_ebitda": ev_ebitda,
                "free cash flow yield": free_cash_flow_yield,
                "earnings yield": earnings_yield
            })

    return pd.DataFrame(value_table)


def calculate_ev_ebitda(
        price_adj_close, 
        total_debt, 
        ebitda, 
        cash, 
        earnings_per_share, 
        net_income
    ):
    market_cap = price_adj_close * (net_income/earnings_per_share)
    ev = market_cap + total_debt - cash
    ev_ebitda = ev / ebitda
    return ev_ebitda

    # MAKE SURE MARKET CAP CALCULATION IS CORRECT (PRICES X SHARES OUTSTANDING)

def calculate_fcf_yield(
        price_adj_close, 
        operating_cash_flow, 
        capital_expenditure, 
        earnings_per_share, 
        net_income
    ):
    market_cap = price_adj_close * (net_income/earnings_per_share)
    free_cash_flow = operating_cash_flow - capital_expenditure
    fcf_yield = free_cash_flow / market_cap
    return fcf_yield
    

def calculate_earnings_yield(
        price_adj_close, 
        net_income, 
        earnings_per_share
    ):
    market_cap = price_adj_close * (net_income/earnings_per_share)
    earnings_yield = net_income / market_cap
    return earnings_yield