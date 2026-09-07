import pandas as pd

def load_file(file_path, index_col = 0):
    try:
        return pd.read_csv(file_path, index_col = index_col)
    except FileNotFoundError:
        return None