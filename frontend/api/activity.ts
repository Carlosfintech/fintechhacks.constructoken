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

import type {
  IActorProfile,
  IKeyable,
  IStatus,
  IActorUpdate,
  IMsg,
  IMediaImport,
} from "@/interfaces"
import { apiCore } from "./core"

export const apiActivity = {
  // VALIDATE ACTORS
  async checkPersonaName(name: string) {
    return await useFetch(`${apiCore.url()}/actor/check/${name}`)
  },
  // ACTOR PERSONAS AND WORKS
  async getCreatorActors(token: string, language: string = "") {
    let query: IKeyable = {}
    if (language) query["language"] = language
    return await useFetch<IActorProfile[]>(`${apiCore.url()}/actor`, {
      headers: apiCore.headers(token),
      query,
    })
  },
  // OTHER PUBLIC ACTORS
  async lookupActor(handle: string, token: string = "", language: string = "") {
    let query: IKeyable = {
      handle,
    }
    if (language) query["language"] = language
    if (token)
      return await useFetch<IActorProfile>(`${apiCore.url()}/actor/lookup`, {
        headers: apiCore.headers(token),
        query,
      })
    else
      return await useFetch<IActorProfile>(`${apiCore.url()}/actor/lookup`, {
        query,
      })
  },
  async lookupAssociations(
    handle: string,
    token: string = "",
    language: string = ""
  ) {
    let query: IKeyable = {
      handle,
    }
    if (language) query["language"] = language
    if (token)
      return await useFetch<IActorProfile[]>(
        `${apiCore.url()}/actor/associations`,
        {
          headers: apiCore.headers(token),
          query,
        }
      )
    else
      return await useFetch<IActorProfile[]>(
        `${apiCore.url()}/actor/associations`,
        {
          query,
        }
      )
  },
  async getPublicActors() {
    return await useFetch<IActorProfile[]>(`${apiCore.url()}/actor/all`)
  },
  // MANAGING CREATOR ACTORS - PERSONAS AND WORKS
  async getActorForUpdate(
    handle: string,
    token: string = "",
    language: string = ""
  ) {
    let query: IKeyable = {
      handle,
    }
    if (language) query["language"] = language
    return await useFetch<IActorUpdate>(`${apiCore.url()}/actor/update`, {
      headers: apiCore.headers(token),
      query,
    })
  },
  async createActor(
    handle: string,
    token: string,
    language: string = "",
    maker: string = ""
  ) {
    let query: IKeyable = {}
    if (language) query["language"] = language
    if (maker)
      return await useFetch<IActorProfile>(
        `${apiCore.url()}/actor/${maker}/${handle}`,
        {
          method: "POST",
          headers: apiCore.headers(token),
          query,
        }
      )
    else
      return await useFetch<IActorProfile>(`${apiCore.url()}/actor/${handle}`, {
        method: "POST",
        headers: apiCore.headers(token),
        query,
      })
  },
  async updateActor(token: string, payload: IActorUpdate) {
    return await useFetch<IMsg>(`${apiCore.url()}/actor/${payload.id}`, {
      method: "PUT",
      body: { obj_in: payload },
      headers: apiCore.headers(token),
    })
  },
  async postMediaForActor(token: string, payload: FormData) {
    return await useFetch<IMsg>(`${apiCore.url()}/actor/media`, {
      method: "POST",
      body: payload,
      headers: apiCore.headers(token),
    })
  },
  async updateMediaForActor(token: string, key: string, payload: IMediaImport) {
    return await useFetch<IMsg>(
      `${apiCore.url()}/actor/${key}/media/${payload.id}`,
      {
        method: "PUT",
        body: { obj_in: payload },
        headers: apiCore.headers(token),
      }
    )
  },
  async deleteActor(token: string, key: string) {
    return await useFetch<IMsg>(`${apiCore.url()}/actor/${key}`, {
      method: "DELETE",
      headers: apiCore.headers(token),
    })
  },
  async deleteMediaForActor(token: string, key: string, media_key: string) {
    return await useFetch<IMsg>(
      `${apiCore.url()}/actor/${key}/media/${media_key}`,
      {
        method: "DELETE",
        headers: apiCore.headers(token),
      }
    )
  },
  // STATUSES
  async getStatuses(
    handle: string,
    token: string = "",
    language: string = "",
    next: string = "",
    pinned: boolean = false
  ) {
    let query: IKeyable = {}
    if (language) query["language"] = language
    if (pinned) query["pinned"] = true
    if (next) query["next"] = next
    if (token)
      return await useFetch<IStatus[]>(
        `${apiCore.url()}/actor/${handle}/statuses`,
        {
          headers: apiCore.headers(token),
          query,
        }
      )
    else
      return await useFetch<IStatus[]>(
        `${apiCore.url()}/actor/${handle}/statuses`,
        {
          query,
        }
      )
  },
}
