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

from dataclasses import dataclass
import regex as re
from urllib.parse import urlparse
from copy import deepcopy
import nh3

from app.core.config import settings

NH3_ATTRIBUTES = deepcopy(nh3.ALLOWED_ATTRIBUTES)
NH3_ATTRIBUTES["a"].add("rel")


@dataclass
class Regexes:
    """
    Inspired by https://github.com/superseriousbusiness/gotosocial/blob/main/internal/regexes/regexes.go
    and https://stackoverflow.com/a/55827638/295606
    Check https://regex101.com/r/A326u1/5 for reference
    """

    # STANDARDS
    users: str = r"users"
    actors: str = r"actors"
    actorTypes: str = r"(?:creator|work)"
    statuses: str = r"statuses"
    inbox: str = r"inbox"
    outbox: str = r"outbox"
    followers: str = r"followers"
    following: str = r"following"
    liked: str = r"liked"
    featured: str = r"featured"
    publicKey: str = r"main-key"
    follow: str = r"follow"
    blocks: str = r"blocks"
    reports: str = r"reports"
    tags: str = r"tags"
    replies: str = r"replies"
    shares: str = r"shares"
    likes: str = r"likes"
    threads: str = r"threads"

    # DEFINITIONS
    # Allowed URI protocols for parsing links in text.
    schemes: str = r"(http|https)://"
    # A single number or script character in any language, including chars with accents.
    alphaNumeric: str = r"\p{L}\p{M}*|\p{N}"
    # Non-capturing group that matches against a single valid actorname character.
    actornameGrp: str = r"(?:" + alphaNumeric + r"|\.|\-|\_)"
    # Non-capturing group that matches against a single valid domain character.
    domainGrp: str = r"(?:" + alphaNumeric + r"|\.|\-|\:)"
    # Extract parts of one mention, maybe including domain.
    mentionName: str = r"^@(" + actornameGrp + r"+)(?:@(" + domainGrp + r"+))?$"
    # Extract all mentions from a text, each mention may include domain.
    mentionFinder: str = r"(?:^|\s)(@" + actornameGrp + r"+(?:@" + domainGrp + r"+)?)"
    # Pattern for emoji shortcodes. maximumEmojiShortcodeLength = 30
    emojiShortcode: str = r"\w{2,30}"
    # Extract all emoji shortcodes from a text.
    emojiFinder: str = r"(?:\b)?:(" + emojiShortcode + r"):(?:\b)?"
    # Validate a single emoji shortcode.
    emojiValidator: str = r"^" + emojiShortcode + r"$"
    # Pattern for actornames on THIS instance. maximumactornameLength = 64
    actornameStrict: str = r"^[A-Za-z0-9_]{1,64}$"
    # Relaxed version of actorname that can match instance accounts too.
    actornameRelaxed: str = r"[A-Za-z0-9_\.]{1,}"
    # Extract reported Note URIs from the text of a Misskey report/flag.
    misskeyReportNotesFinder: str = r"(?m)(?:^Note: ((?:http|https):\/\/.*)$)"
    # Pattern for ULID.
    ulid: str = r"[0123456789ABCDEFGHJKMNPQRSTVWXYZ]{26}"
    # Validate one ULID.
    ulidValidate: str = r"^" + ulid + r"$"
    # Validate one hashtag
    hashtag: str = r"(^|\B)#(?![0-9_]+\b)([" + alphaNumeric + r"_]{1,100})"

    # PATH PARTS
    actorPathPrefix: str = r"^/?" + actors + r"/(" + actornameRelaxed + r")"
    actorURI: str = rf"^{settings.SERVER_HOST}" + r"/?" + actorTypes + r"/(" + actornameRelaxed + r")"
    actorPath: str = actorPathPrefix + r"$"
    actorWebPathPrefix: str = r"^/?" + r"@(" + actornameRelaxed + r")"
    actorWebPath: str = actorWebPathPrefix + r"$"
    publicKeyPath: str = actorPathPrefix + r"/" + publicKey + r"$"
    inboxPath: str = actorPathPrefix + r"/" + inbox + r"$"
    outboxPath: str = actorPathPrefix + r"/" + outbox + r"$"
    followersPath: str = actorPathPrefix + r"/" + followers + r"$"
    followingPath: str = actorPathPrefix + r"/" + following + r"$"
    likedPath: str = actorPathPrefix + r"/" + liked + r"$"
    followPath: str = actorPathPrefix + r"/" + follow + r"/(" + ulid + r")$"
    likePath: str = actorPathPrefix + r"/" + liked + r"/(" + ulid + r")$"
    statusesPath: str = actorPathPrefix + r"/" + statuses + r"/(" + ulid + r")$"
    blockPath: str = actorPathPrefix + r"/" + blocks + r"/(" + ulid + r")$"
    reportPath: str = r"^/?" + reports + r"/(" + ulid + r")$"
    filePath: str = r"^/?(" + ulid + r")/([a-z]+)/([a-z]+)/(" + ulid + r")\.([a-z0-9]+)$"

    # COMPILED
    DOMAIN_FORMAT: re.Pattern = re.compile(
        r"(?:^(\w{1,255}):(.{1,255})@|^)"  # http basic authentication [optional]
        r"(?:(?:(?=\S{0,253}(?:$|:))"  # check full domain length to be less than or equal to 253 (starting after http basic auth, stopping before port)
        r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"  # check for at least one subdomain (maximum length per subdomain: 63 characters), dashes in between allowed
        r"(?:[a-z0-9]{1,63})))"  # check for top level domain, no dashes allowed
        r"|localhost)"  # accept also "localhost" only
        r"(:\d{1,5})?",  # port [optional]
        re.IGNORECASE,
    )
    SCHEME_FORMAT: re.Pattern = re.compile(r"^(http|hxxp|ftp|fxp)s?$", re.IGNORECASE)  # scheme: http(s) or ftp(s)
    LINK_FORMAT: re.Pattern = re.compile(
        r"(?:(?:https?)://)"
        r"(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
        r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|"
        r"(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)"
        r"(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*"
        r"(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?",
        re.IGNORECASE,
    )
    HASHTAG_FORMAT: re.Pattern = re.compile(hashtag, re.IGNORECASE)

    ###################################################################################################
    # MATCHES AND SUBSTITUTIONS
    ###################################################################################################

    def matches(self, exp: str, term: str) -> bool:
        if re.fullmatch(exp, term):
            return True
        return False

    def matches_from_text(self, exp: str, text: str) -> list[str]:
        # https://stackoverflow.com/a/67751172
        # https://stackoverflow.com/a/48902765
        return re.findall(exp, text)

    ###################################################################################################
    # URLS
    ###################################################################################################

    def url_validates(self, url: str) -> bool:
        try:
            url = str(url).strip()
            if not url or len(url) > 2048:
                return False
            result = urlparse(url)
            scheme = result.scheme
            domain = result.netloc
            return all(
                [
                    scheme in ["file", "http", "https"],
                    self.matches(self.SCHEME_FORMAT, scheme),
                    domain,
                    self.matches(self.DOMAIN_FORMAT, domain),
                ]
            )
        except (AttributeError, ValueError, TypeError):
            pass
        return False

    def url_root(self, url: str) -> str:
        if self.url_validates(url):
            return urlparse(str(url)).netloc
        return url

    def url_is_local(self, url: str) -> bool:
        if self.url_root(url) == settings.NGROK_DOMAIN:
            return True
        return False

    def actor_url(self, term: str) -> str:
        if self.url_validates(term):
            response = re.search(self.actorURI, term)
            if response:
                return response.group(0)
        return None

    ###################################################################################################
    # MENTIONS AND LINKS
    ###################################################################################################

    # async def hashdown(db: Session, match: str) -> str:
    #     obj_in = await crud.actor.fetch_remote(db=db, remote_id=match, fetch_only=True)
    #     if obj_in:
    #         return [match, f"[@{obj_in.preferredUsername}]({obj_in.URL})"]
    #     return [match, None]

    # async def mention_to_markdown(db: Session, text: str) -> str:
    #     mentions = [await hashdown(db, m.strip(".")) for m in re.findall(regex.mentionFinder, text)]
    #     for original, replacement in mentions:
    #         if replacement:
    #             text = text.replace(original, replacement)
    #     return text

    def links_to_markdown(self, text: str, length: int = 23, as_markdown: bool = False) -> str:
        for original in [u for u in re.findall(self.LINK_FORMAT, text) if regex.url_validates(u)]:
            result = urlparse(original)
            shortened = result.netloc + result.path
            if as_markdown:
                replacement = f"[{shortened}]({original})"
            else:
                replacement = f'<a href="{original}" rel="external">{shortened}</a>'
            text = text.replace(original, replacement)
        return text

    ###################################################################################################
    # HASHTAGS
    ###################################################################################################

    def hashtags_from_text(self, text: str) -> list[str]:
        # https://stackoverflow.com/a/67751172
        # https://stackoverflow.com/a/48902765
        if re.search(self.HASHTAG_FORMAT, text):
            return [h[1].lower() for h in re.findall(self.HASHTAG_FORMAT, text)]
        return []

    def hashtag_root(self, text: str) -> str:
        """Specifically for validating individual terms in tag objects"""
        root = re.search(self.HASHTAG_FORMAT, text)
        if root:
            return root.group(0).replace("#", "").lower()
        return None

    def hashdown(self, match: re.Match, as_markdown: bool = False) -> str:
        link = f"{settings.SERVER_HOST}/{self.tags}/{self.hashtag_root(match.group(0))}"
        if as_markdown:
            return f"[{match.group(0)}]({link})"
        else:
            return f'<a href="{link}" rel="tag">{match.group(0)}</a>'

    def hashtag_to_markdown(self, text: str) -> str:
        return re.sub(self.HASHTAG_FORMAT, self.hashdown, text)


regex = Regexes()
