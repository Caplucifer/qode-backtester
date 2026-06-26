"""
schemas.py
----------
Pydantic models defining the FastAPI request/response contracts.
These mirror the dataclasses in backtest_engine.py but add validation
suitable for incoming JSON from the React frontend.
"""

from datetime import date
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class FilterRuleSchema(BaseModel):
    metric: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class RankRuleSchema(BaseModel):
    metric: str
    ascending: bool = False
    weight: float = 1.0


class BacktestRequest(BaseModel):
    start_date: date
    end_date: date
    rebalance_frequency: Literal["monthly", "quarterly", "yearly"] = "quarterly"
    portfolio_size: int = Field(default=20, gt=0, le=100)
    position_sizing: Literal["equal", "market_cap", "metric"] = "equal"
    sizing_metric: Optional[str] = None
    filters: List[FilterRuleSchema] = []
    rank_rules: List[RankRuleSchema] = []
    initial_capital: float = Field(default=1_000_000.0, gt=0)


class EquityPoint(BaseModel):
    date: str
    value: float


class DrawdownPoint(BaseModel):
    date: str
    drawdown_pct: float


class PortfolioLogEntry(BaseModel):
    rebalance_date: str
    symbol: str
    weight: float
    entry_price: Optional[float]
    exit_price: Optional[float]
    stock_return: float


class SymbolReturn(BaseModel):
    symbol: str
    stock_return: float


class BacktestMetrics(BaseModel):
    cagr: float
    sharpe_ratio: float
    max_drawdown: float
    final_portfolio_value: float
    total_return_pct: float
    num_rebalances: int


class BacktestResponse(BaseModel):
    equity_curve: List[EquityPoint]
    drawdown: List[DrawdownPoint]
    metrics: BacktestMetrics
    portfolio_logs: List[PortfolioLogEntry]
    top_winners: List[SymbolReturn]
    top_losers: List[SymbolReturn]


class AvailableMetric(BaseModel):
    name: str
    label: str


class CompanyInfo(BaseModel):
    symbol: str
    company_name: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
