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

from app.schemas.base_schema import BaseSchema, LocaleType, CountryListType, CurrencyType
from app.schema_types import ProductContributorRoleType


class ContributorBase(BaseSchema):
    created: Optional[datetime] = Field(None, description="Automatically generated date was first created.")
    role: ProductContributorRoleType = Field(
        default=ProductContributorRoleType.Creator,
        description="Contributor role associated with the Product. Default is a creator.",
    )
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the language used. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    terms: Optional[str] = Field(
        None, description="Copyright or useage terms for the work related to this contributor."
    )
    ratio: Optional[float] = Field(
        None, description="Share of the selling price for each transaction paid to this contributor."
    )
    limit_value: Optional[float] = Field(None, description="Maximum amount of total sales paid to this contributor.")
    limit_currency: Optional[CurrencyType] = Field(
        None,
        description="Currency conversion of all prices paid to this contributor. Only meaningful with `limit_value`.",
    )
    limit_date: Optional[datetime] = Field(
        None, description="Date after-which this contributor will no longer receive payments."
    )
    countries: Optional[list[CountryListType]] = Field(
        [], description="List of countries where this contributor will receive payments."
    )
    actor_id: Optional[ULID] = Field(None, description="Actor associated with this Contributor.")
    product_id: Optional[ULID] = Field(None, description="Contributor is associated with this Product.")
    model_config = ConfigDict(from_attributes=True)


class ContributorCreate(ContributorBase):
    pass


class ContributorUpdate(ContributorBase):
    id: ULID = Field(..., description="Automatically generated unique identity.")
    updated: Optional[datetime] = Field(None, description="Automatically generated date was updated.")


class Contributor(ContributorUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")
