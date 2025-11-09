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
    field_validator,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)
from datetime import datetime
from sqlalchemy.orm import Query
import bovine

from app.schemas.base_schema import BaseSchema, ModelMeta, LocaleType
from .media import MediaAttachment
from app.schema_types import ActorType
from app.utilities.regexes import regex
from app.utilities.parser import dataparser
from app.core.config import settings

"""
Design assumptions:

CREATE/UPDATE ->
    - Receive `summary_raw` as a `dict` of `[str, str]` reflecting `language`: `text`.
    - Root `language` will be populated with the default.
    - Need to process text to extract `tag` models.
    - Convert `summary_raw` to html for `summary`.

REMOTE/IN ->
    - Receive `summary` as a `dict` of `[str, str]` reflecting `language`: `text`.
    - Tags already extracted.
"""


class ActorBase(BaseSchema):
    # REQUIRED ACTIVITYSTREAMS PROPERTIES
    type: ActorType = Field(
        default=ActorType.Person, description="Defined ActivityPub Actor types, default is 'Person'."
    )
    preferredUsername: str = Field(
        ...,
        description="Username of the account, should just be a string of [a-zA-Z0-9_]. Can be added to domain to create the full username in the form ``[username]@[domain]`` eg., ``user_96@example.org``. Username and domain should be unique *with* each other.",
    )
    name: Optional[str] = Field(
        None,
        description="Display Name for this account. Can be empty, then just the preferredUsername will be used for display purposes.",
    )
    domain: Optional[str] = Field(
        None,
        description="Domain of the account, will be null if this is a local account, otherwise something like ``example.org``. Should be unique with username.",
    )
    # RECOMMENDED ACTIVITYSTREAMS PROPERTIES
    inbox: Optional[HttpUrl] = Field(
        None,
        description="Address of this account's ActivityPub inbox, for sending activity to.",
    )
    outbox: Optional[HttpUrl] = Field(
        None,
        description="Address of this account's activitypub outbox.",
    )
    sharedInbox: Optional[HttpUrl] = Field(
        None,
        description="Address of this account's ActivityPub sharedInbox.",
    )
    following: Optional[HttpUrl] = Field(
        None,
        description="URI for getting the following list of this account.",
    )
    followers: Optional[HttpUrl] = Field(
        None,
        description="URI for getting the followers list of this account.",
    )
    liked: Optional[HttpUrl] = Field(
        None,
        description="URI for getting the favourites / likes list of this account.",
    )
    featured: Optional[HttpUrl] = Field(
        None,
        description="URL for getting the featured collection list of this account.",
    )
    # OPTIONAL ACTIVITYSTREAMS PROPERTIES
    URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI for this account.",
    )
    URL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile.",
    )
    iconURL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile icon image.",
    )
    standoutURL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile header / standout image.",
    )
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the language used by the actor. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    summary_raw: Optional[dict[str, str]] = Field(None, description="Public summary for this Actor.")
    summary: Optional[dict[str, str]] = Field(None, description="Public summary for this Actor, HTML version.")
    tag: Optional[list[dict[str, str]]] = Field([], description="A list of topics of the pathway.")
    attachment: Optional[list[dict[str, str]]] = Field(
        [], description="List of key-value pairs added as attachment to profile."
    )
    alsoKnownAs: Optional[list[str]] = Field(
        None, description="ActivityPub URI/IDs by which this account is also known."
    )
    # AUTHENTICATION AND PERSISTENCE
    publicKey: str = Field(
        ...,
        description="Privatekey for signing activitypub requests, will only be defined for local accounts.",
    )
    publicKeyURI: HttpUrl = Field(
        ...,
        description="Web-reachable location of this account's public key.",
    )
    # SETTINGS
    locked: bool = Field(False, description="Requires manual approval of followers.")
    discoverable: bool = Field(False, description="Should this account be shown in the instance's profile directory?")
    memorial: bool = Field(False, description="Actor has made their crossing.")
    default_persona: Optional[bool] = Field(None, description="Default Persona for a Creator. Can only be one.")
    model_config = ConfigDict(from_attributes=True)

    @field_validator("preferredUsername")
    @classmethod
    def validate_preferredUsername(cls, v: str) -> str:
        if not regex.matches(regex.actornameRelaxed, v):
            raise ValueError("Must be a valid preferredUsername")
        return v

    @model_validator(mode="after")
    def process_tags(self) -> Self:
        if isinstance(self.summary_raw, dict) and self.summary_raw:
            self.tag = []
            tagset = set()
            for k, v in self.summary_raw.items():
                for tag in set(regex.hashtags_from_text(v)):
                    if tag not in tagset:
                        self.tag.append({"language": k, "name": tag})
                    tagset.add(tag)
        return self


