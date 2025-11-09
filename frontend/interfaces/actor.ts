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
    Merchant Listing data: https://developers.google.com/search/docs/appearance/structured-data/merchant-listing#technical-guidelines
*/

import type { IMediaImport } from "./activitypub/media"

export interface ITag {
  type: "Hashtag"
  href: string
  name: string
}

export interface IImage {
  type: "Image"
  url: string
  mediaType?: string
}

export interface IPublicKey {
  id: string
  owner: string
  publicKeyPem: string
}

export interface IWellKnownActor {
  id: string
  type: "Person" | "Service"
  preferredUsername: string
  name?: string
  summary?: string
  inbox: string
  outbox: string
  followers?: string
  following?: string
  url?: string
  domain?: string
  iconUrl?: string
  iconAlt?: string
  imageUrl?: string
  imageAlt?: string
  price?: number
  priceCurrency?: string
  tag: ITag[]
  manuallyApprovesFollowers?: boolean
  discoverable?: boolean
  memorial?: boolean
  suspended?: boolean
  publicKey?: IPublicKey
}

export interface IActorProfile {
  id: string
  created?: string
  type: "Person" | "Service"
  preferredUsername: string
  name?: string
  domain?: string
  URL?: string
  URI?: string
  iconURL?: string
  standoutURL?: string
  outbox: string
  // featured: string
  followersCount?: number
  followingCount?: number
  statusCount?: number
  lastStatus?: string
  locked?: boolean
  discoverable?: boolean
  memorial?: boolean
  language?: string
  summary?: string
  suspended?: boolean
  attachment?: {
    [key: string]: any | any[]
  }[]
  works?: IWorkSnapshot[]
  maker_id?: string
  default_persona: boolean
  is_following: boolean
  is_followed: boolean
}

export interface IActorUpdate {
  id: string
  name?: string
  default_persona: boolean
  language?: string
  summary?: string
  summary_raw?: string
  locked?: boolean
  discoverable?: boolean
  attachment?: {
    [key: string]: any | any[]
  }[]
  icon?: IMediaImport
  iconURL?: string
  standout?: IMediaImport
  standoutURL?: string
}

export interface IWorkSnapshot {
  id: string
  created?: string
  preferredUsername: string
  name?: string
  domain?: string
  URL?: string
  URI?: string
  iconURL?: string
  standoutURL?: string
  summary?: string
  price?: number
  priceCurrency?: string
}

export interface IWorkOffer {
  url?: string
  price: number
  priceCurrency: string
}

export interface IWorkProduct {
  name: string
  image?: string | string[]
  description?: string
  offers?: IWorkOffer | IWorkOffer[]
}

export interface IWorkProductSnapshot {
  name: string
  image?: string
  description?: string
  url?: string
  price?: number
  priceCurrency?: string
}
