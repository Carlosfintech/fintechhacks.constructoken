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

from typing import Any
from fastapi import Request, Response, HTTPException
from sqlalchemy.orm import Session

import orjson
from functools import wraps

from bovine.crypto import build_validate_http_signature_raw
from bovine.activitystreams.utils import actor_for_object
from bovine import BovineActor
from bovine.crypto.types import CryptographicIdentifier

from app.crud.activitypub.crud_actor import actor as crud_actor
from .regexes import regex
from app.core.config import settings

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


class ActivityResponse(Response):
    # https://fastapi.tiangolo.com/advanced/custom-response/#custom-response-class
    media_type = "application/activity+json"

    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed"
        return orjson.dumps(content)


def fetch_public_key(actor: BovineActor) -> CryptographicIdentifier:
    """
    Validate_signature takes `(method, url, headers, body)` as parameters and returns the owner if the http signature is valid.
    https://codeberg.org/bovine/bovine/src/commit/91ec9a0b77863c164c0598227e6e14b3d4cc005f/bovine/bovine/crypto/__init__.py#L105

    Use as:

        actor_fetch = fetch_public_key(actor)
        assert await bovine.crypto.build_validate_http_signature_raw(actor_fetch)(
            "post", str(request.url), request.headers, request.body)
        )
    """

    async def fetch_with_url(key_url: str):
        data = await actor.get(key_url, fail_silently=True)
        if data:
            return CryptographicIdentifier.from_public_key(data.get("publicKey", data))

    return fetch_with_url


def verify_request_signature(endpoint):
    # https://stackoverflow.com/a/72312122/295606
    # https://stackoverflow.com/a/42769789/295606
    # WAS: https://codeberg.org/bovine/cattle_grid/src/commit/336feea0079ba559a1482d956ee0cc4b81a612d1/cattle_grid/signature.py
    # NOW: https://codeberg.org/bovine/bovine/src/branch/main/bovine/bovine/crypto/signature.py
    @wraps(endpoint)
    async def wrapper(*, db: Session, request: Request, **kwargs):
        # Returns an error message, or the original data
        # 1. Reject large requests
        body = await request.json()
        if len(body) > settings.JSONLD_MAX_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Payload data too large.",
            )
        # 2. Check if requesting actor or domain are blocked
        #    requesting actor from `body.get("actor")`
        request_actor = actor_for_object(body)
        if not request_actor:
            raise HTTPException(
                status_code=400,
                detail="Unspecified actor.",
            )
        # 3. Check whether the targeted actor exists
        target_url = regex.actor_url(str(request.url).replace("http:", "https:"))
        if not target_url:
            raise HTTPException(
                status_code=400,
                detail="Unspecified actor.",
            )
        target_actor = crud_actor.get_by_uri(db=db, URI=target_url)
        if not target_actor:
            raise HTTPException(
                status_code=400,
                detail="Unspecified actor.",
            )
        service_actor = crud_actor.get_site_actor(db=db)
        await service_actor.init()
        # 4. Validate the poster http signature
        verify = build_validate_http_signature_raw(fetch_public_key(service_actor))
        try:
            claimed_actor = await verify(request.method, str(request.url), request.headers, request.body)
            print("CLAIMED: ", claimed_actor)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="HTTP Signature validation failed.",
            )
        await service_actor.session.close()
        # 5. Check if the actor has blocked the poster
        # 6. Check if the request poster is the same as the claimed actor
        if claimed_actor != request_actor:
            raise HTTPException(
                status_code=400,
                detail="Unspecified actor.",
            )
        return await endpoint(db=db, request=request, **kwargs)

    return wrapper
