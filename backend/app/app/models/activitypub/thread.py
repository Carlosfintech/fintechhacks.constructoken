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

from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from app.db.base_class import Base, generate_ULID

if TYPE_CHECKING:
    from .status import Status  # noqa: F401
    from .thread_mute import ThreadMute  # noqa: F401


class Thread(Base):
    """
    A thread of posts.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    status: Mapped[list["Status"]] = relationship(
        foreign_keys="[Status.thread_id]", back_populates="thread", lazy="select"
    )
    mutes: Mapped[list["ThreadMute"]] = relationship(
        foreign_keys="[ThreadMute.thread_id]", back_populates="thread", lazy="select"
    )
