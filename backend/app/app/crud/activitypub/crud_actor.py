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

from typing import Optional, TypeVar
from pydantic import HttpUrl
from sqlalchemy.orm import Session
from sqlalchemy import desc
from babel import Locale
from bovine import activitystreams, BovineActor
from bovine.types import Visibility
from bovine.clients import lookup_uri_with_webfinger
from bovine.utils import webfinger_response_json, parse_fediverse_handle
from aiohttp.client_exceptions import ClientConnectorDNSError

from app.core.config import settings
from ..base import CRUDBase
from app.models.creator import Creator
from app.models.activitypub.actor import Actor, ActorSummary, ActorSummaryRaw
from app.models.activitypub.media import MediaAttachment
from app.schemas.activitypub.actor import (
    ActorCreate,
    ActivityActorCreate,
    ActorUpdate,
    Actor as ActorProfile,
    ActorWorkSummary,
)
from app.schema_types import ActorType
from app.utilities.regexes import regex

# from app.utilities.parser import dataparser
from ..crud_source import source as crud_source


class CRUDActor(CRUDBase[Actor, ActorCreate, ActorUpdate]):
    """
    All CRUD for Actors.

    https://www.w3.org/TR/activitystreams-vocabulary/#dfn-follow
    """

    ###################################################################################################
    # STANDARD CRUD
    ###################################################################################################

    def get_multi_creators(self, db: Session, *, page: int = 0, page_break: bool = False) -> list[dict[str, any]]:
        query_filter = self.model.type == ActorType.Person
        query_filter &= self.model.discoverable.is_(True)
        db_objs = db.query(self.model).filter(query_filter)
        if not page_break:
            if page > 0:
                db_objs = db_objs.offset(page * settings.MULTI_MAX)
            db_objs = db_objs.limit(settings.MULTI_MAX)
        db_objs = db_objs.all()
        return [self.get_wellknown_actor(db=db, db_obj=db_obj, visibility=Visibility.OWNER) for db_obj in db_objs]

    def get_actors_by_creator(
        self, *, db_creator: Creator, page: int = 0, page_break: bool = False, actor_type: ActorType = None
    ) -> list[Actor]:
        query_filter = None
        db_objs = db_creator.actors
        if actor_type:
            query_filter = self.model.type == actor_type
        if query_filter:
            db_objs = db_objs.filter(query_filter)
        if not page_break:
            if page > 0:
                db_objs = db_objs.offset(page * settings.MULTI_MAX)
            db_objs = db_objs.limit(settings.MULTI_MAX)
        return db_objs.all()

    async def _get_profile_social_attributes(
        self,
        *,
        actor: BovineActor,
        db_obj: Actor,
        schema: TypeVar = ActorProfile,
        language: str | Locale = settings.DEFAULT_LANGUAGE,
    ):
        obj_in = self.get_schema_by_language(db_obj=db_obj, schema=schema, language=language)
        attributes = [("followersCount", "followers"), ("followingCount", "following"), ("statusCount", "outbox")]
        for field, attr in attributes:
            if hasattr(db_obj, attr) and getattr(db_obj, attr):
                try:
                    remoteURI = str(getattr(db_obj, attr))
                    response = await actor.get(remoteURI)
                    if response and response.get("totalItems"):
                        value = int(response.get("totalItems"))
                        setattr(obj_in, field, value)
                    if attr == "outbox" and response and response.get("first") and isinstance(response["first"], str):
                        response = await actor.get(response["first"])
                        if response and response.get("orderedItems"):
                            obj_in.lastStatus = response["orderedItems"][0].get("published")
                except (ClientConnectorDNSError, ValueError):
                    pass
        return obj_in

    async def get_profile_by_language(
        self,
        db: Session,
        *,
        db_obj: Actor,
        db_actor: Actor | None = None,
        actor: BovineActor | None = None,
        schema: TypeVar = ActorProfile,
        language: str | Locale = settings.DEFAULT_LANGUAGE,
        as_local: bool = False,
    ):
        # `db_actor` is the requesting agent ... if not present then there can be no `is_following` or `is_followed`
        if not db_actor:
            db_obj.is_following = None
            db_obj.is_followed = None
        else:
            db_obj.is_following = db_obj.is_following(db_actor.id)
            db_obj.is_followed = db_obj.is_followed(db_actor.id)
        if as_local or db_obj.is_local:
            obj_in = self.get_schema_by_language(db_obj=db_obj, schema=schema, language=language)
            obj_in.followersCount = db_obj.follower_actors.count()
            obj_in.followingCount = db_obj.following_actors.count()
            obj_in.statusCount = db_obj.status.count()
            obj_in.works = [ActorWorkSummary.model_validate(w) for w in db_obj.works.all()]
            obj_status = db_obj.status.order_by(desc("created")).first()
            if obj_status:
                obj_in.lastStatus = obj_status.created
        else:
            if not actor:
                if not db_actor:
                    actor = self.get_site_actor(db=db)
                else:
                    actor = self.get_requests_actor(db_obj=db_actor)
            keep_alive = actor.session and not actor.session.closed
            if not keep_alive:
                await actor.init()
            obj_in = await self._get_profile_social_attributes(
                actor=actor, db_obj=db_obj, schema=schema, language=language
            )
            if not keep_alive:
                await actor.session.close()
        return obj_in

    ###################################################################################################
    # GET WORKING ACTORS
    ###################################################################################################

    def get_by_name(self, db: Session, *, name: str, domain: str = settings.NGROK_DOMAIN) -> Optional[Actor]:
        query_filter = self.model.preferredUsername == name
        query_filter &= self.model.domain == domain
        return db.query(self.model).filter(query_filter).first()

    def check_persona_name(self, db: Session, *, name: str) -> bool:
        # 1. Check if persona is valid
        if len(name) < settings.MINIMUM_NAME_LENGTH or len(name) > settings.MAXIMUM_NAME_LENGTH:
            return False
        if name in settings.RESERVED_NAMES:
            return False
        if not regex.matches(regex.actornameStrict, name):
            return False
        # 2. Check if persona already exists
        query_filter = self.model.preferredUsername == name
        query_filter &= self.model.domain == settings.NGROK_DOMAIN
        db_obj = db.query(self.model).filter(query_filter).first()
        if db_obj:
            return False
        return True

    def get_by_resource(self, db: Session, *, resource: str):
        # Check if the resource encapsulates a webfinger query
        preferredUsername, domain = parse_fediverse_handle(resource)
        preferredUsername = preferredUsername.replace("acc:", "")
        return self.get_by_name(db=db, name=preferredUsername, domain=domain)

    def get_site_actor(self, *, db: Session) -> Optional[Actor]:
        preferredUsername = regex.url_root(settings.SERVER_HOST).replace("-", "_").replace(".", "_")
        db_obj = db.query(self.model).filter(self.model.preferredUsername == preferredUsername).first()
        return BovineActor(
            actor_id=db_obj.URL,
            public_key_url=db_obj.publicKeyURI,
            secret=db_obj.privateKey,
        )

    def get_requests_actor(self, *, db_obj: Actor):
        return BovineActor(
            actor_id=db_obj.URL,
            public_key_url=db_obj.publicKeyURI,
            secret=db_obj.privateKey,
        )

    ###################################################################################################
    # PERFORM ACTIVITY FETCH OF REMOTE DATA
    ###################################################################################################

    async def fetch_ordered_collection(self, *, db_actor: Actor, remote_id: str, max_items: int | None = 19) -> Actor:
        actor = self.get_requests_actor(db_obj=db_actor)
        await actor.init()
        response = await actor.get_ordered_collection(remote_id, max_items)
        await actor.session.close()
        return response

    ###################################################################################################
    # SETTINGS
    ###################################################################################################

    def set_default_persona(self, db: Session, *, db_creator: Creator, db_obj: Actor) -> Actor:
        # Check that this is an Actor of type Person, and that it's local
        if (
            db_obj.creator_id != db_creator.id
            or db_obj.type != ActorType.Person
            or (db_obj.domain and not regex.url_is_local(db_obj.domain))
        ):
            raise ValueError(f"'{db_obj.preferredUsername}' is not a valid default for this creator.")
        # Then check if there is a default and unset it
        query_filter = Actor.type == ActorType.Person
        query_filter &= Actor.default_persona.is_(True)
        for db_persona in db_creator.actors.filter(query_filter).all():
            db_persona.default_persona = False
            db.add(db_persona)
            db.commit()
            db.refresh(db_persona)
        # Finally, set the new persona as the default
        db_obj.default_persona = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    ###################################################################################################
    # FETCH REMOTE ACTOR
    ###################################################################################################

    def parse_mention(self, *, remote_id: str) -> tuple[str, str, str]:
        """
        Splits fediverse handle in name and domain. Supported forms are:

        - user@domain -> (user, domain)
        - @user@domain -> (user, domain)
        - acct:user@domain -> (user, domain)
        """
        domain = None
        if regex.url_validates(remote_id):
            domain = regex.url_root(remote_id)
            name = remote_id.split("/")[-1]
        elif regex.matches(regex.mentionFinder, remote_id) or regex.matches(regex.mentionFinder, "@" + remote_id):
            remote_id = remote_id.strip()
            if remote_id.startswith("@"):
                remote_id = remote_id[1:]
            if remote_id.endswith("."):  # match is greedy
                remote_id = remote_id[:-1]
            name, domain = remote_id.split("@")
            remote_id = "acct:" + remote_id
        return name, domain, remote_id

    def parse_handle(self, *, resource_id: str) -> tuple[str, str, str]:
        """
        Splits fediverse handle in name and domain. Supported forms are:

        - user@domain -> (user, domain)
        - @user@domain -> (user, domain)
        - acct:user@domain -> (user, domain)
        """
        preferredUsername, domain = parse_fediverse_handle(resource_id)
        remote_id = f"acct:{preferredUsername}@{domain}"
        return preferredUsername, domain, remote_id

    async def fetch_actor_with_uri(self, *, db: Session, actor: BovineActor, URI: str | HttpUrl) -> ActorProfile:
        """
        Convenience wrapper. Requires an initiated actor.
        """
        db_obj = self.get_by_uri(db=db, URI=URI)
        if not db_obj or (db_obj and not db_obj.is_local and not crud_source.should_fetch(db_obj.fetched)):
            obj_in = await actor.get(URI)
            obj_in.fetched = crud_source.get_now()
            if db_obj:
                obj_in.id = db_obj.id
                db_obj = self.update(db=db, db_obj=db_obj, obj_in=obj_in)
            else:
                db_obj = self.create(db=db, obj_in=obj_in)
        return ActorProfile.model_validate(db_obj)

    async def fetch_remote_actor(
        self, *, db: Session, db_obj: Actor = None, db_actor: Actor = None, remote_id: str = None, domain: str = None
    ) -> ActivityActorCreate:
        """
        Returns a remote actor via a request either from a logged-in creator, or the default site creator. Checks as to
        which is appropriate must happen elsewhere.

        `db_obj` is the existing remote actor, if it already exists in the database. If refetching, then this is to update.
        """
        if not db_actor:
            actor = self.get_site_actor(db=db)
        else:
            actor = self.get_requests_actor(db_obj=db_actor)
        await actor.init()
        try:
            remote, _ = await lookup_uri_with_webfinger(actor.session, remote_id, domain)
        except (ClientConnectorDNSError, ValueError):
            await actor.session.close()
            return None
        if not remote:
            # Bridged URIs don't have a webfinger response ... can try and see if the direct link works
            remote = remote_id
        remote_actor = await actor.get(remote)
        await actor.session.close()
        # print("-------------------------------------------------------------------")
        # print(remote)
        # print(remote_actor)
        # print("-------------------------------------------------------------------")
        if not remote_actor or remote_actor.get("type") == "Tombstone":
            # Will need to handle Tombstones at some point
            return None
        obj_in = ActivityActorCreate.model_validate(remote_actor)
        obj_in.fetched = crud_source.get_now()
        if db_obj:
            obj_in.id = db_obj.id
        return obj_in

    async def fetch_remote(self, *, db: Session, db_obj: Actor = None, db_actor: Actor = None, remote_id: str):
        """
        Fetches remote actor.

        NOTE: moderation validations must take place in advance (i.e. is this an acceptable actor)
        """
        if not db_obj:
            if regex.url_validates(remote_id):
                domain = regex.url_root(remote_id)
                db_obj = self.get_by_uri(db=db, URI=remote_id)
            else:
                name, domain, remote_id = self.parse_handle(resource_id=remote_id)
                db_obj = self.get_by_name(db=db, name=name, domain=domain)
        else:
            domain = db_obj.domain
        if db_obj and db_obj.is_local:
            return db_obj
        # if we have it, then it may need to be updated
        if db_obj and not db_obj.is_local and not crud_source.should_fetch(db_obj.fetched):
            return db_obj
        obj_in = await self.fetch_remote_actor(
            db=db, db_obj=db_obj, db_actor=db_actor, remote_id=remote_id, domain=domain
        )
        if not obj_in:
            return None
        if db_obj:
            return self.update(db=db, db_obj=db_obj, obj_in=obj_in)
        return self.create(db=db, obj_in=obj_in)

    async def fetch_mentions(self, *, db: Session, mentions: list[str]) -> list[Actor]:
        return [await self.fetch_remote(db=db, remote_id=m) for m in mentions]

    # async def hashdown(db: Session, match: str) -> str:
    #     obj_in = await crud.actor.fetch_remote(db=db, remote_id=match, fetch_only=True)
    #     if obj_in:
    #         return [match, f"[@{obj_in.preferredUsername}]({obj_in.URL})"]
    #     return [match, None]

    # async def mention_to_markdown(db: Session, text: str) -> str:
    #     mentions = [await hashdown(db, m.strip(".")) for m in re.findall(regex.mentionFinder, text)]
    #     for original, replacement in mentions:
    #         if replacement:
    #             text = text.replace(original, replacement)
    #     return text

    ###################################################################################################
    # PROCESS ACTOR MEDIA
    ###################################################################################################

    def update_media_url(self, *, db: Session, db_obj: Actor, URL: str | None = None, is_avatar: bool = True) -> Actor:
        """
        Updating includes deleting as 'None' is a valid value.
        """
        if is_avatar:
            db_obj.iconURL = str(URL)
        else:
            db_obj.standoutURL = str(URL)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    ###################################################################################################
    # BUILD ACTOR ACTIVITY STREAM
    ###################################################################################################

    def get_wellknown_webfinger(self, *, db_obj: Actor) -> dict[str, any]:
        return webfinger_response_json(f"acct:{db_obj.preferredUsername}@{db_obj.domain}", db_obj.URI)

    def get_wellknown_actor(
        self,
        db: Session,
        *,
        db_obj: Actor,
        language: Locale = settings.DEFAULT_LANGUAGE,
        visibility: Visibility = Visibility.PUBLIC,
    ) -> dict[str, any]:
        # additional parameters
        summary = self._get_summary(db_obj=db_obj, language=language)
        icon_id = None
        if db_obj.icon:
            icon_id = db_obj.icon.id
        icon = self._get_image(db=db, image_id=icon_id, image_url=db_obj.iconURL)
        # build
        response = activitystreams.Actor(
            id=db_obj.URI,
            url=db_obj.URL,
            type=db_obj.type.value,
            preferred_username=db_obj.preferredUsername,
            name=db_obj.name,
            inbox=db_obj.inbox,
            outbox=db_obj.outbox,
            followers=db_obj.followers,
            following=db_obj.following,
            public_key=db_obj.publicKey,
            public_key_name=regex.publicKey,
            icon=icon,
            summary=summary,
            properties=self._get_properties(
                db=db,
                db_obj=db_obj,
                language=language,
                visibility=visibility,
            ),
        )
        return response.build(visibility)

    def get_outbox(
        self,
        *,
        db_obj: Actor,
    ) -> dict[str, any]:
        return activitystreams.OrderedCollection(
            db_obj.outbox, first=f"{db_obj.outbox}?page=true", last=f"{db_obj.outbox}?min_id=0&page=true"
        ).build()

    def _get_summary(self, *, db_obj, language: Locale = settings.DEFAULT_LANGUAGE) -> str:
        if not db_obj.summary:
            return None
        summary = db_obj.summary.get(language)
        if not summary and db_obj.language:
            summary = db_obj.summary.get(db_obj.language)
        if summary:
            return summary.summary
        return None

    def _get_image(self, db: Session, *, image_id: str = None, image_url: str = None) -> dict[str, str]:
        if image_id:
            image = db(MediaAttachment).filter(id=image_id).first()
            if image:
                return {
                    "type": "Image",
                    "mediaType": image.content_type,
                    "url": image.URL,
                }
        if image_url:
            return {
                "type": "Image",
                "url": image_url,
            }
        return None

    def _get_properties(
        self, db: Session, *, db_obj, language: Locale = settings.DEFAULT_LANGUAGE, visibility: Visibility
    ) -> dict[str, any]:
        properties = {"@context": []}
        context = {
            "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
            "featured": {"@id": "as:featured", "@type": "@id"},
            "alsoKnownAs": {"@id": "as:alsoKnownAs", "@type": "@id"},
            "movedTo": {"@id": "as:movedTo", "@type": "@id"},
            "schema": "http://schema.org#",
            "PropertyValue": "schema:PropertyValue",
            "value": "schema:value",
            "discoverable": "as:discoverable",
            "suspended": "as:suspended",
            "memorial": "as:memorial",
            "Hashtag": "as:Hashtag",
        }
        # language
        language = db_obj.language or language
        if language:
            context["@language"] = str(language)
        properties["manuallyApprovesFollowers"] = db_obj.locked
        properties["discoverable"] = db_obj.discoverable
        properties["memorial"] = db_obj.memorial
        properties["suspended"] = bool(db_obj.suspended)
        if hasattr(db_obj, "featured") and visibility not in [Visibility.WEB]:
            properties["featured"] = db_obj.featured
        if hasattr(db_obj, "alsoKnownAs") and db_obj.alsoKnownAs:
            properties["alsoKnownAs"] = db_obj.alsoKnownAs
        if hasattr(db_obj, "tag") and db_obj.tag and visibility not in [Visibility.WEB]:
            tag = []
            for t in db_obj.tg:
                if t.language == language:
                    tag.append(
                        {
                            "type": "Hashtag",
                            "href": f"{settings.SERVER_HOST}/{regex.tags}/{t.name}",
                            "name": f"#{t.name}",
                        }
                    )
                if tag:
                    properties["tag"] = tag
        if hasattr(db_obj, "attachment") and db_obj.attachment:
            properties["attachment"] = db_obj.attachment
        if hasattr(db_obj, "standout_id") and (db_obj.standout_id or db_obj.standoutURL):
            standout = self._get_image(db=db, image_id=db_obj.standout_id, image_url=db_obj.standoutURL)
            if standout:
                properties["image"] = standout
        if hasattr(db_obj, "sharedInbox") and db_obj.sharedInbox and visibility in [Visibility.WEB]:
            properties["endpoints"] = {"sharedInbox": db_obj.sharedInbox}
        properties["@context"].append(context)
        return properties

    def build(
        self,
        db: Session,
        *,
        db_obj,
        language: Locale = settings.DEFAULT_LANGUAGE,
        visibility: Visibility = Visibility.PUBLIC,
    ) -> dict[str, any]:
        # additional parameters
        summary = self._get_summary(db_obj=db_obj, language=language)
        icon = self._get_image(db=db, image_id=db_obj.icon_id, image_url=db_obj.iconURL)
        # build
        response = activitystreams.Actor(
            id=db_obj.URI,
            url=db_obj.URL,
            type=db_obj.type.value,
            preferred_username=db_obj.preferredUsername,
            name=db_obj.name,
            inbox=db_obj.inbox,
            outbox=db_obj.outbox,
            followers=db_obj.followers,
            following=db_obj.following,
            public_key=db_obj.publicKey,
            public_key_name=regex.publicKey,
            icon=icon,
            summary=summary,
            properties=self._get_properties(
                db=db,
                db_obj=db_obj,
                language=language,
                visibility=visibility,
            ),
        )
        return response.build(visibility)


actor = CRUDActor(model=Actor, i18n_terms={"summary": ActorSummary, "summary_raw": ActorSummaryRaw})
