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

from typing import TYPE_CHECKING, Optional, Final
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship, attribute_keyed_dict
from sqlalchemy import ForeignKey, String, DateTime, Computed, Index, Table, Column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy_utils import LocaleType, TSVectorType
from babel import Locale
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM

from app.db.base_class import Base, generate_ULID
from app.schema_types import VisibilityType

if TYPE_CHECKING:
    from .actor import Actor  # noqa: F401
    from .media import MediaAttachment, media_attachments_association_table  # noqa: F401
    from .moderation_report import Report, report_status_association_table  # noqa: F401
    from .tag import Tag  # noqa: F401
    from .mention import Mention  # noqa: F401
    from .thread import Thread  # noqa: F401
    from .like import Like  # noqa: F401
    from .bookmark import Bookmark  # noqa: F401


class Status(Base):
    """
    Represents a 'post' or 'status', either remote or local. Can be offered in multiple languages.

    ref: https://www.w3.org/TR/activitystreams-vocabulary/#object-types
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    fetched: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # For remote status which are updated remotely
    pinned: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    # MESSAGE CONTENT
    local: Mapped[bool] = mapped_column(default=False, nullable=True)  # From a local account
    URI: Mapped[Optional[str]] = mapped_column(index=True, unique=True, nullable=False)  # ActivityPub URI
    URL: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)  # Web URL
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)  # Default language ... can set others
    content_header: Mapped[dict[str | Locale, "StatusContentHeader"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    content: Mapped[dict[str | Locale, "StatusContent"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    content_header_raw: Mapped[dict[str | Locale, "StatusContentHeaderRaw"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    content_raw: Mapped[dict[str | Locale, "StatusContentRaw"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    is_markdown: Mapped[bool] = mapped_column(default=False, nullable=True)  # for processing the content
    attachments: Mapped[list["MediaAttachment"]] = relationship(
        secondary="media_attachments_association_table", back_populates="status"
    )
    tg: Mapped[list["Tag"]] = relationship(secondary=lambda: status_tag_table)
    tag: AssociationProxy[list[str]] = association_proxy("tg", "name")
    mentions: Mapped[list["Mention"]] = relationship(
        foreign_keys="[Mention.status_id]", back_populates="status", lazy="select"
    )
    sensitive: Mapped[bool] = mapped_column(default=False, nullable=True)
    visibility: Mapped[ENUM[VisibilityType]] = mapped_column(
        ENUM(VisibilityType), nullable=False, default=VisibilityType.Unlocked
    )
    edited: Mapped[bool] = mapped_column(default=False, nullable=True)
    # ASSOCIATIONS AND OWNERSHIP
    actor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    actor: Mapped[Optional["Actor"]] = relationship(back_populates="status", foreign_keys=[actor_id])
    actorURI: Mapped[Optional[str]] = mapped_column(index=True, nullable=True)  # ActivityPub Actor URI
    reply_id: Mapped[Optional[str]] = mapped_column(ForeignKey("status.id"), nullable=True)
    reply: Mapped[Optional["Status"]] = relationship(foreign_keys=[reply_id])
    inReplyToURI: Mapped[Optional[str]] = mapped_column(nullable=True)
    replyURI: Mapped[Optional[str]] = mapped_column(nullable=True)
    reply_actor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    reply_actor: Mapped[Optional["Actor"]] = relationship(back_populates="replies", foreign_keys=[reply_actor_id])
    reply_actor_URI: Mapped[Optional[str]] = mapped_column(nullable=True)
    share_id: Mapped[Optional[str]] = mapped_column(ForeignKey("status.id"), nullable=True)
    share: Mapped[Optional["Status"]] = relationship(foreign_keys=[share_id])
    sharesURI: Mapped[Optional[str]] = mapped_column(nullable=True)  # link to Collection counts for shares
    share_actor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    share_actor: Mapped[Optional["Actor"]] = relationship(back_populates="shares", foreign_keys=[share_actor_id])
    share_actor_URI: Mapped[Optional[str]] = mapped_column(nullable=True)
    thread_id: Mapped[Optional[str]] = mapped_column(ForeignKey("thread.id"), nullable=True)
    thread: Mapped[Optional["Thread"]] = relationship(back_populates="status", foreign_keys=[thread_id])
    threadURI: Mapped[Optional[str]] = mapped_column(nullable=True)
    likes: Mapped[list["Like"]] = relationship(foreign_keys="[Like.status_id]", back_populates="status", lazy="select")
    likesURI: Mapped[Optional[str]] = mapped_column(nullable=True)
    bookmarks: Mapped[list["Bookmark"]] = relationship(
        foreign_keys="[Bookmark.status_id]", back_populates="status", lazy="select"
    )
    # MODERATION
    reports: Mapped[list["Report"]] = relationship(secondary="report_status_association_table", back_populates="status")


class StatusContentHeader(Base):
    """
    For search of the header ("content warning").
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    status_id: Mapped[str] = mapped_column(ForeignKey("status.id", onupdate="CASCADE", ondelete="CASCADE"))
    status: Mapped["Status"] = relationship(back_populates="content_header", foreign_keys=[status_id])
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    content_header: Mapped[Optional[str]] = mapped_column(nullable=True)
    content_header_vector: Mapped[TSVectorType] = mapped_column(
        TSVectorType("content_header", regconfig="pg_catalog.simple"),
        Computed("to_tsvector('pg_catalog.simple', \"content_header\")", persisted=True),
        nullable=True,
    )

    __table_args__ = (
        # Indexing the TSVector column
        Index("ix_status_content_header_vector", content_header_vector, postgresql_using="gin"),
    )

    def __init__(self, language: str | Locale, content_header: str, back_ref: Status | None = None):
        self.language = language
        self.content_header = content_header
        if back_ref:
            self.status = back_ref


