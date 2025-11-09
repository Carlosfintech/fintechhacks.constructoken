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
from pydantic import (
    ConfigDict,
    Field,
    model_validator,
)
from bovine.activitystreams.utils import actor_for_object, recipients_for_object
from copy import deepcopy

from app.schemas.base_schema import BaseSchema
from app.schema_types import ActivityType, ObjectLinkType, ActorType
from app.utilities.regexes import regex

# from app.core.config import settings


class InboxActivity(BaseSchema):
    URI: Optional[str] = Field(None, description="ActivityPub URI derived from object id.")
    domain: Optional[str] = Field(
        None,
        description="Domain of the account, will be null if this is a local account, otherwise something like ``example.org``. Should be unique with username.",
    )
    actor: str = Field(..., description="Unique actor id for the target of this activity.")
    to: Optional[list[str]] = Field([], description="Who this activity is intended for.")
    type: Optional[ActivityType] = Field(None, description="Activity type.")
    object_type: Optional[ObjectLinkType | ActivityType | ActorType] = Field(
        None, description="Activities may contain objects with specific additional information."
    )
    object_uri: Optional[str] = Field(None, description="URI as identifier to an object.")
    has_content: bool = Field(default=False, description="If the object has content, e.g. a Note.")
    payload: dict[str, Any] = Field(
        ...,
        description="Free form key value pairs for an activity request.",
    )
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def restructure_remote_source(cls, data: Any) -> Any:
        data = deepcopy(data)
        data["payload"] = deepcopy(data)
        data["URI"] = data.get("id")
        data["domain"] = regex.url_root(data.get("actor"))
        data["actor"] = actor_for_object(data)
        recipients = recipients_for_object(data)
        data["to"] = recipients
        # l = regex.url_root(settings.SERVER_HOST)  # noqa: E741
        # data["to"] = [r for r in recipients if regex.url_root(r) == l]
        if isinstance(data.get("object"), dict):
            data["object_type"] = data.get("object", {}).get("type")
            data["has_content"] = bool(
                data.get("object", {}).get("content") or data.get("object", {}).get("contentMap")
            )
            if isinstance(data.get("object", {}).get("object"), str):
                data["object_uri"] = data.get("object").get("object")
        elif isinstance(data.get("object"), str):
            data["object_uri"] = data.get("object")
        return data
