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

from app.schemas.base_schema import BaseSchema, LocaleType
from app.utilities.regexes import regex


# NOTE: this is to support the database, not ActivityPub
class TagBase(BaseSchema):
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the language of pathway. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    name: Optional[str] = Field(None, description="Name of the tag without the hash prefix.")
    local: bool = Field(False, description="Tag is local to this instance.")
    usable: bool = Field(False, description="Tag is useable on this instance.")
    listable: bool = Field(False, description="Tagged statuses can be listed on this instance.")
    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseSchema):
    pass


class TagUpdate(TagCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class Tag(TagUpdate):
    created: Optional[datetime] = Field(None, description="Automatically generated date created.")
    modified: Optional[datetime] = Field(None, description="Automatically generated date last modified.")


class ActivityTagCreate(TagBase):

    @model_validator(mode="before")
    def restructure_remote_source(cls, data: Any) -> Any:
        data["name"] = regex.hashtag_root(data.get("name"))
        if data.get("href") and regex.url_is_local(data["href"]):
            # Other bools are derived from more exacting rules
            data["local"] = True
        return data
