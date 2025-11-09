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

from enum import Enum


class BaseEnum(str, Enum):
    # noinspection PyMethodParameters
    # cf https://gitter.im/tiangolo/fastapi?at=5d775f4050508949d30b6eec
    def _generate_next_value_(name, start, count, last_values) -> str:  # type: ignore
        """
        Uses the name as the automatic value, rather than an integer

        See https://docs.python.org/3/library/enum.html#using-automatic-values for reference
        """
        return name

    @classmethod
    def as_dict(cls):
        member_dict = {role: member.value for role, member in cls.__members__.items()}
        return member_dict

    @classmethod
    def _missing_(cls, value):
        # https://stackoverflow.com/a/68311691/295606
        for member in cls:
            if member.value.upper() == value.upper():
                return member
