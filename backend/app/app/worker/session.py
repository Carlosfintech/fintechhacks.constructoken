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

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session

from app.core.config import settings


def get_scoped_session():
    # https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/68#issuecomment-537883784
    # Method of use:
    #     SessionScoped = get_scoped_session()
    #     db = SessionScoped()
    #     ...
    #     db.close()
    #     SessionScoped.remove()
    # Has to be *inside* the function calling it to ensure that it is an independent session.
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        pool_recycle=3600,  # this line might not be needed
        connect_args={
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
    )
    meta = MetaData()
    meta.reflect(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    SessionScoped = scoped_session(SessionLocal)
    # Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionScoped
