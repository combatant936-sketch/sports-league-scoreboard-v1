"""
SQLAlchemy ORM table definitions.

All enum values are stored as plain strings so they are compatible with
both SQLite and PostgreSQL without needing database-level enum types.
Datetime columns use timezone=True; SQLite stores them as TEXT in ISO-8601,
while PostgreSQL stores them as TIMESTAMPTZ.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LeagueRow(Base):
    __tablename__ = "leagues"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    season: Mapped[str] = mapped_column(String, nullable=False)
    # LeagueStatus value, e.g. "active"
    status: Mapped[str] = mapped_column(String, nullable=False)
    admin_email: Mapped[str] = mapped_column(String, nullable=False)
    admin_password_hash: Mapped[str] = mapped_column(String, nullable=False)

    teams: Mapped[list[TeamRow]] = relationship("TeamRow", back_populates="league")


class TeamRow(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    logo: Mapped[str] = mapped_column(String, nullable=False)
    league_id: Mapped[str] = mapped_column(String, ForeignKey("leagues.id"), nullable=False)

    league: Mapped[LeagueRow] = relationship("LeagueRow", back_populates="teams")
    players: Mapped[list[PlayerRow]] = relationship("PlayerRow", back_populates="team")


class PlayerRow(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    jersey_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # PlayerPosition value, e.g. "GK"
    position: Mapped[str] = mapped_column(String, nullable=False)
    is_captain: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    team_id: Mapped[str] = mapped_column(String, ForeignKey("teams.id"), nullable=False)

    team: Mapped[TeamRow] = relationship("TeamRow", back_populates="players")


class MatchRow(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    home_team_id: Mapped[str] = mapped_column(String, ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[str] = mapped_column(String, ForeignKey("teams.id"), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # MatchStatus value, e.g. "scheduled"
    status: Mapped[str] = mapped_column(String, nullable=False)
    home_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    events: Mapped[list[MatchEventRow]] = relationship(
        "MatchEventRow", back_populates="match", cascade="all, delete-orphan"
    )


class MatchEventRow(Base):
    __tablename__ = "match_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    match_id: Mapped[str] = mapped_column(String, ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[str] = mapped_column(String, nullable=False)
    player_id: Mapped[str] = mapped_column(String, nullable=False)
    # EventType value, e.g. "goal"
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    player_in_id: Mapped[str | None] = mapped_column(String, nullable=True)
    player_out_id: Mapped[str | None] = mapped_column(String, nullable=True)

    match: Mapped[MatchRow] = relationship("MatchRow", back_populates="events")
