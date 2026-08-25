from src import config

import pandas as pd
import numpy as np

def get_latest_fundamental_period(fundamentals, date):
    pass

def calculate_roic(
        ebit,
        total_debt,
        equity,
        cash,
        tax_provision,
        pretax_income,
        latest_balance_sheet_period, 
        latest_income_statement_period,
        ticker_country
    ):
    if latest_income_statement_period is None or latest_balance_sheet_period is None:
        return np.nan

    if pd.isna(ebit) or pd.isna(total_debt) or pd.isna(equity) or pd.isna(cash):
        return np.nan

    if not pd.isna(tax_provision) and not pd.isna(pretax_income):
        tax_rate = tax_provision / pretax_income
    elif ticker_country == "US":
        tax_rate = config.FLAT_US_TAX_RATE_FALLBACK
    else:
        tax_rate = config.FLAT_UK_TAX_RATE_FALLBACK

    nopat = ebit * (1 - tax_rate)
    invested_capital = total_debt + equity - cash

    return nopat / invested_capital #TODO: check if dividing by 0

def calculate_gross_margin(gross_profit, total_revenue, latest_income_statement_period):
    if latest_income_statement_period is None:
        return np.nan

    if pd.isna(gross_profit) or pd.isna(total_revenue):
        return np.nan

    return gross_profit / total_revenue #TODO: check divide by 0

def calculate_operating_margin(ebit, total_revenue, latest_income_statement_period):
    if latest_income_statement_period is None:
        return np.nan

    if pd.isna(ebit) or pd.isna(total_revenue):
        return np.nan

    return ebit / total_revenue #TODO: check divide by 0

def build_quality_table(universe):
    quality_table = []
    missing_files_log = []

    for ticker in universe["Ticker"]:
        try:
            balance_sheet = pd.read_csv(f"../data/raw/fundamentals/{ticker}/balance_sheet.csv", index_col = 0) #TODO: check
        except FileNotFoundError:
            missing_files_log.append({"ticker": ticker, "missing_file": "balance sheet"})
            continue

        try:
            income_statement = pd.read_csv(f"../data/raw/fundamentals/{ticker}/income_statement.csv", index_col = 0) #TODO: check
        except FileNotFoundError:
            missing_files_log.append({"ticker": ticker, "missing_file": "income statement"})
            continue

        ticker_country = universe.loc[ticker, "Country"]
        for date in config.REBALANCE_DATES:
            latest_balance_sheet_period = get_latest_fundamental_period(balance_sheet, date)
            latest_income_statement_period = get_latest_fundamental_period(income_statement, date)
            #TODO: log if periods are different and check if fine

            ebit = income_statement.loc["EBIT", latest_income_statement_period]
            tax_provision = income_statement.loc["Tax Provision", latest_income_statement_period]
            pretax_income = income_statement.loc["Pretax Income", latest_income_statement_period]
            gross_profit = income_statement.loc["Gross Profit", latest_income_statement_period]
            total_revenue = income_statement.loc["Total Revenue", latest_income_statement_period]

            total_debt = balance_sheet.loc["Total Debt", latest_balance_sheet_period]
            equity = balance_sheet.loc["Total Equity Gross Minority Interest", latest_balance_sheet_period]
            cash = balance_sheet.loc["Cash And Cash Equivalents", latest_balance_sheet_period]

            roic = calculate_roic(
                ebit,
                total_debt,
                equity,
                cash,
                tax_provision,
                pretax_income,
                latest_balance_sheet_period, 
                latest_income_statement_period,
                ticker_country
            )
            gross_margin = calculate_gross_margin(
                gross_profit, 
                total_revenue, 
                latest_income_statement_period
            )
            operating_margin = calculate_operating_margin(
                ebit, 
                total_revenue, 
                latest_income_statement_period
            )

            quality_table.append({
                "ticker": ticker,
                "date": date,
                "roic": roic,
                "gross margin": gross_margin,
                "operating margin": operating_margin
            })

    return pd.DataFrame(quality_table)