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

from app.schemas.base_schema import BaseSchema, CountryListType, CurrencyType
from app.schema_types import ProductFeeResponsibilityType


class PriceBase(BaseSchema):
    created: Optional[datetime] = Field(None, description="Automatically generated date was first created.")
    amount: str = Field(..., description="Price is an unsigned 64-bit integer amount, represented as a string.")
    currency: CurrencyType = Field(..., description="This must be an ISO4217 currency code.")
    scale: int = Field(
        ..., description="Number of decimal places defining the scale of the smallest divisible currency unit."
    )
    countries: Optional[list[CountryListType]] = Field([], description="List of countries where this price is valid.")
    fees: ProductFeeResponsibilityType = Field(
        default=ProductFeeResponsibilityType.Seller,
        description="Who will pay the transaction fees? Default is the seller.",
    )
    product_id: Optional[ULID] = Field(None, description="Price is associated with this Product.")
    model_config = ConfigDict(from_attributes=True)


class PriceCreate(PriceBase):
    pass


class PriceUpdate(PriceBase):
    id: ULID = Field(..., description="Automatically generated unique identity.")
    updated: Optional[datetime] = Field(None, description="Automatically generated date was updated.")


class Price(PriceUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")
