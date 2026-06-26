"""
fetch_data.py
--------------
Fetches historical OHLCV price data and fundamental data for the NSE
stock universe using yfinance, cleans it, and writes two CSV files:

    data/raw/prices.csv       -> daily OHLCV for every stock
    data/raw/fundamentals.csv -> quarterly/annual fundamental snapshots

These CSVs are the input to load_to_db.py, which loads them into the
database. We deliberately separate "fetch" from "load" so that a slow
or partially-failed scrape can be re-run / inspected before touching
the database.

Run from the backend/ directory:
    python scripts/fetch_data.py
"""

import os
import time
import traceback
from datetime import datetime

import pandas as pd
import yfinance as yf

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.data.universe import NSE_UNIVERSE

# ---- Config ----
START_DATE = "2015-01-01"
END_DATE = datetime.today().strftime("%Y-%m-%d")
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

SLEEP_BETWEEN_CALLS = 1.2  # be polite to Yahoo's endpoint, avoid throttling


def fetch_prices(symbol: str) -> pd.DataFrame:
    """Fetch daily OHLCV for a single symbol. Returns empty df on failure."""
    try:
        df = yf.download(
            symbol,
            start=START_DATE,
            end=END_DATE,
            progress=False,
            auto_adjust=False,
        )
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.reset_index()
        # yfinance sometimes returns MultiIndex columns when downloading
        # a single ticker depending on version -- flatten defensively.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

        df["symbol"] = symbol
        df = df.rename(columns={
            "Date": "date", "Open": "open", "High": "high",
            "Low": "low", "Close": "close", "Adj Close": "adj_close",
            "Volume": "volume",
        })
        keep = ["symbol", "date", "open", "high", "low", "close", "adj_close", "volume"]
        return df[[c for c in keep if c in df.columns]]
    except Exception as e:
        print(f"  [PRICE ERROR] {symbol}: {e}")
        return pd.DataFrame()


