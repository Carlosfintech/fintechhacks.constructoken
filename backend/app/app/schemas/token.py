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

from typing import Optional
from pydantic import field_validator, ConfigDict, BaseModel
from ulid import ULID
from fastapi.security import SecurityScopes


class Token(BaseModel):
    token: str
    authenticates_id: Optional[ULID]
    scopes: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)

    @field_validator("scopes", mode="before")
    @classmethod
    def evaluate_scopes(cls, scopes):
        if isinstance(scopes, SecurityScopes):
            return scopes.scope_str
        if isinstance(scopes, list):
            return " ".join(scopes)
        return scopes


class TokenCreate(Token):
    authenticates_id: ULID


class TokenUpdate(Token):
    pass


class TokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    scopes: Optional[str] = None
    token_type: str

    @field_validator("scopes", mode="before")
    @classmethod
    def evaluate_scopes(cls, scopes):
        if isinstance(scopes, SecurityScopes):
            return scopes.scope_str
        if isinstance(scopes, list):
            return " ".join(scopes)
        return scopes


class TokenPayload(BaseModel):
    sub: Optional[ULID] = None
    refresh: Optional[bool] = False
    scopes: Optional[list[str]] = []
    totp: Optional[bool] = False

    @field_validator("scopes", mode="before")
    @classmethod
    def evaluate_scopes(cls, scopes):
        if scopes and isinstance(scopes, str):
            return [s.strip() for s in scopes.replace(" ", ",").split(",") if s]
        return scopes


class MagicTokenPayload(BaseModel):
    sub: Optional[ULID] = None
    fingerprint: Optional[ULID] = None


class WebToken(BaseModel):
    claim: str
