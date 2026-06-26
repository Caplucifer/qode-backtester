"""
patch_market_cap.py
--------------------
One-off fix: the original fetch_data.py run saved market_cap in RAW
RUPEES instead of CRORES, which made any crore-based market-cap filter
(e.g. "1000 to 10000") reject every stock. This patches the existing
fundamentals.csv in place by dividing market_cap by 1 crore, without
re-hitting the Yahoo Finance API.

Run once from the backend/ directory:
    python scripts/patch_market_cap.py
"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PATH = os.path.join(RAW_DIR, "fundamentals.csv")

CRORE = 1_00_00_000


def main():
    df = pd.read_csv(PATH)

    if "market_cap" not in df.columns:
        print("No market_cap column found -- nothing to patch.")
        return

    non_null = df["market_cap"].dropna()
    if non_null.empty:
        print("market_cap column is entirely empty -- nothing to patch.")
        return

    median_val = non_null.median()
    if median_val < 50_00_000:  # already looks like crores, not raw rupees
        print(f"market_cap median is {median_val:,.1f} -- looks already converted. Skipping.")
        return

    df["market_cap"] = df["market_cap"] / CRORE
    df.to_csv(PATH, index=False)
    print(f"Patched market_cap: divided by {CRORE:,} (1 crore).")
    print(f"New market_cap range: {df['market_cap'].min():,.1f} to {df['market_cap'].max():,.1f} (crores)")


if __name__ == "__main__":
    main()