class ActorCreate(ActorBase):
    """Only for local Actor creation, otherwise use ActivityActorCreate"""

    creator_id: ULID = Field(..., description="Creator account which controls this Actor.")
    maker_id: Optional[ULID] = Field(None, description="Actor maker account which controls this Actor work.")
    # AUTHENTICATION AND PERSISTENCE
    privateKey: Optional[str] = Field(
        None,
        description="Publickey for authorizing signed activitypub requests, will be defined for both local and remote accounts.",
    )
    publicKey: Optional[str] = Field(
        None,
        description="Privatekey for signing activitypub requests, will only be defined for local accounts.",
    )
    publicKeyURI: Optional[HttpUrl] = Field(
        None,
        description="Web-reachable location of this account's public key.",
    )

    @model_validator(mode="after")
    def process_summaries(self) -> Self:
        if isinstance(self.summary_raw, dict) and self.summary_raw:
            self.summary = {}
            for k, v in self.summary_raw.items():
                v = dataparser.clean_html(v)
                self.summary[k] = dataparser.text_to_html(v)
        return self

    @model_validator(mode="after")
    def generate_keys(self) -> Self:
        if not self.publicKey and not self.privateKey:
            self.publicKey, self.privateKey = bovine.crypto.generate_rsa_public_private_key()
        return self

    @model_validator(mode="after")
    def generate_endpoints(self) -> Self:
        if self.preferredUsername:
            # Settings
            domain = settings.SERVER_HOST
            if not isinstance(settings.SERVER_HOST, str):
                domain = str(settings.SERVER_HOST)
            if domain[-1] == "/":
                domain = domain[:-1]
            # URIs
            self.domain = regex.url_root(settings.SERVER_HOST)
            self.inbox = f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.inbox}"
            self.outbox = f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.outbox}"
            self.sharedInbox = f"{domain}/{regex.inbox}"
            self.following = f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.following}"
            self.followers = f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.followers}"
            self.liked = f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.liked}"
            self.featured = f"{domain}/{self.type.as_uri}/{self.preferredUsername}/{regex.featured}"
            self.publicKeyURI = f"{domain}/{self.type.as_uri}/{self.preferredUsername}#{regex.publicKey}"
            self.URI = f"{domain}/{self.type.as_uri}/{self.preferredUsername}"
            self.URL = f"{domain}/@{self.preferredUsername}"
        return self


