import secrets
from typing import Optional

_tokens: dict[str, str] = {}


def create_token(email: str) -> str:
    token = secrets.token_urlsafe(32)
    _tokens[token] = email
    return token


def validate_token(token: str) -> Optional[str]:
    return _tokens.get(token)


def revoke_token(token: str) -> None:
    _tokens.pop(token, None)


def clear_tokens() -> None:
    _tokens.clear()
