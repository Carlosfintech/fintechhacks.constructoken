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

import sentry_sdk
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path

from app.api.api_v1.api import api_router, root_router
from app.core.config import settings

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS and settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# TODO: Static media are served locally from a server directory. This could be moved to a CDN or S3 object store.
# Ensure the media directory exists
if isinstance(settings.API_MEDIA_STR, str):
    media_directory = Path(settings.API_MEDIA_STR)
media_directory.mkdir(parents=True, exist_ok=True)
app.mount(f"/{settings.API_MEDIA_STR}", StaticFiles(directory=str(media_directory)), name=settings.API_MEDIA_STR)

# Include the routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router, prefix="")
# app.include_router(root_router, prefix=settings.API_ROOT_STR)
