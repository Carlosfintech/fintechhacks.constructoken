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

###################################################################################################
# CORE CRUD
###################################################################################################
from .crud_creator import creator  # noqa: F401
from .crud_token import token  # noqa: F401
from .crud_source import source  # noqa: F401
from .crud_location import location  # noqa: F401

###################################################################################################
# ACTIVITYSTREAMS CRUD
###################################################################################################
from .activitypub.crud_activity import activity  # noqa: F401
from .activitypub.crud_actor import actor  # noqa: F401
from .activitypub.crud_status import status  # noqa: F401
from .activitypub.crud_instance import rules  # noqa: F401
from .activitypub.crud_media import media  # noqa: F401

###################################################################################################
# PRODUCT CRUD
###################################################################################################

###################################################################################################
# OPENPAYMENTS CRUD
###################################################################################################
# from .openpayments.crud_payments import payments_parser  # noqa: F401
from .openpayments.crud_open_payments import OpenPaymentsProcessor  # noqa: F401


###################################################################################################
# NEW CRUD
###################################################################################################
# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
