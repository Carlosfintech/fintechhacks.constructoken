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

from typing import Any
from sqlalchemy.orm import Session
from pydantic import HttpUrl
from fastapi.encoders import jsonable_encoder
from aiohttp import ClientResponse

from app.crud.base import CRUDBase
from app.models.follow import Follow
from app.schemas import FollowCreate, FollowUpdate, InboxActivity, NotificationCreate
from app.schema_types import ActivityType, NotificationType
from app.utilities.regexes import regex


class CRUDFollow(CRUDBase[Follow, FollowCreate, FollowUpdate]):
    """
    All CRUD for Follows.

    https://www.w3.org/TR/activitystreams-vocabulary/#dfn-follow
    https://github.com/boyter/activitypub/blob/main/follow-post.md
    https://www.rfc-editor.org/rfc/rfc3339

    Published time should be in RFC3339 and look like the following 2006-01-02T15:04:05Z07:00.

    The follow accept is not actually required for a follow to work, but is usually done in order to confirm that
    the follow request has been accepted. In the case where a instance user has set to manually approve follow
    requests this process can take an indefinate amount of time.

    Example follow request to be POST'ed to a user we want to follow.

        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "actor": "https://some.instance/u/followinguser",
            "id": "https://some.instance/u/followinguser/sub/someuniqueid",
            "object": "https://another.instance/u/userwewanttofollow",
            "published": "2006-01-02T15:04:05Z07:00",
            "to": "https://some.instance/u/%s/inbox",
            "type": "Follow"
        }

    `Undo` is the Undo activity with this exact `Follow` object as a sub-object.

    Any local Actor can *only* trigger an ActivityStream request after authentication.
    """

    ###################################################################################################
    # COMMON CREATE, READ, UPDATE, DELETE
    ###################################################################################################

    def create(self, db: Session, actor: Any, target: Any, URI: str | HttpUrl) -> Any:
        # Create the db_obj
        obj_in = FollowCreate(**{"actor_id": actor.id, "target_id": target.id, "URI": str(URI)})
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        return db.refresh(db_obj)

    def update(self, db: Session, *, URI: str | HttpUrl, response: ActivityType) -> Any:
        """
        Retrieve and update/remove Follow object. Activity response processed elsewhere.
        """
        if response in [ActivityType.Reject, ActivityType.Undo]:
            # REJECT OR REMOVE
            db_obj = self.remove_by_uri(db=db, URI=URI)
        else:
            # ACCEPT
            db_obj = self.get_by_uri(db=db, URI=URI)
            if db_obj:
                db_obj.has_accepted = True
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
        return db_obj

    ###################################################################################################
    # BOVINE AND ACTIVITYSTREAM UTILITIES
    # NOTE: ALL THESE REQUIRE AUTHENTICATION OF THE ACTOR
    ###################################################################################################

    async def request(self, actor: Any, target: Any) -> ClientResponse:
        # Post the activity to the appropriate inbox
        activity_factory, _ = self.get_factories_for_actor(db_obj=actor)
        message = activity_factory.follow(target.URI, id=self.create_stream_id()).build()
        # Target sends the response to the original Actor's inbox
        return await self.post_to_inbox(actor=actor, message=message, inbox=target.inbox)

    async def respond(self, db: Session, *, db_obj: Any, response: ActivityType) -> ClientResponse:
        # https://codeberg.org/bovine/bovine/src/commit/14ed6026df16059c4529bf7a46a5677b9de235a4/bovine/bovine/activitystreams/activity_factory.py
        activity_factory, _ = self.get_factories_for_actor(db_obj=db_obj.target)
        message = activity_factory.follow(db_obj.target.URI, id=db_obj.URI).build()
        match response:
            case ActivityType.Accept:
                message = activity_factory.accept(message).build()
            case ActivityType.Reject:
                message = activity_factory.reject(message).build()
            case ActivityType.Undo:
                message = activity_factory.undo(message).build()
            case _:
                raise ValueError(f"Unknown ActivityType: {response}")
        return await self.post_to_inbox(actor=db_obj.actor, message=message, inbox=db_obj.target.inbox)

    ###################################################################################################
    # INBOX PROCESS - ACTORS VALIDATED
    ###################################################################################################

    async def process_inbox(self, db: Session, *, obj_in: InboxActivity, actor: Any, target: Any) -> NotificationCreate:
        """
        Has already been sorted, so can make some assumptions in the ActivityType.
        """
        notice = None
        match obj_in.type:
            case ActivityType.Follow:
                # Create
                self.create(db=db, actor=actor, target=target, URI=obj_in.URI)
                notice = NotificationType.FollowRequest
                # Is the target actor local and do they automatically accept follow requests
                if not target.locked and regex.url_is_local(url=target.URI):
                    response = await self.respond(db=db, URI=obj_in.URI, response=ActivityType.Accept)
                    if not response.status == 202:
                        raise ValueError(str(response))
                    notice = NotificationType.Follow
            case _:
                self.update(db=db, URI=obj_in.URI, response=obj_in.type)
        # And notify the Actor
        if notice:
            return NotificationCreate(**{"type": notice, "actor_id": target.id, "origin_id": actor.id})
        return None


follow = CRUDFollow(model=Follow)
