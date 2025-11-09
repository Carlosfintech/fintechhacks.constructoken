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
from sqlalchemy_utils import Currency, CurrencyType
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from app.db.base_class import Base, generate_ULID

if TYPE_CHECKING:
    from ..creator import Creator  # noqa: F401
    from ..product.product import Product  # noqa: F401
    from ..product.price import Price  # noqa: F401
    from .wallet import OpenWallet  # noqa: F401
    from .receipt import OpenReceipt  # noqa: F401


class OpenRecipient(Base):
    """
    An Open Payments payemnt to a recipient.

    https://openpayments.dev/guides/split-payments/
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    # RECIPIENT DETAILS
    wallet_id: Mapped[str] = mapped_column(ForeignKey("openwallet.id"), nullable=False)
    wallet: Mapped["OpenWallet"] = relationship(back_populates="recipients", foreign_keys=[wallet_id])
    creator_id: Mapped[Optional[str]] = mapped_column(ForeignKey("creator.id"), nullable=True)
    creator: Mapped[Optional["Creator"]] = relationship(back_populates="op_recipients", foreign_keys=[creator_id])
    # ORDER WORKFLOW
    product_id: Mapped[str] = mapped_column(ForeignKey("product.id"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="recipients", foreign_keys=[product_id])
    price_id: Mapped[str] = mapped_column(ForeignKey("price.id"), nullable=False)
    price: Mapped["Price"] = relationship(back_populates="recipients", foreign_keys=[price_id])
    receipt_id: Mapped[str] = mapped_column(ForeignKey("openreceipt.id"), nullable=False)
    receipt: Mapped["OpenReceipt"] = relationship(back_populates="recipients", foreign_keys=[receipt_id])
    amount: Mapped[float] = mapped_column(nullable=False)
    assetCode: Mapped[Currency] = mapped_column(CurrencyType, nullable=False)
    assetScale: Mapped[int] = mapped_column(nullable=False, default=2)
    payment_response: Mapped[Optional[list[any]]] = mapped_column(ARRAY(JSONB), nullable=True)
