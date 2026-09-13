"""
Database initialisation: schema creation + seed data.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.db.base import Base
from app.db.models import LeagueRow, MatchEventRow, MatchRow, PlayerRow, TeamRow

ADMIN_EMAIL = "admin@league.com"
ADMIN_PASSWORD = "admin123"


def _dt(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _is_empty(session: Session) -> bool:
    return session.query(LeagueRow).first() is None


def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)


def seed(session: Session) -> None:
    """Insert seed data — only called when the DB is empty."""
    league = LeagueRow(
        id="league-1",
        name="Premier City League",
        season="2025/26",
        status="active",
        admin_email=ADMIN_EMAIL,
        admin_password_hash=hash_password(ADMIN_PASSWORD),
    )
    session.add(league)

    teams = [
        TeamRow(id="team-1", name="North United",   logo="⚽", league_id="league-1"),
        TeamRow(id="team-2", name="South City FC",  logo="🦁", league_id="league-1"),
        TeamRow(id="team-3", name="East Rovers",    logo="🦅", league_id="league-1"),
        TeamRow(id="team-4", name="West Athletic",  logo="🐺", league_id="league-1"),
    ]
    session.add_all(teams)

    players = [
        PlayerRow(id="player-1",  name="Alex Morgan",    jersey_number=1,  position="GK",  is_captain=False, team_id="team-1"),
        PlayerRow(id="player-2",  name="Jordan Lee",      jersey_number=9,  position="FWD", is_captain=True,  team_id="team-1"),
        PlayerRow(id="player-3",  name="Sam Rivera",      jersey_number=10, position="MID", is_captain=False, team_id="team-1"),
        PlayerRow(id="player-4",  name="Chris Park",      jersey_number=1,  position="GK",  is_captain=False, team_id="team-2"),
        PlayerRow(id="player-5",  name="Taylor Brooks",   jersey_number=7,  position="FWD", is_captain=True,  team_id="team-2"),
        PlayerRow(id="player-6",  name="Morgan Ellis",    jersey_number=6,  position="MID", is_captain=False, team_id="team-2"),
        PlayerRow(id="player-7",  name="Riley Chen",      jersey_number=11, position="FWD", is_captain=True,  team_id="team-3"),
        PlayerRow(id="player-8",  name="Casey Wright",    jersey_number=4,  position="DEF", is_captain=False, team_id="team-3"),
        PlayerRow(id="player-9",  name="Jamie Fox",       jersey_number=8,  position="MID", is_captain=True,  team_id="team-4"),
        PlayerRow(id="player-10", name="Drew Stone",      jersey_number=3,  position="DEF", is_captain=False, team_id="team-4"),
    ]
    session.add_all(players)

    matches = [
        MatchRow(id="match-1", home_team_id="team-1", away_team_id="team-2",
                 scheduled_at=_dt("2026-09-10T15:00:00.000Z"), status="finished", home_score=2, away_score=1),
        MatchRow(id="match-2", home_team_id="team-3", away_team_id="team-4",
                 scheduled_at=_dt("2026-09-11T15:00:00.000Z"), status="finished", home_score=1, away_score=1),
        MatchRow(id="match-3", home_team_id="team-1", away_team_id="team-3",
                 scheduled_at=_dt("2026-09-20T14:00:00.000Z"), status="scheduled", home_score=0, away_score=0),
        MatchRow(id="match-4", home_team_id="team-2", away_team_id="team-4",
                 scheduled_at=_dt("2026-09-21T16:30:00.000Z"), status="scheduled", home_score=0, away_score=0),
    ]
    session.add_all(matches)

    events = [
        MatchEventRow(id="event-1", match_id="match-1", team_id="team-1", player_id="player-2", event_type="goal",        minute=23, description="Header from corner"),
        MatchEventRow(id="event-2", match_id="match-1", team_id="team-2", player_id="player-5", event_type="goal",        minute=41, description="Penalty kick"),
        MatchEventRow(id="event-3", match_id="match-1", team_id="team-1", player_id="player-3", event_type="goal",        minute=78, description="Long-range strike"),
        MatchEventRow(id="event-4", match_id="match-1", team_id="team-2", player_id="player-6", event_type="yellow_card", minute=55, description="Late tackle"),
        MatchEventRow(id="event-5", match_id="match-2", team_id="team-3", player_id="player-7", event_type="goal",        minute=12, description="Tap-in"),
        MatchEventRow(id="event-6", match_id="match-2", team_id="team-4", player_id="player-9", event_type="goal",        minute=67, description="Free kick"),
    ]
    session.add_all(events)
    session.commit()


def init_db(engine: Engine) -> None:
    """Create tables and seed if the DB is empty. Safe to call on every startup."""
    create_tables(engine)
    with Session(engine) as session:
        if _is_empty(session):
            seed(session)
