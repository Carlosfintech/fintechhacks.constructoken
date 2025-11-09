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

from sqlalchemy.orm import Session
from babel import Locale

from app.core.config import settings
from app.crud.base import CRUDBase
from app.models.activitypub.media import MediaAttachment, MediaDescription
from app.schemas.activitypub.media import (
    MediaAttachmentCreate,
    MediaAttachmentUpdate,
    MediaAttachment as MediaAttachmentOut,
)
from app.models.activitypub.actor import Actor
from app.schema_types import MediaType
from app.utilities.regexes import regex


class CRUDMedia(CRUDBase[MediaAttachment, MediaAttachmentCreate, MediaAttachmentUpdate]):
    """
    All CRUD for Medias.

    https://www.w3.org/TR/activitystreams-vocabulary/#object-types
    """

    def get_updateable_media(
        self, *, db: Session, db_actor: Actor, media_type: str, language: str | Locale = settings.DEFAULT_LANGUAGE
    ) -> MediaAttachmentOut:
        # Short-term for use in generated profiles
        db_refresh = False
        obj_in = {"type": MediaType.Image, "language": language, "text": db_actor.summary_raw[language].summary_raw}
        language = self._fix_language(language)
        if media_type == "icon":
            if db_actor.icon_id:
                db_obj = db_actor.icon
            if not db_actor.icon_id and db_actor.iconURL:
                obj_in["as_avatar"] = True
                if regex.url_is_local(db_actor.iconURL):
                    obj_in["URL"] = db_actor.iconURL
                else:
                    obj_in["remoteURL"] = db_actor.iconURL
                db_refresh = True
        if media_type == "standout":
            if db_actor.standout_id:
                db_obj = db_actor.standout
            if not db_actor.standout_id and db_actor.standoutURL:
                obj_in["as_standout"] = True
                if regex.url_is_local(db_obj.standoutURL):
                    obj_in["URL"] = db_obj.standoutURL
                else:
                    obj_in["remoteURL"] = db_obj.standoutURL
                db_refresh = True
        if db_refresh:
            db_obj = self.create(db=db, obj_in=obj_in)
            if media_type == "icon":
                db_actor.icon_id = db_obj.id
            if media_type == "standout":
                db_actor.standout_id = db_obj.id
            db.add(db_actor)
            db.commit()
            db.refresh(db_actor)
        if db_obj:
            # return db_obj
            return self.get_schema_by_language(db_obj=db_obj, schema=MediaAttachmentOut, language=language)
        return None


media = CRUDMedia(model=MediaAttachment, i18n_terms={"text": MediaDescription})
