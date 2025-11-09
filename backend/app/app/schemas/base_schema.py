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
from typing_extensions import Annotated
from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationError,
)
from pydantic._internal._model_construction import ModelMetaclass
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from babel import Locale  # , UnknownLocaleError
from sqlalchemy_utils import Country, Currency


class BaseSchema(BaseModel):
    @property
    def as_db_dict(self):
        to_db = self.model_dump(exclude_defaults=True, exclude_none=True, exclude={"identifier, id"})
        for key in ["id", "identifier"]:
            if key in self.model_dump().keys():
                to_db[key] = self.model_dump()[key].hex
        return to_db


class ModelMeta(ModelMetaclass):
    """
    From https://github.com/pydantic/pydantic/discussions/6699#discussioncomment-11529807

    Use to exclude inherited fields. e.g.

        class Parent(BaseModel):
            key: str
            value: str

        class Child(Parent, metaclass=ModelMeta):
            __exclude_parent_fields__ = ["value"]

    This is critical where we don't want to send confidential or private information while
    subclassing models.
    """

    #
    def __new__(cls, name, bases, namespace, **kwargs):
        epf = set(namespace.get("__exclude_parent_fields__", set()) or set())
        parent = bases[0]  # There will be at least BaseModel
        for base in parent.__mro__:
            if base == BaseModel:
                break
            base.__annotations__ = {k: v for k, v in base.__annotations__.items() if k not in epf}
            base.__pydantic_fields_set__ = {k for k in base.__annotations__.keys() if k not in epf}
            new_validators = {}
            validators = getattr(base, "__pydantic_decorators__", None)
            if validators:
                for (
                    func_name,
                    validator_decorator,
                ) in validators.field_validators.items():
                    if set(validator_decorator.info.fields) & epf:
                        continue
                    new_validators[func_name] = validator_decorator
                validators.field_validators = new_validators
        return super().__new__(cls, name, bases, namespace, **kwargs)


# ======================================================================================================================
# THIRD-PARTY TYPES FOR LOCALE AND COUNTRY
# https://docs.pydantic.dev/latest/concepts/types/#handling-third-party-types
# https://docs.pydantic.dev/latest/concepts/json_schema/#implementing-__get_pydantic_json_schema__
class _LocalePydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        A Locale Annotation which supports integrations with BaseModel
        * str will be parsed as `Locale` instances
        * `Locale` instances will be parsed as `Locale` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a str
        """

        def validate_type(value: str | Locale) -> Locale:
            if isinstance(value, str):
                try:
                    return Locale.parse(value, sep="-")
                except ValueError:
                    return Locale.parse(value, sep="_")
            return Locale(str(value).lower())

        from_instance_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(validate_type),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_instance_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(Locale),
                    from_instance_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance).replace("_", "-")
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `str`
        json_schema = handler(core_schema.str_schema())
        json_schema["examples"] = ["fr"]
        return json_schema


class _CountryPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        A Country Annotation which supports integrations with BaseModel
        * str will be parsed as `Country` instances
        * `Country` instances will be parsed as `Country` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a str
        """

        def validate_type(value: str | Country) -> Country:
            if isinstance(value, str):
                return Country(value.upper())
            if isinstance(value, Country):
                return Country(value.code)

        from_instance_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(validate_type),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_instance_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(Country),
                    from_instance_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: str(instance)),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `str`
        json_schema = handler(core_schema.str_schema())
        json_schema["examples"] = ["FR"]
        return json_schema


class _CountryListPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def validate_type(value: list[str] | list[Country]) -> list[Country]:
            if not isinstance(value, list):
                raise ValidationError("Input should be an instance of `list[Country]`")
            validated = []
            for v in value:
                if isinstance(v, str):
                    validated.append(Country(v.upper()))
                if isinstance(v, Country):
                    validated.append(Country(v.code))
            return validated

        from_instance_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(validate_type),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_instance_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(list),
                    from_instance_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: [str(i) for i in instance]),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `str`
        json_schema = handler(core_schema.list_schema())
        json_schema["examples"] = [["FR", "GB", "ZA"]]
        return json_schema


class _CurrencyPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        A Currency Annotation which supports integrations with BaseModel
        * str will be parsed as `Currency` instances
        * `Currency` instances will be parsed as `Currency` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a str
        """

        def validate_type(value: str | Currency) -> Currency:
            if isinstance(value, str):
                return Currency(value.upper())
            if isinstance(value, Currency):
                return Currency(value.code)

        from_instance_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(validate_type),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_instance_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(Currency),
                    from_instance_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: str(instance)),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `str`
        json_schema = handler(core_schema.str_schema())
        json_schema["examples"] = ["EUR"]
        return json_schema


# ANNOTATED WRAPPERS FOR USE IN BASEMODELS
LocaleType = Annotated[Locale, _LocalePydanticAnnotation]
CountryType = Annotated[Country, _CountryPydanticAnnotation]
CountryListType = Annotated[list[Country], _CountryListPydanticAnnotation]
CurrencyType = Annotated[Currency, _CurrencyPydanticAnnotation]

# ======================================================================================================================
