/*
  Hop Sauna
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
  along with this program.  If not, see <http:www.gnu.org/licenses/>.
*/

export const apiCore = {
  url(): string {
    return useRuntimeConfig().public.apiUrl
  },
  root(): string {
    return useRuntimeConfig().public.apiRootUrl
  },
  // WS(): string {
  //   return useRuntimeConfig().public.apiWS
  // },
  headers(token: string) {
    return {
      "Cache-Control": "no-cache",
      Authorization: `Bearer ${token}`,
    }
  },
}
