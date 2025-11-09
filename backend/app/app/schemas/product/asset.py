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

from typing import Optional
from ulid import ULID
from pydantic import ConfigDict, Field
from datetime import datetime

from app.schemas.base_schema import BaseSchema, LocaleType
from app.schema_types import ProductAssetType


class AssetBase(BaseSchema):
    created: Optional[datetime] = Field(None, description="Automatically generated date was first created.")
    type: ProductAssetType = Field(
        default=ProductAssetType.Download,
        description="Type of asset associated with the Product. Default is a download.",
    )
    language: Optional[LocaleType] = Field(
        None,
        description="Specify the language used by the actor. Controlled vocabulary defined by ISO 639-1, ISO 639-2 or ISO 639-3.",
    )
    name: Optional[str] = Field(None, description="Language-defined name for the product asset.")
    description: Optional[str] = Field(None, description="Language-defined description for the product asset.")
    path: Optional[str] = Field(None, description="Local path in the working directory or remote drive.")
    product_id: Optional[ULID] = Field(None, description="Asset is associated with this Product.")
    model_config = ConfigDict(from_attributes=True)


class AssetCreate(AssetBase):
    pass


class AssetUpdate(AssetBase):
    id: ULID = Field(..., description="Automatically generated unique identity.")
    updated: Optional[datetime] = Field(None, description="Automatically generated date was updated.")


class Asset(AssetUpdate):
    created: datetime = Field(..., description="Automatically generated date was first created.")
    updated: datetime = Field(..., description="Automatically generated date was last updated.")
