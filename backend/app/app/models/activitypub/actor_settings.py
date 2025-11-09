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
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM

from app.db.base_class import Base, generate_ULID
from app.schema_types import VisibilityType

if TYPE_CHECKING:
    from .actor import Actor  # noqa: F401


class ActorSettings(Base):
    """
    Represents either a local or remote ActivityPub actor. For local, represents both creators and works.

    ref: https://www.w3.org/TR/activitypub/#actor-objects
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    # SETTINGS
    privacy: Mapped[ENUM[VisibilityType]] = mapped_column(
        ENUM(VisibilityType), nullable=False, default=VisibilityType.Unlocked
    )
    sensitive: Mapped[bool] = mapped_column(default=False, nullable=True)  # Posts by this account marked as sensitive
    hide_collections: Mapped[bool] = mapped_column(default=False, nullable=True)  # Hide lists of Follows and Followers
    enable_rss: Mapped[bool] = mapped_column(default=False, nullable=True)  # Enable public RSS feed of Actor posts
    # ACTOR
    actor_id: Mapped[str] = mapped_column(ForeignKey("actor.id"))
    actor: Mapped["Actor"] = relationship(back_populates="settings")
