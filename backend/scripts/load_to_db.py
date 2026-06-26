"""
load_to_db.py
-------------
Reads the cleaned CSVs produced by fetch_data.py and loads them into
the database defined in app/database.py + app/models.py.

Run from the backend/ directory, AFTER fetch_data.py has produced
data/raw/prices.csv and data/raw/fundamentals.csv:

    python scripts/load_to_db.py
"""

import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import init_db, SessionLocal
from app.models import Company, StockPrice, StockFundamental

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def parse_date(val):
    if pd.isna(val):
        return None
    if isinstance(val, str):
        return datetime.strptime(val[:10], "%Y-%m-%d").date()
    return pd.to_datetime(val).date()


def load_companies_and_fundamentals(db):
    path = os.path.join(RAW_DIR, "fundamentals.csv")
    if not os.path.exists(path):
        print(f"Missing {path} -- run fetch_data.py first.")
        return

    df = pd.read_csv(path)
    inserted_companies = 0
    inserted_fund = 0
    seen_symbols = set()  # tracks symbols already added in THIS session, since
                           # a query can't see our own uncommitted inserts yet
    seen_fund_keys = set()  # tracks (symbol, snapshot_date) pairs added in THIS session

    for _, row in df.iterrows():
        symbol = row.get("symbol")
        if not symbol or pd.isna(symbol):
            continue

        # Upsert company (check both the DB and what we've already queued
        # in this session, since multiple fundamental rows share a symbol)
        if symbol not in seen_symbols:
            company = db.query(Company).filter_by(symbol=symbol).first()
            if not company:
                company = Company(
                    symbol=symbol,
                    company_name=row.get("company_name") if pd.notna(row.get("company_name")) else None,
                    sector=row.get("sector") if pd.notna(row.get("sector")) else None,
                    industry=row.get("industry") if pd.notna(row.get("industry")) else None,
                )
                db.add(company)
                db.flush()  # write immediately so later rows in this loop can see it
                inserted_companies += 1
            seen_symbols.add(symbol)

        snapshot_date = parse_date(row.get("snapshot_date"))
        if snapshot_date is None:
            continue

        fund_key = (symbol, snapshot_date)
        if fund_key in seen_fund_keys:
            continue  # duplicate (symbol, snapshot_date) within this CSV -- skip 2nd occurrence
        seen_fund_keys.add(fund_key)

        existing = db.query(StockFundamental).filter_by(
            symbol=symbol, snapshot_date=snapshot_date
        ).first()
        if existing:
            continue  # already loaded in a previous run, skip (idempotent re-run)

        def f(col):
            v = row.get(col)
            return float(v) if pd.notna(v) else None

        fund = StockFundamental(
            symbol=symbol,
            snapshot_date=snapshot_date,
            total_revenue=f("total_revenue"),
            pat=f("pat"),
            ebit=f("ebit"),
            total_equity=f("total_equity"),
            total_debt=f("total_debt"),
            total_assets=f("total_assets"),
            operating_cashflow=f("operating_cashflow"),
            market_cap=f("market_cap"),
            roe=f("roe"),
            roce=f("roce"),
            pe_ratio=f("pe_ratio"),
            pb_ratio=f("pb_ratio"),
            dividend_yield=f("dividend_yield"),
            debt_to_equity=f("debt_to_equity"),
            current_ratio=f("current_ratio"),
        )
        db.add(fund)
        inserted_fund += 1

    db.commit()
    print(f"Companies inserted: {inserted_companies}")
    print(f"Fundamental rows inserted: {inserted_fund}")


def load_prices(db):
    path = os.path.join(RAW_DIR, "prices.csv")
    if not os.path.exists(path):
        print(f"Missing {path} -- run fetch_data.py first.")
        return

    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    from sqlalchemy.exc import IntegrityError

    records = df.to_dict(orient="records")
    chunk_size = 1000
    inserted = 0

    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        try:
            db.bulk_insert_mappings(StockPrice, chunk)
            db.commit()
            inserted += len(chunk)
        except IntegrityError:
            db.rollback()
            for rec in chunk:
                try:
                    db.add(StockPrice(**rec))
                    db.commit()
                    inserted += 1
                except IntegrityError:
                    db.rollback()

    print(f"Price rows inserted: {inserted}")


def main():
    init_db()
    db = SessionLocal()
    try:
        load_companies_and_fundamentals(db)
        load_prices(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()