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

from typing import Annotated, Any, Union

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.utilities import (
    send_reset_password_email,
    send_magic_login_email,
)

router = APIRouter(lifespan=deps.get_lifespan)

"""
https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Authentication_Cheat_Sheet.md
Specifies minimum criteria:
    - Change password must require current password verification to ensure that it's the legitimate creator.
    - Login page and all subsequent authenticated pages must be exclusively accessed over TLS or other strong transport.
    - An application should respond with a generic error message regardless of whether:
        - The creator ID or password was incorrect.
        - The account does not exist.
        - The account is locked or disabled.
    - Code should go through the same process, no matter what, allowing the application to return in approximately
      the same response time.
    - In the words of George Orwell, break these rules sooner than do something truly barbaric.

See `core/security.py` for other requirements.
"""


@router.post("/magic/{email}", response_model=schemas.WebToken)
@router.post("/magic/{email}/{name}", response_model=schemas.WebToken)
def login_with_magic_link(*, db: Annotated[Session, Depends(deps.get_db)], email: str, name: str | None = None) -> Any:
    """
    First step of a 'magic link' login. Check if the creator exists and generate a magic link. Generates two short-duration
    jwt tokens, one for validation, one for email. Raises exception if creator does not exist.
    """
    creator = crud.creator.get_by_email(db, email=email)
    if not creator and not name:
        raise HTTPException(status_code=400, detail="Login failed; account does not exist.")
    if not creator and name:
        db_response = crud.actor.check_persona_name(db=db, name=name)
        if db_response:
            raise HTTPException(status_code=400, detail="Login failed; name unavailable.")
        creator_in = schemas.CreatorCreate(
            **{"email": email, "accepted_rules": True, "language": settings.SERVER_LANGUAGE}
        )
        creator = crud.creator.create(db, obj_in=creator_in)
        obj_in = schemas.ActorCreate(
            **dict(
                creator_id=creator.id,
                preferredUsername=name,
                discoverable=True,
            )
        )
        crud.actor.create(db=db, obj_in=obj_in)
    if not crud.creator.is_active(creator):
        raise HTTPException(status_code=400, detail="A link to activate your account has been emailed.")
    tokens = security.create_magic_tokens(subject=creator.id)
    if settings.emails_enabled and creator.email:
        # Send email with creator.email as subject
        send_magic_login_email(email_to=creator.email, token=tokens[0])
    return {"claim": tokens[1]}


