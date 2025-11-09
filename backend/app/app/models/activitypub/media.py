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
from sqlalchemy import ForeignKey, String, DateTime, Table, Column
from sqlalchemy_utils import LocaleType
from babel import Locale
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM

from app.db.base_class import Base, generate_ULID
from app.schema_types import MediaType

if TYPE_CHECKING:
    from .actor import Actor  # noqa: F401
    from .status import Status  # noqa: F401


media_attachments_association_table = Table(
    "media_attachments_association_table",
    Base.metadata,
    Column("attachment_id", ForeignKey("mediaattachment.id"), primary_key=True),
    Column("status_id", ForeignKey("status.id"), primary_key=True),
)


class MediaAttachment(Base):
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    URL: Mapped[Optional[str]] = mapped_column(nullable=True)  # local link
    remoteURL: Mapped[Optional[str]] = mapped_column(nullable=True)  # remote link
    type: Mapped[ENUM[MediaType]] = mapped_column(ENUM(MediaType), nullable=True)
    path: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)  # local file path
    content_type: Mapped[Optional[str]] = mapped_column(nullable=True)  # mime type
    file_size: Mapped[Optional[int]] = mapped_column(nullable=True)  # file size in bytes
    thumbnail: Mapped[bool] = mapped_column(default=False, nullable=True)
    as_avatar: Mapped[bool] = mapped_column(default=False, nullable=True)
    as_standout: Mapped[bool] = mapped_column(default=False, nullable=True)
    # DESCRIPTION BY LOCALE
    text: Mapped[dict[str | Locale, "MediaDescription"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    # REFERENCES
    actor_avatar_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    actor_avatar: Mapped[Optional["Actor"]] = relationship(
        back_populates="icon",
        foreign_keys=[actor_avatar_id],
        single_parent=True,
    )
    actor_standout_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    actor_standout: Mapped[Optional["Actor"]] = relationship(
        back_populates="standout",
        foreign_keys=[actor_standout_id],
        single_parent=True,
    )
    status: Mapped[list["Status"]] = relationship(
        secondary="media_attachments_association_table", back_populates="attachments"
    )


class MediaDescription(Base):
    # A combination of Dictionary Collection and TSVector searchable term
    # https://docs.sqlalchemy.org/en/20/orm/collection_api.html#dictionary-collections
    # https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.locale
    # Access this term using:
    #       mediaattachment.text[locale]
    # Where `locale` is a Babel type.
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    media_id: Mapped[str] = mapped_column(ForeignKey("mediaattachment.id", onupdate="CASCADE", ondelete="CASCADE"))
    media: Mapped["MediaAttachment"] = relationship(back_populates="text", foreign_keys=[media_id])
    text: Mapped[Optional[str]] = mapped_column(nullable=True)
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)

    def __init__(self, language: str | Locale, text: str, back_ref: MediaAttachment | None = None):
        self.language = language
        self.text = text
        if back_ref:
            self.mediaattachment = back_ref
