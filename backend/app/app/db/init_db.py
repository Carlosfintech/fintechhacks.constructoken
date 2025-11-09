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

from app import crud, schemas, schema_types
from app.core.config import settings
from app.db import base  # noqa: F401
from app.utilities.regexes import regex

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    creator = crud.creator.get_by_email(db, email=settings.FIRST_ADMIN)
    if not creator:
        # Create creator auth
        creator_in = schemas.CreatorCreate(
            email=settings.FIRST_ADMIN,
            password=settings.FIRST_ADMIN_PASSWORD,
            is_admin=True,
        )
        creator = crud.creator.create(db, obj_in=creator_in)  # noqa: F841
    preferredUsername = regex.url_root(settings.SERVER_HOST).replace("-", "_")
    actor = crud.actor.get_by_name(db=db, name=preferredUsername)
    if not actor:
        # Create the default site Actor
        actor_in = schemas.ActorCreate(
            **{
                "type": schema_types.ActorType.Service,
                "preferredUsername": preferredUsername,
                "creator_id": str(creator.id),
            }
        )
        actor_in = actor_in.model_dump(exclude_unset=True, mode="json")
        actor_in["preferredUsername"] = preferredUsername
        actor = crud.actor.create(db=db, obj_in=actor_in)  # noqa: F841
