"""
Database engine factory.

The connection string is read from the DATABASE_URL environment variable.
It defaults to a local SQLite file so the server works out-of-the-box.

Examples
--------
SQLite (default, file on disk):
    DATABASE_URL=sqlite:///./scoreboard.db

SQLite in-memory (useful for tests):
    DATABASE_URL=sqlite:///:memory:

PostgreSQL:
    DATABASE_URL=postgresql+psycopg2://user:password@localhost/scoreboard
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

load_dotenv()

_DEFAULT_URL = "sqlite:///./scoreboard.db"


def _build_engine(url: str) -> Engine:
    kwargs: dict = {}
    # SQLite requires check_same_thread=False when used with FastAPI/threading.
    # Other dialects (e.g. PostgreSQL) do not support or need this argument.
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        # In-memory SQLite needs StaticPool so all connections share the same database
        if url in ("sqlite://", "sqlite:///:memory:"):
            kwargs["poolclass"] = StaticPool
    return create_engine(url, **kwargs)


def get_engine() -> Engine:
    url = os.environ.get("DATABASE_URL", _DEFAULT_URL)
    return _build_engine(url)


def build_engine(url: str) -> Engine:
    """Build an engine from an explicit URL — used by tests."""
    return _build_engine(url)
