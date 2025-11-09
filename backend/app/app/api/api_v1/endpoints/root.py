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

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from bovine import activitystreams

from app import crud, models, schemas, schema_types
from app.api import deps
from app.core.config import settings

from faststream.rabbit.fastapi import RabbitRouter, Logger
from app.utilities.activity import ActivityResponse, verify_request_signature

router = RabbitRouter("amqp://guest@queue//")

# router = APIRouter(lifespan=deps.get_lifespan)
# ngrok http --url=mollusk-modest-sharply.ngrok-free.app 80


class Incoming(BaseModel):
    m: dict


def call():
    return True


@router.subscriber("inbox")
async def process_inbox(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    logger: Logger,
    request: dict[str, Any],
):
    """
    FastStream Inbox process
    """
    activity = schemas.InboxActivity.model_validate(request)
    logger.info(activity.payload)
    crud.source.save_json(
        data=activity.payload,
        source_id=f"{activity.type.value.lower()}_response.json",
    )
    return {"response": "All polished."}


@router.subscriber("process_inbox")
@router.publisher("response")
async def hello(m: Incoming, logger: Logger, d=Depends(call)):
    logger.info(m)
    return {"response": "Hello, Rabbit!"}


@router.subscriber("response")
async def reponses(response: Any, logger: Logger, d=Depends(call)):
    logger.info(response)


@router.get("/tester", response_model=schemas.Msg)
async def hello_http() -> Any:
    """
    Test current endpoint.
    """
    inc = Incoming(**{"m": {"m": "Hello, Bunny!"}})
    await router.broker.publish(inc, "process_inbox")
    return {"msg": "Message returned ok."}


@router.post("/{actorname}/inbox", status_code=status.HTTP_202_ACCEPTED)
@router.post("/{actortype}/{actorname}/inbox", status_code=status.HTTP_202_ACCEPTED)
@verify_request_signature
async def post_to_actor_inbox(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    actortype: str = "person",
    actorname: str,
    request: Request,
):
    """
    Post an activity to a local actor.
    """
    db_obj = crud.actor.get_by_name(db=db, name=actorname)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail=f"{actortype} unknown.",
        )
    body = await request.json()
    # Pass the inbox to FastStream for asynchronous response
    await router.broker.publish(body, "inbox")

    print("-----------------------------")
    print(request.cookies)
    print(request.client)
    print(request.url)
    print(request.method)
    print(request.headers)
    print("-----------------------------")
    # 1. Reject large requests
    # if len(body) > settings.JSONLD_MAX_SIZE:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Payload data too large.",
    #     )
    # 2. Check if user or domain are blocked
    # 3. Get actor and check if they have blocked the poster
    # db_obj = crud.actor.get_by_name(db=db, preferredUsername=actorname, actortype=actortype)
    # if not db_obj:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"{actortype} unknown.",
    #     )
    # 4. Verify the sender, and add to db if needed
    # print("-----------------------------")
    # validation_response = await crud.activity.validate_http_signature(db_obj=db_obj, request=request)
    # validation_response = await crud.activity.validate_http_signature(request=request)
    # if validation_response:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=validation_response,
    #     )
    # print(json.dumps(body, indent=2))
    # print("-----------------------------")
    # crud.source.save_json(data=body, source=f"{settings.DEFAULT_WORKING_DIRECTORY}/test_follow_response.json")
    # 5. Convert body to an activitypub class
    # 6. Queue processing the activity


@router.get("/{actortype}/{actorname}/outbox", status_code=status.HTTP_202_ACCEPTED)
@verify_request_signature
async def get_actor_outbox(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    actortype: schema_types.ActorType | None = None,
    actorname: str,
    request: Request,
):
    """
    Get the Outbox of a local Actor.
    """
    db_obj = crud.actor.get_by_name(db=db, name=actorname)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail=f"{actortype} unknown.",
        )
    return activitystreams.OrderedCollection(
        db_obj.outbox, first=f"{db_obj.outbox}?page=true", last=f"{db_obj.outbox}?min_id=0&page=true"
    ).build()


@router.get("/{actortype}/{actorname}/featured", status_code=status.HTTP_202_ACCEPTED)
@verify_request_signature
async def get_actor_featured_collection(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    actortype: schema_types.ActorType | None = None,
    actorname: str,
    request: Request,
):
    """
    Get the Featured Collection of a local Actor.
    """
    db_obj = crud.actor.get_by_name(db=db, name=actorname)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail=f"{actortype} unknown.",
        )
    return activitystreams.OrderedCollection(db_obj.featured).build()


###################################################################################################
# PLACE IN ACTOR FILE
###################################################################################################


@router.get("/{actorname}", response_class=ActivityResponse)
@router.get("/{actortype}/{actorname}", response_class=ActivityResponse)
async def read_actor(
    *,
    db: Annotated[Session, Depends(deps.get_db)],
    actortype: schema_types.ActorType | None = None,
    actorname: str,
    request: Request,
) -> Any:
    """
    Get an actor of a specified type.
    """
    db_obj = crud.actor.get_by_name(db=db, name=actorname)
    if not db_obj:
        raise HTTPException(
            status_code=400,
            detail=f"{actortype} unknown.",
        )
    return crud.actor.get_wellknown_actor(db=db, db_obj=db_obj)
    # wk = crud.activity.get_wellknown_actor()
    # # output_class = ap.get_class(wk)
    # return Response(content=orjson.dumps(wk), media_type="application/activity+json")
