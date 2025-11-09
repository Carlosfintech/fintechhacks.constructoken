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
from pydantic import (
    ConfigDict,
    Field,
    HttpUrl,
)
from datetime import datetime

from app.schemas.base_schema import BaseSchema


class MoveBase(BaseSchema):
    attempted: Optional[datetime] = Field(
        None,
        description="When was processing of the Move to TargetURI last attempted by our instance (None if not yet attempted).",
    )
    succeeded: Optional[datetime] = Field(
        None,
        description="When did the processing of the Move to TargetURI succeed according to our criteria (None if not yet complete).",
    )
    URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub ID/URI of the Move Activity itself.",
    )
    originURI: Optional[HttpUrl] = Field(
        None,
        description="OriginURI of the Move. Ie., the Move Object.",
    )
    targetURI: Optional[HttpUrl] = Field(
        None,
        description="TargetURI of the Move. Ie., the Move Target.",
    )
    model_config = ConfigDict(from_attributes=True)


class MoveCreate(MoveBase):
    pass


class MoveUpdate(MoveCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class Move(MoveUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")
