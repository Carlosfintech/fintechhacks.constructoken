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

from typing import Optional, Any
from typing_extensions import Self
from ulid import ULID
from pydantic import (
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)
from datetime import datetime
from copy import deepcopy

from app.schemas.base_schema import BaseSchema, ModelMeta, LocaleType
from app.schemas.activitypub.actor import Actor
from app.schema_types import VisibilityType, ActivityType, ObjectLinkType
from app.utilities.regexes import regex
from app.utilities.parser import dataparser
from app.core.config import settings


class StatusBase(BaseSchema):
    URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI for this account.",
    )
    URL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile.",
    )
    local: Optional[bool] = Field(False, description="Apply mute to notifications as well as statuses.")
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the default language. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    content_header_raw: Optional[dict[str, str]] = Field(
        None, description="Original text of the content warning without formatting."
    )
    content_raw: Optional[dict[str, str]] = Field(None, description="Original text of the status without formatting.")
    tag: Optional[list[dict[str, str]]] = Field([], description="A list of topics of the pathway.")
    mentions: Optional[list[str]] = Field([], description="List of Actors mentioned in the Status.")
    is_markdown: Optional[bool] = Field(False, description="Whether the raw text should be processed as MarkDown.")
    sensitive: Optional[bool] = Field(False, description="Whether the status is marked as sensitive.")
    visibility: VisibilityType = Field(
        default=VisibilityType.Unlocked, description="Default post privacy for this status."
    )
    edited: Optional[bool] = Field(False, description="Whether the status has been edited.")
    actor_id: Optional[ULID] = Field(None, description="Actor who posted this status.")
    actorURI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI for this the creator of this status.",
    )
    reply_id: Optional[ULID] = Field(None, description="ID of the status this status replies to.")
    inReplyToURI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI of the status this status replies to.",
    )
    replyURI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI of the list of replies to this status.",
    )
    reply_actor_id: Optional[ULID] = Field(None, description="ID of the actor who posted the replied-to status.")
    reply_actor_URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI of the actor who posted the replied-to status.",
    )
    share_id: Optional[ULID] = Field(None, description="ID of the status this status is a share of.")
    sharesURI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub shares URI of this status.",
    )
    share_actor_id: Optional[ULID] = Field(None, description="ID of the actor who posted this shareed status.")
    share_actor_URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI of the actor who posted this shareed status.",
    )
    thread_id: Optional[ULID] = Field(None, description="ID of the thread to which this status belongs.")
    likesURI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub shares URI of this status.",
    )
    pinned: Optional[datetime] = Field(None, description="Status was pinned by owning account at this time.")
    model_config = ConfigDict(from_attributes=True)


class StatusCreate(StatusBase):
    id: Optional[ULID] = Field(None, description="Automatically generated unique identity.")
    actor_id: ULID = Field(..., description="Actor who posted this status.")
    preferredUsername: str = Field(
        ...,
        description="Username of the account, should just be a string of [a-zA-Z0-9_].",
    )
    type: ActivityType | ObjectLinkType = Field(..., description="Defined ActivityPub Activity or ObjectLink types.")
    content_header: Optional[dict[str, str]] = Field(
        None, description="Original text of the content warning without formatting."
    )
    content: Optional[dict[str, str]] = Field(None, description="Original text of the status without formatting.")

    @model_validator(mode="after")
    def process_tags_and_mentions(self) -> Self:
        self.tag = []
        tagset = set()
        mentionset = set()
        if isinstance(self.content_raw, dict) and self.content_raw:
            for k, v in self.content_raw.items():
                mentionset.update(regex.matches_from_text(regex.mentionFinder, v))
                for tag in set(regex.hashtags_from_text(v)):
                    if tag not in tagset:
                        self.tag.append({"language": k, "name": tag})
                    tagset.add(tag)
        if isinstance(self.content_header_raw, dict) and self.content_header_raw:
            for k, v in self.content_header_raw.items():
                mentionset.update(regex.matches_from_text(regex.mentionFinder, v))
                for tag in set(regex.hashtags_from_text(v)):
                    if tag not in tagset:
                        self.tag.append({"language": k, "name": tag})
                    tagset.add(tag)
        self.mentions = list(mentionset)
        return self

    # @model_validator(mode="after")
    # def process_content(self) -> Self:
    #     if isinstance(self.content_raw, dict) and self.content_raw:
    #         self.content = {}
    #         for k, v in self.content_raw.items():
    #             v = dataparser.clean_html(v)
    #             self.content[k] = dataparser.text_to_html(v)
    #     if isinstance(self.content_header_raw, dict) and self.content_header_raw:
    #         self.content_header = {}
    #         for k, v in self.content_header_raw.items():
    #             v = dataparser.clean_html(v)
    #             self.content_header[k] = dataparser.text_to_html(v)
    #     return self

    @model_validator(mode="after")
    def generate_endpoints(self) -> Self:
        self.id = ULID()
        # Settings
        domain = settings.SERVER_HOST
        if not isinstance(settings.SERVER_HOST, str):
            domain = str(settings.SERVER_HOST)
        if domain[-1] == "/":
            domain = domain[:-1]
        # URIs
        self.actorURI = f"{domain}/{self.type.as_uri}/{self.preferredUsername}"
        self.URI = f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.statuses}/{self.id}"
        self.URL = f"{domain}/@{self.preferredUsername}/{self.id}"
        self.replyURI = (
            f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.statuses}/{self.id}/{regex.replies}"
        )
        self.sharesURI = (
            f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.statuses}/{self.id}/{regex.shares}"
        )
        self.likesURI = f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.statuses}/{self.id}/{regex.likes}"
        return self