class ActivityActorCreate(ActorBase):
    """
    Transforming remote ActivityPub Actors into local fields.
    """

    id: Optional[ULID] = Field(None, description="Automatically generated unique identity.")
    created: Optional[datetime] = Field(None, description="Date actor was created / published.")
    fetched: datetime = Field(
        default_factory=datetime.now, description="Automatically generated date actor was last fetched (remote)."
    )
    # mentions: Optional[list[str]] = Field(
    #     [], description="List of Actors mentioned in the Status. Found in 'tags' as type 'Mention'."
    # )

    @model_validator(mode="before")
    def restructure_remote_source(cls, data: Any) -> Any:
        # from `bovine.parse.Actor.validate`
        if "outbox" not in data:
            raise ValueError("An actor must have an outbox")
        if not isinstance(data["outbox"], str):
            raise ValueError("The outbox must be a single string")
        if "inbox" not in data:
            raise ValueError("An actor must have an inbox")
        if not isinstance(data["inbox"], str):
            raise ValueError("The inbox must be a single string")
        if isinstance(data["featured"], dict):
            # Can happen for bridged data
            if data["featured"].get("id"):
                data["featured"] = data["featured"]["id"]
            else:
                raise ValueError("Featured link must be a single string")
        # restructure for import
        if "published" in data:
            data["created"] = data["published"]
        data["URI"] = data.get("id")
        data["domain"] = regex.url_root(data.get("id"))
        if data.get("url") and isinstance(data["url"], list):
            # For bridged sources
            if len(data["url"]):
                data["url"] = data["url"][0]
            else:
                data["url"] = None
        data["URL"] = data.get("url")
        data["language"] = dataparser.get_default_language(data, settings.DEFAULT_LANGUAGE)
        if data["language"]:
            language = str(data["language"])
        if isinstance(data.get("summary"), str):
            data["summary"] = {language: dataparser.clean_html(data["summary"])}
        if isinstance(data.get("publicKey"), dict):
            if data["publicKey"].get("owner") != data.get("id"):
                raise ValueError("Public key has incorrect owner.")
            data["publicKeyURI"] = data["publicKey"].get("id")
            data["publicKey"] = data["publicKey"].get("publicKeyPem")
        if isinstance(data.get("icon"), dict):
            data["iconURL"] = data["icon"].get("url")
        if isinstance(data.get("image"), dict):
            data["standoutURL"] = data["image"].get("url")
        if "manuallyApprovesFollowers" in data:
            data["locked"] = data["manuallyApprovesFollowers"]
        if isinstance(data.get("endpoints"), dict):
            data["sharedInbox"] = data["endpoints"].get("sharedInbox")
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
                # First rectify it converting everything to strings
                if isinstance(attch, dict):
                    for k, v in attch.items():
                        attch[k] = str(v)
                        if k == "value":
                            attch[k] = dataparser.clean_html(v)
                else:
                    attch = dataparser.clean_html(str(attch))
                attachment.append(attch)
            data["attachment"] = attachment
        if isinstance(data.get("alsoKnownAs"), list):
            data["alsoKnownAs"] = [u for u in data["alsoKnownAs"] if regex.url_validates(u)]
        # Reset the id. If being updated, this will be set externally.
        data["id"] = None
        return data


class ActorUpdate(ActorBase, metaclass=ModelMeta):
    __exclude_parent_fields__ = [
        "type",
        "preferredUsername",
        "summary",
        "tag",
        "domain",
        "inbox",
        "outbox",
        "sharedInbox",
        "following",
        "followers",
        "liked",
        "featured",
        "URI",
        "URL",
        "alsoKnownAs",
        "publicKey",
        "publicKeyURI",
    ]
    id: ULID = Field(..., description="Automatically generated unique identity.")
    created: Optional[datetime] = Field(None, description="Automatically generated date actor was created.")
    modified: Optional[datetime] = Field(
        default_factory=datetime.now, description="Automatically generated date actor was last modified."
    )
    summary_raw: Optional[str] = Field(None, description="Public summary for this Actor.")


class ActorUpdateTest(BaseSchema):
    id: Optional[str] = Field(None, description="Public summary for this Actor, HTML version.")
    summary_raw: Optional[str] = Field(None, description="Public summary for this Actor, HTML version.")


class ActorUpdateIn(ActorUpdate, metaclass=ModelMeta):
    __exclude_parent_fields__ = [
        "created",
        "iconURL",
        "standoutURL",
    ]
    summary: Optional[str] = Field(None, description="Public summary for this Actor, HTML version.")
    tag: Optional[list[dict[str, str]]] = Field([], description="A list of topics of the pathway.")

    @model_validator(mode="after")
    def process_summary(self) -> Self:
        if self.summary_raw:
            summary = dataparser.clean_html(self.summary_raw)
            self.summary = dataparser.text_to_html(summary)
        return self

    @model_validator(mode="after")
    def process_tags(self) -> Self:
        if self.summary_raw and self.language:
            self.tag = []
            tagset = set()
            for tag in set(regex.hashtags_from_text(self.summary_raw)):
                if tag not in tagset:
                    self.tag.append({"language": self.language, "name": tag})
                tagset.add(tag)
        return self


class ActorMediaUpdate(ActorUpdate):
    icon: Optional[MediaAttachment] = Field(None, description="Media metadata for the actor icon.")
    standout: Optional[MediaAttachment] = Field(None, description="Media metadata for the actor standout.")


class ModeratorActorUpdate(ActorUpdate):
    creator_id: ULID = Field(..., description="Creator account which controls this Actor.")
    # ADMINISTRATION AND MODERATION
    sensitizedAt: Optional[datetime] = Field(
        None, description="When was this account set to have all its media shown as sensitive?"
    )
    silencedAt: Optional[datetime] = Field(
        None, description="When was this account silenced (eg., statuses only visible to followers, not public)?"
    )
    suspendedAt: Optional[datetime] = Field(
        None,
        description="When was this account suspended (eg., don't allow it to log in/post, don't accept media/posts from this account)?",
    )


