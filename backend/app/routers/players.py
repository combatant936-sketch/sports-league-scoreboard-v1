from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import require_auth
from app.models.schemas import AuthUser, CreatePlayerInput, Player, UpdatePlayerInput
from app.store import Database, get_db

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("", response_model=list[Player])
def list_players(
    db: Annotated[Database, Depends(get_db)],
    team_id: Annotated[Optional[str], Query(alias="teamId")] = None,
) -> list[Player]:
    return db.list_players(team_id)


@router.post("", response_model=Player, status_code=status.HTTP_201_CREATED)
def create_player(
    data: CreatePlayerInput,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Player:
    try:
        return db.create_player(data)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Team not found"})


@router.get("/{player_id}", response_model=Player)
def get_player(player_id: str, db: Annotated[Database, Depends(get_db)]) -> Player:
    try:
        return db.get_player(player_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Player not found"})


@router.patch("/{player_id}", response_model=Player)
def update_player(
    player_id: str,
    data: UpdatePlayerInput,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Player:
    try:
        return db.update_player(player_id, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": str(exc)})


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
    player_id: str,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> None:
    try:
        db.delete_player(player_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Player not found"})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})
