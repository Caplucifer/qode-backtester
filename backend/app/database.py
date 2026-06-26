"""
database.py
-----------
Database connection setup using SQLAlchemy.

Currently configured for SQLite (zero-install, file-based) so this
project runs immediately with no external database server. The schema
in models.py uses only standard SQLAlchemy types, so switching to
PostgreSQL or MySQL later is a ONE-LINE change to DATABASE_URL below
(plus `pip install psycopg2-binary` or `pip install pymysql`).

Example Postgres URL (commented out):
    postgresql://username:password@localhost:5432/qode_backtester

Example MySQL URL (commented out):
    mysql+pymysql://username:password@localhost:3306/qode_backtester
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_PATH = os.path.join(BASE_DIR, "qode_backtester.db")

DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
# DATABASE_URL = "postgresql://postgres:password@localhost:5432/qode_backtester"

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
