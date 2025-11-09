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
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy_utils import Currency, CurrencyType, CountryType, Country
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM, ARRAY

# from sqlalchemy.ext.mutable import MutableDict
# import json

from app.db.base_class import Base, generate_ULID
from app.schema_types import ProductFeeResponsibilityType


if TYPE_CHECKING:
    from .product import Product  # noqa: F401
    from ..openpayments.order import OpenOrder  # noqa: F401
    from ..openpayments.receipt import OpenReceipt  # noqa: F401
    from ..openpayments.recipient import OpenRecipient  # noqa: F401


class Price(Base):
    """
    A product asset, defining a digital object which can be bought and / or distributed.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    amount: Mapped[str] = mapped_column(nullable=False)
    currency: Mapped[Currency] = mapped_column(CurrencyType, nullable=False)
    scale: Mapped[int] = mapped_column(nullable=False, default=2)
    countries: Mapped[Optional[list[Country]]] = mapped_column(ARRAY(CountryType), nullable=True)
    fees: Mapped[Optional[ENUM[ProductFeeResponsibilityType]]] = mapped_column(
        ENUM(ProductFeeResponsibilityType), nullable=True, default=ProductFeeResponsibilityType.Seller
    )
    # FOREIGN KEYS AND RELATIONSHIPS
    product_id: Mapped[Optional[str]] = mapped_column(ForeignKey("product.id"), nullable=True)
    product: Mapped[Optional["Product"]] = relationship(back_populates="prices", foreign_keys=[product_id])
    # OPENPAYMENTS - ORDERS AND RECEIPTS
    orders: Mapped[list["OpenOrder"]] = relationship(
        foreign_keys="[OpenOrder.price_id]",
        order_by="OpenOrder.created",
        back_populates="price",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    receipts: Mapped[list["OpenReceipt"]] = relationship(
        foreign_keys="[OpenReceipt.price_id]",
        order_by="OpenReceipt.created",
        back_populates="price",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    recipients: Mapped[list["OpenRecipient"]] = relationship(
        foreign_keys="[OpenRecipient.price_id]",
        order_by="OpenRecipient.created",
        back_populates="price",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
