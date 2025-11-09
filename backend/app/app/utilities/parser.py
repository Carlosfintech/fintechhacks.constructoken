"""Hop Sauna

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
along with this program.  If not, see <http:#www.gnu.org/licenses/>.

"""

from typing import Any
from dataclasses import dataclass
from copy import deepcopy
import mistune

import nh3
from babel import Locale, UnknownLocaleError

from app.core.config import settings
from .regexes import regex

NH3_ATTRIBUTES = deepcopy(nh3.ALLOWED_ATTRIBUTES)
NH3_ATTRIBUTES["a"].update(["rel", "translate", "target"])
NH3_ATTRIBUTES["span"] = set(["class"])
# https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel
NH3_REL_TERMS = [
    "alternate",
    "author",
    "bookmark",
    "canonical",
    "compression-dictionary",
    "dns-prefetch",
    "external",
    "expect",
    "help",
    "icon",
    "license",
    "manifest",
    "me",
    "modulepreload",
    "next",
    "nofollow",
    "noopener",
    "noreferrer",
    "opener",
    "pingback",
    "preconnect",
    "prefetch",
    "preload",
    "prerender",
    "prev",
    "privacy-policy",
    "search",
    "stylesheet",
    "tag",
    "terms-of-service",
]


@dataclass
class DataParser:

    def text_to_html(self, text: str) -> str:
        text = regex.links_to_markdown(text)
        text = regex.hashtag_to_markdown(text)
        return mistune.html(text).rstrip()

    def clean_html(self, text: str) -> str:
        return nh3.clean(
            text,
            attributes=NH3_ATTRIBUTES,
            attribute_filter=self._attribute_filter,
            link_rel=None,
        )

    def _get_default_language(self, data: Any, default: bool = False) -> str | None:
        if isinstance(data, dict):
            if data.get("@context") and isinstance(data["@context"], list):
                for term in data["@context"]:
                    if isinstance(term, dict) and term.get("@language"):
                        return term["@language"]
            if (
                data.get("contentMap")
                and isinstance(data["contentMap"], dict)
                and (data.get("summary") or data.get("content"))
            ):
                text = data.get("summary") or data.get("content")
                for k, v in data["contentMap"].items():
                    if v == text:
                        return k
            if data.get("language"):
                return data["language"]
            if data.get("object"):
                return self.get_default_language(data["object"])
        if default:
            return settings.DEFAULT_LANGUAGE
        return None

    def get_default_language(self, data: Any, default: bool = False) -> str | None:
        language = self._get_default_language(data, default)
        if language:
            try:
                Locale(language)
            except UnknownLocaleError:
                if default:
                    return settings.DEFAULT_LANGUAGE
                return None
            except TypeError:
                # It's already a Locale
                return language
        return language

    def _attribute_filter(self, tag, attr, value):
        # https://nh3.readthedocs.io/en/latest/
        # Mastodon likes to use span classes with `invisible`
        if tag == "span" and attr == "class":
            if "invisible" in value.split(" "):
                return "invisible"
            return None
        if attr == "rel":
            terms = set([v for v in value.split(" ") if v in NH3_REL_TERMS])
            terms.update(["noopener", "noreferrer"])
            return " ".join(terms)
        if attr == "translate":
            if "no" in value.split(" "):
                return "no"
            if "yes" in value.split(" "):
                return "yes"
            return None
        if attr == "target":
            if "_blank" in value.split(" "):
                return "_blank"
            return None
        return value


dataparser = DataParser()
