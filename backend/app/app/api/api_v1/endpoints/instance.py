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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from babel import Locale

from app.core.config import settings
from app import crud, schemas
from app.api import deps

router = APIRouter(lifespan=deps.get_lifespan)


@router.get("/rules", response_model=list[schemas.Rule])
def get_instance_rules(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    language: str | None = settings.SERVER_LANGUAGE,
) -> Any:
    """
    Get the list of instance rules in a selected language.
    """
    db_objs = crud.rules.get_multi(db=db)
    if not db_objs:
        raise HTTPException(
            status_code=400,
            detail="Rules unavailable.",
        )
    return [
        schemas.Rule(**{"language": language, "text": db_obj.text[Locale(language)].text, "order": db_obj.order})
        for db_obj in db_objs
        if not db_obj.deleted
    ]
