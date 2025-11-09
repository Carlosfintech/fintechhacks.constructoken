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

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Any
from sqlalchemy.orm import Session

from app import schemas, crud
from app.api import deps
from app.core.config import settings

router = APIRouter(lifespan=deps.get_lifespan)


@router.get("/nodeinfo", response_model=schemas.NodeInfoRoot, response_model_exclude_none=True)
def read_nodeinfo_endpoint() -> Any:
    """
    Get wellknown nodeinfo endpoint.
    """
    return schemas.NodeInfoRoot(
        **{
            "links": [
                {
                    "rel": "http://nodeinfo.diaspora.software/ns/schema/2.1",
                    "href": f"https://{settings.SERVER_HOST}/nodeinfo/2.1",
                }
            ]
        }
    )


@router.get("/nodeinfo/2.1", response_model=schemas.NodeInfo, response_model_exclude_none=True)
def read_nodeinfo(*, db: Annotated[Session, Depends(deps.get_db)]) -> Any:
    """
    Get wellknown nodeinfo 2.1.
    """
    return crud.activity.get_wellknown_nodeinfo()


@router.get("/webfinger", response_model=schemas.WebFinger, response_model_exclude_none=True)
# @router.get("/webfinger")
def read_webfinger(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    resource: str = "",
) -> Any:
    """
    Get wellknown actor.
    """
    db_obj = crud.actor.get_by_resource(db=db, resource=resource)
    if not resource or not db_obj:
        raise HTTPException(
            status_code=400,
            detail="Well-known actor unknown.",
        )
    return crud.actor.get_wellknown_webfinger(db_obj=db_obj)
