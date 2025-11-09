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
from datetime import datetime

from app.schemas.base_schema import BaseSchema


class FollowBase(BaseSchema):
    URI: Optional[str] = Field(None, description="ActivityPub URI for this follow.")
    actor_id: ULID = Field(..., description="Initiating Actor of the Follow.")
    target_id: ULID = Field(..., description="Target Actor of the Follow.")
    has_accepted: bool = Field(default=False, description="Has the target Actor accepted the Follow?")
    show_reposts: bool = Field(default=True, description="Show reposts as well as posts by the Followed actor.")
    notify: bool = Field(default=False, description="Notify when the Followed Actor posts.")
    model_config = ConfigDict(from_attributes=True)


class FollowCreate(FollowBase):
    pass


class FollowUpdate(FollowCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class Follow(FollowUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")


# class ActivityFollow()
