from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class LeagueStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


class PlayerPosition(StrEnum):
    GK = "GK"
    DEF = "DEF"
    MID = "MID"
    FWD = "FWD"


class MatchStatus(StrEnum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class EventType(StrEnum):
    GOAL = "goal"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"


class ErrorResponse(CamelModel):
    message: str


class LoginCredentials(CamelModel):
    email: EmailStr
    password: str


class AuthUser(CamelModel):
    email: EmailStr


class LoginResponse(CamelModel):
    email: EmailStr
    token: str


class League(CamelModel):
    id: str
    name: str
    season: str
    status: LeagueStatus


class UpdateLeagueInput(CamelModel):
    name: Optional[str] = None
    season: Optional[str] = None
    status: Optional[LeagueStatus] = None


class Team(CamelModel):
    id: str
    name: str
    logo: str
    league_id: str


class CreateTeamInput(CamelModel):
    name: str
    logo: str


class UpdateTeamInput(CamelModel):
    name: Optional[str] = None
    logo: Optional[str] = None


class Player(CamelModel):
    id: str
    name: str
    jersey_number: int
    position: PlayerPosition
    is_captain: bool
    team_id: str


class CreatePlayerInput(CamelModel):
    name: str
    jersey_number: int = Field(ge=1, le=99)
    position: PlayerPosition
    is_captain: bool
    team_id: str


class UpdatePlayerInput(CamelModel):
    name: Optional[str] = None
    jersey_number: Optional[int] = Field(default=None, ge=1, le=99)
    position: Optional[PlayerPosition] = None
    is_captain: Optional[bool] = None
    team_id: Optional[str] = None


class Match(CamelModel):
    id: str
    home_team_id: str
    away_team_id: str
    scheduled_at: datetime
    status: MatchStatus
    home_score: int
    away_score: int


class CreateMatchInput(CamelModel):
    home_team_id: str
    away_team_id: str
    scheduled_at: datetime


class UpdateMatchInput(CamelModel):
    home_team_id: Optional[str] = None
    away_team_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class MatchEvent(CamelModel):
    id: str
    match_id: str
    team_id: str
    player_id: str
    event_type: EventType
    minute: int
    description: str
    player_in_id: Optional[str] = None
    player_out_id: Optional[str] = None


class CreateEventInput(CamelModel):
    team_id: str
    player_id: str
    event_type: EventType
    minute: int = Field(ge=1, le=120)
    description: str = ""
    player_in_id: Optional[str] = None
    player_out_id: Optional[str] = None


class StandingRow(CamelModel):
    position: int
    team_id: str
    team_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
