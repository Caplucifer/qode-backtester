"""
Quick sanity test of BacktestEngine using synthetic data.
Not part of the deliverable -- just verifies engine logic before
relying on it with real scraped data.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from datetime import date
from app.services.backtest_engine import BacktestEngine, BacktestConfig, FilterRule, RankRule

np.random.seed(42)

symbols = [f"STOCK{i}" for i in range(1, 11)]
dates = pd.date_range("2020-01-01", "2021-12-31", freq="D")

# synthetic prices: random walk per stock
price_rows = []
for sym in symbols:
    price = 100 + np.random.rand() * 50
    for d in dates:
        price *= (1 + np.random.normal(0.0003, 0.015))
        price_rows.append({"symbol": sym, "date": d, "close": price})
prices_df = pd.DataFrame(price_rows)

# synthetic fundamentals: one snapshot per quarter per stock
fund_rows = []
snap_dates = pd.date_range("2019-12-01", "2021-12-01", freq="QS")
for sym in symbols:
    base_mc = np.random.uniform(1000, 9000)  # crore
    base_roce = np.random.uniform(5, 30)
    base_pat = np.random.uniform(-50, 500)
    for d in snap_dates:
        fund_rows.append({
            "symbol": sym,
            "snapshot_date": d,
            "market_cap": base_mc * (1 + np.random.normal(0, 0.05)),
            "roce": base_roce * (1 + np.random.normal(0, 0.1)),
            "pat": base_pat * (1 + np.random.normal(0, 0.1)),
            "pe_ratio": np.random.uniform(8, 40),
        })
fundamentals_df = pd.DataFrame(fund_rows)

config = BacktestConfig(
    start_date=date(2020, 1, 1),
    end_date=date(2021, 12, 1),
    rebalance_frequency="quarterly",
    portfolio_size=5,
    position_sizing="equal",
    filters=[
        FilterRule(metric="market_cap", min_value=1000, max_value=10000),
        FilterRule(metric="pat", min_value=0),
    ],
    rank_rules=[
        RankRule(metric="roce", ascending=False),
        RankRule(metric="pe_ratio", ascending=True),
    ],
    initial_capital=1_000_000,
)

engine = BacktestEngine(prices_df, fundamentals_df, config)
result = engine.run()

print("=== METRICS ===")
for k, v in result["metrics"].items():
    print(f"  {k}: {v}")

print("\n=== EQUITY CURVE (first 3, last 3) ===")
for row in result["equity_curve"][:3]:
    print(" ", row)
print("  ...")
for row in result["equity_curve"][-3:]:
    print(" ", row)

print("\n=== TOP WINNERS ===")
for row in result["top_winners"]:
    print(" ", row)

print("\n=== TOP LOSERS ===")
for row in result["top_losers"]:
    print(" ", row)

print(f"\n=== PORTFOLIO LOG SAMPLE (first 5 of {len(result['portfolio_logs'])}) ===")
for row in result["portfolio_logs"][:5]:
    print(" ", row)

# Basic assertions
assert len(result["equity_curve"]) > 0, "equity curve should not be empty"
assert result["metrics"]["final_portfolio_value"] > 0, "final value should be positive"
assert all(0.99 <= sum(p["weight"] for p in result["portfolio_logs"] if p["rebalance_date"] == rd) <= 1.01
           for rd in set(p["rebalance_date"] for p in result["portfolio_logs"])), "weights should sum to ~1 each period"

print("\n✅ ALL SANITY CHECKS PASSED")
