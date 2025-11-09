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

from .base_schema import (  # noqa: F401
    BaseSchema,
    ModelMeta,
    LocaleType,
    CountryType,
    CountryListType,
    CurrencyType,
)
from .msg import Msg  # noqa: F401
from .token import (  # noqa: F401
    Token,
    TokenCreate,
    TokenUpdate,
    TokenData,
    TokenPayload,
    MagicTokenPayload,
    WebToken,
)
from .creator import Creator, CreatorCreate, CreatorInDB, CreatorUpdate, CreatorLogin  # noqa: F401
from .emails import EmailContent, EmailValidation  # noqa: F401
from .totp import NewTOTP, EnableTOTP  # noqa: F401
from .location import CountryCode, IPCode  # noqa: F401

###################################################################################################
# ACTIVITYSTREAMS SCHEMAS
###################################################################################################
from .activitypub.protocol import WebFinger, NodeInfo, NodeInfoRoot  # noqa: F401
from .activitypub.actor import (  # noqa: F401
    ActorCreate,
    ActorUpdate,
    ActorMediaUpdate,
    ActorUpdateIn,
    ModeratorActorUpdate,
    ActivityActorCreate,
    ActorWorkSummary,
    Actor,
    ActorUpdateTest,
)
from .activitypub.activity import InboxActivity  # noqa: F401
from .activitypub.follow import FollowCreate, FollowUpdate, Follow  # noqa: F401
from .activitypub.tag import TagCreate, TagUpdate, Tag, ActivityTagCreate  # noqa: F401
from .activitypub.notification import NotificationCreate, NotificationUpdate, Notification  # noqa: F401
from .activitypub.actor_mute import ActorMuteCreate, ActorMuteUpdate, ActorMute  # noqa: F401
from .activitypub.actor_settings import ActorSettingsCreate, ActorSettingsUpdate, ActorSettings  # noqa: F401
from .activitypub.block import BlockCreate, BlockUpdate, Block  # noqa: F401
from .activitypub.bookmark import BookmarkCreate, BookmarkUpdate, Bookmark  # noqa: F401
from .activitypub.domain_allow import DomainAllowCreate, DomainAllowUpdate, DomainAllow  # noqa: F401
from .activitypub.domain_block import DomainBlockCreate, DomainBlockUpdate, DomainBlock  # noqa: F401
from .activitypub.email_domain_block import (  # noqa: F401
    EmailDomainBlockCreate,
    EmailDomainBlockUpdate,
    EmailDomainBlock,
)
from .activitypub.like import LikeCreate, LikeUpdate, Like  # noqa: F401
from .activitypub.media import MediaAttachmentCreate, MediaAttachmentUpdate, MediaAttachment  # noqa: F401
from .activitypub.mention import MentionCreate, MentionUpdate, Mention  # noqa: F401
from .activitypub.moderation_report import ReportCreate, ReportUpdate, Report  # noqa: F401
from .activitypub.moderator_action import ModeratorActionCreate, ModeratorActionUpdate, ModeratorAction  # noqa: F401
from .activitypub.move import MoveCreate, MoveUpdate, Move  # noqa: F401
from .activitypub.rule import RuleCreate, RuleUpdate, Rule  # noqa: F401
from .activitypub.status import StatusCreate, ActivityStatusCreate, StatusUpdate, Status  # noqa: F401
from .activitypub.thread_mute import ThreadMuteCreate, ThreadMuteUpdate, ThreadMute  # noqa: F401
from .activitypub.tombstone import TombstoneCreate, TombstoneUpdate, Tombstone  # noqa: F401

###################################################################################################
# PRODUCT SCHEMAS
###################################################################################################

from .product.product import ProductCreate, ProductUpdate, Product  # noqa: F401
from .product.price import PriceCreate, PriceUpdate, Price  # noqa: F401
from .product.contributor import ContributorCreate, ContributorUpdate, Contributor  # noqa: F401
from .product.asset import AssetCreate, AssetUpdate, Asset  # noqa: F401

###################################################################################################
# OPENPAYMENTS SCHEMAS
###################################################################################################

from .openpayments.wallet import OpenWalletCreate, OpenWalletUpdate, OpenWallet  # noqa: F401
from .openpayments.order import OpenOrderCreate, OpenOrderUpdate, OpenOrder  # noqa: F401
from .openpayments.receipt import OpenReceiptCreate, OpenReceiptUpdate, OpenReceipt  # noqa: F401
from .openpayments.recipient import OpenRecipientCreate, OpenRecipientUpdate, OpenRecipient  # noqa: F401
from .openpayments.open_payments import SellerOpenPaymentAccount, PendingIncomingPaymentTransaction  # noqa: F401

###################################################################################################
# GENERATOR - REMOVE AFTER DEVELOPMENT COMPLETE
###################################################################################################
from .generate import GeneratorCreator, GeneratorPersona  # noqa: F401
