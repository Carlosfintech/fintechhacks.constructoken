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

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from sqlalchemy.sql import func

from app.db.base_class import Base, generate_ULID


class Move(Base):
    """
    An ActivityPub "Move" activity received or created by this instance.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    attempted: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    succeeded: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    URI: Mapped[Optional[str]] = mapped_column(index=True, unique=True, nullable=False)  # ActivityPub URI move activity
    originURI: Mapped[Optional[str]] = mapped_column(
        index=True, unique=True, nullable=False
    )  # ActivityPub URI of the move origin
    targetURI: Mapped[Optional[str]] = mapped_column(
        index=True, unique=True, nullable=False
    )  # ActivityPub URI of the move target
