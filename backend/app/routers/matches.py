from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import require_auth
from app.models.schemas import (
    AuthUser,
    CreateEventInput,
    CreateMatchInput,
    Match,
    MatchEvent,
    MatchStatus,
    UpdateMatchInput,
)
from app.store import Database, get_db

router = APIRouter(prefix="/matches", tags=["Matches"])


def _match_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Match not found"})


def _event_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Event not found"})


@router.get("", response_model=list[Match])
def list_matches(
    db: Annotated[Database, Depends(get_db)],
    status_filter: Annotated[Optional[MatchStatus], Query(alias="status")] = None,
) -> list[Match]:
    return db.list_matches(status_filter)


@router.post("", response_model=Match, status_code=status.HTTP_201_CREATED)
def create_match(
    data: CreateMatchInput,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return db.create_match(data)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Team not found"})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.get("/{match_id}", response_model=Match)
def get_match(match_id: str, db: Annotated[Database, Depends(get_db)]) -> Match:
    try:
        return db.get_match(match_id)
    except LookupError:
        raise _match_not_found()


@router.patch("/{match_id}", response_model=Match)
def update_match(
    match_id: str,
    data: UpdateMatchInput,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return db.update_match(match_id, data)
    except LookupError:
        raise _match_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.post("/{match_id}/start", response_model=Match)
def start_match(
    match_id: str,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return db.start_match(match_id)
    except LookupError:
        raise _match_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.post("/{match_id}/cancel", response_model=Match)
def cancel_match(
    match_id: str,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return db.cancel_match(match_id)
    except LookupError:
        raise _match_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.post("/{match_id}/finish", response_model=Match)
def finish_match(
    match_id: str,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return db.finish_match(match_id)
    except LookupError:
        raise _match_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.get("/{match_id}/events", response_model=list[MatchEvent], tags=["Match Events"])
def list_events(match_id: str, db: Annotated[Database, Depends(get_db)]) -> list[MatchEvent]:
    try:
        return db.list_events(match_id)
    except LookupError:
        raise _match_not_found()


@router.post("/{match_id}/events", response_model=MatchEvent, status_code=status.HTTP_201_CREATED, tags=["Match Events"])
def add_event(
    match_id: str,
    data: CreateEventInput,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> MatchEvent:
    try:
        return db.add_event(match_id, data)
    except LookupError as exc:
        msg = str(exc)
        if "Event" in msg:
            raise _event_not_found()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": msg})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.delete("/{match_id}/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Match Events"])
def remove_event(
    match_id: str,
    event_id: str,
    db: Annotated[Database, Depends(get_db)],
    _: Annotated[AuthUser, Depends(require_auth)],
) -> None:
    try:
        db.remove_event(match_id, event_id)
    except LookupError as exc:
        msg = str(exc)
        if "Match" in msg:
            raise _match_not_found()
        raise _event_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})
