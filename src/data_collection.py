import os
import yfinance as yf
import pandas as pd

def collect_prices(ticker, ticker_object, start_date, end_date, log_entries): #TODO save dir?
    try:
        prices = ticker_object.history(start = start_date, end = end_date, auto_adjust = False)
        if prices.empty:
            log_entries.append({
                "ticker": ticker, 
                "data_type": "prices",
                "status": "fail",
                "rows": 0,
                "start_date": None,
                "end_date": None,
                "missing_values": None,
                "missing_required_fields": None,
                "error": "empty data returned"
            })
        else:
            prices.to_csv(f"../data/raw/prices/{ticker}.csv")
            missing_values = prices.isna().sum().sum()
            log_entries.append({
                "ticker": ticker, 
                "data_type": "prices",
                "status": "success",
                "rows": len(prices),
                "start_date": prices.index.min(),
                "end_date": prices.index.max(),
                "missing_values": missing_values,
                "missing_required_fields": None,
                "error": None
            })
    except Exception as e:
        log_entries.append({
            "ticker": ticker, 
            "data_type": "prices",
            "status": "fail",
            "rows": 0,
            "start_date": None,
            "end_date": None,
            "missing_values": None,
            "missing_required_fields": None,
            "error": str(e)
        })

def collect_fundamentals(ticker, ticker_object, fundamental_type, required_fields, log_entries):
    try:
        if fundamental_type == "balance_sheet":
            fundamental_statement = ticker_object.balance_sheet
        elif fundamental_type == "cash_flow":
            fundamental_statement = ticker_object.cash_flow
        else:
            fundamental_statement = ticker_object.income_stmt

        available_fields = [field for field in required_fields if field in fundamental_statement.index]
        filtered_statement = fundamental_statement.loc[available_fields]

        if filtered_statement.empty:
            log_entries.append({
                "ticker": ticker, 
                "data_type": fundamental_type,
                "status": "fail",
                "rows": 0,
                "start_date": None,
                "end_date": None,
                "missing_values": None,
                "missing_required_fields": None,
                "error": "empty data returned"
            })
        else:
            os.makedirs(f"../data/raw/fundamentals/{ticker}", exist_ok = True)
            cleaned_statement = filtered_statement.dropna(axis = 1, how = "all")
            cleaned_statement.to_csv(f"../data/raw/fundamentals/{ticker}/{fundamental_type}.csv")
            missing_values = cleaned_statement.isna().sum().sum()
            missing_fields = [field for field in required_fields if field not in cleaned_statement.index]
            log_entries.append({
                "ticker": ticker, 
                "data_type": fundamental_type,
                "status": "success",
                "rows": cleaned_statement.shape[1],
                "start_date": cleaned_statement.columns.min(),
                "end_date": cleaned_statement.columns.max(),
                "missing_values": missing_values,
                "missing_required_fields": missing_fields,
                "error": None
            })
    except Exception as e:
        log_entries.append({
            "ticker": ticker, 
            "data_type": fundamental_type,
            "status": "fail",
            "rows": 0,
            "start_date": None,
            "end_date": None,
            "missing_values": None,
            "missing_required_fields": None,
            "error": str(e)
        })


def collect_metadata(ticker, ticker_object, required_fields, log_entries):
    #TODO make it more reusable (required fields)
    pass

def collect_all_data(ticker, start_date, end_date, ):
    #TODO why startdate and enddate here but not required fields
    log_entries = []
    ticker_object = yf.Ticker(ticker)
    # collect everything 

    collection_log = pd.DataFrame(log_entries)
    collection_log.to_csv("../data/raw/collection_log.csv", index = False)