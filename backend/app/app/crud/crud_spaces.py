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

import logging
import boto3
from botocore.response import StreamingBody
from botocore.exceptions import ClientError
from ulid import ULID
import base64
import orjson
from typing import BinaryIO

from app.core.config import settings


# https://tenacity.readthedocs.io/en/latest/
from tenacity import after_log, retry, stop_after_attempt, wait_fixed  # noqa: F401
import warnings

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 10 * 1  # 10 seconds
wait_seconds = 1
return_value_on_error = {}


class CRUDSpaces:
    def __init__(self):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD) DigitalOcean Spaces.

        # https://docs.digitalocean.com/products/spaces/resources/s3-sdk-examples/
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#object
        """
        self.space = None
        self.bucket = None
        if settings.USE_SPACES:
            self.space = boto3.resource(
                "s3",
                region_name=settings.SPACES_REGION_NAME,
                endpoint_url=str(settings.SPACES_ENDPOINT_URL),
                aws_access_key_id=settings.SPACES_ACCESS_KEY,
                aws_secret_access_key=settings.SPACES_SECRET_KEY,
            )
            self.bucket = self.space.Bucket(settings.SPACES_BUCKET)

    def get_key(self, *, folder_id: ULID | str | None = None, filename: str) -> str:
        key = f"{filename}"
        if folder_id:
            key = f"{folder_id}/{key}"
        if settings.SPACES_VOLUME_ID:
            key = f"{settings.SPACES_VOLUME_ID}/{key}"
        return key

    def exists(self, *, folder_id: ULID | str | None = None, filename: str) -> bool:
        key = self.get_key(folder_id=folder_id, filename=filename)
        obj = self.bucket.Object(key)
        try:
            obj.load()
            return True
        except ClientError:
            return False

    @retry(
        stop=stop_after_attempt(max_tries),
        wait=wait_fixed(wait_seconds),
        after=after_log(logger, logging.WARN),
        retry_error_callback=lambda retry_state: return_value_on_error,
    )
    def get(self, *, folder_id: ULID | str | None = None, filename: str) -> BinaryIO:
        # https://stackoverflow.com/a/35376156/295606
        key = self.get_key(folder_id=folder_id, filename=filename)
        obj = self.bucket.Object(key)
        source = obj.get()["Body"].read().decode("utf-8")
        # Convert base64 to binary to json
        return orjson.loads(base64.b64decode(source))

    def get_stream(self, *, folder_id: ULID | str | None = None, filename: str) -> StreamingBody:
        # https://stackoverflow.com/questions/69617252/response-file-stream-from-s3-fastapi
        key = self.get_key(folder_id=folder_id, filename=filename)
        try:
            obj = self.bucket.Object(key)
            return obj.get()["Body"].iter_chunks()
        except Exception as e:
            print("-----------------------------------------------------------")
            print(f"ERROR: Spaces Stream     -     {filename}")
            print("-----------------------------------------------------------")
            raise e

    def upload_file(self, *, folder_id: ULID | str | None = None, filename: str, source_path: str) -> None:
        key = self.get_key(folder_id=folder_id, filename=filename)
        self.bucket.upload_file(Filename=source_path, Key=key)

    def download_file(self, *, folder_id: ULID | str | None = None, filename: str, source_path: str) -> None:
        key = self.get_key(folder_id=folder_id, filename=filename)
        self.bucket.download_file(Filename=source_path, Key=key)

    def create(self, *, folder_id: ULID | str | None = None, filename: str, source: str) -> int:
        key = self.get_key(folder_id=folder_id, filename=filename)
        obj = self.bucket.Object(key)
        obj.put(Body=source)

    @retry(
        stop=stop_after_attempt(max_tries),
        wait=wait_fixed(wait_seconds),
        after=after_log(logger, logging.WARN),
    )
    def update(self, *, folder_id: ULID | str | None = None, filename: str, source: str) -> int:
        try:
            self.create(folder_id=folder_id, filename=filename, source=source)
        except Exception as e:
            logger.error(e)
            raise e

    def rename(self, *, folder_id: ULID | str | None = None, oldname: str, newname: str) -> None:
        old_key = self.get_key(folder_id=folder_id, filename=oldname)
        new_key = self.get_key(folder_id=folder_id, filename=newname)
        old_obj = {"Bucket": settings.SPACES_BUCKET, "Key": old_key}
        self.bucket.copy(old_obj, new_key)
        self.bucket.Object(old_key).delete()

    def remove(self, *, folder_id: ULID | str | None = None, filename: str) -> int:
        key = self.get_key(folder_id=folder_id, filename=filename)
        obj = self.bucket.Object(key)
        obj.delete()


spaces = CRUDSpaces()
