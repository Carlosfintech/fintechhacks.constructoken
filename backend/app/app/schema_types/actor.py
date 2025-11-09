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

from enum import auto

from app.schema_types.base import BaseEnum


class ActorType(BaseEnum):
    Application = auto()
    Group = auto()
    Organization = auto()
    Person = auto()
    Service = auto()
    Tombstone = auto()  # Special case for closed account

    @classmethod
    def _missing_(cls, value):
        # https://stackoverflow.com/a/68311691/295606
        for member in cls:
            if member.value.upper() == value.upper():
                return member
            # SPECIAL CASES
            if member.value.upper() == "PERSON" and value.upper() == "CREATOR":
                return member
            if member.value.upper() == "SERVICE" and value.upper() == "WORK":
                return member
            if member.value.upper() == "ORGANIZATION" and value.upper() == "ORGANISATION":
                return member

    @property
    def as_uri(self):
        terms = {
            "Person": "creator",
            "Service": "work",
        }
        return terms.get(self.value, self.value.lower())
