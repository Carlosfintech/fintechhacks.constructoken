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

from typing import Optional, Any
from ulid import ULID
from pydantic import ConfigDict, Field, model_validator
from datetime import datetime

from app.schemas.base_schema import BaseSchema
from app.utilities.regexes import regex
from app.schema_types import VisibilityType


# NOTE: this is to support the database, not ActivityPub
class ActorSettingsBase(BaseSchema):
    privacy: VisibilityType = Field(
        default=VisibilityType.Unlocked, description="Default post privacy for this account."
    )
    sensitive: bool = Field(False, description="Posts by this account marked as sensitive.")
    hide_collections: bool = Field(False, description="Hide lists of Follows and Followers.")
    enable_rss: bool = Field(False, description="Enable public RSS feed of Actor posts.")
    actor_id: ULID = Field(..., description="Actor associated with these settings.")
    model_config = ConfigDict(from_attributes=True)


class ActorSettingsCreate(BaseSchema):
    pass


class ActorSettingsUpdate(ActorSettingsCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class ActorSettings(ActorSettingsUpdate):
    created: Optional[datetime] = Field(None, description="Automatically generated date created.")
    modified: Optional[datetime] = Field(None, description="Automatically generated date last modified.")


class ActivityActorSettingsCreate(ActorSettingsBase):

    @model_validator(mode="before")
    def restructure_remote_source(cls, data: Any) -> Any:
        data["name"] = regex.hashtag_root(data.get("name"))
        if data.get("href") and regex.url_is_local(data["href"]):
            # Other bools are derived from more exacting rules
            data["local"] = True
        return data
