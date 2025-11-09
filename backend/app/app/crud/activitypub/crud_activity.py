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

# from sqlalchemy.orm import Session
from typing import Any
import bovine
import base64

# from datetime import date, timedelta
import tomllib

# from app.crud.base import CRUDBase
# from app.core.config import settings
from app.schemas.activitypub.actor import ActivityActorCreate, ActorCreate
from app.schemas.activitypub.activity import InboxActivity
from app.schema_types import ActivityType, ObjectLinkType, ActorType
from app.utilities.regexes import regex
from app.schemas import NodeInfo
from ..crud_source import source as crud_source

# from app.schemas import TokenCreate, TokenUpdate
from app.core.config import settings


# with open("working/config.toml", "rb") as fp:
#     ACTOR_CONFIG = tomllib.load(fp)
ACTOR_CONFIG = dict(
    handle_name="turukawa",
    hostname="854a-193-32-126-143.ngrok-free.app",
    public_key="""
    -----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvCq7p6vn31brbHRvTglx
    HYaOfQs0m35ADycjb4HeCYxEULZZ8FfhlkqxA/pMzjWuXsBt/opAWUPN3rtl+Ffc
    mJ+5Qs9Rnc+SudIQzkxrOYafRXHU5qIE4akEO3W28WWkK6caLlrlzoWIzLnaLgcV
    twM26xCOvveTGqoquF90mIX8SRvKZq72qJJyfPylD8VgNhp5e99CxNIZTfOtNbG5
    WoeNJxvuxAv7WFM27bV0uPY19yGZBI4PkZ4yJszuc4VkbndGSPIuBI1xT4f6FGRF
    Nwn2VOPGvs4+3UqddhCxa9JavXeaRSjJefcsdLBGNkDDl0Y64laf18HMC1fkn4eQ
    BwIDAQAB
    -----END PUBLIC KEY-----
    """,
    private_key="""
    -----BEGIN PRIVATE KEY-----
    MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8Krunq+ffVuts
    dG9OCXEdho59CzSbfkAPJyNvgd4JjERQtlnwV+GWSrED+kzONa5ewG3+ikBZQ83e
    u2X4V9yYn7lCz1Gdz5K50hDOTGs5hp9FcdTmogThqQQ7dbbxZaQrpxouWuXOhYjM
    udouBxW3AzbrEI6+95Maqiq4X3SYhfxJG8pmrvaoknJ8/KUPxWA2Gnl730LE0hlN
    8601sblah40nG+7EC/tYUzbttXS49jX3IZkEjg+RnjImzO5zhWRud0ZI8i4EjXFP
    h/oUZEU3CfZU48a+zj7dSp12ELFr0lq9d5pFKMl59yx0sEY2QMOXRjriVp/XwcwL
    V+Sfh5AHAgMBAAECggEAMuSF88Apiz0JmMBXOG6SUw+JK2Xj+Sho8BBAY9DmuoNf
    GMtxQPGr+IfEH9TLgDyBqGv4dA91fw85N8RMvKIa7obIxzqmkv3I7AxWck219I2m
    N1Sl5iktE9GwbNqWO+0nPY1JJf98x2JTkTe1PJy68VBjwqksSpdQiLY8rrhWo0em
    BePP9VVI6aP22sTWAEjKUPhX5YI0nz+d4EaiIJvi5b0p+/njdHKU+AfvCf2Yu4G0
    cZ5QmtJBq0Te/CSJJOyI21tlnC6FCXVh373ll5gl21JhjyPWMjJ0Gb5w/QVWrf1W
    7xRcx/vOUzEBMLZd11URTQYlo6cpKQfG1z3W357IJQKBgQD8XqBAHc7WoDcqo79W
    0oM+Qrpou8JU3V84gONRi5kWaaCUuGMRfUk2wAsxC0tZn26PpHWM5CP4T5oZ9r7z
    wp2QWBTtZRLq5rxBaauSy1mRcTVfKPu3bt4O3O7YXlWWBbX4uG+SZXi+NK/Y8tz5
    915IBG4UaBeiYJ5/bFG5zqmFgwKBgQC+36y9mpg9zLYASGSoTtoudhlV2kJ2obIE
    0JwA8qIizGQJ/D0OqjCAx1JmHZ6SdxqCOCUM5bcKXEHj4HvH/ce/aEp9HjBeMG9F
    AtBu3Esz+MewGVIOMx+Tf/xo/l188EZEZGBTqbF4KN9r60MGJXA59cw0OsnqN9DX
    hXkGzAUILQKBgDJlNvz2ttoXDk0ee9P7n6esLYtCizDlL+GZo0siZEScfSuVknro
    mNktCk8V4UsZUjuu7KZg3Gn2g2BR7JnCsDIl1K//MgLkZo1ta4yZvN4VTEIfbfyY
    UBGJvsxIMjEOHON4+Raz2qOo48Cf5s6nvhUFhXHfw3ByeNQbLkq7YRC/AoGBALNe
    mQNYyyaQQJyFa2orJ6evveFLCVhYXWVe8KuHV8xhzMUBcBNe5dOu/AUQYpr7KEMl
    JdQ370niJt1RcKEhINwD0rQ/cW6iD36HxX3YsSc269jWAqFrc4n2JSo5l3s4hJ/y
    v/7/IdJsfoD5BfQ5rHwbO3n9oQ/kwfI28OPtR/FFAoGAa81eWg/Y5jrUiGkOuwCj
    5G1fD09ehHzgyYE56Z+BF7Byv3nVP9V5d6XpjD+ZIRqaPBXWXeN44ZX7ZkqxFTl7
    KLNq3UZ4csNY11SddgH6dC9oDHB08EBndr/FSt86QVS4ftnYSg+T57cpJ4F0VLgW
    S5WYfkaAuzDUNy5rZn+DFqw=
    -----END PRIVATE KEY-----
    """,
)
ACTOR_HANDLE_NAME = ACTOR_CONFIG["handle_name"]
ACTOR_HOSTNAME = settings.NGROK_DOMAIN
ACTOR_ID = f"https://{ACTOR_HOSTNAME}/{ACTOR_HANDLE_NAME}"
ACTOR_OBJECT = bovine.activitystreams.Actor(
    id=ACTOR_ID,
    preferred_username=ACTOR_HANDLE_NAME,
    name="Turukawa-the-bird",
    inbox=f"https://{ACTOR_HOSTNAME}/{ACTOR_HANDLE_NAME}/inbox",
    outbox=ACTOR_ID,
    public_key=ACTOR_CONFIG["public_key"],
    public_key_name="main-key",
).build()


