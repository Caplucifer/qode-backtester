"""
backtest_engine.py
-------------------
Core backtesting logic for fundamental equity strategies.

Pipeline for a single backtest run:
    1. Load price + fundamental data from the DB (once, for the whole
       date range -- not re-queried every rebalance, for speed).
    2. At each rebalance date:
        a. Apply FILTERS using only fundamental data dated ON OR BEFORE
           the rebalance date (no future leakage).
        b. RANK the filtered universe by one or more metrics.
        c. Pick the top N stocks.
        d. SIZE positions (equal / market-cap / metric weighted).
        e. Apply returns from this rebalance date to the next, compounding
           the portfolio value.
    3. Record equity curve, drawdown, and per-period portfolio logs.

No-future-leakage rule: when filtering/ranking "as of" date D, we only
ever look at fundamental rows where snapshot_date <= D, and price rows
up to date D. We never use information that would not have been
available to a real investor on date D.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Literal, Optional

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta


RebalanceFrequency = Literal["monthly", "quarterly", "yearly"]
PositionSizing = Literal["equal", "market_cap", "metric"]


@dataclass
class RankRule:
    metric: str                      # e.g. "roce", "pe_ratio"
    ascending: bool = False          # False = higher is better (e.g. ROE desc)
    weight: float = 1.0              # for composite ranking


@dataclass
class FilterRule:
    metric: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class BacktestConfig:
    start_date: date
    end_date: date
    rebalance_frequency: RebalanceFrequency = "quarterly"
    portfolio_size: int = 20
    position_sizing: PositionSizing = "equal"
    sizing_metric: Optional[str] = None     # required if position_sizing == "metric"
    filters: List[FilterRule] = field(default_factory=list)
    rank_rules: List[RankRule] = field(default_factory=list)
    initial_capital: float = 1_000_000.0
    benchmark_symbol: Optional[str] = "^NSEI"


def generate_rebalance_dates(start: date, end: date, freq: RebalanceFrequency) -> List[date]:
    """Generate rebalance dates from start to end at the given frequency."""
    step = {"monthly": 1, "quarterly": 3, "yearly": 12}[freq]
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current = current + relativedelta(months=step)
    return dates


class BacktestEngine:
    """
    Runs a fundamental-strategy backtest over historical price + fundamental
    data already loaded into pandas DataFrames (queried from the DB by the
    caller -- see app/services/data_loader.py).
    """

    def __init__(self, prices_df: pd.DataFrame, fundamentals_df: pd.DataFrame, config: BacktestConfig):
        """
        prices_df columns: symbol, date, close   (date is a pandas Timestamp)
        fundamentals_df columns: symbol, snapshot_date, market_cap, roce, pat, ... (any metric)
        """
        self.prices = prices_df.copy()
        self.fundamentals = fundamentals_df.copy()
        self.config = config

        self.prices["date"] = pd.to_datetime(self.prices["date"])
        self.fundamentals["snapshot_date"] = pd.to_datetime(self.fundamentals["snapshot_date"])

        # Pivot prices for fast lookup: index=date, columns=symbol, values=close
        self._price_pivot = self.prices.pivot_table(
            index="date", columns="symbol", values="close", aggfunc="last"
        ).sort_index()

    # ---------- Step a: filtering ----------
    def _get_fundamentals_as_of(self, as_of: pd.Timestamp) -> pd.DataFrame:
        """
        Returns the most recent fundamental snapshot for each symbol where
        snapshot_date <= as_of. This is the no-future-leakage guarantee:
        we never see a fundamental row dated after `as_of`.
        """
        eligible = self.fundamentals[self.fundamentals["snapshot_date"] <= as_of]
        if eligible.empty:
            return eligible
        # take the latest snapshot per symbol up to this date
        latest_idx = eligible.groupby("symbol")["snapshot_date"].idxmax()
        return eligible.loc[latest_idx].reset_index(drop=True)

    def _apply_filters(self, fund_snapshot: pd.DataFrame) -> pd.DataFrame:
        df = fund_snapshot.copy()
        for rule in self.config.filters:
            if rule.metric not in df.columns:
                continue
            if rule.min_value is not None:
                df = df[df[rule.metric] >= rule.min_value]
            if rule.max_value is not None:
                df = df[df[rule.metric] <= rule.max_value]
        return df

    # ---------- Step b: ranking ----------
    def _apply_ranking(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or not self.config.rank_rules:
            return df

        df = df.copy()
        rank_cols = []
        for rule in self.config.rank_rules:
            if rule.metric not in df.columns:
                continue
            col_name = f"_rank_{rule.metric}"
            df[col_name] = df[rule.metric].rank(ascending=rule.ascending, method="average") * rule.weight
            rank_cols.append(col_name)

        if not rank_cols:
            return df

        # Composite rank score = average of individual (weighted) ranks.
        # Lower composite score = better (rank 1 = best on that metric).
        df["composite_rank"] = df[rank_cols].mean(axis=1)
        df = df.sort_values("composite_rank", ascending=True)
        return df

    # ---------- Step c+d: select + size ----------
    def _select_and_size(self, ranked_df: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
        top_n = ranked_df.head(self.config.portfolio_size).copy()
        if top_n.empty:
            return top_n

        # Only keep stocks that actually have a price on/near this date
        available_symbols = self._price_pivot.columns
        top_n = top_n[top_n["symbol"].isin(available_symbols)]
        if top_n.empty:
            return top_n

        sizing = self.config.position_sizing
        if sizing == "equal":
            top_n["weight"] = 1.0 / len(top_n)
        elif sizing == "market_cap":
            total = top_n["market_cap"].sum()
            top_n["weight"] = top_n["market_cap"] / total if total else 1.0 / len(top_n)
        elif sizing == "metric":
            metric = self.config.sizing_metric
            if metric not in top_n.columns or top_n[metric].sum() == 0:
                top_n["weight"] = 1.0 / len(top_n)
            else:
                # shift to ensure positivity before weighting, in case metric has negatives
                shifted = top_n[metric] - min(0, top_n[metric].min())
                total = shifted.sum()
                top_n["weight"] = shifted / total if total else 1.0 / len(top_n)
        return top_n

    def _get_price_on_or_after(self, symbol: str, target_date: pd.Timestamp) -> Optional[float]:
        """Find the closest available trading price on/after target_date (handles holidays)."""
        if symbol not in self._price_pivot.columns:
            return None
        series = self._price_pivot[symbol].dropna()
        future_prices = series[series.index >= target_date]
        if future_prices.empty:
            return None
        return future_prices.iloc[0]

    # ---------- Main run loop ----------
    def run(self) -> dict:
        rebalance_dates = generate_rebalance_dates(
            self.config.start_date, self.config.end_date, self.config.rebalance_frequency
        )

        portfolio_value = self.config.initial_capital
        equity_curve = []   # list of {date, value}
        portfolio_logs = []  # list of {rebalance_date, symbol, weight, entry_price, exit_price, period_return}

        for i, rebal_date in enumerate(rebalance_dates):
            rebal_ts = pd.Timestamp(rebal_date)
            next_ts = pd.Timestamp(rebalance_dates[i + 1]) if i + 1 < len(rebalance_dates) else pd.Timestamp(self.config.end_date)

            fund_snapshot = self._get_fundamentals_as_of(rebal_ts)
            filtered = self._apply_filters(fund_snapshot)
            ranked = self._apply_ranking(filtered)
            picks = self._select_and_size(ranked, rebal_ts)

            if picks.empty:
                equity_curve.append({"date": rebal_ts, "value": portfolio_value})
                continue

            period_return = 0.0
            for _, pick in picks.iterrows():
                symbol = pick["symbol"]
                entry_price = self._get_price_on_or_after(symbol, rebal_ts)
                exit_price = self._get_price_on_or_after(symbol, next_ts)

                if entry_price is None or exit_price is None or entry_price == 0:
                    stock_return = 0.0
                else:
                    stock_return = (exit_price - entry_price) / entry_price

                period_return += pick["weight"] * stock_return

                portfolio_logs.append({
                    "rebalance_date": rebal_ts.strftime("%Y-%m-%d"),
                    "symbol": symbol,
                    "weight": round(float(pick["weight"]), 4),
                    "entry_price": round(float(entry_price), 2) if entry_price is not None else None,
                    "exit_price": round(float(exit_price), 2) if exit_price is not None else None,
                    "stock_return": round(float(stock_return), 4),
                })

            portfolio_value *= (1 + period_return)
            equity_curve.append({"date": rebal_ts, "value": portfolio_value})

        return self._compute_results(equity_curve, portfolio_logs)

    # ---------- Metrics ----------
    def _compute_results(self, equity_curve: list, portfolio_logs: list) -> dict:
        if not equity_curve:
            return {"equity_curve": [], "drawdown": [], "metrics": {}, "portfolio_logs": [], "top_winners": [], "top_losers": []}

        eq_df = pd.DataFrame(equity_curve)
        eq_df["date"] = pd.to_datetime(eq_df["date"])
        eq_df = eq_df.sort_values("date").reset_index(drop=True)
        eq_df["returns"] = eq_df["value"].pct_change().fillna(0)

        # Drawdown
        eq_df["running_max"] = eq_df["value"].cummax()
        eq_df["drawdown"] = (eq_df["value"] - eq_df["running_max"]) / eq_df["running_max"]

        # CAGR
        n_years = max((eq_df["date"].iloc[-1] - eq_df["date"].iloc[0]).days / 365.25, 1e-6)
        final_value = eq_df["value"].iloc[-1]
        initial_value = self.config.initial_capital
        cagr = (final_value / initial_value) ** (1 / n_years) - 1 if initial_value > 0 else 0

        # Sharpe (annualized, using rebalance-period returns; risk-free rate assumed 0 for simplicity)
        freq_per_year = {"monthly": 12, "quarterly": 4, "yearly": 1}[self.config.rebalance_frequency]
        mean_ret = eq_df["returns"].mean()
        std_ret = eq_df["returns"].std()
        sharpe = (mean_ret / std_ret) * np.sqrt(freq_per_year) if std_ret and std_ret > 0 else 0.0

        max_drawdown = eq_df["drawdown"].min()

        metrics = {
            "cagr": round(float(cagr) * 100, 2),
            "sharpe_ratio": round(float(sharpe), 2),
            "max_drawdown": round(float(max_drawdown) * 100, 2),
            "final_portfolio_value": round(float(final_value), 2),
            "total_return_pct": round(float((final_value / initial_value - 1) * 100), 2),
            "num_rebalances": len(eq_df),
        }

        # Top winners / losers across all logged positions
        logs_df = pd.DataFrame(portfolio_logs)
        top_winners, top_losers = [], []
        if not logs_df.empty:
            agg = logs_df.groupby("symbol")["stock_return"].mean().sort_values(ascending=False)
            top_winners = [
                {"symbol": s, "stock_return": round(float(r), 4)}
                for s, r in agg.head(5).items()
            ]
            top_losers = [
                {"symbol": s, "stock_return": round(float(r), 4)}
                for s, r in agg.tail(5).sort_values().items()
            ]

        return {
            "equity_curve": [
                {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 2)}
                for d, v in zip(eq_df["date"], eq_df["value"])
            ],
            "drawdown": [
                {"date": d.strftime("%Y-%m-%d"), "drawdown_pct": round(float(dd) * 100, 2)}
                for d, dd in zip(eq_df["date"], eq_df["drawdown"])
            ],
            "metrics": metrics,
            "portfolio_logs": portfolio_logs,
            "top_winners": top_winners,
            "top_losers": top_losers,
        }
