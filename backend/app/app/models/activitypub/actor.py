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
from sqlalchemy import ForeignKey, String, DateTime, UniqueConstraint, Computed, Index, Table, Column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy_utils import LocaleType, TSVectorType
from babel import Locale
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM, JSONB

# from sqlalchemy.ext.mutable import MutableDict
# import json

from app.db.base_class import Base, generate_ULID
from app.schema_types import ActorType
from app.utilities.regexes import regex

from .follow import Follow  # noqa: F401
from .like import Like  # noqa: F401
from .status import Status  # noqa: F401
from .bookmark import Bookmark  # noqa: F401

if TYPE_CHECKING:
    from ..creator import Creator  # noqa: F401
    from .actor_settings import ActorSettings  # noqa: F401
    from .media import MediaAttachment  # noqa: F401
    from .moderator_action import ModeratorAction  # noqa: F401
    from .moderation_report import Report  # noqa: F401
    from .block import Block  # noqa: F401
    from .actor_mute import ActorMute  # noqa: F401
    from .tag import Tag  # noqa: F401
    from .mention import Mention  # noqa: F401
    from .thread_mute import ThreadMute  # noqa: F401
    from .notification import Notification  # noqa: F401
    from ..product.product import Product  # noqa: F401
    from ..product.contributor import Contributor  # noqa: F401


