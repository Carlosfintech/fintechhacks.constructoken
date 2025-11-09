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
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Computed, Index
from sqlalchemy.sql import func
from sqlalchemy_utils import LocaleType, TSVectorType
from babel import Locale

from app.db.base_class import Base, generate_ULID

if TYPE_CHECKING:
    from .actor import Actor, actor_tag_table, follow_tag_table  # noqa: F401
    from .status import Status, status_tag_table  # noqa: F401


class Tag(Base):
    """
    Hashtags
    """

    # Sort of but not quite: https://docs.sqlalchemy.org/en/20/_modules/examples/graphs/directed_graph.html
    # https://docs.sqlalchemy.org/en/20/orm/extensions/associationproxy.html
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(index=True, unique=True)
    name_vector: Mapped[TSVectorType] = mapped_column(
        TSVectorType("name", regconfig="pg_catalog.simple"),
        Computed("to_tsvector('pg_catalog.simple', \"name\")", persisted=True),
        nullable=True,
    )
    local: Mapped[bool] = mapped_column(default=False, nullable=True)  # Tag is local to this instance.
    usable: Mapped[bool] = mapped_column(default=False, nullable=True)  # Tag is useable on this instance.
    listable: Mapped[bool] = mapped_column(
        default=True, nullable=True
    )  # Tagged statuses can be listed on this instance.

    __table_args__ = (
        # Indexing the TSVector column
        Index("ix_tag_name_vector", name_vector, postgresql_using="gin"),
    )
