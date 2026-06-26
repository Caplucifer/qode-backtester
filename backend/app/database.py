"""
database.py
-----------
Database connection setup using SQLAlchemy.

Configured for PostgreSQL (per the assignment spec, which asks for
PostgreSQL or MySQL). Update the credentials below to match your local
Postgres setup -- everything else (models, queries, the backtest
engine) is unchanged, since SQLAlchemy abstracts the actual SQL
dialect.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_PATH = os.path.join(BASE_DIR, "qode_backtester.db")

# ---- PostgreSQL (active) ----
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "abhang123")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "qode_backtester")

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ---- SQLite (fallback for quick local testing, zero setup) ----
# DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

# ---- MySQL (alternative) ----
# DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/qode_backtester"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Safe to call repeatedly -- no-ops if tables exist."""
    from app import models  # noqa: F401 (ensures models are registered)
    Base.metadata.create_all(bind=engine)