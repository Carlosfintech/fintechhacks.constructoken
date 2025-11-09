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

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect, WebSocketException

# from websockets.exceptions import ConnectionClosedError


async def send_response(*, websocket: WebSocket, response: dict):
    try:
        await websocket.send_json(response)
        return True
    except (WebSocketDisconnect, WebSocketException):
        return False


async def receive_request(*, websocket: WebSocket) -> dict:
    try:
        return await websocket.receive_json()
    except (WebSocketDisconnect, WebSocketException):
        return {}


def sanitize_data_request(data: any) -> any:
    # Putting here for want of a better place
    if isinstance(data, (list, tuple, set)):
        return type(data)(sanitize_data_request(x) for x in data if x or isinstance(x, bool))
    elif isinstance(data, dict):
        return type(data)(
            (sanitize_data_request(k), sanitize_data_request(v))
            for k, v in data.items()
            if k and v or isinstance(v, bool)
        )
    else:
        return data