class CRUDActivityPub:

    def save_actor_by_resource(self, *, resource: Any):
        data = ActivityActorCreate.model_validate(resource)
        filename = f"{base64.urlsafe_b64encode(str(data.URI).encode("utf-8")).decode("utf-8")}.json"
        crud_source.save_json(
            data=data.dict(exclude_unset=True), source=f"{settings.DEFAULT_WORKING_DIRECTORY}/{filename}"
        )

    def get_actor_by_resource(self, *, resource: str):
        # Check if the resource encapsulates a webfinger query
        preferredUsername, domain = bovine.utils.parse_fediverse_handle(resource)
        preferredUsername = preferredUsername.replace("acc:", "")
        if preferredUsername == ACTOR_HANDLE_NAME and domain == ACTOR_HOSTNAME:
            return ACTOR_OBJECT
        # Check if the resource is the actor URL
        resource = resource.replace("http:", "https:").replace("/inbox", "")
        if regex.url_validates(resource) and resource == ACTOR_ID:
            return ACTOR_OBJECT
        try:
            filename = f"{base64.urlsafe_b64encode(resource.encode("utf-8")).decode("utf-8")}.json"
            data = crud_source.load_json(source=f"{settings.DEFAULT_WORKING_DIRECTORY}/{filename}")
            data = ActorCreate.model_validate(data)
            return bovine.activitystreams.Actor(
                id=data.URI,
                preferred_username=data.preferredUsername,
                name=data.name,
                inbox=data.inbox,
                outbox=data.outbox,
                public_key=data.publicKey,
                public_key_name=str(data.publicKeyURI).split("#")[-1],
            ).build()
        except FileNotFoundError:
            pass
        return None

    def get_requests_actor(self):
        return bovine.BovineActor(
            actor_id=ACTOR_OBJECT["id"],
            public_key_url=ACTOR_OBJECT["publicKey"]["id"],
            secret=ACTOR_CONFIG["private_key"],
        )

    def get_wellknown_webfinger(self):
        return bovine.utils.webfinger_response_json(f"acct:{ACTOR_HANDLE_NAME}@{ACTOR_HOSTNAME}", ACTOR_OBJECT["id"])

    def get_wellknown_actor(self):
        return bovine.activitystreams.Actor(
            id=ACTOR_OBJECT["id"],
            preferred_username=ACTOR_HANDLE_NAME,
            name=ACTOR_OBJECT["name"],
            inbox=ACTOR_OBJECT["inbox"],
            outbox=ACTOR_OBJECT["outbox"],
            public_key=ACTOR_CONFIG["public_key"],
            public_key_name="main-key",
        ).build()

    def get_wellknown_nodeinfo(self) -> NodeInfo:
        # Get usage and return defaults
        # activeMonth = date.today() - timedelta(30)
        # activeHalf = date.today() - timedelta(180)
        usage = {
            "users": {
                "total": 1,
                "activeMonth": 1,
                "activeHalfyear": 1,
            },
            "localPosts": 0,
        }
        return NodeInfo(**{"usage": usage})

    def process_inbox(self, *, obj_in: InboxActivity | dict[str, Any]):
        # https://www.w3.org/TR/activitystreams-vocabulary/#motivations
        if isinstance(obj_in, dict):
            obj_in = InboxActivity.model_validate(obj_in)
        match obj_in.type:
            # ACTOR AND ACTIVITY STATE MANAGEMENT
            case ActivityType.Create:
                match obj_in.object_type:
                    case ObjectLinkType.Note:
                        if obj_in.has_content:
                            # Create a new Note
                            print(obj_in.object_type)
                        else:
                            # Likely to be an interaction
                            print(obj_in.object_type, obj_in.has_content)
            case ActivityType.Update:
                if isinstance(obj_in.object_type, ObjectLinkType):
                    # Update an Activity
                    print(obj_in.object_type)
                elif isinstance(obj_in.object_type, ActorType):
                    # Update an Actor
                    print(obj_in.object_type)
                else:
                    print(None)
            case ActivityType.Delete:
                if obj_in.object_type in [ObjectLinkType.Note, ObjectLinkType.Tombstone]:
                    # Delete the object
                    print(obj_in.object_type)
                elif obj_in.object_uri:
                    # Check if the object_uri is an actor or a post
                    print(obj_in.object_uri)
            # NOTIFICATIONS
            case ActivityType.Announce:
                if obj_in.object_type not in [ActivityType.Like, ActivityType.Dislike]:
                    # It's a type of interaction
                    print(obj_in.type)
            # RELATIONSHIP MANAGEMENT
            case ActivityType.Follow:
                print(obj_in.type)
            # REACTIONS
            case ActivityType.Like:
                print(obj_in.type)
            case ActivityType.Accept:
                if obj_in.object_type in [ActivityType.Follow, None]:
                    # Accepted the Follow
                    print(obj_in.type)
            case ActivityType.Reject:
                if obj_in.object_type in [ActivityType.Follow, None]:
                    # Rejected the Follow
                    print(obj_in.type)
            case ActivityType.Block:
                print(obj_in.type)
            # REPORT AND MODERATE
            case ActivityType.Flag:
                print(obj_in.type)
            # COLLECTION MANAGEMENT
            case ActivityType.Add | ActivityType.Move | ActivityType.Remove:
                # Post interaction types
                print(obj_in.type)
            # NEGATIONS
            case ActivityType.Undo:
                match obj_in.object_type:
                    case ActivityType.Follow:
                        print(obj_in.object_uri)
                    case ActivityType.Block:
                        print(obj_in.object_uri)
                    case ActivityType.Like | ActivityType.Accounce:
                        print(obj_in.object_uri)
            # EVERYTHING ELSE
            case _:
                # For now, anything not in the above isn't processed
                print("Not processed yet, or unknown.")


activity = CRUDActivityPub()
