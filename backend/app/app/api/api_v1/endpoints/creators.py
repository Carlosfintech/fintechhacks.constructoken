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

from typing import Annotated, Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.core import security
from app.utilities import (
    send_new_account_email,
)

router = APIRouter(lifespan=deps.get_lifespan)


@router.post("/", response_model=schemas.Creator)
def create_creator_profile(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    password: str = Body(...),
    email: EmailStr = Body(...),
) -> Any:
    """
    Create new creator without the need to be logged in.
    """
    creator = crud.creator.get_by_email(db, email=email)
    if creator:
        raise HTTPException(
            status_code=400,
            detail="This creatorname is not available.",
        )
    # Create creator auth
    creator_in = schemas.CreatorCreate(
        password=password,
        email=email,
    )
    creator = crud.creator.create(db, obj_in=creator_in)
    return creator


@router.put("/", response_model=schemas.Creator)
def update_creator(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    obj_in: schemas.CreatorUpdate,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Update creator.
    """
    if creator.hashed_password:
        creator = crud.creator.authenticate(db, email=creator.email, password=obj_in.original)
        if not obj_in.original or not creator:
            raise HTTPException(status_code=400, detail="Unable to authenticate this update.")
    creator_data = jsonable_encoder(creator)
    creator_in = schemas.CreatorUpdate(**creator_data)
    if obj_in.password is not None:
        creator_in.password = obj_in.password
    if obj_in.email is not None:
        check_creator = crud.creator.get_by_email(db, email=obj_in.email)
        if check_creator and check_creator.email != creator.email:
            raise HTTPException(
                status_code=400,
                detail="This creatorname is not available.",
            )
        creator_in.email = obj_in.email
    creator = crud.creator.update(db, db_obj=creator, obj_in=creator_in)
    return creator


@router.get("/", response_model=schemas.Creator)
def read_creator(
    *,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Get current creator.
    """
    return creator


@router.get("/identities", response_model=list[schemas.Actor])
async def read_creator_identities(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
    page: int = 0,
    language: str | None = settings.SERVER_LANGUAGE,
) -> Any:
    """
    For the current creator, get a list of all the Actor identities they control.
    """
    db_objs = crud.actor.get_actors_by_creator(db_creator=creator, page=page)
    return [
        await crud.actor.get_profile_by_language(db=db, db_obj=db_obj, language=language, as_local=True)
        for db_obj in db_objs
    ]


@router.get("/all", response_model=List[schemas.Creator])
def read_all_creators(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    page: int = 0,
    creator: Annotated[models.Creator, Depends(deps.get_active_admin)],
) -> Any:
    """
    Retrieve all current creators.
    """
    return crud.creator.get_multi(db=db, page=page)


@router.post("/new-totp", response_model=schemas.NewTOTP)
def request_new_totp(
    *,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Request new keys to enable TOTP on the creator account.
    """
    obj_in = security.create_new_totp(label=creator.email)
    # Remove the secret ...
    obj_in.secret = None
    return obj_in


@router.post("/toggle-state", response_model=schemas.Msg)
def toggle_state(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    creator_in: schemas.CreatorUpdate,
    creator: Annotated[models.Creator, Depends(deps.get_active_admin)],
) -> Any:
    """
    Toggle creator state (moderator function)
    """
    response = crud.creator.toggle_creator_state(db=db, obj_in=creator_in)
    if not response:
        raise HTTPException(
            status_code=400,
            detail="Invalid request.",
        )
    return {"msg": "Creator state toggled successfully."}


@router.post("/create", response_model=schemas.Creator)
def create_creator(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    creator_in: schemas.CreatorCreate,
    creator: Annotated[models.Creator, Depends(deps.get_active_admin)],
) -> Any:
    """
    Create new creator (moderator function).
    """
    creator = crud.creator.get_by_email(db, email=creator_in.email)
    if creator:
        raise HTTPException(
            status_code=400,
            detail="The creator with this creatorname already exists in the system.",
        )
    creator = crud.creator.create(db, obj_in=creator_in)
    if settings.emails_enabled and creator_in.email:
        send_new_account_email(email_to=creator_in.email, creatorname=creator_in.email, password=creator_in.password)
    return creator


@router.get("/tester", response_model=schemas.Msg)
def test_endpoint() -> Any:
    """
    Test current endpoint.
    """
    return {"msg": "Message returned ok."}
