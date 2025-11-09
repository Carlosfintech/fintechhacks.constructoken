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
from ulid import ULID
from pydantic import ConfigDict, Field

from app.schemas.base_schema import BaseSchema, LocaleType


class RuleBase(BaseSchema):
    text: Optional[dict[str, str]] = Field(None, description="Text content of the rule. Dict or 'lang': 'text'.")
    order: Optional[int] = Field(None, description="Rule ordering, index from 0.")
    deleted: bool = Field(
        default=False,
        description="Rule been deleted, still kept in database for reference in historic reports.",
    )
    model_config = ConfigDict(from_attributes=True)


class RuleCreate(RuleBase):
    pass


class RuleUpdate(RuleCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class Rule(BaseSchema):
    language: Optional[LocaleType] = Field(
        None, description="Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3."
    )
    text: str = Field(..., description="Text content of the rule.")
    order: int = Field(..., description="Rule ordering, index from 0.")
    model_config = ConfigDict(from_attributes=True)
