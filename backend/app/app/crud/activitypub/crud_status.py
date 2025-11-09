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

from pydantic import HttpUrl
from sqlalchemy.orm import Session
from babel import Locale
from bovine import activitystreams
from bovine.types import Visibility
from copy import deepcopy

from app.core.config import settings
from ..base import CRUDBase

from app.models.activitypub.actor import Actor
from app.models.activitypub.status import (
    Status,
    StatusContentHeader,
    StatusContentHeaderRaw,
    StatusContent,
    StatusContentRaw,
)
from app.models.activitypub.media import MediaAttachment
from app.schemas import (
    StatusCreate,
    ActivityStatusCreate,
    StatusUpdate,
    MediaAttachmentCreate,
    Actor as ActorProfile,
    Status as StatusPost,
)
from app.utilities.regexes import regex

# from app.utilities.parser import dataparser
from .crud_actor import actor as crud_actor
from ..crud_source import source as crud_source
from .crud_media import media as crud_media


class CRUDStatus(CRUDBase[Status, StatusCreate, StatusUpdate]):
    """
    All CRUD for Status.

    https://www.w3.org/TR/activitystreams-vocabulary/#dfn-follow
    """

    ###################################################################################################
    # CORE CRUD
    ###################################################################################################

    """
    A new Status must be processed carefully. After 'Mentions' are extracted, they must be Fetched and then
    the content and content headers converted to HTML.
    """

    ###################################################################################################
    # FETCH REMOTE STATUS
    ###################################################################################################

    """
    Actors listed in 'Mentions' for a remote status are not imported or built. If a remote Status is Shared
    Then it is treated as if it originated locally.
    """

    def get_status_actor_state(self, *, db: Session, db_actor: Actor, status: dict) -> dict:
        if status.get("URI"):
            db_obj = self.get_by_uri(db=db, URI=status["URI"])
            if db_obj:
                status["has_shared"] = db_actor.has_shared(db_actor.id, db_obj.id)
                status["has_liked"] = db_actor.has_liked(db_actor.id, db_obj.id)
                status["has_bookmarked"] = db_actor.has_bookmarked(db_actor.id, db_obj.id)
        return status

    async def fetch_remote_statuses(
        self,
        *,
        db: Session,
        db_actor: Actor,
        db_obj: Actor,
        remote_id: str,
        max_items: int | None = 19,
        language: str | Locale = settings.DEFAULT_LANGUAGE,
    ) -> list[StatusPost]:
        """
        NOTE: `db_obj` is the remote actor *being* queried, `db_actor` is the actor *performing* the request.
        """
        # Initialise requesting actor
        actor = crud_actor.get_requests_actor(db_obj=db_actor)
        await actor.init()
        # Prepare requested actor
        db_obj.is_following = db_actor.is_following(db_obj.id)
        db_obj.is_followed = db_actor.is_followed(db_obj.id)
        actor_in = (
            await crud_actor.get_profile_by_language(
                db=db, actor=actor, db_obj=db_obj, schema=ActorProfile, language=language
            )
        ).model_dump()
        # Prepare statuses
        statuses = await actor.get_ordered_collection(remote_id, max_items)
        status_out = []
        for status in statuses.get("items", []):
            # TODO: check if any status is by a blocked actor and exclude it
            status = status.get("object", status)
            is_share = False
            if isinstance(status, str):
                # Could be resharing own status
                is_share = True
                try:
                    status = await actor.get(status)
                except Exception:
                    continue
            if not isinstance(status, dict):
                continue
            status = ActivityStatusCreate.model_validate(status).model_dump()
            status = self.get_status_actor_state(db=db, db_actor=db_actor, status=status)
            actorURI = str(status.get("actorURI"))
            status = self.get_schema_by_language(db_obj=status, schema=StatusPost).model_dump()
            if is_share:
                # This is a shared status, potentially as part of a status update ('quote tweet')
                if actorURI != db_obj.URI:
                    status["actor"] = await crud_actor.fetch_remote(db=db, db_actor=db_actor, remote_id=actorURI)
                    if status["actor"]:
                        status["actor"].is_following = db_actor.is_following(status["actor"].id)
                        status["actor"].is_followed = db_actor.is_followed(status["actor"].id)
                        status["actor"] = (
                            await crud_actor.get_profile_by_language(
                                db=db, actor=actor, db_obj=status["actor"], schema=ActorProfile, language=language
                            )
                        ).model_dump()
                else:
                    status["actor"] = actor_in
                status_in = {
                    "actor": actor_in,
                    "share": status,
                }
            else:
                status_in = status
                status_in["actor"] = actor_in
            status_out.append(status_in)
        await actor.session.close()
        return [StatusPost.model_validate(s) for s in status_out]

    def create_or_update_remote_attachments(self, *, db: Session, db_obj: Status, obj_in: ActivityStatusCreate):
        """
        Unlike with Actors, images/media are stored as attachments.

        Do this *after* creating the remote Status object.
        """
        attachments = {a.remoteURL: a for a in db_obj.attachments if a.remoteURL}
        for attch in obj_in.attachments:
            if attch.get("mediaType") and attch.get("url") and attch.get("type") == "Document":
                media_in = MediaAttachmentCreate(
                    **{
                        "status_id": str(obj_in.id),
                        "actor_id": str(obj_in.creator_id),
                        "created": obj_in.created,
                        "content_type": attch["mediaType"],
                        "remoteURL": attch["url"],
                    }
                )
                if attch.get("name"):
                    media_in.text = {obj_in.language: media_in["name"]}
                # And create the media attachment
                if attachments.get(media_in.remoteURL):
                    crud_media.update(db=db, db_obj=attachments[media_in.remoteURL], obj_in=media_in)
                    del attachments[media_in.remoteURL]
                else:
                    crud_media.create(db=db, obj_in=media_in)
        # Also need to process any attachments that have been removed
        for attachment in attachments.values():
            crud_media.remove(db=db, id=attachment.id)
        db.refresh(db_obj)
        return db_obj

    async def fetch_remote(self, *, db: Session, URI: str | HttpUrl) -> Status:
        if not regex.url_validates(URI):
            raise ValueError(f"URL is invalid: '{URI}'")
        # FIRST: CHECK IF WE HAVE IT
        db_obj = self.get_by_uri(db=db, URI=URI)
        if db_obj and not db_obj.is_local and crud_source.should_fetch(db_obj.fetched):
            db_obj = await self.create_or_update_remote(db=db, db_obj=db_obj)
        if db_obj:
            return db_obj
        # ELSE: FETCH IT AND RETURN THE DB_OBJ
        return self.create_or_update_remote(db=db, URI=URI)

    async def create_or_update_remote(self, *, db: Session, db_obj: Status = None, URI: str | HttpUrl) -> Status:
        if db_obj:
            URI = db_obj.URI
        actor = self.get_site_actor(db=db)
        await actor.init()
        remote_status = await actor.get(URI)
        obj_in = ActivityStatusCreate.model_validate(remote_status)
        obj_in.fetched = crud_source.get_now()
        if obj_in.actorURI:
            db_actor = crud_actor.fetch_remote(db=db, remote_id=obj_in.actorURI)
            if db_actor:
                obj_in.creator_id = db_actor.id
        await actor.session.close()
        attachments = []
        if obj_in.attachments:
            attachments = deepcopy(obj_in.attachments)
            obj_in.attachments = []
        if db_obj:
            obj_in.id = db_obj.id
            db_obj = self.update(db=db, db_obj=db_obj, obj_in=obj_in)
        else:
            db_obj = self.create(db=db, obj_in=obj_in)
        if attachments:
            obj_in.attachments = attachments
            db_obj = self.create_or_update_remote_attachments(db=db, db_obj=db_obj, obj_in=obj_in)
        return db_obj

    async def fetch_mentions(self, *, db: Session, mentions: list[str]) -> list[Status]:
        return [await self.fetch_remote(db=db, remote_id=m) for m in mentions]

    ###################################################################################################
    # BUILD STATUS ACTIVITY STREAM
    ###################################################################################################

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
        """
        Unlike with Actors, images/media are stored as attachments.
        """
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
        response = activitystreams.Status(
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


status = CRUDStatus(
    model=Status,
    i18n_terms={
        "content_header": StatusContentHeader,
        "content_header_raw": StatusContentHeaderRaw,
        "content": StatusContent,
        "content_raw": StatusContentRaw,
    },
)
