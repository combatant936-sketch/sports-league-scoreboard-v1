"""
SQLAlchemy session dependency for FastAPI.

`get_session` is a generator dependency that provides one Session per
request, commits on success, and rolls back on any exception.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.db.engine import get_engine

# Module-level session factory, initialised lazily on first use.
# Tests override this via app.db.session.SessionLocal directly.
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=get_engine(), autocommit=False, autoflush=False
)


def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
