"""Hop Sauna

SPDX-FileCopyrightText: Copyright (C) Whythawk and Hop Sauna Authors ask@whythawk.com
SPDX-License-Identifier: AGPL-3.0-or-later

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http:#www.gnu.org/licenses/>.

"""

from typing import Generator, Annotated
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.db.session import SessionLocal


scope_scheme = {
    "read": "Read",
    "write": "Write",
    "admin": "Admin",
}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", scopes=scope_scheme)
# https://stackoverflow.com/a/66512998/295606
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", scopes=scope_scheme, auto_error=False
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class CredentialsException(HTTPException):
    def __init__(self, detail: str, headers: list[str] = []) -> HTTPException:
        if headers and isinstance(headers, (str, list)):
            if isinstance(headers, list):
                headers = " ".join(headers)
            headers = f'Bearer scope="{headers}"'
        else:
            headers = "Bearer"
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": headers},
        )


@asynccontextmanager
async def get_lifespan(_: FastAPI) -> AsyncIterator[None]:
    # https://github.com/long2ice/fastapi-cache?tab=readme-ov-file
    redis = aioredis.from_url(
        f"redis://{settings.DOCKER_IMAGE_CACHE}", password=settings.REDIS_PASSWORD, decode_responses=False
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


def get_token_payload(token: str) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    return token_data


def get_creator(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
    security_scopes: list[str] = [],
) -> models.Creator:
    token_data = get_token_payload(token)
    if token_data.refresh or token_data.totp:
        # Refresh token is not a valid access token and TOTP True can only be used to validate TOTP
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    # Now test for scopes
    creator = crud.creator.get(db, id=token_data.sub)
    if not settings.USE_REFRESH_TOKEN:
        # If not using refresh tokens, need to check that this is a valid token
        if not crud.token.get_by_creator(token=token, creator=creator):
            creator = None
    if not creator:
        raise CredentialsException(detail="Creator not found.", headers=security_scopes)
    if security_scopes and token_data.scopes:
        security_scopes = crud.token.validate_scopes(security_scopes)
        for scope in security_scopes:
            if scope not in token_data.scopes:
                raise CredentialsException(detail="Not enough permissions.", headers=security_scopes)
    return creator


def get_totp_creator(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]
) -> models.Creator:
    token_data = get_token_payload(token)
    if token_data.refresh or not token_data.totp:
        # Refresh token is not a valid access token and TOTP False cannot be used to validate TOTP
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    creator = crud.creator.get(db, id=token_data.sub)
    if not creator:
        raise CredentialsException(detail="Could not validate credentials.")
    return creator


def get_magic_token(token: Annotated[str, Depends(oauth2_scheme)]) -> schemas.MagicTokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = schemas.MagicTokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    return token_data


def get_refresh_token(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]
) -> models.Token:
    """
    REFRESH tokens are for issuing new ACCESS tokens only. They are refreshed only if they have an expiry date.
    """
    token_data = get_token_payload(token)
    if not token_data.refresh:
        # Access token is not a valid refresh token
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    creator = crud.creator.get(db, id=token_data.sub)
    if not creator or not crud.creator.is_active(creator):
        raise CredentialsException(detail="Could not validate credentials.")
    # Explicitly check that this REFRESH token belongs to this creator
    token_obj = crud.token.get_by_creator(token=token, creator=creator)
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    return token_obj


def get_active_creator(
    creator: Annotated[models.Creator, Depends(get_creator)],
) -> models.Creator:
    if not crud.creator.is_active(creator):
        raise CredentialsException(detail="Could not validate credentials.")
    return creator


def get_optional_creator(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(optional_oauth2_scheme)] = None,
    security_scopes: list[str] = [],
) -> models.Creator | None:
    creator = None
    if token:
        try:
            creator = get_creator(db=db, token=token, security_scopes=security_scopes)
            creator = get_active_creator(creator=creator)
        except (HTTPException, CredentialsException):
            pass
    return creator


def get_active_admin(
    creator: Annotated[models.Creator, Depends(get_creator)],
) -> models.Creator:
    if not crud.creator.is_active(creator) or not crud.creator.is_admin(creator):
        raise CredentialsException(detail="Not enough permissions.")
    return creator


def get_active_websocket_creator(*, db: Session, token: str, security_scopes: list[str] = []) -> models.Creator:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise ValidationError("Could not validate credentials.")
    if token_data.refresh:
        # Refresh token is not a valid access token
        raise ValidationError("Could not validate credentials.")
    creator = crud.creator.get(db, id=token_data.sub)
    if not creator:
        raise ValidationError("Creator not found.")
    if not crud.creator.is_active(creator):
        raise ValidationError("Inactive creator.")
    if security_scopes and token_data.scopes:
        security_scopes = crud.token.validate_scopes(security_scopes)
        for scope in security_scopes:
            if scope not in token_data.scopes:
                raise ValidationError("Not enough permissions.")
    return creator
