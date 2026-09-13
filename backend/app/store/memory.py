from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.auth.password import hash_password, verify_password
from app.models.schemas import (
    CreateEventInput,
    CreateMatchInput,
    CreatePlayerInput,
    CreateTeamInput,
    EventType,
    League,
    LeagueStatus,
    Match,
    MatchEvent,
    MatchStatus,
    Player,
    PlayerPosition,
    Team,
    UpdateLeagueInput,
    UpdateMatchInput,
    UpdatePlayerInput,
    UpdateTeamInput,
)
from app.store.standings import calculate_standings

ADMIN_EMAIL = "admin@league.com"
ADMIN_PASSWORD = "admin123"


def _next_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass
class Store:
    league: League
    teams: list[Team] = field(default_factory=list)
    players: list[Player] = field(default_factory=list)
    matches: list[Match] = field(default_factory=list)
    events: list[MatchEvent] = field(default_factory=list)
    admin_email: str = ADMIN_EMAIL
    admin_password_hash: str = ""

    @classmethod
    def create_seed(cls) -> Store:
        store = cls(
            league=League(
                id="league-1",
                name="Premier City League",
                season="2025/26",
                status=LeagueStatus.ACTIVE,
            ),
            teams=[
                Team(id="team-1", name="North United", logo="⚽", league_id="league-1"),
                Team(id="team-2", name="South City FC", logo="🦁", league_id="league-1"),
                Team(id="team-3", name="East Rovers", logo="🦅", league_id="league-1"),
                Team(id="team-4", name="West Athletic", logo="🐺", league_id="league-1"),
            ],
            players=[
                Player(id="player-1", name="Alex Morgan", jersey_number=1, position=PlayerPosition.GK, is_captain=False, team_id="team-1"),
                Player(id="player-2", name="Jordan Lee", jersey_number=9, position=PlayerPosition.FWD, is_captain=True, team_id="team-1"),
                Player(id="player-3", name="Sam Rivera", jersey_number=10, position=PlayerPosition.MID, is_captain=False, team_id="team-1"),
                Player(id="player-4", name="Chris Park", jersey_number=1, position=PlayerPosition.GK, is_captain=False, team_id="team-2"),
                Player(id="player-5", name="Taylor Brooks", jersey_number=7, position=PlayerPosition.FWD, is_captain=True, team_id="team-2"),
                Player(id="player-6", name="Morgan Ellis", jersey_number=6, position=PlayerPosition.MID, is_captain=False, team_id="team-2"),
                Player(id="player-7", name="Riley Chen", jersey_number=11, position=PlayerPosition.FWD, is_captain=True, team_id="team-3"),
                Player(id="player-8", name="Casey Wright", jersey_number=4, position=PlayerPosition.DEF, is_captain=False, team_id="team-3"),
                Player(id="player-9", name="Jamie Fox", jersey_number=8, position=PlayerPosition.MID, is_captain=True, team_id="team-4"),
                Player(id="player-10", name="Drew Stone", jersey_number=3, position=PlayerPosition.DEF, is_captain=False, team_id="team-4"),
            ],
            matches=[
                Match(id="match-1", home_team_id="team-1", away_team_id="team-2", scheduled_at=_parse_dt("2026-09-10T15:00:00.000Z"), status=MatchStatus.FINISHED, home_score=2, away_score=1),
                Match(id="match-2", home_team_id="team-3", away_team_id="team-4", scheduled_at=_parse_dt("2026-09-11T15:00:00.000Z"), status=MatchStatus.FINISHED, home_score=1, away_score=1),
                Match(id="match-3", home_team_id="team-1", away_team_id="team-3", scheduled_at=_parse_dt("2026-09-20T14:00:00.000Z"), status=MatchStatus.SCHEDULED, home_score=0, away_score=0),
                Match(id="match-4", home_team_id="team-2", away_team_id="team-4", scheduled_at=_parse_dt("2026-09-21T16:30:00.000Z"), status=MatchStatus.SCHEDULED, home_score=0, away_score=0),
            ],
            events=[
                MatchEvent(id="event-1", match_id="match-1", team_id="team-1", player_id="player-2", event_type=EventType.GOAL, minute=23, description="Header from corner"),
                MatchEvent(id="event-2", match_id="match-1", team_id="team-2", player_id="player-5", event_type=EventType.GOAL, minute=41, description="Penalty kick"),
                MatchEvent(id="event-3", match_id="match-1", team_id="team-1", player_id="player-3", event_type=EventType.GOAL, minute=78, description="Long-range strike"),
                MatchEvent(id="event-4", match_id="match-1", team_id="team-2", player_id="player-6", event_type=EventType.YELLOW_CARD, minute=55, description="Late tackle"),
                MatchEvent(id="event-5", match_id="match-2", team_id="team-3", player_id="player-7", event_type=EventType.GOAL, minute=12, description="Tap-in"),
                MatchEvent(id="event-6", match_id="match-2", team_id="team-4", player_id="player-9", event_type=EventType.GOAL, minute=67, description="Free kick"),
            ],
        )
        store.admin_password_hash = hash_password(ADMIN_PASSWORD)
        return store

    def verify_admin(self, email: str, password: str) -> bool:
        return email == self.admin_email and verify_password(password, self.admin_password_hash)

    def get_league(self) -> League:
        return self.league

    def update_league(self, data: UpdateLeagueInput) -> League:
        updates = data.model_dump(exclude_unset=True)
        self.league = self.league.model_copy(update=updates)
        return self.league

    def list_teams(self) -> list[Team]:
        return list(self.teams)

    def get_team(self, team_id: str) -> Team:
        team = next((t for t in self.teams if t.id == team_id), None)
        if team is None:
            raise LookupError("Team not found")
        return team

    def create_team(self, data: CreateTeamInput) -> Team:
        team = Team(id=_next_id("team"), name=data.name, logo=data.logo, league_id=self.league.id)
        self.teams.append(team)
        return team

    def update_team(self, team_id: str, data: UpdateTeamInput) -> Team:
        team = self.get_team(team_id)
        updates = data.model_dump(exclude_unset=True)
        updated = team.model_copy(update=updates)
        self.teams = [updated if t.id == team_id else t for t in self.teams]
        return updated

    def delete_team(self, team_id: str) -> None:
        self.get_team(team_id)
        if any(p.team_id == team_id for p in self.players):
            raise ValueError("Cannot delete team with assigned players")
        if any(m.home_team_id == team_id or m.away_team_id == team_id for m in self.matches):
            raise ValueError("Cannot delete team referenced in matches")
        self.teams = [t for t in self.teams if t.id != team_id]

    def list_players(self, team_id: Optional[str] = None) -> list[Player]:
        if team_id:
            return [p for p in self.players if p.team_id == team_id]
        return list(self.players)

    def get_player(self, player_id: str) -> Player:
        player = next((p for p in self.players if p.id == player_id), None)
        if player is None:
            raise LookupError("Player not found")
        return player

    def _demote_captains(self, team_id: str, except_id: Optional[str] = None) -> None:
        self.players = [
            p.model_copy(update={"is_captain": False})
            if p.team_id == team_id and p.id != except_id and p.is_captain
            else p
            for p in self.players
        ]

    def create_player(self, data: CreatePlayerInput) -> Player:
        self.get_team(data.team_id)
        player = Player(id=_next_id("player"), **data.model_dump())
        if player.is_captain:
            self._demote_captains(player.team_id)
        self.players.append(player)
        return player

    def update_player(self, player_id: str, data: UpdatePlayerInput) -> Player:
        player = self.get_player(player_id)
        updates = data.model_dump(exclude_unset=True)
        if "team_id" in updates:
            self.get_team(updates["team_id"])
        updated = player.model_copy(update=updates)
        if updated.is_captain:
            self._demote_captains(updated.team_id, except_id=player_id)
        self.players = [updated if p.id == player_id else p for p in self.players]
        return updated

    def delete_player(self, player_id: str) -> None:
        self.get_player(player_id)
        if any(
            e.player_id == player_id or e.player_in_id == player_id or e.player_out_id == player_id
            for e in self.events
        ):
            raise ValueError("Cannot delete player referenced in match events")
        self.players = [p for p in self.players if p.id != player_id]

    def list_matches(self, status: Optional[MatchStatus] = None) -> list[Match]:
        matches = self.matches if status is None else [m for m in self.matches if m.status == status]
        return sorted(matches, key=lambda m: m.scheduled_at, reverse=True)

    def get_match(self, match_id: str) -> Match:
        match = next((m for m in self.matches if m.id == match_id), None)
        if match is None:
            raise LookupError("Match not found")
        return match

    def create_match(self, data: CreateMatchInput) -> Match:
        if data.home_team_id == data.away_team_id:
            raise ValueError("Home and away teams must be different")
        self.get_team(data.home_team_id)
        self.get_team(data.away_team_id)
        match = Match(
            id=_next_id("match"),
            home_team_id=data.home_team_id,
            away_team_id=data.away_team_id,
            scheduled_at=data.scheduled_at,
            status=MatchStatus.SCHEDULED,
            home_score=0,
            away_score=0,
        )
        self.matches.append(match)
        return match

    def update_match(self, match_id: str, data: UpdateMatchInput) -> Match:
        match = self.get_match(match_id)
        if match.status != MatchStatus.SCHEDULED:
            raise ValueError("Only scheduled matches can be updated")
        updates = data.model_dump(exclude_unset=True)
        if "home_team_id" in updates:
            self.get_team(updates["home_team_id"])
        if "away_team_id" in updates:
            self.get_team(updates["away_team_id"])
        updated = match.model_copy(update=updates)
        self.matches = [updated if m.id == match_id else m for m in self.matches]
        return updated

    def start_match(self, match_id: str) -> Match:
        match = self.get_match(match_id)
        if match.status != MatchStatus.SCHEDULED:
            raise ValueError("Only scheduled matches can be started")
        updated = match.model_copy(update={"status": MatchStatus.LIVE})
        self.matches = [updated if m.id == match_id else m for m in self.matches]
        return updated

    def cancel_match(self, match_id: str) -> Match:
        match = self.get_match(match_id)
        if match.status == MatchStatus.FINISHED:
            raise ValueError("Finished matches cannot be cancelled")
        updated = match.model_copy(update={"status": MatchStatus.CANCELLED, "home_score": 0, "away_score": 0})
        self.matches = [updated if m.id == match_id else m for m in self.matches]
        self.events = [e for e in self.events if e.match_id != match_id]
        return updated

    def finish_match(self, match_id: str) -> Match:
        match = self.get_match(match_id)
        if match.status != MatchStatus.LIVE:
            raise ValueError("Only live matches can be finished")
        updated = match.model_copy(update={"status": MatchStatus.FINISHED})
        self.matches = [updated if m.id == match_id else m for m in self.matches]
        return updated

    def list_events(self, match_id: str) -> list[MatchEvent]:
        self.get_match(match_id)
        events = [e for e in self.events if e.match_id == match_id]
        return sorted(events, key=lambda e: e.minute)

    def _recalculate_score(self, match_id: str) -> None:
        match = self.get_match(match_id)
        goals = [e for e in self.events if e.match_id == match_id and e.event_type == EventType.GOAL]
        home_score = sum(1 for g in goals if g.team_id == match.home_team_id)
        away_score = sum(1 for g in goals if g.team_id == match.away_team_id)
        updated = match.model_copy(update={"home_score": home_score, "away_score": away_score})
        self.matches = [updated if m.id == match_id else m for m in self.matches]

    def add_event(self, match_id: str, data: CreateEventInput) -> MatchEvent:
        match = self.get_match(match_id)
        if match.status != MatchStatus.LIVE:
            raise ValueError("Events can only be added to live matches")
        self.get_team(data.team_id)
        self.get_player(data.player_id)
        if data.event_type == EventType.SUBSTITUTION:
            if not data.player_in_id or not data.player_out_id:
                raise ValueError("Substitution requires player in and player out")
            self.get_player(data.player_in_id)
            self.get_player(data.player_out_id)
        event = MatchEvent(
            id=_next_id("event"),
            match_id=match_id,
            team_id=data.team_id,
            player_id=data.player_id,
            event_type=data.event_type,
            minute=data.minute,
            description=data.description,
            player_in_id=data.player_in_id,
            player_out_id=data.player_out_id,
        )
        self.events.append(event)
        if event.event_type == EventType.GOAL:
            self._recalculate_score(match_id)
        return event

    def remove_event(self, match_id: str, event_id: str) -> None:
        match = self.get_match(match_id)
        if match.status != MatchStatus.LIVE:
            raise ValueError("Events can only be removed from live matches")
        event = next((e for e in self.events if e.id == event_id and e.match_id == match_id), None)
        if event is None:
            raise LookupError("Event not found")
        was_goal = event.event_type == EventType.GOAL
        self.events = [e for e in self.events if e.id != event_id]
        if was_goal:
            self._recalculate_score(match_id)

    def get_standings(self):
        return calculate_standings(self.teams, self.matches)


_store: Store = Store.create_seed()


def get_store() -> Store:
    return _store


def reset_store() -> Store:
    global _store
    from app.auth.tokens import clear_tokens

    clear_tokens()
    _store = Store.create_seed()
    return _store
