# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is part of Sophie.

from __future__ import annotations

import re
import typing
import inspect

from abc import ABCMeta
from copy import deepcopy

from aiogram.dispatcher.filters import BaseFilter

from sophie.components.localization.strings import GetStrings
from sophie.utils.logging import log

from ._internal import _ArgField
from .fields import Undefined

if typing.TYPE_CHECKING:
    from aiogram.dispatcher.filters import CommandObject
    from aiogram.api.types import Message

WHITESPACE = r"\s?"
FIELD = r"(?P<{field}>{re}|)"
OPTIONAL_FIELD = r"(?:\s?(?P<{field}>{re}|)?)"


class ArgumentParserMeta(ABCMeta):

    def __new__(
            mcs, name: str, bases: typing.Tuple[typing.Type[ArgumentParser]], namespace: dict, **kwargs: typing.Any
    ) -> typing.Any:
        fields = {}
        parsers = {}

        # check in base class; if there is predefined
        # argument parsing methods or field declared in there
        # which would reduce code duplication
        for base in reversed(bases):
            if hasattr(base, "__ArgumentParser__") or base.__name__ != "ArgumentParser":
                fields.update(deepcopy(base.__fields__))
                parsers.update(deepcopy(base.__parsers__))

        for field in namespace:
            field_info = namespace.get(field)
            if not isinstance(field_info, _ArgField):
                mcs._extract_parsers_(parsers, field_info)
                continue

            # we allow fields to overide the fields declared in base
            # fields may not be in same index as base so uhmm!
            fields[field] = typing.cast(_ArgField, field_info)

        # Generate regex
        regex = ''
        field_list = sorted(fields.items(), key=lambda e: e[1].index)
        for field, field_data in field_list:
            if field_data.optional:
                regex += OPTIONAL_FIELD.format(field=field, re=field_data.regex)
            else:
                if regex:
                    regex += WHITESPACE
                regex += FIELD.format(field=field, re=field_data.regex)

        new_namespace = {
            "__regex__": re.compile(regex),
            "__fields__": fields,
            "__parsers__": parsers,
            **{name: value for name, value in namespace.items() if name not in (fields or parsers)},
        }
        new_namespace["__namespace__"] = new_namespace  # save a snapshot of new namespace
        cls = super().__new__(mcs, name, bases, new_namespace)
        return cls

    @classmethod
    def _extract_parsers_(mcs, parsers: dict, field_data: typing.Any) -> typing.Any:
        if isinstance(field_data, classmethod):  # parsers would be classmethods
            attr = getattr(field_data, "__parser_method__", None)  # ((field1, field2, ...), <parser>)
            if attr:
                for field in attr[0]:
                    parsers[field] = attr[1]


class ArgumentParser(metaclass=ArgumentParserMeta):

    if typing.TYPE_CHECKING:
        __regex__: re.Pattern
        __fields__: typing.Dict[typing.Any, _ArgField]
        __parsers__: typing.Dict[str, typing.Callable[..., typing.Any]]

    def __init__(self, **data: typing.Any) -> None:
        object.__setattr__(self, '__dict__', data)

    def __repr__(self) -> str:
        # make debugging better; inspired from pydantic
        attrs = ", ".join(repr(v) if k is None else f'{k}={v!r}' for k, v in self.__dict__.items())
        cls = self.__class__.__name__
        return f"{cls}({attrs})"

    @classmethod
    def filter(cls, optional: bool = False, skip_command: bool = False) -> _ArgFilter:  # noqa: A003
        return _ArgFilter(
            parser=cls, optional=optional, skip_command=skip_command
        )


class _ArgFilter(BaseFilter):
    parser: typing.Type[ArgumentParser]
    """parser"""
    optional: bool
    """If Arguments are optional"""
    skip_command: bool
    """True if commands need to be included in args"""

    async def __call__(
            self, message: Message, command: typing.Optional[CommandObject] = None
    ) -> typing.Union[bool, typing.Dict[str, typing.Any]]:
        strings = await GetStrings().get_by_chat_id(message.chat.id)

        if not (args := self.get_args(message, command)):
            if not self.optional:
                await message.reply(strings['no_args'])
                return False

            values: typing.Dict[str, typing.Any] = {}
            for field, field_data in self.parser.__fields__.items():
                try:
                    if not (
                        value := await self.trigger_parser(
                            field, value=None, values=values, field=field_data, match=None
                        )
                    ):
                        values[field] = field_data.default if type(field_data.default) is not Undefined else None
                    else:
                        values[field] = value
                except InvalidArg:
                    return False
            return {
                "args": self.parser(**values)
            }

        regex = self.parser.__regex__.match(args)
        if not regex:
            log.warning(
                f"Found unmatched regex; {self.parser.__name__}; {args=}; re={self.parser.__regex__}' match={regex}"
            )
            return False

        values = {}
        for field, field_data in self.parser.__fields__.items():
            value = regex.group(field)
            try:
                if not (value := await self.trigger_parser(field, value, values=values, field=field_data, match=regex)):
                    if (not field_data.optional) and (type(field_data.default) is not Undefined):
                        await message.reply(strings['no_args:fields'].format(field=field))
                        return False
                    values[field] = field_data.default if field_data.default is not Undefined else None
                else:
                    values[field] = value
            except InvalidArg:
                return False

        return {
            "args": self.parser(**values)
        }

    async def trigger_parser(
            self, field_name: typing.Any, value: typing.Any, **kwargs: typing.Any
    ) -> typing.Any:
        parser = self.parser.__parsers__.get(field_name, None)
        if parser:
            spec = inspect.getfullargspec(parser)
            kwargs = {key: value for key, value in kwargs.items() if key in spec.args}
            try:
                if inspect.iscoroutinefunction(parser):
                    value = await parser(self.parser, value, **kwargs)
                else:
                    value = parser(self.parser, value, **kwargs)
            except (TypeError, ValueError, AssertionError):
                raise InvalidArg
        return value

    def get_args(
            self, message: Message, command: typing.Optional[CommandObject]
    ) -> typing.Union[typing.Optional[str], typing.Literal[False]]:
        if not self.skip_command:
            if command:
                if command.args:
                    return command.args
        elif message.text:
            return message.text
        return False


class InvalidArg(Exception):
    pass