@router.post("/claim", response_model=schemas.TokenData)
def validate_magic_link(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    obj_in: schemas.WebToken,
    magic_in: Annotated[bool, Depends(deps.get_magic_token)],
) -> Any:
    """
    Second step of a 'magic link' login.
    """
    claim_in = deps.get_magic_token(token=obj_in.claim)
    # Get the creator
    creator = crud.creator.get(db, id=magic_in.sub)
    # Test the claims
    if (
        (claim_in.sub == magic_in.sub)
        or (claim_in.fingerprint != magic_in.fingerprint)
        or not creator
        or not crud.creator.is_active(creator)
    ):
        raise HTTPException(status_code=400, detail="Login failed; invalid claim.")
    # Validate that the email is the creator's
    if not creator.email_validated:
        crud.creator.validate_email(db=db, db_obj=creator)
    # Initial claim, no REFRESH and force check for TOTP
    refresh_token = None
    force_totp = True
    return crud.token.create_token_response(
        db=db,
        creator=creator,
        force_totp=force_totp,
        scopes=["read", "write", "admin"],
        token_type="bearer",
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=schemas.TokenData)
def login_with_oauth2(
    db: Annotated[Session, Depends(deps.get_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    """
    First step with OAuth2 compatible token login, get an access token for future requests.
    """
    creator = crud.creator.authenticate(db, email=form_data.username, password=form_data.password)
    if not form_data.password or not creator or not crud.creator.is_active(creator):
        raise HTTPException(status_code=400, detail="Login failed; incorrect email or password")
    # Initial claim, no REFRESH and force check for TOTP
    refresh_token = None
    force_totp = True
    return crud.token.create_token_response(
        db=db,
        creator=creator,
        force_totp=force_totp,
        scopes=["read", "write", "admin"],
        token_type="bearer",
        refresh_token=refresh_token,
    )


@router.post("/totp", response_model=schemas.TokenData)
def login_with_totp(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    totp_data: schemas.WebToken,
    creator: Annotated[models.Creator, Depends(deps.get_totp_creator)],
) -> Any:
    """
    Final validation step, using TOTP.
    """
    new_counter = security.verify_totp(
        token=totp_data.claim, secret=creator.totp_secret, last_counter=creator.totp_counter
    )
    if not new_counter:
        raise HTTPException(status_code=400, detail="Login failed; unable to verify TOTP.")
    # Save the new counter to prevent reuse
    creator = crud.creator.update_totp_counter(db=db, db_obj=creator, new_counter=new_counter)
    # Initial claim, no REFRESH and passed TOTP
    refresh_token = None
    force_totp = False
    return crud.token.create_token_response(
        db=db,
        creator=creator,
        force_totp=force_totp,
        scopes=["read", "write", "admin"],
        token_type="bearer",
        refresh_token=refresh_token,
    )


@router.put("/totp", response_model=schemas.Msg)
def enable_totp_authentication(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    data_in: schemas.EnableTOTP,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    For validation of token before enabling TOTP.
    """
    if creator.hashed_password:
        creator = crud.creator.authenticate(db, email=creator.email, password=data_in.password)
        if not data_in.password or not creator:
            raise HTTPException(status_code=400, detail="Unable to authenticate or activate TOTP.")
    totp_in = security.create_new_totp(label=creator.email, uri=data_in.uri)
    print("-------------------------------------------------------------------------")
    print("claim", data_in.claim)
    print("token", security.totp_factory.from_source(data_in.uri).generate())
    print("-------------------------------------------------------------------------")
    new_counter = security.verify_totp(token=data_in.claim, secret=totp_in.secret, last_counter=creator.totp_counter)
    if not new_counter:
        raise HTTPException(status_code=400, detail="Unable to authenticate or activate TOTP.")
    # Enable TOTP and save the new counter to prevent reuse
    creator = crud.creator.activate_totp(db=db, db_obj=creator, totp_in=totp_in)
    creator = crud.creator.update_totp_counter(db=db, db_obj=creator, new_counter=new_counter)
    return {"msg": "TOTP enabled. Do not lose your recovery code."}


@router.delete("/totp", response_model=schemas.Msg)
def disable_totp_authentication(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    data_in: schemas.CreatorUpdate,
    creator: Annotated[models.Creator, Depends(deps.get_active_creator)],
) -> Any:
    """
    Disable TOTP.
    """
    if creator.hashed_password:
        creator = crud.creator.authenticate(db, email=creator.email, password=data_in.original)
        if not data_in.original or not creator:
            raise HTTPException(status_code=400, detail="Unable to authenticate or deactivate TOTP.")
    crud.creator.deactivate_totp(db=db, db_obj=creator)
    return {"msg": "TOTP disabled."}


@router.post("/refresh", response_model=schemas.TokenData)
def refresh_token(
    db: Annotated[Session, Depends(deps.get_db)],
    token_obj: Annotated[models.Token, Depends(deps.get_refresh_token)],
) -> Any:
    """
    Present a refresh token to request a new access token.
    """
    return crud.token.create_token_response(
        db=db,
        creator=token_obj.authenticates,
        force_totp=False,
        scopes=token_obj.scopes,
        token_type="bearer",
        refresh_token=token_obj,
    )


@router.post("/revoke", response_model=schemas.Msg)
def revoke_token(
    db: Annotated[Session, Depends(deps.get_db)],
    token_obj: Annotated[models.Token, Depends(deps.get_refresh_token)],
) -> Any:
    """
    Revoke a refresh token
    """
    crud.token.remove(db, db_obj=token_obj)
    return {"msg": "Token revoked"}


@router.post("/recover/{email}", response_model=Union[schemas.WebToken, schemas.Msg])
def recover_password(email: str, db: Annotated[Session, Depends(deps.get_db)]) -> Any:
    """
    Password Recovery
    """
    creator = crud.creator.get_by_email(db, email=email)
    if creator and crud.creator.is_active(creator):
        tokens = security.create_magic_tokens(subject=creator.id)
        if settings.emails_enabled:
            send_reset_password_email(email_to=creator.email, email=email, token=tokens[0])
            return {"claim": tokens[1]}
    return {"msg": "If that login exists, we'll send you an email to reset your password."}


@router.post("/reset", response_model=schemas.Msg)
def reset_password(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    new_password: str = Body(...),
    claim: str = Body(...),
    magic_in: Annotated[bool, Depends(deps.get_magic_token)],
) -> Any:
    """
    Reset password
    """
    claim_in = deps.get_magic_token(token=claim)
    # Get the creator
    creator = crud.creator.get(db, id=magic_in.sub)
    # Test the claims
    if (
        (claim_in.sub == magic_in.sub)
        or (claim_in.fingerprint != magic_in.fingerprint)
        or not creator
        or not crud.creator.is_active(creator)
    ):
        raise HTTPException(status_code=400, detail="Password update failed; invalid claim.")
    # Update the password
    hashed_password = security.get_password_hash(new_password)
    creator.hashed_password = hashed_password
    db.add(creator)
    db.commit()
    return {"msg": "Password updated successfully."}
