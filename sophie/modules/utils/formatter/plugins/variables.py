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
import re

from typing import Any, Callable, Optional, TYPE_CHECKING
from string import Formatter

from .bases import BaseFormatPlugin

if TYPE_CHECKING:
    from ..compiler import ParsedNoteModel
    from aiogram.api.types import Chat, Message, User


class Variables(BaseFormatPlugin):

    @classmethod
    async def compile_(
            cls, message: Message, payload: ParsedNoteModel, chat: Chat, user: Optional[User]
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
        spec = None
        add_offset = 0
        for match in re.finditer(r'{(?P<attr>[^}]+)}', text):
            raw_attr = match.group('attr')
            if '!' in raw_attr:
                raw_attr, spec = raw_attr.split('!', 1)

            if attr := getattr(self._variables, raw_attr, None):
                offset = match.start() + add_offset

                value = await self.call_var(attr, spec=spec)
                text = text[:offset] + re.sub(re.escape(match.group(0)), str(value), text[offset:], 1)

                # update additional offsets
                add_offset += len(str(value)) - len(match.group(0))
        return text

    @classmethod
    async def call_var(cls, attr: Callable[..., Any], **kwargs: Any) -> Any:
        spec = inspect.getfullargspec(attr)
        kwargs = {k: v for k, v in kwargs.items() if k in spec.args}
        if inspect.iscoroutinefunction(attr):
            return await attr(**kwargs)
        else:
            return attr(**kwargs)


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

        chat_id = self._chat.id if self._chat is not None else self._message.chat.id
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

    def first(self, spec: Optional[str]) -> str:
        """represting first name of user"""
        if spec in {'reply'}:
            if (reply := self._message.reply_to_message) and reply.from_user:
                return reply.from_user.first_name
        user = self._get_user()
        if user:
            return html.escape(user.first_name, quote=False)
        return 'Null'

    def last(self, spec: Optional[str]) -> str:
        # last name of a user
        if spec in {'reply'}:
            if (reply := self._message.reply_to_message) and reply.from_user:
                return reply.from_user.last_name or ''
        user = self._get_user()
        if user and user.last_name:
            return html.escape(user.last_name, quote=False)
        return ''

    def fullname(self, spec: Optional[str]) -> str:
        return self.first(spec) + ' ' + self.last(spec)

    def id(self, spec: Optional[str]) -> int:  # noqa: A003
        if spec in {'reply'}:
            if (reply := self._message.reply_to_message) and reply.from_user:
                return reply.from_user.id
        user = self._get_user()
        if user:
            return user.id
        return 0

    def mention(self, spec: Optional[str]) -> str:
        raise NotImplementedError

    def username(self, spec: Optional[str]) -> str:
        if spec in {'reply'}:
            if (reply := self._message.reply_to_message) and reply.from_user:
                return reply.from_user.username or self.mention(spec)
        user = self._get_user()
        if user and user.username:
            return '@' + user.username
        return self.mention(spec)

    def chatid(self) -> int:
        chat = self._get_chat()
        return chat.id

    def chatname(self) -> str:
        chat = self._get_chat()
        return html.escape(chat.title or 'Null', quote=False)

    def chatnick(self) -> str:
        chat = self._get_chat()
        if chat.username:
            return '@' + chat.username
        return self.chatname()

    def date(self) -> str:
        raise NotImplementedError

    def time(self) -> str:
        raise NotImplementedError

    def timedate(self) -> str:
        raise NotImplementedError
