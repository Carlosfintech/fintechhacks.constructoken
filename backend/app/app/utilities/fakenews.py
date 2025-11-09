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

from typing import Optional, Any
from pathlib import Path
from faker import Faker
import os
import random
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session

from app.core.config import settings
from app import crud, schemas, models  # , schema_types


class FakeNews:
    """Core functions for creating Actors and simulating interactions."""

    def __init__(
        self,
        languages: list[str] = ["fr_FR", "en_US", "ja_JP"],
    ) -> None:
        self.languages = languages
        self.fake = Faker()
        self.folder_id = "fakenews"
        self.working_path = Path(settings.DEFAULT_WORKING_DIRECTORY) / self.folder_id
        Path(self.working_path).mkdir(parents=True, exist_ok=True)
        self.fakebase_db = self.get_fakebase()

    ###################################################################################################
    # GENERATE AND TRACK CREATORS
    ###################################################################################################

    def create_creator(self, *, db: Session, password: str | None = None) -> dict[str, Any]:
        if not password:
            password = self.fake.password(length=16)
        language = random.choice(self.languages).replace("_", "-")
        while True:
            obj_in = schemas.CreatorCreate(
                **dict(
                    email=self.fake.safe_email(),
                    language=language,
                    password=password,
                )
            )
            if not self.is_unique(core="creators", field="email", name=obj_in.email):
                continue
            # Else, we're good and can create and add it to the db.
            db_creator = crud.creator.create(db=db, obj_in=obj_in)
            # obj_out = schemas.Creator.model_validate(db_creator)
            obj_out = obj_in.model_dump(mode="json")
            obj_out["id"] = db_creator.id
            self.fakebase_db["creators"].append(obj_out)
            self.save_fakebase(obj_in=self.fakebase_db)
            break
        return obj_out

    def create_actor(self, *, db: Session, creator: dict[str, Any] = None) -> models.Actor:
        if not creator:
            creator = self.create_creator(db=db)
        language = self._faker_language(text=creator["language"])
        fake = Faker(language)
        while True:
            obj_in = schemas.ActorCreate(
                **dict(
                    creator_id=creator["id"],
                    preferredUsername=fake.user_name(),
                    name=fake.name(),
                    language=creator["language"],
                    summary_raw={
                        language: self.generate_text(fake),
                    },
                    iconURL=self.get_random_iconURL(),
                    discoverable=True,
                )
            )
            if not self.is_unique(core="actors", field="preferredUsername", name=obj_in.preferredUsername):
                continue
            # Else, we're good and can create and add it to the db.
            db_actor = crud.actor.create(db=db, obj_in=obj_in)
            # obj_out = schemas.ActorCreate.model_validate(db_actor)
            self.fakebase_db["actors"].append(obj_in.model_dump(mode="json"))
            self.save_fakebase(obj_in=self.fakebase_db)
            break
        return db_actor

    def create_status(self) -> schemas.Status:
        pass

    ###################################################################################################
    # GENERATE ACTORS AND STATUS POSTS
    ###################################################################################################

    def generate_image(self) -> str:
        return self.fake.image_url(placeholder_url="https:/picsum.photos/{width}/{height}")

    def get_random_iconURL(self) -> str:
        iconURL = random.choice(os.listdir(Path(settings.API_MEDIA_STR) / "default-icon"))
        return f"{settings.SERVER_HOST}/{settings.API_MEDIA_STR}/default-icon/{iconURL}"

    def generate_link(self) -> str:
        if random.randint(0, 3) >= 2:
            return self.fake.uri(schemes=["https"])
        else:
            try:
                return f"[{self.fake.word(part_of_speech='noun')}]({self.fake.uri(schemes=['https'])})"
            except Exception:
                return f"[{self.fake.word()}]({self.fake.uri(schemes=['https'])})"

    def generate_tags(self, text: str) -> str:
        text = text.split()
        idx = [text.index(t) for t in text if t.endswith(".") or t.endswith("。")]
        try:
            rdx = random.sample(idx, k=random.randint(0, 3))
            for i in rdx:
                text[i] = f"#{text[i]}"
        except ValueError:
            pass
        return " ".join(text)

    def generate_text(self, fake: Faker = None) -> str:
        if not fake:
            fake = Faker()
        text = fake.text(max_nb_chars=300)
        text = self.generate_tags(text)
        return f"{text} {self.generate_link()}".strip()

    def create_note(self, language: str = None) -> dict[str, str]:
        if not language:
            language = random.choice(self.languages)
        fake = Faker(language)
        obj_in = dict(
            language=language,
            content_header_raw=fake.text(max_nb_chars=40).strip().rstrip("."),
            content_raw=self.generate_text(fake),
        )
        return obj_in

    ###################################################################################################
    # MANAGE FAKEBASE
    ###################################################################################################

    def get_fakebase(self, *, source_id: Optional[str] = "fakebase.json") -> dict[str, str]:
        try:
            return crud.source.get(
                folder_id=self.folder_id, source_id=source_id, null_response={"creators": [], "actors": []}
            )
        except ClientError:
            return {"creators": [], "actors": []}

    def is_unique(self, *, core: str, field: str, name: str) -> bool:
        return not next((item for item in self.fakebase_db[core] if item[field] == name), False)

    def save_fakebase(self, *, obj_in: dict, source_id: Optional[str] = "fakebase.json") -> None:
        try:
            obj_in = {k: v for k, v in obj_in.items() if k != v}
            crud.source.update(source=obj_in, folder_id=self.folder_id, source_id=source_id)
        except Exception:
            pass

    def _faker_language(self, *, text: str) -> str:
        text = text.split("-")
        text[1] = text[1].upper()
        return "_".join(text)
