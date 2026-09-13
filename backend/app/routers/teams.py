from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import require_auth
from app.models.schemas import AuthUser, CreateTeamInput, Team, UpdateTeamInput
from app.store import Database, get_db

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("", response_model=list[Team])
def list_teams(db: Annotated[Database, Depends(get_db)]) -> list[Team]:
    return db.list_teams()


@router.post("", response_model=Team, status_code=status.HTTP_201_CREATED)
def create_team(
    data: CreateTeamInput,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Team:
    return db.create_team(data)


@router.get("/{team_id}", response_model=Team)
def get_team(team_id: str, db: Annotated[Database, Depends(get_db)]) -> Team:
    try:
        return db.get_team(team_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Team not found"})


@router.patch("/{team_id}", response_model=Team)
def update_team(
    team_id: str,
    data: UpdateTeamInput,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Team:
    try:
        return db.update_team(team_id, data)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Team not found"})


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: str,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> None:
    try:
        db.delete_team(team_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Team not found"})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})
