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

# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base, generate_ULID  # noqa
from app.models.creator import Creator  # noqa
from app.models.token import Token  # noqa

###################################################################################################
# ACTIVITYSTREAMS OBJECTS
###################################################################################################
from app.models.activitypub.actor import (  # noqa: F401
    Actor,
    ActorSummary,
    ActorSummaryRaw,
    actor_tag_table,
    follow_tag_table,
)
from app.models.activitypub.actor_mute import ActorMute  # noqa: F401
from app.models.activitypub.actor_settings import ActorSettings  # noqa: F401
from app.models.activitypub.status import (  # noqa: F401
    Status,
    StatusContentHeader,
    StatusContentHeaderRaw,
    StatusContent,
    StatusContentRaw,
    status_tag_table,
)
from app.models.activitypub.block import Block  # noqa: F401
from app.models.activitypub.bookmark import Bookmark  # noqa: F401
from app.models.activitypub.domain_allow import DomainAllow, DomainAllowText  # noqa: F401
from app.models.activitypub.domain_block import DomainBlock, DomainBlockText  # noqa: F401
from app.models.activitypub.email_domain_block import EmailDomainBlock  # noqa: F401
from app.models.activitypub.follow import Follow  # noqa: F401
from app.models.activitypub.like import Like  # noqa: F401
from app.models.activitypub.media import (  # noqa: F401
    MediaAttachment,
    MediaDescription,
    media_attachments_association_table,
)
from app.models.activitypub.mention import Mention  # noqa: F401
from app.models.activitypub.moderation_report import (  # noqa: F401
    Report,
    report_action_association_table,
    report_rule_association_table,
    report_status_association_table,
)
from app.models.activitypub.moderator_action import ModeratorAction  # noqa: F401
from app.models.activitypub.move import Move  # noqa: F401
from app.models.activitypub.notification import Notification  # noqa: F401
from app.models.activitypub.rule import Rule, RuleText  # noqa: F401
from app.models.activitypub.tag import Tag  # noqa: F401
from app.models.activitypub.thread import Thread  # noqa: F401
from app.models.activitypub.thread_mute import ThreadMute  # noqa: F401
from app.models.activitypub.tombstone import Tombstone  # noqa: F401

###################################################################################################
# PRODUCT OBJECTS
###################################################################################################
from app.models.product.product import Product, ProductName, ProductDescription  # noqa: F401
from app.models.product.price import Price  # noqa: F401
from app.models.product.contributor import Contributor, ContributorTerms  # noqa: F401
from app.models.product.asset import Asset  # noqa: F401

###################################################################################################
# OPENPAYMENTS OBJECTS
###################################################################################################
from app.models.openpayments.wallet import OpenWallet  # noqa: F401
from app.models.openpayments.order import OpenOrder  # noqa: F401
from app.models.openpayments.receipt import OpenReceipt  # noqa: F401
from app.models.openpayments.recipient import OpenRecipient  # noqa: F401
