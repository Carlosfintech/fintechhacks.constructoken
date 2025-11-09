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


class EmailDomainBlockBase(BaseSchema):
    domain: Optional[str] = Field(
        None,
        description="EmailDomain of the account to block, something like `example.org`.",
    )
    creator_id: ULID = Field(..., description="Creator account which controls this Actor.")
    model_config = ConfigDict(from_attributes=True)


class EmailDomainBlockCreate(EmailDomainBlockBase):
    pass


class EmailDomainBlockUpdate(EmailDomainBlockCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class EmailDomainBlock(EmailDomainBlockUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")
