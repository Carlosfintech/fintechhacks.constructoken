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

import secrets
import warnings
from typing import Annotated, Any, List, Optional, Literal
from typing_extensions import Self
from babel import Locale

from pydantic import (
    AnyUrl,
    AnyHttpUrl,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    BeforeValidator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    SERVER_NAME: str
    SERVER_LANGUAGE: str = "en"
    # SERVER_HOST: AnyHttpUrl
    SERVER_BOT: str = "Symona"
    API_V1_STR: str = "/v1"
    API_ROOT_STR: str = ""
    SECRET_KEY: str = secrets.token_urlsafe(32)
    TOTP_SECRET_KEY: str = secrets.token_urlsafe(32)
    # ACCESS for authentication, REFRESH for refreshing expired ACCESS tokens
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 5  # 5 minutes
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 0  # REFRESH tokens don't expire -- they must be revoked
    USE_REFRESH_TOKEN: bool = True  # use refresh tokens
    FORCE_TOTP: bool = True
    JWT_ALGO: str = "HS512"
    TOTP_ALGO: str = "SHA-1"
    HASH_ALGO: List[str] = ["argon2"]
    FRONTEND_HOST: AnyHttpUrl = "http://localhost:3000"
    NGROK_DOMAIN: str = "1270-193-32-126-143.ngrok-free.app"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", "http://localhost:8080"]'
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SERVER_HOST(self) -> str:
        return f"https://{self.NGROK_DOMAIN}"

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None

    # ACTIVITYPUB SETTINGS
    JSONLD_MAX_SIZE: int = 1024 * 50  # 50 KB
    REFETCH_AFTER: int = 3  # days, refetch remote content

    # OPENPAYMENTS SETTINGS
    DEFAULT_REDIRECT_AFTER_AUTH: str = "http://localhost:3000/fulfil/"
    TEST_SELLER_WALLET: str
    TEST_SELLER_KEY: str
    TEST_SELLER_KEY_ID: str
    TEST_BUYER_WALLET: str

    # NODEINFO 2.1
    SOFTWARE_NAME: str = "hop-sauna"
    SOFTWARE_VERSION: str = "0.1.0"
    SOFTWARE_REPOSITORY: AnyHttpUrl = "https://codeberg.org/whythawk/hop-sauna"
    SOFTWARE_HOMEPAGE: AnyHttpUrl = "https://codeberg.org/whythawk/hop-sauna"
    OPEN_REGISTRATION: bool = True

    # GENERAL SETTINGS
    MULTI_MAX: int = 20
    DEFAULT_WORKING_DIRECTORY: str = "working"
    DEFAULT_MEDIA_MAX_SIZE: int = 12800000000
    API_MEDIA_STR: str = "media"
    API_AVATAR_DIRECTORY: str = "avatar"
    API_STANDOUT_DIRECTORY: str = "standout"
    API_STATUS_DIRECTORY: str = "status"
    DEFAULT_LANGUAGE: Locale = Locale("en")
    MINIMUM_NAME_LENGTH: int = 5
    MAXIMUM_NAME_LENGTH: int = 64
    DUNBARS_NUMBER: int = 150
    RESERVED_NAMES: list[str] = [
        "abuse",
        "account",
        "accounts",
        "admin",
        "administration",
        "administrator",
        "admins",
        "api",
        "auth",
        "authentication",
        "banned",
        "billing",
        "config",
        "error",
        "help",
        "helpdesk",
        "host",
        "hostname",
        "index",
        "info",
        "instance",
        "mod",
        "moderator",
        "moderators",
        "mods",
        "monitoring",
        "notification",
        "notifications",
        "oauth",
        "owner",
        "password",
        "permissions",
        "ping",
        "preferences",
        "public",
        "queue",
        "recover",
        "register",
        "registration",
        "root",
        "security",
        "server",
        "staff",
        "status",
        "subscriber",
        "subscription",
        "superuser",
        "support",
        "system",
        "team",
        "teams",
        "undefined",
        "user",
        "users",
        "validate",
        "validation",
        "validator",
        "webmaster",
        "www",
    ]

    # DATABASE SETTINGS
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    EMAILS_TO_EMAIL: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"

    @computed_field  # type: ignore[misc]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.SMTP_PORT and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_ADMIN: EmailStr
    FIRST_ADMIN_PASSWORD: str

    # Redis cache settings
    DOCKER_IMAGE_CACHE: str = "cache"
    REDIS_PASSWORD: str
    REDIS_PORT: int = 6379

    # DIGITALOCEAN SPACES KEYS
    SPACES_ACCESS_KEY: Optional[str] = None
    SPACES_SECRET_KEY: Optional[str] = None
    SPACES_REGION_NAME: Optional[str] = None
    SPACES_ENDPOINT_URL: Optional[HttpUrl] = None
    SPACES_BUCKET: Optional[str] = None
    SPACES_VOLUME_ID: Optional[str] = None
    USE_SPACES: bool = False

    @model_validator(mode="after")
    def _set_default_use_spaces(self) -> Self:
        if not self.USE_SPACES:
            self.USE_SPACES = bool(
                self.SPACES_ACCESS_KEY
                and self.SPACES_SECRET_KEY
                and self.SPACES_REGION_NAME
                and self.SPACES_ENDPOINT_URL
                and self.SPACES_BUCKET
            )
        return self

    # PAYMENT KEYS
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_PUBLIC_KEY: Optional[str] = None
    STRIPE_WEBHOOK: Optional[str] = None
    USE_STRIPE: bool = False

    @model_validator(mode="after")
    def _set_default_use_stripe(self) -> Self:
        if not self.USE_STRIPE:
            self.USE_STRIPE = bool(self.STRIPE_API_KEY and self.STRIPE_PUBLIC_KEY and self.STRIPE_WEBHOOK)
        return self

    # IP2LOCATION IP COUNTRY LOCATION
    IP2_DOWNLOAD_URL: HttpUrl = "https://download.ip2location.com/lite/"
    IP2_DOWNLOAD_FILE_TYPE: str = ".ZIP"
    IP2_DOWNLOAD_FILE_HASH: str = ".md5"
    IP2_FOLDER: Optional[str] = "ip2location"
    IP2_BIN_FILE: str = "IP2LOCATION-LITE-DB1.BIN"
    IP2_TOKEN: Optional[str] = None
    IP2_FILE: Optional[str] = "DB11LITEBIN"
    IP2_FILE_IPV6: Optional[str] = "DB11LITEBINIPV6"
    IP2_ENDPOINT_URL: Optional[HttpUrl] = None
    USE_IP2: bool = False
    EURO_CURRENCY: List[str] = [
        "AT",
        "BE",
        "BG",
        "CH",
        "CY",
        "CZ",
        "DE",
        "DK",
        "EE",
        "ES",
        "FI",
        "FR",
        "GR",
        "HR",
        "HU",
        "IE",
        "IS",
        "IT",
        "LI",
        "LT",
        "LU",
        "LV",
        "MT",
        "NL",
        "NO",
        "PL",
        "PT",
        "RO",
        "SE",
        "SI",
        "SK",
    ]

    @model_validator(mode="after")
    def _set_use_ip2_and_ip2_endpoint_url(self) -> Self:
        if not self.USE_IP2:
            self.USE_IP2 = bool(self.IP2_TOKEN and self.IP2_TOKEN and self.IP2_FILE)
        if self.USE_IP2 and not self.IP2_ENDPOINT_URL:
            self.IP2_ENDPOINT_URL = f"{self.IP2_DOWNLOAD_URL}?token={self.IP2_TOKEN}&file={self.IP2_FILE}"
        return self

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", ' "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("TOTP_SECRET_KEY", self.TOTP_SECRET_KEY)
        self._check_default_secret("FIRST_ADMIN_PASSWORD", self.FIRST_ADMIN_PASSWORD)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("REDIS_PASSWORD", self.REDIS_PASSWORD)

        return self


settings = Settings()
