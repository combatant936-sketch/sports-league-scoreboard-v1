"""
Database-backed store.

`Database` exposes exactly the same public methods as the old in-memory
`Store`, so all routers continue to work unchanged — only their dependency
injection wiring is updated.

Raises the same exception types as before:
  - LookupError  →  404 in routers
  - ValueError   →  400 in routers
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.auth.password import verify_password
from app.db.models import LeagueRow, MatchEventRow, MatchRow, PlayerRow, TeamRow
from app.models.schemas import (
    CreateEventInput,
    CreateMatchInput,
    CreatePlayerInput,
    CreateTeamInput,
    EventType,
    League,
    MatchEvent,
    MatchStatus,
    Player,
    StandingRow,
    Team,
    UpdateLeagueInput,
    UpdateMatchInput,
    UpdatePlayerInput,
    UpdateTeamInput,
)
from app.models.schemas import Match as MatchSchema
from app.store.standings import calculate_standings


def _next_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ── Row → Pydantic schema helpers ─────────────────────────────────────────────

def _league_schema(row: LeagueRow) -> League:
    return League.model_validate(row, from_attributes=True)


def _team_schema(row: TeamRow) -> Team:
    return Team.model_validate(row, from_attributes=True)


def _player_schema(row: PlayerRow) -> Player:
    return Player.model_validate(row, from_attributes=True)


def _match_schema(row: MatchRow) -> MatchSchema:
    return MatchSchema.model_validate(row, from_attributes=True)


def _event_schema(row: MatchEventRow) -> MatchEvent:
    return MatchEvent.model_validate(row, from_attributes=True)


# ── Database class ────────────────────────────────────────────────────────────

class Database:
    def __init__(self, session: Session) -> None:
        self._s = session

    # ── Auth ──────────────────────────────────────────────────────────────────

    def verify_admin(self, email: str, password: str) -> bool:
        league = self._s.query(LeagueRow).first()
        if league is None:
            return False
        return email == league.admin_email and verify_password(password, league.admin_password_hash)

    # ── League ────────────────────────────────────────────────────────────────

    def get_league(self) -> League:
        row = self._s.query(LeagueRow).first()
        if row is None:
            raise LookupError("League not found")
        return _league_schema(row)

    def update_league(self, data: UpdateLeagueInput) -> League:
        row = self._s.query(LeagueRow).first()
        if row is None:
            raise LookupError("League not found")
        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(row, key, value.value if hasattr(value, "value") else value)
        self._s.flush()
        return _league_schema(row)

    # ── Teams ─────────────────────────────────────────────────────────────────

    def list_teams(self) -> list[Team]:
        rows = self._s.query(TeamRow).all()
        return [_team_schema(r) for r in rows]

    def get_team(self, team_id: str) -> Team:
        row = self._s.get(TeamRow, team_id)
        if row is None:
            raise LookupError("Team not found")
        return _team_schema(row)

    def _get_team_row(self, team_id: str) -> TeamRow:
        row = self._s.get(TeamRow, team_id)
        if row is None:
            raise LookupError("Team not found")
        return row

    def create_team(self, data: CreateTeamInput) -> Team:
        league = self._s.query(LeagueRow).first()
        if league is None:
            raise LookupError("League not found")
        row = TeamRow(id=_next_id("team"), name=data.name, logo=data.logo, league_id=league.id)
        self._s.add(row)
        self._s.flush()
        return _team_schema(row)

    def update_team(self, team_id: str, data: UpdateTeamInput) -> Team:
        row = self._get_team_row(team_id)
        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(row, key, value)
        self._s.flush()
        return _team_schema(row)

    def delete_team(self, team_id: str) -> None:
        row = self._get_team_row(team_id)
        has_players = self._s.query(PlayerRow).filter_by(team_id=team_id).first() is not None
        if has_players:
            raise ValueError("Cannot delete team with assigned players")
        in_match = (
            self._s.query(MatchRow)
            .filter(
                (MatchRow.home_team_id == team_id) | (MatchRow.away_team_id == team_id)
            )
            .first()
            is not None
        )
        if in_match:
            raise ValueError("Cannot delete team referenced in matches")
        self._s.delete(row)
        self._s.flush()

    # ── Players ───────────────────────────────────────────────────────────────

    def list_players(self, team_id: Optional[str] = None) -> list[Player]:
        q = self._s.query(PlayerRow)
        if team_id:
            q = q.filter_by(team_id=team_id)
        return [_player_schema(r) for r in q.all()]

    def get_player(self, player_id: str) -> Player:
        row = self._s.get(PlayerRow, player_id)
        if row is None:
            raise LookupError("Player not found")
        return _player_schema(row)

    def _get_player_row(self, player_id: str) -> PlayerRow:
        row = self._s.get(PlayerRow, player_id)
        if row is None:
            raise LookupError("Player not found")
        return row

    def _demote_captains(self, team_id: str, except_id: Optional[str] = None) -> None:
        q = self._s.query(PlayerRow).filter_by(team_id=team_id, is_captain=True)
        if except_id:
            q = q.filter(PlayerRow.id != except_id)
        for p in q.all():
            p.is_captain = False

    def create_player(self, data: CreatePlayerInput) -> Player:
        self._get_team_row(data.team_id)
        row = PlayerRow(
            id=_next_id("player"),
            name=data.name,
            jersey_number=data.jersey_number,
            position=data.position.value if hasattr(data.position, "value") else str(data.position),
            is_captain=data.is_captain,
            team_id=data.team_id,
        )
        if row.is_captain:
            self._demote_captains(row.team_id)
        self._s.add(row)
        self._s.flush()
        return _player_schema(row)

    def update_player(self, player_id: str, data: UpdatePlayerInput) -> Player:
        row = self._get_player_row(player_id)
        updates = data.model_dump(exclude_unset=True)
        if "team_id" in updates:
            self._get_team_row(updates["team_id"])
        for key, value in updates.items():
            setattr(row, key, value.value if hasattr(value, "value") else value)
        if row.is_captain:
            self._demote_captains(row.team_id, except_id=player_id)
        self._s.flush()
        return _player_schema(row)

    def delete_player(self, player_id: str) -> None:
        row = self._get_player_row(player_id)
        in_event = (
            self._s.query(MatchEventRow)
            .filter(
                (MatchEventRow.player_id == player_id)
                | (MatchEventRow.player_in_id == player_id)
                | (MatchEventRow.player_out_id == player_id)
            )
            .first()
            is not None
        )
        if in_event:
            raise ValueError("Cannot delete player referenced in match events")
        self._s.delete(row)
        self._s.flush()

    # ── Matches ───────────────────────────────────────────────────────────────

    def list_matches(self, status: Optional[MatchStatus] = None) -> list[MatchSchema]:
        q = self._s.query(MatchRow)
        if status is not None:
            status_val = status.value if hasattr(status, "value") else str(status)
            q = q.filter_by(status=status_val)
        rows = q.order_by(MatchRow.scheduled_at.desc()).all()
        return [_match_schema(r) for r in rows]

    def get_match(self, match_id: str) -> MatchSchema:
        row = self._s.get(MatchRow, match_id)
        if row is None:
            raise LookupError("Match not found")
        return _match_schema(row)

    def _get_match_row(self, match_id: str) -> MatchRow:
        row = self._s.get(MatchRow, match_id)
        if row is None:
            raise LookupError("Match not found")
        return row

    def create_match(self, data: CreateMatchInput) -> MatchSchema:
        if data.home_team_id == data.away_team_id:
            raise ValueError("Home and away teams must be different")
        self._get_team_row(data.home_team_id)
        self._get_team_row(data.away_team_id)
        row = MatchRow(
            id=_next_id("match"),
            home_team_id=data.home_team_id,
            away_team_id=data.away_team_id,
            scheduled_at=data.scheduled_at,
            status=MatchStatus.SCHEDULED.value,
            home_score=0,
            away_score=0,
        )
        self._s.add(row)
        self._s.flush()
        return _match_schema(row)

    def update_match(self, match_id: str, data: UpdateMatchInput) -> MatchSchema:
        row = self._get_match_row(match_id)
        if row.status != MatchStatus.SCHEDULED.value:
            raise ValueError("Only scheduled matches can be updated")
        updates = data.model_dump(exclude_unset=True)
        if "home_team_id" in updates:
            self._get_team_row(updates["home_team_id"])
        if "away_team_id" in updates:
            self._get_team_row(updates["away_team_id"])
        for key, value in updates.items():
            setattr(row, key, value.value if hasattr(value, "value") else value)
        self._s.flush()
        return _match_schema(row)

    def start_match(self, match_id: str) -> MatchSchema:
        row = self._get_match_row(match_id)
        if row.status != MatchStatus.SCHEDULED.value:
            raise ValueError("Only scheduled matches can be started")
        row.status = MatchStatus.LIVE.value
        self._s.flush()
        return _match_schema(row)

    def cancel_match(self, match_id: str) -> MatchSchema:
        row = self._get_match_row(match_id)
        if row.status == MatchStatus.FINISHED.value:
            raise ValueError("Finished matches cannot be cancelled")
        row.status = MatchStatus.CANCELLED.value
        row.home_score = 0
        row.away_score = 0
        # Delete all match events
        for event in self._s.query(MatchEventRow).filter_by(match_id=match_id).all():
            self._s.delete(event)
        self._s.flush()
        return _match_schema(row)

    def finish_match(self, match_id: str) -> MatchSchema:
        row = self._get_match_row(match_id)
        if row.status != MatchStatus.LIVE.value:
            raise ValueError("Only live matches can be finished")
        row.status = MatchStatus.FINISHED.value
        self._s.flush()
        return _match_schema(row)

    # ── Match Events ──────────────────────────────────────────────────────────

    def list_events(self, match_id: str) -> list[MatchEvent]:
        self._get_match_row(match_id)
        rows = (
            self._s.query(MatchEventRow)
            .filter_by(match_id=match_id)
            .order_by(MatchEventRow.minute)
            .all()
        )
        return [_event_schema(r) for r in rows]

    def _recalculate_score(self, match_row: MatchRow) -> None:
        goals = (
            self._s.query(MatchEventRow)
            .filter_by(match_id=match_row.id, event_type=EventType.GOAL.value)
            .all()
        )
        match_row.home_score = sum(1 for g in goals if g.team_id == match_row.home_team_id)
        match_row.away_score = sum(1 for g in goals if g.team_id == match_row.away_team_id)

    def add_event(self, match_id: str, data: CreateEventInput) -> MatchEvent:
        match_row = self._get_match_row(match_id)
        if match_row.status != MatchStatus.LIVE.value:
            raise ValueError("Events can only be added to live matches")
        self._get_team_row(data.team_id)
        self._get_player_row(data.player_id)
        if data.event_type == EventType.SUBSTITUTION:
            if not data.player_in_id or not data.player_out_id:
                raise ValueError("Substitution requires player in and player out")
            self._get_player_row(data.player_in_id)
            self._get_player_row(data.player_out_id)
        event_row = MatchEventRow(
            id=_next_id("event"),
            match_id=match_id,
            team_id=data.team_id,
            player_id=data.player_id,
            event_type=data.event_type.value,
            minute=data.minute,
            description=data.description,
            player_in_id=data.player_in_id,
            player_out_id=data.player_out_id,
        )
        self._s.add(event_row)
        self._s.flush()
        if event_row.event_type == EventType.GOAL.value:
            self._recalculate_score(match_row)
            self._s.flush()
        return _event_schema(event_row)

    def remove_event(self, match_id: str, event_id: str) -> None:
        match_row = self._get_match_row(match_id)
        if match_row.status != MatchStatus.LIVE.value:
            raise ValueError("Events can only be removed from live matches")
        event_row = (
            self._s.query(MatchEventRow)
            .filter_by(id=event_id, match_id=match_id)
            .first()
        )
        if event_row is None:
            raise LookupError("Event not found")
        was_goal = event_row.event_type == EventType.GOAL.value
        self._s.delete(event_row)
        self._s.flush()
        if was_goal:
            self._recalculate_score(match_row)
            self._s.flush()

    # ── Standings ─────────────────────────────────────────────────────────────

    def get_standings(self) -> list[StandingRow]:
        teams = self.list_teams()
        matches = self.list_matches()
        return calculate_standings(teams, matches)
