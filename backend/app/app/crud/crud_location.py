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

from pathlib import Path
import IP2Location
import hashlib

from app.core.config import settings
from app.schemas.location import CountryCode  # , IPCode

# from app.schema_types.currency import CurrencyType
from app.crud.crud_source import source


class CRUDLocation:

    def __init__(self) -> None:
        self.default_directory = source.check_path(directory=Path.cwd() / settings.IP2_FOLDER)
        self.IP2_PATH = self.default_directory / settings.IP2_BIN_FILE
        self.IP2_DOWNLOAD_URI = str(settings.IP2_DOWNLOAD_URL) + settings.IP2_BIN_FILE + settings.IP2_DOWNLOAD_FILE_TYPE
        self.IP2_DOWNLOAD_HASH = (
            str(settings.IP2_DOWNLOAD_URL)
            + settings.IP2_BIN_FILE
            + settings.IP2_DOWNLOAD_FILE_TYPE
            + settings.IP2_DOWNLOAD_FILE_HASH
        )
        self.initialise_base()

    def initialise_base(self):
        try:
            self.IP2_BASE = IP2Location.IP2Location(self.IP2_PATH, "SHARED_MEMORY")
        except ValueError:
            self.IP2_BASE = None

    def get_md5(self, *, source: str) -> str:
        # https://stackoverflow.com/a/3431838
        source_md5 = hashlib.md5()
        with open(source, "rb") as f:
            while chunk := f.read(8192):
                source_md5.update(chunk)
        return source_md5.hexdigest()

    def get_IP2_database(self, initialise: bool = True) -> None:
        # DOWNLOAD THE LATEST - UPDATES ON THE 1ST OF EVERY MONTH ... DOWNLOAD WITHIN 7 DAYS
        local_zip = source.download_uri_source(source=self.IP2_DOWNLOAD_URI, directory=self.default_directory)
        hash_check = source.download_uri_source(source=location.IP2_DOWNLOAD_HASH, directory=location.default_directory)
        # DO A HASHCHECK
        if str.encode(source.get_md5(source=local_zip)) in open(hash_check, "rb").read():
            # CONFIRMED
            source.get_unzipped_source(source=local_zip, directory=self.default_directory, keep=self.IP2_PATH)
        source.delete_file(source=local_zip)
        source.delete_file(source=hash_check)
        if initialise:
            self.initialise_base()

    def get_country(self, request_ip: str) -> CountryCode:
        if self.IP2_BASE:
            return self.IP2_BASE.get_all(request_ip)


location = CRUDLocation()
