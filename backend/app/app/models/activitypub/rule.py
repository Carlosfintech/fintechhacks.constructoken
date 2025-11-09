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
from sqlalchemy.sql import func
from sqlalchemy_utils import LocaleType
from babel import Locale

from app.db.base_class import Base, generate_ULID

if TYPE_CHECKING:
    from .moderation_report import Report, report_rule_association_table  # noqa: F401


class Rule(Base):
    """
    Rules governing the code of conduct for this service. Can be referenced when reporting or moderating activity.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    # RULE REFERENCE
    text: Mapped[dict[str | Locale, "RuleText"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    order: Mapped[int] = mapped_column()
    deleted: Mapped[bool] = mapped_column(default=False, nullable=True)
    # REFERENCED
    reports: Mapped[list["Report"]] = relationship(secondary="report_rule_association_table", back_populates="rules")


class RuleText(Base):
    # A combination of Dictionary Collection and TSVector searchable term
    # https://docs.sqlalchemy.org/en/20/orm/collection_api.html#dictionary-collections
    # https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.locale
    # Access this term using:
    #       rule.text[locale]
    # Where `locale` is a Babel type.
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    rule_id: Mapped[str] = mapped_column(ForeignKey("rule.id", onupdate="CASCADE", ondelete="CASCADE"))
    rule: Mapped["Rule"] = relationship(back_populates="text", foreign_keys=[rule_id])
    text: Mapped[Optional[str]] = mapped_column(nullable=True)
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)

    def __init__(self, language: str | Locale, text: str, back_ref: Rule | None = None):
        self.language = language
        self.text = text
        if back_ref:
            self.rule = back_ref
