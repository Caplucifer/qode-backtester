"""
models.py
---------
SQLAlchemy ORM models defining the database schema.

Two core tables, as required by the assignment:
  - stock_prices: daily OHLCV, one row per (symbol, date)
  - stock_fundamentals: fundamental snapshot, one row per (symbol, snapshot_date)

A third lightweight `companies` table acts as a normalized lookup for
static info (name, sector) so it isn't repeated on every price row --
this is the "normalize tables" requirement from the spec.

Indexes are added on (symbol, date) / (symbol, snapshot_date) since
every backtest rebalance query filters by symbol + as-of date -- this
is the hot path, so it needs to be fast.

This schema works unchanged on SQLite, PostgreSQL, or MySQL -- only
the connection string in database.py changes.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255))
    sector = Column(String(100))
    industry = Column(String(150))

    prices = relationship("StockPrice", back_populates="company")
    fundamentals = relationship("StockFundamental", back_populates="company")


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("companies.symbol"), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(Float)

    company = relationship("Company", back_populates="prices")

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_price_symbol_date"),
        Index("ix_price_symbol_date", "symbol", "date"),
    )


class StockFundamental(Base):
    __tablename__ = "stock_fundamentals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("companies.symbol"), nullable=False)
    snapshot_date = Column(Date, nullable=False)

    # P&L
    total_revenue = Column(Float)
    pat = Column(Float)          # Profit After Tax / Net Income
    ebit = Column(Float)

    # Balance sheet
    total_equity = Column(Float)
    total_debt = Column(Float)
    total_assets = Column(Float)

    # Cash flow
    operating_cashflow = Column(Float)

    # Ratios / valuation metrics
    market_cap = Column(Float)
    roe = Column(Float)
    roce = Column(Float)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    dividend_yield = Column(Float)
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)

    company = relationship("Company", back_populates="fundamentals")

    __table_args__ = (
        UniqueConstraint("symbol", "snapshot_date", name="uq_fund_symbol_date"),
        Index("ix_fund_symbol_date", "symbol", "snapshot_date"),
    )
