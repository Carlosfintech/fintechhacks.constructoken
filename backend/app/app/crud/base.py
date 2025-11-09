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

from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept
from pydantic import BaseModel
from sqlalchemy.orm import Session, Query
from ulid import ULID
from pydantic import HttpUrl
from babel import Locale, UnknownLocaleError
from copy import deepcopy

# from bovine.activitystreams.utils import actor_for_object
from bovine.activitystreams import factories_for_actor_object
from bovine.activitystreams.activity_factory import ActivityFactory
from bovine.activitystreams.object_factory import ObjectFactory
from bovine import BovineActor
from bovine.activitystreams import Actor as BovineStreamsActor

from app.db.base_class import Base
from app.models.activitypub.tag import Tag
from app.core.config import settings

from app.utilities.regexes import regex

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        *,
        model: Type[ModelType],
        i18n_terms: dict[str, DeclarativeAttributeIntercept] = {},
    ):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.i18n_terms = i18n_terms

    ###################################################################################################
    # COMMON CREATE, READ, UPDATE, DELETE
    ###################################################################################################

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        if isinstance(id, ULID):
            id = str(id)
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_uri(self, db: Session, URI: str | HttpUrl) -> Optional[ModelType]:
        if isinstance(URI, HttpUrl):
            URI = str(URI)
        return db.query(self.model).filter(self.model.URI == URI).first()

    def get_multi(self, db: Session, *, page: int = 0, page_break: bool = False) -> list[ModelType]:
        db_objs = db.query(self.model)
        if not page_break:
            if page > 0:
                db_objs = db_objs.offset(page * settings.MULTI_MAX)
            db_objs = db_objs.limit(settings.MULTI_MAX)
        return db_objs.all()

    def create_tags(
        self,
        db: Session,
        *,
        objs_in: list[dict[str, str]],
        language: Locale = settings.DEFAULT_LANGUAGE,
        is_local: bool = False,
        is_usable: bool = True,
    ) -> list[Tag]:
        # Automatically populate tags as a matter of course
        # Prevents tag term duplication (hopefully)
        db_objs = []
        for obj_in in objs_in:
            if not obj_in.get("name"):
                continue
            name = obj_in["name"]
            if "#" in name:
                name = regex.hashtag_root(name)
            lang = self._fix_language(obj_in.get("language", language))
            if not name:
                continue
            try:
                # https://stackoverflow.com/a/52075777/295606
                db_obj = Tag(
                    **{
                        "language": lang,
                        "name": name,
                        "local": is_local,
                        "usable": is_usable,
                    }
                )
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
            except IntegrityError:
                db.rollback()
                db_obj = db.query(Tag).filter(Tag.name == name).first()
            if db_obj:
                db_objs.append(db_obj)
        return db_objs

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        # obj_in_data = jsonable_encoder(obj_in)
        if not isinstance(obj_in, dict):
            obj_in = obj_in.model_dump(exclude_unset=True, mode="json")
        obj_in_data = deepcopy(obj_in)
        if hasattr(self.model, "tag") and obj_in_data.get("tag", False):
            tag_objs = obj_in_data.pop("tag", None)
            is_local = False
            if hasattr(self.model, "URI") and obj_in_data.get("URI", False):
                is_local = regex.url_is_local(obj_in_data["URI"])
            # 'tg' for the database, vs 'tag' for the list of terms
            obj_in_data["tg"] = self.create_tags(db=db, objs_in=tag_objs, is_local=is_local)
        if hasattr(self.model, "country") and obj_in_data.get("country", False):
            obj_in_data["country"] = obj_in["country"]
        if hasattr(self.model, "language") and obj_in_data.get("language", False):
            obj_in["language"] = self._fix_language(obj_in["language"])
            # This will be the default language
            obj_in_data["language"] = obj_in["language"]
        for field in self.i18n_terms.keys():
            if obj_in_data.get(field, False):
                # Now, have two options ... value can be a string, or a dict of different languages
                if isinstance(obj_in_data[field], str):
                    obj_in_data[field] = {
                        obj_in["language"]: self.i18n_terms[field](obj_in["language"], obj_in_data[field])
                    }
                elif isinstance(obj_in_data[field], dict):
                    # ASSUME: has form {'language': 'text'}
                    obj_in_field = {}
                    for k, v in obj_in_data[field].items():
                        k = self._fix_language(k)
                        obj_in_field[k] = self.i18n_terms[field](k, v)
                    if obj_in_field:
                        obj_in_data[field] = obj_in_field
        if not hasattr(self.model, "language") and obj_in_data.get("language", False):
            # for 'reasons' no default language - usually derived from parent
            del obj_in_data["language"]
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if not db_obj.id == update_data["id"]:
            raise ValueError("Update error: mismatch between object and update data.")
        # CLEAN UP DICT
        update_data.pop("id", None)
        language = update_data.pop("language", None)
        # Seems to commit to db as lowercase, so ensure this when checking for updates
        language = self._fix_language(language)
        if hasattr(db_obj, "language") and not db_obj.language and language:
            db_obj.language = language
        # UPDATE LOOP
        for field in update_data:
            if not hasattr(self.model, field):
                continue
            if field == "tag":
                tag_attrs = [attr for attr in getattr(db_obj, "tag")]
                tag_objs = self.create_tags(db=db, objs_in=update_data.get(field, set()))
                for tag_attr in tag_attrs:
                    db_obj.tag.remove(tag_attr)
                # 'tg' for the database, vs 'tag' for the list of terms
                db_obj.tg = tag_objs
                # for tag_obj in tag_objs:
                #     # 'tg' is the actual table, but 'tag' is an association proxy
                #     print("---------------------------------------------------------------------")
                #     print(tag_obj)
                #     db_obj.tag.add(tag_obj)
            elif field in self.i18n_terms and language:
                # Create of the form Model(language, term, db_obj)
                i18n_obj = getattr(db_obj, field)
                str_lang = str(language)
                if i18n_obj and i18n_obj.get(str_lang):
                    i18n_obj = i18n_obj[str_lang]
                    setattr(i18n_obj, field, update_data[field][str_lang])
                else:
                    i18n_obj = self.i18n_terms[field](language, update_data[field], db_obj)
                db.add(i18n_obj)
                print("----------------------------------update-----------------------------------")
                print(i18n_obj)
                print(field, language, update_data[field])
                print("----------------------------------update-----------------------------------")
                db.commit()
            else:
                if isinstance(update_data[field], HttpUrl):
                    update_data[field] = str(update_data[field])
                setattr(db_obj, field, update_data[field])
                db.add(db_obj)
                db.commit()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> ModelType:
        if isinstance(id, ULID):
            id = str(id)
        obj = db.query(self.model).filter(self.model.id == id).first()
        db.delete(obj)
        db.commit()
        return obj

    def remove_by_uri(self, db: Session, *, URI: str | HttpUrl) -> ModelType:
        if isinstance(URI, HttpUrl):
            URI = str(URI)
        obj = db.query(self.model).filter(self.model.URI == URI).first()
        db.delete(obj)
        db.commit()
        return obj

    ###################################################################################################
    # FOR LANGUAGE-SPECIFIC SCHEMA OUTPUT
    ###################################################################################################

    def _hasattr(self, obj: ModelType | dict, field: str) -> any:
        """
        Convenience method for objects which may be of either a model type, or a dictionary.
        """
        if isinstance(obj, dict):
            return field in obj
        else:
            return hasattr(obj, field)

    def _getattr(self, obj: ModelType | dict, field: str) -> any:
        """
        Convenience method for objects which may be of either a model type, or a dictionary.
        """
        if isinstance(obj, dict):
            return obj.get(field)
        elif isinstance(obj, str):
            return obj
        else:
            return getattr(obj, field)

    def get_schema_by_language(
        self, *, db_obj: ModelType, schema: BaseModel, language: str | Locale = settings.DEFAULT_LANGUAGE
    ) -> dict[str, Any]:
        obj_out = {}
        language = self._fix_language(language)
        if isinstance(db_obj, dict):
            # `db_obj` is not a database object but a dictionary
            language = str(language)
        else:
            language = self._fix_language_for_db(language)
        fallback_language = None
        for field in schema.model_fields.keys():
            if not self._hasattr(db_obj, field):
                continue
            if field in self.i18n_terms:
                i18n_obj = self._getattr(db_obj, field)
                if not i18n_obj:
                    continue
                if i18n_obj.get(language):
                    obj_out[field] = self._getattr(i18n_obj[language], field)
                elif isinstance(db_obj, dict) and db_obj.get("language") and i18n_obj.get(db_obj["language"]):
                    # Again, the `db_obj` isn't an instance of the ModelType
                    fallback_language = str(db_obj["language"])
                    obj_out[field] = self._getattr(i18n_obj[fallback_language], field)
                elif not isinstance(db_obj, dict) and i18n_obj.get(db_obj.language):
                    obj_out[field] = self._getattr(i18n_obj[db_obj.language], field)
                    fallback_language = str(db_obj.language)
            else:
                attr = self._getattr(db_obj, field)
                if not isinstance(attr, Query):
                    obj_out[field] = attr
        if fallback_language:
            obj_out["language"] = fallback_language
        elif language:
            obj_out["language"] = language
        return schema(**obj_out)

    ###################################################################################################
    # BOVINE AND ACTIVITYSTREAM UTILITIES
    ###################################################################################################

    def create_stream_id(self, id: str | ULID = None):
        if not id:
            id = str(ULID())
        return f"{settings.SERVER_HOST}/{id}"

    def creator_requests_actor(self, db_obj: Any) -> BovineActor:
        URI = db_obj.URI
        publicKeyURI = db_obj.publicKeyURI
        if not URI:
            URI = f"https://{settings.SERVER_HOST}/{db_obj.preferredUsername}"
        if not publicKeyURI:
            publicKeyURI = f"{URI}#main-key"
        return BovineActor(
            actor_id=URI,
            public_key_url=publicKeyURI,
            secret=db_obj.privateKey,
        )

    def get_factories_for_actor(self, *, db_obj: Any) -> tuple[ActivityFactory, ObjectFactory]:
        """
        Builds the Bovine actor factories permitting activitystream requests
        """
        obj_in = BovineStreamsActor(
            id=f"https://{settings.SERVER_HOST}/{db_obj.preferredUsername}",
            preferred_username=db_obj.preferredUsername,
            name=db_obj.name,
            inbox=db_obj.inbox,
            outbox=db_obj.outbox,
            public_key=db_obj.publicKey,
            public_key_name="main-key",
        ).build()
        # returns activity_factory, object_factory
        return factories_for_actor_object(obj_in)

    async def post_to_inbox(self, *, actor: Any, message: dict[str, Any], inbox: str) -> str:
        actor = self.creator_requests_actor(db_obj=actor)
        await actor.init()
        response = await actor.post(inbox, message)
        await actor.session.close()
        return response

    ###################################################################################################
    # GENERAL UTILITIES
    ###################################################################################################

    def _fix_language(self, language: str | Locale | None) -> Optional[Locale]:
        # Locale is saved as lowercase to the db
        if language and isinstance(language, Locale):
            language = Locale(str(language).lower())
        if language and isinstance(language, str):
            try:
                language = language.replace("-", "_")
                language = Locale(language.lower())
            except UnknownLocaleError:
                language = settings.DEFAULT_LANGUAGE
        return language

    def _fix_language_for_db(self, language: str | Locale | None) -> Optional[Locale]:
        # For fetching language-defined db termslanguage = str(db_actor.language)
        language = str(self._fix_language(language))
        language = language.split("_")
        if len(language) == 2:
            language = Locale(language[0], language[1].upper())
        else:
            language = Locale(language[0])
        return language
