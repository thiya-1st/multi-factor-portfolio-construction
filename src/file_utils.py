import pandas as pd

def load_file(ticker, missing_files, file_name, file_path):
    try:
        return pd.read_csv(file_path, index_col = 0)
    except FileNotFoundError:
        missing_files.append({"ticker": ticker, "missing_file": file_name})
        return None