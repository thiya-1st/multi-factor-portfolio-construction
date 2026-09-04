from src.factors.utils import has_missing_data

import numpy as np

def calculate_ev_ebitda(total_debt, ebitda, cash, market_cap):
    if has_missing_data(total_debt, ebitda, cash, market_cap) or ebitda == 0:
        return np.nan
    
    ev = market_cap + total_debt - cash
    return ev / ebitda

def calculate_fcf_yield(operating_cash_flow, capital_expenditure, market_cap):
    if has_missing_data(operating_cash_flow, capital_expenditure, market_cap) or market_cap == 0:
        return np.nan
    
    free_cash_flow = operating_cash_flow - capital_expenditure
    return free_cash_flow / market_cap
       

def calculate_earnings_yield(market_cap, net_income):

    if has_missing_data(net_income, market_cap) or market_cap == 0:
        return np.nan
    
    return net_income / market_cap

def build_value_table(
        ticker, 
        date, 
        balance_sheet, 
        cash_flow, 
        income_statement, 
        prices,
        metadata,
        latest_balance_sheet_period,
        latest_income_statement_period,
        latest_cash_flow_period,
        latest_price_date,
        value_table
    ):

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