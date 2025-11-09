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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from babel import Locale

from app.core.config import settings
from app import crud, schemas
from app.api import deps

router = APIRouter(lifespan=deps.get_lifespan)


@router.get("/webhook/{key}", status_code=status.HTTP_202_ACCEPTED)
def get_merchant_response(*, key: str, hash: str, interact_ref: str) -> Any:
    """
    Get the list of instance rules in a selected language.
    """
    print("-------------------------------------------------------------------")
    print("key", key)
    print("hash", hash)
    print("interact_ref", interact_ref)
    print("-------------------------------------------------------------------")
