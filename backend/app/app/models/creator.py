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
from sqlalchemy import DateTime, String
from sqlalchemy.sql import func
from sqlalchemy_utils import LocaleType
from babel import Locale

from app.db.base_class import Base, generate_ULID
from app.schema_types import ActorType
from .activitypub.actor import Actor

if TYPE_CHECKING:
    from .token import Token  # noqa: F401
    from .activitypub.moderation_report import Report, report_action_association_table  # noqa: F401
    from .activitypub.moderator_action import ModeratorAction  # noqa: F401
    from .activitypub.domain_block import DomainBlock  # noqa: F401
    from .activitypub.domain_allow import DomainAllow  # noqa: F401
    from .activitypub.email_domain_block import EmailDomainBlock  # noqa: F401
    from .openpayments.wallet import OpenWallet  # noqa: F401
    from .openpayments.order import OpenOrder  # noqa: F401
    from .openpayments.receipt import OpenReceipt  # noqa: F401
    from .openpayments.recipient import OpenRecipient  # noqa: F401

    # from .creator_settings import CreatorSettings  # noqa: F401


class Creator(Base):
    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ULID)
    # ACTIVITY
    # https://github.com/sqlalchemy/sqlalchemy/discussions/10189
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )
    # METADATA
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(nullable=True)
    language: Mapped[Locale] = mapped_column(LocaleType, nullable=True)
    # AUTHENTICATION AND PERSISTENCE
    totp_secret: Mapped[Optional[str]] = mapped_column(nullable=True)
    totp_counter: Mapped[Optional[int]] = mapped_column(nullable=True)
    email_validated: Mapped[bool] = mapped_column(default=False)
    accepted_rules: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_disabled: Mapped[bool] = mapped_column(default=False)
    is_approved: Mapped[bool] = mapped_column(default=True)
    is_moderator: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    tokens: Mapped[list["Token"]] = relationship(
        foreign_keys="[Token.authenticates_id]", back_populates="authenticates", lazy="dynamic"
    )
    # ACTIVITYPUB ACTORS
    actors: Mapped[list["Actor"]] = relationship(
        foreign_keys="[Actor.creator_id]",
        order_by="Actor.created",
        back_populates="creator",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    # MODERATION - `moderator` = *to* this creator, `moderation` = *by* this creator
    moderation_reports: Mapped[list["Report"]] = relationship(
        foreign_keys="[Report.moderator_id]", back_populates="moderator", lazy="dynamic"
    )
    moderator_actions: Mapped[list["ModeratorAction"]] = relationship(
        foreign_keys="[ModeratorAction.creator_id]", back_populates="creator", lazy="dynamic"
    )
    moderation_actions: Mapped[list["ModeratorAction"]] = relationship(
        foreign_keys="[ModeratorAction.moderator_id]", back_populates="moderator", lazy="dynamic"
    )
    domain_blocks: Mapped[list["DomainBlock"]] = relationship(
        foreign_keys="[DomainBlock.creator_id]", back_populates="creator", lazy="dynamic"
    )
    domain_allows: Mapped[list["DomainAllow"]] = relationship(
        foreign_keys="[DomainAllow.creator_id]", back_populates="creator", lazy="dynamic"
    )
    email_domain_blocks: Mapped[list["EmailDomainBlock"]] = relationship(
        foreign_keys="[EmailDomainBlock.creator_id]", back_populates="creator", lazy="dynamic"
    )
    # OPENPAYMENTS TRANSACTIONS
    # NOTE: `creator` have financial interactions, while `actor` have product interactions
    op_wallets: Mapped[list["OpenWallet"]] = relationship(
        foreign_keys="[OpenWallet.creator_id]",
        order_by="OpenWallet.created",
        back_populates="creator",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    op_orders: Mapped[list["OpenOrder"]] = relationship(
        foreign_keys="[OpenOrder.creator_id]",
        order_by="OpenOrder.created",
        back_populates="creator",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    op_receipts: Mapped[list["OpenReceipt"]] = relationship(
        foreign_keys="[OpenReceipt.creator_id]",
        order_by="OpenReceipt.created",
        back_populates="creator",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    op_recipients: Mapped[list["OpenRecipient"]] = relationship(
        foreign_keys="[OpenRecipient.creator_id]",
        order_by="OpenRecipient.created",
        back_populates="creator",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @property
    def default_persona(self) -> Actor:
        query_filter = Actor.type == ActorType.Person
        query_filter &= Actor.default_persona.is_(True)
        return self.actors.filter(query_filter).first()

    def has_persona(self, actor_id) -> bool:
        query_filter = Actor.type == ActorType.Person
        query_filter &= Actor.id == actor_id
        return self.actors.filter(query_filter).first() is not None

    def has_work(self, actor_id) -> bool:
        query_filter = Actor.type == ActorType.Work
        query_filter &= Actor.id == actor_id
        return self.actors.filter(query_filter).first() is not None

    def get_actor_by_handle(self, handle) -> Actor:
        query_filter = Actor.preferredUsername == handle
        return self.actors.filter(query_filter).first()

    def get_actor_by_id(self, actor_id) -> Actor:
        query_filter = Actor.id == str(actor_id)
        return self.actors.filter(query_filter).first()
