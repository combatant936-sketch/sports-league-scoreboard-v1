from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_auth
from app.models.schemas import AuthUser, League, UpdateLeagueInput
from app.store import Database, get_db

router = APIRouter(prefix="/league", tags=["League"])


@router.get("", response_model=League)
def get_league(db: Annotated[Database, Depends(get_db)]) -> League:
    return db.get_league()


@router.patch("", response_model=League)
def update_league(
    data: UpdateLeagueInput,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> League:
    return db.update_league(data)
