from src import config
from src.factors.utils import has_missing_data

import pandas as pd
import numpy as np

def calculate_roic(
        ebit,
        total_debt,
        equity,
        cash,
        tax_provision,
        pretax_income,
        ticker_country
    ):
    if has_missing_data([ebit, total_debt, equity, cash]):
        return np.nan

    if not pd.isna(tax_provision) and not pd.isna(pretax_income) and pretax_income != 0:
        tax_rate = tax_provision / pretax_income
    elif ticker_country == "US":
        tax_rate = config.FLAT_US_TAX_RATE_FALLBACK
    else:
        tax_rate = config.FLAT_UK_TAX_RATE_FALLBACK

    nopat = ebit * (1 - tax_rate)
    invested_capital = total_debt + equity - cash

    if invested_capital == 0:
        return np.nan
    
    return nopat / invested_capital

def calculate_gross_margin(gross_profit, total_revenue):

    if has_missing_data([gross_profit, total_revenue]) or total_revenue == 0:
        return np.nan

    return gross_profit / total_revenue 

def calculate_operating_margin(ebit, total_revenue):

    if has_missing_data([ebit, total_revenue]) or total_revenue == 0:
        return np.nan #TODO: do i need logs
    
    return ebit / total_revenue 

def build_quality_table(ticker, ticker_country, date, balance_sheet, income_statement, latest_balance_sheet_period, latest_income_statement_period, quality_table):
    if latest_income_statement_period is not None:
        ebit = income_statement.loc["EBIT", latest_income_statement_period]
        tax_provision = income_statement.loc["Tax Provision", latest_income_statement_period]
        pretax_income = income_statement.loc["Pretax Income", latest_income_statement_period]
        gross_profit = income_statement.loc["Gross Profit", latest_income_statement_period]
        total_revenue = income_statement.loc["Total Revenue", latest_income_statement_period]
    else:
        ebit = tax_provision = pretax_income = gross_profit = total_revenue = np.nan

    if latest_balance_sheet_period is not None:
        total_debt = balance_sheet.loc["Total Debt", latest_balance_sheet_period]
        equity = balance_sheet.loc["Total Equity Gross Minority Interest", latest_balance_sheet_period]
        cash = balance_sheet.loc["Cash And Cash Equivalents", latest_balance_sheet_period]
    else:
        total_debt = equity = cash = np.nan   

    roic = calculate_roic(ebit, total_debt, equity,cash, tax_provision, pretax_income, ticker_country)
    gross_margin = calculate_gross_margin(gross_profit, total_revenue)
    operating_margin = calculate_operating_margin(ebit, total_revenue)

    quality_table.append({
        "ticker": ticker,
        "date": date,
        "roic": roic,
        "gross margin": gross_margin,
        "operating margin": operating_margin
    })