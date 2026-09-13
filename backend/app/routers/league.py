from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_auth
from app.models.schemas import AuthUser, League, UpdateLeagueInput
from app.store import get_store

router = APIRouter(prefix="/league", tags=["League"])


@router.get("", response_model=League)
def get_league() -> League:
    return get_store().get_league()


@router.patch("", response_model=League)
def update_league(
    data: UpdateLeagueInput,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> League:
    return get_store().update_league(data)
