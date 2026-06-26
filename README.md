# Qode Backtester — Fundamental Equity Strategy Backtesting Platform

An end-to-end backtesting platform for fundamental equity strategies on NSE-listed stocks. Define filters, ranking logic, position sizing, and rebalancing frequency, then visualize equity curves, drawdowns, and detailed portfolio logs.

**Stack:** Python (FastAPI, pandas, SQLAlchemy) · PostgreSQL · React + Tailwind CSS

---

## 1. Architecture Overview

qode-backtester/

├── backend/

│   ├── app/

│   │   ├── main.py              # FastAPI app entry point

│   │   ├── database.py          # SQLAlchemy engine/session (PostgreSQL, swappable to MySQL/SQLite)

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

### Data flow

yfinance API  →  fetch_data.py  →  CSV files  →  backfill_market_data.py  →  load_to_db.py  →  PostgreSQL DB

↓

FastAPI (data_loader.py)

↓

BacktestEngine (filter/rank/size)

↓

React frontend (charts/tables)

The backend deliberately separates **fetch** → **load** → **backtest** into independent stages. This means a slow scrape can be re-run without re-querying the API, and the core `BacktestEngine` class has zero knowledge of SQL — it operates purely on pandas DataFrames, so its logic can be (and was) unit-tested with synthetic data before ever touching real scraped data.

---

## 2. Setup & Run Instructions (Windows)

### Prerequisites
- Python 3.10+ ([python.org](https://www.python.org/downloads/)) — check "Add to PATH" during install
- Node.js 18+ LTS ([nodejs.org](https://nodejs.org/))
- PostgreSQL ([postgresql.org](https://www.postgresql.org/download/windows/))

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
This creates `data/raw/prices.csv` and `data/raw/fundamentals.csv`. Market cap is already saved in ₹ Crores and already backfilled onto every historical snapshot — see "Assumptions & Known Limitations" below.

**Step 2 — Load into database:**

Before running this, make sure PostgreSQL is installed and running locally, and create the database once:
```sql
CREATE DATABASE qode_backtester;
```
(Update the connection credentials in `app/database.py` if your Postgres user/password differ from the defaults.)

```bash
python scripts/load_to_db.py
```
This creates all tables in your `qode_backtester` Postgres database and loads the fetched CSVs into them.

**Step 3 — Run the API server:**
```bash
uvicorn app.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` to see interactive Swagger API docs.

> **Note:** `scripts/backfill_market_data.py` and `scripts/patch_market_cap.py` are one-off repair scripts kept in the repo for reference (they were used during development to fix an earlier data run) — they are not needed for a fresh `fetch_data.py` run, since both fixes are now built directly into `fetch_data.py`.

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

Built on SQLAlchemy, running on PostgreSQL as required by the assignment spec. Switching to MySQL (or back to SQLite for zero-setup local testing) is a one-line change to `DATABASE_URL` in `database.py` — no model or query code changes needed, since SQLAlchemy abstracts the SQL dialect.

### `backend/scripts/fetch_data.py` — data collection
Fetches daily OHLCV and multiple **historical** annual fundamental snapshots (income statement, balance sheet, cash flow) per company via `yfinance`, covering 123 NSE-listed companies across banking, IT, energy, FMCG, auto, pharma, metals, and more sectors.

### `frontend/src/components/StrategyForm.jsx` — strategy configuration UI
Lets the user set date range, rebalance frequency, portfolio size, position sizing method, an arbitrary number of filters (metric + min/max range), and an arbitrary number of ranking metrics with direction and composite weight.

---

## 4. Assumptions & Known Limitations

This section is intentionally explicit, since these are real constraints of free data sources, not bugs:

1. **Fundamental data depth**: `yfinance`'s free tier exposes roughly the last 4 years of *annual* financial statements (not quarterly), and only the company's **current** market cap, P/E, P/B, dividend yield, and current ratio (not historical). This means:
   - ROCE, ROE, PAT, revenue, and debt ratios *are* point-in-time correct across history (computed from dated financial statements).
   - Market cap and valuation ratios are NOT available historically from free data sources. We address this with `scripts/backfill_market_data.py`, which backfills each company's most recently known market cap / P/E / P/B / dividend yield / current ratio onto its older snapshots. This is a documented approximation — a 2021 rebalance technically uses 2026's market cap — but it's what makes market-cap and valuation filters usable across the whole backtest window rather than only the most recent rebalance date. A production system would replace this with a paid provider offering true historical point-in-time fundamentals (e.g. Screener.in's data API, Refinitiv, Bloomberg).

2. **Market cap filter calibration**: the assignment's example filter ("₹1000 Cr to ₹10000 Cr") is illustrative of the filter *mechanism*, not a fixed requirement — the actual range should be calibrated to the stock universe being tested. Our 123-stock universe skews large/mid-cap (real range: ₹9,228 Cr to ₹17,83,850 Cr), so we use a ₹10,000 Cr–₹3,00,000 Cr band by default to capture a meaningful slice of the universe for a proper top-20 portfolio. A narrower filter copied verbatim from the spec example would (and during testing, did) return zero qualifying stocks for this universe.

3. **Portfolio size ramps up over time, not a fixed 20 from day one**: in earlier rebalances (2020-2022), fewer companies have a dated fundamental snapshot available yet (since we only have ~4 years of annual statements per company), so the filter+rank step may return fewer than the target portfolio_size. This is the no-future-leakage rule working as intended — the engine never invents data that wasn't available on that date — and portfolios naturally fill out to the configured size as more dated snapshots become available later in the backtest window.

4. **Rebalance-to-rebalance pricing**: when a rebalance date falls on a non-trading day (weekend/holiday), the engine uses the next available trading day's closing price.

5. **No transaction costs or slippage modeled**: the backtest assumes frictionless rebalancing. This could be added as a configurable basis-point cost per trade.

6. **Survivorship bias**: the 123-stock universe is today's NSE listings; it doesn't account for companies that were delisted or merged during the backtest period.

7. **PostgreSQL chosen as the active database** per the assignment spec. The schema (`models.py`) and connection layer (`database.py`) are 100% SQLAlchemy-based, so switching to MySQL or SQLite is a one-line `DATABASE_URL` change with no other code changes.

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
| Database | PostgreSQL (MySQL/SQLite-compatible schema via SQLAlchemy) |
| Frontend | React (Vite), Tailwind CSS, Recharts, Axios |
| Data Source | Yahoo Finance via `yfinance` |