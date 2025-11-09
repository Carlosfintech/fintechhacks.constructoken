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

from app.db.base_class import Base, generate_ULID

if TYPE_CHECKING:
    from .actor import Actor  # noqa: F401
    from .thread import Thread  # noqa: F401


class ThreadMute(Base):
    """
    Muting of a thread of posts.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    actor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    actor: Mapped[Optional["Actor"]] = relationship(back_populates="threads_muted", foreign_keys=[actor_id])
    thread_id: Mapped[Optional[str]] = mapped_column(ForeignKey("thread.id"), nullable=True)
    thread: Mapped[Optional["Thread"]] = relationship(back_populates="mutes", foreign_keys=[thread_id])
