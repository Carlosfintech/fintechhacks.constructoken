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

from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.db.base_class import Base

if TYPE_CHECKING:
    from .creator import Creator  # noqa: F401


class Token(Base):
    token: Mapped[str] = mapped_column(primary_key=True, index=True)
    scopes: Mapped[Optional[str]] = mapped_column(nullable=True)
    authenticates_id: Mapped[str] = mapped_column(ForeignKey("creator.id"))
    authenticates: Mapped["Creator"] = relationship(back_populates="tokens")
