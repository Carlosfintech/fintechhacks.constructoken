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
from pydantic import AnyHttpUrl
from fastapi import APIRouter, Depends, HTTPException, Request, Response
import httpx

from app import models
from app.api import deps


router = APIRouter(lifespan=deps.get_lifespan)

"""
A proxy for the frontend client when hitting cors issues with axios requests. Adjust as required. This version has
a creator-login dependency to reduce the risk of leaking the server as a random proxy.
"""


@router.post("/{path:path}")
async def proxy_post_request(
    *,
    path: AnyHttpUrl,
    request: Request,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    # https://www.starlette.io/requests/
    # https://www.python-httpx.org/quickstart/
    # https://github.com/tiangolo/fastapi/issues/1788#issuecomment-698698884
    # https://fastapi.tiangolo.com/tutorial/path-params/#__code_13
    try:
        data = await request.json()
        headers = {
            "Content-Type": request.headers.get("Content-Type"),
            "Authorization": request.headers.get("Authorization"),
        }
        async with httpx.AsyncClient() as client:
            proxy = await client.post(f"{path}", headers=headers, data=data)
        response = Response(content=proxy.content, status_code=proxy.status_code)
        return response
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{path:path}")
async def proxy_get_request(
    *,
    path: AnyHttpUrl,
    request: Request,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    try:
        headers = {
            "Content-Type": request.headers.get("Content-Type", "application/x-www-form-urlencoded"),
            "Authorization": request.headers.get("Authorization"),
        }
        async with httpx.AsyncClient() as client:
            proxy = await client.get(f"{path}", headers=headers)
        response = Response(content=proxy.content, status_code=proxy.status_code)
        return response
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
