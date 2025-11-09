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

from sqlalchemy.orm import Session
from fastapi.security import SecurityScopes

from app.crud.base import CRUDBase
from app.models import Creator, Token, Actor
from app.schemas import TokenCreate, TokenUpdate, TokenData
from app.core.config import settings
from app.core.security import create_refresh_token, create_access_token


class CRUDToken(CRUDBase[Token, TokenCreate, TokenUpdate]):
    # Everything is creator-dependent
    def create(
        self, db: Session, *, obj_in: str, creator_obj: Creator, scopes: SecurityScopes = SecurityScopes([])
    ) -> Token:
        db_obj = db.query(self.model).filter(self.model.token == obj_in).first()
        if db_obj and db_obj.authenticates != creator_obj:
            raise ValueError("Token mismatch between key and creator.")
        obj_in = TokenCreate(**{"token": obj_in, "authenticates_id": creator_obj.id, "scopes": scopes})
        return super().create(db=db, obj_in=obj_in)

    def create_token_response(
        self,
        db: Session,
        *,
        creator: Creator,
        actor: Actor | None = None,
        force_totp: bool = False,
        scopes: str = "",
        token_type: str = "bearer",
        refresh_token: str | None = None,
    ) -> TokenData:
        """
        Authentication process:
            - Login or account recovery (i.e. no ACCESS token presented) requires challenge/response (password, or magic link / email)
            - If successful, check if creator requires TOTP ... if so `force_totp` is `True`
            - Only once successfully passed challenges - both response & TOTP - issue REFRESH token

        Caveats:
            - If a REFRESH token is unlimited (i.e. does not expire), don't issue a new one
            - Otherwise, when a REFRESH token is used, invalidate it and issue a new one
        """
        subject = str(creator.id)
        if force_totp and not creator.totp_secret:
            force_totp = False
        if settings.REFRESH_TOKEN_EXPIRE_SECONDS and refresh_token:
            # revoke the REFRESH token
            token_obj = self.get_by_creator(token=token, creator=creator)
            self.remove(db, db_obj=token_obj)
            refresh_token = None
        if not force_totp and not refresh_token:
            # No TOTP, so this concludes the login validation
            refresh_token = create_refresh_token(subject=subject, actor=actor)
            self.create(db=db, obj_in=refresh_token, creator_obj=creator, scopes=scopes)
        if refresh_token and isinstance(refresh_token, Token):
            refresh_token = refresh_token.token
        return {
            "access_token": create_access_token(
                subject=subject, actor=actor, force_totp=force_totp, security_scopes=scopes
            ),
            "refresh_token": refresh_token,
            "scopes": scopes,
            "token_type": token_type,
        }

    def get(self, db: Session, token: str) -> Token:
        return db.query(self.model).filter(self.model.token == token).first()

    def get_by_creator(self, *, creator: Creator, token: str) -> Token:
        return creator.tokens.filter(self.model.token == token).first()

    def get_multi(self, *, creator: Creator, page: int = 0, page_break: bool = False) -> list[Token]:
        db_objs = creator.tokens
        if not page_break:
            if page > 0:
                db_objs = db_objs.offset(page * settings.MULTI_MAX)
            db_objs = db_objs.limit(settings.MULTI_MAX)
        return db_objs.all()

    def remove(self, db: Session, *, db_obj: Token) -> None:
        db.delete(db_obj)
        db.commit()
        return None

    def validate_scopes(self, scopes: str | list[str] | SecurityScopes):
        if isinstance(scopes, SecurityScopes):
            return scopes.scopes
        if isinstance(scopes, str):
            return [s.strip() for s in scopes.replace(" ", ",").split(",") if s]
        return [s.strip() for s in scopes if s]


token = CRUDToken(model=Token)
