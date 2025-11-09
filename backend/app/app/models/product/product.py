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

from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship, attribute_keyed_dict
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy_utils import LocaleType, Currency, CurrencyType, CountryType, Country
from babel import Locale
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM, ARRAY

# from sqlalchemy.ext.mutable import MutableDict
# import json

from app.db.base_class import Base, generate_ULID
from app.schema_types import ProductType, ConditionType, RenewalType, ProductFeeResponsibilityType


if TYPE_CHECKING:
    from ..activitypub.actor import Actor  # noqa: F401
    from .asset import Asset  # noqa: F401
    from .contributor import Contributor  # noqa: F401
    from .price import Price  # noqa: F401
    from ..openpayments.order import OpenOrder  # noqa: F401
    from ..openpayments.receipt import OpenReceipt  # noqa: F401
    from ..openpayments.recipient import OpenRecipient  # noqa: F401


class Product(Base):
    """
    An Open Payments product defining the conditions, terms and assets for a commercial item.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    # PRODUCT
    type: Mapped[ENUM[ProductType]] = mapped_column(ENUM(ProductType), nullable=False, default=ProductType.OneTime)
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)  # Default language ... can set others
    name: Mapped[dict[str | Locale, "ProductName"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    description: Mapped[dict[str | Locale, "ProductDescription"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    assets: Mapped[list["Asset"]] = relationship(
        foreign_keys="[Asset.product_id]",
        order_by="Asset.name",
        back_populates="product",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    contributors: Mapped[list["Contributor"]] = relationship(
        foreign_keys="[Contributor.product_id]",
        order_by="Contributor.role",
        back_populates="product",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    # WORKFLOW
    actor_id: Mapped[str] = mapped_column(ForeignKey("actor.id"))
    actor: Mapped[Optional["Actor"]] = relationship(back_populates="products", foreign_keys=[actor_id])
    editor_id: Mapped[str] = mapped_column(ForeignKey("actor.id"))
    editor: Mapped["Actor"] = relationship(back_populates="edits", foreign_keys=[editor_id])
    approved: Mapped[bool] = mapped_column(default=False, nullable=False)
    published: Mapped[bool] = mapped_column(default=False, nullable=False)
    # PRODUCT CONDITIONS
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    condition: Mapped[Optional[ENUM[ConditionType]]] = mapped_column(ENUM(ConditionType), nullable=True)
    condition_total: Mapped[Optional[float]] = mapped_column(nullable=True)
    # https://openpayments.dev/guides/outgoing-grant-future-payments/#about-the-interval
    renewal: Mapped[Optional[ENUM[RenewalType]]] = mapped_column(ENUM(RenewalType), nullable=True)
    renewal_periods: Mapped[Optional[int]] = mapped_column(nullable=True)
    allowed_countries: Mapped[Optional[list[Country]]] = mapped_column(ARRAY(CountryType), nullable=True)
    blocked_countries: Mapped[Optional[list[Country]]] = mapped_column(ARRAY(CountryType), nullable=True)
    # PRICES
    currency: Mapped[Currency] = mapped_column(CurrencyType, nullable=True)  # Default currency ...
    fees: Mapped[Optional[ENUM[ProductFeeResponsibilityType]]] = mapped_column(
        ENUM(ProductFeeResponsibilityType), nullable=True, default=ProductFeeResponsibilityType.Seller
    )
    prices: Mapped[list["Price"]] = relationship(
        foreign_keys="[Price.product_id]",
        back_populates="product",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    # OPENPAYMENTS - ORDERS AND RECEIPTS
    orders: Mapped[list["OpenOrder"]] = relationship(
        foreign_keys="[OpenOrder.product_id]",
        order_by="OpenOrder.created",
        back_populates="product",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    receipts: Mapped[list["OpenReceipt"]] = relationship(
        foreign_keys="[OpenReceipt.product_id]",
        order_by="OpenReceipt.created",
        back_populates="product",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    recipients: Mapped[list["OpenRecipient"]] = relationship(
        foreign_keys="[OpenRecipient.product_id]",
        order_by="OpenRecipient.created",
        back_populates="product",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class ProductName(Base):
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    product_id: Mapped[str] = mapped_column(ForeignKey("product.id", onupdate="CASCADE", ondelete="CASCADE"))
    product: Mapped["Product"] = relationship(back_populates="name", foreign_keys=[product_id])
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(nullable=True)

    def __init__(self, language: str | Locale, name: str, back_ref: Product | None = None):
        self.language = language
        self.name = name
        if back_ref:
            self.product = back_ref


class ProductDescription(Base):
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    product_id: Mapped[str] = mapped_column(ForeignKey("product.id", onupdate="CASCADE", ondelete="CASCADE"))
    product: Mapped["Product"] = relationship(back_populates="description", foreign_keys=[product_id])
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    def __init__(self, language: str | Locale, description: str, back_ref: Product | None = None):
        self.language = language
        self.description = description
        if back_ref:
            self.product = back_ref
