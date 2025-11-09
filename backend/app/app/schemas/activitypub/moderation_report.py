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

from app.schemas.base_schema import BaseSchema, LocaleType


class ReportBase(BaseSchema):
    URI: Optional[str] = Field(None, description="ActivityPub URI for this Report.")
    submitter_id: Optional[ULID] = Field(None, description="Submitting Actor of the Report.")
    actor_id: ULID = Field(..., description="Targetted Actor of the Report.")
    moderator_id: Optional[ULID] = Field(None, description="Moderator who reviewed the Report.")
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the language. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    text: Optional[str] = Field(None, description="Description of what action was taken in response to this report.")
    actioned: Optional[datetime] = Field(None, description="Date at which action was taken, if any.")
    forwarded: bool = Field(default=False, description="Whether report should be forwarded to remote instance.")
    model_config = ConfigDict(from_attributes=True)


class ReportCreate(ReportBase):
    pass


class ReportUpdate(ReportCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class Report(ReportUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")
