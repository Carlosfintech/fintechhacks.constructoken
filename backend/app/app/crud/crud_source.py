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

from typing import Generator

import orjson
import base64
import sys
import hashlib
from urllib.parse import urlparse
import urllib
import posixpath
from ulid import ULID
from datetime import date, datetime, timezone, timedelta
import zipfile
from pathlib import Path
import locale
import warnings
import celery.bin.amqp
from fastapi import UploadFile
from io import BufferedReader
from collections.abc import Iterator
from botocore.response import StreamingBody
from fastapi import HTTPException

from app.core.config import settings
from app.core.celery_app import celery_app
from app.crud.crud_spaces import spaces

try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except locale.Error:
    # Readthedocs has a problem, but difficult to replicate
    locale.setlocale(locale.LC_ALL, "")


class SourceParser:
    """Core functions for file and path management, and general ad-hoc utilities."""

    def __init__(self) -> None:
        self.directory = self.check_path(directory=Path.cwd() / settings.DEFAULT_WORKING_DIRECTORY)
        self.root = self.check_path(directory=Path.cwd())
        self.use_spaces = settings.USE_SPACES

    ###################################################################################################
    # AD-HOC UTILITIES
    ###################################################################################################

    def get_now(self) -> str:
        return date.isoformat(datetime.now())

    def should_fetch(self, fetched: datetime) -> bool:
        if not fetched:
            return True
        return fetched <= datetime.now().astimezone(timezone.utc) - timedelta(days=settings.REFETCH_AFTER)

    def chunks(self, *, lst: list, n: int) -> Generator:
        """Yield successive n-sized chunks from l."""
        # https://stackoverflow.com/a/976918/295606
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    def show_warning(self, message: str) -> None:
        warnings.warn(message, UserWarning)

    ###################################################################################################
    # PATH MANAGEMENT
    ###################################################################################################

    def get_path(
        self,
        *,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
        check_source: bool = True,
        use_root: bool = False,
    ) -> Path:
        source = self.directory
        if use_root:
            source = self.root
        if folder_id:
            source = source / str(folder_id)
        source = source / str(source_id)
        if check_source and not self.check_source(source=source):
            raise FileNotFoundError(f"File at `{source}` not valid.")
        return source

    def check_path(self, *, directory: str) -> Path:
        if isinstance(directory, str):
            directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def check_source(self, *, source: str) -> bool:
        if isinstance(source, str):
            source = Path(source)
        return source.exists()

    def check_uri(self, *, source: str) -> bool:
        # https://stackoverflow.com/a/38020041
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc, result.path])
        except (ValueError, AttributeError):
            return False

    def check_path_or_uri(self, *, source: str) -> bool:
        if not isinstance(source, str):
            source = str(source)
        return any([Path(source).exists(), self.check_uri(source=source)])

    def rename_file(self, *, source: str, newname: str, add_suffix: bool = False) -> str:
        p = Path(source)
        if add_suffix:
            newname = f"{newname}.{p.suffix}"
        p.rename(Path(p.parent, newname))
        return newname

    def delete_file(self, *, source: Path | str):
        if isinstance(source, str):
            source = Path(source)
        try:
            assert sys.version_info >= (3, 8)
        except AssertionError:
            source.unlink()
        else:
            source.unlink(missing_ok=True)

    ###################################################################################################
    # DATA IMPORTERS
    ###################################################################################################

    def download_uri_source(
        self, source: str, directory: Path | str | None = None, filename: str | None = None
    ) -> Path:
        """Downloads a source at a remote uri, and returns a Path for that downloaded source.

        Parameters
        ----------
        source: str
            URI path to source.
        directory: Path | str | None

        Returns
        -------
        Path to local source.
        """
        if not filename:
            request = urllib.request.Request(source, method="HEAD")
            request = urllib.request.urlopen(request).info()
            filename = request.get_filename()
            if not filename:
                #  https://stackoverflow.com/a/11783319/295606
                source_path = urllib.request.urlsplit(source).path
                filename = posixpath.basename(source_path)
            if not filename:
                # Make something up ...
                filename = f"temporary-{ULID()}"
        if not directory:
            directory = self.directory
        local_source = Path(directory) / filename
        if not self.check_source(source=local_source):
            # https://stackoverflow.com/a/46511429
            # https://docs.python.org/3/library/urllib.request.html
            opener = urllib.request.build_opener()
            opener.addheaders = [("User-agent", "Mozilla/5.0")]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(source, local_source)
        return local_source

    ###################################################################################################
    # CHECKSUMS
    ###################################################################################################

    def get_checksum(self, *, source: Path | str) -> str:
        # https://stackoverflow.com/a/47800021
        if isinstance(source, Path):
            source = str(source)
        checksum = hashlib.blake2b()
        with open(source, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                checksum.update(chunk)
        return checksum.hexdigest()

    def get_md5(self, *, source: Path | str) -> str:
        # https://stackoverflow.com/a/59056796
        if isinstance(source, Path):
            source = str(source)
        with open(source, "rb") as f:
            source_md5 = hashlib.md5()
            while chunk := f.read(8192):
                source_md5.update(chunk)
        return source_md5.hexdigest()

    ###################################################################################################
    # ZIPPED SOURCE
    ###################################################################################################

    def get_unzipped_source(self, *, source: str, directory: Path, keep: Path | str | None = None) -> None:
        with zipfile.ZipFile(source, "r") as zip_ref:
            zip_ref.extractall(directory)
            if keep:
                # Delete everything else
                for f in zip_ref.namelist():
                    f = directory / f
                    if f != keep:
                        self.delete_file(source=f)

    ###################################################################################################
    # SOURCE HISTORY AND TASK IMPLEMENTATION
    ###################################################################################################

    def get_celery_active_tasks(self) -> list[str]:
        i = celery_app.control.inspect()
        active = [{k: v for k, v in row.items() if k in ["name"]} for row in [c for c in i.active().values()][0]]
        return [a["name"].split(".")[-1] for a in active]

    def purge_celery_queue(self, *, queue_name: str = "main-queue"):
        # Throw the boat at it and make sure nothing is running
        # https://stackoverflow.com/a/24463916/295606
        # Purge queue
        amqp = celery.bin.amqp.amqp(app=celery_app)
        amqp.run("queue.purge", queue_name)
        # Purge active
        # https://stackoverflow.com/a/9369466/295606
        inspect = celery_app.control.inspect()
        task_owner = next(iter(inspect.active()))
        rvk = [r["id"] for r in inspect.active()[task_owner]]
        inspect.app.control.revoke(rvk, terminate=True)
        # Purge reserved
        task_owner = next(iter(inspect.reserved()))
        rvk = [r["id"] for r in inspect.reserved()[task_owner]]
        inspect.app.control.revoke(rvk, terminate=True)
        celery_app.control.purge()

    ###################################################################################################
    # JSON & FILE LOAD & SAVE
    ###################################################################################################

    def load_json(
        self,
        *,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
    ) -> dict:
        """
        Load and return a JSON file, if it exists.

        Paramaters
        ----------
        source: the filename & path to open

        Raises
        ------
        JSONDecoderError if not a valid json file
        FileNotFoundError if not a valid source

        Returns
        -------
        dict
        """
        source = self.get_path(folder_id=folder_id, source_id=source_id)
        with open(source, "r") as f:
            response = f.read()
            try:
                return orjson.loads(response)
            except orjson.JSONDecodeError:
                return orjson.loads(base64.b64decode(response))
            # try:
            #     return orjson.loads(f)
            # except orjson.JSONDecodeError:
            #     e = f"File at `{source}` not valid json."
            #     raise orjson.JSONDecodeError(e)

    def save_json(
        self,
        *,
        data: dict,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
    ) -> bool:
        """
        Save a dictionary as a json file.

        Parameters
        ----------
        data: dictionary to be saved
        source: the filename to save, including path

        Returns
        -------
        bool, True if saved.
        """
        data = orjson.dumps(data, default=str, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
        return self.save_file(data=data, folder_id=folder_id, source_id=source_id)

    def save_file(
        self,
        *,
        data: str | bytes,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
    ) -> bool:
        """Save json to file.

        Parameters
        ----------
        data: dictionary to be saved
        source: the filename to save, including path

        Returns
        -------
        bool, True if saved.
        """
        write_as = "w"
        if isinstance(data, bytes):
            write_as = "wb"
        source = self.get_path(folder_id=folder_id, source_id=source_id, check_source=False)
        with open(source, write_as) as f:
            f.write(data)
        return True

    def save_media_file(
        self,
        *,
        data: str | bytes,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
    ) -> bool:
        """Save json to file.


        Parameters
        ----------
        data: dictionary to be saved
        source: the filename to save, including path

        Returns
        -------
        bool, True if saved.
        """
        try:
            media = data.file.read()
            write_as = "w"
            if isinstance(media, bytes):
                write_as = "wb"
            source = self.get_path(folder_id=folder_id, source_id=source_id, check_source=False, use_root=True)
            self.check_path(directory=source.parent)
            with open(str(source), write_as) as f:
                f.write(media)
        except Exception:
            raise HTTPException(status_code=500, detail="Media upload failed.")
        finally:
            data.file.close()
        return True

    ###################################################################################################
    # SOURCE MANAGEMENT
    ###################################################################################################

    def get_local_source_path(self, *, folder_id: ULID | str | None = None) -> Path:
        source_path = self.directory
        if folder_id:
            source_path = self.check_path(directory=self.directory / folder_id)
        return source_path

    def exists(
        self,
        *,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
    ) -> StreamingBody | Iterator[BufferedReader]:
        if self.use_spaces:
            return spaces.exists(folder_id=folder_id, filename=source_id)
        source_path = self.get_local_source_path(folder_id=folder_id)
        return self.check_source(source=source_path / source_id)

    def get_data_stream(
        self,
        *,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
    ) -> StreamingBody | Iterator[BufferedReader]:
        if self.use_spaces:
            if spaces.exists(folder_id=folder_id, filename=source_id):
                return spaces.get_stream(folder_id=folder_id, filename=source_id)
        source_path = self.get_local_source_path(folder_id=folder_id)
        if self.check_source(source=source_path / source_id):
            with open(source_path / source_id, mode="rb") as stream:
                while chunk := stream.read(settings.CHUNK_SIZE):
                    yield chunk

    def get_local_path(
        self,
        *,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
    ) -> Path | None:
        source_path = self.get_local_source_path(folder_id=folder_id)
        if self.check_source(source=source_path / source_id):
            return source_path / source_id
        if self.use_spaces:
            if spaces.exists(folder_id=folder_id, filename=source_id):
                spaces.download_file(folder_id=folder_id, filename=source_id, source_path=source_path / source_id)
                return source_path / source_id
        return None

    def get(
        self, *, folder_id: ULID | str | None = None, source_id: ULID | str, null_response: dict = {}
    ) -> Path | None:
        """
        Only useful for JSON files.
        """
        data = {}
        if self.use_spaces:
            if spaces.exists(folder_id=folder_id, filename=source_id):
                data = spaces.get(folder_id=folder_id, filename=source_id)
        if not data:
            source_path = self.get_local_source_path(folder_id=folder_id)
            if self.check_source(source=source_path / source_id):
                data = self.load_json(folder_id=folder_id, source_id=source_id)
        if data:
            return data
        return null_response

    def update(
        self,
        *,
        source: UploadFile | bytes | dict,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
        local_only: bool = False,
    ):
        # Functions for both create and update for an imported / uploaded file
        # https://stackoverflow.com/questions/63048825/how-to-upload-file-using-fastapi/70657621#70657621
        source_path = self.get_local_source_path(folder_id=folder_id)
        try:
            with open(source_path / source_id, "wb") as f:
                if isinstance(source, UploadFile):
                    while contents := source.file.read():
                        f.write(contents)
                if isinstance(source, dict):
                    source = base64.b64encode(orjson.dumps(source))
                if isinstance(source, bytes):
                    f.write(source)
        except Exception as e:
            raise ValueError(e)
        finally:
            if isinstance(source, UploadFile):
                source.file.close()
        if self.use_spaces:
            spaces.upload_file(folder_id=folder_id, filename=source_id, source_path=source_path / source_id)
        if local_only:
            # Potentially remove local version
            self.remove(folder_id=folder_id, source_id=source_id, local_only=True)

    def remove(self, *, folder_id: ULID | str | None = None, source_id: ULID | str, local_only: bool = False):
        source_path = self.get_local_source_path(folder_id=folder_id) / source_id
        if self.check_source(source=source_path):
            try:
                assert sys.version_info >= (3, 8)
            except AssertionError:
                source_path.unlink()
            else:
                source_path.unlink(missing_ok=True)
        if self.use_spaces and not local_only:
            if spaces.exists(folder_id=folder_id, filename=source_id):
                spaces.remove(folder_id=folder_id, filename=source_id, source_path=source_path)
        return source_path

    def upload(
        self,
        *,
        folder_id: ULID | str | None = None,
        source_id: ULID | str,
        source: bytes | dict = None,
        local_only: bool = False,
    ):
        source_path = self.get_local_source_path(folder_id=folder_id)
        if self.use_spaces:
            if not self.check_source(source=source_path / source_id):
                if not source:
                    raise ValueError("No source data available.")
                local_only = True
                if isinstance(source, dict):
                    source = base64.b64encode(orjson.dumps(source))
                with open(source_path / source_id, "wb") as w:
                    w.write(source)
            spaces.upload_file(folder_id=folder_id, filename=source_id, source_path=source_path / source_id)
            # Potentially remove local version
            if local_only:
                self.remove(folder_id=folder_id, source_id=source_id, local_only=local_only)


source = SourceParser()
