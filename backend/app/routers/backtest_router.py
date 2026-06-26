"""
backtest_router.py
-------------------
REST API endpoints for running backtests and listing companies/metrics.
This satisfies the bonus "API endpoints via FastAPI" requirement and is
also what the React frontend calls.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import BacktestRequest, BacktestResponse, CompanyInfo, AvailableMetric
from app.services import data_loader
from app.services.backtest_engine import BacktestEngine, BacktestConfig, FilterRule, RankRule

router = APIRouter(prefix="/api", tags=["backtest"])


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(req: BacktestRequest, db: Session = Depends(get_db)):
    if req.start_date >= req.end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

    prices_df = data_loader.load_prices(db, req.start_date, req.end_date)
    if prices_df.empty:
        raise HTTPException(
            status_code=400,
            detail="No price data found for this date range. Did you run fetch_data.py and load_to_db.py?",
        )

    fundamentals_df = data_loader.load_fundamentals(db, req.end_date)
    if fundamentals_df.empty:
        raise HTTPException(status_code=400, detail="No fundamental data found in database.")

    config = BacktestConfig(
        start_date=req.start_date,
        end_date=req.end_date,
        rebalance_frequency=req.rebalance_frequency,
        portfolio_size=req.portfolio_size,
        position_sizing=req.position_sizing,
        sizing_metric=req.sizing_metric,
        filters=[FilterRule(**f.model_dump()) for f in req.filters],
        rank_rules=[RankRule(**r.model_dump()) for r in req.rank_rules],
        initial_capital=req.initial_capital,
    )

    engine = BacktestEngine(prices_df, fundamentals_df, config)
    result = engine.run()
    return result


@router.get("/companies", response_model=list[CompanyInfo])
def list_companies(db: Session = Depends(get_db)):
    df = data_loader.load_company_list(db)
    return df.to_dict(orient="records")


@router.get("/debug/fundamentals-summary")
def fundamentals_summary(db: Session = Depends(get_db)):
    """
    Diagnostic endpoint: returns min/max/median/null-count for every
    fundamental metric across ALL snapshots in the database.
    """
    import pandas as pd
    from datetime import date

    df = data_loader.load_fundamentals(db, date(2100, 1, 1))
    if df.empty:
        return {"error": "No fundamental data in database."}

    numeric_cols = [c for c in df.columns if c not in ("symbol", "snapshot_date")]
    summary = {}
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors="coerce")
        non_null = series.dropna()
        summary[col] = {
            "non_null_count": int(non_null.count()),
            "null_count": int(series.isna().sum()),
            "min": float(non_null.min()) if not non_null.empty else None,
            "max": float(non_null.max()) if not non_null.empty else None,
            "median": float(non_null.median()) if not non_null.empty else None,
        }

    return {
        "total_rows": len(df),
        "unique_symbols": int(df["symbol"].nunique()),
        "snapshot_date_range": [str(df["snapshot_date"].min()), str(df["snapshot_date"].max())],
        "metrics": summary,
    }


@router.get("/metrics", response_model=list[AvailableMetric])
def list_available_metrics():
    """Static list of fundamental metrics the frontend can build filters/ranks from."""
    return [
        {"name": "market_cap", "label": "Market Cap (₹ Cr)"},
        {"name": "pat", "label": "PAT (Net Profit)"},
        {"name": "roce", "label": "ROCE (%)"},
        {"name": "roe", "label": "ROE (%)"},
        {"name": "pe_ratio", "label": "P/E Ratio"},
        {"name": "pb_ratio", "label": "P/B Ratio"},
        {"name": "total_revenue", "label": "Total Revenue"},
        {"name": "total_debt", "label": "Total Debt"},
        {"name": "debt_to_equity", "label": "Debt to Equity"},
        {"name": "current_ratio", "label": "Current Ratio"},
        {"name": "dividend_yield", "label": "Dividend Yield"},
    ]
