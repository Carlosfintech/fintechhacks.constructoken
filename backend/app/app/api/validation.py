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

from http import HTTPStatus
from typing import Any, Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


"""
Use `request_validation_exception_handler` by adding it to the FastAPI router:

    router = APIRouter(lifespan=deps.get_lifespan, route_class=FormValidationErrorRoute)

Adapted from the Pydantic docs and this discussion:
https://docs.pydantic.dev/latest/errors/errors/#custom-errors
https://github.com/fastapi/fastapi/discussions/11923
"""


def convert_validation_errors(validation_error: ValidationError | RequestValidationError) -> list[dict[str, Any]]:
    converted_errors = []
    for error in validation_error.errors():
        try:
            jsonable_encoder([error])
            converted_errors.append(error)
        except UnicodeDecodeError:
            converted_error = {
                "type": error["type"],
                "loc": loc_to_dot_sep(error["loc"]),
                "msg": error["msg"],
            }
            converted_errors.append(converted_error)
    return converted_errors


def loc_to_dot_sep(loc: tuple[str | int, ...]) -> str:
    path = ""
    for i, x in enumerate(loc):
        if isinstance(x, str):
            if i > 0:
                path += "."
            path += x
        elif isinstance(x, int):
            path += f"[{x}]"
        else:
            raise TypeError("Unexpected type")
    return path


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = convert_validation_errors(exc)
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(errors)},
    )


class FormValidationErrorRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as exc:
                return await request_validation_exception_handler(request, exc)

        return custom_route_handler
