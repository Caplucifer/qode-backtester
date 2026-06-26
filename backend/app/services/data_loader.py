"""
data_loader.py
---------------
Bridges the database (SQLAlchemy models) and the BacktestEngine
(which operates on plain pandas DataFrames). Keeping this separate
means the engine itself has zero knowledge of SQL/SQLAlchemy and can
be unit-tested with synthetic DataFrames, as we did in test_engine.py.
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import StockPrice, StockFundamental, Company


def load_prices(db: Session, start_date, end_date) -> pd.DataFrame:
    stmt = select(
        StockPrice.symbol, StockPrice.date, StockPrice.close
    ).where(
        StockPrice.date >= start_date, StockPrice.date <= end_date
    )
    rows = db.execute(stmt).all()
    return pd.DataFrame(rows, columns=["symbol", "date", "close"])


def load_fundamentals(db: Session, end_date) -> pd.DataFrame:
    """
    Loads ALL fundamental snapshots up to end_date (not just within the
    backtest window) -- the engine needs snapshots that may predate
    start_date so the very first rebalance has data to filter/rank on.
    """
    stmt = select(
        StockFundamental.symbol,
        StockFundamental.snapshot_date,
        StockFundamental.market_cap,
        StockFundamental.pat,
        StockFundamental.roce,
        StockFundamental.roe,
        StockFundamental.pe_ratio,
        StockFundamental.pb_ratio,
        StockFundamental.total_revenue,
        StockFundamental.total_debt,
        StockFundamental.total_equity,
        StockFundamental.debt_to_equity,
        StockFundamental.current_ratio,
        StockFundamental.dividend_yield,
    ).where(StockFundamental.snapshot_date <= end_date)
    rows = db.execute(stmt).all()
    columns = [
        "symbol", "snapshot_date", "market_cap", "pat", "roce", "roe",
        "pe_ratio", "pb_ratio", "total_revenue", "total_debt", "total_equity",
        "debt_to_equity", "current_ratio", "dividend_yield",
    ]
    return pd.DataFrame(rows, columns=columns)


def load_company_list(db: Session) -> pd.DataFrame:
    stmt = select(Company.symbol, Company.company_name, Company.sector, Company.industry)
    rows = db.execute(stmt).all()
    return pd.DataFrame(rows, columns=["symbol", "company_name", "sector", "industry"])
