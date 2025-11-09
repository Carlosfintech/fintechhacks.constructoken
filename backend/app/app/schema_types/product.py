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

from enum import auto

from app.schema_types.base import BaseEnum


class ProductType(BaseEnum):
    OneTime = auto()
    Subscription = auto()
    Conditional = auto()
    ConditionalSubscription = auto()


class ConditionType(BaseEnum):
    Amount = auto()
    Release = auto()


class RenewalType(BaseEnum):
    Weekly = auto()
    Monthly = auto()
    Annually = auto()
    Conditionally = auto()


class ProductAssetType(BaseEnum):
    Download = auto()
    Image = auto()


class ProductContributorRoleType(BaseEnum):
    Creator = auto()
    Editor = auto()
    Translator = auto()
    Illustrator = auto()
    Curator = auto()


class ProductFeeResponsibilityType(BaseEnum):
    Buyer = auto()
    Seller = auto()
    Choice = auto()
