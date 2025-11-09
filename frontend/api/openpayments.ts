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

import type { IKeyable, IMsg } from "@/interfaces"
import { apiCore } from "./core"

export const apiOpenPayments = {
  // ORDER MANAGEMENT
  async orderProduct(
    key: string,
    payload: string,
    volume: number,
    token: string = ""
  ) {
    if (token)
      return await useFetch<IMsg>(
        `${apiCore.url()}/openpayments/order/${key}/${volume}`,
        {
          method: "POST",
          body: { buyer_wallet: payload },
          headers: apiCore.headers(token),
        }
      )
    else
      return await useFetch<IMsg>(
        `${apiCore.url()}/openpayments/order/${key}/${volume}`,
        {
          method: "POST",
          body: { buyer_wallet: payload },
        }
      )
  },
  async fulfilProduct(
    key: string,
    hash: string,
    interact_ref: string,
    token: string = ""
  ) {
    let query: IKeyable = {
      hash,
      interact_ref,
    }
    if (token) {
      return await useFetch<IMsg>(
        `${apiCore.url()}/openpayments/fulfil/${key}`,
        {
          method: "POST",
          query,
          headers: apiCore.headers(token),
          // @ts-ignore
          //   headers: Object.assign({}, apiCore.headers(token), {
          //     "Content-Disposition": params,
          //   }),
        }
      )
    } else
      return await useFetch<IMsg>(
        `${apiCore.url()}/openpayments/fulfil/${key}`,
        {
          method: "POST",
          query,
          // @ts-ignore
          //   headers: { "Content-Disposition": params },
        }
      )
  },
}
