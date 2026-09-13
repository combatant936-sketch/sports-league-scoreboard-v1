from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import require_auth
from app.models.schemas import AuthUser, CreateTeamInput, Team, UpdateTeamInput
from app.store import get_store

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("", response_model=list[Team])
def list_teams() -> list[Team]:
    return get_store().list_teams()


@router.post("", response_model=Team, status_code=status.HTTP_201_CREATED)
def create_team(
    data: CreateTeamInput,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Team:
    return get_store().create_team(data)


@router.get("/{team_id}", response_model=Team)
def get_team(team_id: str) -> Team:
    try:
        return get_store().get_team(team_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Team not found"})


@router.patch("/{team_id}", response_model=Team)
def update_team(
    team_id: str,
    data: UpdateTeamInput,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Team:
    try:
        return get_store().update_team(team_id, data)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Team not found"})


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: str,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> None:
    try:
        get_store().delete_team(team_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Team not found"})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})
