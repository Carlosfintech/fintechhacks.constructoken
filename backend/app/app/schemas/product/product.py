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
from typing_extensions import Self
from ulid import ULID
from pydantic import (
    ConfigDict,
    Field,
    model_validator,
)
from datetime import datetime

from app.schemas.base_schema import BaseSchema, LocaleType, CountryListType, CurrencyType
from app.schema_types import ProductType, ConditionType, RenewalType, ProductFeeResponsibilityType


class ProductBase(BaseSchema):
    # PRODUCT
    type: ProductType = Field(
        default=ProductType.OneTime, description="Defined Product types, default is 'OneTime' for one-time payment."
    )
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the language used. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    name: Optional[str] = Field(None, description="Language-defined name for the product Product.")
    description: Optional[str] = Field(None, description="Language-defined description for the Product.")
    # WORKFLOW
    actor_id: Optional[ULID] = Field(None, description="Actor managing this Product.")
    editor_id: Optional[ULID] = Field(None, description="Editor reviewing & approving this Product.")
    approved: bool = Field(False, description="Current approval state for this Product.")
    published: bool = Field(False, description="Current publication state for this Product.")
    # PRODUCT CONDITIONS
    start: Optional[datetime] = Field(None, description="Date after-which this product can be published.")
    end: Optional[datetime] = Field(None, description="Date after-which this product will no longer be published.")
    condition: Optional[ConditionType] = Field(
        None,
        description="Product requires meeting a conditional target, either a total amount raised, or a specific release.",
    )
    condition_total: Optional[float] = Field(
        None, description="If a conditional total is required, this is the amount."
    )
    # https://openpayments.dev/guides/outgoing-grant-future-payments/#about-the-interval
    renewal: Optional[RenewalType] = Field(
        None,
        description="Product is available as a periodic release, of a particular frequency or condition.",
    )
    renewal_periods: Optional[int] = Field(
        None,
        description="Count of how many times this Product will be automatically renewed when the purchaser buys (i.e. they're committing to this).",
    )
    allowed_countries: Optional[list[CountryListType]] = Field(
        [], description="List of countries where this contributor will receive payments."
    )
    blocked_countries: Optional[list[CountryListType]] = Field(
        [], description="List of countries where this contributor will receive payments."
    )
    # PRICES
    currency: CurrencyType = Field(
        ...,
        description="Default price currency choice. This must be an ISO4217 currency code.",
    )
    fees: ProductFeeResponsibilityType = Field(
        default=ProductFeeResponsibilityType.Seller,
        description="Who will pay the transaction fees? Default is the seller.",
    )
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def validate_conditions(self) -> Self:
        if self.condition_total is not None and self.condition != ConditionType.Amount:
            raise ValueError("Set `condition` to `ConditionType.Amount` when setting a `condition_total`.")
        if self.renewal_periods is not None and self.renewal is None:
            raise ValueError("Set `renewal` when setting `renewal_periods`.")
        return self


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    id: ULID = Field(..., description="Automatically generated unique identity.")
    updated: Optional[datetime] = Field(None, description="Automatically generated date was updated.")


class Product(ProductUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")
