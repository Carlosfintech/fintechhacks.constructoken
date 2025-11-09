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
    Convenience Interfaces.
    Derived from ActivityPub: https://www.w3.org/TR/activitystreams-vocabulary
*/

import type { IActorProfile } from "./actor"

export interface IStatusPost {
  id: string
  created?: string
  modified?: string
  fetched?: string
  URI?: string
  URL?: string
  local?: boolean
  language?: string
  content_header?: string
  content?: string
  attachments?: {
    [key: string]: any | any[]
  }[]
  tag?: {
    [key: string]: any | any[]
  }[]
  edited?: boolean
  actor?: IActorProfile
  reply_id?: string
  inReplyToURI?: string
  replyUR?: string
  reply_actor_id?: string
  reply_actor_URI?: string
  share_id?: string
  sharesURI?: string
  share_actor_id?: string
  share_actor_URI?: string
  thread_id?: string
  likesURI?: string
  sharesCount?: number
  likesCount?: number
  repliesCount?: number
  has_shared?: boolean
  has_liked?: boolean
  has_bookmarked?: boolean
  pinned?: boolean
}

export interface IStatus extends IStatusPost {
  content_header_raw?: string
  content_raw?: string
  share?: IStatusPost
}