class Actor(Base):
    """
    Represents either a local or remote ActivityPub actor. For local, represents both creators and works.

    ref: https://www.w3.org/TR/activitypub/#actor-objects
    """

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True
    )
    fetched: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # For remote Actors which are updated remotely
    # ACTIVITYSTREAMS PROPERTIES
    type: Mapped[ENUM[ActorType]] = mapped_column(ENUM(ActorType), nullable=False, default=ActorType.Person)
    name: Mapped[str] = mapped_column(nullable=True)
    name_vector: Mapped[TSVectorType] = mapped_column(
        TSVectorType("name", regconfig="pg_catalog.simple"),
        Computed("to_tsvector('pg_catalog.simple', \"name\")", persisted=True),
        nullable=True,
    )
    preferredUsername: Mapped[str] = mapped_column(index=True, nullable=False)  # Used for @<preferredUsername>
    domain: Mapped[Optional[str]] = mapped_column(index=True, nullable=True)
    inbox: Mapped[str] = mapped_column(nullable=True)
    outbox: Mapped[str] = mapped_column(unique=True, nullable=True)
    sharedInbox: Mapped[Optional[str]] = mapped_column(nullable=True)
    following: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    followers: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    featured: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    liked: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    URI: Mapped[Optional[str]] = mapped_column(index=True, unique=True, nullable=False)  # ActivityPub URI
    URL: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)  # Actor Profile URL
    # MEDIA AND CONTENT PROPERTIES
    icon: Mapped[Optional["MediaAttachment"]] = relationship(
        back_populates="actor_avatar",
        foreign_keys="[MediaAttachment.actor_avatar_id]",
        cascade="all, delete-orphan",
        remote_side="MediaAttachment.actor_avatar_id",
    )
    iconURL: Mapped[Optional[str]] = mapped_column(nullable=True)  # Remote icon URL. Null for local.
    standout: Mapped[Optional["MediaAttachment"]] = relationship(
        back_populates="actor_standout",
        foreign_keys="[MediaAttachment.actor_standout_id]",
        cascade="all, delete-orphan",
        remote_side="MediaAttachment.actor_standout_id",
    )
    standoutURL: Mapped[Optional[str]] = mapped_column(nullable=True)  # Remote header URL. Null for local.
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)  # Default language ... can set others
    summary: Mapped[dict[str | Locale, "ActorSummary"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    summary_raw: Mapped[dict[str | Locale, "ActorSummaryRaw"]] = relationship(
        collection_class=attribute_keyed_dict("language"),
        cascade="all, delete-orphan",
    )
    tg: Mapped[list["Tag"]] = relationship(secondary=lambda: actor_tag_table, cascade="all, delete")
    tag: AssociationProxy[list[str]] = association_proxy("tg", "name")
    # key-value pairs for use as attachements, cf https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
    attachment: Mapped[Optional[any]] = mapped_column(JSONB, nullable=True)
    alsoKnownAs: Mapped[Optional[any]] = mapped_column(JSONB, nullable=True)
    # STATUSES
    status: Mapped[list["Status"]] = relationship(
        foreign_keys="[Status.actor_id]", back_populates="actor", lazy="dynamic", cascade="all, delete-orphan"
    )
    replies: Mapped[list["Status"]] = relationship(
        foreign_keys="[Status.reply_actor_id]",
        back_populates="reply_actor",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    shares: Mapped[list["Status"]] = relationship(
        foreign_keys="[Status.share_actor_id]",
        back_populates="share_actor",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        foreign_keys="[Notification.actor_id]", back_populates="actor", lazy="dynamic", cascade="all, delete-orphan"
    )
    # AUTHENTICATION AND PERSISTENCE
    privateKey: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    publicKey: Mapped[str] = mapped_column(unique=True, nullable=False)
    publicKeyURI: Mapped[str] = mapped_column(unique=True, nullable=False)
    # CREATOR TO MAKER TO WORK RELATIONSHIPS
    # creator: login and settings for an account, has control of actors of all types
    # maker: public actor persona responsible for creating and publishing works
    # work: public actor persona controlled by a maker
    creator_id: Mapped[Optional[str]] = mapped_column(ForeignKey("creator.id"), nullable=True)
    creator: Mapped[Optional["Creator"]] = relationship(back_populates="actors", foreign_keys=[creator_id])
    maker_id: Mapped[Optional[str]] = mapped_column(ForeignKey("actor.id"), nullable=True)
    maker: Mapped[Optional["Actor"]] = relationship(foreign_keys=[maker_id], remote_side="Actor.id")
    works: Mapped[list["Actor"]] = relationship(
        foreign_keys="[Actor.maker_id]",
        order_by="Actor.created",
        back_populates="maker",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    # RELATIONSHIPS
    following_actors: Mapped[list["Follow"]] = relationship(
        foreign_keys="[Follow.actor_id]", back_populates="actor", lazy="dynamic"
    )
    follower_actors: Mapped[list["Follow"]] = relationship(
        foreign_keys="[Follow.target_id]", back_populates="target", lazy="dynamic"
    )
    mentions: Mapped[list["Mention"]] = relationship(
        foreign_keys="[Mention.target_id]", back_populates="target", lazy="dynamic"
    )  # Mentions *of* this actor
    mentioned: Mapped[list["Mention"]] = relationship(
        foreign_keys="[Mention.actor_id]", back_populates="actor", lazy="dynamic"
    )  # Actors mentioned by this actor
    likes: Mapped[list["Like"]] = relationship(
        foreign_keys="[Like.target_id]", back_populates="target", lazy="dynamic"
    )  # Like *of* this actor's posts
    liked_list: Mapped[list["Like"]] = relationship(
        foreign_keys="[Like.actor_id]", back_populates="actor", lazy="dynamic"
    )  # Likes of posts *by* this actor
    bookmarks: Mapped[list["Bookmark"]] = relationship(
        foreign_keys="[Bookmark.target_id]", back_populates="target", lazy="dynamic"
    )  # Bookmarks *of* this actor's posts
    bookmarked: Mapped[list["Bookmark"]] = relationship(
        foreign_keys="[Bookmark.actor_id]", back_populates="actor", lazy="dynamic"
    )  # Bookmarks of posts *by* this actor
    follow_tg: Mapped[list["Tag"]] = relationship(secondary=lambda: follow_tag_table, cascade="all, delete")
    follow_tag: AssociationProxy[list[str]] = association_proxy("follow_tg", "name")
    blocking: Mapped[list["Block"]] = relationship(
        foreign_keys="[Block.actor_id]", back_populates="actor", lazy="dynamic"
    )
    blocked_by: Mapped[list["Block"]] = relationship(
        foreign_keys="[Block.target_id]", back_populates="target", lazy="dynamic"
    )
    muting: Mapped[list["ActorMute"]] = relationship(
        foreign_keys="[ActorMute.actor_id]", back_populates="actor", lazy="dynamic"
    )
    muted_by: Mapped[list["ActorMute"]] = relationship(
        foreign_keys="[ActorMute.target_id]", back_populates="target", lazy="dynamic"
    )
    threads_muted: Mapped[list["ThreadMute"]] = relationship(
        foreign_keys="[ThreadMute.actor_id]", back_populates="actor", lazy="dynamic"
    )
    # SETTINGS AND REPORTS
    locked: Mapped[bool] = mapped_column(default=False, nullable=True)  # Requires manual approval of followers
    discoverable: Mapped[bool] = mapped_column(default=False, nullable=True)  # Served for search and discovery
    memorial: Mapped[bool] = mapped_column(default=False, nullable=True)  # Actor has made their crossing
    settings: Mapped["ActorSettings"] = relationship(back_populates="actor")
    reports_submitted: Mapped[list["Report"]] = relationship(
        foreign_keys="[Report.submitter_id]", back_populates="submitter", lazy="dynamic"
    )
    default_persona: Mapped[bool] = mapped_column(default=False, nullable=True)  # Default Persona for a Creator
    # SECURITY AND MODERATION - THESE MAY BE SET BY MODS, NOT THE CREATOR
    memorialised: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Date account marked as a memorial
    sensitised: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Date account marked as sensitive
    silenced: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # Date account silenced
    suspended: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # Date account suspended
    moderator_actions: Mapped[list["ModeratorAction"]] = relationship(
        foreign_keys="[ModeratorAction.actor_id]", back_populates="actor", lazy="dynamic"
    )
    moderator_reports: Mapped[list["Report"]] = relationship(
        foreign_keys="[Report.actor_id]", back_populates="actor", lazy="dynamic"
    )
    # PRODUCTS - OWNER, EDITOR, CONTRIBUTOR
    # NOTE: `creator` have financial interactions, while `actor` have product interactions
    products: Mapped[list["Product"]] = relationship(
        foreign_keys="[Product.actor_id]",
        back_populates="actor",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    edits: Mapped[list["Product"]] = relationship(
        foreign_keys="[Product.editor_id]",
        back_populates="editor",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    contributions: Mapped[list["Contributor"]] = relationship(
        foreign_keys="[Contributor.actor_id]",
        back_populates="actor",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # UNIQUENESS CONSTRAINT
    __table_args__ = (
        UniqueConstraint("preferredUsername", "domain"),
        # Indexing the TSVector column
        Index("ix_actor_name_vector", name_vector, postgresql_using="gin"),
    )

    @property
    def is_local(self) -> bool:
        return regex.url_is_local(self.domain)

    # OTHER ACTORS
    def is_following(self, actor_id) -> bool:
        query_filter = Follow.actor_id == actor_id
        return self.following_actors.filter(query_filter).first() is not None

    def is_followed(self, actor_id) -> bool:
        query_filter = Follow.target_id == actor_id
        return self.follower_actors.filter(query_filter).first() is not None

    # OTHER STATUSES
    def has_liked(self, actor_id, status_id) -> bool:
        query_filter = Like.actor_id == actor_id
        query_filter &= Like.status_id == status_id
        return self.liked_list.filter(query_filter).first() is not None

    def has_bookmarked(self, actor_id, status_id) -> bool:
        query_filter = Bookmark.actor_id == actor_id
        query_filter &= Bookmark.status_id == status_id
        return self.liked_list.filter(query_filter).first() is not None

    def has_shared(self, actor_id, status_id) -> bool:
        query_filter = Status.share_actor_id == actor_id
        query_filter &= Status.id == status_id
        return self.shares.filter(query_filter).first() is not None


class ActorSummary(Base):
    # A combination of Dictionary Collection and TSVector searchable term
    # https://docs.sqlalchemy.org/en/20/orm/collection_api.html#dictionary-collections
    # https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.locale
    # https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.ts_vector
    # Access this term using:
    #       actor.summary[locale]
    # Where `locale` is a Babel type.
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    actor_id: Mapped[str] = mapped_column(ForeignKey("actor.id", onupdate="CASCADE", ondelete="CASCADE"))
    actor: Mapped["Actor"] = relationship(back_populates="summary", foreign_keys=[actor_id])
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(nullable=True)
    summary_vector: Mapped[TSVectorType] = mapped_column(
        TSVectorType("summary", regconfig="pg_catalog.simple"),
        Computed("to_tsvector('pg_catalog.simple', \"summary\")", persisted=True),
        nullable=True,
    )

    __table_args__ = (
        # Indexing the TSVector column
        Index("ix_actor_summary_vector", summary_vector, postgresql_using="gin"),
    )

    def __init__(self, language: str | Locale, summary: str, back_ref: Actor | None = None):
        self.language = language
        self.summary = summary
        if back_ref:
            self.actor = back_ref


class ActorSummaryRaw(Base):
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    actor_id: Mapped[str] = mapped_column(ForeignKey("actor.id", onupdate="CASCADE", ondelete="CASCADE"))
    actor: Mapped["Actor"] = relationship(back_populates="summary_raw", foreign_keys=[actor_id])
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    summary_raw: Mapped[Optional[str]] = mapped_column(nullable=True)

    def __init__(self, language: str | Locale, summary_raw: str, back_ref: Actor | None = None):
        self.language = language
        self.summary_raw = summary_raw
        if back_ref:
            self.actor = back_ref


actor_tag_table: Final[Table] = Table(
    "actor_tag",
    Base.metadata,
    Column("actor_id", String, ForeignKey("actor.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tag.id"), primary_key=True),
)


follow_tag_table: Final[Table] = Table(
    "follow_tag",
    Base.metadata,
    Column("actor_id", String, ForeignKey("actor.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tag.id"), primary_key=True),
)
