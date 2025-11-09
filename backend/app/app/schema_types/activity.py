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


class ActivityType(BaseEnum):
    Accept = auto()
    Add = auto()
    Announce = auto()
    Arrive = auto()
    Block = auto()
    Create = auto()
    Delete = auto()
    Dislike = auto()
    Flag = auto()
    Follow = auto()
    Ignore = auto()
    Invite = auto()
    Join = auto()
    Leave = auto()
    Like = auto()
    Listen = auto()
    Move = auto()
    Offer = auto()
    Question = auto()
    Reject = auto()
    Read = auto()
    Remove = auto()
    TentativeReject = auto()
    TentativeAccept = auto()
    Travel = auto()
    Undo = auto()
    Update = auto()
    View = auto()


class ObjectLinkType(BaseEnum):
    Article = auto()
    Audio = auto()
    Document = auto()
    Event = auto()
    Image = auto()
    Note = auto()
    Page = auto()
    Place = auto()
    Profile = auto()
    Relationship = auto()
    Tombstone = auto()
    Video = auto()
