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

from app.crud.base import CRUDBase
from app.models.product.asset import Asset
from app.schemas.product.asset import AssetCreate, AssetUpdate, Asset as AssetOut


class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetUpdate]):
    """
    All CRUD for Asset management.
    """

    pass


asset = CRUDAsset(model=Asset)
