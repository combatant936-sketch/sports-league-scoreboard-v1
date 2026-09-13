"""
Public store API.

`get_db` is the FastAPI dependency that all routers use.
It yields a `Database` instance backed by the current request's Session.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.engine import get_engine
from app.db.init import seed
from app.db.session import get_session
from app.store.database import Database


def get_db(session: Annotated[Session, Depends(get_session)]) -> Generator[Database, None, None]:
    yield Database(session)


def reset_store(engine: Optional[Engine] = None) -> None:
    """Reset DB schema and seed data. Useful for testing and backward compatibility."""
    if engine is None:
        engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        seed(session)


__all__ = ["get_db", "Database", "reset_store"]
