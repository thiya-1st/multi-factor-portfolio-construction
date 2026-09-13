from src.factors.utils import has_missing_data

import numpy as np
import pandas as pd
from typing import Optional

def calculate_ev_ebitda(
        total_debt: float,
        ebitda: float,
        cash: float,
        market_cap: float
    ) -> float:
    """
    Calculate EV/EBITDA for a single company-period.

    Enterprise Value = Market Cap + Total Debt - Cash.
    EV/EBITDA = Enterprise Value / EBITDA.

    Parameters:
        total_debt: Total debt, from the balance sheet.
        ebitda: EBITDA, from the income statement.
        cash: Cash and Cash Equivalents, from the balance sheet.
        market_cap: Market capitalisation (price * shares outstanding).

    Returns:
        EV/EBITDA as a ratio, or np.nan if any required input is missing
        or EBITDA is zero.
    """

    if has_missing_data([total_debt, ebitda, cash, market_cap]) or ebitda == 0:
        return np.nan
    
    ev = market_cap + total_debt - cash
    return ev / ebitda

def calculate_fcf_yield(
        operating_cash_flow: float,
        capital_expenditure: float,
        market_cap: float
    ) -> float:
    """
    Calculate Free Cash Flow yield for a single company-period.

    Free Cash Flow = Operating Cash Flow - Capital Expenditure.
    FCF Yield = Free Cash Flow / Market Cap.

    Parameters:
        operating_cash_flow: Operating Cash Flow, from the cash flow statement.
        capital_expenditure: Capital Expenditure, from the cash flow statement.
        market_cap: Market capitalisation (price * shares outstanding).

    Returns:
        FCF yield as a decimal, or np.nan if any required input is
        missing or Market Cap is zero.
    """

    if has_missing_data([operating_cash_flow, capital_expenditure, market_cap]) or market_cap == 0:
        return np.nan
    
    free_cash_flow = operating_cash_flow - capital_expenditure
    return free_cash_flow / market_cap
       

def calculate_earnings_yield(
        market_cap: float,
        net_income: float
    ) -> float:
    """
    Calculate earnings yield for a single company-period.

    Earnings Yield = Net Income / Market Cap (inverse of trailing P/E).

    Parameters:
        market_cap: Market capitalisation (price * shares outstanding).
        net_income: Net Income, from the income statement.

    Returns:
        Earnings yield as a decimal, or np.nan if either input is
        missing or Market Cap is zero.
    """

    if has_missing_data([net_income, market_cap]) or market_cap == 0:
        return np.nan
    
    return net_income / market_cap

def build_value_table(
        ticker: str,
        date: pd.Timestamp,
        balance_sheet: pd.DataFrame,
        cash_flow: pd.DataFrame,
        income_statement: pd.DataFrame,
        prices: pd.DataFrame,
        metadata: pd.DataFrame,
        latest_balance_sheet_period: Optional[pd.Timestamp],
        latest_income_statement_period: Optional[pd.Timestamp],
        latest_cash_flow_period: Optional[pd.Timestamp],
        latest_price_date: Optional[pd.Timestamp],
        value_table: list[dict]
    ) -> None:
    """
    Calculate all Phase 1 value metrics for one ticker at one rebalance
    date and append the result as a row to value_table.

    Looks up the required fields from balance_sheet, cash_flow, and
    income_statement at the given latest available periods, plus the
    latest available adjusted close price and shares outstanding, derives
    market cap, computes EV/EBITDA, FCF yield, and earnings yield, and
    appends a single dict record. If a given statement's latest period
    (or the latest price date) is None, the corresponding inputs are
    treated as NaN and propagate to NaN metric values.

    Parameters:
        ticker: Ticker symbol for the company being processed.
        date: Rebalance date this row corresponds to.
        balance_sheet: Balance sheet data for this ticker, indexed by
            field name with periods as columns.
        cash_flow: Cash flow statement data for this ticker, indexed by
            field name with periods as columns.
        income_statement: Income statement data for this ticker, indexed
            by field name with periods as columns.
        prices: Price history for this ticker, indexed by date with an
            "Adj Close" column.
        metadata: Metadata for all tickers, indexed by ticker, with a
            "sharesOutstanding" column.
        latest_balance_sheet_period: The most recent balance sheet period
            considered "known" as of date (already lag-adjusted), or None
            if no such period exists.
        latest_income_statement_period: The most recent income statement
            period considered "known" as of date (already lag-adjusted),
            or None if no such period exists.
        latest_cash_flow_period: The most recent cash flow statement
            period considered "known" as of date (already lag-adjusted),
            or None if no such period exists.
        latest_price_date: The most recent trading date with an available
            price as of date (within the search threshold), or None if
            none was found.
        value_table: Accumulator list that this function appends a
            result row to, in place.

    Returns:
        None. Mutates value_table in place.
    """

    if latest_income_statement_period is not None:
        ebitda = income_statement.loc["EBITDA", latest_income_statement_period]
        net_income = income_statement.loc["Net Income", latest_income_statement_period]
    else:
        ebitda = net_income = np.nan

    if latest_balance_sheet_period is not None:
        total_debt = balance_sheet.loc["Total Debt", latest_balance_sheet_period]
        cash = balance_sheet.loc["Cash And Cash Equivalents", latest_balance_sheet_period]
    else:
        total_debt = cash = np.nan

    if latest_cash_flow_period is not None:
        operating_cash_flow = cash_flow.loc["Operating Cash Flow" , latest_cash_flow_period]
        capital_expenditure = cash_flow.loc["Capital Expenditure" , latest_cash_flow_period]
    else:
        operating_cash_flow = capital_expenditure = np.nan
    
    if latest_price_date is not None:
        price_adj_close = prices.loc[latest_price_date, "Adj Close"] #TODO: same function as momentum
    else:
        price_adj_close = np.nan

    try:
        shares_outstanding = metadata.loc[ticker, "sharesOutstanding"]
    except:
        shares_outstanding = np.nan

    if has_missing_data([price_adj_close, shares_outstanding]):
        market_cap = np.nan
    else:
        market_cap = price_adj_close * shares_outstanding
        
    ev_ebitda = calculate_ev_ebitda(total_debt, ebitda, cash, market_cap)
    free_cash_flow_yield = calculate_fcf_yield(operating_cash_flow, capital_expenditure, market_cap)
    earnings_yield = calculate_earnings_yield(market_cap, net_income)

    value_table.append({
        "ticker": ticker,
        "date": date,
        "ev_ebitda": ev_ebitda,
        "free cash flow yield": free_cash_flow_yield,
        "earnings yield": earnings_yield
    }) 