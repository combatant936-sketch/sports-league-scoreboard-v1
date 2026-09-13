from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.tokens import validate_token
from app.models.schemas import AuthUser

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(_bearer)],
) -> Optional[AuthUser]:
    if credentials is None:
        return None
    email = validate_token(credentials.credentials)
    if email is None:
        return None
    return AuthUser(email=email)


def require_auth(
    user: Annotated[Optional[AuthUser], Depends(get_current_user)],
) -> AuthUser:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Unauthorized"},
        )
    return user