class ActorWorkSummary(BaseSchema):
    id: Optional[ULID] = Field(None, description="Automatically generated unique identity.")
    preferredUsername: str = Field(
        ...,
        description="Username of the account, should just be a string of [a-zA-Z0-9_]. Can be added to domain to create the full username in the form ``[username]@[domain]`` eg., ``user_96@example.org``. Username and domain should be unique *with* each other.",
    )
    name: Optional[str] = Field(
        None,
        description="Display Name for this account. Can be empty, then just the preferredUsername will be used for display purposes.",
    )
    domain: Optional[str] = Field(
        None,
        description="Domain of the account, will be null if this is a local account, otherwise something like ``example.org``. Should be unique with username.",
    )
    URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI for this account.",
    )
    URL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile.",
    )
    iconURL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile icon image.",
    )
    model_config = ConfigDict(from_attributes=True)


class Actor(BaseSchema):
    id: Optional[ULID] = Field(None, description="Automatically generated unique identity.")
    created: Optional[datetime] = Field(None, description="Date actor was created / published.")
    type: ActorType = Field(
        default=ActorType.Person, description="Defined ActivityPub Actor types, default is 'Person'."
    )
    preferredUsername: str = Field(
        ...,
        description="Username of the account, should just be a string of [a-zA-Z0-9_]. Can be added to domain to create the full username in the form ``[username]@[domain]`` eg., ``user_96@example.org``. Username and domain should be unique *with* each other.",
    )
    name: Optional[str] = Field(
        None,
        description="Display Name for this account. Can be empty, then just the preferredUsername will be used for display purposes.",
    )
    domain: Optional[str] = Field(
        None,
        description="Domain of the account, will be null if this is a local account, otherwise something like ``example.org``. Should be unique with username.",
    )
    URI: Optional[HttpUrl] = Field(
        None,
        description="ActivityPub URI for this account.",
    )
    URL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile.",
    )
    iconURL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile icon image.",
    )
    standoutURL: Optional[HttpUrl] = Field(
        None,
        description="Web URL for this account's profile header / standout image.",
    )
    # outbox: Optional[HttpUrl] = Field(
    #     None,
    #     description="Address of this account's activitypub outbox.",
    # )
    # featured: Optional[HttpUrl] = Field(
    #     None,
    #     description="URL for getting the featured collection list of this account.",
    # )
    followersCount: Optional[int] = Field(None, description="Count of followers.")
    followingCount: Optional[int] = Field(None, description="Count of following.")
    statusCount: Optional[int] = Field(None, description="Count of status updates.")
    lastStatus: Optional[datetime] = Field(None, description="Last status creation date.")
    locked: bool = Field(False, description="Requires manual approval of followers.")
    discoverable: bool = Field(False, description="Should this account be shown in the instance's profile directory?")
    memorial: bool = Field(False, description="Actor has made their crossing.")
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the language used by the actor. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    summary: Optional[str] = Field(None, description="Public summary for this Actor, HTML version.")
    attachment: Optional[list[dict[str, str]]] = Field(
        [], description="List of key-value pairs added as attachment to profile."
    )
    default_persona: Optional[bool] = Field(None, description="Default Persona for a Creator. Can only be one.")
    is_following: Optional[bool] = Field(None, description="If requested by a logged-in persona, if following.")
    is_followed: Optional[bool] = Field(None, description="If requested by a logged-in persona, if followed.")
    can_edit: Optional[bool] = Field(None, description="If requested by a logged-in persona, if they can edit.")
    works: Optional[list[ActorWorkSummary]] = Field([], description="List of works controlled by this Actor.")
    maker_id: Optional[ULID] = Field(None, description="Actor maker account which controls this Actor work.")
    model_config = ConfigDict(from_attributes=True)

    @field_validator("works", mode="before")
    @classmethod
    def evaluate_lazy_works(cls, v):
        # https://github.com/samuelcolvin/pydantic/issues/1334#issuecomment-745434257
        # Call PydanticModel.model_validate(dbQuery)
        if isinstance(v, Query):
            return [ActorWorkSummary.model_validate(work) for work in v.all()]
