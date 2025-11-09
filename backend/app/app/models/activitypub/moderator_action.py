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
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM

from app.db.base_class import Base, generate_ULID
from app.schema_types import ModeratorActionType, ModerationCategoryType

if TYPE_CHECKING:
    from ..creator import Creator  # noqa: F401
    from .actor import Actor  # noqa: F401
    from .moderation_report import Report, report_action_association_table  # noqa: F401


class ModeratorAction(Base):
    """
    Describes an action performed by a moderator on an entity. This includes actions related to:

    - Federation with domains
    - Moderating user and actor behaviour
    - Reviewing works offered for sale
    - Responding to purchase disputes
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    completed: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    # TYPE AND TARGET OF MODERATION
    category: Mapped[ENUM[ModerationCategoryType]] = mapped_column(ENUM(ModerationCategoryType), nullable=True)
    action: Mapped[ENUM[ModeratorActionType]] = mapped_column(ENUM(ModeratorActionType), nullable=True)
    # ACTION
    moderator_id: Mapped[str] = mapped_column(ForeignKey("creator.id"))
    moderator: Mapped["Creator"] = relationship(back_populates="moderation_actions", foreign_keys=[moderator_id])
    decision: Mapped[str] = mapped_column(nullable=True)
    send_email: Mapped[bool] = mapped_column(default=False, nullable=True)
    # REFERENCED TARGET
    domain: Mapped[Optional[str]] = mapped_column(index=True, nullable=True)
    creator_id: Mapped[Optional[str]] = mapped_column(ForeignKey("creator.id"), nullable=True)
    creator: Mapped[Optional["Creator"]] = relationship(back_populates="moderator_actions", foreign_keys=[creator_id])
    actor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    actor: Mapped[Optional["Actor"]] = relationship(back_populates="moderator_actions", foreign_keys=[actor_id])
    reports: Mapped[list["Report"]] = relationship(
        secondary="report_action_association_table", back_populates="actions"
    )
    errors: Mapped[str] = mapped_column(nullable=True)
