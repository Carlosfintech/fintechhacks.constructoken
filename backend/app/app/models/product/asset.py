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
from sqlalchemy_utils import LocaleType
from babel import Locale
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM

# from sqlalchemy.ext.mutable import MutableDict
# import json

from app.db.base_class import Base, generate_ULID
from app.schema_types import ProductAssetType


if TYPE_CHECKING:
    from .product import Product  # noqa: F401


class Asset(Base):
    """
    A product asset, defining a digital object which can be bought and / or distributed.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    type: Mapped[ENUM[ProductAssetType]] = mapped_column(
        ENUM(ProductAssetType), nullable=False, default=ProductAssetType.Download
    )
    language: Mapped[Optional[Locale]] = mapped_column(LocaleType, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    path: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)  # local file path
    # FOREIGN KEYS AND RELATIONSHIPS
    product_id: Mapped[Optional[str]] = mapped_column(ForeignKey("product.id"), nullable=True)
    product: Mapped[Optional["Product"]] = relationship(back_populates="assets", foreign_keys=[product_id])
