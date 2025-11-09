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

from app.db.base_class import Base, generate_ULID

if TYPE_CHECKING:
    from ..creator import Creator  # noqa: F401
    from .order import OpenOrder  # noqa: F401
    from .receipt import OpenReceipt  # noqa: F401
    from .recipient import OpenRecipient  # noqa: F401


class OpenWallet(Base):
    """
    A product asset, defining a digital object which can be bought and / or distributed.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    address: Mapped[str] = mapped_column(index=True, nullable=False)
    publicName: Mapped[Optional[str]] = mapped_column(nullable=True)
    assetCode: Mapped[Currency] = mapped_column(CurrencyType, nullable=False)
    assetScale: Mapped[int] = mapped_column(nullable=False, default=2)
    authServer: Mapped[Optional[str]] = mapped_column(nullable=True)
    resourceServer: Mapped[Optional[str]] = mapped_column(nullable=True)
    keyID: Mapped[Optional[str]] = mapped_column(nullable=True)
    privateKey: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    # FOREIGN KEYS AND RELATIONSHIPS
    creator_id: Mapped[Optional[str]] = mapped_column(ForeignKey("creator.id"), nullable=True)
    creator: Mapped[Optional["Creator"]] = relationship(back_populates="op_wallets", foreign_keys=[creator_id])
    # ORDERS AND RECEIPTS - AS BUYER
    orders: Mapped[list["OpenOrder"]] = relationship(
        foreign_keys="[OpenOrder.buyer_id]",
        order_by="OpenOrder.created",
        back_populates="buyer",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    receipts: Mapped[list["OpenReceipt"]] = relationship(
        foreign_keys="[OpenReceipt.buyer_id]",
        order_by="OpenReceipt.created",
        back_populates="buyer",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    # INCOME AND PAYMENTS - AS SELLER
    recipients: Mapped[list["OpenRecipient"]] = relationship(
        foreign_keys="[OpenRecipient.wallet_id]",
        order_by="OpenRecipient.created",
        back_populates="wallet",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
