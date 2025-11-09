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

/*
Creator Store is for the personas and works belonging to the logged-in creator
*/

import type { IActorProfile } from "@/interfaces"
import { apiActivity } from "@/api"
import { useAuthStore } from "./auth"
import { useTokenStore } from "./tokens"

export const useCreatorStore = defineStore("creator", {
  state: () => ({
    personas: [] as IActorProfile[],
    works: [] as IActorProfile[],
  }),
  persist: true,
  getters: {
    persona: (state) =>
      state.personas.find((item) => item.default_persona === true),
    hasPersona: (state) => {
      return (id: string) => state.personas.some((item) => item.id === id)
    },
    hasWork: (state) => {
      return (id: string) => state.works.some((item) => item.id === id)
    },
    hasActor: (state) => {
      return (id: string) =>
        state.works.some((item) => item.id === id) ||
        state.personas.some((item) => item.id === id)
    },
    getMaker: (state) => {
      return (id: string) => state.personas.find((item) => item.id === id)
    },
    authStore: () => {
      return useAuthStore()
    },
    tokenStore: () => {
      return useTokenStore()
    },
  },
  actions: {
    // GETTERS
    async getActors(locale: string = "") {
      if (this.authStore.loggedIn) {
        await this.tokenStore.refreshTokens()
        if (this.tokenStore.token) {
          try {
            const { data: response } = await apiActivity.getCreatorActors(
              this.tokenStore.token,
              locale
            )
            if (response.value) {
              this.setPersonas(response.value)
              this.setWorks(response.value)
            }
          } catch (error) {}
        }
      }
    },
    // LOCAL SETTERS
    setPersonas(payload: IActorProfile[]) {
      this.personas = payload.filter((r) => r.type === "Person")
    },
    setWorks(payload: IActorProfile[]) {
      this.works = payload.filter((r) => r.type === "Service")
    },
    // reset state using `$reset`
    resetState() {
      this.$reset()
    },
  },
})
