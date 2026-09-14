from src import config
from src.factors.utils import has_missing_data

from typing import Optional
import pandas as pd
import numpy as np

def calculate_roic(
        ebit: float,
        total_debt: float,
        equity: float,
        cash: float,
        tax_provision: float,
        pretax_income: float,
        ticker_country: str
    ) -> float:
    """
    Calculate Return on Invested Capital (ROIC) for a single company-period.

    ROIC = NOPAT / Invested Capital, where NOPAT = EBIT * (1 - effective
    tax rate) and Invested Capital = Total Debt + Equity - Cash. The
    effective tax rate is Tax Provision / Pretax Income where both are
    available and Pretax Income is non-zero; otherwise it falls back to
    a flat, country-specific assumed rate.

    Parameters:
        ebit: Earnings Before Interest and Tax, from the income statement.
        total_debt: Total debt, from the balance sheet.
        equity: Total Equity Gross Minority Interest, from the balance sheet.
        cash: Cash and Cash Equivalents, from the balance sheet.
        tax_provision: Tax Provision, from the income statement. May be NaN.
        pretax_income: Pretax Income, from the income statement. May be NaN.
        ticker_country: Company's country (e.g. "US", "UK"), used to select
            the fallback tax rate when actual tax data is unavailable.

    Returns:
        ROIC as a decimal (e.g. 0.15 for 15%), or np.nan if any required
        input (ebit, total_debt, equity, cash) is missing, or if Invested
        Capital is zero.
    """

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

def calculate_gross_margin(gross_profit: float, total_revenue: float) -> float:
    """
    Calculate gross margin for a single company-period.

    Parameters:
        gross_profit: Gross Profit, from the income statement.
        total_revenue: Total Revenue, from the income statement.

    Returns:
        Gross margin as a decimal, or np.nan if either input is missing
        or Total Revenue is zero.
    """

    if has_missing_data([gross_profit, total_revenue]) or total_revenue == 0:
        return np.nan

    return gross_profit / total_revenue 

def calculate_operating_margin(ebit: float, total_revenue: float) -> float:
    """
    Calculate operating margin for a single company-period.

    Parameters:
        ebit: Earnings Before Interest and Tax, from the income statement.
        total_revenue: Total Revenue, from the income statement.

    Returns:
        Operating margin as a decimal, or np.nan if either input is
        missing or Total Revenue is zero.
    """

    if has_missing_data([ebit, total_revenue]) or total_revenue == 0:
        return np.nan
    
    return ebit / total_revenue 

def build_quality_table(
        ticker: str,
        ticker_country: str,
        string_date: pd.Timestamp,
        balance_sheet: pd.DataFrame,
        income_statement: pd.DataFrame,
        latest_balance_sheet_period: Optional[pd.Timestamp],
        latest_income_statement_period: Optional[pd.Timestamp],
        quality_table: list[dict]
    ) -> None:
    """
    Calculate all Phase 1 quality metrics for one ticker at one rebalance
    date and append the result as a row to quality_table.

    Looks up the required fields from balance_sheet and income_statement
    at the given latest available periods, computes ROIC, gross margin,
    and operating margin, and appends a single dict record. If a given
    statement's latest period is None, the corresponding inputs are
    treated as NaN and propagate to NaN metric values.

    Parameters:
        ticker: Ticker symbol for the company being processed.
        ticker_country: Company's country, passed through to
            calculate_roic for the tax rate fallback.
        string_date: Rebalance date this row corresponds to.
        balance_sheet: Balance sheet data for this ticker, indexed by
            field name with periods as columns.
        income_statement: Income statement data for this ticker, indexed
            by field name with periods as columns.
        latest_balance_sheet_period: The most recent balance sheet period
            considered "known" as of date (already lag-adjusted), or None
            if no such period exists.
        latest_income_statement_period: The most recent income statement
            period considered "known" as of date (already lag-adjusted),
            or None if no such period exists.
        quality_table: Accumulator list that this function appends a
            result row to, in place.

    Returns:
        None. Mutates quality_table in place.
    """

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
        "date": string_date,
        "roic": roic,
        "gross margin": gross_margin,
        "operating margin": operating_margin
    })