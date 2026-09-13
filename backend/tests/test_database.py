import os
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.engine import _build_engine, get_engine
from app.db.init import _is_empty, init_db
from app.db.models import LeagueRow


def test_build_engine_sqlite_has_correct_args():
    engine = _build_engine("sqlite:///:memory:")
    # SQLite in-memory uses StaticPool
    assert engine.url.drivername == "sqlite"
    assert isinstance(engine.pool, StaticPool)


def test_build_engine_non_sqlite_url():
    # Verify that for non-sqlite URLs, connect_args check_same_thread is omitted
    with patch("app.db.engine.create_engine") as mock_create:
        _build_engine("postgresql+psycopg2://user:password@localhost:5432/scoreboard")
        mock_create.assert_called_once_with(
            "postgresql+psycopg2://user:password@localhost:5432/scoreboard"
        )


def test_get_engine_reads_env_var():
    with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///./custom_test.db"}):
        engine = get_engine()
        assert "custom_test.db" in str(engine.url)


def test_init_db_idempotent():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)

    with Session(engine) as session:
        assert not _is_empty(session)
        first_count = session.query(LeagueRow).count()
        assert first_count == 1

    # Calling init_db again should not duplicate rows
    init_db(engine)
    with Session(engine) as session:
        assert session.query(LeagueRow).count() == 1