class ActivityStatusCreate(StatusBase):
    id: Optional[ULID] = Field(None, description="Automatically generated unique identity.")
    created: Optional[datetime] = Field(None, description="Date status was created / published.")
    fetched: datetime = Field(
        default_factory=datetime.now, description="Automatically generated date actor was last fetched (remote)."
    )
    content_header: Optional[dict[str, str]] = Field(
        None, description="Original text of the content warning without formatting."
    )
    content: Optional[dict[str, str]] = Field(None, description="Original text of the status without formatting.")
    attachments: Optional[list[dict[str, Any]]] = Field([], description="List of media attachments to this Status.")
    sharesCount: Optional[int] = Field(None, description="Count of status shares.")
    likesCount: Optional[int] = Field(None, description="Count of status likes.")
    repliesCount: Optional[int] = Field(None, description="Count of status replies, not usually available.")
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def restructure_remote_source(cls, data: Any) -> Any:
        # restructure for import
        if "published" in data:
            data["created"] = data["published"]
        data["URI"] = deepcopy(data.get("id"))
        if isinstance(data.get("url"), list) and len(data["url"]) >= 1:
            data["URL"] = data.get("url")[0]
        else:
            data["URL"] = data.get("url")
        data["actorURI"] = data.get("attributedTo")
        data["language"] = dataparser.get_default_language(data, settings.DEFAULT_LANGUAGE)
        if data["language"]:
            language = str(data["language"])
        if data.get("summary") and isinstance(data["summary"], str):
            data["content_header"] = {language: dataparser.clean_html(data["summary"])}
        if isinstance(data.get("contentMap"), dict) and data.get("contentMap"):
            data["content"] = {}
            for k, v in data["contentMap"].items():
                data["content"][str(k)] = dataparser.clean_html(v)
        elif data.get("content") and isinstance(data["content"], str):
            data["content"] = {language: dataparser.clean_html(data["content"])}
        # Get the socials
        if isinstance(data.get("likes"), dict) and data.get("likes"):
            data["likesURI"] = data["likes"].get("id")
            data["likesCount"] = data["likes"].get("totalItems")
        if data.get("inReplyTo"):
            data["inReplyToURI"] = data["inReplyTo"]
        if isinstance(data.get("replies"), dict) and data.get("replies"):
            data["replyURI"] = data["replies"].get("id")
            if data["replies"].get("totalItems"):
                data["repliesCount"] = data["replies"].get("totalItems")
            elif len(data["replies"].get("items", [])):
                data["repliesCount"] = len(data["replies"].get("items", []))
            elif data.get("repliesCount"):
                data["repliesCount"] = data.get("repliesCount")
        if isinstance(data.get("shares"), dict) and data.get("shares"):
            data["sharesURI"] = data["shares"].get("id")
            data["sharesCount"] = data["shares"].get("totalItems")
        if isinstance(data.get("tag"), list):
            tagged = []
            # data["mentions"] = []
            for tag in data["tag"]:
                if isinstance(tag, dict) and tag.get("name"):
                    if tag.get("type") == "Hashtag":
                        name = tag["name"].lower()
                        if "#" in name:
                            name = regex.hashtag_root(tag["name"])
                        tagged.append(dict(language=language, name=name))
                    # if tag.get("type") == "Mention" and tag.get("href"):
                    #     data["mentions"].append(tag["href"])
            data["tag"] = tagged
        if isinstance(data.get("attachment"), list):
            attachment = []
            for attch in data["attachment"]:
                if isinstance(attch, dict):
                    if attch.get("value"):
                        attch["value"] = dataparser.clean_html(attch["value"])
                    if attch.get("url") and not regex.url_validates(attch["url"]):
                        attch["url"] = None
                attachment.append(attch)
            data["attachments"] = attachment
        # Reset the id. If being updated, this will be set externally.
        data["id"] = None
        return data


