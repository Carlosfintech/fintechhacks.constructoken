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
  Convenience Composable for extracting necessary fields from AP schema.
  Derived from ActivityPub: https://www.w3.org/TR/activitystreams-vocabulary
  Product information stored in `attachment`: https://developers.google.com/search/docs/appearance/structured-data/merchant-listing#technical-guidelines
*/

import type {
  APActor,
  UrlField,
  APLink,
  APImage,
  ImageField,
  AttachmentField,
  AnyAPObject,
} from "activitypub-types"
import type {
  IWorkOffer,
  IWorkSnapshot,
  IWorkProductSnapshot,
  IWellKnownActor,
} from "~/interfaces"

// Type Predicates
function getValidLink(links: APLink[]): string | undefined {
  let link = links.find((term) => term.mediaType === "text/html")
  if (link !== undefined && "href" in link) return link.href
  return undefined
}
function getValidName(links: APLink[]): string | undefined {
  let link = links.find((term) => term.mediaType === "text/html")
  if (link !== undefined && "name" in link) return link.name
  return undefined
}
function getLink(term: any): string | undefined {
  if (isFieldArray(term)) {
    if (typeof term[0] === "string") return term[0]
    if (isAPLinkArray(term)) return getValidLink(term)
    if (isAPLinkArray(term[0]) && "url" in term[0]) return term[0].url as string
  }
  if (isField(term)) {
    if (typeof term === "string") return term
    if (isAPLink(term) && "href" in term) return term.href as string
    if (isAPLink(term) && "url" in term) return term.url as string
  }
  return undefined
}
function getAltText(
  term: any,
  summary: string | undefined
): string | undefined {
  if (isFieldArray(term) && isAPLinkArray(term) && term[0] !== undefined) {
    if ("href" in term[0]) return getValidName(term)
    if ("name" in term[0]) return term[0].name as string
  }
  if (isField(term) && isAPLink(term) && "name" in term)
    return term.name as string
  return summary
}

// Actor Field Predicates
function isField(term: any): term is UrlField | ImageField {
  return (
    term !== undefined &&
    !Array.isArray(term) &&
    (typeof term === "string" || typeof term === "object")
  )
}
function isFieldArray(term: any): term is UrlField[] | ImageField[] {
  return term !== undefined && Array.isArray(term) && term.length > 0
}
function isAPLink(term: any): term is APLink | APImage {
  return (
    term !== undefined &&
    !Array.isArray(term) &&
    ("href" in term || "url" in term)
  )
}
function isAPLinkArray(term: any): term is APLink[] | APImage[] {
  return (
    term !== undefined &&
    Array.isArray(term) &&
    term.length > 0 &&
    isAPLink(term[0])
  )
}
function isAnyAPObject(term: any): term is AnyAPObject {
  return (
    term !== undefined &&
    !Array.isArray(term) &&
    typeof term !== "string" &&
    "type" in term &&
    term.type === "Product"
  )
}
function isAttachmentFieldArray(term: any): term is AnyAPObject[] {
  return term !== undefined && Array.isArray(term) && term.length > 0
}

function fixLinks(
  term: string,
  domain: string,
  linkClass: string = ""
): string {
  // term = term
  //   .replaceAll("<a", "<NuxtLinkLocale")
  //   .replaceAll("</a", "</NuxtLinkLocale")
  //   .replaceAll('href="', 'to="')
  term = term.replaceAll(domain, "")
  console.log("domain", domain)
  if (linkClass) {
    term = term.replaceAll('rel="', `class="${linkClass}" rel="`)
  }
  return term
}

export const useExtractor = () => {
  function getSnapshot(actor: APActor): IWellKnownActor {
    let extract = <IWellKnownActor>{
      id: actor.id,
      type: actor.type,
      name: actor.name,
      preferredUsername: actor.preferredUsername,
      url: actor.url,
      summary: actor.summary,
      followers: actor.followers,
      following: actor.following,
    }
    // GET DOMAIN
    if (actor.id) {
      const url = new URL(actor.id as string)
      extract.domain = url.hostname
    }
    // GET ICON URL
    extract.iconUrl = actor.icon !== undefined ? getLink(actor.icon) : ""
    // GET ICON ALT TEXT
    extract.iconAlt =
      actor.icon !== undefined ? getAltText(actor.icon, extract.summary) : ""
    return extract
  }
  function localiseSummary(
    summary: string,
    url: string,
    linkClass: string = ""
  ): string {
    let URI = new URL(url)
    const domain = `${URI.protocol}//${URI.hostname}`
    return fixLinks(summary, domain, linkClass)
  }
  return {
    getSnapshot,
    localiseSummary,
  }
}
