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

import type { ITokenResponse, IWebToken } from "@/interfaces"
import { apiAuth } from "@/api"
import { tokenExpired, tokenParser } from "@/utilities"
import { useToastStore } from "./toasts"

export const useTokenStore = defineStore("tokens", {
  state: (): ITokenResponse => ({
    access_token: "",
    refresh_token: "",
    token_type: "",
  }),
  persist: true,
  // persist: {
  //   storage: piniaPluginPersistedstate.cookies({
  //     // https://prazdevs.github.io/pinia-plugin-persistedstate/frameworks/nuxt-3.html
  //     // https://nuxt.com/docs/api/composables/use-cookie#options
  //     // in seconds
  //     path: "/",
  //     secure: true,
  //     maxAge: 60 * 60 * 24 * 90,
  //     expires: new Date(new Date().getTime() + 60 * 60 * 24 * 90),
  //   }),
  // },
  getters: {
    token: (state) => state.access_token,
    refresh: (state) => state.refresh_token,
  },
  actions: {
    async getTokens(payload: { username: string; password?: string }) {
      const toasts = useToastStore()
      // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment
      let response
      try {
        if (payload.password !== undefined)
          ({ data: response } = await apiAuth.loginWithOauth(
            payload.username,
            payload.password
          ))
        else
          ({ data: response } = await apiAuth.loginWithMagicLink(
            payload.username
          ))
        if (response.value) {
          if (response.value.hasOwnProperty("claim"))
            this.setMagicToken(response.value as unknown as IWebToken)
          else this.setTokens(response.value as unknown as ITokenResponse)
        } else throw "Error"
      } catch (error) {
        toasts.addNotice({
          title: "Login error",
          content:
            "Please check your details, or internet connection, and try again.",
          icon: "error",
        })
        await this.deleteTokens()
      }
    },
    async validateMagicTokens(token: string) {
      const toasts = useToastStore()
      try {
        const data: string = this.token
        // Check the two magic tokens meet basic criteria
        const localClaim = tokenParser(data)
        const magicClaim = tokenParser(token)
        if (
          localClaim.hasOwnProperty("fingerprint") &&
          magicClaim.hasOwnProperty("fingerprint") &&
          localClaim["fingerprint"] === magicClaim["fingerprint"]
        ) {
          const { data: response } = await apiAuth.validateMagicLink(token, {
            claim: data,
          })
          if (response.value) {
            this.setTokens(response.value as unknown as ITokenResponse)
          } else throw "Error"
        }
      } catch (error) {
        toasts.addNotice({
          title: "Login error",
          content:
            "Ensure you're using the same browser and that the token hasn't expired.",
          icon: "error",
        })
        // await this.deleteTokens()
      }
    },
    async validateTOTPClaim(data: string) {
      const toasts = useToastStore()
      try {
        const { data: response } = await apiAuth.loginWithTOTP(
          this.access_token,
          { claim: data }
        )
        if (response.value) {
          this.setTokens(response.value as unknown as ITokenResponse)
        } else throw "Error"
      } catch (error) {
        toasts.addNotice({
          title: "Two-factor error",
          content:
            "Unable to validate your verification code. Make sure it is the latest.",
          icon: "error",
        })
        await this.deleteTokens()
      }
    },
    setMagicToken(payload: IWebToken) {
      this.access_token = payload.claim
    },
    setTokens(payload: ITokenResponse) {
      this.access_token = payload.access_token
      this.refresh_token = payload.refresh_token
      this.token_type = payload.token_type
    },
    async refreshTokens() {
      let hasExpired = this.token ? tokenExpired(this.token) : true
      if (hasExpired) {
        hasExpired = this.refresh ? tokenExpired(this.refresh) : true
        if (!hasExpired) {
          try {
            const { data: response } = await apiAuth.getRefreshedToken(
              this.refresh
            )
            if (response.value) this.setTokens(response.value)
          } catch (error) {
            await this.deleteTokens()
          }
        } else {
          await this.deleteTokens()
        }
      }
    },
    // reset state using `$reset`
    async deleteTokens() {
      if (this.refresh_token)
        await apiAuth.revokeRefreshedToken(this.refresh_token)
      this.$reset()
    },
  },
})
