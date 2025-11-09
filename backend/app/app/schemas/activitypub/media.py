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

from typing import Optional
from ulid import ULID
from pydantic import (
    ConfigDict,
    Field,
    HttpUrl,
)
from datetime import datetime

from app.schemas.base_schema import BaseSchema, LocaleType
from app.schema_types import MediaType


class MediaAttachmentBase(BaseSchema):
    created: Optional[datetime] = Field(None, description="Automatically generated date was first created.")
    URL: Optional[HttpUrl] = Field(
        None,
        description="Where can the attachment be retrieved on *this* server.",
    )
    remoteURL: Optional[HttpUrl] = Field(
        None,
        description="Where can the attachment be retrieved on a remote server (empty for local media).",
    )
    type: Optional[MediaType] = Field(None, description="Type of file (image/gifv/audio/video/unknown)")
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the language used by the actor. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    text: Optional[str] = Field(None, description="Language-defined description for the media attachment.")
    path: Optional[str] = Field(None, description="Local path in the working directory or remote drive.")
    content_type: Optional[str] = Field(None, description="Mime type, if known.")
    file_size: Optional[int] = Field(None, description="File size, if known.")
    thumbnail: bool = Field(
        default=False, description="Small image thumbnail derived from a larger image, video, or audio file."
    )
    actor_avatar_id: Optional[ULID] = Field(None, description="Actor id which which this media is an avatar.")
    as_avatar: bool = Field(default=False, description="Is this attachment being used as an avatar?")
    actor_standout_id: Optional[ULID] = Field(None, description="Actor id which which this media is a standout.")
    as_standout: bool = Field(default=False, description="Is this attachment being used as a standout?")
    model_config = ConfigDict(from_attributes=True)


class MediaAttachmentCreate(MediaAttachmentBase):
    pass


class MediaAttachmentUpdate(MediaAttachmentCreate):
    id: ULID = Field(..., description="Automatically generated unique identity.")


class MediaAttachment(MediaAttachmentUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
