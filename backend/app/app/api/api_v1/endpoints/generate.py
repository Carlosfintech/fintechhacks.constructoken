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
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.utilities.fakenews import FakeNews

"""
GENERATOR FUNCTIONS - ONLY FOR DEVELOPMENT

Delete all of this after you have completed development. This is purely a set of convenience functions to
support generating personas, posts, and ActivityPub-based actions.
"""

router = APIRouter(lifespan=deps.get_lifespan)


@router.post("/creator", response_model=schemas.GeneratorCreator)
def create_persona_with_creator(*, db: Annotated[Session, Depends(deps.get_db)]) -> Any:
    """
    Generate a new ActivityPub `Person` profile. Creates both a 'creator' and 'actor'. Uses default password 'changethis'.
    """
    faker = FakeNews()
    # Create creator
    db_creator = faker.create_creator(db=db, password="changethis")
    # Create persona
    faker.create_actor(db=db, creator=db_creator)
    return schemas.GeneratorCreator(**{"email": db_creator.email, "password": "changethis"})


@router.post("/persona", response_model=schemas.Actor)
def create_persona(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Generate a new ActivityPub `Person` profile. Creates both an 'actor'.
    """
    faker = FakeNews()
    # Create persona
    db_obj = faker.create_actor(db=db, creator=creator)
    return db_obj
