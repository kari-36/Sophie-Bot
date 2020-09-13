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

import html
import warnings
import re

from abc import ABCMeta
from inspect import signature
from typing import Any, Callable, Dict, Literal, Match, Optional, TYPE_CHECKING, Tuple

from aiogram.api.types import InlineKeyboardMarkup, InlineKeyboardButton
from pydantic import BaseModel, Extra

from .bases import BaseFormatPlugin

if TYPE_CHECKING:
    from ..compiler import ParsedNoteModel, RawNoteModel
    from aiogram.api.types import Chat, Message, User

BUTTONS: Dict[str, Dict[str, Any]] = {}


class ButtonDataModel(BaseModel):
    text: str
    """Button text"""
    data: Optional[str] = None
    """Contains data obtained from syntax"""
    same_row: bool = False
    button_type: str

    class Config:
        extra = Extra.allow


class NoteButtons(BaseFormatPlugin):
    __syntax__: str = r"\[(?P<text>.+?)\]\((?P<type>\w+)(?:\:(?P<data>(?!same).+?|))?(?:\:(?P<row>same))?\)(?:\s)?"

    @classmethod
    async def validate(cls, message: Message, match: Match, data: RawNoteModel) -> Any:  # type: ignore

        if (btn_type := match.group('type')) not in BUTTONS:
            return

        button_data = ButtonDataModel(text=match.group('text'), data=match.group('data'), button_type=btn_type)
        if validator := get_validator(BUTTONS[btn_type]['validator']):
            if validator_cls := get_cls(btn_type):
                await validator(validator_cls, message, button_data, match.group('data'))

        if match.group('row') is not None:
            button_data.same_row = True

        if not hasattr(data, 'buttons'):
            data.buttons = [button_data]  # type: ignore
        else:
            data.buttons.append(button_data)  # type: ignore

        if data.text is not None:
            data.text = re.sub(re.escape(match.group(0)), '', data.text)

    @classmethod
    async def compile_(
            cls, message: Message, data: RawNoteModel, payload: ParsedNoteModel, chat: Chat, user: Optional[User]
    ) -> Any:
        buttons = []
        if btn_data := getattr(data, 'buttons', None):
            for button in btn_data:  # type: ButtonDataModel
                if compiler := get_compiler(button.button_type):
                    btn = InlineKeyboardButton(text=button.text)
                    await compiler(
                        get_cls(button.button_type), message, button, btn, chat, user
                    )
                    buttons.append([btn])
            payload.reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    async def decompile(
            cls, message: Message, data: RawNoteModel, payload: ParsedNoteModel, chat: Chat, user: Optional[User]
    ) -> Any:
        if (btn_data := getattr(data, 'buttons', None)) and payload.text is not None:
            for button in btn_data:  # type: ButtonDataModel
                syntax = (
                    f"[{html.escape(button.text, quote=False)}]"
                    f"({button.button_type}{':' + html.escape(button.data, quote=False) if button.data else ''}"
                    f"{':same' if button.same_row else ''})")

                payload.text += "\n"
                payload.text += syntax


def get_compiler(
        button_type: str
) -> Optional[Callable[[type, Message, ButtonDataModel, InlineKeyboardButton, Chat, Optional[User]], Any]]:
    if button_type not in BUTTONS:
        return None
    compiler = BUTTONS[button_type]['compiler']
    return compiler


def get_validator(
        validator: Callable[..., Any]
) -> Optional[Callable[[type, Message, ButtonDataModel, str], Any]]:
    args = set(list(signature(validator).parameters.keys())[3:])

    if args == {}:
        return lambda cls, message, data, arg: validator(cls, message, data)
    elif args == {'arg'} or 'kwargs' in args:
        return lambda cls, message, data, arg: validator(cls, message, data, arg=arg)
    else:
        return None


def get_cls(button: str) -> type:
    if button not in BUTTONS:
        raise ValueError(f"There is no registered button named `{button}`")

    name = BUTTONS[button]['_class']
    for base in BaseNoteButton.__subclasses__():
        if base.__name__ == name:
            return base

    warnings.warn(
        f"Can't find registered class for button type `{button}`, Module may not be loaded/initiated!",
        RuntimeWarning
    )
    return type


class _BaseNoteButtonMeta(ABCMeta):

    def __new__(mcs, name: str, bases: Tuple[type, Any], namespace: dict) -> type:  # type: ignore

        if validator := namespace.get('validate', None):
            if not isinstance(validator, classmethod):
                raise ValueError(f"NoteButton expected 'validator' to be classmethod not {type(validator)}")

        if compiler := namespace.get('compiler', None):
            if not isinstance(compiler, classmethod):
                raise ValueError(f"NoteButton expected 'compiler' to be classmethod not {type(compiler)}")

        if name != "BaseNoteButton":
            BUTTONS[namespace['name']] = {
                "_class": name,
                "type": namespace['button_type'],
                "validator": validator.__func__,
                "compiler": compiler.__func__
            }
        return super().__new__(mcs, name, bases, namespace)


class BaseNoteButton(metaclass=_BaseNoteButtonMeta):
    name: str
    button_type: Literal['callback', 'url'] = 'callback'

    @classmethod
    async def validate(cls, *args: Any, **kwargs: Any) -> Any:
        pass

    @classmethod
    async def compiler(
            cls,
            message: Message,
            data: ButtonDataModel,
            payload: InlineKeyboardButton,
            chat: Chat,
            user: Optional[User]
    ) -> Any:
        """should return callback data, fast as possible"""
        pass


class URLButton(BaseNoteButton):
    name = "url"
    button_type: Literal['url'] = "url"

    @classmethod
    async def validate(cls, message: Message, data: ButtonDataModel, arg: str) -> Any:  # type: ignore
        match = re.match(r"(//)?(?P<url>.+)", arg)
        if match is not None:
            data.__setattr__('url', match.group('url'))

    @classmethod
    async def compiler(
            cls,
            message: Message,
            data: ButtonDataModel,
            payload: InlineKeyboardButton,
            chat: Chat,
            user: Optional[User]
    ) -> Any:
        if url := getattr(data, 'url', None):
            payload.url = url
