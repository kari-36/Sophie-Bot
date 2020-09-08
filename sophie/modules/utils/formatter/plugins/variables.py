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
import inspect

from typing import Any, Optional, TYPE_CHECKING
from string import Formatter

from .bases import BaseFormatPlugin

if TYPE_CHECKING:
    from ..compiler import ParsedNoteModel, RawNoteModel
    from aiogram.api.types import Chat, Message, User


class Variables(BaseFormatPlugin):

    @classmethod
    async def compile_(
            cls, message: Message, data: RawNoteModel, payload: ParsedNoteModel, chat: Chat, user: Optional[User]
    ) -> Any:
        if payload.text is not None:
            text = await _populateVars(
                _builtinVars(message, chat=chat, user=user)
            ).populate(payload.text)
            payload.text = text


class _populateVars(Formatter):

    def __init__(self, variables: object):
        self._variables = variables

    async def populate(self, text: str) -> str:
        results = []

        for literal_text, field_name, format_spec, _ in self.parse(text):
            if literal_text:
                results.append(literal_text)

            if not field_name:
                continue

            value = await self._get_value(field_name)
            results.append(self.format_field(value, format_spec))  # type: ignore
        return ''.join(results)

    async def _get_value(self, key: str) -> str:
        if not key.startswith('_'):  # ignore dunders
            if obj := getattr(self._variables, key, None):
                if inspect.iscoroutinefunction(obj):
                    return await obj()
                else:
                    return obj()
        return '{' + key + '}'


class _builtinVars:

    def __init__(
            self,
            message: Message,
            custom_event: Optional[Message] = None,
            chat: Optional[Chat] = None,
            user: Optional[User] = None
    ):
        self._message = custom_event or message
        self._user = user
        self._chat = chat

    async def _language_code(self) -> str:
        from sophie.components.localization.locale import get_chat_locale

        if self._chat is not None:
            chat_id = self._chat.id
        else:
            chat_id = self._message.chat.id
        return await get_chat_locale(chat_id)

    def _get_user(self) -> Optional[User]:
        if self._user is not None:
            return self._user

        elif self._message.new_chat_members:
            return self._message.new_chat_members[0]

        elif self._message.from_user:
            return self._message.from_user

        else:
            return None

    def _get_chat(self) -> Chat:
        return self._chat or self._message.chat

    def first(self) -> str:
        """represting first name of user"""
        user = self._get_user()
        if user:
            return html.escape(user.first_name, quote=False)
        return 'Null'

    def last(self) -> str:
        # last name of a user
        user = self._get_user()
        if user and user.last_name:
            return html.escape(user.last_name, quote=False)
        return ''

    def id(self) -> int:  # noqa: A003
        user = self._get_user()
        if user:
            return user.id
        return 0

    def mention(self) -> str:
        raise NotImplementedError

    def username(self) -> str:
        user = self._get_user()
        if user and user.username:
            return '@' + user.username
        return self.mention()

    def chatid(self) -> int:
        chat = self._get_chat()
        return chat.id

    def chatname(self) -> str:
        chat = self._get_chat()
        return html.escape(chat.title or 'Null', quote=False)

    def chatnick(self) -> str:
        chat = self._get_chat()
        return chat.username or self.chatname()

    def date(self) -> str:
        raise NotImplementedError

    def time(self) -> str:
        raise NotImplementedError

    def timedate(self) -> str:
        raise NotImplementedError
