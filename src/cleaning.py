"""Phase 3 + 5: Data cleaning and feature engineering."""
import pandas as pd


def clean_data(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    df = df.copy()
    # standardise text first so " food " and "Food" become identical
    for col in ("Category", "Type", "Payment_Method"):
        if col in df:
            df[col] = df[col].astype(str).str.strip().str.title()

    n0 = len(df)
    df = df.drop_duplicates()
    n_dup = n0 - len(df)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    n1 = len(df)
    df = df.dropna(subset=["Date", "Amount", "Category", "Type"])
    df = df[df["Amount"] > 0]
    n_bad = n1 - len(df)

    # ---- feature engineering ----
    df["Year"] = df["Date"].dt.year
    df["Month_Num"] = df["Date"].dt.month
    df["Month"] = df["Date"].dt.strftime("%b")
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
    df["Weekday"] = df["Date"].dt.day_name()
    df["Is_Weekend"] = df["Date"].dt.dayofweek >= 5
    df["Signed_Amount"] = df["Amount"].where(df["Type"] == "Income", -df["Amount"])

    df = df.sort_values("Date").reset_index(drop=True)
    if verbose:
        print(f"    removed {n_dup} duplicates and {n_bad} invalid rows -> {len(df)} clean rows")
    return df