class StatusContent(Base):
    """
    For search of the content.
    """

    # A combination of Dictionary Collection and TSVector searchable term
    # https://docs.sqlalchemy.org/en/20/orm/collection_api.html#dictionary-collections
    # https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.locale
    # https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.ts_vector
    # Access this term using:
    #       status.content[locale]
    # Where `locale` is a Babel type.
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    status_id: Mapped[str] = mapped_column(ForeignKey("status.id", onupdate="CASCADE", ondelete="CASCADE"))
    status: Mapped["Status"] = relationship(back_populates="content", foreign_keys=[status_id])
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(nullable=True)
    content_vector: Mapped[TSVectorType] = mapped_column(
        TSVectorType("content", regconfig="pg_catalog.simple"),
        Computed("to_tsvector('pg_catalog.simple', \"content\")", persisted=True),
        nullable=True,
    )

    __table_args__ = (
        # Indexing the TSVector column
        Index("ix_status_content_vector", content_vector, postgresql_using="gin"),
    )

    def __init__(self, language: str | Locale, content: str, back_ref: Status | None = None):
        self.language = language
        self.content = content
        if back_ref:
            self.status = back_ref


class StatusContentHeaderRaw(Base):
    """
    For editing of the original header ("content warning").
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    status_id: Mapped[str] = mapped_column(ForeignKey("status.id", onupdate="CASCADE", ondelete="CASCADE"))
    status: Mapped["Status"] = relationship(back_populates="content_header_raw", foreign_keys=[status_id])
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    content_header_raw: Mapped[Optional[str]] = mapped_column(nullable=True)

    def __init__(self, language: str | Locale, content_header_raw: str, back_ref: Status | None = None):
        self.language = language
        self.content_header_raw = content_header_raw
        if back_ref:
            self.status = back_ref


class StatusContentRaw(Base):
    """
    For editing of the original content.
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    status_id: Mapped[str] = mapped_column(ForeignKey("status.id", onupdate="CASCADE", ondelete="CASCADE"))
    status: Mapped["Status"] = relationship(back_populates="content_raw", foreign_keys=[status_id])
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    content_raw: Mapped[Optional[str]] = mapped_column(nullable=True)

    def __init__(self, language: str | Locale, content_raw: str, back_ref: Status | None = None):
        self.language = language
        self.content_raw = content_raw
        if back_ref:
            self.status = back_ref


status_tag_table: Final[Table] = Table(
    "status_tag",
    Base.metadata,
    Column("status_id", String, ForeignKey("status.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tag.id"), primary_key=True),
)
