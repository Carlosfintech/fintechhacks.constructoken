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


class ThreadMuteBase(BaseSchema):
    expires: Optional[datetime] = Field(
        None,
        description="Period when mute expires. Can be None for never expires.",
    )
    actor_id: ULID = Field(..., description="Initiating Actor of the mute.")
    thread_id: ULID = Field(..., description="Thread to be muted.")
    model_config = ConfigDict(from_attributes=True)


class ThreadMuteCreate(ThreadMuteBase):
    pass


class ThreadMuteUpdate(ThreadMuteCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class ThreadMute(ThreadMuteUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")
