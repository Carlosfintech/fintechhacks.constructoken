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
} from "./profile"

import type {
  ITokenResponse,
  IWebToken,
  INewTOTP,
  IEnableTOTP,
  ISendEmail,
  IMsg,
  INotification,
} from "./utilities"

import type {
  IImage,
  IPublicKey,
  ITag,
  IWellKnownActor,
  IActorProfile,
  IActorUpdate,
  IWorkOffer,
  IWorkProduct,
  IWorkSnapshot,
  IWorkProductSnapshot,
} from "./actor"

import type { IStatus, IStatusPost } from "./status"

import type { IRule } from "./instance"

import type { IGenerateCreator, IGeneratePersona } from "./generate"

// ACTIVITYPUB INTERFACES

import type { IMediaType, IMediaImport } from "./activitypub"

// https://stackoverflow.com/a/64782482/295606
interface IKeyable {
  [key: string]: any | any[]
}

export type {
  IKeyable,
  IUserProfile,
  IUserProfileUpdate,
  IUserProfileCreate,
  IUserOpenProfileCreate,
  ITokenResponse,
  IWebToken,
  INewTOTP,
  IEnableTOTP,
  ISendEmail,
  IMsg,
  INotification,
  IImage,
  IPublicKey,
  ITag,
  IWellKnownActor,
  IActorProfile,
  IActorUpdate,
  IWorkOffer,
  IWorkProduct,
  IWorkSnapshot,
  IWorkProductSnapshot,
  IStatus,
  IStatusPost,
  IRule,
  IGenerateCreator,
  IGeneratePersona,
  IMediaType,
  IMediaImport,
}
