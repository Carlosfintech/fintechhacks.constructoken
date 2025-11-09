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

from .email import (  # noqa: F401
    send_email,
    send_test_email,
    send_web_contact_email,
    send_magic_login_email,
    send_reset_password_email,
    send_new_account_email,
    send_email_validation_email,
)

# from .regexes import regex  # noqa: F401

# from .activity import ActivityResponse, verify_request_signature  # noqa: F401
