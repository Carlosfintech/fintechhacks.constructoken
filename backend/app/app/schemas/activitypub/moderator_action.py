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
from app.schema_types import ModeratorActionType, ModerationCategoryType


class ModeratorActionBase(BaseSchema):
    completed: Optional[datetime] = Field(None, description="Date the action was completed.")
    category: Optional[ModerationCategoryType] = Field(None, description="Category of Action taken.")
    action: Optional[ModeratorActionType] = Field(None, description="Class of Action taken.")
    decision: Optional[str] = Field(
        None,
        description="Free text field for explaining why this action was taken, or adding a note about this action.",
    )
    send_email: bool = Field(
        default=False, description="Send an email to the target Actor to explain what happened (local accounts only)."
    )
    moderator_id: Optional[ULID] = Field(None, description="Moderator who performed the Action.")
    domain: Optional[str] = Field(
        None,
        description="Domain of the Action, if this is in response to general review.",
    )
    creator_id: Optional[ULID] = Field(None, description="Targetted Creator of the Action.")
    actor_id: Optional[ULID] = Field(None, description="Targetted Actor of the Action.")
    errors: Optional[str] = Field(None, description="Public comment on this block, viewable (optionally) by everyone.")
    model_config = ConfigDict(from_attributes=True)


class ModeratorActionCreate(ModeratorActionBase):
    pass


class ModeratorActionUpdate(ModeratorActionCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class ModeratorAction(ModeratorActionUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")
