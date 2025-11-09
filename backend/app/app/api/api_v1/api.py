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

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    oauth,
    creators,
    actor,
    proxy,
    wellknown,
    root,
    instance,
    openpayments,
    generate,
    merchant,
    payments,
)

api_router = APIRouter()
api_router.include_router(creators.router, prefix="/creators", tags=["creators"])
api_router.include_router(actor.router, prefix="/actor", tags=["actor"])
api_router.include_router(instance.router, prefix="/instance", tags=["instance"])
api_router.include_router(openpayments.router, prefix="/openpayments", tags=["openpayments"])
api_router.include_router(merchant.router, prefix="/merchant", tags=["merchant"])
api_router.include_router(proxy.router, prefix="/proxy", tags=["proxy"])
api_router.include_router(generate.router, prefix="/generate", tags=["generate"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])

root_router = APIRouter()
root_router.include_router(oauth.router, prefix="/auth", tags=["oauth"])
root_router.include_router(wellknown.router, prefix="/.well-known", tags=["wellknown"])
root_router.include_router(root.router, tags=["root"])
