"""
main.py
-------
FastAPI application entry point.

Run from the backend/ directory:
    uvicorn app.main:app --reload --port 8000

Then visit http://localhost:8000/docs for interactive API docs (Swagger UI).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import backtest_router

app = FastAPI(
    title="Qode Backtesting Framework API",
    description="Backend API for the equity fundamental-strategy backtesting platform.",
    version="1.0.0",
)

# Allow the React dev server (default Vite port 5173, CRA port 3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(backtest_router.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "message": "Qode Backtesting API is running. See /docs for API documentation."}
