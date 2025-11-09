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
from sqlalchemy_utils import Currency, CurrencyType, Country, CountryType
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM

from app.db.base_class import Base, generate_ULID
from app.schema_types import ProductFeeResponsibilityType, ProductType

if TYPE_CHECKING:
    from ..creator import Creator  # noqa: F401
    from ..product.product import Product  # noqa: F401
    from ..product.price import Price  # noqa: F401
    from .wallet import OpenWallet  # noqa: F401
    from .order import OpenOrder  # noqa: F401
    from .recipient import OpenRecipient  # noqa: F401


class OpenReceipt(Base):
    """
    An Open Payments product receipt, defining the final payment details.

    https://openpayments.dev/guides/make-onetime-payment/
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    # PRODUCT DETAILS
    product_id: Mapped[str] = mapped_column(ForeignKey("product.id"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="receipts", foreign_keys=[product_id])
    price_id: Mapped[str] = mapped_column(ForeignKey("price.id"), nullable=False)
    price: Mapped["Price"] = relationship(back_populates="receipts", foreign_keys=[price_id])
    type: Mapped[ENUM[ProductType]] = mapped_column(ENUM(ProductType), nullable=False, default=ProductType.OneTime)
    country: Mapped[Country] = mapped_column(CountryType, nullable=False)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fees: Mapped[Optional[ENUM[ProductFeeResponsibilityType]]] = mapped_column(
        ENUM(ProductFeeResponsibilityType), nullable=True, default=ProductFeeResponsibilityType.Seller
    )
    # BUYER AND RECIPIENT DETAILS
    buyer_id: Mapped[str] = mapped_column(ForeignKey("openwallet.id"), nullable=False)
    buyer: Mapped["OpenWallet"] = relationship(back_populates="receipts", foreign_keys=[buyer_id])
    creator_id: Mapped[Optional[str]] = mapped_column(ForeignKey("creator.id"), nullable=True)
    creator: Mapped[Optional["Creator"]] = relationship(back_populates="op_receipts", foreign_keys=[creator_id])
    # split bills are possible https://openpayments.dev/guides/split-payments/
    recipients: Mapped[list["OpenRecipient"]] = relationship(
        foreign_keys="[OpenRecipient.receipt_id]",
        order_by="OpenRecipient.created",
        back_populates="receipt",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    # ORDER WORKFLOW
    order_id: Mapped[str] = mapped_column(ForeignKey("openorder.id"), nullable=False)
    order: Mapped["OpenOrder"] = relationship(back_populates="receipts", foreign_keys=[order_id])
    amount: Mapped[str] = mapped_column(nullable=False)
    assetCode: Mapped[Currency] = mapped_column(CurrencyType, nullable=False)
    assetScale: Mapped[int] = mapped_column(nullable=False, default=2)