class StatusUpdate(StatusCreate, metaclass=ModelMeta):
    __exclude_parent_fields__ = [
        "URI",
        "URL",
        "reply_id",
        "inReplyToURI",
        "replyURI",
        "reply_actor_id",
        "reply_actor_URI",
        "share_id",
        "sharesURI",
        "share_actor_id",
        "share_actor_URI",
        "thread_id",
        "threadURI",
        "likesURI",
    ]
    id: ULID = Field(..., description="Automatically generated unique identity.")
    created: Optional[datetime] = Field(None, description="Automatically generated date actor was created.")
    modified: Optional[datetime] = Field(None, description="Automatically generated date actor was last modified.")
    fetched: Optional[datetime] = Field(None, description="When was remote item was last fetched.")


class _Status(BaseSchema):
    id: Optional[ULID] = Field(None, description="Automatically generated unique identity.")
    created: Optional[datetime] = Field(None, description="Automatically generated date created.")
    modified: Optional[datetime] = Field(None, description="Automatically generated date last modified.")
    fetched: Optional[datetime] = Field(None, description="When was remote item was last fetched.")
    URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI for this account.",
    )
    URL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile.",
    )
    local: bool = Field(False, description="Apply mute to notifications as well as statuses.")
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the default language. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    content_header: Optional[str] = Field(None, description="Formatted text of the content header.")
    content: Optional[str] = Field(None, description="Formatted text of the status.")
    tag: Optional[list[dict[str, str]]] = Field([], description="A list of topics of the pathway.")
    attachments: Optional[list[dict[str, Any]]] = Field([], description="List of media attachments to this Status.")
    mentions: Optional[list[str]] = Field([], description="List of Actors mentioned in the Status.")
    sensitive: Optional[bool] = Field(False, description="Whether the status is marked as sensitive.")
    visibility: VisibilityType = Field(
        default=VisibilityType.Unlocked, description="Default post privacy for this status."
    )
    edited: Optional[bool] = Field(False, description="Whether the status has been edited.")
    actor: Optional[Actor] = Field(None, description="Actor responsible for this status.")
    reply_id: Optional[ULID] = Field(None, description="ID of the status this status replies to.")
    inReplyToURI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI of the status this status replies to.",
    )
    replyURI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI of the list of replies to this status.",
    )
    reply_actor_id: Optional[ULID] = Field(None, description="ID of the actor who posted the replied-to status.")
    reply_actor_URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI of the actor who posted the replied-to status.",
    )
    share_id: Optional[ULID] = Field(None, description="ID of the status this status is a share of.")
    sharesURI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub shares URI of this status.",
    )
    share_actor_id: Optional[ULID] = Field(None, description="ID of the actor who posted this shareed status.")
    share_actor_URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI of the actor who posted this shareed status.",
    )
    thread_id: Optional[ULID] = Field(None, description="ID of the thread to which this status belongs.")
    likesURI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub shares URI of this status.",
    )
    sharesCount: Optional[int] = Field(None, description="Count of status shares.")
    likesCount: Optional[int] = Field(None, description="Count of status likes.")
    repliesCount: Optional[int] = Field(None, description="Count of status replies, not usually available.")
    has_shared: Optional[bool] = Field(False, description="If the requesting actor has shared this status.")
    has_liked: Optional[bool] = Field(False, description="If the requesting actor has liked this status.")
    has_bookmarked: Optional[bool] = Field(False, description="If the requesting actor has bookmarked this status.")
    pinned: Optional[datetime] = Field(None, description="Status was pinned by owning account at this time.")
    model_config = ConfigDict(from_attributes=True)


class Status(_Status):
    content_header_raw: Optional[dict[str, str]] = Field(
        None, description="Original text of the content warning without formatting."
    )
    content_raw: Optional[dict[str, str]] = Field(None, description="Original text of the status without formatting.")
    share: Optional[_Status] = Field({}, description="If this is a status which shares an existing status.")
