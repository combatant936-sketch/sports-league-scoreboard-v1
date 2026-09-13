from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.schemas import StandingRow
from app.store import Database, get_db

router = APIRouter(prefix="/standings", tags=["Standings"])


@router.get("", response_model=list[StandingRow])
def get_standings(db: Annotated[Database, Depends(get_db)]) -> list[StandingRow]:
    return db.get_standings()
