from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.dependencies import get_current_user, require_auth
from app.auth.tokens import create_token, revoke_token
from app.models.schemas import AuthUser, LoginCredentials, LoginResponse
from app.store import Database, get_db

router = APIRouter(prefix="/auth", tags=["Auth"])
_bearer = HTTPBearer(auto_error=False)


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginCredentials,
    db: Annotated[Database, Depends(get_db)],
) -> LoginResponse:
    if not db.verify_admin(credentials.email, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid email or password"},
        )
    token = create_token(credentials.email)
    return LoginResponse(email=credentials.email, token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    user: Annotated[AuthUser, Depends(require_auth)],
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(_bearer)],
) -> None:
    if credentials:
        revoke_token(credentials.credentials)


@router.get("/me", response_model=Optional[AuthUser])
def me(user: Annotated[Optional[AuthUser], Depends(get_current_user)]) -> Optional[AuthUser]:
    return user
