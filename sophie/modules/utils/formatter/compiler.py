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
from typing import Any, Callable, List, Optional, TYPE_CHECKING, Union

from aiogram.api.types import (
    ForceReply, InlineKeyboardMarkup, Message, MessageEntity, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from aiogram.utils.text_decorations import html_decoration
from pydantic import BaseModel, Extra, Field

from sophie.services.aiogram import bot
from .plugins.bases import get_all_plugins
from .plugins.document import DocumentModel

if TYPE_CHECKING:
    from aiogram.api.types import Chat, User


class ParsedNoteModel(BaseModel):
    text: Optional[str] = Field(None, alias="caption")
    reply_markup: Optional[
        Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
    ] = None

    class Config:
        allow_population_by_field_name = True
        extra = Extra.allow


class RawNoteModel(BaseModel):

    text: Optional[str] = Field(max_length=4096)
    entities: Optional[List[MessageEntity]]
    plugins: Optional[List[str]]
    document: Optional[DocumentModel]

    async def compile_(
            self, message: Message, chat: Optional[Chat] = None, user: Optional[User] = None
    ) -> ParsedNoteModel:
        if not chat:
            chat = message.chat

        payload = ParsedNoteModel(text=self.text)
        for plugin in get_all_plugins(included=self.plugins):
            kwargs = self._generate_kwargs(
                plugin.compile_, message=message, data=self, payload=payload, chat=chat, user=user
            )
            await plugin.compile_(**kwargs)
        return payload

    async def decompile(
            self, message: Message, chat: Optional[Chat] = None, user: Optional[User] = None
    ) -> ParsedNoteModel:
        if not chat:
            chat = message.chat

        payload = ParsedNoteModel(text="")
        if self.text is not None:
            payload.text = html.escape(html.unescape(self.text), quote=False)

        for plugin in get_all_plugins(included=self.plugins):
            kwargs = self._generate_kwargs(
                plugin.decompile, message=message, data=self, payload=payload, chat=chat, user=user
            )
            await plugin.decompile(**kwargs)
        return payload

    def _build_request(self) -> Callable[..., Any]:
        if self.document is not None:
            attr = f"send_{self.document.file_type}"
            request = getattr(bot, attr, None)
            if request is None:
                raise
            return request
        return bot.send_message

    def _build_text(self, obj: ParsedNoteModel, fallback_text: str) -> None:
        if obj.text:
            text = html_decoration.unparse(obj.text, self.entities)
            obj.text = text
        else:
            obj.text = fallback_text

    @classmethod
    def _generate_kwargs(cls, func: object, **kwargs: Any) -> dict:
        spec = inspect.getfullargspec(func)
        return {key: value for key, value in kwargs.items() if key in spec.args}

    async def send(
            self,
            message: Message,
            chat: Optional[Chat] = None,
            user: Optional[User] = None,
            reply_id: Optional[int] = None,
            noformat: bool = False,
            fallback_text: str = '404',
            compiled: Optional[ParsedNoteModel] = None  # well one can pass compiled model too
    ) -> Message:

        payload = compiled
        if not payload:
            if not chat:
                chat = message.chat
            if not user:
                user = message.from_user

            if noformat:
                payload = await self.decompile(message, chat, user)
            else:
                payload = await self.compile_(message, chat, user)

        # build text
        self._build_text(payload, fallback_text)

        # build request
        request = self._build_request()
        params = inspect.getfullargspec(request).args
        if 'caption' in params:
            # by_alias cus "text" would named as "caption"; hacky
            kwargs = payload.dict(by_alias=True)
        elif 'text' in params:
            kwargs = payload.dict()
        else:
            kwargs = payload.dict(exclude={'text'})

        # TODO: Error handling
        # TODO: Entity-safe pagination when text exceeds 4096 or 1024
        return await request(
            chat_id=message.chat.id,
            reply_to_message_id=reply_id,
            **kwargs
        )

    class Config:
        extra = Extra.allow
        validate_assignment = True
