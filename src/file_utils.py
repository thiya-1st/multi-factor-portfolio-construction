import pandas as pd

def load_file(file_path, date_axis = None, index_col = 0):
    try:
        df = pd.read_csv(file_path, index_col = index_col)
        if date_axis == "index":
            df.index = pd.to_datetime(df.index.astype(str).str[:10])
        elif date_axis == "columns":
            df.columns = pd.to_datetime(df.columns)
        return df
    except FileNotFoundError:
        return None