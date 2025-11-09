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
Actor Store is for ActivityPub personas and works belonging to the rest of the world.
*/

import type { IActorProfile, IStatus, IActorUpdate } from "@/interfaces"
import { apiActivity } from "@/api"
import { useAuthStore } from "./auth"
import { useTokenStore } from "./tokens"
import { useToastStore } from "./toasts"

export const useActorStore = defineStore("actors", {
  state: () => ({
    actors: {} as Record<string, IActorProfile>,
    statuses: {} as Record<string, IStatus[]>,
    featured: {} as Record<string, IStatus[]>,
    associations: [] as string[],
    editing: {} as IActorUpdate,
    editingLocale: "",
    savingEdit: false,
  }),
  persist: true,
  getters: {
    hasActor: (state) => {
      return (id: string) => id in state.actors
    },
    hasStatus: (state) => {
      return (id: string) => id in state.statuses
    },
    hasFeatured: (state) => {
      return (id: string) => id in state.featured
    },
    authStore: () => {
      return useAuthStore()
    },
    tokenStore: () => {
      return useTokenStore()
    },
    toastStore: () => {
      return useToastStore()
    },
  },
  actions: {
    // GETTERS
    async lookupActor(handle: string, locale: string = "") {
      // Can lookup without being logged in
      if (this.authStore.loggedIn) await this.tokenStore.refreshTokens()
      try {
        const { data: response } = await apiActivity.lookupActor(
          handle,
          this.tokenStore.token,
          locale
        )
        if (response.value) {
          this.setActor(handle, response.value)
        }
      } catch (error) {}
    },
    async lookupAssociations(handle: string, locale: string = "") {
      // Can lookup without being logged in
      if (this.authStore.loggedIn) await this.tokenStore.refreshTokens()
      try {
        const { data: response } = await apiActivity.lookupAssociations(
          handle,
          this.tokenStore.token,
          locale
        )
        if (response.value && response.value.length) {
          for (const r of response.value) {
            const h = `${r.preferredUsername}@${r.domain}`
            this.setActor(h, r)
            this.associations.push(r.id)
          }
        }
      } catch (error) {}
    },
    async getActorForUpdate(handle: string, locale: string = "") {
      this.resetActorForUpdate()
      if (this.authStore.loggedIn) {
        await this.tokenStore.refreshTokens()
        try {
          const { data: response } = await apiActivity.getActorForUpdate(
            handle,
            this.tokenStore.token,
            locale
          )
          if (response.value) {
            this.setActorForUpdate(response.value)
            this.setLanguageActorUpdate(this.editing.language as string)
          }
        } catch (error) {}
      }
    },
    async getStatuses(
      handle: string,
      locale: string = "",
      next: string = "",
      pinned: boolean = false
    ) {
      // Can lookup without being logged in
      if (this.authStore.loggedIn) await this.tokenStore.refreshTokens()
      try {
        const { data: response } = await apiActivity.getStatuses(
          handle,
          this.tokenStore.token,
          locale,
          next,
          pinned
        )
        if (response.value && response.value.length) {
          if (pinned) this.setFeatured(handle, response.value)
          else this.setStatuses(handle, response.value)
        }
      } catch (error) {}
    },
    // LOCAL SETTERS
    setActor(handle: string, payload: IActorProfile) {
      this.actors[handle] = payload
    },
    setStatuses(handle: string, payload: IStatus[]) {
      this.statuses[handle] = payload
    },
    setFeatured(handle: string, payload: IStatus[]) {
      this.featured[handle] = payload
    },
    setActorForUpdate(payload: IActorUpdate) {
      this.editing = payload
    },
    setLanguageActorUpdate(payload: string) {
      this.editing.language = payload
      this.editingLocale = payload
    },
    // SERVER SETTERS
    async updateActor(payload: IActorUpdate) {
      if (this.authStore.loggedIn) {
        this.savingEdit = true
        await this.tokenStore.refreshTokens()
        try {
          const { data: response } = await apiActivity.updateActor(
            this.tokenStore.token,
            payload
          )
          // if (response.value) {
          //   this.setActorForUpdate(response.value)
          // }
        } catch (error) {
          this.toastStore.addNotice({
            title: "Update error",
            content: error as string,
            icon: "error",
          })
        }
        this.savingEdit = false
      }
    },
    // reset state using `$reset`
    resetActorAssociations() {
      this.associations = [] as string[]
    },
    resetActorForUpdate() {
      this.editing = {} as IActorUpdate
    },
    resetState() {
      this.$reset()
    },
  },
})