def fetch_fundamentals(symbol: str) -> list:
    """
    Fetch MULTIPLE historical fundamental snapshots for a single symbol,
    one per available annual reporting period, using yfinance's
    `.financials` / `.balance_sheet` / `.cashflow` (these expose ~4 years
    of annual columns, not just the latest).

    Returns a LIST of dicts (one per fiscal year-end available), each
    dated at that period's actual reporting date. This is what makes the
    backtest's "no future data leakage" rule meaningful: at rebalance
    date D, the engine only uses snapshots with snapshot_date <= D, so
    it must have at least 2-3 distinct dated snapshots per company to
    behave like a real point-in-time backtest rather than re-using one
    static snapshot for the whole history.

    `.info` fields (market cap, PE, dividend yield, ROE) reflect TODAY's
    market data only -- yfinance's free tier does not expose historical
    market cap or valuation ratios. We attach today's `.info` snapshot
    as well (dated today) so ranking/filtering on market cap or PE still
    works for the most recent rebalances. This is a real limitation of
    free data sources -- documented as an assumption in the README.
    """
    try:
        tk = yf.Ticker(symbol)
        info = tk.info or {}

        financials = tk.financials       # columns = period end dates, most recent first
        balance_sheet = tk.balance_sheet
        cashflow = tk.cashflow

        snapshots = []

        if financials is not None and not financials.empty:
            period_dates = list(financials.columns)

            for period_date in period_dates:
                def get(df, row_name):
                    try:
                        if df is None or df.empty or row_name not in df.index:
                            return None
                        if period_date not in df.columns:
                            return None
                        val = df.loc[row_name, period_date]
                        return None if pd.isna(val) else float(val)
                    except Exception:
                        return None

                pat = get(financials, "Net Income")
                total_revenue = get(financials, "Total Revenue")
                ebit = get(financials, "EBIT")
                total_equity = get(balance_sheet, "Common Stock Equity") or \
                               get(balance_sheet, "Stockholders Equity")
                total_debt = get(balance_sheet, "Total Debt")
                total_assets = get(balance_sheet, "Total Assets")
                op_cashflow = get(cashflow, "Operating Cash Flow")
                current_liab = get(balance_sheet, "Current Liabilities")

                roce = None
                if ebit is not None and total_assets is not None:
                    capital_employed = total_assets - (current_liab or 0)
                    if capital_employed:
                        roce = ebit / capital_employed

                roe = None
                if pat is not None and total_equity:
                    roe = pat / total_equity

                snapshots.append({
                    "symbol": symbol,
                    "company_name": info.get("longName") or info.get("shortName"),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    # market-data fields below are NOT point-in-time (see docstring) --
                    # only attached on the most recent snapshot, left blank on older ones
                    "market_cap": None,
                    "pat": pat,
                    "total_revenue": total_revenue,
                    "ebit": ebit,
                    "total_equity": total_equity,
                    "total_debt": total_debt,
                    "total_assets": total_assets,
                    "operating_cashflow": op_cashflow,
                    "roe": roe,
                    "roce": roce,
                    "pe_ratio": None,
                    "pb_ratio": None,
                    "dividend_yield": None,
                    "debt_to_equity": (total_debt / total_equity) if (total_debt and total_equity) else None,
                    "current_ratio": None,
                    "snapshot_date": pd.Timestamp(period_date).strftime("%Y-%m-%d"),
                })

        # Attach today's live market-data snapshot (market cap, PE, etc.) as the
        # most recent dated row -- these fields are NOT available historically
        # from yfinance's free tier, so we only have a true value as-of today.
        snapshots.append({
            "symbol": symbol,
            "company_name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "pat": snapshots[0]["pat"] if snapshots else None,
            "total_revenue": snapshots[0]["total_revenue"] if snapshots else None,
            "ebit": snapshots[0]["ebit"] if snapshots else None,
            "total_equity": snapshots[0]["total_equity"] if snapshots else None,
            "total_debt": snapshots[0]["total_debt"] if snapshots else None,
            "total_assets": snapshots[0]["total_assets"] if snapshots else None,
            "operating_cashflow": snapshots[0]["operating_cashflow"] if snapshots else None,
            "roe": info.get("returnOnEquity") or (snapshots[0]["roe"] if snapshots else None),
            "roce": snapshots[0]["roce"] if snapshots else None,
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "debt_to_equity": info.get("debtToEquity") or (snapshots[0]["debt_to_equity"] if snapshots else None),
            "current_ratio": info.get("currentRatio"),
            "snapshot_date": END_DATE,
        })

        return snapshots
    except Exception as e:
        print(f"  [FUNDAMENTAL ERROR] {symbol}: {e}")
        return [{"symbol": symbol, "snapshot_date": END_DATE}]


def main():
    all_prices = []
    all_fundamentals = []
    failed = []

    total = len(NSE_UNIVERSE)
    for i, symbol in enumerate(NSE_UNIVERSE, start=1):
        print(f"[{i}/{total}] Fetching {symbol} ...")
        try:
            price_df = fetch_prices(symbol)
            if price_df.empty:
                failed.append(symbol)
            else:
                all_prices.append(price_df)

            fund_list = fetch_fundamentals(symbol)
            all_fundamentals.extend(fund_list)
        except Exception:
            print(f"  [UNEXPECTED ERROR] {symbol}")
            traceback.print_exc()
            failed.append(symbol)

        time.sleep(SLEEP_BETWEEN_CALLS)

    # ---- Save prices ----
    if all_prices:
        prices_df = pd.concat(all_prices, ignore_index=True)
        prices_df = prices_df.dropna(subset=["close"])
        prices_df.to_csv(os.path.join(RAW_DIR, "prices.csv"), index=False)
        print(f"\nSaved {len(prices_df)} price rows for {prices_df['symbol'].nunique()} symbols.")
    else:
        print("\nWARNING: no price data fetched at all.")

    # ---- Save fundamentals ----
    fundamentals_df = pd.DataFrame(all_fundamentals)
    fundamentals_df.to_csv(os.path.join(RAW_DIR, "fundamentals.csv"), index=False)
    n_symbols = fundamentals_df["symbol"].nunique() if "symbol" in fundamentals_df.columns else 0
    print(f"Saved {len(fundamentals_df)} fundamental snapshots across {n_symbols} symbols.")

    if failed:
        print(f"\n{len(failed)} symbols failed entirely: {failed}")
        with open(os.path.join(RAW_DIR, "failed_symbols.txt"), "w") as f:
            f.write("\n".join(failed))


if __name__ == "__main__":
    main()
