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

import type { INotification } from "@/interfaces"
import { generateUUID } from "@/utilities"

export const useToastStore = defineStore("toasts", {
  state: () => ({
    notifications: [] as INotification[],
  }),
  getters: {
    first: (state) => state.notifications.length > 0 && state.notifications[0],
    notices: (state) => state.notifications,
  },
  actions: {
    addNotice(payload: INotification) {
      payload.uid = generateUUID()
      if (!payload.icon) payload.icon = "success"
      this.notices.push(payload)
    },
    removeNotice(payload: INotification) {
      this.notifications = this.notices.filter((note) => note !== payload)
    },
    async timeoutNotice(payload: INotification, timeout: number = 2000) {
      await new Promise((resolve) => {
        setTimeout(() => {
          this.removeNotice(payload)
          resolve(true)
        }, timeout)
      })
    },
    // reset state using `$reset`
    deleteNotices() {
      this.$reset()
    },
  },
})
