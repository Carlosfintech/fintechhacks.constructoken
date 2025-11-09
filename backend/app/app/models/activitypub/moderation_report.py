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
from sqlalchemy import ForeignKey, DateTime, Table, Column, String
from sqlalchemy.sql import func
from sqlalchemy_utils import LocaleType
from babel import Locale

from app.db.base_class import Base, generate_ULID

if TYPE_CHECKING:
    from ..creator import Creator  # noqa: F401
    from .actor import Actor  # noqa: F401
    from .rule import Rule  # noqa: F401
    from .status import Status  # noqa: F401
    from .moderator_action import ModeratorAction  # noqa: F401


report_rule_association_table = Table(
    "report_rule_association_table",
    Base.metadata,
    Column("report_id", ForeignKey("report.id"), primary_key=True),
    Column("rule_id", ForeignKey("rule.id"), primary_key=True),
)


report_status_association_table = Table(
    "report_status_association_table",
    Base.metadata,
    Column("report_id", ForeignKey("report.id"), primary_key=True),
    Column("status_id", ForeignKey("status.id"), primary_key=True),
)

report_action_association_table = Table(
    "report_action_association_table",
    Base.metadata,
    Column("report_id", ForeignKey("report.id"), primary_key=True),
    Column("action_id", ForeignKey("moderatoraction.id"), primary_key=True),
)


class Report(Base):
    """
    Describes a report submitted raising a concern which must be reviewed and acted on by a moderator.

    May reference the rules alleged to have been infringed, and a moderator must action this with a specific
    response summary.

    Can be created locally, or submitted server-to-server via the API.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    # TYPE AND TARGET OF REPORT
    URI: Mapped[Optional[str]] = mapped_column(index=True, unique=True, nullable=False)  # ActivityPub URI
    submitter_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    submitter: Mapped[Optional["Actor"]] = relationship(back_populates="reports_submitted", foreign_keys=[submitter_id])
    actor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    actor: Mapped[Optional["Actor"]] = relationship(back_populates="moderator_reports", foreign_keys=[actor_id])
    rules: Mapped[list["Rule"]] = relationship(secondary="report_rule_association_table", back_populates="reports")
    status: Mapped[list["Status"]] = relationship(secondary="report_status_association_table", back_populates="reports")
    # MODERATOR RESPONSE
    text: Mapped[str] = mapped_column(nullable=True)
    actioned: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    actions: Mapped[list["ModeratorAction"]] = relationship(
        secondary="report_action_association_table", back_populates="reports"
    )
    forwarded: Mapped[bool] = mapped_column(default=False, nullable=True)
    moderator_id: Mapped[str] = mapped_column(ForeignKey("creator.id"), nullable=True)
    moderator: Mapped["Creator"] = relationship(back_populates="moderation_reports", foreign_keys=[moderator_id])
