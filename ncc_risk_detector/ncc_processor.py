import pandas as pd

def load_ncc_data(path):
    df = pd.read_excel(path)
    df["full_text"] = df["Title"] + ". " + df["Description"] + " " + df["Root Cause"]
    return df.to_dict(orient="records")
