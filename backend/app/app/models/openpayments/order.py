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
from sqlalchemy_utils import Country, CountryType
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, ENUM

from app.db.base_class import Base, generate_ULID
from app.schema_types import ProductFeeResponsibilityType, RenewalType

if TYPE_CHECKING:
    from ..creator import Creator  # noqa: F401
    from ..product.product import Product  # noqa: F401
    from ..product.price import Price  # noqa: F401
    from .wallet import OpenWallet  # noqa: F401
    from .receipt import OpenReceipt  # noqa: F401


class OpenOrder(Base):
    """
    An Open Payments product order, defining the ordering and grant-making process.

    https://openpayments.dev/guides/make-onetime-payment/
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    # PRODUCT DETAILS
    product_id: Mapped[str] = mapped_column(ForeignKey("product.id"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="orders", foreign_keys=[product_id])
    price_id: Mapped[str] = mapped_column(ForeignKey("price.id"), nullable=False)
    price: Mapped["Price"] = relationship(back_populates="orders", foreign_keys=[price_id])
    country: Mapped[Country] = mapped_column(CountryType, nullable=False)
    renewal: Mapped[Optional[ENUM[RenewalType]]] = mapped_column(ENUM(RenewalType), nullable=True)
    renewal_periods: Mapped[Optional[int]] = mapped_column(nullable=True)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    cancelled: Mapped[bool] = mapped_column(default=False, nullable=False)
    fees: Mapped[Optional[ENUM[ProductFeeResponsibilityType]]] = mapped_column(
        ENUM(ProductFeeResponsibilityType), nullable=True, default=ProductFeeResponsibilityType.Seller
    )
    # BUYER DETAILS
    buyer_id: Mapped[str] = mapped_column(ForeignKey("openwallet.id"), nullable=False)
    buyer: Mapped["OpenWallet"] = relationship(back_populates="orders", foreign_keys=[buyer_id])
    creator_id: Mapped[Optional[str]] = mapped_column(ForeignKey("creator.id"), nullable=True)
    creator: Mapped[Optional["Creator"]] = relationship(back_populates="op_orders", foreign_keys=[creator_id])
    # ORDER WORKFLOW
    # key-value pairs for use as attachments, cf https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
    incoming_payments: Mapped[Optional[list[any]]] = mapped_column(ARRAY(JSONB), nullable=True)
    incoming_quotes: Mapped[Optional[list[any]]] = mapped_column(ARRAY(JSONB), nullable=True)
    interactive_outgoings: Mapped[Optional[list[any]]] = mapped_column(ARRAY(JSONB), nullable=True)
    receipts: Mapped[list["OpenReceipt"]] = relationship(
        foreign_keys="[OpenReceipt.order_id]",
        order_by="OpenReceipt.created",
        back_populates="order",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
