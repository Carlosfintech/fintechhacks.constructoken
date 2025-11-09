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
from sqlalchemy_utils import LocaleType, CountryType, Country, Currency, CurrencyType
from babel import Locale
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM, ARRAY

# from sqlalchemy.ext.mutable import MutableDict
# import json

from app.db.base_class import Base, generate_ULID
from app.schema_types import ProductContributorRoleType


if TYPE_CHECKING:
    from .product import Product  # noqa: F401
    from ..activitypub.actor import Actor  # noqa: F401


class Contributor(Base):
    """
    A contributing Actor to a product which can be bought and / or distributed.

    `ratio` for all contributing Actors must total 1.0. Validation is left to the CRUD class.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    role: Mapped[ENUM[ProductContributorRoleType]] = mapped_column(
        ENUM(ProductContributorRoleType), nullable=False, default=ProductContributorRoleType.Creator
    )
    terms: Mapped[dict[str | Locale, "ContributorTerms"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    ratio: Mapped[Optional[float]] = mapped_column(nullable=True)
    limit_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    limit_currency: Mapped[Optional[Currency]] = mapped_column(CurrencyType, nullable=True)
    limit_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    countries: Mapped[Optional[list[Country]]] = mapped_column(ARRAY(CountryType), nullable=True)
    # FOREIGN KEYS AND RELATIONSHIPS
    product_id: Mapped[Optional[str]] = mapped_column(ForeignKey("product.id"), nullable=True)
    product: Mapped[Optional["Product"]] = relationship(back_populates="contributors", foreign_keys=[product_id])
    actor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    actor: Mapped[Optional["Actor"]] = relationship(back_populates="contributions", foreign_keys=[actor_id])


class ContributorTerms(Base):
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    contributor_id: Mapped[str] = mapped_column(ForeignKey("contributor.id", onupdate="CASCADE", ondelete="CASCADE"))
    contributor: Mapped["Contributor"] = relationship(back_populates="terms", foreign_keys=[contributor_id])
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    terms: Mapped[Optional[str]] = mapped_column(nullable=True)

    def __init__(self, language: str | Locale, terms: str, back_ref: Contributor | None = None):
        self.language = language
        self.terms = terms
        if back_ref:
            self.asset = back_ref
