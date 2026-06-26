"""
backfill_market_data.py
------------------------
Root-cause fix: market_cap, pe_ratio, pb_ratio, dividend_yield, and
current_ratio are only available from yfinance's free tier for TODAY,
not historically. This backfills those "today-only" fields onto every
older snapshot for the same symbol using that symbol's most recent
known value -- a documented approximation that makes filters usable
across the whole backtest period instead of only the most recent date.

Run once from the backend/ directory:
    python scripts/backfill_market_data.py
"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PATH = os.path.join(RAW_DIR, "fundamentals.csv")

MARKET_DATA_FIELDS = ["market_cap", "pe_ratio", "pb_ratio", "dividend_yield", "current_ratio"]


def main():
    df = pd.read_csv(PATH)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df = df.sort_values(["symbol", "snapshot_date"])

    before_nulls = {f: df[f].isna().sum() for f in MARKET_DATA_FIELDS if f in df.columns}

    for field in MARKET_DATA_FIELDS:
        if field not in df.columns:
            continue
        latest_known = df.groupby("symbol")[field].transform(lambda s: s.dropna().iloc[-1] if s.dropna().size else None)
        df[field] = df[field].fillna(latest_known)

    after_nulls = {f: df[f].isna().sum() for f in MARKET_DATA_FIELDS if f in df.columns}

    df["snapshot_date"] = df["snapshot_date"].dt.strftime("%Y-%m-%d")
    df.to_csv(PATH, index=False)

    print("Backfilled market-data fields onto historical snapshots:")
    for f in MARKET_DATA_FIELDS:
        if f in before_nulls:
            print(f"  {f}: {before_nulls[f]} nulls -> {after_nulls[f]} nulls")


if __name__ == "__main__":
    main()