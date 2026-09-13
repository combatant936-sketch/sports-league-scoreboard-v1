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
from app.store import get_store

router = APIRouter(prefix="/matches", tags=["Matches"])


def _match_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Match not found"})


def _event_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Event not found"})


@router.get("", response_model=list[Match])
def list_matches(
    status_filter: Annotated[Optional[MatchStatus], Query(alias="status")] = None,
) -> list[Match]:
    return get_store().list_matches(status_filter)


@router.post("", response_model=Match, status_code=status.HTTP_201_CREATED)
def create_match(
    data: CreateMatchInput,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return get_store().create_match(data)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Team not found"})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.get("/{match_id}", response_model=Match)
def get_match(match_id: str) -> Match:
    try:
        return get_store().get_match(match_id)
    except LookupError:
        raise _match_not_found()


@router.patch("/{match_id}", response_model=Match)
def update_match(
    match_id: str,
    data: UpdateMatchInput,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return get_store().update_match(match_id, data)
    except LookupError:
        raise _match_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.post("/{match_id}/start", response_model=Match)
def start_match(
    match_id: str,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return get_store().start_match(match_id)
    except LookupError:
        raise _match_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.post("/{match_id}/cancel", response_model=Match)
def cancel_match(
    match_id: str,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return get_store().cancel_match(match_id)
    except LookupError:
        raise _match_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.post("/{match_id}/finish", response_model=Match)
def finish_match(
    match_id: str,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> Match:
    try:
        return get_store().finish_match(match_id)
    except LookupError:
        raise _match_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})


@router.get("/{match_id}/events", response_model=list[MatchEvent], tags=["Match Events"])
def list_events(match_id: str) -> list[MatchEvent]:
    try:
        return get_store().list_events(match_id)
    except LookupError:
        raise _match_not_found()


@router.post("/{match_id}/events", response_model=MatchEvent, status_code=status.HTTP_201_CREATED, tags=["Match Events"])
def add_event(
    match_id: str,
    data: CreateEventInput,
    _: Annotated[AuthUser, Depends(require_auth)],
) -> MatchEvent:
    try:
        return get_store().add_event(match_id, data)
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
    _: Annotated[AuthUser, Depends(require_auth)],
) -> None:
    try:
        get_store().remove_event(match_id, event_id)
    except LookupError as exc:
        msg = str(exc)
        if "Match" in msg:
            raise _match_not_found()
        raise _event_not_found()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})
