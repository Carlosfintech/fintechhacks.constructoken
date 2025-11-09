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

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
from ulid import ULID

from app import crud, models, schemas, schema_types
from app.api import deps
from app.api.validation import FormValidationErrorRoute
from app.api.generic import GenericModelValidator
from app.core.config import settings
from app.utilities.activity import ActivityResponse

router = APIRouter(lifespan=deps.get_lifespan, route_class=FormValidationErrorRoute)


@router.get("/check/{name}", status_code=status.HTTP_202_ACCEPTED)
def check_persona_name(*, db: Annotated[Session, Depends(deps.get_db)], name: str) -> Any:
    """
    Check whether a proposed persona name is valid and available.
    """
    db_response = crud.actor.check_persona_name(db=db, name=name)
    if not db_response:
        raise HTTPException(
            status_code=400,
            detail="Name unavailable.",
        )


@router.post("/media", response_model=schemas.Msg)
async def create_media_for_actor(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    data: Annotated[schemas.MediaAttachmentCreate, Depends(GenericModelValidator(schemas.MediaAttachmentCreate))],
    file: Annotated[UploadFile, File(...)],
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    # correct - it's to the public directory
    path = Path(settings.API_MEDIA_STR)
    if data.as_avatar:
        maker_id = data.actor_avatar_id
        media_folder = settings.API_AVATAR_DIRECTORY
    if data.as_standout:
        maker_id = data.actor_standout_id
        media_folder = settings.API_STANDOUT_DIRECTORY
    db_obj = creator.get_actor_by_id(maker_id)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    if file.size > settings.DEFAULT_MEDIA_MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Media size not permitted. Try something smaller.",
        )
    # Remove old media, if it exists
    if data.as_avatar and db_obj.icon:
        crud.source.delete_file(source=db_obj.icon.path)
        crud.media.remove(db=db, id=db_obj.icon.id)
    if data.as_standout and db_obj.standout:
        crud.source.delete_file(source=db_obj.standout.path)
        crud.media.remove(db=db, id=db_obj.standout.id)
    # TODO: Will need to develop methods for downscaling images, as appropriate
    path = path / str(maker_id) / media_folder
    media_name = f"{ULID()}.{file.filename.split('.')[-1]}"
    data.path = str(path / media_name)
    data.URL = f"{settings.SERVER_HOST}/{path}/{media_name}"
    data.file_size = file.size
    crud.source.save_media_file(data=file, folder_id=path, source_id=media_name)
    crud.media.create(db, obj_in=data)
    # And update the Actor
    crud.actor.update_media_url(db=db, db_obj=db_obj, URL=data.URL, is_avatar=data.as_avatar)
    return {"msg": "Source files successfully uploaded."}


