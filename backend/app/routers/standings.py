from fastapi import APIRouter

from app.models.schemas import StandingRow
from app.store import get_store

router = APIRouter(prefix="/standings", tags=["Standings"])


@router.get("", response_model=list[StandingRow])
def get_standings() -> list[StandingRow]:
    return get_store().get_standings()
