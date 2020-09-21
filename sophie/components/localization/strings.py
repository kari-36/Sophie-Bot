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

from typing import Optional, TypeVar, Any, Dict, cast, Callable

from aiogram.dispatcher.handler import MessageHandler
from babel.core import Locale

from .lanuages import get_babel, get_language_emoji
from .locale import get_chat_locale
from .loader import GLOBAL_TRANSLATIONS


class GetStrings:
    # !! dont access these
    translations: Dict[str, Dict[str, str]]
    locale_code: str

    def __init__(self, module: Optional[str] = None):
        from sophie.utils.loader import LOADED_MODULES

        self._modules = LOADED_MODULES
        self.module = module

    def get_by_locale_name(self, locale_code: str) -> GetStrings:
        if not self.module:
            self.translations = GLOBAL_TRANSLATIONS
        else:
            self.translations = self._modules[self.module].data['translations']

        self.locale_code = locale_code
        if locale_code not in self.translations:
            self.locale_code = 'en-US'

        return self

    async def get_by_chat_id(self, chat_id: int) -> GetStrings:
        locale_name = await get_chat_locale(chat_id)
        return self.get_by_locale_name(locale_name)

    def __getitem__(self, key: str) -> str:
        fallback_locale = 'en-US'

        if not hasattr(self, 'translations'):
            raise RuntimeError(
                "GetStrings should initialised and should call either `get_by_locale_name` or `get_by_chat_id`"
            )

        if key in (translations := self.translations[self.locale_code]):
            return translations[key]

        elif key in (translations := self.translations[fallback_locale]):
            return translations[key]

        elif key in (translations := GLOBAL_TRANSLATIONS.get(self.locale_code, GLOBAL_TRANSLATIONS[fallback_locale])):
            return translations[key]

        else:
            return key

    def __repr__(self) -> str:
        # debugging
        attrs = ", ".join(repr(v) if k is None else f'{k}={v!r}' for k, v in self.__dict__.items()
                          if not k.startswith('_'))
        cls = self.__class__.__name__
        return f"{cls}({attrs})"


async def GetString(
        key: str, module: Optional[str] = None, chat_id: Optional[int] = None, locale_code: Optional[str] = None
) -> str:
    if chat_id:
        translations = await GetStrings(module).get_by_chat_id(chat_id)
    elif locale_code:
        translations = GetStrings(module).get_by_locale_name(locale_code)
    else:
        raise ValueError('Expected either `locale code` or `chat_id`')

    return translations[key]


class Strings:
    """
    Replacement of strings dict
    """

    def __init__(self, locale_code: str, module: str):
        self.locale_code = locale_code
        self.strings = GetStrings(module).get_by_locale_name(locale_code)

    def _get_string(self, key: str) -> str:
        return self.strings[key]

    def get(self, key: str, **kwargs: Any) -> str:
        string = self._get_string(key)
        string = string.format(**kwargs)
        return string

    @property
    def code(self) -> str:
        return self.locale_code

    @property
    def babel(self) -> Locale:
        return get_babel(self.locale_code)

    @property
    def emoji(self) -> str:
        return get_language_emoji(self.locale_code)

    def __getitem__(self, key: str) -> str:
        return self._get_string(key)

    def __repr__(self) -> str:
        # debugging
        attrs = ", ".join(repr(v) if k is None else f'{k}={v!r}' for k, v in self.__dict__.items())
        cls = self.__class__.__name__
        return f"{cls}({attrs})"


T = TypeVar("T", bound=Callable[..., Any])


def get_strings_dec(func: T) -> T:
    async def decorated(event: MessageHandler, *args: Any, **kwargs: Any) -> Any:
        module_name = func.__module__.split('.')[2]

        chat_id = event.chat.id
        strings = Strings(await get_chat_locale(chat_id), module_name)

        return await func(event, *args, strings=strings, **kwargs)

    return cast(T, decorated)
