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

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext
from passlib.totp import TOTP
from passlib.exc import TokenError, MalformedTokenError
from passlib.pwd import genphrase
from ulid import ULID

from app.core.config import settings
from app.schemas import NewTOTP

"""
https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Authentication_Cheat_Sheet.md
https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html
https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Password_Storage_Cheat_Sheet.md
https://blog.cloudflare.com/ensuring-randomness-with-linuxs-random-number-generator/
https://passlib.readthedocs.io/en/stable/lib/passlib.pwd.html
Specifies minimum criteria:
    - Use Argon2id with a minimum configuration of 15 MiB of memory, an iteration count of 2, and 1 degree of parallelism.
    - Passwords shorter than 8 characters are considered to be weak (NIST SP800-63B).
    - Maximum password length of 64 prevents long password Denial of Service attacks.
    - Do not silently truncate passwords.
    - Allow usage of all characters including unicode and whitespace.
"""
pwd_context = CryptContext(
    schemes=settings.HASH_ALGO, deprecated=["auto"]
)  # current defaults: $argon2id$v=19$m=65536,t=3,p=4, "bcrypt" is deprecated
totp_factory = TOTP.using(secrets={"1": settings.TOTP_SECRET_KEY}, issuer=settings.SERVER_NAME, alg=settings.TOTP_ALGO)


def create_access_token(
    *,
    subject: str | Any,
    actor: str | Any | None = None,
    expires_delta: timedelta = None,
    force_totp: bool = False,
    security_scopes: list[str] = [],
) -> str:
    """
    ACCESS tokens are for AUTHORISATION of the `creator`. They should expire within a relatively short interval.
    """
    # NOTE: this is CONVENIENCE ONLY - it is real stupid to have a perpetual, non-revokable ACCESS token
    expire = 0
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    elif settings.ACCESS_TOKEN_EXPIRE_SECONDS:
        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode = {"sub": str(subject), "totp": force_totp}
    if expire:
        to_encode["exp"] = expire
    else:
        # Non-expiring access tokens create a problem as being non-unique
        to_encode["name"] = genphrase(length=2, wordset="eff_short", sep="-")
    if security_scopes and isinstance(security_scopes, list):
        to_encode["scopes"] = security_scopes
    if actor:
        to_encode["actor"] = str(actor)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGO)
    return encoded_jwt


def create_refresh_token(
    *,
    subject: str | Any,
    actor: str | Any | None = None,
    expires_delta: timedelta = None,
    security_scopes: list[str] = [],
) -> str:
    """
    REFRESH tokens are for issuing new ACCESS tokens only. They are refreshed only if they have an expiry date.
    """
    expire = 0
    # Placeholder, assume TRUE for now: if settings.USE_REFRESH_TOKEN:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    elif settings.REFRESH_TOKEN_EXPIRE_SECONDS:
        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    to_encode = {"sub": str(subject), "refresh": True}
    if expire:
        to_encode["exp"] = expire
    else:
        # Non-expiring access tokens create a problem as being non-unique
        to_encode["name"] = genphrase(length=2, wordset="eff_short", sep="-")
    if security_scopes and isinstance(security_scopes, list):
        to_encode["scopes"] = security_scopes
    if actor:
        to_encode["actor"] = str(actor)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGO)
    return encoded_jwt


def create_magic_tokens(*, subject: str | Any, expires_delta: timedelta = None) -> list[str]:
    """
    MAGIC tokens are for AUTHENTICATION of the `creator`. They should expire within a relatively short interval.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    fingerprint = str(ULID())
    magic_tokens = []
    # First sub is the creator.id, to be emailed. Second is the disposable id.
    for sub in [subject, ULID()]:
        to_encode = {"exp": expire, "sub": str(sub), "fingerprint": fingerprint}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGO)
        magic_tokens.append(encoded_jwt)
    return magic_tokens


def create_new_totp(*, label: str, uri: str | None = None) -> NewTOTP:
    if not uri:
        totp = totp_factory.new()
    else:
        totp = totp_factory.from_source(uri)
    return NewTOTP(
        **{
            "secret": totp.to_json(),
            "key": totp.pretty_key(),
            "uri": totp.to_uri(issuer=settings.SERVER_NAME, label=label),
        }
    )


def verify_totp(*, token: str, secret: str, last_counter: int = None) -> str | bool:
    """
    token: from creator
    secret: totp security string from creator in db
    last_counter: int from creator in db (may be None)
    """
    try:
        match = totp_factory.verify(token, secret, last_counter=last_counter)
    except (MalformedTokenError, TokenError):
        return False
    else:
        return match.counter


def verify_password(*, plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