@router.post("/{actor_id}/{name}", response_model=schemas.Actor)
@router.post("/{name}", response_model=schemas.Actor)
async def create_actor(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    actor_id: str = None,
    name: str,
    language: str | None = settings.SERVER_LANGUAGE,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Create a new ActivityPub Actor.
    """
    # NOTE: create must be only the minimal fields (`name`, `preferredName`, `type`, `language`)
    db_response = crud.actor.check_persona_name(db=db, name=name)
    if not db_response:
        raise HTTPException(
            status_code=400,
            detail="Name unavailable.",
        )
    obj_in = schemas.ActorCreate(
        **{
            "preferredUsername": name,
            "type": schema_types.ActorType.Person,
            "creator_id": creator.id,
            "language": language,
        }
    )
    if actor_id:
        if not creator.get_actor_by_id(actor_id):
            raise HTTPException(
                status_code=400,
                detail="Actor not available.",
            )
        obj_in.type = schema_types.ActorType.Service
        obj_in.maker_id = actor_id
    if not creator.default_persona and obj_in.type == schema_types.ActorType.Person:
        obj_in.default_persona = True
    # Create persona
    db_obj = crud.actor.create(db, obj_in=obj_in)
    return await crud.actor.get_profile_by_language(db=db, db_obj=db_obj, language=language)


@router.put("/{id}", response_model=schemas.ActorMediaUpdate)
def update_actor(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    id: str,
    obj_in: schemas.ActorUpdate,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Update actor for a creator.
    """
    db_obj = creator.get_actor_by_id(obj_in.id)
    if not db_obj or id != db_obj.id:
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    obj_in = schemas.ActorUpdateIn(**obj_in.model_dump())
    db_obj = crud.actor.update(db=db, db_obj=db_obj, obj_in=obj_in)
    obj_in = crud.actor.get_schema_by_language(db_obj=db_obj, schema=schemas.ActorUpdate, language=obj_in.language)
    obj_in = schemas.ActorMediaUpdate(**obj_in.model_dump())
    if db_obj.icon:
        obj_in.icon = crud.media.get_schema_by_language(
            db_obj=db_obj.icon, schema=schemas.MediaAttachment, language=obj_in.language
        )
    if db_obj.standout:
        obj_in.standout = crud.media.get_schema_by_language(
            db_obj=db_obj.standout, schema=schemas.MediaAttachment, language=obj_in.language
        )
    return obj_in


@router.put("/{id}/media/{media_id}", response_model=schemas.ActorMediaUpdate)
async def update_media_for_actor(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    id: str,
    media_id: str,
    obj_in: schemas.MediaAttachmentUpdate,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    db_obj = creator.get_actor_by_id(obj_in.id)
    if not db_obj or id != db_obj.id:
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    media_obj = db_obj.icon
    if obj_in.as_standout:
        media_obj = db_obj.standout
    if media_obj.id != obj_in.id or media_obj.id != media_id:
        raise HTTPException(
            status_code=400,
            detail="Media not available.",
        )
    crud.media.update(db, db_obj=media_obj, obj_in=obj_in)
    return {"msg": "Source files successfully uploaded."}


@router.get("/lookup", response_model=schemas.Actor)
async def lookup_actor(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    creator: Annotated[models.Actor | None, Depends(deps.get_optional_creator)],
    handle: str,
    language: str | None = settings.SERVER_LANGUAGE,
) -> Any:
    """
    Get profile data for an individual Actor. If creator controls this actor, bypass some checks.
    """
    # Check if the resource_id exists in the local instance db
    name, domain, remote_id = crud.actor.parse_handle(resource_id=handle)
    # TODO: ensure that the handle isn't blocked, either by the site, or the requesting creator
    db_actor = None
    if creator:
        db_actor = creator.default_persona
    blocked_creator = False
    if (not creator and blocked_creator) or (creator and blocked_creator):
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    db_obj = crud.actor.get_by_name(db=db, name=name, domain=domain)
    if db_obj and db_obj.is_local:
        # Persona resides on this instance
        if (db_obj.silenced or db_obj.suspended) and (not creator or not creator.has_persona(db_obj.id)):
            raise HTTPException(
                status_code=400,
                detail="Actor not available.",
            )
    else:
        # Persona is remote
        db_obj = await crud.actor.fetch_remote(db=db, db_obj=db_obj, db_actor=db_actor, remote_id=remote_id)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail="Actor not found.",
        )
    return await crud.actor.get_profile_by_language(db=db, db_obj=db_obj, language=language)


@router.get("/update", response_model=schemas.ActorMediaUpdate)
async def lookup_actor_for_update(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    creator: Annotated[models.Creator | None, Depends(deps.get_active_creator)],
    handle: str,
    language: str | None = settings.SERVER_LANGUAGE,
) -> Any:
    """
    Get actor data for update by creator.
    """
    # Check if the resource_id exists in the local instance db
    name, domain, remote_id = crud.actor.parse_handle(resource_id=handle)
    # TODO: ensure that the handle isn't blocked, either by the site, or the requesting creator
    db_obj = creator.get_actor_by_handle(name)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    obj_in = crud.actor.get_schema_by_language(db_obj=db_obj, schema=schemas.ActorUpdate, language=language)
    obj_in = schemas.ActorMediaUpdate(**obj_in.model_dump())
    if db_obj.icon:
        obj_in.icon = crud.media.get_schema_by_language(
            db_obj=db_obj.icon, schema=schemas.MediaAttachment, language=obj_in.language
        )
    if db_obj.standout:
        obj_in.standout = crud.media.get_schema_by_language(
            db_obj=db_obj.standout, schema=schemas.MediaAttachment, language=obj_in.language
        )
    return obj_in


@router.get("/", response_model=list[schemas.Actor])
async def get_actors_for_creator(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
    actor_type: schema_types.ActorType = None,
    page: int = 0,
    page_break: bool = True,
    language: str | None = settings.SERVER_LANGUAGE,
) -> Any:
    """
    For the current creator, get a list of all the Actor identities they control. Default is to get everything.
    """
    db_objs = crud.actor.get_actors_by_creator(
        db_creator=creator, page=page, actor_type=actor_type, page_break=page_break
    )
    return [
        await crud.actor.get_profile_by_language(db=db, db_obj=db_obj, language=language, as_local=True)
        for db_obj in db_objs
    ]


@router.get("/{handle}/statuses", response_model=list[schemas.Status])
async def get_actor_statuses(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    creator: Annotated[models.Actor | None, Depends(deps.get_optional_creator)],
    handle: str,
    pinned: bool = False,
    next: str | None = None,
    language: str | None = settings.SERVER_LANGUAGE,
) -> Any:
    """
    Get status data for an individual Actor. If creator controls this actor, bypass some checks.

    NOTE: the request can be anonymous
    """
    # Check if the resource_id exists in the local instance db
    name, domain, remote_id = crud.actor.parse_handle(resource_id=handle)
    # TODO: ensure that the handle isn't blocked, either by the site, or the requesting creator
    db_actor = None
    if creator:
        db_actor = creator.default_persona
    blocked_creator = False
    if (
        (not creator and domain != settings.NGROK_DOMAIN)
        or (not creator and blocked_creator)
        or (creator and blocked_creator)
    ):
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    db_obj = crud.actor.get_by_name(db=db, name=name, domain=domain)
    if not db_obj or (db_obj and (db_obj.silenced or db_obj.suspended) and not creator.has_persona(db_obj.id)):
        raise HTTPException(
            status_code=400,
            detail="Actor not found.",
        )
    if next:
        request_id = next
    else:
        if pinned:
            request_id = db_obj.featured
        else:
            request_id = db_obj.outbox
    return await crud.status.fetch_remote_statuses(
        db=db, db_obj=db_obj, db_actor=db_actor, remote_id=request_id, language=language
    )


@router.get("/all", response_class=ActivityResponse)
def read_all_working_creators(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    page: int = 0,
) -> Any:
    """
    Retrieve all discoverable working creators.
    """
    return crud.actor.get_multi_creators(db=db, page=page)


# @router.get("/all", response_model=List[schemas.Creator])
# def read_all_actors(
#     *,
#     db: Annotated[Session, Depends(deps.get_db)],
#     page: int = 0,
#     creator: Annotated[models.Creator, Depends(deps.get_active_admin)],
# ) -> Any:
#     """
#     Retrieve all creators.
#     """
#     return crud.actor.get_multi(db=db, page=page)


@router.get("/associations", response_model=list[schemas.Actor])
async def get_all_associated_actors(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    handle: str,
    language: str | None = settings.SERVER_LANGUAGE,
    creator: Annotated[models.Actor | None, Depends(deps.get_optional_creator)],
) -> Any:
    """
    Retrieve all Actors associated with a specific Actor. Breaks on `type`, either work or creator.
    """
    # Check if the resource_id exists in the local instance db
    db_obj = crud.actor.get_by_resource(db=db, resource=handle)
    # TODO: ensure that the handle isn't blocked, either by the site, or the requesting creator
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    associations = []
    if db_obj.type == schema_types.ActorType.Service and db_obj.maker:
        # TODO: include all associations
        associations = [db_obj.maker]
    if db_obj.type == schema_types.ActorType.Person:
        associations = db_obj.works.limit(3).all()
    objs_in = [await crud.actor.get_profile_by_language(db=db, db_obj=obj, language=language) for obj in associations]
    return objs_in


@router.get("/{resource}", response_class=ActivityResponse)
def read_actor(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    resource: str,
    # creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Get Actor.
    """
    db_obj = crud.actor.get_by_resource(db=db, resource=resource)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail="Actor not found.",
        )
    if db_obj.silenced or db_obj.suspended:
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    return crud.actor.get_wellknown_actor(db=db, db_obj=db_obj)


@router.delete("/{id}", response_model=schemas.Msg)
def delete_actor(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    id: str,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Remove actor for a creator.
    """
    db_obj = creator.get_actor_by_id(id)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    crud.actor.remove(db=db, id=id)
    return {"msg": "Actor has been successfully removed."}


@router.delete("/{id}/media/{media_id}", response_model=schemas.Msg)
def delete_media(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    id: str,
    media_id: str,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Remove media for an actor.
    """
    db_obj = creator.get_actor_by_id(id)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail="Actor not available.",
        )
    as_avatar = None
    media_source = None
    if db_obj.icon and db_obj.icon.id == media_id:
        as_avatar = True
        media_source = db_obj.icon.path
    if db_obj.standout and db_obj.standout.id == media_id:
        as_avatar = False
        media_source = db_obj.standout.path
    if not isinstance(as_avatar, bool):
        raise HTTPException(
            status_code=400,
            detail="Media not available.",
        )
    crud.actor.update_media_url(db=db, db_obj=db_obj, URL=None, is_avatar=as_avatar)
    crud.source.delete_file(source=media_source)
    crud.media.remove(db=db, id=id)
    return {"msg": "Media has been successfully removed."}
