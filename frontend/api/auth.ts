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
  IUserProfile,
  IUserProfileUpdate,
  IUserProfileCreate,
  IUserOpenProfileCreate,
  ITokenResponse,
  IWebToken,
  INewTOTP,
  IEnableTOTP,
  IMsg,
} from "@/interfaces"
import { apiCore } from "./core"

export const apiAuth = {
  // TEST
  async getTestText() {
    return await useFetch<IMsg>(`${apiCore.url()}/creators/tester`)
  },
  // LOGIN WITH MAGIC LINK OR OAUTH2 (USERNAME/PASSWORD)
  async loginWithMagicLink(email: string) {
    return await useFetch<IWebToken>(`${apiCore.root()}/auth/magic/${email}`, {
      method: "POST",
    })
  },
  async validateMagicLink(token: string, data: IWebToken) {
    return await useFetch<ITokenResponse>(`${apiCore.root()}/auth/claim`, {
      method: "POST",
      body: data,
      headers: apiCore.headers(token),
    })
  },
  async loginWithOauth(username: string, password: string) {
    // Version of this: https://github.com/unjs/ofetch/issues/37#issuecomment-1262226065
    // useFetch is borked, so you'll need to ignore errors https://github.com/unjs/ofetch/issues/37
    const params = new URLSearchParams()
    params.append("username", username)
    params.append("password", password)
    return await useFetch<ITokenResponse>(`${apiCore.root()}/auth/login`, {
      method: "POST",
      body: params,
      // @ts-ignore
      headers: { "Content-Disposition": params },
    })
  },
  // TOTP SETUP AND AUTHENTICATION
  async loginWithTOTP(token: string, data: IWebToken) {
    return await useFetch<ITokenResponse>(`${apiCore.root()}/auth/totp`, {
      method: "POST",
      body: data,
      headers: apiCore.headers(token),
    })
  },
  async requestNewTOTP(token: string) {
    return await useFetch<INewTOTP>(`${apiCore.url()}/creators/new-totp`, {
      method: "POST",
      headers: apiCore.headers(token),
    })
  },
  async enableTOTPAuthentication(token: string, data: IEnableTOTP) {
    // FastAPI PUT expects `security_scopes` as well, which we're not implementing here
    // This implies you need to specify the body parsing destination: `data_in`
    return await useFetch<IMsg>(`${apiCore.root()}/auth/totp`, {
      method: "PUT",
      body: { data_in: data },
      headers: apiCore.headers(token),
    })
  },
  async disableTOTPAuthentication(token: string, data: IUserProfileUpdate) {
    return await useFetch<IMsg>(`${apiCore.root()}/auth/totp`, {
      method: "DELETE",
      body: data,
      headers: apiCore.headers(token),
    })
  },
  // MANAGE JWT TOKENS (REFRESH / REVOKE)
  async getRefreshedToken(token: string) {
    return await useFetch<ITokenResponse>(`${apiCore.root()}/auth/refresh`, {
      method: "POST",
      headers: apiCore.headers(token),
    })
  },
  async revokeRefreshedToken(token: string) {
    return await useFetch<IMsg>(`${apiCore.root()}/auth/revoke`, {
      method: "POST",
      headers: apiCore.headers(token),
    })
  },
  // USER PROFILE MANAGEMENT
  async createProfile(data: IUserOpenProfileCreate) {
    return await useFetch<IUserProfile>(`${apiCore.url()}/creators/`, {
      method: "POST",
      body: data,
    })
  },
  async getProfile(token: string) {
    return await useFetch<IUserProfile>(`${apiCore.url()}/creators/`, {
      headers: apiCore.headers(token),
    })
  },
  async updateProfile(token: string, data: IUserProfileUpdate) {
    // FastAPI PUT expects `security_scopes` as well, which we're not implementing here
    // This implies you need to specify the body parsing destination: `obj_in`
    return await useFetch<IUserProfile>(`${apiCore.url()}/creators/`, {
      method: "PUT",
      body: { obj_in: data },
      headers: apiCore.headers(token),
    })
  },
  // ACCOUNT RECOVERY
  async recoverPassword(email: string) {
    return await useFetch<IMsg | IWebToken>(
      `${apiCore.root()}/auth/recover/${email}`,
      {
        method: "POST",
      }
    )
  },
  async resetPassword(password: string, claim: string, token: string) {
    return await useFetch<IMsg>(`${apiCore.root()}/auth/reset`, {
      method: "POST",
      body: {
        new_password: password,
        claim,
      },
      headers: apiCore.headers(token),
    })
  },
  async requestValidationEmail(token: string) {
    return await useFetch<IMsg>(
      `${apiCore.url()}/creators/send-validation-email`,
      {
        method: "POST",
        headers: apiCore.headers(token),
      }
    )
  },
  async validateEmail(token: string, validation: string) {
    return await useFetch<IMsg>(`${apiCore.url()}/creators/validate-email`, {
      method: "POST",
      body: { validation },
      headers: apiCore.headers(token),
    })
  },
  // ADMIN USER MANAGEMENT
  async getAllUsers(token: string) {
    return await useFetch<IUserProfile[]>(`${apiCore.url()}/creators/all`, {
      headers: apiCore.headers(token),
    })
  },
  async toggleUserState(token: string, data: IUserProfileUpdate) {
    return await useFetch<IMsg>(`${apiCore.url()}/creators/toggle-state`, {
      method: "POST",
      body: data,
      headers: apiCore.headers(token),
    })
  },
  async createUserProfile(token: string, data: IUserProfileCreate) {
    return await useFetch<IUserProfile>(`${apiCore.url()}/creators/create`, {
      method: "POST",
      body: data,
      headers: apiCore.headers(token),
    })
  },
}
