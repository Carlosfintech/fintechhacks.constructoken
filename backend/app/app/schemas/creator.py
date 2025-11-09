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
from typing_extensions import Self
from ulid import ULID
from pydantic import field_validator, StringConstraints, ConfigDict, BaseModel, Field, EmailStr, model_validator
from typing_extensions import Annotated

from app.schemas.base_schema import BaseSchema, ModelMeta, LocaleType


class CreatorLogin(BaseModel):
    username: str
    password: str


# Shared properties
class CreatorBase(BaseSchema):
    email: Optional[EmailStr] = None
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the language used by the creator. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    email_validated: Optional[bool] = False
    accepted_rules: Optional[bool] = False
    is_active: Optional[bool] = True
    is_disabled: Optional[bool] = False
    is_approved: Optional[bool] = True
    is_moderator: Optional[bool] = False
    is_admin: Optional[bool] = False
    model_config = ConfigDict(from_attributes=True)


# Properties to receive via API on creation
class CreatorCreate(CreatorBase):
    email: EmailStr
    password: Optional[Annotated[str, StringConstraints(min_length=8, max_length=64)]] = None


# Properties to receive via API on update
class CreatorUpdate(CreatorBase):
    id: Optional[ULID] = None
    original: Optional[Annotated[str, StringConstraints(min_length=8, max_length=64)]] = None
    password: Optional[Annotated[str, StringConstraints(min_length=8, max_length=64)]] = None

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if (self.original is not None or self.password is not None) and self.original != self.password:
            raise ValueError("Passwords do not match.")
        return self


# Additional properties to return via API
class Creator(CreatorBase, metaclass=ModelMeta):
    __exclude_parent_fields__ = ["password"]
    id: ULID = None
    hashed_password: bool = Field(default=False, alias="password")
    totp_secret: bool = Field(default=False, alias="totp")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @field_validator("hashed_password", mode="before")
    @classmethod
    def evaluate_hashed_password(cls, hashed_password):
        if hashed_password:
            return True
        return False

    @field_validator("totp_secret", mode="before")
    @classmethod
    def evaluate_totp_secret(cls, totp_secret):
        if totp_secret:
            return True
        return False


# Additional properties stored in DB
class CreatorInDB(CreatorBase):
    id: Optional[ULID] = None
    hashed_password: Optional[str] = None
    totp_secret: Optional[str] = None
    totp_counter: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
