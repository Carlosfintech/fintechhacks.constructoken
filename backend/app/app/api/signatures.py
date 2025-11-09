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

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from bovine.crypto.http_signature import HttpSignature
from bovine.crypto.signature import Signature
from bovine.crypto.types import CryptographicIdentifier
from functools import wraps
import json
import orjson

from app import crud, models, schemas, schema_types
from app.api import deps
from app.core.config import settings
from app.core import security


"""
# HTTP Message Signatures

Given the federated nature of ActivityPub servers, it is critical that any requests received are from who they say they are.

Enter [HTTP Message Signatures](https://datatracker.ietf.org/doc/html/rfc9421). What follows leans heavily on schemes
developed by:

    - [Mastodon](https://docs.joinmastodon.org/spec/security/), which has great documentation
    - Bovine's [Cattle Grid](https://bovine.codeberg.page/cattle_grid/) and its further implementation in
    [Bovine Herd](https://bovine-herd.readthedocs.io/en/latest/deployment/.)
    - [Takahē](https://github.com/jointakahe/takahe)

Because of the nature of the process, it's difficult to use anything off-the-shelf. A combination of web proxying,
database and web framework stack all make things somewhat fiddly.

The process is structured as followed:

1. Verify HTTP Signatures:
    - A wrapper around `APIRouter` requests
    - Tests the HTTP Signature
    - Checks if the requester is on the main server blocklist.
2. Inbox POST validation:
    - A similar check, but for the actor activity ... this requires the targetted actor to respond to the requesting
    actor, and - for their safety - this requires the other checks happen in advance.
    - An additional check as to whether the actor has blocked the requester.

Mastodon describes the special use-case for Linked Data signatures for actor deletion notices, since the actor is no
longer reachable (i.e. no public key).
"""


def verify_request_signature(endpoint):
    # https://stackoverflow.com/a/72312122/295606
    @wraps(endpoint)
    async def wrapper(*, db: Session, request: Request, **kwargs):
        if not request.headers.get("signature"):
            raise HTTPException(status_code=401, detail="Invalid client secret")
        http_signature = HttpSignature()
        parsed_signature = Signature.from_signature_header(request.headers["signature"])
        signature_fields = parsed_signature.fields
        for field in signature_fields:
            if field == "keyId":
                print(request.headers[field])
            if field == "(request-target)":
                method = request.method.lower()
                path = request.url
                http_signature.with_field(field, f"{method} {path}")
            elif field == "host":
                http_signature.with_field(field, request.headers["x-forwarded-host"])
            else:
                http_signature.with_field(field, request.headers[field])
        # print(http_signature)
        print("-------------------------------------------------")
        # kwargs["db"] = db
        # kwargs["request"] = request
        # https://stackoverflow.com/a/42769789/295606
        return await endpoint(db=db, request=request, **kwargs)

    return wrapper
