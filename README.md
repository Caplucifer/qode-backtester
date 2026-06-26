# Qode Backtester — Fundamental Equity Strategy Backtesting Platform

An end-to-end backtesting platform for fundamental equity strategies on NSE-listed stocks. Define filters, ranking logic, position sizing, and rebalancing frequency, then visualize equity curves, drawdowns, and detailed portfolio logs.

**Stack:** Python (FastAPI, pandas, SQLAlchemy) · SQLite · React + Tailwind CSS

---

## 1. Architecture Overview

```
qode-backtester/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # SQLAlchemy engine/session (SQLite, Postgres-ready)
│   │   ├── models.py            # ORM models: Company, StockPrice, StockFundamental
│   │   ├── schemas.py           # Pydantic request/response contracts
│   │   ├── data/
│   │   │   └── universe.py      # List of 123 NSE stock symbols
│   │   ├── services/
│   │   │   ├── backtest_engine.py  # Core backtest logic (filter → rank → size → compound)
│   │   │   └── data_loader.py      # DB → pandas DataFrame bridge
│   │   └── routers/
│   │       └── backtest_router.py  # REST endpoints
│   ├── scripts/
│   │   ├── fetch_data.py        # Scrapes price + fundamental data via yfinance
│   │   └── load_to_db.py        # Loads CSVs into the database
│   ├── data/raw/                # Output of fetch_data.py (prices.csv, fundamentals.csv)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx               # Main layout
    │   ├── api.js                # Axios client
    │   └── components/
    │       ├── StrategyForm.jsx      # Configure filters, ranking, sizing
    │       ├── MetricsCards.jsx      # CAGR, Sharpe, Max DD, etc.
    │       ├── EquityCurveChart.jsx
    │       ├── DrawdownChart.jsx
    │       ├── WinnersLosers.jsx
    │       └── PortfolioLogTable.jsx # Paginated logs + CSV/Excel export
    └── package.json
```

### Data flow

```
yfinance API  →  fetch_data.py  →  CSV files  →  load_to_db.py  →  SQLite DB
                                                                       ↓
                                                          FastAPI (data_loader.py)
                                                                       ↓
                                                       BacktestEngine (filter/rank/size)
                                                                       ↓
                                                        React frontend (charts/tables)
```

The backend deliberately separates **fetch** → **load** → **backtest** into independent stages. This means a slow scrape can be re-run without re-querying the API, and the core `BacktestEngine` class has zero knowledge of SQL — it operates purely on pandas DataFrames, so its logic can be (and was) unit-tested with synthetic data before ever touching real scraped data.

---

## 2. Setup & Run Instructions (Windows)

### Prerequisites
- Python 3.10+ ([python.org](https://www.python.org/downloads/)) — check "Add to PATH" during install
- Node.js 18+ LTS ([nodejs.org](https://nodejs.org/))

### Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Step 1 — Fetch data** (takes ~10-20 minutes for 123 stocks, be patient, it sleeps between API calls to avoid throttling):
```bash
python scripts/fetch_data.py
```
This creates `data/raw/prices.csv` and `data/raw/fundamentals.csv`.

**Step 2 — Load into database:**
```bash
python scripts/load_to_db.py
```
This creates `qode_backtester.db` (SQLite file) in the `backend/` folder.

**Step 3 — Run the API server:**
```bash
uvicorn app.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` to see interactive Swagger API docs.

### Frontend setup

In a **new** terminal:
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:5173` in your browser.

---

## 3. Module Descriptions

### `backend/app/services/backtest_engine.py` — the core logic
Implements the full pipeline per the assignment spec:
- **Filtering**: applied once per rebalance using only fundamental data dated on or before the rebalance date (prevents future-data leakage).
- **Ranking**: single or composite (multi-metric averaged rank), ascending or descending per metric.
- **Position sizing**: equal-weighted, market-cap-weighted, or metric-weighted.
- **Compounding**: portfolio value compounds at each rebalance based on the weighted return of the period.
- **Metrics**: CAGR, Sharpe ratio (annualized using the rebalance frequency), max drawdown, total return.

### `backend/app/database.py` + `models.py` — schema
Three normalized tables:
- `companies` — static lookup (symbol, name, sector, industry)
- `stock_prices` — daily OHLCV, indexed on `(symbol, date)`
- `stock_fundamentals` — fundamental snapshots, indexed on `(symbol, snapshot_date)`

Built on SQLAlchemy so switching from SQLite to PostgreSQL/MySQL is a one-line change to `DATABASE_URL` in `database.py` — no model or query code changes needed.

### `backend/scripts/fetch_data.py` — data collection
Fetches daily OHLCV and multiple **historical** annual fundamental snapshots (income statement, balance sheet, cash flow) per company via `yfinance`, covering 123 NSE-listed companies across banking, IT, energy, FMCG, auto, pharma, metals, and more sectors.

### `frontend/src/components/StrategyForm.jsx` — strategy configuration UI
Lets the user set date range, rebalance frequency, portfolio size, position sizing method, an arbitrary number of filters (metric + min/max range), and an arbitrary number of ranking metrics with direction and composite weight.

---

## 4. Assumptions & Known Limitations

This section is intentionally explicit, since these are real constraints of free data sources, not bugs:

1. **Fundamental data depth**: `yfinance`'s free tier exposes roughly the last 4 years of *annual* financial statements (not quarterly), and only the company's **current** market cap, P/E, P/B, and dividend yield (not historical). This means:
   - ROCE, ROE, PAT, revenue, debt ratios *are* point-in-time correct across history (computed from dated financial statements).
   - Market cap and valuation ratios (P/E, P/B, dividend yield) are only accurate for the most recent rebalance dates, since historical values aren't available without a paid data provider.
   - For a production system, this would be replaced with a paid fundamentals API (e.g., Screener.in's data, Refinitiv, or Bloomberg) that has true historical point-in-time fundamentals.

2. **Rebalance-to-rebalance pricing**: when a rebalance date falls on a non-trading day (weekend/holiday), the engine uses the next available trading day's closing price.

3. **No transaction costs or slippage modeled**: the backtest assumes frictionless rebalancing. This could be added as a configurable basis-point cost per trade.

4. **Survivorship bias**: the 123-stock universe is today's NSE listings; it doesn't account for companies that were delisted or merged during the backtest period.

5. **SQLite instead of PostgreSQL/MySQL**: chosen for zero-setup local development. The schema is 100% portable — see `database.py` for the one-line swap.

---

## 5. Optional / Bonus Features Implemented

- ✅ FastAPI REST API (`/api/backtest`, `/api/metrics`, `/api/companies`) — interactive docs at `/docs`
- ⬜ Prebuilt strategy presets (not implemented — see "Future Work")
- ⬜ Strategy comparison view (not implemented — see "Future Work")
- ⬜ Benchmark comparison vs Nifty 50 (not implemented — see "Future Work")

## 6. Future Work

Given more time, the next additions would be:
- Benchmark overlay (Nifty 50) on the equity curve for relative performance comparison
- A "save strategy" feature to compare 2-3 strategies side-by-side
- Quarterly (not just annual) fundamental snapshots via a paid data provider for finer-grained point-in-time accuracy
- Transaction cost modeling

---

## 7. Tech Stack Summary

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, pandas, NumPy, SQLAlchemy |
| Database | SQLite (Postgres/MySQL-ready schema) |
| Frontend | React (Vite), Tailwind CSS, Recharts, Axios |
| Data Source | Yahoo Finance via `yfinance` |
